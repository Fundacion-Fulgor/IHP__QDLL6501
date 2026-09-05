v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 70 -0 120 -0 {lab=PDOUT}
N -90 20 -50 20 {lab=PDIN2}
N -90 -20 -50 -20 {lab=PDIN1}
C {sg13g2_xor2_1.sym} 10 0 0 0 {name=x1 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {iopin.sym} -50 -180 0 0 {name=p1 lab=VDD
}
C {iopin.sym} -50 -140 0 0 {name=p2 lab=VSS}
C {opin.sym} 120 0 0 0 {name=p5 lab=PDOUT}
C {ipin.sym} -90 -20 0 0 {name=p3 lab=PDIN1}
C {ipin.sym} -90 20 0 0 {name=p4 lab=PDIN2}
