import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "plot_io_comparison", ROOT / "scripts" / "plot_io_comparison.py"
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def build_synthetic_lib_text(scale=1.0, max_load=10.0, add_condition=False):
    cells = []
    for cname, out_p, in_p, cat in [
        ("sg13g2_IOPadOut4mA", "pad", "c2p", "out"),
        ("sg13g2_IOPadOut16mA", "pad", "c2p", "out"),
        ("sg13g2_IOPadOut30mA", "pad", "c2p", "out"),
        ("sg13g2_IOPadIn", "p2c", "pad", "in"),
        ("sg13g2_IOPadAnalog", "pad", "pad", "analog"),
    ]:
        if cat == "analog":
            cells.append(f"""
            cell ({cname}) {{
              pin (pad) {{
                timing () {{
                  cell_rise (delay_template_2x2) {{
                    values ("1000.0, 1000.0", "1000.0, 1000.0");
                  }}
                  rise_transition (delay_template_2x2) {{
                    values ("200.0, 200.0", "200.0, 200.0");
                  }}
                  cell_fall (delay_template_2x2) {{
                    values ("1000.0, 1000.0", "1000.0, 1000.0");
                  }}
                  fall_transition (delay_template_2x2) {{
                    values ("200.0, 200.0", "200.0, 200.0");
                  }}
                }}
              }}
            }}
            """)
        else:
            cond_attr = 'when : "enable == 1";' if add_condition else ""
            v1 = 1.0 * scale
            v2 = 2.0 * scale
            cells.append(f"""
            cell ({cname}) {{
              pin ({out_p}) {{
                timing () {{
                  related_pin : "{in_p}";
                  timing_type : combinational;
                  timing_sense : positive_unate;
                  {cond_attr}
                  cell_rise () {{
                    index_1 ("0.05, 0.2");
                    index_2 ("1.0, {max_load}");
                    values ("{v1}, {v2}", "{v1 * 1.5}, {v2 * 1.5}");
                  }}
                  cell_fall () {{
                    index_1 ("0.05, 0.2");
                    index_2 ("1.0, {max_load}");
                    values ("{v1}, {v2}", "{v1 * 1.5}, {v2 * 1.5}");
                  }}
                  rise_transition () {{
                    index_1 ("0.05, 0.2");
                    index_2 ("1.0, {max_load}");
                    values ("{v1}, {v2}", "{v1 * 1.5}, {v2 * 1.5}");
                  }}
                  fall_transition () {{
                    index_1 ("0.05, 0.2");
                    index_2 ("1.0, {max_load}");
                    values ("{v1}, {v2}", "{v1 * 1.5}, {v2 * 1.5}");
                  }}
                }}
              }}
            }}
            """)
    body = "\n".join(cells)
    return f"""
    library (sg13g2_io_typ_1p2V_3p3V_25C) {{
      time_unit : "1ns";
      capacitive_load_unit (1, pf);
      voltage_unit : "1V";
      current_unit : "1uA";
      voltage_map (vdd, 1.2);
      voltage_map (iovdd, 3.3);
      voltage_map (vss, 0);
      voltage_map (iovss, 0);
      slew_lower_threshold_pct_rise : 10;
      slew_upper_threshold_pct_rise : 90;
      slew_lower_threshold_pct_fall : 10;
      slew_upper_threshold_pct_fall : 90;
      input_threshold_pct_rise : 50;
      input_threshold_pct_fall : 50;
      output_threshold_pct_rise : 50;
      output_threshold_pct_fall : 50;
      operating_conditions (sg13g2_io_typ_1p2V_3p3V_25C) {{
        process : 1;
        temperature : 25;
        voltage : 1.2;
      }}
      lu_table_template (delay_template_2x2) {{
        variable_1 : input_net_transition;
        variable_2 : total_output_net_capacitance;
        index_1 ("10.0, 200.0");
        index_2 ("500.0, 30000.0");
      }}
      {body}
    }}
    """


