v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 150 60 150 80 {lab=VSS}
N 100 0 200 0 {lab=VOUT}
N -370 280 -370 290 {lab=VSS}
N -600 100 -600 120 {lab=GND}
N -500 100 -500 120 {lab=GND}
N -40 70 -40 120 {lab=VCONT}
N -600 260 -600 290 {lab=VSS}
N -600 180 -600 200 {lab=VIN}
N -170 0 -110 0 {lab=VIN}
N -370 180 -370 200 {lab=VCONT}
N 40 70 40 120 {lab=VSS}
N 0 -110 0 -60 {lab=VDD}
N -290 260 -290 280 {lab=VSS}
N -370 280 -290 280 {lab=VSS}
N -370 260 -370 280 {lab=VSS}
N -370 180 -290 180 {lab=VCONT}
N -370 170 -370 180 {lab=VCONT}
N -290 180 -290 200 {lab=VCONT}
C {vsource.sym} -600 230 0 0 {name=Vin value="PULSE(0 1.2 0 10p 10p 0.99n 2n)"}
C {devices/lab_pin.sym} 200 0 0 1 {name=p2 sig_type=std_logic lab=VOUT}
C {code_shown.sym} -680 -240 0 0 {name=MODEL1 only_toplevel=true
format="tcleval( @value )"
value="

.param corner=0

.if (corner==0)
.lib cornerMOSlv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.endif
"}
C {devices/code_shown.sym} -680 -440 0 0 {name=NGSPICE1 only_toplevel=true
value="
.control
 tran 1p 10n
 plot v(VIN) v(VOUT)
 plot v(VCONT)
.endc
"
spice_ignore=true}
C {capa.sym} 150 30 0 0 {name=C1
m=1
value=100f
footprint=1206
device="ceramic capacitor"}
C {devices/vsource.sym} -370 230 0 0 {name=Vcont1 value="PWL(100n 0 200n 1.2)"
spice_ignore=true}
C {VCDL.sym} 0 0 0 0 {name=x1}
C {vsource.sym} -600 70 0 0 {name=V3 value=1.2 savecurrent=false}
C {gnd.sym} -600 120 0 0 {name=l6 lab=GND}
C {lab_pin.sym} -600 40 2 0 {name=p3 sig_type=std_logic lab=VDD}
C {vsource.sym} -500 70 0 0 {name=V4 value=0 savecurrent=false}
C {gnd.sym} -500 120 0 0 {name=l7 lab=GND}
C {lab_pin.sym} -500 40 2 0 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -370 290 2 0 {name=p4 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 150 80 2 0 {name=p6 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} -600 180 0 0 {name=p7 sig_type=std_logic lab=VIN}
C {devices/lab_pin.sym} -170 0 0 0 {name=p8 sig_type=std_logic lab=VIN}
C {lab_pin.sym} -600 290 2 0 {name=p1 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} -370 170 0 0 {name=p9 sig_type=std_logic lab=VCONT}
C {devices/lab_pin.sym} -40 120 0 0 {name=p10 sig_type=std_logic lab=VCONT}
C {lab_pin.sym} 40 120 2 0 {name=p11 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 0 -110 2 0 {name=p12 sig_type=std_logic lab=VDD}
C {code.sym} -370 -440 0 0 {name=PHASE_MEASR only_toplevel=true
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
C {vsource.sym} -290 230 0 0 {name=V1 value=0.6 savecurrent=false
}
