v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {netlist_not_shown.sym} 0 0 0 0 {name=s1 only_toplevel=false value=".param period_s = '1/CACE\{fin\}'
.param clock_start = 'period_s*5'
.lib CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.tech/ngspice/models/cornerMOSlv.lib mos_CACE\{corner\}
.lib CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.tech/ngspice/models/cornerRES.lib res_typ
.lib CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.tech/ngspice/models/cornerCAP.lib cap_typ
.include CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
.include \"CACE\{DUT_path\}\"
.temp CACE\{temperature\}
Vdd VDD GND CACE\{vdd\}
Vss VSS GND 0
Vin1 IN1 GND PULSE(0 CACE\{vdd\} 'clock_start' 10p 10p 'period_s/2' 'period_s')
Vin2 IN2 GND PULSE(0 CACE\{vdd\} 'clock_start+period_s/4' 10p 10p 'period_s/2' 'period_s')
Vin3 IN3 GND PULSE(0 CACE\{vdd\} 'clock_start' 10p 10p 'period_s/2' 'period_s')
Vcont2 VCONT2 GND 'CACE\{vdd\}/2'
XDUT VDD VSS IN1 OUT1 OUT2 IN2 CPOUT2 VCONT2 IN3 OUT3 QDLL_TOP
Cload1 OUT1 GND CACE\{cload\}
Cload2 OUT2 GND CACE\{cload\}
Cload3 OUT3 GND CACE\{cload\}
Cloadcp CPOUT2 GND CACE\{cload\}
.tran 10p 'period_s*30'
.control
run
let static_start = 2/CACE\{fin\}
let static_end = 4/CACE\{fin\}
let dynamic_start = 20/CACE\{fin\}
let dynamic_end = 30/CACE\{fin\}
meas tran idd_static AVG i(Vdd) FROM=$&static_start TO=$&static_end
meas tran idd_dynamic AVG i(Vdd) FROM=$&dynamic_start TO=$&dynamic_end
let idd_static_abs = abs(idd_static)
let idd_dynamic_abs = abs(idd_dynamic)
set filetype=ascii
echo $&idd_static_abs $&idd_dynamic_abs > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc"}
