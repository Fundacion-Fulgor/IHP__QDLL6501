# QDLL6501 datasheet

## Document scope

This preliminary datasheet describes the checked-out design at source revision
`227f809efd0bbee771a714ff6b9c48f825c4f215`, reviewed on 2026-09-18.
The current release is `v.2.0.0` (commit `b5cb328`). Electrical values below
are simulation results or design targets, not silicon measurements or
guaranteed operating limits.

| Item | Current value |
| --- | --- |
| Design | Quadrature delay-locked loop with externally controlled and fixed-delay test paths |
| Technology | IHP SG13G2, 130 nm CMOS devices |
| Core top cell | `QDLL_TOP` |
| Release GDS | `release/v.2.0.0/gds/QDLL_TOP.gds` |
| Release version | `v.2.0.0` |
| Nominal core supply | 1.2 V relative to `VSS` |
| Nominal input frequency | 250 MHz |
| Clock interface | Single-ended CMOS |
| Maturity | Self-assessed TRL 3: schematic proof of concept; qualification incomplete |
| License | Apache-2.0 |

See [Specifications](Specifications.md) for acceptance criteria and
[TRL assessment](TRL-Analog.md) for the evidence and remaining work.

## Functional description

The [top-level schematic](../QDLL6501-main/schematic/xschem/QDLL_TOP.sch)
contains three paths:

| Path | Operation |
| --- | --- |
| `IN1` to `OUT1` | Closed-loop DLL. A current-starved VCDL and fixed delay/buffer chain feed an XOR phase detector. Its filtered output controls the VCDL internally. The target phase delay is 90 degrees. |
| `IN2` to `OUT2` | Externally controlled VCDL and delay/buffer chain. Drive `VCONT2` externally; `CPOUT2` exposes the filtered phase-detector output. These pins are not internally tied. |
| `IN3` to `OUT3` | Fixed, inverting delay-line monitor. It uses the full-strength `DLine` chain ending in `sg13g2_inv_16`. |

The block named `CP` is a passive RC loop filter, not a switched charge pump.
Its schematic uses twelve series `rppd` resistors, each 1 µm wide and 10 µm
long, and one enabled 60 µm by 20 µm `cap_cmim`. The additional capacitor
instances in `CP.sch` are marked `spice_ignore=true`.

In `v.2.0.0`, the core schematic incorporates:
1. A supply decoupling capacitor `C1` (`cap_cmim`, 25.5 µm by 6.99 µm, ~267 fF)
   connected between `VDD` and `VSS`.
2. Antenna protection diodes `x10` and `x11` (`sg13g2_antennanp`) connected on
   the internal control net `VCONT` and pin `VCONT2`.
3. Widened M3 and M4 interconnect lines (up to 0.5 to 1.0 µm) on critical clock
   and control paths in the layout.
4. TopMetal2 artwork logo without passivation opening (the opening layer was
   removed in commit `8b6a6d2`).

The first two paths are non-inverting overall. `OUT3` transitions with the
opposite polarity to `IN3`. The core has no register interface, reset pin,
enable pin, or lock-status output.

## Core pinout

| Pin | Direction | Function |
| --- | --- | --- |
| `VDD` | Supply | Core positive supply, nominally 1.2 V |
| `VSS` | Supply | Core ground reference |
| `IN1` | Input | Reference clock for the internally controlled DLL |
| `OUT1` | Output | Clock output of the internally controlled DLL |
| `IN2` | Input | Reference clock for the externally controlled path |
| `OUT2` | Output | Clock output of the externally controlled path |
| `VCONT2` | Analog input | External VCDL control voltage for path 2 |
| `CPOUT2` | Analog output | RC-filtered phase-detector voltage for path 2 |
| `IN3` | Input | Reference clock for the fixed delay-line monitor |
| `OUT3` | Output | Inverted, delayed monitor clock |

The top-level SPICE order used by the CACE testbenches is:

```text
QDLL_TOP VDD VSS IN1 OUT1 OUT2 IN2 CPOUT2 VCONT2 IN3 OUT3
```

These are core ports, not package pin numbers. Clock stimuli span `VSS` to
`VDD`; `VCONT2` is exercised within the same range. No absolute-maximum,
input-threshold, ESD, or output-current ratings are established here.
Pad/wrapper testbenches have separate 3.3 V IO supplies; this does not make
the 1.2 V core pins 3.3 V tolerant.

## Intended operating conditions

These conditions come from [the CACE configuration](../cace/QDLL_TOP.yaml).
A declared sweep is not evidence that every point passed.

| Parameter | Minimum | Typical | Maximum |
| --- | ---: | ---: | ---: |
| Core supply | 1.14 V | 1.20 V | 1.26 V |
| Input frequency | 225 MHz | 250 MHz | 275 MHz |
| Temperature | 0 °C | 65 °C | 125 °C |
| Process corners | SS | TT | FF |
| OUT3 test load | 100 fF | 300 fF | 350 fF |

