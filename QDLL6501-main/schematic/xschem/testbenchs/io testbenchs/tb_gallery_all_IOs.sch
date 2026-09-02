v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 550 60 710 60 {lab=in_a}
N -380 -270 -380 -260 {
lab=IO_vdd}
N -320 -270 -320 -260 {
lab=IO_iovdd}
N -460 -270 -460 -260 {
lab=IO_vss}
N -520 -270 -520 -260 {
lab=IO_iovss}
N -60 -250 -40 -250 {lab=GND}
N -40 -250 -40 -240 {lab=GND}
N -140 -250 -120 -250 {lab=sub!}
N -140 -250 -140 -240 {lab=sub!}
N 550 50 550 60 {lab=in_a}
N 520 60 550 60 {lab=in_a}
N 440 210 440 230 {lab=GND}
N 440 60 440 150 {lab=#net1}
N 440 60 460 60 {lab=#net1}
N 840 -180 840 -150 {lab=IO_vdd}
N 790 -180 840 -180 {lab=IO_vdd}
N 790 -210 790 -180 {lab=IO_vdd}
N 880 -180 880 -150 {lab=IO_iovdd}
N 880 -180 940 -180 {lab=IO_iovdd}
N 940 -210 940 -180 {lab=IO_iovdd}
N 790 260 840 260 {lab=IO_vss}
N 840 240 840 260 {lab=IO_vss}
N 790 260 790 290 {lab=IO_vss}
N 880 240 880 260 {lab=IO_iovss}
N 880 260 930 260 {lab=IO_iovss}
N 930 260 930 300 {lab=IO_iovss}
N 680 80 710 80 {lab=IO_vdd}
N 680 40 710 40 {lab=IO_vss}
N 1000 190 1150 190 {lab=out1}
N 1000 170 1170 170 {lab=out2}
N 1000 150 1190 150 {lab=out3}
N 1000 130 1210 130 {lab=out4}
N 1000 110 1230 110 {lab=out5}
N 1000 70 1230 70 {lab=out7}
N 1230 30 1230 70 {lab=out7}
N 1000 50 1210 50 {lab=out8}
N 1210 -30 1210 50 {lab=out8}
N 1000 30 1190 30 {lab=out9}
N 1190 -90 1190 30 {lab=out9}
N 1000 10 1170 10 {lab=out10}
N 1170 -150 1170 10 {lab=out10}
N 1150 -210 1150 -10 {lab=out11}
N 1000 -10 1150 -10 {lab=out11}
N 1000 -30 1130 -30 {lab=#net2}
N 1130 -270 1130 -30 {lab=#net2}
N 1150 390 1320 390 {lab=out1}
N 1170 330 1320 330 {lab=out2}
N 1190 270 1320 270 {lab=out3}
N 1210 210 1320 210 {lab=out4}
N 1150 190 1150 390 {lab=out1}
N 1170 170 1170 330 {lab=out2}
N 1190 150 1190 270 {lab=out3}
N 1210 130 1210 210 {lab=out4}
N 1230 150 1320 150 {lab=out5}
N 1230 110 1230 150 {lab=out5}
N 1000 90 1320 90 {lab=out6}
N 1230 30 1320 30 {lab=out7}
N 1210 -30 1320 -30 {lab=out8}
N 1190 -90 1320 -90 {lab=out9}
N 1170 -150 1320 -150 {lab=out10}
N 1150 -210 1320 -210 {lab=out11}
N 1130 -270 1320 -270 {lab=#net2}
N 1000 -50 1110 -50 {lab=in_a}
N 1110 -330 1110 -50 {lab=in_a}
N 1110 -330 1320 -330 {lab=in_a}
N 1000 -70 1090 -70 {lab=out14}
N 1090 -390 1090 -70 {lab=out14}
N 1090 -390 1320 -390 {lab=out14}
N 1000 -90 1070 -90 {lab=out15}
N 1070 -430 1070 -90 {lab=out15}
C {gnd.sym} 440 230 0 0 {name=l7 lab=GND
}
C {vsource.sym} 440 180 0 0 {name=Vin value="PULSE(0 1.2 0 40p 40p 1n 2n)"
}
C {vsource.sym} -380 -230 0 0 {name=V1 value=1.2}
C {gnd.sym} -380 -200 0 0 {name=l3 lab=GND}
C {lab_pin.sym} -380 -270 1 0 {name=p7 sig_type=std_logic lab=IO_vdd}
C {vsource.sym} -320 -230 0 0 {name=V2 value=3.3
}
C {gnd.sym} -320 -200 0 0 {name=l4 lab=GND}
C {lab_pin.sym} -320 -270 1 0 {name=p8 sig_type=std_logic lab=IO_iovdd}
C {vsource.sym} -460 -230 0 0 {name=V3 value=0 savecurrent=false}
C {gnd.sym} -460 -200 0 0 {name=l5 lab=GND}
C {lab_pin.sym} -460 -270 1 0 {name=p9 sig_type=std_logic lab=IO_vss}
C {vsource.sym} -520 -230 0 0 {name=V4 value=0 savecurrent=false}
C {gnd.sym} -520 -200 0 0 {name=l6 lab=GND}
C {lab_pin.sym} -520 -270 1 0 {name=p10 sig_type=std_logic lab=IO_iovss}
C {sg13g2_pr/sub.sym} -140 -240 0 0 {name=l8 lab=sub!}
C {gnd.sym} -40 -240 0 0 {name=l11 lab=GND}
C {vsource.sym} -90 -250 1 0 {name=V5 value=0 savecurrent=false}
C {devices/code_shown.sym} -550 -530 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.include diodes.lib
.include sg13g2_bondpad.lib
.include /foss/pdks/ihp-sg13g2/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
"}
C {code.sym} 140 -170 0 0 {name=TRANSIENT1 only_toplevel=true
value="
.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1
.control
 tran 10p 20n 10p
*plot v(in_a) v(out1)
*plot v(in_a) v(out2)
*plot v(in_a) v(out3)
*plot v(in_a) v(out4)
*plot v(in_a) v(out5)
*plot v(in_a) v(out6)
*plot v(in_a) v(out7)
*plot v(in_a) v(out8)
*plot v(in_a) v(out9)
*plot v(in_a) v(out10)
*plot v(in_a) v(out11)
*plot v(in_a) v(out12)
*plot v(in_a) v(out13)
plot v(in_a) v(out14)
*plot v(in_a) v(out15)
.endc
"
}
C {lab_pin.sym} 550 50 1 0 {name=p5 sig_type=std_logic lab=in_a
}
C {res.sym} 490 60 3 0 {name=R1
value=10
footprint=1206
device=resistor
m=1
}
C {sg13g2_Gallery.sym} 860 60 0 0 {name=x2}
C {sg13g2_pr/bondpad.sym} 790 -250 0 0 {name=X3
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 940 -250 0 0 {name=X4
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 790 330 2 0 {name=X5
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 930 340 2 0 {name=X6
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {lab_pin.sym} 930 270 2 0 {name=p1 sig_type=std_logic lab=IO_iovss}
C {lab_pin.sym} 790 270 0 0 {name=p2 sig_type=std_logic lab=IO_vss}
C {lab_pin.sym} 880 -160 2 0 {name=p3 sig_type=std_logic lab=IO_iovdd}
C {lab_pin.sym} 840 -160 0 0 {name=p4 sig_type=std_logic lab=IO_vdd}
C {lab_pin.sym} 680 80 0 0 {name=p6 sig_type=std_logic lab=IO_vdd}
C {lab_pin.sym} 680 40 0 0 {name=p11 sig_type=std_logic lab=IO_vss}
C {sg13g2_pr/bondpad.sym} 1360 -270 1 0 {name=X1
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 1360 -210 1 0 {name=X7
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 1360 -150 1 0 {name=X8
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 1360 -90 1 0 {name=X9
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 1360 -30 1 0 {name=X10
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 1360 30 1 0 {name=X11
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 1360 90 1 0 {name=X12
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 1360 210 1 0 {name=X14
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 1360 330 1 0 {name=X16
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 1360 -390 1 0 {name=X19
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {lab_pin.sym} 1150 370 2 0 {name=p12 sig_type=std_logic lab=out1}
C {lab_pin.sym} 1170 310 2 0 {name=p13 sig_type=std_logic lab=out2}
C {lab_pin.sym} 1190 250 2 0 {name=p14 sig_type=std_logic lab=out3}
C {lab_pin.sym} 1210 190 2 0 {name=p15 sig_type=std_logic lab=out4}
C {lab_pin.sym} 1230 120 2 0 {name=p16 sig_type=std_logic lab=out5}
C {lab_pin.sym} 1250 90 2 0 {name=p17 sig_type=std_logic lab=out6}
C {lab_pin.sym} 1230 40 2 0 {name=p18 sig_type=std_logic lab=out7}
C {lab_pin.sym} 1210 -20 2 0 {name=p19 sig_type=std_logic lab=out8}
C {lab_pin.sym} 1190 -80 2 0 {name=p20 sig_type=std_logic lab=out9}
C {lab_pin.sym} 1170 -130 2 0 {name=p21 sig_type=std_logic lab=out10}
C {lab_pin.sym} 1150 -200 2 0 {name=p22 sig_type=std_logic lab=out11}
C {lab_pin.sym} 1090 -370 2 0 {name=p25 sig_type=std_logic lab=out14}
C {lab_pin.sym} 1070 -430 2 0 {name=p26 sig_type=std_logic lab=out15}
C {lab_pin.sym} 1110 -230 2 0 {name=p27 sig_type=std_logic lab=in_a
}
