# IHP__QDLL6501

## 💬 Team & Acknowledgements

This project was developed by students from Fulgor Foundation as part of the UNIC-CASS open-source tapeout program.

**Team Members:**
- Leonardo David Vazquez — Project Lead,  Integration and Analog Design
- Martín Doric — Project Lead,, Layout Consultant
- Santiago Basignana — Layout Designer
- Mateo Buteler — Toolflow Integration
- Clemente Molinari - Analog Verification


# QDLL - Quadrature Delay Locked Loop

QDLL is a full-custom analog integrated circuit developed using the open-source SG13G2 PDK from IHP.  
The design features two parallel delay-locked loops (DLLs) targeting timing alignment and phase synchronization applications, suitable for use at ~250 MHz.

---

## 🔧 Project Goals

- Design and tapeout of a QDLL using the IHP SG13G2 130nm process.
- Validate timing alignment through post-layout simulations.
- Use only **open-source EDA tools** including Magic, KLayout, Xschem, ngspice, python tools and others.
- Participate in the UNIC-CASS tapeout program for educational and research purposes.

---

## 🧩 Project Structure (Folder [QDLL](unic_cass_wrapper_analog/QDLL) )

- `Cells/` — Xschem schematics cells and symbols for all blocks, including the QDLL_TOP.
- `Layouts/` — KLayout layout files.
- `python/` — Python codes for post-processing analysis.
- `testbenchs/` — Testbenches for functional simulations.
- `docs/` — Documentation and reports. The Mock Tape-Out Report is: 
[QDLL Mock Tape Out Milestone 1](https://docs.google.com/presentation/d/1buPqdt9BBiQd7oaACnhc4rbIgDi21SVI7TTmWeHhwfk/edit?usp=sharing)
[QDLL Mock Tape Out Milestone 2](https://docs.google.com/presentation/d/1SaUPbj3oBROP9z1-2TtK8tWIxL02-J9qEyfox9xo-iI/edit?usp=sharing)

---

## 🛠 Tools Used

- [Magic VLSI](http://opencircuitdesign.com/magic/)
- [KLayout](https://www.klayout.de/)
- [Xschem](https://github.com/StefanSchippers/xschem)
- [ngspice](http://ngspice.sourceforge.net/)
- [Netgen](http://opencircuitdesign.com/netgen/)
- [OpenPDK (SG13G2)](https://github.com/IHP-GmbH/IHP-Open-PDK)

## Reproducible setup

Initialize the pinned PDK dependency after cloning:

```bash
git submodule update --init --recursive
```

Launch Xschem from the repository root so it loads the project `xschemrc`:

```bash
xschem QDLL6501-main/schematic/xschem/QDLL_TOP.sch
```

The target-adapted CACE 5.2 datasheet is `cace/QDLL_TOP.yaml` and was validated with CACE 2.9.0. Its ngspice templates characterize VCDL delay, current consumption, phase-detector gain, and OUT3 delay, slew, pulse width, and output swing across the specified 225–275 MHz, 1.14–1.26 V, and 0/65/125 °C conditions. The OUT3 test additionally covers 100, 300, and 350 fF loads. The declared schematic-level PVT regressions pass; release layout and extracted-netlist signoff remain pending. SG13G2 transistor simulation requires ngspice 40+ with OSDI enabled and compiled PSP103 models in the PDK.

Run characterization with the pinned PDK explicitly selected:

```bash
export PDK_ROOT="$PWD/IHP-Open-PDK"
export PDK=ihp-sg13g2
cace cace/QDLL_TOP.yaml -s schematic
```

Xschem uses a valid external `PDK_ROOT` when supplied and otherwise falls back to the pinned submodule.

---

## 📐 QDLL Specifications

### 🔧 Boundary Conditions

| **Parameter**        | **Requirement**       |
|----------------------|------------------------|
| Technology           | CMOS                  |
| Node                 | 130 nm                |
| Supply Voltage       | 1.2 ± 5% V            |
| Temperature Range    | [0, 65, 125] °C       |
| Input Amplitude      | [0, 1.2] V (CMOS)     |
| Input Frequency      | 250 ± 25 MHz          |
| Input/Output Type    | Fully Differential     |

### 📊 Performance Specifications

| **Specification**       | **Value**               |
|--------------------------|--------------------------|
| Phase Difference         | 90 ± 5 degrees           |
| Output Swing             | [0, 1.2] V (CMOS)        |
| Output Rise/Fall Time    | < [value TBD]           |
| V<sub>cont</sub> Ripple  | < [value TBD]           |
| Output Jitter            | [value TBD]             |


## 🔌 IO Pin Summary

| **Pin Type**      | **Name**   | **IO Cell**              |
|-------------------|------------|---------------------------|
| Input             | inpad1     | sg13g2_IOPADAnalog        |
| Input             | inpad2     | sg13g2_IOPADAnalog        |
| Output            | outpad1    | sg13g2_IOPADAnalog        |
| Output            | outpad2    | sg13g2_IOPADAnalog        |
| Power Supply      | VDD        | sg13g2_IOPadVdd           |
| Power Supply      | VSS        | sg13g2_IOPadVss           |



## 📏 Estimated Chip Area

- **Dimensions:** 100 µm × 100 µm  
- **Total area:** 10000 µm² = 0.01 mm²


<p align="center">
  <img width="941" height="541" alt="image" src="https://github.com/user-attachments/assets/e3e0819a-c1d5-4399-898d-5d0034b7dd4f" />
</p>


---

## 📅 Current Status

- ✅ Schematic design and functional simulations completed.
- ✅ Layout of core blocks DRC/LVS completed.
- Full SG13G2 DRC of `release/v.1.0.0/gds/QDLL_TOP.gds` currently reports violations in nine rule categories.
- Release GDS/netlist artifacts predate the current source schematic and require regeneration and signoff together.
- 🔄 Post-Layout Simulations In Progress.

- 
<p align="center">
<img width="1314" height="728" alt="image" src="https://github.com/user-attachments/assets/73327962-c8ca-483a-b55b-74c9b348b97e" /
</p>

---

## 💬 Team & Acknowledgements

This project was developed by students from The Fulgor Foundation as part of the UNIC-CASS open-source tapeout program.

Special thanks to:
- Mentor Agustín Carlos Galetto
- Prof. Jorge Marín 
- IHP Microelectronics for the open PDK
- UNIC-CASS and all mentors involved

---

## 📜 License

This project is open-source project.


Refer to [README](https://github.com/unic-cass/unic-cass-wrapper/blob/main/docs/README.md) for this sample project documentation.



