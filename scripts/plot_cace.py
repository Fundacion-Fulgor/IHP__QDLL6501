#!/usr/bin/env python3
import argparse
import csv
import math
import os
import shutil
import re
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

import matplotlib.pyplot as plt
import yaml
from cace.common.spiceunits import spice_unit_convert

PREFERRED_AXES = ("cload", "fin", "vdd", "temperature", "corner")


def load_datasheet(path):
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def find_runs(root):
    return sorted(
        path
        for path in (root / "runs").glob("RUN_*")
        if any(path.glob("parameters/*/simulation_summary.csv"))
    )


def resolve_run(root, requested):
    if requested:
        path = Path(requested).expanduser()
        if not path.is_absolute():
            path = root / path
        if not path.is_dir():
            raise SystemExit(f"Run directory does not exist: {path}")
        return path.resolve()
    runs = find_runs(root)
    if not runs:
        raise SystemExit(
            "No completed CACE runs found. Run ./plot-cace run <parameter> first."
        )
    return runs[-1].resolve()


def available_parameters(run_dir):
    return sorted(
        path.parent.name for path in run_dir.glob("parameters/*/simulation_summary.csv")
    )


def choose_parameter(run_dir, requested):
    parameters = available_parameters(run_dir)
    if not parameters:
        raise SystemExit(f"No simulation summaries found in {run_dir}")
    if requested:
        if requested not in parameters:
            raise SystemExit(
                f"Parameter {requested!r} is unavailable. Choose: {', '.join(parameters)}"
            )
        return requested
    if len(parameters) == 1:
        return parameters[0]
    if sys.stdin.isatty():
        print("Available parameters:")
        for index, name in enumerate(parameters, 1):
            print(f"  {index}. {name}")
        value = input("Select parameter: ").strip()
        if value.isdigit() and 1 <= int(value) <= len(parameters):
            return parameters[int(value) - 1]
        if value in parameters:
            return value
    raise SystemExit(f"Specify a parameter: {', '.join(parameters)}")


def read_summary(run_dir, parameter):
    path = run_dir / "parameters" / parameter / "simulation_summary.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise SystemExit(f"Simulation summary is empty: {path}")
    metadata = run_dir / "plot-cace.yaml"
    if metadata.is_file():
        conditions = yaml.safe_load(metadata.read_text(encoding="utf-8")).get(
            "conditions", {}
        )
        for row in rows:
            row.update({name: str(value) for name, value in conditions.items()})
    return rows


def parse_value(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def parse_filters(values):
    filters = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"Expected NAME=VALUE, got {item!r}")
        name, value = item.split("=", 1)
        filters[name.strip()] = parse_value(value.strip())
    return filters


def unit_scale(unit):
    if not unit:
        return 1.0
    return float(spice_unit_convert((str(unit), "1")))


def column_units(datasheet, parameter):
    units = {}
    for name, spec in datasheet.get("default_conditions", {}).items():
        units[name] = spec.get("unit", "")
    param = datasheet["parameters"][parameter]
    for name, spec in param.get("spec", {}).items():
        units[name] = spec.get("unit", param.get("unit", ""))
    return units


def condition_names(datasheet, parameter, columns):
    names = list(datasheet["parameters"][parameter].get("conditions", {}))
    return [name for name in names if name in columns]


def result_names(datasheet, parameter, columns):
    names = list(datasheet["parameters"][parameter].get("spec", {}))
    return [name for name in names if name in columns]


def display_name(datasheet, parameter, name):
    defaults = datasheet.get("default_conditions", {})
    spec = datasheet["parameters"][parameter].get("spec", {})
    if name in defaults:
        return defaults[name].get("display", name)
    if name in spec:
        return spec[name].get("display", name)
    return name


def values_match(actual, wanted, unit):
    actual = parse_value(actual)
    if isinstance(actual, float) and isinstance(wanted, float):
        scaled_wanted = wanted * unit_scale(unit)
        return math.isclose(actual, scaled_wanted, rel_tol=1e-9, abs_tol=1e-18)
    return str(actual) == str(wanted)


def typical_value(datasheet, name):
    spec = datasheet.get("default_conditions", {}).get(name, {})
    if "typical" not in spec:
        return None
    return parse_value(spec["typical"])


def varying_columns(rows, names):
    return [name for name in names if len({row[name] for row in rows}) > 1]


