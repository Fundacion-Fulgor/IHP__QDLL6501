v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N -210 -0 -160 -0 {lab=RIN}
N -100 -0 -70 0 {lab=#net1}
N -10 -0 20 0 {lab=#net2}
N 80 -0 120 -0 {lab=#net3}
N 180 -0 230 0 {lab=#net4}
N 290 0 320 0 {lab=#net5}
N 380 0 410 0 {lab=#net6}
N 470 0 510 0 {lab=#net7}
N 570 0 620 0 {lab=#net8}
N 680 0 710 0 {lab=#net9}
N 770 0 800 0 {lab=#net10}
N 860 0 900 0 {lab=#net11}
N 960 0 1010 0 {lab=ROUT}
C {ipin.sym} -210 0 0 0 {name=p1 lab=RIN}
C {opin.sym} 1010 0 0 0 {name=p5 lab=ROUT}
C {iopin.sym} -210 80 0 0 {name=p2 lab=VSS}
C {sg13g2_pr/rppd.sym} -130 0 1 0 {name=R13
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {sg13g2_pr/rppd.sym} -40 0 1 0 {name=R1
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {sg13g2_pr/rppd.sym} 50 0 1 0 {name=R2
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {sg13g2_pr/rppd.sym} 150 0 1 0 {name=R3
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {sg13g2_pr/rppd.sym} 260 0 1 0 {name=R4
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {sg13g2_pr/rppd.sym} 350 0 1 0 {name=R5
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {sg13g2_pr/rppd.sym} 440 0 1 0 {name=R6
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {sg13g2_pr/rppd.sym} 540 0 1 0 {name=R7
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {sg13g2_pr/rppd.sym} 650 0 1 0 {name=R8
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {sg13g2_pr/rppd.sym} 740 0 1 0 {name=R9
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {sg13g2_pr/rppd.sym} 830 0 1 0 {name=R10
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {sg13g2_pr/rppd.sym} 930 0 1 0 {name=R11
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
