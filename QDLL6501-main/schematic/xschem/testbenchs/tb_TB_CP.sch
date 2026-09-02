v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N -580 270 -580 290 {lab=GND}
N -480 270 -480 290 {lab=GND}
N -480 110 -480 130 {lab=VSS}
N -580 110 -580 130 {lab=VSS}
N -580 0 -580 50 {lab=PDIN1}
N -480 0 -480 50 {lab=PDIN2}
N 140 -0 180 0 {lab=PDOUT}
N 0 80 0 100 {lab=VSS}
N 280 80 280 100 {lab=VSS}
N 140 100 140 150 {lab=VSS}
N 140 100 280 100 {lab=VSS}
N -0 -120 0 -80 {lab=VDD}
N 380 -0 440 -0 {lab=VCONT}
N -160 20 -100 20 {lab=PDIN2}
N -160 -20 -100 -20 {lab=PDIN1}
N 0 100 140 100 {lab=VSS}
N 140 -30 140 -0 {lab=PDOUT}
N 100 -0 140 -0 {lab=PDOUT}
C {vsource.sym} -580 80 0 1 {name=V1 value="pulse(0,vdd,0,tr,tf,duty,per) dc 0 ac 0)" savecurrent=false}
C {vsource.sym} -480 80 0 0 {name=V2 value="pulse(0,vdd,delay,tr,tf,duty,per) dc 0 ac 0)" savecurrent=false}
C {code_shown.sym} -660 -370 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.include /opt/pdks/ihp-sg13g2/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
"}
C {vsource.sym} -580 240 0 0 {name=V3 value=vdd savecurrent=false}
C {gnd.sym} -580 290 0 0 {name=l3 lab=GND}
C {lab_pin.sym} -580 210 2 0 {name=p1 sig_type=std_logic lab=VDD}
C {vsource.sym} -480 240 0 0 {name=V4 value=0 savecurrent=false}
C {gnd.sym} -480 290 0 0 {name=l4 lab=GND}
C {lab_pin.sym} -480 210 2 0 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -580 130 2 0 {name=p2 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -480 130 2 0 {name=p7 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -580 0 2 0 {name=p8 sig_type=std_logic lab=PDIN1
}
C {lab_pin.sym} -480 0 2 0 {name=p9 sig_type=std_logic lab=PDIN2
}
C {lab_pin.sym} 140 150 2 0 {name=p3 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 0 -120 2 0 {name=p4 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -160 20 0 0 {name=p6 sig_type=std_logic lab=PDIN2
}
C {lab_pin.sym} -160 -20 0 0 {name=p10 sig_type=std_logic lab=PDIN1
}
C {lab_pin.sym} 440 0 2 0 {name=p11 sig_type=std_logic lab=VCONT
}
C {lab_pin.sym} 140 -30 1 0 {name=p12 sig_type=std_logic lab=PDOUT}
C {IHP__MPC0349/dependencies/IHP__QDLL6501/QDLL6501-main/schematic/xschem/PD.sym} 0 0 0 0 {name=x3}
C {IHP__MPC0349/dependencies/IHP__QDLL6501/QDLL6501-main/schematic/xschem/CP.sym} 280 0 0 0 {name=x1}
C {code.sym} -680 -570 0 0 {name=TRANSIENT_TT only_toplevel=true
value="
.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=1.2 vd=\{vdd\}


.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ


.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1
.control
 set color0 = white
 save all 
 tran 2p 1u 0.05n
 plot v(PDIN1) v(PDIN2)
 plot v(VCONT)
 plot v(PDOUT)
.endc
"
}
C {code.sym} -500 -560 0 0 {name=TT_VN_TN_RT_CT 
value="
.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=1.2 vd=\{vdd\}


.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ

.endc
"
spice_ignore=true}
