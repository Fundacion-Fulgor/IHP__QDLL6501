v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {code.sym} -340 -230 0 0 {name=TRANSIENT_TT_VN_TN_RT_CT only_toplevel=true
value="
.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=1.2 vd=\{vdd\}


.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ

.endc
"}
C {code.sym} -30 -230 0 0 {name=TRANSIENT_TT_VN_TN_RB_CB only_toplevel=true
value="
.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=1.2 vd=\{vdd\}


.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_bsc
.lib cornerRES.lib res_bsc

.endc
"}
C {code.sym} 290 -230 0 0 {name=TRANSIENT_TT_VN_TN_RW_CW only_toplevel=true
value="
.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=20p tf=20p delay=2n
.param vin=1.2 vd=\{vdd\}


.lib cornerMOSlv.lib mos_tt
.lib cornerCAP.lib cap_wsc
.lib cornerRES.lib res_wsc

.endc
"}
C {code.sym} -350 0 0 0 {name=TRANSIENT_FF_VL_TH_RT_CT only_toplevel=true
value="
.param temp=125 vdd=1.08 
.param per=4n duty=2n tr=19p tf=19p delay=1.9n
.param vin=1.08 vd=\{vdd\}

.lib cornerMOSlv.lib mos_ff
.lib cornerRES.lib   res_typ
.lib cornerCAP.lib   cap_typ

.endc
"
}
C {code.sym} -30 0 0 0 {name=TRANSIENT_SS_VH_TL_RT_CT only_toplevel=true
value="
.param temp=0 vdd=1.32
.param per=4n duty=2n tr=21p tf=21p delay=2.1n
.param vin=1.32 vd=\{vdd\}


.lib cornerMOSlv.lib mos_ss
.lib cornerRES.lib   res_typ
.lib cornerCAP.lib   cap_typ


.endc
"
}
C {code.sym} -360 200 0 0 {name=TRANSIENT_SF_VN_TN_RT_CT only_toplevel=true
value="
.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=21p tf=19p delay=2n
.param vin=1.2 vd=\{vdd\}


.lib cornerMOSlv.lib mos_sf
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ

.endc
"}
C {code.sym} -40 200 0 0 {name=TRANSIENT_FS_VN_TN_RT_CT1 only_toplevel=true
value="
.param temp=65 vdd=1.2 
.param per=4n duty=2n tr=19p tf=21p delay=2n
.param vin=1.2 vd=\{vdd\}


.lib cornerMOSlv.lib mos_fs
.lib cornerCAP.lib cap_typ
.lib cornerRES.lib res_typ

.endc
"}
