v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N -170 410 -170 480 {lab=VCONT2}
N 290 580 290 650 {lab=CPOUT2}
N 0 -100 0 -70 {lab=VDD}
N 0 60 0 100 {lab=VSS}
N 150 -10 180 -10 {lab=OUT3}
N -190 -10 -150 -10 {lab=IN3}
N -30 -640 10 -640 {lab=#net1}
N -20 -330 30 -330 {lab=#net2}
N -120 -440 -120 -410 {lab=VDD}
N 130 -250 130 -210 {lab=VSS}
N -120 -250 -120 -210 {lab=VSS}
N -140 -760 -140 -700 {lab=VDD}
N 160 -760 160 -700 {lab=VDD}
N -140 -760 160 -760 {lab=VDD}
N 380 -640 440 -640 {lab=OUT1}
N 310 -640 380 -640 {lab=OUT1}
N -320 -180 380 -180 {lab=OUT1}
N -320 -640 -250 -640 {lab=IN1}
N -100 -570 160 -570 {lab=VSS}
N -180 -570 -180 -490 {lab=#net3}
N 160 -580 160 -570 {lab=VSS}
N -100 -570 -100 -540 {lab=VSS}
N 160 -570 160 -540 {lab=VSS}
N -320 -350 -220 -350 {lab=IN1}
N -180 -490 280 -490 {lab=#net3}
N 280 -490 280 -330 {lab=#net3}
N 230 -330 280 -330 {lab=#net3}
N -320 -310 -320 -180 {lab=OUT1}
N 380 -640 380 -180 {lab=OUT1}
N -320 -640 -320 -350 {lab=IN1}
N -410 -640 -320 -640 {lab=IN1}
N -20 340 20 340 {lab=#net4}
N -10 650 40 650 {lab=#net5}
N -110 540 -110 570 {lab=VDD}
N 140 730 140 770 {lab=VSS}
N -110 730 -110 770 {lab=VSS}
N -130 220 -130 280 {lab=VDD}
N 170 220 170 280 {lab=VDD}
N -130 220 170 220 {lab=VDD}
N 320 340 390 340 {lab=OUT2}
N -310 800 390 800 {lab=OUT2}
N -310 340 -240 340 {lab=IN2}
N -90 410 170 410 {lab=VSS}
N 170 400 170 410 {lab=VSS}
N -90 410 -90 440 {lab=VSS}
N 170 410 170 440 {lab=VSS}
N -310 630 -210 630 {lab=IN2}
N 240 650 290 650 {lab=CPOUT2}
N -310 670 -310 800 {lab=OUT2}
N 390 340 390 800 {lab=OUT2}
N -310 340 -310 630 {lab=IN2}
N -400 340 -310 340 {lab=IN2}
N 390 340 460 340 {lab=OUT2}
N -310 670 -210 670 {lab=OUT2}
N -320 -310 -220 -310 {lab=OUT1}
C {iopin.sym} -720 -490 2 0 {name=p1 lab=VDD
}
C {iopin.sym} -720 -460 2 0 {name=p2 lab=VSS}
C {ipin.sym} -410 -640 0 0 {name=p7 lab=IN1}
C {ipin.sym} -400 340 0 0 {name=p8 lab=IN2}
C {opin.sym} 440 -640 0 0 {name=p11 lab=OUT1}
C {opin.sym} 460 340 0 0 {name=p12 lab=OUT2}
C {opin.sym} 290 580 3 0 {name=p9 lab=CPOUT2}
C {ipin.sym} -170 480 0 0 {name=p10 lab=VCONT2}
C {lab_wire.sym} 0 -100 0 0 {name=p13 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 0 100 0 0 {name=p14 sig_type=std_logic lab=VSS}
C {opin.sym} 180 -10 0 0 {name=p15 lab=OUT3}
C {ipin.sym} -190 -10 0 0 {name=p16 lab=IN3}
C {lab_pin.sym} 160 -540 2 0 {name=p17 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 160 -740 2 0 {name=p18 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -140 -740 2 0 {name=p19 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -100 -540 2 0 {name=p20 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 130 -210 2 0 {name=p21 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -120 -210 2 0 {name=p22 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -120 -440 2 0 {name=p23 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 170 440 2 0 {name=p24 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 170 240 2 0 {name=p25 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -130 240 2 0 {name=p26 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -90 440 2 0 {name=p27 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 140 770 2 0 {name=p28 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -110 770 2 0 {name=p29 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -110 540 2 0 {name=p30 sig_type=std_logic lab=VDD}
C {VCDL.sym} -140 -640 0 0 {name=x2}
C {VCDL.sym} -130 340 0 0 {name=x5}
C {DLine.sym} 170 340 0 0 {name=x1}
C {DLine.sym} 0 -10 0 0 {name=x3}
C {DLine.sym} 160 -640 0 0 {name=x4}
C {PD.sym} -110 650 0 0 {name=x6}
C {PD.sym} -120 -330 0 0 {name=x7}
C {CP.sym} 130 -330 0 0 {name=x8}
C {CP.sym} 140 650 0 0 {name=x9}
