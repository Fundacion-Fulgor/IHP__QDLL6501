v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 210 -50 210 -20 {lab=out_a}
N 180 -20 210 -20 {lab=out_a}
N 210 -20 240 -20 {lab=out_a}
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
N -100 10 -60 10 {lab=IO_iovdd}
N -80 -50 -60 -50 {lab=IO_vdd}
N -70 -40 -60 -40 {lab=IO_vss}
N 510 -90 510 -50 {lab=out_a}
N 550 -90 580 -90 {lab=out_a}
N 580 -90 580 -50 {lab=out_a}
N 550 -120 550 -90 {lab=out_a}
N 510 -90 550 -90 {lab=out_a}
N -220 -30 -220 -20 {lab=in_a}
N -250 -20 -220 -20 {lab=in_a}
N -330 130 -330 150 {lab=GND}
N -330 -20 -330 70 {lab=#net1}
N -330 -20 -310 -20 {lab=#net1}
N -100 0 -60 0 {lab=IO_iovss}
N -80 -30 -60 -30 {lab=IO_vdd}
N -80 -50 -80 -30 {lab=IO_vdd}
N -100 -50 -80 -50 {lab=IO_vdd}
N -80 -10 -60 -10 {lab=in_a}
N -80 -20 -80 -10 {lab=in_a}
N -220 -20 -80 -20 {lab=in_a}
N -70 -20 -60 -20 {lab=IO_vss}
N -70 -40 -70 -20 {lab=IO_vss}
N -100 -40 -70 -40 {lab=IO_vss}
C {gnd.sym} -330 150 0 0 {name=l7 lab=GND
}
C {vsource.sym} -330 100 0 0 {name=Vin value="PULSE(0 1.2 0 40p 40p 1n 2n)"
}
C {sg13g2_pr/bondpad.sym} 280 -20 1 0 {name=X16
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {lab_pin.sym} 210 -50 1 0 {name=p13 sig_type=std_logic lab=out_a
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
C {lab_pin.sym} -100 10 0 0 {name=p1 sig_type=std_logic lab=IO_iovdd
}
C {lab_pin.sym} -100 -50 0 0 {name=p2 sig_type=std_logic lab=IO_vdd
}
C {lab_pin.sym} -100 -40 0 0 {name=p3 sig_type=std_logic lab=IO_vss
}
C {lab_pin.sym} -100 0 0 0 {name=p4 sig_type=std_logic lab=IO_iovss
}
C {capa.sym} 510 -20 0 0 {name=C5
m=1
value=100f
footprint=1206
device="ceramic capacitor"
spice_ignore=true}
C {res.sym} 580 -20 0 0 {name=R2
value=50k
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {gnd.sym} 510 10 0 0 {name=l13 lab=GND
spice_ignore=true}
C {gnd.sym} 580 10 0 0 {name=l14 lab=GND
spice_ignore=true}
C {lab_pin.sym} 550 -120 1 0 {name=p21 sig_type=std_logic lab=out_a
}
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
C {code.sym} -670 -100 0 0 {name=TRANSIENT1 only_toplevel=true
value="
.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1
.control
 tran 10p 20n 10p
 plot v(in_a) v(out_a)
 plot i(Vin) 
.endc
"
}
C {lab_pin.sym} -220 -30 1 0 {name=p5 sig_type=std_logic lab=in_a
}
C {res.sym} -280 -20 3 0 {name=R1
value=10
footprint=1206
device=resistor
m=1
}
C {sg13g2_IOPadInOut4mA.sym} 60 -20 2 1 {name=x1}