def choose_x(rows, conditions, requested):
    if requested:
        if requested not in conditions:
            raise SystemExit(
                f"Unknown x-axis {requested!r}. Choose: {', '.join(conditions)}"
            )
        return requested
    varying = varying_columns(rows, conditions)
    for name in PREFERRED_AXES:
        if name in varying:
            return name
    if varying:
        return varying[0]
    return conditions[0] if conditions else "run"


def filter_rows(rows, filters, units):
    selected = rows
    for name, wanted in filters.items():
        if name not in rows[0]:
            raise SystemExit(f"Unknown filter {name!r}. Choose: {', '.join(rows[0])}")
        selected = [
            row
            for row in selected
            if values_match(row[name], wanted, units.get(name, ""))
        ]
    if not selected:
        formatted = ", ".join(f"{name}={value}" for name, value in filters.items())
        raise SystemExit(f"No results match: {formatted}")
    return selected


def spec_limits(datasheet, parameter, metric):
    result = []
    spec = datasheet["parameters"][parameter].get("spec", {}).get(metric, {})
    scale = unit_scale(
        spec.get("unit", datasheet["parameters"][parameter].get("unit", ""))
    )
    for kind in ("minimum", "typical", "maximum"):
        value = spec.get(kind, {}).get("value")
        if value is not None and value != "any":
            result.append((kind, float(value) * scale))
    return result


def choose_groups(varying, xaxis, requested, show_all):
    if requested:
        return requested
    if show_all:
        return [name for name in varying if name != xaxis]
    return ["corner"] if "corner" in varying and xaxis != "corner" else []


def grouped_rows(rows, groups):
    if not groups:
        return [("results", rows)]
    buckets = {}
    for row in rows:
        key = tuple(row[name] for name in groups)
        buckets.setdefault(key, []).append(row)
    return [
        (", ".join(f"{name}={value}" for name, value in zip(groups, key)), value)
        for key, value in sorted(buckets.items())
    ]


def plot_results(args, root, datasheet):
    run_dir = resolve_run(root, args.run_dir)
    parameter = choose_parameter(run_dir, args.parameter)
    if parameter not in datasheet["parameters"]:
        raise SystemExit(f"Parameter {parameter!r} is absent from the datasheet")
    rows = read_summary(run_dir, parameter)
    columns = list(rows[0])
    conditions = condition_names(datasheet, parameter, columns)
    metrics = args.metric or result_names(datasheet, parameter, columns)
    unknown_metrics = [name for name in metrics if name not in columns]
    if unknown_metrics:
        raise SystemExit(f"Unknown metric(s): {', '.join(unknown_metrics)}")
    xaxis = choose_x(rows, conditions, args.x)
    varying = varying_columns(rows, conditions)
    groups = choose_groups(varying, xaxis, args.group, args.all)
    unknown_groups = [name for name in groups if name not in conditions]
    if unknown_groups:
        raise SystemExit(f"Unknown group(s): {', '.join(unknown_groups)}")
    filters = parse_filters(args.where)
    units = column_units(datasheet, parameter)
    selected = filter_rows(rows, filters, units) if filters else rows
    if not args.all:
        kept = set(groups) | {xaxis} | set(filters)
        for name in conditions:
            if name in kept or len({row[name] for row in selected}) <= 1:
                continue
            typical = typical_value(datasheet, name)
            if typical is None:
                continue
            candidates = [
                row
                for row in selected
                if values_match(row[name], typical, units.get(name, ""))
            ]
            if candidates:
                selected = candidates
    if not selected:
        raise SystemExit("No rows remain after applying typical-condition selection")
    columns_count = min(2, len(metrics))
    rows_count = math.ceil(len(metrics) / columns_count)
    figure, axes = plt.subplots(
        rows_count,
        columns_count,
        figsize=(7 * columns_count, 4.3 * rows_count),
        squeeze=False,
    )
    xscale = unit_scale(units.get(xaxis, ""))
    for axis, metric in zip(axes.flat, metrics):
        yscale = unit_scale(units.get(metric, ""))
        metric_has_value = False
        for label, group_rows in grouped_rows(selected, groups):
            points = sorted(
                (
                    (parse_value(row[xaxis]), parse_value(row[metric]))
                    for row in group_rows
                ),
                key=lambda point: (
                    point[0] if isinstance(point[0], float) else str(point[0])
                ),
            )
            xvalues = [
                point[0] / xscale if isinstance(point[0], float) else point[0]
                for point in points
            ]
            yvalues = [
                point[1] / yscale if abs(point[1]) < 1e90 else math.nan
                for point in points
            ]
            metric_has_value = metric_has_value or any(
                not math.isnan(value) for value in yvalues
            )
            axis.plot(xvalues, yvalues, marker="o", label=label)
        for kind, value in spec_limits(datasheet, parameter, metric):
            axis.axhline(
                value / yscale, linestyle="--", linewidth=1, label=f"{kind} spec"
            )
        xunit = units.get(xaxis, "")
        yunit = units.get(metric, "")
        axis.set_xlabel(
            f"{display_name(datasheet, parameter, xaxis)} ({xunit})"
            if xunit
            else display_name(datasheet, parameter, xaxis)
        )
        axis.set_ylabel(
            f"{display_name(datasheet, parameter, metric)} ({yunit})"
            if yunit
            else display_name(datasheet, parameter, metric)
        )
        axis.set_title(display_name(datasheet, parameter, metric))
        if not metric_has_value:
            axis.text(
                0.5,
                0.5,
                "No threshold crossing",
                ha="center",
                va="center",
                transform=axis.transAxes,
            )
        axis.grid(True, linestyle=":", alpha=0.6)
        if groups or spec_limits(datasheet, parameter, metric):
            axis.legend(fontsize="small")
    for axis in axes.flat[len(metrics) :]:
        axis.remove()
    figure.suptitle(
        f"{datasheet.get('name', root.name)} — {datasheet['parameters'][parameter].get('display', parameter)}\n{run_dir.name}"
    )
    figure.tight_layout()
    if args.save:
        output = Path(args.save).expanduser().resolve()
        figure.savefig(output, bbox_inches="tight")
        print(output)
    print(f"Plotted {len(selected)} of {len(rows)} results from {run_dir}")
    print(
        f"x={xaxis}; metrics={','.join(metrics)}; groups={','.join(groups) or 'none'}"
    )
    if not args.no_show:
        plt.show()
    return run_dir, parameter


