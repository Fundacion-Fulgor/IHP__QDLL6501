import argparse
import csv
import datetime
import hashlib
import json
import math
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


class LibGroup:
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []
        self.attributes = {}
        self.repeated_attributes = {}
        self.groups = []

    def get_groups(self, name):
        return [g for g in self.groups if g.name == name]

    def get_group(self, name):
        groups = self.get_groups(name)
        return groups[0] if groups else None

    def get_attribute(self, name):
        return self.attributes.get(name)


def tokenize_liberty(text):
    pos = 0
    length = len(text)
    tokens = []
    while pos < length:
        ch = text[pos]
        if ch.isspace():
            pos += 1
            continue
        if ch == "\\" and pos + 1 < length and text[pos + 1] in "\r\n":
            pos += 1
            if text[pos] == "\r" and pos + 1 < length and text[pos + 1] == "\n":
                pos += 1
            pos += 1
            continue
        if ch == "/":
            if pos + 1 < length and text[pos + 1] == "*":
                end = text.find("*/", pos + 2)
                if end == -1:
                    raise ValueError(f"Unterminated block comment at position {pos}")
                pos = end + 2
                continue
            elif pos + 1 < length and text[pos + 1] == "/":
                end = text.find("\n", pos + 2)
                pos = length if end == -1 else end + 1
                continue
            else:
                raise ValueError(f"Unexpected standalone '/' at position {pos}")
        if ch == "*":
            raise ValueError(f"Unexpected standalone '*' at position {pos}")
        if ch == '"':
            start = pos
            pos += 1
            closed = False
            while pos < length:
                if text[pos] == "\\":
                    pos += 2
                elif text[pos] == '"':
                    pos += 1
                    closed = True
                    break
                elif text[pos] in "\r\n":
                    raise ValueError(f"Unterminated string literal at line {start}")
                else:
                    pos += 1
            if not closed:
                raise ValueError(f"Unterminated string literal starting at {start}")
            tokens.append(text[start:pos])
            continue
        if ch in "{}():;,":
            tokens.append(ch)
            pos += 1
            continue
        start = pos
        while (
            pos < length
            and not text[pos].isspace()
            and text[pos] not in "{}():;,\"/*"
        ):
            pos += 1
        if start == pos:
            raise ValueError(f"Unexpected character '{text[pos]}' at position {pos}")
        tokens.append(text[start:pos])
    return tokens


def parse_liberty(text):
    tokens = tokenize_liberty(text)
    pos = 0
    n = len(tokens)

    def parse_group(name, args):
        nonlocal pos
        group = LibGroup(name, args)
        if pos >= n or tokens[pos] != "{":
            raise ValueError(f"Expected '{{' for group {name}")
        pos += 1
        while pos < n and tokens[pos] != "}":
            token = tokens[pos]
            pos += 1
            if pos < n and tokens[pos] == "(":
                pos += 1
                call_args = []
                while pos < n and tokens[pos] != ")":
                    if tokens[pos] != ",":
                        call_args.append(tokens[pos])
                    pos += 1
                if pos >= n or tokens[pos] != ")":
                    raise ValueError(f"Unclosed argument list for {token}")
                pos += 1
                if pos < n and tokens[pos] == "{":
                    child = parse_group(token, call_args)
                    group.groups.append(child)
                else:
                    if pos < n and tokens[pos] == ";":
                        pos += 1
                    group.attributes[token] = call_args
                    group.repeated_attributes.setdefault(token, []).append(call_args)
            elif pos < n and tokens[pos] == ":":
                pos += 1
                val_parts = []
                while pos < n and tokens[pos] not in (";", "}"):
                    val_parts.append(tokens[pos])
                    pos += 1
                if pos < n and tokens[pos] == ";":
                    pos += 1
                val = (
                    " ".join(val_parts)
                    if len(val_parts) > 1
                    else (val_parts[0] if val_parts else "")
                )
                group.attributes[token] = val
            elif token == ";":
                continue
            else:
                raise ValueError(f"Unexpected token inside group: {token}")
        if pos >= n or tokens[pos] != "}":
            raise ValueError(f"Unterminated group '{name}': missing '}}'")
        pos += 1
        return group

    if not tokens:
        raise ValueError("Empty Liberty text")
    name = tokens[pos]
    pos += 1
    args = []
    if pos < n and tokens[pos] == "(":
        pos += 1
        while pos < n and tokens[pos] != ")":
            if tokens[pos] != ",":
                args.append(tokens[pos])
            pos += 1
        if pos >= n or tokens[pos] != ")":
            raise ValueError(f"Unclosed argument list for root group {name}")
        pos += 1
    root = parse_group(name, args)
    if pos != n:
        raise ValueError(f"Extra trailing tokens starting with '{tokens[pos]}'")
    return root


def parse_num_list(raw):
    if raw is None:
        return []
    if not isinstance(raw, list):
        raw = [raw]
    res = []
    for item in raw:
        s = str(item).strip('" \t\r\n')
        for part in s.split(","):
            part = part.strip()
            if part:
                res.append(float(part))
    return res


