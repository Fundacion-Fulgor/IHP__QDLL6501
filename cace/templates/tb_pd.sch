v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {netlist_not_shown.sym} 0 0 0 0 {name=s1 only_toplevel=false value=".param period_s = '1/CACE\{fin\}'
.param phase_delay_s = 'period_s/8'
.lib CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.tech/ngspice/models/cornerMOSlv.lib mos_CACE\{corner\}
.lib CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.tech/ngspice/models/cornerRES.lib res_typ
.lib CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.tech/ngspice/models/cornerCAP.lib cap_typ
.include CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
.include \"CACE\{DUT_path\}\"
.temp CACE\{temperature\}
Vdd VDD GND CACE\{vdd\}
Vss VSS GND 0
Vref CK_REF GND PULSE(0 CACE\{vdd\} 0 10p 10p 'period_s/2' 'period_s')
Vin CK_IN GND PULSE(0 CACE\{vdd\} 'phase_delay_s' 10p 10p 'period_s/2' 'period_s')
XPD VDD VSS CK_IN PDOUT CK_REF PD
Cload PDOUT GND CACE\{cload\}
.tran 1p 'period_s*12'
.control
run
let measure_start = 4/CACE\{fin\}
let measure_end = 12/CACE\{fin\}
meas tran vout_avg AVG v(PDOUT) FROM=$&measure_start TO=$&measure_end
let pd_gain = vout_avg/0.7853981633974483
set filetype=ascii
echo $&pd_gain > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc"}
