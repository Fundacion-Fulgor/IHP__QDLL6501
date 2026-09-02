v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 330 -150 330 -120 {lab=#net1}
N 300 -120 330 -120 {lab=#net1}
N 330 -120 360 -120 {lab=#net1}
N -100 -120 60 -120 {lab=#net2}
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
N 630 -190 630 -150 {lab=out_a}
N 670 -190 700 -190 {lab=out_a}
N 700 -190 700 -150 {lab=out_a}
N 670 -220 670 -190 {lab=out_a}
N 630 -190 670 -190 {lab=out_a}
N -100 -130 -100 -120 {lab=#net2}
N -130 -120 -100 -120 {lab=#net2}
N -210 30 -210 50 {lab=GND}
N -210 -120 -210 -30 {lab=#net2}
N -210 -120 -190 -120 {lab=#net2}
N 340 260 340 290 {lab=in_a}
N 310 290 340 290 {lab=in_a}
N 340 290 370 290 {lab=in_a}
N -90 290 70 290 {lab=out_a}
N 30 320 70 320 {lab=IO_iovdd}
N 30 260 70 260 {lab=IO_vdd}
N 30 270 70 270 {lab=IO_vss}
N 30 310 70 310 {lab=IO_iovss}
N -90 280 -90 290 {lab=out_a}
N -120 290 -90 290 {lab=out_a}
N 340 440 340 460 {lab=GND}
N 340 290 340 380 {lab=in_a}
N -230 290 -230 320 {lab=out_a}
N -230 290 -180 290 {lab=out_a}
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
spice_ignore=true}
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
value=100f
footprint=1206
device="ceramic capacitor"
spice_ignore=true}
C {res.sym} 700 -120 0 0 {name=R2
value=50k
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {gnd.sym} 630 -90 0 0 {name=l13 lab=GND
spice_ignore=true}
C {gnd.sym} 700 -90 0 0 {name=l14 lab=GND
spice_ignore=true}
C {lab_pin.sym} 670 -220 1 0 {name=p21 sig_type=std_logic lab=out_a
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
.include /foss/pdks/ihp-sg13g2/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
"}
C {code.sym} -550 -200 0 0 {name=TRANSIENT1 only_toplevel=true
value="
.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1
.control
 set color0 = white
 tran 10p 20n 10p
 plot v(in_a) v(out_a)
 plot i(Vin) 
.endc
"
}
C {lab_pin.sym} -100 -130 1 0 {name=p5 sig_type=std_logic lab=in_a
spice_ignore=true}
C {res.sym} -160 -120 3 0 {name=R1
value=10
footprint=1206
device=resistor
m=1
spice_ignore=short}
C {gnd.sym} 340 460 0 0 {name=l1 lab=GND}
C {sg13g2_pr/bondpad.sym} 410 290 1 0 {name=X1
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {lab_pin.sym} -90 280 1 0 {name=p6 sig_type=std_logic lab=out_a
}
C {sg13g2_IOPadAnalog.sym} 190 290 2 1 {name=x2
}
C {lab_pin.sym} 30 320 0 0 {name=p11 sig_type=std_logic lab=IO_iovdd}
C {lab_pin.sym} 30 260 0 0 {name=p12 sig_type=std_logic lab=IO_vdd}
C {lab_pin.sym} 30 270 0 0 {name=p14 sig_type=std_logic lab=IO_vss}
C {lab_pin.sym} 30 310 0 0 {name=p15 sig_type=std_logic lab=IO_iovss}
C {lab_pin.sym} 340 260 1 0 {name=p16 sig_type=std_logic lab=in_a
}
C {res.sym} -150 290 3 0 {name=R3
value=10
footprint=1206
device=resistor
m=1
spice_ignore=short}
C {capa.sym} -230 350 0 0 {name=C1
m=1
value=100f
footprint=1206
device="ceramic capacitor"
}
C {gnd.sym} -230 380 0 0 {name=l2 lab=GND}
C {sg13g2_IOPadIn.sym} 70 480 0 0 {name=x3
spice_ignore=true}
C {vsource.sym} 340 410 0 0 {name=Vin1 value="PULSE(0 1.2 0 200p 200p 2n 4n)"
}
