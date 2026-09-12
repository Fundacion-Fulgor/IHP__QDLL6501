v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 0 30 0 50 {lab=GND}
N 170 30 170 150 {lab=VSS}
N 460 20 460 50 {lab=#net1
spice_ignore=true}
N 460 -60 460 -40 {lab=VCONT}
N 310 -60 460 -60 {lab=VCONT}
N 170 -60 170 -30 {lab=#net1}
N 310 -110 310 -60 {lab=VCONT}
N 260 -60 310 -60 {lab=VCONT}
N 170 -60 200 -60 {lab=#net1}
N 460 110 460 150 {lab=VSS}
N 170 150 460 150 {lab=VSS}
N 460 -60 610 -60 {lab=VCONT}
N -80 -50 -80 -30 {lab=VSS}
N -80 30 -80 50 {lab=GND}
C {vsource.sym} 0 0 0 0 {name=V6 value=0 savecurrent=false}
C {gnd.sym} 0 50 0 0 {name=l4 lab=GND}
C {lab_pin.sym} 0 -30 2 0 {name=p15 sig_type=std_logic lab=VSS}
C {devices/vsource.sym} 170 0 0 0 {name=Vcont1 value="PWL(0n 0 300n 1.2)"
}
C {lab_pin.sym} 170 60 2 0 {name=p4 sig_type=std_logic lab=VSS}
C {code.sym} -320 -330 0 0 {name=TRANSIENT_TT_VN_TN_RT_CT only_toplevel=true
value="
.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=1.2 vd=\{vdd\}
.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1

.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt


.control 
tran 1p 300n
plot v(VCONT)
plot i(Vcont1)

.endc
"
}
C {lab_pin.sym} 310 -110 2 0 {name=p1 sig_type=std_logic lab=VCONT}
C {res.sym} 230 -60 1 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {sg13g2_pr/dantenna.sym} 460 -10 0 0 {name=D1
model=dantenna
l=0.78u
w=0.78u
spiceprefix=X
spice_ignore=true}
C {sg13g2_pr/dpantenna.sym} 460 80 0 0 {name=D3
model=dpantenna
l=0.78u
w=0.78u
spiceprefix=X
spice_ignore=true}
C {sg13g2_antennanp.sym} 700 -60 0 0 {name=x1 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {vsource.sym} -80 -80 0 0 {name=V5 value=vdd savecurrent=false}
C {lab_pin.sym} -80 -110 2 0 {name=p14 sig_type=std_logic lab=VDD}
C {vsource.sym} -80 0 0 0 {name=V1 value=0 savecurrent=false}
C {gnd.sym} -80 50 0 0 {name=l1 lab=GND}
C {lab_pin.sym} -80 -30 2 0 {name=p2 sig_type=std_logic lab=VSS}
