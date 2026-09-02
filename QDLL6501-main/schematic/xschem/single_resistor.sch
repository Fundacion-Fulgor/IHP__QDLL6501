v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N -80 0 -30 0 {lab=RIN}
N 30 0 80 -0 {lab=ROUT}
C {ipin.sym} -80 0 0 0 {name=p1 lab=RIN}
C {iopin.sym} 0 -60 0 0 {name=p2 lab=VSS}
C {sg13g2_pr/rppd.sym} 0 0 1 0 {name=R13
w=1e-6
l=10e-6
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
value="expr(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )"
}
C {opin.sym} 80 0 0 0 {name=p5 lab=ROUT}
