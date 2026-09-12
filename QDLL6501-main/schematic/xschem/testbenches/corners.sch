v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {code.sym} -340 -230 0 0 {name=TRANSIENT_TT_VN_TN_RT_CT only_toplevel=true
value="
.param temp=65 
.param VDD1P2=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=\{VDD1P2\} vd=\{VDD1P2\}


.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt

.endc
"}
C {code.sym} -30 -230 0 0 {name=TRANSIENT_TT_VN_TN_RB_CB only_toplevel=true
value="
.param temp=65 
.param VDD1P2=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=\{VDD1P2\} vd=\{VDD1P2\}


.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_bcs
.lib cornerRES.lib res_bcs
.lib cornerDIO.lib dio_tt

.endc
"}
C {code.sym} 290 -230 0 0 {name=TRANSIENT_TT_VN_TN_RW_CW only_toplevel=true
value="
.param temp=65 
.param VDD1P2=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=\{VDD1P2\} vd=\{VDD1P2\}


.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_wcs
.lib cornerRES.lib res_wcs
.lib cornerDIO.lib dio_tt

.endc
"}
C {code.sym} -350 0 0 0 {name=TRANSIENT_FF_VL_TH_RT_CT only_toplevel=true
value="
.param temp=125 
.param VDD1P2=1.08 
.param per=4n duty=2n tr=19p tf=19p delay=1.9n
.param vin=\{VDD1P2\} vd=\{VDD1P2\}

.lib cornerMOSlv.lib mos_ff
.lib cornerRES.lib   res_typ
.lib cornerCAP.lib   cap_typ
.lib cornerDIO.lib dio_tt

.endc
"
}
C {code.sym} -30 0 0 0 {name=TRANSIENT_SS_VH_TL_RT_CT only_toplevel=true
value="
.param temp=0 
.param VDD1P2=1.32 
.param per=4n duty=2n tr=21p tf=21p delay=2.1n
.param vin=\{VDD1P2\} vd=\{VDD1P2\}


.lib cornerMOSlv.lib mos_ss
.lib cornerRES.lib   res_typ
.lib cornerCAP.lib   cap_typ
.lib cornerDIO.lib dio_tt

.endc
"
}
C {code.sym} -360 200 0 0 {name=TRANSIENT_SF_VN_TN_RT_CT only_toplevel=true
value="

.param temp=65 
.param VDD1P2=1.2
.param per=4n duty=2n tr=21p tf=19p delay=2n
.param vin=\{VDD1P2\} vd=\{VDD1P2\}


.lib cornerMOSlv.lib mos_sf
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt

.endc
"}
C {code.sym} -40 200 0 0 {name=TRANSIENT_FS_VN_TN_RT_CT only_toplevel=true
value="
.param temp=65 
.param VDD1P2=1.2
.param per=4n duty=2n tr=19p tf=21p delay=2n
.param vin=\{VDD1P2\} vd=\{VDD1P2\}


.lib cornerMOSlv.lib mos_fs
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt

.endc
"}
