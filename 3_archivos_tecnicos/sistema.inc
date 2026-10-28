* ============================================================
* Miniestacion industrial automatizada - bloques del circuito (LTspice)
* Cada .subckt es un bloque del diagrama (ver 1_Arquitectura). Nodos globales: 0 = tierra.
*   vm = 12 V despues del diodo de entrada, v5 = 5 V regulados
* Los valores marcados con trimpot se ajustan en el montaje.
* ============================================================

* ---- compuertas 74HC (modelo de comportamiento, Rout 50 ohm, tpd ~10 ns) ----
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
* inversor Schmitt (74HC14): umbrales 3.0 V (sube) y 2.0 V (baja)
.model SWSCH SW(Ron=1 Roff=1G Vt=2.5 Vh=0.5)
.subckt HC_SCHINV a y vcc
S1 yi 0 a 0 SWSCH
Rp vcc yi 1k
Rcl yi y 50
Co y 0 5p
.ends

* ---- Bloque 1: regulador 5 V (Zener + BJT de paso) ----
.subckt REG5V vm v5
Rz vm bz 510
DZ N1 bz D1N4734
Rtr 0 N1 10
Q1 vm bz v5 QBD139
Cout v5 0 100u
C2 v5 0 100n
.ends

* ---- Bloque 2: sensor IR (LED, emisor comun, comparador con histeresis). b = nodo donde entra la corriente del fototransistor ----
.subckt SENSOR_IR v5 b tin p
Rled v5 nled 270
Dled nled 0 DIR
R1 v5 b 47k
R2 b 0 10k
Cac tin b 1u
Q2 c b e Q2N3904
RE e 0 150
Rc v5 c 680
Ra v5 th1 10k
Rp1 th1 th {10k*(1-kir)}
Rp2 th th2 {10k*kir}
Rb th2 0 26.8k
Xu1 th c v5 0 p LM393
Rpu v5 p 10k
Rh p th 220k
.param kir=0.55
.ends

* ---- Bloque 3: sobrecorriente (shunt visto en nodo sh, vm alimenta el LM358) ----
.subckt SOBRECORRIENTE vm v5 sh setn
Xu2 sh fb vm 0 oa LM358
Rg fb 0 1k
Rf oa fb 6.8k
D1 oa pk D1N4148
Cpk pk 0 100n
Rbl pk 0 22k
Rd pk dl 10k
Cd dl 0 10u
Ra v5 rt 10k
Rp1 rt ref {10k*(1-koc)}
Rp2 ref rb2 {10k*koc}
Rb rb2 0 10k
Xu3 ref dl v5 0 setn LM393
.param koc=0.2
.ends

* ---- Bloque 4: sobretemperatura (ntc = nodo de la mitad del divisor NTC-10k) ----
.subckt TEMPERATURA v5 tnode setn
Rfix tnode 0 10k
Ra v5 rt 22k
Rp1 rt ref {10k*(1-ktm)}
Rp2 ref rb2 {10k*ktm}
Rb rb2 0 68k
Rh setn ref 1Meg
Xu4 ref tnode v5 0 setn LM393
.param ktm=0.5
.ends
* (el NTC va entre v5 y tnode: en las pruebas es una resistencia que depende de la temperatura)

* ---- Bloque 5: logica ----
.subckt LOGICA v5 ein gin rin p setn m n l f fn
* entradas: interruptor E, cubierta G y boton de reset (reposo = 0 por resistencia a tierra)
Rpe ein 0 10k
Rse ein ef 10k
Cef ef 0 100n
Rpg gin 0 10k
Rsg gin gf 10k
Cgf gf 0 100n
Rpr rin 0 10k
Rsr rin rf 10k
Crf rf 0 100n
* arranque: un pulso al encender borra la falla (reset automatico)
Cpor v5 por 1u
Rpor por 0 47k
Dpor por rf D1N4148
* inversores Schmitt (74HC14), dos por entrada: dejan la senal limpia y en logica positiva
Xi1 ef ein_n v5 HC_SCHINV
Xi2 ein_n e v5 HC_SCHINV
Xi3 gf gin_n v5 HC_SCHINV
Xi4 gin_n g v5 HC_SCHINV
Xi5 rf rin_n v5 HC_SCHINV
Xi6 rin_n rst v5 HC_SCHINV
* falla enclavada: pestillo con NAND (74HC00). setn activa en bajo (fallas de corriente o temperatura)
Rsn v5 setn 10k
Xg1 rst setn reset_n v5 HC_NAND2
Xg2 setn fn f v5 HC_NAND2
Xg3 reset_n f fn v5 HC_NAND2
Xg4 p p pn v5 HC_NAND2
* decision (74HC08)
Xa1 e g m1 v5 HC_AND2
Xa2 m1 fn m v5 HC_AND2
Xa3 m pn n v5 HC_AND2
Xa4 m p l v5 HC_AND2
.ends