def parse_table_values(raw):
    if raw is None:
        return []
    if not isinstance(raw, list):
        raw = [raw]
    rows = []
    for item in raw:
        s = str(item).strip('" \t\r\n')
        row = []
        for part in s.split(","):
            part = part.strip()
            if part:
                row.append(float(part))
        if row:
            rows.append(row)
    return rows


def find_template(lib_root, template_name):
    for tmpl in lib_root.get_groups("lu_table_template"):
        if tmpl.args and tmpl.args[0] == template_name:
            return tmpl
    return None


def find_cell(lib_root, cell_name):
    for c in lib_root.get_groups("cell"):
        if c.args and c.args[0] == cell_name:
            return c
    return None


def validate_liberty_metadata(lib_root, context):
    time_unit = str(lib_root.get_attribute("time_unit") or "").strip('"')
    if time_unit not in ("1ns", "1 ns"):
        raise ValueError(f"Unsupported time_unit '{time_unit}' in {context}")

    cap_unit = lib_root.get_attribute("capacitive_load_unit")
    if (
        not isinstance(cap_unit, list)
        or len(cap_unit) != 2
        or float(cap_unit[0]) != 1.0
        or cap_unit[1].strip('"').lower() != "pf"
    ):
        raise ValueError(f"Unsupported capacitive_load_unit '{cap_unit}' in {context}")

    volt_unit = str(lib_root.get_attribute("voltage_unit") or "").strip('"')
    if volt_unit not in ("1V", "1 V"):
        raise ValueError(f"Unsupported voltage_unit '{volt_unit}' in {context}")

    for key, expected in [
        ("slew_lower_threshold_pct_rise", "10"),
        ("slew_upper_threshold_pct_rise", "90"),
        ("slew_lower_threshold_pct_fall", "10"),
        ("slew_upper_threshold_pct_fall", "90"),
        ("input_threshold_pct_rise", "50"),
        ("input_threshold_pct_fall", "50"),
        ("output_threshold_pct_rise", "50"),
        ("output_threshold_pct_fall", "50"),
    ]:
        val = str(lib_root.get_attribute(key) or "").strip('"')
        if val != expected:
            raise ValueError(
                f"Unsupported threshold {key}='{val}' "
                f"(expected {expected}) in {context}"
            )

    op_conds = lib_root.get_groups("operating_conditions")
    if len(op_conds) != 1:
        raise ValueError(f"Expected one operating condition in {context}")
    for key, expected in (("process", 1.0), ("temperature", 25.0), ("voltage", 1.2)):
        value = op_conds[0].get_attribute(key)
        if value is None or float(value) != expected:
            raise ValueError(f"Only nominal 1.2V/3.3V, 25C is supported: {context}")
    voltage_maps = lib_root.repeated_attributes.get("voltage_map", [])
    supplies = {name.strip('"'): float(value) for name, value in voltage_maps}
    if any(supplies.get(name) != voltage for name, voltage in (
        ("vdd", 1.2), ("iovdd", 3.3), ("vss", 0.0), ("iovss", 0.0)
    )):
        raise ValueError(f"Missing or non-nominal supply voltage_map in {context}")
    if str(lib_root.get_attribute("current_unit")).strip('"') != "1uA":
        raise ValueError(f"Unsupported current_unit in {context}")

    for tmpl in lib_root.get_groups("lu_table_template"):
        v1 = str(tmpl.get_attribute("variable_1") or "").strip('"')
        v2 = str(tmpl.get_attribute("variable_2") or "").strip('"')
        if v1 != "input_net_transition":
            raise ValueError(f"Unsupported variable_1 '{v1}' in {tmpl.args} {context}")
        if v2 != "total_output_net_capacitance":
            raise ValueError(f"Unsupported variable_2 '{v2}' in {tmpl.args} {context}")


def validate_table(i1, i2, values, context=""):
    if len(i1) < 2:
        raise ValueError(f"index_1 length must be >= 2 in {context}")
    if len(i2) < 2:
        raise ValueError(f"index_2 length must be >= 2 in {context}")
    for val in i1:
        if not math.isfinite(val):
            raise ValueError(f"Non-finite index_1 value {val} in {context}")
    for val in i2:
        if not math.isfinite(val):
            raise ValueError(f"Non-finite index_2 value {val} in {context}")
    if any(i1[k + 1] <= i1[k] for k in range(len(i1) - 1)):
        raise ValueError(f"index_1 must be strictly increasing in {context}")
    if any(i2[k + 1] <= i2[k] for k in range(len(i2) - 1)):
        raise ValueError(f"index_2 must be strictly increasing in {context}")
    if len(values) != len(i1):
        raise ValueError(
            f"Row count mismatch in {context}: {len(values)} != {len(i1)}"
        )
    for r_idx, row in enumerate(values):
        if len(row) != len(i2):
            raise ValueError(
                f"Col count mismatch in {context} row {r_idx}: {len(row)} != {len(i2)}"
            )
        for val in row:
            if not math.isfinite(val):
                raise ValueError(f"Non-finite value in {context}: {val}")