OUT3 loads are three enumerated test points, not a continuous guaranteed load
range. The global CACE default load is 100 fF. The quadrature target is
90 ± 5 degrees, equivalent to a 1 ns nominal delay at 250 MHz; current evidence
does not establish compliance across these conditions.

## Nominal OUT3 simulation snapshot

The local CACE run `runs/RUN_2026-09-02_21-05-53/summary.md` reports the
following schematic-level results at TT, 1.2 V, 65 °C, 250 MHz and 350 fF.
`runs/` is Git-ignored; these values are transcribed here so the result and its
scope are recorded, but the raw run is not part of a fresh clone.

| Metric | Acceptance limit | Simulated value |
| --- | --- | ---: |
| Falling output delay | ≤ 1200 ps | 705.450 ps |
| Rising output delay | ≤ 1200 ps | 744.210 ps |
| Rising slew, 10% to 90% | ≤ 500 ps | 143.063 ps |
| Falling slew, 90% to 10% | ≤ 500 ps | 109.228 ps |
| High pulse width | ≥ 1.4 ns | 1.951 ns |
| Low pulse width | ≥ 1.4 ns | 2.049 ns |
| Maximum transient output voltage | ≥ 1.0 V | 1.221 V |
| Minimum transient output voltage | ≤ 0.1 V | -0.018 V |

All eight checks pass at this point. The voltage checks use the maximum and
minimum over the transient, including overshoot and undershoot; they are not
settled DC `VOH`/`VOL` guarantees. Delay uses 50% crossings, with input rising
to output falling and input falling to output rising. The test drives only
`IN3`, holds `IN1` and `IN2` low, and biases `VCONT2` at `VDD/2`.
The load is an ideal capacitor on the core output, without an IO pad or package.

The repository does not yet provide a qualified numerical power budget,
closed-loop phase-error sweep, lock-time limit, control-voltage ripple limit,
or output jitter specification. Exploratory notebook figures are not used as
ratings; see the verification gaps in [Specifications](Specifications.md).

## Layout and verification

The [release v2.0.0 GDS](../release/v.2.0.0/gds/QDLL_TOP.gds) has a `QDLL_TOP`
bounding box of 918.035 µm by 516.800 µm, including the logo and separated
layout structures. This is neither the active circuit area nor a sealed die
size. No `EdgeSeal.drawing` geometry (39/0) is present in this cell. The
`sealring_x` and `sealring_y` values in [info.json](info.json) remain inherited
metadata, not verified sealring dimensions.

| Check | Saved evidence | Qualification |
| --- | --- | --- |
| DRC | Main, antenna, and maximal checks were reported clean during layout development (commits `419f122` and `31010b4`) | Archived report in `drc/` dates to 2026-09-09 (`v.1.0.0`); an archived runset report specifically for `release/v.2.0.0/gds/QDLL_TOP.gds` is pending |
| LVS | Final execution in [lvs_run_2026_09_11_12_12_30.log](../lvs/lvs_run_2026_09_11_12_12_30.log) ends with `Netlists match` | Device/connectivity comparison on the v2 layout basis (`QDLL_TOP_test.gds`); the summary also records errors from earlier appended runs |
| PEX and post-layout timing | No validated full-core parasitic netlist and PVT result set identified | Pending |
| Fabrication and silicon measurements | No supporting evidence in this snapshot | Not claimed |

Release artifact synchronization for `v.2.0.0` remains partial: `release/v.2.0.0/`
currently contains `gds/QDLL_TOP.gds`; standalone `netlist/` and `doc/`
directories under `release/v.2.0.0/` are not yet populated. The updated
schematic netlist is tracked at
[simulation/QDLL_TOP.spice](../QDLL6501-main/schematic/xschem/simulation/QDLL_TOP.spice).
The standalone logo generator currently writes only TopMetal2; its requested
ground connection and passivation-opening feature are not implemented or
qualified in this snapshot.

## Reproducing characterization

From the repository root, initialize dependencies and enter the tool container
before loading the project environment:

```bash
git submodule update --init --recursive
distrobox enter iic-osic-tools2
source ./SOURCEME
cace cace/QDLL_TOP.yaml -s schematic
```

To repeat the nominal OUT3 point from a host shell at the repository root:

```bash
./plot-cace run out3_timing --typical --set cload=350
```

`cload` is in fF. The helper runs inside `iic-osic-tools2`. CACE 2.9.0 is the
recorded characterization version; SG13G2 simulation requires ngspice 40 or
later with OSDI support and compiled PSP103 models. Xschem, KLayout and the
pinned standard-cell/device libraries are also required. The commands above
are reproduction instructions, not a claim that characterization was rerun
for this documentation update.
