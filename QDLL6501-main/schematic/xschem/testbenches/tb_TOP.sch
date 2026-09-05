v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 1180 110 1180 130 {lab=VSS}
N -470 200 -470 220 {lab=GND}
N -370 200 -370 220 {lab=GND}
N -470 440 -470 470 {lab=VSS}
N -470 280 -470 300 {lab=VIN}
N 1180 0 1230 0 {lab=VOUT}
N 1180 0 1180 50 {lab=VOUT}
N 720 60 720 100 {lab=VSS}
N 720 -100 720 -60 {lab=VDD}
N 920 -0 1180 0 {lab=VOUT}
N 530 0 570 0 {lab=#net1}
N 380 70 380 240 {lab=VCONT}
N 350 240 380 240 {lab=VCONT}
N 100 240 150 240 {lab=#net2}
N 920 -0 920 450 {lab=VOUT}
N 870 0 920 -0 {lab=VOUT}
N -180 450 920 450 {lab=VOUT}
N -180 260 -180 450 {lab=VOUT}
N -180 260 -100 260 {lab=VOUT}
N -180 220 -100 220 {lab=VIN}
N -180 -0 -180 220 {lab=VIN}
N -180 -0 310 -0 {lab=VIN}
N 0 130 0 160 {lab=VDD}
N 250 320 250 360 {lab=VSS}
N -0 320 0 360 {lab=VSS}
N 420 -100 420 -60 {lab=VDD}
N 460 70 460 100 {lab=VSS}
N -240 -0 -180 0 {lab=VIN}
N -470 370 -470 380 {lab=#net3}
C {vsource.sym} -470 410 0 0 {name=Vin value="PULSE(0 1.2 0 10p 10p 0.99n 2n)"}
C {devices/lab_pin.sym} 1230 0 0 1 {name=p4 sig_type=std_logic lab=VOUT}
C {code_shown.sym} -530 570 0 0 {name=MODEL1 only_toplevel=true
format="tcleval( @value )"
value="

.param corner=0

.if (corner==0)
.lib cornerMOSlv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.include $::env(PDK_ROOT)/$::env(PDK)/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
.endif
"}
C {devices/code_shown.sym} -590 -460 0 0 {name=NGSPICE1 only_toplevel=true
value="
.control
 tran 1p 10n
 plot v(VIN) v(VOUT)
 plot v(VCONT)
.endc
"
spice_ignore=true}
C {capa.sym} 1180 80 0 0 {name=C3
m=1
value=100f
footprint=1206
device="ceramic capacitor"}
C {vsource.sym} -470 170 0 0 {name=V2 value=1.2 savecurrent=false}
C {gnd.sym} -470 220 0 0 {name=l1 lab=GND}
C {lab_pin.sym} -470 140 2 0 {name=p8 sig_type=std_logic lab=VDD}
C {vsource.sym} -370 170 0 0 {name=V5 value=0 savecurrent=false}
C {gnd.sym} -370 220 0 0 {name=l8 lab=GND}
C {lab_pin.sym} -370 140 2 0 {name=p9 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1180 130 2 0 {name=p11 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} -470 280 0 0 {name=p12 sig_type=std_logic lab=VIN}
C {devices/lab_pin.sym} -240 0 0 0 {name=p13 sig_type=std_logic lab=VIN}
C {lab_pin.sym} -470 470 2 0 {name=p14 sig_type=std_logic lab=VSS}
C {code.sym} -280 -460 0 0 {name=PHASE_MEASR1 only_toplevel=true
value="
.control
* ---- settings you tweak ----


   * ---- user settings ----
  let vlow  = 0
  let vhigh = 1.2
  let v50   = vlow + 0.5*(vhigh - vlow)

  let start_edge = 0     ; skip early edges (settling)
  let N = 200             ; number of phase samples



  tran 1p 10n

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
}
C {code.sym} -280 -280 0 0 {name=TRANSIENT1 only_toplevel=true
value="
.control
 tran 1p 200n
 plot v(VIN) v(VOUT)
 plot v(VCONT)
.endc
"
spice_ignore=true}
C {code.sym} -90 -460 0 0 {name=PHASE_vs_VCONT1 only_toplevel=true
value="
.control
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
.endc
"
spice_ignore=true}
C {DLine.sym} 720 0 0 0 {name=x1}
C {lab_pin.sym} 720 100 2 0 {name=p1 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 720 -100 2 0 {name=p2 sig_type=std_logic lab=VDD}
C {VCDL.sym} 420 0 0 0 {name=x2}
C {PD.sym} 0 240 0 0 {name=x3
}
C {CP.sym} 250 240 0 0 {name=x4
}
C {lab_pin.sym} 420 -100 2 0 {name=p3 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 460 100 2 0 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 250 360 2 0 {name=p6 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 0 360 2 0 {name=p7 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 0 130 2 0 {name=p10 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 380 150 2 0 {name=p15 sig_type=std_logic lab=VCONT}
C {sg13g2_inv_2.sym} -470 330 3 0 {name=x5 VDD=VDD VSS=VSS prefix=sg13g2_}
