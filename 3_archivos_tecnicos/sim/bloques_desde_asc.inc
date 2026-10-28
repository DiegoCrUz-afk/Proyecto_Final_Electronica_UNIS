* Subcircuitos armados desde los esquematicos dibujados (BLOQUE_*.asc) - generado por armar_desde_asc.py
.model SWSCH SW(Ron=1 Roff=1G Vt=2.5 Vh=0.5)
.subckt HC_AND2 a b y vcc
B1 yi 0 V=V(vcc)*u(V(a)-V(vcc)/2)*u(V(b)-V(vcc)/2)
Ro yi y 50
Co y 0 5p
.ends
.subckt HC_NAND2 a b y vcc
B1 yi 0 V=V(vcc)*(1-u(V(a)-V(vcc)/2)*u(V(b)-V(vcc)/2))
Ro yi y 50
Co y 0 5p
.ends
.subckt HC_BUF a y vcc
B1 yi 0 V=V(vcc)*u(V(a)-V(vcc)/2)
Ro yi y 50
Co y 0 5p
.ends
.subckt HC_SCHINV a y vcc
S1 yi 0 a 0 SWSCH
Rp vcc yi 1k
Rcl yi y 50
Co y 0 5p
.ends
.subckt REG5V vm v5
Rz vm bz 510
DZ P001 bz D1N4734
Rtr P001 0 10
Q1 vm bz v5 0 QBD139
Cout v5 0 100u
C2 v5 0 100n
.ends
.subckt SENSOR_IR v5 b tin p
Rled v5 P001 270
Dled P001 0 DIR
Cac b tin 1u
R1 v5 b 47k
R2 b 0 10k
Q2 c b P002 0 Q2N3904
Rc v5 c 680
RE P002 0 150
Ra v5 P003 10k
Rp1 P003 th {10k*(1-kir)}
Rp2 th P004 {10k*kir}
Rb P004 0 26.8k
Xu1 th c v5 0 p LM393
Rpu v5 p 10k
Rh p th 220k
.param kir=0.55
.ends
.subckt SOBRECORRIENTE vm v5 sh setn
Xu2 sh N002 vm 0 N001 LM358
Rg N002 0 1k
Rf N001 N002 6.8k
D1 N001 N003 D1N4148
Cpk N003 0 100n
Rbl N003 0 22k
Rd dl N003 10k
Cd dl 0 10u
Xu3 ref dl v5 0 setn LM393
Ra v5 P001 10k
Rp1 P001 ref {10k*(1-koc)}
Rp2 ref P002 {10k*koc}
Rb P002 0 10k
.param koc=0.2
.ends
.subckt TEMPERATURA v5 tnode setn
Rfix tnode 0 10k
Ra v5 P001 22k
Rp1 P001 ref {10k*(1-ktm)}
Rp2 ref P002 {10k*ktm}
Rb P002 0 68k
Xu4 ref tnode v5 0 setn LM393
Rh setn ref 1Meg
.param ktm=0.5
.ends
.subckt LOGICA v5 ein gin rin p setn m n l f fn
Rpe ein 0 10k
Rse ef ein 10k
Cef ef 0 100n
Xi1 ef N001 v5 HC_SCHINV
Xi2 N001 e v5 HC_SCHINV
Rpg gin 0 10k
Rsg gf gin 10k
Cgf gf 0 100n
Xi3 gf N002 v5 HC_SCHINV
Xi4 N002 g v5 HC_SCHINV
Rpr rin 0 10k
Rsr rf rin 10k
Crf rf 0 100n
Xi5 rf N003 v5 HC_SCHINV
Xi6 N003 rst v5 HC_SCHINV
Cpor v5 N004 1u
Rpor N004 0 47k
Dpor N004 rf D1N4148
Xg1 rst setn reset_n v5 HC_NAND2
Xg2 setn fn f v5 HC_NAND2
Xg3 reset_n f fn v5 HC_NAND2
Xg4 p p pn v5 HC_NAND2
Rsn v5 setn 10k
Xa1 e g m1 v5 HC_AND2
Xa2 m1 fn m v5 HC_AND2
Xa3 m pn n v5 HC_AND2
Xa4 m p l v5 HC_AND2
.ends
.subckt ALARMA vm f
Rb P001 f 1k
Q6 P002 P001 0 0 Q2N3904
Rbz vm P002 400
Rl f P003 470
Dl P003 0 DLED
.ends
.subckt REFVEL v5 l vref
Rt v5 vref 68k
Rp1 vref 0 {10k*kvn}
Rp2 vref P001 {10k*kvr}
Q5 P001 N001 0 0 Q2N3904
Rb5 N001 l 10k
Cr vref 0 100n
.param kvn=0.8 kvr=0.7
.ends
.subckt ENCODER_FV v5 enc vspd
Rled v5 P001 220
Dled P001 0 DIR
Rpe v5 enc 10k
Xu7 eref enc v5 0 eq LM393
Ru1 v5 eref 10k
Ru2 eref 0 10k
Rpq v5 eq 10k
Rhe eq eref 1Meg
Cd tg eq 1n
Rtg v5 tg 10k
Dcl tg v5 D1N4148
X7 0 tg mono v5 N002 dis7 dis7 v5 NE555
Rt7 v5 dis7 20k
Ct7 dis7 0 10n
Ccvm N002 0 10n
Xb1 mono N001 v5 HC_BUF
Rfv vf1 N001 10k
Cfv vf1 0 1u
Rfv2 vspd vf1 10k
Cfv2 vspd 0 1u
.ends
.subckt ERROR_AMP vm v5 vref vspd vctrl
Xbr vref vrb vm 0 vrb LM358
Xbs vspd vsb vm 0 vsb LM358
Xbo voff vob vm 0 vob LM358
Rv1 v5 voff 4.7k
Rv2 voff 0 5.1k
Cv voff 0 100n
R1 inn vsb 10k
R3 inp vrb 10k
R4 inp vob {Kerr*10k}
Rf6 oa inn {Kerr*10k}
Cf6 oa inn 10n
Xu2b inp inn vm 0 oa LM358
Ro vctrl oa 1k
Cvc vctrl 0 100n
.param Kerr=10
.ends
.subckt PWM_GEN v5 vctrl pwm
X5 0 tri tri_o v5 cv tri N001 v5 NE555
Ra5 v5 N001 1k
Rb5 N001 tri 10k
Ct tri 0 10n
Ccv cv 0 10n
Xu6 vctrl tri v5 0 pwm LM393
Rpu v5 pwm 10k
.ends
.subckt POTENCIA v5 vm pwm m dm sh
Xa5 pwm m N001 v5 HC_AND2
Q3 v5 N001 N002 0 Q2N3904
Q4 0 N001 N002 0 Q2N3906
Rg gate N002 47
Rpd gate 0 10k
M1 dm gate sh sh IRLZ44N
Dfw dm vm D1N5819
Rsh sh 0 0.47
.ends
