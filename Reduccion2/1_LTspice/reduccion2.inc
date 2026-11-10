* Reduccion 2 - generado por scripts/gen_inc.py

* IRLZ44N (nivel logico). MODELO PROPIO aproximado de la hoja de datos (NO del fabricante): Vth ~1.8 V (1 a 2 V), Rds(on) ~25 mohm a Vgs=5 V
.model IRLZ44N_P VDMOS(Rg=4 Vto=1.8 Rd=6m Rs=3m Rb=6m Kp=15 mtriode=1 Cgdmax=600p Cgdmin=60p Cgs=1.5n Cjo=300p Is=1e-12)

.subckt LOGICA_R2 v5 ein gin rin p setn m n l f fn
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
* LED de objeto (verde): se enciende cuando hay objeto (pn = 0)
Rlo v5 lo 680
Dlo lo pn DLED
.ends LOGICA_R2
