v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 330 -150 330 -120 {lab=out_a}
N 300 -120 330 -120 {lab=out_a}
N 330 -120 360 -120 {lab=out_a}
N -100 -120 60 -120 {lab=in_a}
N -260 -370 -260 -360 {
lab=IO_vdd}
N -200 -370 -200 -360 {
lab=IO_iovdd}
N -340 -370 -340 -360 {
lab=IO_vss}
N -400 -370 -400 -360 {
lab=IO_iovss}
N 60 -350 80 -350 {lab=GND}
N 80 -350 80 -340 {lab=GND}
N -20 -350 0 -350 {lab=sub!}
N -20 -350 -20 -340 {lab=sub!}
N 20 -90 60 -90 {lab=IO_iovdd}
N 20 -150 60 -150 {lab=IO_vdd}
N 20 -140 60 -140 {lab=IO_vss}
N 20 -100 60 -100 {lab=IO_iovss}
N 630 -180 630 -150 {lab=out_a
}
N -100 -130 -100 -120 {lab=in_a}
N -130 -120 -100 -120 {lab=in_a}
N -210 30 -210 50 {lab=GND}
N -210 -120 -210 -30 {lab=in_a}
N -210 -120 -190 -120 {lab=in_a}
N 320 240 320 270 {lab=out_b}
N 290 270 320 270 {lab=out_b}
N 320 270 350 270 {lab=out_b}
N -110 270 50 270 {lab=in_b}
N 660 170 660 200 {lab=out_b
spice_ignore=true}
N 620 200 660 200 {lab=out_b
spice_ignore=true}
N -110 260 -110 270 {lab=in_b}
N -140 270 -110 270 {lab=in_b}
N -220 420 -220 440 {lab=GND}
N -220 270 -220 360 {lab=in_b}
N -220 270 -200 270 {lab=in_b}
N 10 240 50 240 {lab=IO_iovdd}
N 10 250 50 250 {lab=IO_iovss}
N 10 300 50 300 {lab=IO_vdd}
N 10 290 50 290 {lab=IO_vss}
C {gnd.sym} -210 50 0 0 {name=l7 lab=GND
}
C {vsource.sym} -210 0 0 0 {name=Vin value="PULSE(0 1.2 0 200p 200p 2n 4n)"
}
C {sg13g2_pr/bondpad.sym} 400 -120 1 0 {name=X16
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {lab_pin.sym} 330 -150 1 0 {name=p13 sig_type=std_logic lab=out_a
}
C {sg13g2_IOPadAnalog.sym} 180 -120 2 1 {name=x5
}
C {vsource.sym} -260 -330 0 0 {name=V1 value=1.2}
C {gnd.sym} -260 -300 0 0 {name=l3 lab=GND}
C {lab_pin.sym} -260 -370 1 0 {name=p7 sig_type=std_logic lab=IO_vdd}
C {vsource.sym} -200 -330 0 0 {name=V2 value=3.3
}
C {gnd.sym} -200 -300 0 0 {name=l4 lab=GND}
C {lab_pin.sym} -200 -370 1 0 {name=p8 sig_type=std_logic lab=IO_iovdd}
C {vsource.sym} -340 -330 0 0 {name=V3 value=0 savecurrent=false}
C {gnd.sym} -340 -300 0 0 {name=l5 lab=GND}
C {lab_pin.sym} -340 -370 1 0 {name=p9 sig_type=std_logic lab=IO_vss}
C {vsource.sym} -400 -330 0 0 {name=V4 value=0 savecurrent=false}
C {gnd.sym} -400 -300 0 0 {name=l6 lab=GND}
C {lab_pin.sym} -400 -370 1 0 {name=p10 sig_type=std_logic lab=IO_iovss}
C {sg13g2_pr/sub.sym} -20 -340 0 0 {name=l8 lab=sub!}
C {gnd.sym} 80 -340 0 0 {name=l11 lab=GND}
C {vsource.sym} 30 -350 1 0 {name=V5 value=0 savecurrent=false}
C {lab_pin.sym} 20 -90 0 0 {name=p1 sig_type=std_logic lab=IO_iovdd
}
C {lab_pin.sym} 20 -150 0 0 {name=p2 sig_type=std_logic lab=IO_vdd
}
C {lab_pin.sym} 20 -140 0 0 {name=p3 sig_type=std_logic lab=IO_vss
}
C {lab_pin.sym} 20 -100 0 0 {name=p4 sig_type=std_logic lab=IO_iovss
}
C {capa.sym} 630 -120 0 0 {name=C5
m=1
value=1pf
footprint=1206
device="ceramic capacitor"
}
C {res.sym} 700 -120 0 0 {name=R2
value=50k
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {gnd.sym} 630 -90 0 0 {name=l13 lab=GND
}
C {gnd.sym} 700 -90 0 0 {name=l14 lab=GND
spice_ignore=true}
C {lab_pin.sym} 630 -180 1 0 {name=p21 sig_type=std_logic lab=out_a
}
C {devices/code_shown.sym} -430 -630 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.include diodes.lib
.include sg13g2_bondpad.lib
.include $::env(PDK_ROOT)/$::env(PDK)/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
"}
C {code.sym} -550 -200 0 0 {name=TRANSIENT1 only_toplevel=true
value="
.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1
.control
 set color0 = white
 tran 10p 20n 10p
 plot v(in_a) v(out_a) v(in_b) v(out_b)
.endc
"
}
C {lab_pin.sym} -100 -130 1 0 {name=p5 sig_type=std_logic lab=in_a
}
C {res.sym} -160 -120 3 0 {name=R1
value=10
footprint=1206
device=resistor
m=1
spice_ignore=short}
C {sg13g2_IOPadOut30mA.sym} 170 270 0 0 {name=x4}
C {gnd.sym} -220 440 0 0 {name=l1 lab=GND
}
C {vsource.sym} -220 390 0 0 {name=Vin2 value="PULSE(0 1.2 0 200p 200p 2n 4n)"
}
C {sg13g2_pr/bondpad.sym} 390 270 1 0 {name=X1
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {lab_pin.sym} 320 240 1 0 {name=p6 sig_type=std_logic lab=out_b
}
C {capa.sym} 620 270 0 0 {name=C1
m=1
value=10pf
footprint=1206
device="ceramic capacitor"
spice_ignore=true}
C {res.sym} 690 270 0 0 {name=R3
value=50k
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {gnd.sym} 620 300 0 0 {name=l2 lab=GND
spice_ignore=true}
C {gnd.sym} 690 300 0 0 {name=l9 lab=GND
spice_ignore=true}
C {lab_pin.sym} 660 170 1 0 {name=p16 sig_type=std_logic lab=out_b
spice_ignore=true}
C {lab_pin.sym} -110 260 1 0 {name=p17 sig_type=std_logic lab=in_b
}
C {res.sym} -170 270 3 0 {name=R4
value=10
footprint=1206
device=resistor
m=1
spice_ignore=short}
C {lab_pin.sym} 10 240 0 0 {name=p18 sig_type=std_logic lab=IO_iovdd
}
C {lab_pin.sym} 10 250 0 0 {name=p19 sig_type=std_logic lab=IO_iovss
}
C {lab_pin.sym} 10 300 0 0 {name=p20 sig_type=std_logic lab=IO_vdd
}
C {lab_pin.sym} 10 290 0 0 {name=p22 sig_type=std_logic lab=IO_vss
}
C {openpdk-libraries/ihp-sg13g2/sg13g2_io/xschem/sg13g2_IOPadRF.sym} 280 490 0 0 {name=x2}
