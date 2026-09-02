import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "plot_cace", ROOT / "scripts" / "plot_cace.py"
)
PLOT_CACE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLOT_CACE)


class PlotCaceTest(unittest.TestCase):
    def setUp(self):
        self.datasheet = yaml.safe_load((ROOT / "cace" / "QDLL_TOP.yaml").read_text())
        self.rows = [
            {
                "run": "run_000",
                "corner": "tt",
                "temperature": "65.000",
                "vdd": "1.200",
                "fin": "2.500e+08",
                "cload": "1.000e-13",
                "out3_delay_fall": "6.5e-10",
            },
            {
                "run": "run_001",
                "corner": "tt",
                "temperature": "65.000",
                "vdd": "1.200",
                "fin": "2.500e+08",
                "cload": "3.000e-13",
                "out3_delay_fall": "7.0e-10",
            },
            {
                "run": "run_002",
                "corner": "ff",
                "temperature": "65.000",
                "vdd": "1.200",
                "fin": "2.500e+08",
                "cload": "1.000e-13",
                "out3_delay_fall": "5.5e-10",
            },
        ]

    def test_units_match_user_facing_values(self):
        units = PLOT_CACE.column_units(self.datasheet, "out3_timing")
        selected = PLOT_CACE.filter_rows(
            self.rows,
            {"temperature": 65.0, "fin": 250.0, "cload": 100.0},
            units,
        )
        self.assertEqual([row["run"] for row in selected], ["run_000", "run_002"])

    def test_default_axis_prefers_load(self):
        conditions = ["corner", "temperature", "vdd", "fin", "cload"]
        self.assertEqual(PLOT_CACE.choose_x(self.rows, conditions, None), "cload")

    def test_all_groups_every_non_axis_pvt_condition(self):
        groups = PLOT_CACE.choose_groups(
            ["corner", "temperature", "vdd", "fin", "cload"],
            "cload",
            None,
            True,
        )
        self.assertEqual(groups, ["corner", "temperature", "vdd", "fin"])

    def test_latest_complete_run_is_selected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for tag in ("RUN_2026-01-01_00-00-00", "RUN_2026-01-02_00-00-00"):
                parameter = root / "runs" / tag / "parameters" / "out3_timing"
                parameter.mkdir(parents=True)
                with (parameter / "simulation_summary.csv").open(
                    "w", newline=""
                ) as stream:
                    writer = csv.writer(stream)
                    writer.writerow(("run", "cload", "out3_delay_fall"))
                    writer.writerow(("run_000", "1e-13", "6e-10"))
            self.assertEqual(
                PLOT_CACE.resolve_run(root, None).name,
                "RUN_2026-01-02_00-00-00",
            )

    def test_run_datasheet_supports_typical_50pf_override(self):
        with tempfile.TemporaryDirectory() as directory:
            datasheet_path = ROOT / "cace" / "QDLL_TOP.yaml"
            generated = PLOT_CACE.create_run_datasheet(
                self.datasheet,
                datasheet_path,
                "out3_timing",
                {"cload": 50000.0},
                True,
                Path(directory),
            )
            result = yaml.safe_load(generated.read_text())
            conditions = result["parameters"]["out3_timing"]["conditions"]
            self.assertEqual(conditions["cload"], {"typical": 50000.0})
            self.assertEqual(conditions["corner"], {"typical": "tt"})
            self.assertTrue(Path(result["paths"]["root"]).is_absolute())

    def test_waveform_selection_uses_typical_frequency(self):
        rows = [
            {**self.rows[0], "run": "run_000", "fin": "2.250e+08"},
            {**self.rows[0], "run": "run_001", "fin": "2.500e+08"},
            {**self.rows[0], "run": "run_002", "fin": "2.750e+08"},
        ]
        selected = PLOT_CACE.select_waveform_row(
            rows, self.datasheet, "out3_timing", {}
        )
        self.assertEqual(selected["run"], "run_001")

    def test_allow_fail_only_suppresses_specification_failures(self):
        self.assertFalse(PLOT_CACE.preserve_cace_failure(0, False))
        self.assertTrue(PLOT_CACE.preserve_cace_failure(2, False))
        self.assertFalse(PLOT_CACE.preserve_cace_failure(2, True))
        for returncode in (1, 3, 4):
            self.assertTrue(PLOT_CACE.preserve_cace_failure(returncode, True))

    def test_netlist_must_stay_in_project_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "outside"
            outside.mkdir()
            with self.assertRaises(SystemExit):
                PLOT_CACE.find_simulation_netlist(
                    root, outside, "out3_timing", "run_0", "tb_out3.sch"
                )

    def test_raw_write_replaces_untrusted_control_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            netlist = Path(directory) / "test.spice"
            netlist.write_text(
                ".tran 1p 1n\n.control\nshell touch /tmp/unsafe\nrun\n.endc\n"
            )
            patched = PLOT_CACE.add_raw_write(netlist, Path("result.raw"))
            self.assertNotIn("shell", patched)
            self.assertIn("run\nwrite result.raw all\nquit\n", patched)


if __name__ == "__main__":
    unittest.main()