class TestPlotIoComparison(unittest.TestCase):
    def test_tokenizer_valid_comments_and_quotes(self):
        snippet = """
        /* Multi-line
           comment */
        library (demo) {
          // Line comment
          str : "Quotes with \\"escaped\\" text and /*not comment*/";
          cont : "line 1 \\
line 2";
        }
        """
        tokens = MOD.tokenize_liberty(snippet)
        self.assertIn("library", tokens)
        self.assertIn("demo", tokens)
        self.assertIn("str", tokens)
        self.assertNotIn("Multi-line", tokens)
        self.assertNotIn("Line comment", tokens)

    def test_tokenizer_unterminated_block_comment(self):
        with self.assertRaises(ValueError):
            MOD.tokenize_liberty("library (test) { /* unclosed comment")

    def test_tokenizer_unterminated_string(self):
        with self.assertRaises(ValueError):
            MOD.tokenize_liberty('library (test) { key : "unclosed string; }')

    def test_tokenizer_standalone_slash(self):
        with self.assertRaises(ValueError):
            MOD.tokenize_liberty("library (test) { key / value; }")

    def test_tokenizer_standalone_star(self):
        with self.assertRaises(ValueError):
            MOD.tokenize_liberty("library (test) { key * value; }")

    def test_parse_liberty_group_hierarchy(self):
        lib = MOD.parse_liberty(build_synthetic_lib_text())
        self.assertEqual(lib.name, "library")
        self.assertEqual(lib.args, ["sg13g2_io_typ_1p2V_3p3V_25C"])
        c_out4 = MOD.find_cell(lib, "sg13g2_IOPadOut4mA")
        self.assertIsNotNone(c_out4)
        arc = MOD.match_timing_arc(c_out4, "pad", "c2p")
        self.assertIsNotNone(arc)

    def test_parse_liberty_unclosed_group(self):
        with self.assertRaises(ValueError):
            MOD.parse_liberty("library (test) { cell (c) { pin (p) { } }")

    def test_metadata_validation(self):
        valid_lib = MOD.parse_liberty(build_synthetic_lib_text())
        MOD.validate_liberty_metadata(valid_lib, "test_valid")

        bad_time = build_synthetic_lib_text().replace('"1ns"', '"1ps"')
        with self.assertRaises(ValueError):
            MOD.validate_liberty_metadata(MOD.parse_liberty(bad_time), "bad_time")

        bad_cap = build_synthetic_lib_text().replace("(1, pf)", "(1, ff)")
        with self.assertRaises(ValueError):
            MOD.validate_liberty_metadata(MOD.parse_liberty(bad_cap), "bad_cap")

        bad_thresh = build_synthetic_lib_text().replace(
            "slew_lower_threshold_pct_rise : 10;",
            "slew_lower_threshold_pct_rise : 20;"
        )
        with self.assertRaises(ValueError):
            MOD.validate_liberty_metadata(MOD.parse_liberty(bad_thresh), "bad_thresh")

    def test_table_validation(self):
        i1 = [0.1, 0.2]
        i2 = [1.0, 2.0]
        MOD.validate_table(i1, i2, [[1.0, 2.0], [3.0, 4.0]], "valid")

        with self.assertRaises(ValueError):
            MOD.validate_table([0.2, 0.1], i2, [[1.0, 2.0], [3.0, 4.0]], "not_incr")

        with self.assertRaises(ValueError):
            MOD.validate_table(i1, [2.0, 1.0], [[1.0, 2.0], [3.0, 4.0]], "not_incr2")

        with self.assertRaises(ValueError):
            MOD.validate_table(
                [0.1, float("nan")], i2, [[1.0, 2.0], [3.0, 4.0]], "nan_i1"
            )

        with self.assertRaises(ValueError):
            MOD.validate_table(i1, i2, [[1.0, float("inf")], [3.0, 4.0]], "inf_val")

    def test_arc_matching_positive_unate_unconditional(self):
        lib_valid = MOD.parse_liberty(build_synthetic_lib_text())
        cell = MOD.find_cell(lib_valid, "sg13g2_IOPadOut4mA")
        arc = MOD.match_timing_arc(cell, "pad", "c2p")
        self.assertEqual(str(arc.get_attribute("timing_sense")), "positive_unate")

        lib_cond = MOD.parse_liberty(build_synthetic_lib_text(add_condition=True))
        cell_cond = MOD.find_cell(lib_cond, "sg13g2_IOPadOut4mA")
        with self.assertRaises(ValueError):
            MOD.match_timing_arc(cell_cond, "pad", "c2p")

    def test_analog_sentinel_detection(self):
        lib = MOD.parse_liberty(build_synthetic_lib_text())
        analog_cell = MOD.find_cell(lib, "sg13g2_IOPadAnalog")
        is_sentinel, reason = MOD.check_analog_sentinel(analog_cell)
        self.assertTrue(is_sentinel)
        self.assertIn("static sentinel", reason)

        out_cell = MOD.find_cell(lib, "sg13g2_IOPadOut4mA")
        is_sentinel_out, _ = MOD.check_analog_sentinel(out_cell)
        self.assertFalse(is_sentinel_out)

    def test_interpolation_exact_and_anti_extrapolation(self):
        i1 = [0.1, 0.5]
        i2 = [1.0, 5.0, 10.0]
        vals = [[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]]
        loads = [1.0, 5.0, 10.0]

        curve0 = MOD.interp_curve(i1, i2, vals, 0.1, loads)
        np.testing.assert_allclose(curve0, [10.0, 20.0, 30.0])

        with self.assertRaises(ValueError):
            MOD.interp_curve(i1, i2, vals, 0.05, loads)
        with self.assertRaises(ValueError):
            MOD.interp_curve(i1, i2, vals, 0.6, loads)
        with self.assertRaises(ValueError):
            MOD.interp_curve(i1, i2, vals, 0.2, [0.5])
        with self.assertRaises(ValueError):
            MOD.interp_curve(i1, i2, vals, 0.2, [15.0])

    def test_safe_percent_diff(self):
        d1, p1 = MOD.safe_percent_diff(100.0, 110.0)
        self.assertAlmostEqual(d1, 10.0)
        self.assertAlmostEqual(p1, 10.0)

        d0, p0 = MOD.safe_percent_diff(0.0, 5.0)
        self.assertAlmostEqual(d0, 5.0)
        self.assertIsNone(p0)

    def test_compare_cells_disjoint_intervals_and_points(self):
        lib0 = MOD.parse_liberty(build_synthetic_lib_text(max_load=5.0))
        lib1 = MOD.parse_liberty(build_synthetic_lib_text(max_load=10.0))

        with self.assertRaises(ValueError):
            MOD.compare_cells(lib0, lib1, slew_ns=0.1, num_points=1)

    def test_plot_grid_text_bounds_not_clipped(self):
        lib0 = MOD.parse_liberty(build_synthetic_lib_text(scale=1.0))
        lib1 = MOD.parse_liberty(build_synthetic_lib_text(scale=1.05))
        res, _ = MOD.compare_cells(lib0, lib1, slew_ns=0.1, num_points=5)

        with tempfile.TemporaryDirectory() as tmpdir:
            p_png = Path(tmpdir) / "test.png"
            p_svg = Path(tmpdir) / "test.svg"
            title_lines = [
                "IHP Published Liberty Characterization: Output Drivers",
                "origin/dev (22f43352) vs origin/IO-xschem (8d3ee38d)",
                "Typ 1.2V/3.3V, 25°C | Published Liberty tables (not new PEX)",
            ]
            MOD.plot_grid(
                ["sg13g2_IOPadOut4mA"], res,
                "dev (22f43352)", "io (8d3ee38d)",
                title_lines, p_png, p_svg
            )
            self.assertTrue(p_png.is_file())
            self.assertTrue(p_svg.is_file())

            fig, ax = plt.subplots(figsize=(11, 4))
            st = fig.suptitle("\n".join(title_lines), fontsize=10, weight="bold")
            fig.canvas.draw()
            r = fig.canvas.get_renderer()
            fig_w = fig.get_window_extent(r).width
            st_box = st.get_window_extent(r)
            self.assertGreaterEqual(st_box.x0, 0.0)
            self.assertLessEqual(st_box.x1, fig_w)
            plt.close(fig)

    def test_portable_git_operations(self):
        sha0 = "1111111111111111111111111111111111111111"
        short0 = sha0[:8]
        sha1 = "2222222222222222222222222222222222222222"
        short1 = sha1[:8]
        lib0_text = build_synthetic_lib_text(scale=1.0)
        lib1_text = build_synthetic_lib_text(scale=1.05)

        def fake_run_git_cmd(repo_dir, args):
            if len(args) == 3 and args[0] == "rev-parse" and args[1] == "--short":
                return f"{args[2][:8]}\n".encode("utf-8")
            if args == ["rev-parse", "dev"]:
                return f"{sha0}\n".encode("utf-8")
            if args == ["rev-parse", "IO-xschem"]:
                return f"{sha1}\n".encode("utf-8")
            if len(args) == 2 and args[0] == "show":
                spec = args[1]
                if spec.startswith(sha0) or spec.startswith("dev"):
                    return lib0_text.encode("utf-8")
                if spec.startswith(sha1) or spec.startswith("IO-xschem"):
                    return lib1_text.encode("utf-8")
                raise subprocess.CalledProcessError(1, ["git"] + args)
            if args == ["remote", "get-url", "origin"]:
                return b"https://github.com/IHP-GmbH/IHP-Open-PDK.git\n"
            raise subprocess.CalledProcessError(1, ["git"] + args)

        with tempfile.TemporaryDirectory() as tmp_git:
            repo_dir = Path(tmp_git)
            with patch.object(MOD, "run_git_cmd", side_effect=fake_run_git_cmd):
                sha0_res, short0_res = MOD.resolve_commit_info(repo_dir, "dev")
                sha1_res, short1_res = MOD.resolve_commit_info(repo_dir, "IO-xschem")
                self.assertNotEqual(sha0_res, sha1_res)
                self.assertEqual(sha0_res, sha0)
                self.assertEqual(short0_res, short0)
                self.assertEqual(sha1_res, sha1)
                self.assertEqual(short1_res, short1)

                blob, path_used = MOD.load_lib_from_git(
                    repo_dir, sha0,
                    "libs.ref/sg13g2_io/lib/sg13g2_io_typ_1p2V_3p3V_25C.lib"
                )
                self.assertIn("library", blob.decode("utf-8"))

                with tempfile.TemporaryDirectory() as outdir:
                    artifacts = MOD.run_comparison(
                        pdk_repo=repo_dir,
                        refs=("dev", "IO-xschem"),
                        output_dir=outdir,
                        slew_ns=0.1,
                        lib_path=(
                            "libs.ref/sg13g2_io/lib/sg13g2_io_typ_1p2V_3p3V_25C.lib"
                        ),
                        num_points=5,
                    )
                    self.assertIn("summary", artifacts)
                    self.assertTrue((Path(outdir) / "summary.json").is_file())
                    self.assertTrue((Path(outdir) / "output_timing.png").is_file())
                    self.assertTrue((Path(outdir) / "output_timing.svg").is_file())
                    self.assertTrue((Path(outdir) / "input_timing.png").is_file())
                    self.assertTrue((Path(outdir) / "input_timing.svg").is_file())
                    self.assertTrue((Path(outdir) / "sampled_curves.csv").is_file())

                    snap0 = Path(outdir) / (
                        f"sg13g2_io_typ_1p2V_3p3V_25C_dev_{short0}.lib"
                    )
                    snap1 = Path(outdir) / (
                        f"sg13g2_io_typ_1p2V_3p3V_25C_IO-xschem_{short1}.lib"
                    )
                    self.assertTrue(snap0.is_file())
                    self.assertTrue(snap1.is_file())
                    self.assertEqual(snap0.read_bytes(), lib0_text.encode("utf-8"))
                    self.assertEqual(snap1.read_bytes(), lib1_text.encode("utf-8"))

                    prov = artifacts["summary"]["provenance"]
                    self.assertEqual(prov["ref_0"]["commit_sha"], sha0)
                    self.assertEqual(prov["ref_1"]["commit_sha"], sha1)
                    self.assertEqual(prov["ref_0"]["short_sha"], short0)
                    self.assertEqual(prov["ref_1"]["short_sha"], short1)
                    self.assertEqual(
                        prov["remote_origin_url"],
                        "https://github.com/IHP-GmbH/IHP-Open-PDK.git",
                    )

    def test_compare_interp_rejects_nan_inf_slew_and_loads(self):
        i1 = [0.1, 0.5]
        i2 = [1.0, 5.0, 10.0]
        vals = [[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]]
        valid_loads = [1.0, 5.0, 10.0]

        for bad_slew in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                MOD.interp_curve(i1, i2, vals, bad_slew, valid_loads)

        for bad_loads in (
            [float("nan")],
            [float("inf")],
            [float("-inf")],
            [1.0, float("nan"), 5.0],
            [1.0, float("inf"), 5.0],
            [1.0, float("-inf"), 5.0],
        ):
            with self.assertRaises(ValueError):
                MOD.interp_curve(i1, i2, vals, 0.2, bad_loads)

        lib0 = MOD.parse_liberty(build_synthetic_lib_text(scale=1.0))
        lib1 = MOD.parse_liberty(build_synthetic_lib_text(scale=1.05))

        for bad_slew in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                MOD.compare_cells(lib0, lib1, slew_ns=bad_slew, num_points=5)
            with self.assertRaises(ValueError):
                MOD.compare_cells(
                    lib0, lib1, slew_ns=0.1, in_slew_ns=bad_slew, num_points=5
                )

    def test_metadata_rejects_mislabeled_corner_and_units(self):
        original = build_synthetic_lib_text()
        for before, after in (
            ("capacitive_load_unit (1, pf)", "capacitive_load_unit (10, pf)"),
            ("temperature : 25", "temperature : 125"),
            ("voltage_map (iovdd, 3.3)", "voltage_map (iovdd, 3.6)"),
            ("voltage_map (vdd, 1.2);", ""),
        ):
            with self.subTest(after=after), self.assertRaises(ValueError):
                MOD.validate_liberty_metadata(
                    MOD.parse_liberty(original.replace(before, after)), "fixture"
                )

    def test_cli_arg_parse(self):
        args = MOD.parse_args(["--slew-ns", ".1", "--output", "/tmp/out_test"])
        self.assertAlmostEqual(args.slew_ns, 0.1)
        self.assertEqual(args.output, "/tmp/out_test")
        self.assertEqual(args.refs, ["origin/dev", "origin/IO-xschem"])

    def test_optional_ihp_pdk_integration(self):
        pdk_dir = ROOT / "IHP-Open-PDK"
        if not pdk_dir.is_dir():
            self.skipTest("IHP-Open-PDK directory not found")

        try:
            res = subprocess.run(
                [
                    "git", "-C", str(pdk_dir), "cat-file", "-t",
                    "22f43352dd8219f9007eb659e422e0d5fe28c5fb"
                ],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if res.returncode != 0:
                self.skipTest("Specific immutable SHA not in PDK submodule")
        except Exception:
            self.skipTest("Git inspection failed")

        blob, _ = MOD.load_lib_from_git(
            pdk_dir, "22f43352dd8219f9007eb659e422e0d5fe28c5fb",
            "ihp-sg13g2/libs.ref/sg13g2_io/lib/sg13g2_io_typ_1p2V_3p3V_25C.lib"
        )
        self.assertIn("sg13g2_IOPadOut4mA", blob.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
