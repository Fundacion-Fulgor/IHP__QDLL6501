v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 200 110 200 130 {lab=VSS}
N -820 -30 -820 -10 {lab=GND}
N -720 -30 -720 -10 {lab=GND}
N -820 130 -820 160 {lab=VSS}
N -820 50 -820 70 {lab=VIN}
N 200 0 250 0 {lab=VOUT}
N 200 0 200 50 {lab=VOUT}
N -400 0 -230 -0 {lab=VIN}
N 70 -0 200 0 {lab=VOUT}
N -80 60 -80 100 {lab=VSS}
N -80 -100 -80 -60 {lab=VDD}
C {vsource.sym} -820 100 0 0 {name=Vin value="PULSE(0 1.2 0 10p 10p 0.99n 2n)"}
C {devices/lab_pin.sym} 250 0 0 1 {name=p4 sig_type=std_logic lab=VOUT}
C {code_shown.sym} -1010 -330 0 0 {name=MODEL1 only_toplevel=true
format="tcleval( @value )"
value="

.param corner=0

.if (corner==0)
.lib cornerMOSlv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.include /foss/pdks/ihp-sg13g2/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
.endif
"}
C {devices/code_shown.sym} -900 -570 0 0 {name=NGSPICE1 only_toplevel=true
value="
.control
 tran 1p 10n
 plot v(VIN) v(VOUT)
 plot v(VCONT)
.endc
"
spice_ignore=true}
C {capa.sym} 200 80 0 0 {name=C3
m=1
value=100f
footprint=1206
device="ceramic capacitor"}
C {vsource.sym} -820 -60 0 0 {name=V2 value=1.2 savecurrent=false}
C {gnd.sym} -820 -10 0 0 {name=l1 lab=GND}
C {lab_pin.sym} -820 -90 2 0 {name=p8 sig_type=std_logic lab=VDD}
C {vsource.sym} -720 -60 0 0 {name=V5 value=0 savecurrent=false}
C {gnd.sym} -720 -10 0 0 {name=l8 lab=GND}
C {lab_pin.sym} -720 -90 2 0 {name=p9 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 200 130 2 0 {name=p11 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} -820 50 0 0 {name=p12 sig_type=std_logic lab=VIN}
C {devices/lab_pin.sym} -400 0 0 0 {name=p13 sig_type=std_logic lab=VIN}
C {lab_pin.sym} -820 160 2 0 {name=p14 sig_type=std_logic lab=VSS}
C {code.sym} -590 -570 0 0 {name=PHASE_MEASR1 only_toplevel=true
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
C {code.sym} -590 -390 0 0 {name=TRANSIENT1 only_toplevel=true
value="
.control
 tran 1p 10n
 plot v(VIN) v(VOUT)
 *plot v(VCONT)
.endc
"
spice_ignore=true}
C {code.sym} -400 -570 0 0 {name=PHASE_vs_VCONT1 only_toplevel=true
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
C {/foss/designs/DLL/2026/Cells/DLine.sym} -80 0 0 0 {name=x1}
C {lab_pin.sym} -80 100 2 0 {name=p1 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -80 -100 2 0 {name=p2 sig_type=std_logic lab=VDD}