def match_timing_arc(
    cell_group, out_pin, in_pin,
    expected_type="combinational",
    expected_sense="positive_unate"
):
    pin_groups = [
        p for p in cell_group.get_groups("pin")
        if p.args and p.args[0] == out_pin
    ]
    if not pin_groups:
        raise ValueError(f"Pin {out_pin} not found in cell {cell_group.args[0]}")
    pin_group = pin_groups[0]
    matched = []
    for tg in pin_group.get_groups("timing"):
        rel_pin = str(tg.get_attribute("related_pin") or "").strip('"')
        ttype = str(tg.get_attribute("timing_type") or "").strip('"')
        tsense = str(tg.get_attribute("timing_sense") or "").strip('"')
        when_cond = tg.get_attribute("when")
        if (
            rel_pin == in_pin
            and ttype == expected_type
            and tsense == expected_sense
            and when_cond is None
        ):
            matched.append(tg)
    if len(matched) != 1:
        raise ValueError(
            f"Ambiguous or missing timing arc {in_pin}->{out_pin} "
            f"(type {expected_type}, sense {expected_sense}, unconditional) "
            f"in {cell_group.args[0]}: found {len(matched)}"
        )
    return matched[0]


def check_analog_sentinel(cell_group):
    if not cell_group or not cell_group.args:
        return False, "Not analog cell"
    cname = cell_group.args[0]
    if "Analog" not in cname:
        return False, "Not analog cell"
    pin_groups = cell_group.get_groups("pin")
    if not pin_groups:
        return True, "Analog cell has no pin timing"
    for p in pin_groups:
        for t in p.get_groups("timing"):
            for cr in t.get_groups("cell_rise"):
                vals = parse_table_values(cr.get_attribute("values"))
                arr = np.array(vals, dtype=float)
                if arr.size > 0 and np.ptp(arr) == 0.0 and arr.flat[0] >= 100.0:
                    return True, (
                        f"Detected static sentinel timing table (uniform delay "
                        f"{arr.flat[0]} ns, uncharacterized analog passthrough)"
                    )
    return False, "Valid analog characterization"


def extract_table_data(lib_root, timing_group, table_name, cell_context):
    tg_list = timing_group.get_groups(table_name)
    if not tg_list:
        raise ValueError(f"Missing {table_name} table in {cell_context}")
    tg = tg_list[0]
    i1 = parse_num_list(tg.get_attribute("index_1"))
    i2 = parse_num_list(tg.get_attribute("index_2"))
    if not i1 or not i2:
        template_name = tg.args[0] if tg.args else None
        if template_name:
            tmpl = find_template(lib_root, template_name)
            if tmpl:
                if not i1:
                    i1 = parse_num_list(tmpl.get_attribute("index_1"))
                if not i2:
                    i2 = parse_num_list(tmpl.get_attribute("index_2"))
    values = parse_table_values(tg.get_attribute("values"))
    validate_table(i1, i2, values, f"{cell_context} -> {table_name}")
    return {
        "index_1": i1,
        "index_2": i2,
        "values": values,
        "template": tg.args[0] if tg.args else "",
    }


def interp_curve(i1, i2, values_matrix, slew, loads):
    validate_table(i1, i2, values_matrix, "interpolation")
    slew = float(slew)
    if not math.isfinite(slew) or not np.all(np.isfinite(loads)):
        raise ValueError("Slew and loads must be finite")
    i1_arr = np.asarray(i1, dtype=float)
    i2_arr = np.asarray(i2, dtype=float)
    if slew < i1_arr[0] - 1e-9 or slew > i1_arr[-1] + 1e-9:
        raise ValueError(
            f"Slew {slew} out of range [{i1_arr[0]}, {i1_arr[-1]}], "
            "extrapolation forbidden"
        )
    slew = max(i1_arr[0], min(i1_arr[-1], slew))
    mat = np.asarray(values_matrix, dtype=float)
    if np.isclose(slew, i1_arr[0]):
        row = mat[0, :]
    elif np.isclose(slew, i1_arr[-1]):
        row = mat[-1, :]
    else:
        k = int(np.searchsorted(i1_arr, slew)) - 1
        k = max(0, min(k, len(i1_arr) - 2))
        s0, s1 = i1_arr[k], i1_arr[k + 1]
        t = (slew - s0) / (s1 - s0) if s1 > s0 else 0.0
        row = (1.0 - t) * mat[k, :] + t * mat[k + 1, :]

    loads_arr = np.asarray(loads, dtype=float)
    if np.any(loads_arr < i2_arr[0] - 1e-9) or np.any(loads_arr > i2_arr[-1] + 1e-9):
        raise ValueError(
            f"Load out of range [{i2_arr[0]}, {i2_arr[-1]}], extrapolation forbidden"
        )
    loads_clamped = np.clip(loads_arr, i2_arr[0], i2_arr[-1])
    return np.interp(loads_clamped, i2_arr, row)


