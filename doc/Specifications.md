# QDLL6501 specifications

## Baseline and interpretation

Reviewed on 2026-09-18 against source revision
`00155c5401feb180eba1e244077bb0e48190fef6` and the available `v.1.0.0`
release. These requirements describe the checked-out design, not newer
unmerged changes on `origin/main`.

[Datasheet](Datasheet.md) records the interface and nominal simulation
snapshot. [TRL assessment](TRL-Analog.md) records maturity and missing
qualification. Numerical acceptance limits below are targets unless a result
is explicitly identified. No silicon ratings are claimed.

## Architecture requirements

| Block or path | Implemented function | Verification requirement |
| --- | --- | --- |
| VCDL | Six-transistor current-starved inverting delay element, using SG13G2 low-voltage MOS devices | Establish useful control range, delay range and monotonicity over PVT |
| `DLine` | `sg13g2_dlygate4sd3_1`, `sg13g2_dlygate4sd2_1`, then `sg13g2_inv_4`, `sg13g2_inv_8`, `sg13g2_inv_16` | Check delay, slew, pulse width and swing under the specified load |
| `PD` | `sg13g2_xor2_1` phase detector | Characterize the average output versus phase and duty cycle |
| `CP` | Passive RC low-pass filter: twelve series 1 µm by 10 µm `rppd` resistors and one enabled 60 µm by 20 µm `cap_cmim` | Establish ripple, settling and PVT sensitivity; this is not a switched charge pump |
| `IN1` to `OUT1` | Internally controlled, non-inverting DLL path | Target 90 ± 5 degrees delay at the specified input frequencies |
| `IN2` to `OUT2` | Non-inverting path with external `VCONT2` and separate `CPOUT2` monitor | Characterize open-loop tuning and filtered detector response |
| `IN3` to `OUT3` | Inverting, full-strength fixed-delay monitor | Meet the OUT3 limits below; no `DLineLP` is used |

For periodic clocks, phase delay and time delay are related by
`phase_deg = 360 × fin × delay_s`. A 90-degree delay is `1/(4 × fin)`:
1 ns at 250 MHz. For ideal 50%-duty clocks and phase differences from 0 to
π radians, the XOR average is approximately `VDD × phase_rad/π`.
These relations explain the design intent; they do not prove the achieved
closed-loop phase or acquisition range.

Sources: [QDLL_TOP.sch](../QDLL6501-main/schematic/xschem/QDLL_TOP.sch),
[VCDL.sch](../QDLL6501-main/schematic/xschem/VCDL.sch),
[DLine.sch](../QDLL6501-main/schematic/xschem/DLine.sch),
[PD.sch](../QDLL6501-main/schematic/xschem/PD.sch),
[CP.sch](../QDLL6501-main/schematic/xschem/CP.sch) and
[RES.sch](../QDLL6501-main/schematic/xschem/RES.sch).

## Electrical conditions

| Quantity | Declared conditions | Scope |
| --- | --- | --- |
| Core supply | 1.14, 1.20, 1.26 V | `VDD` relative to `VSS`; nominal ±5% range |
| Temperature | 0, 65, 125 °C | CACE test points |
| MOS process corner | TT, FF, SS | Passive models remain typical in the CACE templates |
| Input frequency | 225, 250, 275 MHz | Nominal 250 MHz |
| Clock amplitude | 0 to `VDD` relative to `VSS` | Single-ended, not differential |
| OUT3 input stimulus | Nominal 50% duty cycle, 10 ps rise/fall ramps | Ideal source in `tb_out3.sch` |
| OUT3 load | 100, 300, 350 fF | Ideal capacitive load directly on the core output |
| External control | Within `VSS` to `VDD`; `VDD/2` in the OUT3 test | Guaranteed tuning range remains to be established |

The full declared OUT3 grid contains 243 combinations (three values of each
of five conditions). A nominal result cannot be substituted for that grid.
Older manual testbenches include ±10% supply experiments; these are distinct
from the ±5% CACE specification and do not extend a guaranteed operating range.

Absolute-maximum voltage, input logic thresholds, input capacitance, output
current, ESD robustness and package pin assignments remain unspecified.
Any 3.3 V IO domain belongs to the pad/wrapper interface, not the core.

## Electrical acceptance criteria

The executable measurement definitions are in
[cace/QDLL_TOP.yaml](../cace/QDLL_TOP.yaml) and
[tb_out3.sch](../cace/templates/tb_out3.sch).

