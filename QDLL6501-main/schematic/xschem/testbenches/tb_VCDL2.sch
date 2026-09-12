v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -310 520 -310 530 {lab=VSS}
N -40 70 -40 120 {lab=VCONT}
N -600 260 -600 290 {lab=VSS}
N -600 180 -600 200 {lab=VIN}
N 40 70 40 120 {lab=VSS}
N 0 -110 0 -60 {lab=VDD}
N -230 500 -230 520 {lab=VSS}
N -310 520 -230 520 {lab=VSS}
N -310 500 -310 520 {lab=VSS}
N 180 340 180 380 {lab=VCONT}
N 80 380 180 380 {lab=VCONT}
N -20 460 -20 490 {lab=VSS}
N -230 380 -230 440 {lab=#net1}
N -230 380 -120 380 {lab=#net1}
N -310 420 -310 440 {lab=#net2}
N -750 20 -750 40 {lab=VSS}
N -750 100 -750 120 {lab=GND}
N 720 60 720 80 {lab=VSS}
N 670 0 770 0 {lab=VOUT}
N 520 -110 520 -60 {lab=VDD}
N 520 70 520 120 {lab=VSS}
N -500 110 -500 140 {lab=VSS}
N -500 20 -500 50 {lab=VDD}
N -310 320 -310 360 {lab=#net3}
N -310 220 -310 260 {lab=#net1}
N -310 220 -230 220 {lab=#net1}
N -230 220 -230 380 {lab=#net1}
N -170 -0 -110 0 {lab=VIN}
N 110 -0 370 0 {lab=#net4}
C {code_shown.sym} -680 -240 0 0 {name=MODEL1 only_toplevel=true
format="tcleval( @value )"
value="

.param corner=0

.if (corner==0)
.lib cornerMOSlv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.endif
"
spice_ignore=true}
C {devices/code_shown.sym} -680 -440 0 0 {name=NGSPICE1 only_toplevel=true
value="
.control
 tran 1p 10n
 plot v(VIN) v(VOUT)
 plot v(VCONT)
.endc
"
spice_ignore=true}
C {devices/vsource.sym} -310 470 0 0 {name=Vcont1 value="PWL(100n 0 200n 0.6)"
}
C {VCDL2.sym} 0 0 0 0 {name=x1
}
C {lab_pin.sym} -310 530 2 0 {name=p4 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} -600 180 0 0 {name=p7 sig_type=std_logic lab=VIN}
C {devices/lab_pin.sym} -170 0 0 0 {name=p8 sig_type=std_logic lab=VIN}
C {lab_pin.sym} -600 290 2 0 {name=p1 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} -40 120 0 0 {name=p10 sig_type=std_logic lab=VCONT}
C {lab_pin.sym} 40 120 2 0 {name=p11 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 0 -110 2 0 {name=p12 sig_type=std_logic lab=VDD}
C {code.sym} -370 -440 0 0 {name=PHASE_MEASR only_toplevel=true
value="
.control

.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=1.2 vd=\{vdd\}
.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ


.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1


* ---- settings you tweak ----


   * ---- user settings ----
  let vlow  = 0
  let vhigh = 1.2
  let v50   = vlow + 0.5*(vhigh - vlow)

  let start_edge = 0     ; skip early edges (settling)
  let N = 200             ; number of phase samples



  tran 2p 200n

  * ---- allocate vectors ----
  let tvec   = vector(N)
  let phivec = vector(N)

  let k = 0
  let i = start_edge

  while k < N
    * crossing times
    meas tran tin      WHEN v(VIN)=v50  RISE=i
    meas tran tout     WHEN v(VOUT)=v50 RISE=i
    meas tran tin_next WHEN v(VIN)=v50  RISE=(i+1)

    * delay + period
    let dt = tout - tin
    let T  = tin_next - tin

    * phase in degrees (per-cycle)
    let phi = 360*dt/T
    let phi = phi - 360*floor(phi/360)

    * store sample at time = tin
    let tvec[k]   = tin
    let phivec[k] = phi

    let k = k + 1
    let i = i + 1
  end

  * plot phase vs time (one point per cycle)
  plot phivec vs tvec
  *plot v(VCONT) 
  plot v(VIN) v(VOUT) 
.endc
"
spice_ignore=true}
C {code.sym} -370 -260 0 0 {name=TRANSIENT only_toplevel=true
value="
.control
 tran 1p 10n
 plot v(VIN) v(VOUT)
 plot v(VCONT)
.endc
"
spice_ignore=true}
C {code.sym} -180 -440 0 0 {name=PHASE_vs_VCONT only_toplevel=true
value="

.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=1.2 vd=\{vdd\}
.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1

.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ


.control
* ---- settings you tweak ----


   * ---- user settings ----
  let vlow  = 0
  let vhigh = 1.2
  let v50   = vlow + 0.5*(vhigh - vlow)

  let start_edge = 0     ; skip early edges (settling)
  let N = 200             ; number of phase samples



  tran 2p 1500n

 * ---- allocate vectors ----
  let tvec   = vector(N)
  let phivec = vector(N)
  let vcontvec  = vector(N)

  let k = 0
  let i = start_edge

  while k < N
    * crossing times
    meas tran tin      WHEN v(VIN)=v50  RISE=i
    meas tran tout     WHEN v(VOUT)=v50 RISE=i
    meas tran tin_next WHEN v(VIN)=v50  RISE=(i+1)

    * delay + period
    let dt = tout - tin
    let T  = tin_next - tin

    * phase in degrees (per-cycle)
    let phi = 360*dt/T
    let phi = phi - 360*floor(phi/360)

    *let vc = value(v(VCONT), tin)
    meas tran vc FIND v(VCONT) AT=tin
    let vcontvec[k] = vc
    * store sample at time = tin
    let tvec[k]   = tin
    let phivec[k] = phi
    let vcontvec[k] = vc

    let k = k + 1
    let i = i + 1
  end

  * plot phase vs time (one point per cycle)
  plot phivec vs tvec
  plot phivec vs vcontvec
  plot v(VCONT)
  plot v(VCONT) phivec
  plot v(VIN) v(VOUT)
.endc
"
spice_ignore=true}
C {vsource.sym} -230 470 0 0 {name=V1 value=0.6 savecurrent=false
spice_ignore=true}
C {IHP__MPC0349/dependencies/IHP__QDLL6501/QDLL6501-main/schematic/xschem/CP.sym} -20 380 0 0 {name=x2}
C {devices/lab_pin.sym} 180 340 0 0 {name=p13 sig_type=std_logic lab=VCONT}
C {lab_pin.sym} -20 490 2 0 {name=p9 sig_type=std_logic lab=VSS}
C {code.sym} -970 -300 0 0 {name=TRANSIENT_TT_VN_TN_RT_CT only_toplevel=true
value="
.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=1.2 vd=\{vdd\}
.options method=gear reltol=1e-1 abstol=1e-1 vntol=1e-1

.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ

* Ajustá TPER al período real de tu fuente (ej. 4n = 4 ns)
.param TPER = 4n

* Detectores de flanco ascendente (umbral 0.6 V para señal 0..1.2 V)
BTRIG_IN  TRIG_IN  0  V='(ddt(V(VIN))>0 && V(VIN)>0.6) ? 1 : 0'
BTRIG_OUT TRIG_OUT 0  V='(ddt(V(VOUT))>0 && V(VOUT)>0.6) ? 1 : 0'

* Sample-and-hold de tiempos de flanco (se guardan solo en el instante del flanco)
BIN_TIME  TIN   0  V='(V(TRIG_IN)>0 ? time : V(TIN))'
BOUT_TIME TOUT  0  V='(V(TRIG_OUT)>0 ? time : V(TOUT))'

* Retardo: solo se actualiza cuando TRIG_OUT se activa
BDELAY DELAY 0 V='(V(TRIG_OUT)>0 ? (V(TOUT)-V(TIN)) : V(DELAY))'

* Fase en grados (valor constante entre actualizaciones)
BPHASE PHASE 0 V='360*(V(DELAY)/TPER)'

* Inicializaciones para evitar valores indefinidos
.ic V(TIN)=0 V(TOUT)=0 V(DELAY)=0 V(PHASE)=0



.control
tran 1p 50n
plot v(VIN) v(VOUT)
plot i(V5)
plot v(PHASE)
.endc

"
}
C {vsource.sym} -600 230 0 1 {name=V2 value="pulse(0,vdd,0,tr,tf,duty,per) dc 0 ac 0)" savecurrent=false}
C {vsource.sym} -750 -10 0 0 {name=V5 value=vdd savecurrent=false}
C {lab_pin.sym} -750 -40 2 0 {name=p14 sig_type=std_logic lab=VDD}
C {vsource.sym} -750 70 0 0 {name=V6 value=0 savecurrent=false}
C {gnd.sym} -750 120 0 0 {name=l4 lab=GND}
C {lab_pin.sym} -750 40 2 0 {name=p15 sig_type=std_logic lab=VSS}
C {DLine.sym} 520 0 0 0 {name=x4}
C {devices/lab_pin.sym} 770 0 0 1 {name=p3 sig_type=std_logic lab=VOUT}
C {capa.sym} 720 30 0 0 {name=C2
m=1
value=100f
footprint=1206
device="ceramic capacitor"}
C {lab_pin.sym} 720 80 2 0 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 520 -110 2 0 {name=p2 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 520 120 2 0 {name=p6 sig_type=std_logic lab=VSS}
C {sg13g2_pr/cap_cmim.sym} -500 80 0 0 {name=C1
model=cap_cmim
w=60e-6
l=20e-6
m=4
spiceprefix=X
}
C {lab_pin.sym} -500 20 2 0 {name=p16 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -500 140 2 0 {name=p17 sig_type=std_logic lab=VSS}
C {code_shown.sym} -820 -580 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.include $::env(PDK_ROOT)/$::env(PDK)/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
"}
C {devices/vsource.sym} -310 390 0 0 {name=Vcont2 value="PWL(300n 0.6 500n -0.6)"
}
C {devices/vsource.sym} -310 290 0 0 {name=Vcont3 value="PWL(500n 0 1000n 1.2)"
}