def list_results(args, root, datasheet):
    run_dir = resolve_run(root, args.run_dir)
    print(run_dir)
    for parameter in available_parameters(run_dir):
        rows = read_summary(run_dir, parameter)
        columns = list(rows[0])
        conditions = condition_names(datasheet, parameter, columns)
        metrics = result_names(datasheet, parameter, columns)
        print(f"{parameter}: {len(rows)} runs")
        print(f"  conditions: {', '.join(conditions)}")
        print(f"  metrics: {', '.join(metrics)}")


def select_waveform_row(rows, datasheet, parameter, filters):
    units = column_units(datasheet, parameter)
    selected = filter_rows(rows, filters, units) if filters else rows
    conditions = condition_names(datasheet, parameter, list(rows[0]))
    for name in conditions:
        if name in filters or len({row[name] for row in selected}) <= 1:
            continue
        typical = typical_value(datasheet, name)
        if typical is None:
            continue
        candidates = [
            row
            for row in selected
            if values_match(row[name], typical, units.get(name, ""))
        ]
        if candidates:
            selected = candidates
    return selected[0]


def ensure_within(path, parent, description):
    resolved = path.resolve()
    try:
        resolved.relative_to(parent.resolve())
    except ValueError:
        raise SystemExit(
            f"{description} escapes the project runs directory: {resolved}"
        )
    return resolved


def find_simulation_netlist(root, run_dir, parameter, run_name, template):
    trusted_runs = (root / "runs").resolve()
    run_dir = ensure_within(run_dir, trusted_runs, "Run directory")
    if not re.fullmatch(r"run_\d+", run_name):
        raise SystemExit(f"Invalid CACE run name: {run_name!r}")
    parameter_dir = ensure_within(
        run_dir / "parameters" / parameter,
        run_dir / "parameters",
        "Parameter directory",
    )
    simulation_dir = ensure_within(
        parameter_dir / run_name, parameter_dir, "Simulation directory"
    )
    netlist_name = f"{Path(template).stem}.spice"
    netlist = ensure_within(simulation_dir / netlist_name, simulation_dir, "Netlist")
    if not netlist.is_file():
        raise SystemExit(f"Generated ngspice netlist not found: {netlist}")
    return netlist


def add_raw_write(netlist, raw_path):
    lines = netlist.read_text(encoding="utf-8").splitlines()
    controls = [
        index for index, line in enumerate(lines) if line.strip().lower() == ".control"
    ]
    if len(controls) != 1:
        raise SystemExit(f"Expected one ngspice control block in {netlist}")
    control = controls[0]
    end = next(
        (
            index
            for index, line in enumerate(lines[control + 1 :], control + 1)
            if line.strip().lower() == ".endc"
        ),
        None,
    )
    if end is None:
        raise SystemExit(f"Unterminated ngspice control block in {netlist}")
    safe_control = [".control", "run", f"write {raw_path} all", "quit", ".endc"]
    return "\n".join(lines[:control] + safe_control + lines[end + 1 :]) + "\n"