def safe_percent_diff(base_val, comp_val, eps=1e-12):
    delta = comp_val - base_val
    if abs(base_val) < eps:
        return delta, None
    return delta, (delta / base_val) * 100.0


def run_git_cmd(repo_dir, args):
    cmd = ["git", "-C", str(repo_dir)] + args
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return res.stdout


def resolve_commit_info(repo_dir, ref):
    sha = run_git_cmd(repo_dir, ["rev-parse", ref]).decode("utf-8").strip()
    short_sha = run_git_cmd(
        repo_dir, ["rev-parse", "--short", sha]
    ).decode("utf-8").strip()
    return sha, short_sha


def load_lib_from_git(repo_dir, ref, rel_path):
    pfx = "ihp-sg13g2/"
    with_pfx = f"{pfx}{rel_path}" if not rel_path.startswith(pfx) else rel_path
    no_pfx = rel_path[len(pfx):] if rel_path.startswith(pfx) else rel_path
    candidates = [rel_path, with_pfx, no_pfx]
    seen = set()
    last_err = None
    for cand in candidates:
        if cand in seen:
            continue
        seen.add(cand)
        try:
            blob = run_git_cmd(repo_dir, ["show", f"{ref}:{cand}"])
            return blob, cand
        except subprocess.CalledProcessError as err:
            last_err = err
    raise RuntimeError(f"Could not find {rel_path} in {ref}: {last_err}")


def get_remote_urls(repo_dir):
    try:
        remote_url = run_git_cmd(
            repo_dir, ["remote", "get-url", "origin"]
        ).decode("utf-8").strip()
    except Exception:
        remote_url = ""

    gitmodules_url = ""
    gitmodules_path = Path(repo_dir).parent / ".gitmodules"
    if not gitmodules_path.is_file():
        gitmodules_path = Path(repo_dir) / ".gitmodules"
    if gitmodules_path.is_file():
        try:
            content = gitmodules_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                if "url =" in line and "IHP-Open-PDK" in line:
                    gitmodules_url = line.split("=", 1)[1].strip()
                    break
        except Exception:
            pass
    return remote_url, gitmodules_url


CELL_CONFIGS = [
    {
        "cell": "sg13g2_IOPadOut4mA",
        "category": "output",
        "out_pin": "pad",
        "in_pin": "c2p",
        "arc_name": "c2p->pad",
    },
    {
        "cell": "sg13g2_IOPadOut16mA",
        "category": "output",
        "out_pin": "pad",
        "in_pin": "c2p",
        "arc_name": "c2p->pad",
    },
    {
        "cell": "sg13g2_IOPadOut30mA",
        "category": "output",
        "out_pin": "pad",
        "in_pin": "c2p",
        "arc_name": "c2p->pad",
    },
    {
        "cell": "sg13g2_IOPadIn",
        "category": "input",
        "out_pin": "p2c",
        "in_pin": "pad",
        "arc_name": "pad->p2c",
    },
    {
        "cell": "sg13g2_IOPadAnalog",
        "category": "analog",
        "out_pin": "pad",
        "in_pin": "pad",
        "arc_name": "pad->pad",
    },
]

TABLE_KEYS = [
    ("cell_rise", "delay", "rise"),
    ("cell_fall", "delay", "fall"),
    ("rise_transition", "slew", "rise"),
    ("fall_transition", "slew", "fall"),
]


