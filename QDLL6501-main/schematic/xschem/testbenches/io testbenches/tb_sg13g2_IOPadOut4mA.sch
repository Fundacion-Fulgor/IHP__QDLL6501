v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 560 -240 560 -210 {lab=out_a}
N 530 -210 560 -210 {lab=out_a}
N 560 -210 590 -210 {lab=out_a}
N 130 -210 290 -210 {lab=in_a}
N -30 -460 -30 -450 {
lab=IO_vdd}
N 30 -460 30 -450 {
lab=IO_iovdd}
N -110 -460 -110 -450 {
lab=IO_vss}
N -170 -460 -170 -450 {
lab=IO_iovss}
N 290 -440 310 -440 {lab=GND}
N 310 -440 310 -430 {lab=GND}
N 210 -440 230 -440 {lab=sub!}
N 210 -440 210 -430 {lab=sub!}
N 250 -180 290 -180 {lab=IO_iovdd}
N 250 -240 290 -240 {lab=IO_vdd}
N 250 -230 290 -230 {lab=IO_vss}
N 250 -190 290 -190 {lab=IO_iovss}
N 860 -280 860 -240 {lab=out_a}
N 900 -280 930 -280 {lab=out_a}
N 930 -280 930 -240 {lab=out_a}
N 900 -310 900 -280 {lab=out_a}
N 860 -280 900 -280 {lab=out_a}
N 130 -220 130 -210 {lab=in_a}
N 100 -210 130 -210 {lab=in_a}
N 20 -60 20 -40 {lab=GND}
N 20 -210 20 -120 {lab=#net1}
N 20 -210 40 -210 {lab=#net1}
C {gnd.sym} 20 -40 0 0 {name=l7 lab=GND
}
C {vsource.sym} 20 -90 0 0 {name=Vin value="PULSE(0 1.2 0 40p 40p 1n 2n)"
}
C {sg13g2_pr/bondpad.sym} 630 -210 1 0 {name=X16
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {lab_pin.sym} 560 -240 1 0 {name=p13 sig_type=std_logic lab=out_a
}
C {vsource.sym} -30 -420 0 0 {name=V1 value=1.2}
C {gnd.sym} -30 -390 0 0 {name=l3 lab=GND}
C {lab_pin.sym} -30 -460 1 0 {name=p7 sig_type=std_logic lab=IO_vdd}
C {vsource.sym} 30 -420 0 0 {name=V2 value=3.3
}
C {gnd.sym} 30 -390 0 0 {name=l4 lab=GND}
C {lab_pin.sym} 30 -460 1 0 {name=p8 sig_type=std_logic lab=IO_iovdd}
C {vsource.sym} -110 -420 0 0 {name=V3 value=0 savecurrent=false}
C {gnd.sym} -110 -390 0 0 {name=l5 lab=GND}
C {lab_pin.sym} -110 -460 1 0 {name=p9 sig_type=std_logic lab=IO_vss}
C {vsource.sym} -170 -420 0 0 {name=V4 value=0 savecurrent=false}
C {gnd.sym} -170 -390 0 0 {name=l6 lab=GND}
C {lab_pin.sym} -170 -460 1 0 {name=p10 sig_type=std_logic lab=IO_iovss}
C {sg13g2_pr/sub.sym} 210 -430 0 0 {name=l8 lab=sub!}
C {gnd.sym} 310 -430 0 0 {name=l11 lab=GND}
C {vsource.sym} 260 -440 1 0 {name=V5 value=0 savecurrent=false}
C {lab_pin.sym} 250 -180 0 0 {name=p1 sig_type=std_logic lab=IO_iovdd
}
C {lab_pin.sym} 250 -240 0 0 {name=p2 sig_type=std_logic lab=IO_vdd
}
C {lab_pin.sym} 250 -230 0 0 {name=p3 sig_type=std_logic lab=IO_vss
}
C {lab_pin.sym} 250 -190 0 0 {name=p4 sig_type=std_logic lab=IO_iovss
}
C {capa.sym} 860 -210 0 0 {name=C5
m=1
value=100f
footprint=1206
device="ceramic capacitor"
spice_ignore=true}
C {res.sym} 930 -210 0 0 {name=R2
value=50k
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {gnd.sym} 860 -180 0 0 {name=l13 lab=GND
spice_ignore=true}
C {gnd.sym} 930 -180 0 0 {name=l14 lab=GND
spice_ignore=true}
C {lab_pin.sym} 900 -310 1 0 {name=p21 sig_type=std_logic lab=out_a
}
C {devices/code_shown.sym} -200 -720 0 0 {name=MODEL only_toplevel=true
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
C {code.sym} -320 -290 0 0 {name=TRANSIENT1 only_toplevel=true
value="
.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1
.control
 tran 10p 20n 10p
 plot v(in_a) v(out_a)
 plot i(Vin) 
.endc
"
}
C {lab_pin.sym} 130 -220 1 0 {name=p5 sig_type=std_logic lab=in_a
}
C {res.sym} 70 -210 3 0 {name=R1
value=10
footprint=1206
device=resistor
m=1
}
C {sg13g2_IOPadOut4mA.sym} 410 -210 2 1 {name=x2}
