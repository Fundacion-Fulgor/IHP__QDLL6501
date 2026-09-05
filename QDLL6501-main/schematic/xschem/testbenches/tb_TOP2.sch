v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 0 310 0 330 {lab=VSS}
N -850 210 -850 230 {lab=GND}
N -750 210 -750 230 {lab=GND}
N -850 450 -850 480 {lab=VSS}
N -850 290 -850 390 {lab=VIN}
N 0 200 50 200 {lab=VOUT}
N 0 200 0 250 {lab=VOUT}
N -450 180 -390 180 {lab=VIN}
N -300 260 -300 330 {lab=VCONT}
N -300 330 -170 330 {lab=VCONT}
N -170 260 -170 330 {lab=VCONT}
N -240 260 -240 280 {lab=VSS}
N -240 110 -240 140 {lab=VDD}
N -50 200 0 200 {lab=VOUT}
N -430 220 -390 220 {lab=VOUT}
N -430 220 -430 380 {lab=VOUT}
N -430 380 -50 380 {lab=VOUT}
N -50 200 -50 380 {lab=VOUT}
N -90 200 -50 200 {lab=VOUT}
C {vsource.sym} -850 420 0 0 {name=Vin value="PULSE(0 1.2 0 10p 10p 0.99n 2n)"}
C {devices/lab_pin.sym} 50 200 0 1 {name=p4 sig_type=std_logic lab=VOUT}
C {code_shown.sym} -910 580 0 0 {name=MODEL1 only_toplevel=true
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
C {devices/code_shown.sym} -1040 -250 0 0 {name=NGSPICE1 only_toplevel=true
value="
.control
 tran 1p 10n
 plot v(VIN) v(VOUT)
 plot v(VCONT)
.endc
"
spice_ignore=true}
C {capa.sym} 0 280 0 0 {name=C3
m=1
value=100f
footprint=1206
device="ceramic capacitor"}
C {vsource.sym} -850 180 0 0 {name=V2 value=1.2 savecurrent=false}
C {gnd.sym} -850 230 0 0 {name=l1 lab=GND}
C {lab_pin.sym} -850 150 2 0 {name=p8 sig_type=std_logic lab=VDD}
C {vsource.sym} -750 180 0 0 {name=V5 value=0 savecurrent=false}
C {gnd.sym} -750 230 0 0 {name=l8 lab=GND}
C {lab_pin.sym} -750 150 2 0 {name=p9 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 0 330 2 0 {name=p11 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} -850 290 0 0 {name=p12 sig_type=std_logic lab=VIN}
C {devices/lab_pin.sym} -450 180 0 0 {name=p13 sig_type=std_logic lab=VIN}
C {lab_pin.sym} -850 480 2 0 {name=p14 sig_type=std_logic lab=VSS}
C {code.sym} -730 -250 0 0 {name=PHASE_MEASR1 only_toplevel=true
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
spice_ignore=true}
C {code.sym} -730 -70 0 0 {name=TRANSIENT1 only_toplevel=true
value="
.control
 tran 1p 10n
 plot v(VIN) v(VOUT)
 plot v(VCONT)
.endc
"
}
C {code.sym} -540 -250 0 0 {name=PHASE_vs_VCONT1 only_toplevel=true
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
C {sg13g2_inv_2.sym} -850 340 3 0 {name=x5 VDD=VDD VSS=VSS prefix=sg13g2_ spice_ignore=true}
C {QDLL_TOP.sym} -240 200 0 0 {name=x1}
C {lab_pin.sym} -240 280 2 0 {name=p1 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -240 110 2 0 {name=p2 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} -300 330 0 0 {name=p3 sig_type=std_logic lab=VCONT}