def compare_cells(lib0, lib1, slew_ns, in_slew_ns=None, num_points=30):
    if num_points < 2:
        raise ValueError("num_points must be at least 2")
    if not math.isfinite(slew_ns) or (
        in_slew_ns is not None and not math.isfinite(in_slew_ns)
    ):
        raise ValueError("Requested slew must be finite")

    validate_liberty_metadata(lib0, "ref0")
    validate_liberty_metadata(lib1, "ref1")

    results = {}
    csv_rows = []

    for cfg in CELL_CONFIGS:
        cname = cfg["cell"]
        c0 = find_cell(lib0, cname)
        c1 = find_cell(lib1, cname)
        if not c0 or not c1:
            raise ValueError(f"Cell {cname} missing in one or both libraries")

        if cfg["category"] == "analog":
            is_sentinel_0, reason_0 = check_analog_sentinel(c0)
            is_sentinel_1, reason_1 = check_analog_sentinel(c1)
            results[cname] = {
                "status": "placeholder_skipped",
                "is_sentinel_ref0": is_sentinel_0,
                "is_sentinel_ref1": is_sentinel_1,
                "reason": reason_0 if is_sentinel_0 else reason_1,
            }
            continue

        arc0 = match_timing_arc(c0, cfg["out_pin"], cfg["in_pin"])
        arc1 = match_timing_arc(c1, cfg["out_pin"], cfg["in_pin"])

        tbls0 = {
            k[0]: extract_table_data(lib0, arc0, k[0], f"ref0:{cname}")
            for k in TABLE_KEYS
        }
        tbls1 = {
            k[0]: extract_table_data(lib1, arc1, k[0], f"ref1:{cname}")
            for k in TABLE_KEYS
        }

        min_load = max(
            max(t["index_2"][0] for t in tbls0.values()),
            max(t["index_2"][0] for t in tbls1.values()),
        )
        max_load = min(
            min(t["index_2"][-1] for t in tbls0.values()),
            min(t["index_2"][-1] for t in tbls1.values()),
        )
        if min_load >= max_load:
            raise ValueError(
                f"Common load interval empty [{min_load}, {max_load}] for {cname}"
            )

        inter_slew_min = max(
            max(t["index_1"][0] for t in tbls0.values()),
            max(t["index_1"][0] for t in tbls1.values()),
        )
        inter_slew_max = min(
            min(t["index_1"][-1] for t in tbls0.values()),
            min(t["index_1"][-1] for t in tbls1.values()),
        )
        if inter_slew_min >= inter_slew_max:
            raise ValueError(
                f"Common slew interval empty [{inter_slew_min}, "
                f"{inter_slew_max}] for {cname}"
            )

        target_slew = slew_ns
        if cfg["category"] == "input":
            if in_slew_ns is not None:
                target_slew = in_slew_ns
            elif not (inter_slew_min - 1e-9 <= target_slew <= inter_slew_max + 1e-9):
                target_slew = inter_slew_min

        if target_slew < inter_slew_min - 1e-9 or target_slew > inter_slew_max + 1e-9:
            raise ValueError(
                f"Requested slew {target_slew} ns outside intersection "
                f"[{inter_slew_min}, {inter_slew_max}] ns for cell {cname}"
            )

        f0 = tbls0["cell_rise"]
        f1 = tbls1["cell_rise"]
        pts0 = [p for p in f0["index_2"] if min_load - 1e-9 <= p <= max_load + 1e-9]
        pts1 = [p for p in f1["index_2"] if min_load - 1e-9 <= p <= max_load + 1e-9]
        dense = np.linspace(min_load, max_load, num_points)
        sampled_loads = np.unique(np.sort(np.concatenate([pts0, pts1, dense])))

        slew_exact_0 = bool(np.any(np.isclose(f0["index_1"], target_slew)))
        slew_exact_1 = bool(np.any(np.isclose(f1["index_1"], target_slew)))

        cell_res = {
            "status": "compared",
            "category": cfg["category"],
            "arc": cfg["arc_name"],
            "selected_slew_ns": target_slew,
            "slew_is_exact_grid_point_ref0": slew_exact_0,
            "slew_is_exact_grid_point_ref1": slew_exact_1,
            "intersection_slew_range_ns": [inter_slew_min, inter_slew_max],
            "intersection_load_range_pf": [min_load, max_load],
            "ref0_original_indices": {
                "index_1": f0["index_1"],
                "index_2": f0["index_2"],
            },
            "ref1_original_indices": {
                "index_1": f1["index_1"],
                "index_2": f1["index_2"],
            },
            "sampled_loads_pf": sampled_loads.tolist(),
            "metrics": {},
        }

        for tbl_name, metric, trans in TABLE_KEYS:
            t0 = tbls0[tbl_name]
            t1 = tbls1[tbl_name]

            y0 = interp_curve(
                t0["index_1"], t0["index_2"], t0["values"],
                target_slew, sampled_loads
            )
            y1 = interp_curve(
                t1["index_1"], t1["index_2"], t1["values"],
                target_slew, sampled_loads
            )

            deltas = y1 - y0
            pct_diffs = []
            for d_val, i_val in zip(y0, y1):
                delta, pct = safe_percent_diff(d_val, i_val)
                pct_diffs.append(pct)
                csv_rows.append(
                    {
                        "cell": cname,
                        "arc": cfg["arc_name"],
                        "metric": metric,
                        "transition_type": trans,
                        "slew_ns": target_slew,
                        "load_pf": float(round(sampled_loads[len(pct_diffs) - 1], 6)),
                        "ref0_value_ns": float(round(d_val, 6)),
                        "ref1_value_ns": float(round(i_val, 6)),
                        "delta_ns": float(round(delta, 6)),
                        "percent_diff": float(round(pct, 4)) if pct is not None else "",
                    }
                )

            valid_pcts = [p for p in pct_diffs if p is not None]
            cell_res["metrics"][tbl_name] = {
                "metric": metric,
                "transition_type": trans,
                "ref0_values_ns": y0.tolist(),
                "ref1_values_ns": y1.tolist(),
                "delta_ns": deltas.tolist(),
                "percent_diff": pct_diffs,
                "min_delta_ns": float(np.min(deltas)),
                "max_delta_ns": float(np.max(deltas)),
                "mean_delta_ns": float(np.mean(deltas)),
                "min_percent_diff": float(np.min(valid_pcts)) if valid_pcts else None,
                "max_percent_diff": float(np.max(valid_pcts)) if valid_pcts else None,
                "mean_percent_diff": float(np.mean(valid_pcts)) if valid_pcts else None,
                "ref0_grid_points": [
                    {"load_pf": p, "val_ns": float(v)}
                    for p, v in zip(
                        t0["index_2"],
                        interp_curve(
                            t0["index_1"], t0["index_2"], t0["values"],
                            target_slew, t0["index_2"]
                        ),
                    )
                ],
                "ref1_grid_points": [
                    {"load_pf": p, "val_ns": float(v)}
                    for p, v in zip(
                        t1["index_2"],
                        interp_curve(
                            t1["index_1"], t1["index_2"], t1["values"],
                            target_slew, t1["index_2"]
                        ),
                    )
                ],
            }

        results[cname] = cell_res

    return results, csv_rows


