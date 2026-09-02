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
Vin1 IN1 GND 0
Vin2 IN2 GND 0
Vin3 IN3 GND PULSE(0 CACE\{vdd\} 'clock_start' 10p 10p 'period_s/2' 'period_s')
Vcont2 VCONT2 GND 'CACE\{vdd\}/2'
XDUT VDD VSS IN1 OUT1 OUT2 IN2 CPOUT2 VCONT2 IN3 OUT3 QDLL_TOP
Cload3 OUT3 GND CACE\{cload\}
.tran 5p 'period_s*14'
.control
run
let t_in_rise = -1e99
let t_in_fall = -1e99
let t_out_fall = 1e99
let t_out_rise = 1e99
let out3_slew_rise = 1e99
let out3_slew_fall = 1e99
let out3_high_width = -1e99
let out3_low_width = -1e99
meas tran t_in_rise WHEN v(IN3)='CACE\{vdd\}/2' RISE=6
meas tran t_in_fall WHEN v(IN3)='CACE\{vdd\}/2' FALL=6
meas tran t_out_fall WHEN v(OUT3)='CACE\{vdd\}/2' FALL=6
meas tran t_out_rise WHEN v(OUT3)='CACE\{vdd\}/2' RISE=6
let out3_delay_fall = t_out_fall-t_in_rise
let out3_delay_rise = t_out_rise-t_in_fall
meas tran out3_slew_rise TRIG v(OUT3) VAL='CACE\{vdd\}*0.1' RISE=6 TARG v(OUT3) VAL='CACE\{vdd\}*0.9' RISE=6
meas tran out3_slew_fall TRIG v(OUT3) VAL='CACE\{vdd\}*0.9' FALL=6 TARG v(OUT3) VAL='CACE\{vdd\}*0.1' FALL=6
meas tran out3_high_width TRIG v(OUT3) VAL='CACE\{vdd\}/2' RISE=6 TARG v(OUT3) VAL='CACE\{vdd\}/2' FALL=7
meas tran out3_low_width TRIG v(OUT3) VAL='CACE\{vdd\}/2' FALL=6 TARG v(OUT3) VAL='CACE\{vdd\}/2' RISE=6
meas tran out3_high MAX v(OUT3)
meas tran out3_low MIN v(OUT3)
set filetype=ascii
echo $&out3_delay_fall $&out3_delay_rise $&out3_slew_rise $&out3_slew_fall $&out3_high_width $&out3_low_width $&out3_high $&out3_low > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc"}