def waveform(args, root, datasheet):
    run_dir = resolve_run(root, args.run_dir)
    parameter = choose_parameter(run_dir, args.parameter)
    rows = read_summary(run_dir, parameter)
    filters = parse_filters(args.where)
    row = select_waveform_row(rows, datasheet, parameter, filters)
    template = datasheet["parameters"][parameter]["tool"]["ngspice"]["template"]
    netlist = find_simulation_netlist(root, run_dir, parameter, row["run"], template)
    waveform_dir = run_dir / "waveforms"
    waveform_dir.mkdir(exist_ok=True)
    raw_path = waveform_dir / f"{parameter}_{row['run']}.raw"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".spice", dir=netlist.parent, delete=False, encoding="utf-8"
    ) as stream:
        stream.write(add_raw_write(netlist, raw_path.resolve()))
        patched = Path(stream.name)
    environment = os.environ.copy()
    environment.setdefault("PDK", datasheet.get("PDK", "ihp-sg13g2"))
    environment.setdefault("PDK_ROOT", "/foss/pdks")
    try:
        subprocess.run(
            ["ngspice", "-b", str(patched)],
            cwd=netlist.parent,
            env=environment,
            check=True,
        )
    finally:
        patched.unlink(missing_ok=True)
    selected_conditions = [
        f"{name}={row[name]}"
        for name in condition_names(datasheet, parameter, list(row))
    ]
    print(raw_path.resolve())
    print("Selected " + ", ".join(selected_conditions))
    if args.viewer != "none":
        viewer = shutil.which(args.viewer)
        if not viewer:
            raise SystemExit(f"Waveform viewer not found: {args.viewer}")
        subprocess.Popen([viewer, str(raw_path.resolve())], cwd=root)
    return raw_path


def create_run_datasheet(
    datasheet, datasheet_path, parameter, overrides, typical_only, directory
):
    generated = deepcopy(datasheet)
    configured_root = generated.get("paths", {}).get("root", ".")
    resolved_root = (datasheet_path.parent / configured_root).resolve()
    generated["paths"]["root"] = str(resolved_root)
    generated["paths"]["runs"] = str(resolved_root / "runs")
    if parameter not in generated["parameters"]:
        choices = ", ".join(generated["parameters"])
        raise SystemExit(f"Unknown parameter {parameter!r}. Choose: {choices}")
    generated["parameters"] = {parameter: generated["parameters"][parameter]}
    conditions = generated["parameters"][parameter].get("conditions", {})
    defaults = generated.get("default_conditions", {})
    if typical_only:
        for name in conditions:
            if "typical" in defaults.get(name, {}):
                conditions[name] = {"typical": defaults[name]["typical"]}
    for name, value in overrides.items():
        if name not in conditions:
            raise SystemExit(
                f"Unknown condition {name!r}. Choose: {', '.join(conditions)}"
            )
        conditions[name] = {"typical": value}
    path = directory / "datasheet.yaml"
    path.write_text(yaml.safe_dump(generated, sort_keys=False), encoding="utf-8")
    return path


def preserve_cace_failure(returncode, allow_fail):
    return returncode != 0 and not (returncode == 2 and allow_fail)


def latest_parameter_run(root, parameter, before=None):
    runs = find_runs(root)
    if before:
        runs = [run for run in runs if run.name > before]
    for run in reversed(runs):
        if (run / "parameters" / parameter / "simulation_summary.csv").is_file():
            return run
    return None


