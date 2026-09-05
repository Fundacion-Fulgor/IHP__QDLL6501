v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 340 -110 340 -80 {lab=VDD}
N 410 -160 410 -130 {lab=VSS}
N 760 0 790 0 {lab=#net1}
N 870 0 900 0 {lab=#net2}
N 310 0 360 0 {lab=VIN}
N 440 0 520 0 {lab=#net3}
N 600 0 680 0 {lab=#net4}
N 980 0 1040 0 {lab=VOUT}
C {opin.sym} 1040 0 0 0 {name=p5 lab=VOUT}
C {ipin.sym} 310 0 0 0 {name=p3 lab=VIN}
C {iopin.sym} 340 -110 3 0 {name=p1 lab=VDD
}
C {iopin.sym} 410 -130 1 0 {name=p2 lab=VSS}
C {sg13g2_inv_2.sym} -10 -350 0 0 {name=x30 VDD=VDD VSS=VSS prefix=sg13g2_ spice_ignore=true}
C {sg13g2_inv_4.sym} 720 0 0 0 {name=x2 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {sg13g2_inv_8.sym} 830 0 0 0 {name=x3 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {sg13g2_inv_16.sym} 940 0 0 0 {name=x4 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {sg13g2_dlygate4sd3_1.sym} 400 0 0 0 {name=x5 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {sg13g2_dlygate4sd2_1.sym} 560 0 0 0 {name=x6 VDD=VDD VSS=VSS prefix=sg13g2_ }
