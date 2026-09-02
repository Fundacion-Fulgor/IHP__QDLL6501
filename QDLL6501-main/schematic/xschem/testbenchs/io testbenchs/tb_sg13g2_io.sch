v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 1560 -220 1560 -200 {
lab=GND}
N 70 -510 70 -300 {
lab=vin}
N 1460 -510 1560 -510 {
lab=vout}
N 1560 -510 1560 -390 {
lab=vout}
N 580 -450 580 -300 {
lab=iovdd}
N 580 -610 580 -480 {
lab=iovdd}
N 580 -740 580 -610 {
lab=iovdd}
N 660 -670 660 -540 {
lab=vdd}
N 580 -1020 580 -880 {
lab=iovdd}
N 660 -940 660 -800 {
lab=vdd}
N 1110 -220 1560 -220 {
lab=GND}
N 580 -240 580 -220 {
lab=GND}
N 660 -240 660 -220 {
lab=GND}
N 70 -260 70 -220 {
lab=GND}
N 880 -510 1220 -510 {
lab=dig}
N 1560 -340 1560 -220 {
lab=GND}
N 70 -220 580 -220 {
lab=GND}
N 880 -300 880 -220 {
lab=GND}
N 950 -300 950 -220 {
lab=GND}
N 880 -510 880 -360 {
lab=dig}
N 950 -640 950 -360 {
lab=ana}
N 580 -450 1190 -450 {
lab=iovdd}
N 580 -480 580 -450 {
lab=iovdd}
N 580 -1150 580 -1020 {
lab=iovdd}
N 580 -220 660 -220 {
lab=GND}
N 950 -220 1110 -220 {
lab=GND}
N 660 -220 760 -220 {
lab=GND}
N 660 -540 660 -300 {
lab=vdd}
N 760 -220 880 -220 {
lab=GND}
N 880 -220 950 -220 {
lab=GND}
N 660 -1080 660 -940 {
lab=vdd}
N 70 -510 250 -510 {
lab=vin}
N 490 -510 880 -510 {lab=dig}
N 490 -540 660 -540 {lab=vdd}
N 490 -480 580 -480 {lab=iovdd}
N 1190 -480 1190 -450 {lab=iovdd}
N 1190 -480 1220 -480 {lab=iovdd}
N 950 -670 950 -640 {
lab=ana}
N 500 -640 950 -640 {lab=ana}
N 500 -670 660 -670 {lab=vdd}
N 660 -800 660 -670 {
lab=vdd}
N 500 -610 580 -610 {lab=iovdd}
N 500 -740 580 -740 {lab=iovdd}
N 580 -880 580 -740 {
lab=iovdd}
N 500 -800 660 -800 {lab=vdd}
N 500 -880 580 -880 {lab=iovdd}
N 500 -940 660 -940 {lab=vdd}
N 500 -1020 580 -1020 {lab=iovdd}
N 660 -1210 660 -1080 {
lab=vdd}
N 500 -1080 660 -1080 {lab=vdd}
N 500 -1150 580 -1150 {lab=iovdd}
N 500 -1210 660 -1210 {lab=vdd}
N 500 -1200 760 -1200 {lab=GND}
N 760 -620 760 -220 {lab=GND}
N 500 -1160 760 -1160 {lab=GND}
N 760 -1200 760 -1160 {lab=GND}
N 500 -1070 760 -1070 {lab=GND}
N 760 -1160 760 -1070 {lab=GND}
N 500 -1030 760 -1030 {lab=GND}
N 760 -1070 760 -1030 {lab=GND}
N 500 -930 760 -930 {lab=GND}
N 760 -1030 760 -930 {lab=GND}
N 500 -890 760 -890 {lab=GND}
N 760 -930 760 -890 {lab=GND}
N 500 -790 760 -790 {lab=GND}
N 760 -890 760 -790 {lab=GND}
N 500 -750 760 -750 {lab=GND}
N 760 -790 760 -750 {lab=GND}
N 500 -660 760 -660 {lab=GND}
N 760 -750 760 -660 {lab=GND}
N 500 -620 760 -620 {lab=GND}
N 760 -660 760 -620 {lab=GND}
N 1110 -490 1110 -220 {lab=GND}
N 1110 -490 1220 -490 {lab=GND}
N 1110 -530 1220 -530 {lab=GND}
N 1110 -530 1110 -490 {lab=GND}
N 660 -540 1220 -540 {lab=vdd}
N 760 -1210 760 -1200 {lab=GND}
N -30 -640 -30 -630 {lab=vin2}
N 50 -640 260 -640 {lab=vin2}
N -30 -570 -30 -220 {lab=GND}
N -30 -220 70 -220 {lab=GND}
N 50 -650 50 -640 {lab=vin2}
N -30 -640 50 -640 {lab=vin2}
C {devices/title.sym} 160 -30 0 0 {name=l1 author="Boris Murmann"}
C {sg13g2_IOPadAnalog.sym} 380 -640 2 0 {name=x1}
C {sg13g2_IOPadIn.sym} 370 -510 2 0 {name=x2}
C {devices/vsource.sym} 660 -270 0 0 {name=V1 value=\{vdd\} savecurrent=false}
C {devices/gnd.sym} 1560 -200 0 0 {name=l3 lab=GND}
C {devices/vsource.sym} 70 -270 0 0 {name=V3 value="pulse(0 \{iovdd\} 10n 500p 500p 10n 20n)" savecurrent=false}
C {devices/lab_wire.sym} 70 -430 0 0 {name=p1 sig_type=std_logic lab=vin}
C {devices/lab_wire.sym} 660 -350 0 0 {name=p2 sig_type=std_logic lab=vdd}
C {devices/lab_wire.sym} 950 -670 0 0 {name=p4 sig_type=std_logic lab=ana}
C {devices/lab_wire.sym} 840 -510 0 0 {name=p5 sig_type=std_logic lab=dig}
C {devices/simulator_commands_shown.sym} 960 -1130 0 0 {name=COMMANDS
simulator=ngspice
only_toplevel=false 
value="
* ngspice commands
.lib /foss/pdks/ihp-sg13g2/libs.tech/ngspice/models/cornerMOSlv.lib mos_tt
.lib /foss/pdks/ihp-sg13g2/libs.tech/ngspice/models/cornerMOShv.lib mos_tt
.lib /foss/pdks/ihp-sg13g2/libs.tech/ngspice/models/cornerRES.lib res_typ
.inc /foss/pdks/ihp-sg13g2/libs.tech/ngspice/models/diodes.lib
*.inc /foss/designs/EE628/5_Design/3_Real_circuits/sg13g2_io.spi
.options gmin=1e-8
.param vdd=1.2 iovdd=3

.control
set color0 = white
save i(v4) v(vin) v(vout) v(ana) v(dig) v(vin2)
tran 1n 60n
plot ana dig vout
plot i(v4)
.endc

"}
C {devices/capa.sym} 950 -330 0 0 {name=C1
m=1
value=100f
footprint=1206
device="ceramic capacitor"}
C {devices/capa.sym} 880 -330 0 0 {name=C2
m=1
value=100f
footprint=1206
device="ceramic capacitor"}
C {sg13g2_IOPadOut16mA.sym} 1340 -730 2 1 {name=x3
spice_ignore=true}
C {devices/capa.sym} 1560 -370 0 0 {name=C3
m=1
value=10p
footprint=1206
device="ceramic capacitor"}
C {devices/lab_wire.sym} 1520 -510 0 0 {name=p6 sig_type=std_logic lab=vout}
C {devices/vsource.sym} 580 -270 0 0 {name=V4 value=\{iovdd\} savecurrent=false}
C {sg13g2_IOPadIOVss.sym} 380 -770 2 0 {name=x4}
C {sg13g2_IOPadIOVdd.sym} 380 -910 2 0 {name=x5}
C {sg13g2_IOPadVss.sym} 380 -1050 2 0 {name=x6}
C {sg13g2_IOPadVdd.sym} 380 -1180 2 0 {name=x7}
C {devices/lab_wire.sym} 580 -350 0 0 {name=p3 sig_type=std_logic lab=iovdd}
C {sg13g2_IOPadOut4mA.sym} 1340 -510 2 1 {name=x11
}
C {devices/code_shown.sym} -160 -1150 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.include diodes.lib
.include sg13g2_bondpad.lib
"}
C {sg13g2_pr/bondpad.sym} 580 -1250 0 1 {name=X14
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 760 -1250 0 1 {name=X8
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 800 -1130 1 1 {name=X9
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 540 -390 3 1 {name=X10
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 170 -680 0 1 {name=X12
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 170 -550 0 1 {name=X13
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {sg13g2_pr/bondpad.sym} 1560 -550 0 1 {name=X15
model=bondpad
spiceprefix=X
size=80u
shape=0
padtype=0
}
C {devices/vsource.sym} -30 -600 0 0 {name=V2 value="pulse(0 \{iovdd\} 10n 500p 500p 10n 20n)" savecurrent=false}
C {devices/lab_wire.sym} 50 -650 0 0 {name=p7 sig_type=std_logic lab=vin2}