def plot_grid(cells_list, results, ref0_lbl, ref1_lbl, title_lines, out_png, out_svg):
    n_rows = len(cells_list)
    fig, axes = plt.subplots(
        n_rows, 2, figsize=(11, 3.2 * n_rows), constrained_layout=True
    )
    if n_rows == 1:
        axes = np.array([axes])
    c_ref0 = "#1f77b4"
    c_ref1 = "#d62728"

    for row_idx, cname in enumerate(cells_list):
        cdata = results[cname]
        loads = cdata["sampled_loads_pf"]
        target_slew = cdata["selected_slew_ns"]
        l_min, l_max = cdata["intersection_load_range_pf"]

        for col_idx, (m_type, y_lbl, (r_key, f_key)) in enumerate([
            ("Delay", "Propagation Delay [ns]", ("cell_rise", "cell_fall")),
            ("Slew", "Transition Time (10%-90%) [ns]",
             ("rise_transition", "fall_transition")),
        ]):
            ax = axes[row_idx, col_idx]
            r_data = cdata["metrics"][r_key]
            f_data = cdata["metrics"][f_key]

            ax.plot(
                loads, r_data["ref0_values_ns"], color=c_ref0,
                linestyle="-", label=f"{ref0_lbl} Rise"
            )
            ax.plot(
                loads, f_data["ref0_values_ns"], color=c_ref0,
                linestyle="--", label=f"{ref0_lbl} Fall"
            )
            ax.plot(
                loads, r_data["ref1_values_ns"], color=c_ref1,
                linestyle="-", label=f"{ref1_lbl} Rise"
            )
            ax.plot(
                loads, f_data["ref1_values_ns"], color=c_ref1,
                linestyle="--", label=f"{ref1_lbl} Fall"
            )

            pts0 = [
                pt for pt in r_data["ref0_grid_points"]
                if l_min <= pt["load_pf"] <= l_max
            ]
            pts1 = [
                pt for pt in r_data["ref1_grid_points"]
                if l_min <= pt["load_pf"] <= l_max
            ]
            if pts0:
                ax.plot(
                    [p["load_pf"] for p in pts0], [p["val_ns"] for p in pts0],
                    color=c_ref0, marker="o", linestyle="None",
                    markersize=4, alpha=0.8
                )
            if pts1:
                ax.plot(
                    [p["load_pf"] for p in pts1], [p["val_ns"] for p in pts1],
                    color=c_ref1, marker="s", linestyle="None",
                    markersize=4, alpha=0.8
                )

            ax.set_title(
                f"{cname} {m_type} ({cdata['arc']}) @ {target_slew:.2f} ns slew",
                fontsize=10
            )
            ax.set_xlabel("Output Load Capacitance CL [pF]", fontsize=9)
            ax.set_ylabel(y_lbl, fontsize=9)
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend(loc="upper left", fontsize=8)

    fig.suptitle("\n".join(title_lines), fontsize=10, weight="bold")
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    fig.savefig(out_svg, bbox_inches="tight")
    plt.close(fig)


