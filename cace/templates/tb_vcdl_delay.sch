v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {netlist_not_shown.sym} 0 0 0 0 {name=s1 only_toplevel=false value=".param period_s = '1/CACE\{fin\}'
.lib CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.tech/ngspice/models/cornerMOSlv.lib mos_CACE\{corner\}
.lib CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.tech/ngspice/models/cornerRES.lib res_typ
.lib CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.tech/ngspice/models/cornerCAP.lib cap_typ
.include CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
.include \"CACE\{DUT_path\}\"
.temp CACE\{temperature\}
Vdd VDD GND CACE\{vdd\}
Vss VSS GND 0
Vin VIN GND PULSE(0 CACE\{vdd\} 0 10p 10p 'period_s/2' 'period_s')
Vcont_slow VCONT_SLOW GND 'CACE\{vdd\}/2'
Vcont_fast VCONT_FAST GND CACE\{vdd\}
XDUT_slow VDD VIN VOUT_SLOW VCONT_SLOW VSS VCDL
XDUT_fast VDD VIN VOUT_FAST VCONT_FAST VSS VCDL
Cload_slow VOUT_SLOW GND CACE\{cload\}
Cload_fast VOUT_FAST GND CACE\{cload\}
.tran 1p 'period_s*8'
.control
run
meas tran t_in WHEN v(VIN)='CACE\{vdd\}/2' RISE=3
meas tran t_out_slow WHEN v(VOUT_SLOW)='CACE\{vdd\}/2' FALL=3
meas tran t_out_fast WHEN v(VOUT_FAST)='CACE\{vdd\}/2' FALL=3
let delay_max = t_out_slow-t_in
let delay_min = t_out_fast-t_in
let delay_range = delay_max-delay_min
set filetype=ascii
echo $&delay_min $&delay_max $&delay_range > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc"}