* ---- Bloque 6: generador de PWM (NE555 como rampa + comparador) ----
.subckt PWM_GEN v5 vctrl pwm
X5 0 tri tri_o v5 cv tri dis v5 NE555
Ra5 v5 dis 1k
Rb5 dis tri 10k
Ct tri 0 10n
Ccv cv 0 10n
Xu6 vctrl tri v5 0 pwm LM393
Rpu v5 pwm 10k
.ends

* ---- Bloque 7: compuerta de seguridad, excitador y MOSFET (dm = terminal del motor, sh = fuente sobre el shunt) ----
.subckt POTENCIA v5 vm pwm m dm sh
Xa5 pwm m pwmg v5 HC_AND2
Q3 v5 pwmg g Q2N3904
Q4 0 pwmg g Q2N3906
Rg g gate 47
Rpd gate 0 10k
M1 dm gate sh sh IRFZ44N_P
Dfw dm vm D1N5819
Rsh sh 0 0.5
.ends

* ---- Bloque 8: encoder y convertidor frecuencia-voltaje (555 monoestable) ----
.subckt ENCODER_FV v5 enc vspd
Rpe v5 enc 10k
Rled v5 nled 220
Dled nled 0 DIR
Ru1 v5 eref 10k
Ru2 eref 0 10k
Xu7 eref enc v5 0 eq LM393
Rpq v5 eq 10k
Rhe eq eref 1Meg
Cd eq tg 1n
Rtg v5 tg 10k
Dcl tg v5 D1N4148
X7 0 tg mono v5 cvm dis7 dis7 v5 NE555
Rt7 v5 dis7 20k
Ct7 dis7 0 10n
Ccvm cvm 0 10n
Xb1 mono mq v5 HC_BUF
Rfv mq vf1 10k
Cfv vf1 0 1u
Rfv2 vf1 vspd 10k
Cfv2 vspd 0 1u
.ends

* ---- Bloque 9: referencia de velocidad (normal / reducida) ----
.subckt REFVEL v5 l vref
Rt v5 vref 68k
Rp1 vref 0 {10k*kvn}
Rb5 l bq 10k
Q5 cq bq 0 Q2N3904
Rp2 vref cq {10k*kvr}
Cr vref 0 100n
.param kvn=0.8 kvr=0.7
.ends

* ---- Bloque 10: amplificador de error (resta con ganancia Kerr) y selector lazo abierto / cerrado ----
* Vctrl = Kerr*(Vref - Vspd) + Voff. Tres seguidores (LM324) aislan la referencia, la velocidad medida y el nivel Voff.
.subckt ERROR_AMP vm v5 vref vspd vctrl
Xbr vref vrb vm 0 vrb LM358
Xbs vspd vsb vm 0 vsb LM358
Xbo voff vob vm 0 vob LM358
Rv1 v5 voff 4.7k
Rv2 voff 0 5.1k
Cv voff 0 100n
R1 vsb inn 10k
Rf6 oa inn {Kerr*10k}
Cf6 oa inn 10n
R3 vrb inp 10k
R4 inp vob {Kerr*10k}
Xu2b inp inn vm 0 oa LM358
Ro oa vctrl 1k
Cvc vctrl 0 100n
.param Kerr=10
.ends

* ---- Bloque 11: alarma ----
.subckt ALARMA vm f
Rb f ba 1k
Q6 cz ba 0 Q2N3904
Rbz vm cz 400
* senal luminosa: LED en serie con 470 ohm desde f (5 V logicos, ~8 mA)
Rl f nl 470
Dl nl 0 DLED
.ends