def build_provenance_and_summary(
    pdk_repo, ref0, ref1, sha0, short0, sha1, short1,
    sha256_0, sha256_1, resolved_path,
    remote_url, gitmodules_url,
    results, slew_ns, in_slew_ns
):
    derived_caveats = [
        (
            "Scope: IHP published Liberty characterization tables directly from PDK "
            "repository branches, NOT new simulations and NOT extracted GDS/PEX timing."
        ),
        (
            "Delta definition: delta_ns = ref_1 - ref_0 "
            "(comparator minus baseline ref_0). "
            "Percent difference: ((ref_1 - ref_0) / ref_0) * 100."
        ),
    ]

    for cname, cinfo in results.items():
        if cinfo["status"] == "placeholder_skipped":
            derived_caveats.append(f"{cname}: Skipped - {cinfo['reason']}.")
            continue
        slew = cinfo["selected_slew_ns"]
        ex0 = (
            "exact grid point"
            if cinfo["slew_is_exact_grid_point_ref0"]
            else "interpolated"
        )
        ex1 = (
            "exact grid point"
            if cinfo["slew_is_exact_grid_point_ref1"]
            else "interpolated"
        )
        r0_loads = cinfo["ref0_original_indices"]["index_2"]
        r1_loads = cinfo["ref1_original_indices"]["index_2"]
        i_loads = cinfo["intersection_load_range_pf"]
        derived_caveats.append(
            f"{cname}: Evaluated at input slew {slew:.2f} ns "
            f"({ref0}: {ex0}, {ref1}: {ex1}). "
            f"Load grid ref0 [{r0_loads[0]}, {r0_loads[-1]}] pF vs "
            f"ref1 [{r1_loads[0]}, {r1_loads[-1]}] pF; evaluated strictly "
            f"within intersection [{i_loads[0]}, {i_loads[-1]}] pF "
            "to avoid extrapolation."
        )

    summary = {
        "label": "IHP published Liberty characterization",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pdk_repo": str(pdk_repo),
        "library_file": resolved_path,
        "delta_definition": "ref_1 - ref_0 (comparator minus baseline ref_0)",
        "percent_diff_definition": "((ref_1 - ref_0) / ref_0) * 100",
        "conditions": {
            "operating_condition": "sg13g2_io_typ_1p2V_3p3V_25C",
            "process": 1,
            "temperature_C": 25.0,
            "core_voltage_V": 1.2,
            "io_voltage_V": 3.3,
        },
        "units": {
            "time_unit": "1ns",
            "capacitive_load_unit": "1pf",
            "voltage_unit": "1V",
            "current_unit": "1uA",
        },
        "provenance": {
            "remote_origin_url": remote_url,
            "gitmodules_url": gitmodules_url,
            "ref_0": {
                "ref_name": ref0,
                "commit_sha": sha0,
                "short_sha": short0,
                "sha256": sha256_0,
            },
            "ref_1": {
                "ref_name": ref1,
                "commit_sha": sha1,
                "short_sha": short1,
                "sha256": sha256_1,
            },
        },
        "cells": results,
        "derived_caveats": derived_caveats,
    }
    return summary


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Compare IHP published Liberty characterization between branches."
    )
    parser.add_argument(
        "--pdk-repo", default="IHP-Open-PDK",
        help="Path to IHP-Open-PDK git repository"
    )
    parser.add_argument(
        "--refs", nargs=2, default=["origin/dev", "origin/IO-xschem"],
        help="Two git refs to compare"
    )
    parser.add_argument(
        "--output", default="/tmp/opencode/io-liberty-comparison-final",
        help="Output directory"
    )
    parser.add_argument(
        "--slew-ns", type=float, default=0.1,
        help="Input transition slew in ns"
    )
    parser.add_argument(
        "--in-slew-ns", type=float, default=None,
        help="Input slew for input pad in ns"
    )
    parser.add_argument(
        "--lib-path",
        default="ihp-sg13g2/libs.ref/sg13g2_io/lib/sg13g2_io_typ_1p2V_3p3V_25C.lib",
        help="Relative path to .lib in repo"
    )
    parser.add_argument(
        "--num-points", type=int, default=30,
        help="Number of interpolation points"
    )
    return parser.parse_args(argv)


