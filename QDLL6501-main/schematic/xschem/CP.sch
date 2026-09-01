v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 0 150 0 170 {lab=VSS}
N -0 0 0 40 {lab=CPOUT}
N 100 0 100 40 {lab=CPOUT}
N 100 100 100 150 {lab=VSS}
N 0 150 100 150 {lab=VSS}
N 0 100 0 150 {lab=VSS}
N 240 0 310 0 {lab=CPOUT}
N 240 0 240 40 {lab=CPOUT}
N 100 0 240 0 {lab=CPOUT}
N 240 100 240 150 {lab=VSS}
N 100 150 240 150 {lab=VSS}
N -750 0 -680 0 {lab=CPIN}
N -0 0 100 -0 {lab=CPOUT}
N -490 0 -0 0 {lab=CPOUT}
C {sg13g2_pr/cap_cmim.sym} 0 70 0 0 {name=C1
model=cap_cmim
w=60e-6
l=20e-6
m=1
spiceprefix=X
}
C {iopin.sym} 0 170 1 0 {name=p3 lab=VSS}
C {ipin.sym} -750 0 0 0 {name=p1 lab=CPIN}
C {opin.sym} 310 0 0 0 {name=p5 lab=CPOUT}
C {sg13g2_pr/cap_cmim.sym} 100 70 0 0 {name=C2
model=cap_cmim
w=20e-6
l=20e-6
m=1
spiceprefix=X
spice_ignore=true}
C {sg13g2_pr/cap_cmim.sym} 240 70 0 0 {name=C3
model=cap_cmim
w=20e-6
l=20e-6
m=1
spiceprefix=X
spice_ignore=true}
C {RES.sym} -580 0 0 0 {name=x1}
C {lab_pin.sym} -580 40 1 0 {name=p4 sig_type=std_logic lab=VSS}