def run_cace(args, root, datasheet_path, datasheet):
    overrides = parse_filters(args.set)
    generated_directory = None
    run_datasheet = datasheet_path
    run_conditions = {}
    if overrides or args.typical:
        generated_directory = Path(
            tempfile.mkdtemp(prefix="plot-cace-", dir=datasheet_path.parent)
        )
        run_datasheet = create_run_datasheet(
            datasheet,
            datasheet_path,
            args.parameter,
            overrides,
            args.typical,
            generated_directory,
        )
    existing_runs = find_runs(root)
    previous_tag = existing_runs[-1].name if existing_runs else None
    command = [
        "cace",
        str(run_datasheet),
        "-s",
        args.source,
        "-p",
        args.parameter,
        "-j",
        str(args.jobs),
        "--max-runs",
        str(args.max_runs),
    ]
    if args.force:
        command.append("--force")
    try:
        completed = subprocess.run(command, cwd=root, check=False)
    finally:
        if generated_directory:
            shutil.rmtree(generated_directory)
    completed_run = latest_parameter_run(root, args.parameter, previous_tag)
    if not completed_run:
        raise SystemExit(completed.returncode or 1)
    if completed.returncode == 2:
        print(
            "CACE completed with specification failures; opening the recorded results."
        )
    elif completed.returncode:
        print(
            f"CACE exited with status {completed.returncode}; opening the recorded partial results."
        )
    if overrides:
        units = column_units(datasheet, args.parameter)
        for name, value in overrides.items():
            run_conditions[name] = (
                value * unit_scale(units.get(name, ""))
                if isinstance(value, float)
                else value
            )
        metadata = completed_run / "plot-cace.yaml"
        metadata.write_text(
            yaml.safe_dump({"conditions": run_conditions}, sort_keys=False),
            encoding="utf-8",
        )
    plot_args = argparse.Namespace(
        run_dir=str(completed_run),
        parameter=args.parameter,
        x=args.x,
        metric=args.metric,
        group=args.group,
        where=args.where,
        all=args.all,
        save=args.save,
        no_show=args.no_show,
    )
    plot_results(plot_args, root, datasheet)
    if preserve_cace_failure(completed.returncode, args.allow_fail):
        raise SystemExit(completed.returncode)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="plot-cace",
        description="Run, inspect, and interactively plot CACE/ngspice characterization results.",
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help=argparse.SUPPRESS)
    parser.add_argument("--datasheet", type=Path, default=Path("cace/QDLL_TOP.yaml"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser(
        "list", help="List plottable results in a CACE run"
    )
    list_parser.add_argument("--run", dest="run_dir")

    plot_parser = subparsers.add_parser(
        "plot", help="Open interactive scalar characterization plots"
    )
    add_plot_arguments(plot_parser)
    plot_parser.add_argument("parameter", nargs="?")
    plot_parser.add_argument("--run", dest="run_dir")

    waveform_parser = subparsers.add_parser(
        "waveform", help="Open one CACE transient run in gaw"
    )
    waveform_parser.add_argument("parameter", nargs="?")
    waveform_parser.add_argument("--run", dest="run_dir")
    waveform_parser.add_argument(
        "--where", action="append", default=[], metavar="NAME=VALUE"
    )
    waveform_parser.add_argument(
        "--viewer", default="gaw", help="Viewer command, or 'none'"
    )

    run_parser = subparsers.add_parser(
        "run", help="Run one CACE parameter and open its plots"
    )
    run_parser.add_argument("parameter")
    run_parser.add_argument(
        "--source",
        default="schematic",
        choices=("schematic", "layout", "pex", "rcx", "best"),
    )
    run_parser.add_argument(
        "-j", "--jobs", type=int, default=min(os.cpu_count() or 1, 16)
    )
    run_parser.add_argument("--max-runs", type=int, default=5)
    run_parser.add_argument("--force", action="store_true")
    run_parser.add_argument(
        "--allow-fail",
        action="store_true",
        help="Return success after plotting CACE specification failures",
    )
    run_parser.add_argument(
        "--typical",
        action="store_true",
        help="Run only the typical value of every condition",
    )
    run_parser.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="Override a condition for this run; repeat as needed",
    )
    add_plot_arguments(run_parser)
    return parser


def add_plot_arguments(parser):
    parser.add_argument("--x", help="Condition to place on the x-axis")
    parser.add_argument(
        "--metric", action="append", help="Metric to plot; repeat as needed"
    )
    parser.add_argument(
        "--group", action="append", help="Condition to use for trace grouping"
    )
    parser.add_argument("--where", action="append", default=[], metavar="NAME=VALUE")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Do not hold other conditions at typical values",
    )
    parser.add_argument("--save", help="Also save the figure to this path")
    parser.add_argument("--no-show", action="store_true", help=argparse.SUPPRESS)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()
    datasheet_path = args.datasheet.expanduser()
    if not datasheet_path.is_absolute():
        datasheet_path = root / datasheet_path
    datasheet = load_datasheet(datasheet_path)
    if args.command == "list":
        list_results(args, root, datasheet)
    elif args.command == "plot":
        plot_results(args, root, datasheet)
    elif args.command == "waveform":
        waveform(args, root, datasheet)
    elif args.command == "run":
        run_cace(args, root, datasheet_path, datasheet)


if __name__ == "__main__":
    main()