def run_comparison(
    pdk_repo="IHP-Open-PDK",
    refs=("origin/dev", "origin/IO-xschem"),
    output_dir="/tmp/opencode/io-liberty-comparison-final",
    slew_ns=0.1,
    in_slew_ns=None,
    lib_path="ihp-sg13g2/libs.ref/sg13g2_io/lib/sg13g2_io_typ_1p2V_3p3V_25C.lib",
    num_points=30,
):
    repo_path = Path(pdk_repo)
    if not repo_path.is_dir():
        raise FileNotFoundError(f"PDK repository not found: {repo_path}")

    ref0, ref1 = refs
    sha0, short0 = resolve_commit_info(repo_path, ref0)
    sha1, short1 = resolve_commit_info(repo_path, ref1)

    blob0, resolved0 = load_lib_from_git(repo_path, sha0, lib_path)
    blob1, resolved1 = load_lib_from_git(repo_path, sha1, lib_path)

    sha256_0 = hashlib.sha256(blob0).hexdigest()
    sha256_1 = hashlib.sha256(blob1).hexdigest()

    remote_url, gitmodules_url = get_remote_urls(repo_path)

    lib0 = parse_liberty(blob0.decode("utf-8"))
    lib1 = parse_liberty(blob1.decode("utf-8"))

    results, csv_rows = compare_cells(lib0, lib1, slew_ns, in_slew_ns, num_points)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    clean_ref0 = ref0.replace("/", "_")
    clean_ref1 = ref1.replace("/", "_")
    snap0 = out_path / f"sg13g2_io_typ_1p2V_3p3V_25C_{clean_ref0}_{short0}.lib"
    snap1 = out_path / f"sg13g2_io_typ_1p2V_3p3V_25C_{clean_ref1}_{short1}.lib"
    snap0.write_bytes(blob0)
    snap1.write_bytes(blob1)

    csv_path = out_path / "sampled_curves.csv"
    fieldnames = [
        "cell", "arc", "metric", "transition_type", "slew_ns", "load_pf",
        "ref0_value_ns", "ref1_value_ns", "delta_ns", "percent_diff"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    ref0_lbl = f"{ref0} ({short0})"
    ref1_lbl = f"{ref1} ({short1})"

    out_cells = [cfg["cell"] for cfg in CELL_CONFIGS if cfg["category"] == "output"]
    out_title = [
        "IHP Published Liberty Characterization: Output Drivers",
        f"{ref0_lbl} vs {ref1_lbl}",
        "Typ 1.2V/3.3V, 25°C | Published Liberty tables (not new simulation/PEX)",
    ]
    png_out = out_path / "output_timing.png"
    svg_out = out_path / "output_timing.svg"
    plot_grid(out_cells, results, ref0_lbl, ref1_lbl, out_title, png_out, svg_out)

    in_cells = [cfg["cell"] for cfg in CELL_CONFIGS if cfg["category"] == "input"]
    in_title = [
        "IHP Published Liberty Characterization: Input Buffer (sg13g2_IOPadIn)",
        f"{ref0_lbl} vs {ref1_lbl}",
        "Typ 1.2V/3.3V, 25°C | Published Liberty tables (not new simulation/PEX)",
    ]
    png_in = out_path / "input_timing.png"
    svg_in = out_path / "input_timing.svg"
    plot_grid(in_cells, results, ref0_lbl, ref1_lbl, in_title, png_in, svg_in)

    summary = build_provenance_and_summary(
        pdk_repo, ref0, ref1, sha0, short0, sha1, short1,
        sha256_0, sha256_1, resolved0,
        remote_url, gitmodules_url,
        results, slew_ns, in_slew_ns
    )
    json_path = out_path / "summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return {
        "summary": summary,
        "plots": {
            "output_timing_png": str(png_out),
            "output_timing_svg": str(svg_out),
            "input_timing_png": str(png_in),
            "input_timing_svg": str(svg_in),
        },
        "csv": str(csv_path),
        "json": str(json_path),
        "snapshots": [str(snap0), str(snap1)],
    }


def main():
    args = parse_args()
    artifacts = run_comparison(
        pdk_repo=args.pdk_repo,
        refs=args.refs,
        output_dir=args.output,
        slew_ns=args.slew_ns,
        in_slew_ns=args.in_slew_ns,
        lib_path=args.lib_path,
        num_points=args.num_points,
    )
    summary = artifacts["summary"]

    print("=" * 78)
    print("IHP Published Liberty Characterization Comparison")
    print("=" * 78)
    r0 = summary["provenance"]["ref_0"]
    r1 = summary["provenance"]["ref_1"]
    print(f"Ref 0: {r0['ref_name']} ({r0['short_sha']}) SHA256: {r0['sha256'][:16]}...")
    print(f"Ref 1: {r1['ref_name']} ({r1['short_sha']}) SHA256: {r1['sha256'][:16]}...")
    print(f"Remote origin: {summary['provenance']['remote_origin_url']}")
    print(f"Output Directory: {args.output}")
    print("-" * 78)

    for cname, cinfo in summary["cells"].items():
        if cinfo["status"] == "placeholder_skipped":
            print(f"Cell {cname:20s}: SKIPPED ({cinfo['reason']})")
            continue
        l_min, l_max = cinfo["intersection_load_range_pf"]
        print(f"Cell {cname:20s} [Arc {cinfo['arc']}, "
              f"Slew: {cinfo['selected_slew_ns']:.2f} ns, "
              f"Load: {l_min}..{l_max} pF]:")
        for tbl_name, mdata in cinfo["metrics"].items():
            min_p = (
                f"{mdata['min_percent_diff']:+.2f}%"
                if mdata["min_percent_diff"] is not None
                else "N/A"
            )
            max_p = (
                f"{mdata['max_percent_diff']:+.2f}%"
                if mdata["max_percent_diff"] is not None
                else "N/A"
            )
            d_min = mdata["min_delta_ns"]
            d_max = mdata["max_delta_ns"]
            print(f"  {tbl_name:16s}: delta {d_min:+.4f}..{d_max:+.4f} ns "
                  f"({min_p} .. {max_p})")

    print("-" * 78)
    print("Derived Caveats:")
    for cav in summary["derived_caveats"]:
        print(f"  * {cav}")
    print("-" * 78)
    print("Generated Artifacts:")
    for key, path in artifacts["plots"].items():
        print(f"  {key}: {path}")
    print(f"  CSV sampled curves: {artifacts['csv']}")
    print(f"  Summary JSON:       {artifacts['json']}")
    for s in artifacts["snapshots"]:
        print(f"  Snapshot:           {s}")
    print("=" * 78)


if __name__ == "__main__":
    main()
