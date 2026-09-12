v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -100 30 -100 50 {lab=GND}
N 0 30 0 50 {lab=GND}
N 170 50 170 60 {lab=VSS}
N 460 50 570 50 {lab=VSS}
N 170 30 170 50 {lab=VSS}
N 570 20 570 50 {lab=VSS}
N 460 20 460 50 {lab=VSS}
N 170 50 460 50 {lab=VSS}
N 460 -60 460 -40 {lab=#net1}
N 460 -60 570 -60 {lab=#net1}
N 570 -60 570 -40 {lab=#net1}
N 170 -60 460 -60 {lab=#net1}
N 170 -60 170 -30 {lab=#net1}
C {vsource.sym} -100 0 0 0 {name=V5 value=vdd savecurrent=false}
C {gnd.sym} -100 50 0 0 {name=l3 lab=GND}
C {lab_pin.sym} -100 -30 2 0 {name=p14 sig_type=std_logic lab=VDD}
C {vsource.sym} 0 0 0 0 {name=V6 value=0 savecurrent=false}
C {gnd.sym} 0 50 0 0 {name=l4 lab=GND}
C {lab_pin.sym} 0 -30 2 0 {name=p15 sig_type=std_logic lab=VSS}
C {devices/vsource.sym} 170 0 0 0 {name=Vcont1 value="PWL(100n 0 200n 1.2)"
spice_ignore=true}
C {lab_pin.sym} 170 60 2 0 {name=p4 sig_type=std_logic lab=VSS}
C {code.sym} -320 -330 0 0 {name=TRANSIENT_TT_VN_TN_RT_CT only_toplevel=true
value="
.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=1.2 vd=\{vdd\}


.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ

.endc
"
}
C {sg13g2_pr/dantenna.sym} 460 -10 0 0 {name=D1
model=dantenna
l=0.78u
w=0.78u
spiceprefix=X
}
C {sg13g2_pr/dpantenna.sym} 570 -10 0 0 {name=D2
model=dpantenna
l=0.78u
w=0.78u
spiceprefix=X
}