| Quantity | Criterion | Definition or current coverage |
| --- | --- | --- |
| Closed-loop phase delay | 85 to 95 degrees | Design target; no qualified automated pass result across PVT |
| OUT3 falling propagation delay | ≤ 1200 ps | Input rising 50% crossing to output falling 50% crossing |
| OUT3 rising propagation delay | ≤ 1200 ps | Input falling 50% crossing to output rising 50% crossing |
| OUT3 rising slew | ≤ 500 ps | Output 10% to 90% of `VDD` |
| OUT3 falling slew | ≤ 500 ps | Output 90% to 10% of `VDD` |
| OUT3 high pulse width | ≥ 1.4 ns | At 50% of `VDD` |
| OUT3 low pulse width | ≥ 1.4 ns | At 50% of `VDD` |
| OUT3 transient maximum voltage | ≥ 1.0 V | Maximum over the simulation, not settled DC `VOH` |
| OUT3 transient minimum voltage | ≤ 0.1 V | Minimum over the simulation, not settled DC `VOL` |
| VCDL minimum, maximum and range of delay | TBD | CACE measurements exist; limits are `any` |
| Static and dynamic supply current | TBD | CACE measurements exist; limits are `any` |
| Phase-detector gain | TBD | CACE measures at a 45-degree offset; limits are `any` |
| Lock/acquisition time and range | TBD | Needs a defined settling window and acquisition criterion |
| Control-voltage ripple | TBD | No numerical acceptance limit established |
| Output jitter | TBD | No qualified output-jitter result established |

`any` requests characterization without a numerical acceptance bound. It must
not be reported as proof that a power, tuning or detector-gain specification
has been met. OUT3 limits do not establish OUT1/OUT2 loaded-loop performance.

## Available results and limitations

The [datasheet nominal table](Datasheet.md#nominal-out3-simulation-snapshot)
transcribes the local 2026-09-02 OUT3 run at TT, 1.2 V, 65 °C, 250 MHz and
350 fF. All eight criteria passed at that point. Its raw files are ignored
under `runs/`; a clone must regenerate them. No complete archived CACE PVT
report is identified for all parameters in this snapshot.

Schematic transient data and exploratory analyses are available under
[QDLL6501-main/python](../QDLL6501-main/python/), but the saved
[phase-analysis notebook](../QDLL6501-main/python/phase_analysis_example.ipynb)
has inconsistent input/output pairing, an unpacking exception in the corner
analysis, and a jitter calculation using input signals with a shared TT time
base. Its displayed phase and jitter numbers are not accepted specifications.
Phase sign convention, output signal selection, settling window and per-run
time bases must be fixed and verified before publishing closed-loop results.

## Physical acceptance and release requirements

| Requirement | Evidence or remaining work |
| --- | --- |
| Core layout available | `release/v.1.0.0/gds/QDLL_TOP.gds`, top cell `QDLL_TOP` |
| Layout size recorded | Bounding box 918.035 µm by 504.530 µm including logo; no sealring in this cell |
| DRC | The saved 2026-09-09 main, antenna and maximal run reports zero violations; retain its deck/configuration qualification |
| LVS | Final 2026-09-09 device-level comparison matches; earlier failures remain in the cumulative log |
| Release consistency | Reconcile the older failing DRC report beside the GDS, source schematics and release netlists; archive hashes and fresh reports together |
| Parasitic extraction | Produce and validate a simulator-ready parasitic RC netlist; an LVS device netlist is insufficient |
| Post-layout characterization | Repeat phase, tuning, power and timing checks across PVT with pad/interconnect loading |
| Full-chip integration | Verify pads, supply/substrate connectivity, sealring, fill/density and integration-level DRC/LVS |
| Logo integration | The standalone generator currently emits only TopMetal2; ground routing and legal passivation openings still require implementation and verification |
| Fabrication and measurements | No silicon-validation evidence in this snapshot |

The passing [DRC log](../drc/drc_run_2026_09_09_20_59_08.log) identifies
KLayout 0.30.11 and `/foss/pdks/.../sg13g2_tech_mod.json`; it does not record
an exact match to the pinned PDK commit. Its main log records
`PreCheck DRC enabled: false`. This mode setting alone does not establish
whether all submission checks were covered; check the selected runsets
against the required tapeout checks before signoff. The antenna log also
records fallback rule values. Saved block-level checks are not full-chip
foundry acceptance.

The [release netlist](../release/v.1.0.0/netlist/QDLL_TOP.spice) contains
LVS-oriented primitive device records and an older hierarchy. Generate
simulation netlists from the current Xschem sources rather than treating
that file, or [the LVS extraction](../lvs/QDLL_TOP_extracted.cir), as a
validated ngspice PEX deck.

## Dependencies and tool provenance

| Dependency | Pinned revision in the reviewed parent commit |
| --- | --- |
| `IHP-Open-PDK` | `cfc0e22b92306178ebb5a5bc4865afe3294654d0` |
| `openpdk-libraries` | `7d06b8ac9b453522ad6775bf5da16c8226616f52` |
| Logo `artistic` submodule | `31277dfbcb5f15d219c9834bc9e6f1c9b4705bf3` |

The PDK supplies device models and `sg13g2_stdcell`; `openpdk-libraries`
supplies IO schematic/symbol views. These pins describe the parent repository
baseline, not uncommitted changes inside dependencies. Use `.gitmodules` and
the parent gitlinks to reproduce it.

CACE 2.9.0 is recorded in the project setup. KLayout 0.30.11 is recorded in
the saved DRC/LVS runs. Xschem and ngspice with OSDI/PSP103 support are required
for schematic simulation; a complete version manifest remains to be archived.
The catalog retains the process identifier `SG13CMOS`; the design PDK is
`ihp-sg13g2`. The inherited `sealring_x`/`sealring_y` metadata is not a
measurement of the release layout. Reproduction commands are in
[Datasheet](Datasheet.md#reproducing-characterization).
