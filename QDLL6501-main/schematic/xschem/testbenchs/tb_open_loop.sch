v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 100 0 200 0 {lab=#net1}
N -370 280 -370 290 {lab=VSS}
N -600 100 -600 120 {lab=GND}
N -500 100 -500 120 {lab=GND}
N -40 70 -40 120 {lab=VCONT}
N -600 260 -600 290 {lab=VSS}
N -600 180 -600 200 {lab=VIN}
N -370 180 -370 200 {lab=VCONT}
N 40 70 40 120 {lab=VSS}
N 0 -110 0 -60 {lab=VDD}
N -290 260 -290 280 {lab=VSS}
N -370 280 -290 280 {lab=VSS}
N -370 260 -370 280 {lab=VSS}
N -370 180 -290 180 {lab=VCONT}
N -370 170 -370 180 {lab=VCONT}
N -290 180 -290 200 {lab=VCONT}
N 350 -110 350 -60 {lab=VDD}
N 350 70 350 120 {lab=VSS}
N 200 350 240 350 {lab=PDOUT}
N 60 430 60 450 {lab=VSS}
N 340 430 340 450 {lab=VSS}
N 200 450 200 500 {lab=VSS}
N 200 450 340 450 {lab=VSS}
N 60 230 60 270 {lab=VDD}
N -100 330 -40 330 {lab=VIN}
N 60 450 200 450 {lab=VSS}
N 200 320 200 350 {lab=PDOUT}
N 160 350 200 350 {lab=PDOUT}
N -170 0 -110 0 {lab=VIN}
N 500 0 580 0 {lab=VOUT}
N 440 350 500 350 {lab=VCP}
N -140 370 -140 390 {lab=VOUT}
N -140 370 -40 370 {lab=VOUT}
C {vsource.sym} -600 230 0 0 {name=Vin value="PULSE(0 1.2 0 100p 100p 2n 4n)"}
C {devices/lab_pin.sym} 580 0 0 1 {name=p2 sig_type=std_logic lab=VOUT}
C {devices/code_shown.sym} -680 -260 0 0 {name=NGSPICE1 only_toplevel=true
value="
.control
 tran 1p 10n
 plot v(VIN) v(VOUT)
 plot v(VCONT)
.endc
"
spice_ignore=true}
C {devices/vsource.sym} -370 230 0 0 {name=Vcont1 value="PWL(100n 0 200n 1.2)"
spice_ignore=true}
C {/foss/designs/DLL/2026/Cells/VCDL.sym} 0 0 0 0 {name=x1}
C {vsource.sym} -600 70 0 0 {name=V3 value=1.2 savecurrent=false}
C {gnd.sym} -600 120 0 0 {name=l6 lab=GND}
C {lab_pin.sym} -600 40 2 0 {name=p3 sig_type=std_logic lab=VDD}
C {vsource.sym} -500 70 0 0 {name=V4 value=0 savecurrent=false}
C {gnd.sym} -500 120 0 0 {name=l7 lab=GND}
C {lab_pin.sym} -500 40 2 0 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -370 290 2 0 {name=p4 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} -600 180 0 0 {name=p7 sig_type=std_logic lab=VIN}
C {devices/lab_pin.sym} -170 0 0 0 {name=p8 sig_type=std_logic lab=VIN}
C {lab_pin.sym} -600 290 2 0 {name=p1 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} -370 170 0 0 {name=p9 sig_type=std_logic lab=VCONT}
C {devices/lab_pin.sym} -40 120 0 0 {name=p10 sig_type=std_logic lab=VCONT}
C {lab_pin.sym} 40 120 2 0 {name=p11 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 0 -110 2 0 {name=p12 sig_type=std_logic lab=VDD}
C {code.sym} -370 -260 0 0 {name=PHASE_MEASR only_toplevel=true
value="
.control
* ---- settings you tweak ----


   * ---- user settings ----
  let vlow  = 0
  let vhigh = 1.2
  let v50   = vlow + 0.5*(vhigh - vlow)

  let start_edge = 0     ; skip early edges (settling)
  let N = 500             ; number of phase samples



  tran 2p 300n

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
C {code.sym} -370 -80 0 0 {name=TRANSIENT only_toplevel=true
value="
.control
 tran 1p 10n
 plot v(VIN) v(VOUT)
 plot v(VCONT)
.endc
"
spice_ignore=true}
C {code.sym} -180 -260 0 0 {name=PHASE_vs_VCONT only_toplevel=true
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
C {vsource.sym} -290 230 0 0 {name=V1 value=0.1 savecurrent=false
}
C {/foss/designs/DLL/2026/Cells/DLine.sym} 350 0 0 0 {name=x2}
C {lab_pin.sym} 350 -110 2 0 {name=p13 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 350 120 2 0 {name=p14 sig_type=std_logic lab=VSS}
C {/foss/designs/DLL/2026/Cells/PD.sym} 60 350 0 0 {name=x3}
C {/foss/designs/DLL/2026/Cells/CP.sym} 340 350 0 0 {name=x4}
C {lab_pin.sym} 200 500 2 0 {name=p15 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 60 230 2 0 {name=p16 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 200 320 1 0 {name=p19 sig_type=std_logic lab=PDOUT}
C {devices/lab_pin.sym} -100 330 0 0 {name=p6 sig_type=std_logic lab=VIN}
C {lab_pin.sym} 500 350 2 0 {name=p17 sig_type=std_logic lab=VCP}
C {devices/lab_pin.sym} -140 390 0 1 {name=p18 sig_type=std_logic lab=VOUT}
C {devices/code_shown.sym} -700 -530 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_tt
*.lib cornerMOSlv.lib mos_ss
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.include diodes.lib
.include sg13g2_bondpad.lib
.include /foss/pdks/ihp-sg13g2/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
"}
