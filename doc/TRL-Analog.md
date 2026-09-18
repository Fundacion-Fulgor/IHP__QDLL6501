# QDLL6501 analog/mixed-signal TRL assessment

Reviewed on 2026-09-18 against source revision
`227f809efd0bbee771a714ff6b9c48f825c4f215` and release `v.2.0.0`
(commit `b5cb328`).

The self-assessed maturity is **TRL 3: schematic proof of concept**.
Schematic simulation and an updated physical implementation are available,
including device-level LVS passes on the v2 layout test. Full electrical
qualification, validated parasitic extraction and post-layout PVT
characterization remain incomplete. There is no silicon-validation claim.

This assessment uses the requested `TRL-Analog.md` filename. QDLL combines
analog control and digital delay cells, so [info.json](info.json) retains
`design_type: "M"`. The existing [mixed-signal checklist](TRL-Mixed-Signal-IP.md)
is an unfilled template, not a separate current maturity claim. A checked item
below means supporting evidence exists within the stated scope; it does not
certify every criterion at that level.

## TRL 1: basic principles

- [x] Function and operating principle documented in [Datasheet](Datasheet.md).
- [x] Phase-to-delay and ideal XOR-average relationships described in [Specifications](Specifications.md).
- [x] Schematic transient simulations and analysis files available in [QDLL6501-main/python](../QDLL6501-main/python/).
- [ ] Validated behavioral/Verilog-A model and complete loop-design analysis supplied.

## TRL 2: concept and architecture

- [x] Closed-loop path, externally controlled path and fixed-delay monitor identified.
- [x] VCDL, delay chain, XOR detector and passive RC filter schematics available.
- [x] Block testbenches and a parameterized [CACE setup](../cace/QDLL_TOP.yaml) supplied.
- [ ] Numerical requirements finalized for tuning range, phase-detector gain, power, settling, ripple and jitter.

There is no internal register map or software protocol. The interface consists
of supply, clock and analog-control ports.

## TRL 3: schematic proof of concept

- [x] Transistor-level analog and gate-level digital schematics supplied in [the schematic directory](../QDLL6501-main/schematic/xschem/).
- [x] Decoupling capacitor `CC1` and antenna diodes `x10` and `x11` integrated into the v2 schematic netlist.
- [x] Device, standard-cell and IO-view dependencies identified and pinned through parent gitlinks.
- [x] Core port functions, signal polarity and intended supply domain documented.
- [x] Schematic testbenches and reproduction commands supplied.
- [x] A local nominal OUT3 run passes all eight configured checks; values and provenance are transcribed in [Datasheet](Datasheet.md#nominal-out3-simulation-snapshot).
- [ ] Absolute-maximum, input-threshold, output-drive and package-level electrical ratings established.
- [ ] Repeatable closed-loop phase and jitter acceptance tests archived.

The nominal OUT3 result is schematic-level, at TT, 1.2 V, 65 °C, 250 MHz and
350 fF. Its source directory under `runs/` is Git-ignored. It does not establish
PVT coverage, closed-loop accuracy or pad-loaded performance. TRL 3 describes
the demonstrated development stage, not complete specification compliance.

## TRL 4: fully characterized schematic design

- [x] Process, voltage, temperature, frequency and OUT3 load sweeps declared in CACE.
- [x] Core supply domain and nominal conditions documented.
- [ ] Complete, reproducible electrical PVT pass reports archived.
- [ ] Monte Carlo/mismatch results and yield targets supplied.
- [ ] Power budget and stimulus/load-dependent consumption characterized with numerical limits.
- [ ] Closed-loop acquisition, phase error, duty-cycle sensitivity, ripple and output jitter qualified.

The CACE delay-range, current and detector-gain specifications use `any`, so
successful execution alone cannot establish compliance. The exploratory phase
notebook also needs corrected signal pairing and corner/time-base handling
before its numbers can be used as output specifications.

## TRL 5: layout and post-layout validation

- [x] [Release v2.0.0 layout](../release/v.2.0.0/gds/QDLL_TOP.gds) and updated schematic netlist [simulation/QDLL_TOP.spice](../QDLL6501-main/schematic/xschem/simulation/QDLL_TOP.spice) available.
- [x] Device-level LVS passes on the v2 layout test `QDLL_TOP_test.gds` ([lvs_run_2026_09_11_12_12_30.log](../lvs/lvs_run_2026_09_11_12_12_30.log)).
- [ ] Archived DRC runset report specifically for `release/v.2.0.0/gds/QDLL_TOP.gds` generated and stored in `drc/`.
- [ ] Release GDS, schematic netlist, pinned verification deck and reports archived together; standalone `netlist/` and `doc/` directories in `release/v.2.0.0/` populated.
- [ ] Validated parasitic RC extraction and simulator-ready PEX netlist available.
- [ ] Post-layout PVT characterization, including IO/interconnect loading, completed.
- [ ] Full-chip supply connectivity, pads, fill/density, sealring and logo ground/opening geometry verified.

Development commits report clean main, antenna and maximal DRC during layout
routing. An archived runset report specifically for `release/v.2.0.0/gds/QDLL_TOP.gds`
remains to be stored in `drc/`. `QDLL_TOP_extracted.cir` and `QDLL_TOP_test_extracted.cir`
contain extracted devices for LVS; they are not validated parasitic RC netlists.
Exploratory IO-cell PEX work or published Liberty data cannot substitute for
full-core post-layout validation.

## TRL 6: integration readiness

- [x] Wrapper/pad layout work and IO testbench sources exist in [QDLL6501-main](../QDLL6501-main/).
- [ ] Final integration pinout, supply/ground domains and loading contract qualified together.
- [ ] Integration descriptors/models and system-level checks completed.
- [ ] Final release acceptance and tapeout review recorded.

The release cell has no EdgeSeal geometry. Its 918.035 µm by 516.800 µm
bounding box includes artwork and is not a verified sealed-die dimension.
The standalone logo generator's passivation openings and ground routing
remain pending.

## TRL 7: laboratory demonstrator

- [ ] Fabricated test chip and test setup documented.
- [ ] Laboratory electrical measurements available.
- [ ] Silicon results compared with post-layout predictions.

## TRL 8: system demonstrator

- [ ] Operation validated in the intended integrated system.
- [ ] System-level measurements and correlation reports available.

## TRL 9: qualified application

- [ ] Production qualification, reliability and application evidence available.
- [ ] Release support and maintenance obligations established.

## Work required to advance

1. Define the remaining electrical limits, repair the phase/jitter analysis and
   archive reproducible schematic PVT and mismatch results.
2. Generate an archived DRC runset report for `release/v.2.0.0/gds/QDLL_TOP.gds`,
   populate `release/v.2.0.0/netlist/` and `release/v.2.0.0/doc/`, validate parasitic
   extraction, and run post-layout characterization.
3. Complete pad, ground, sealring, fill and artwork integration before claiming
   full-chip signoff; fabrication and measured silicon results follow that work.
