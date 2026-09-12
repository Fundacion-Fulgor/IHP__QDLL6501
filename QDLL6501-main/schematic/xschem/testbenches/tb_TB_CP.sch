v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -450 420 -450 440 {lab=GND}
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
N -160 20 -100 20 {lab=PDIN2}
N -160 -20 -100 -20 {lab=PDIN1}
N 0 100 140 100 {lab=VSS}
N 140 -30 140 -0 {lab=PDOUT}
N 100 -0 140 -0 {lab=PDOUT}
N 420 -60 420 -0 {lab=VCONT}
N 380 -0 420 -0 {lab=VCONT}
N 680 -40 680 -0 {lab=VCONT}
N 420 -0 680 0 {lab=VCONT}
N 760 -40 760 10 {lab=VSS}
N 720 -210 720 -170 {lab=VDD}
N 560 -110 610 -110 {lab=VSS}
N 830 -110 910 -110 {lab=#net1}
N -450 220 -450 280 {lab=VDD}
N -450 340 -450 360 {lab=VSS}
C {vsource.sym} -580 80 0 1 {name=V1 value="pulse(0,VDD1P2,0,tr,tf,duty,per) dc 0 ac 0)" savecurrent=false}
C {vsource.sym} -480 80 0 0 {name=V2 value="pulse(0,VDD1P2,delay,tr,tf,duty,per) dc 0 ac 0)" savecurrent=false}
C {code_shown.sym} -980 -170 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.include $::env(PDK_ROOT)/$::env(PDK)/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
"}
C {vsource.sym} -450 310 0 0 {name=V3 value=VDD1P2 savecurrent=false}
C {lab_pin.sym} -450 250 2 0 {name=p1 sig_type=std_logic lab=VDD}
C {vsource.sym} -450 390 0 0 {name=V4 value=0 savecurrent=false}
C {gnd.sym} -450 440 0 0 {name=l4 lab=GND}
C {lab_pin.sym} -450 360 2 0 {name=p5 sig_type=std_logic lab=VSS}
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
C {lab_pin.sym} 420 -20 2 0 {name=p11 sig_type=std_logic lab=VCONT
}
C {lab_pin.sym} 140 -30 1 0 {name=p12 sig_type=std_logic lab=PDOUT}
C {PD.sym} 0 0 0 0 {name=x3}
C {CP.sym} 280 0 0 0 {name=x1}
C {sg13g2_antennanp.sym} 420 -150 3 0 {name=x2 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {code.sym} -320 -370 0 0 {name=TRANSIENT_TT_VN_TN only_toplevel=true
value="

.param temp=0
.param VDD1P2=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=1n
.param vin=\{VDD1P2\} vd=\{VDD1P2\}

.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt


.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1
.control

tran 20p 1u 1n
   
plot v(VCONT)

.endc
"
spice_ignore=true}
C {IHP__MPC0349/dependencies/IHP__QDLL6501/QDLL6501-main/schematic/xschem/VCDL.sym} 720 -110 0 0 {name=x4}
C {lab_pin.sym} 760 10 2 0 {name=p13 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 720 -210 2 0 {name=p14 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 560 -110 3 0 {name=p15 sig_type=std_logic lab=VSS}
C {code.sym} -50 -340 0 0 {name=TRANSIENT_TT_VN_TN_RB_CB only_toplevel=true
value="

.param temp=65
.param VDD1P2=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=1n
.param vin=\{VDD1P2\} vd=\{VDD1P2\}

.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_bcs
.lib cornerRES.lib res_bcs
.lib cornerDIO.lib dio_tt


.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1
.control

tran 20p 1u 1n
   
plot v(VCONT)

.endc
"
}
