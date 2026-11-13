* Modelos usados en el proyecto (LTspice). Los marcados "propio" son aproximaciones, NO modelos del fabricante.
.param B3904=200
.model Q2N3904 NPN(IS=1E-14 VAF=100 Bf={B3904} IKF=0.4 XTB=1.5 BR=4 CJC=4E-12 CJE=8E-12 RB=20 RC=0.1 RE=0.1 TR=250E-9 TF=350E-12 ITF=1 VTF=2 XTF=3 Vceo=40 Icrating=200m)
.model Q2N3906 PNP(IS=1E-14 VAF=100 Bf=180 IKF=0.1 XTB=1.5 BR=4 CJC=4.5E-12 CJE=10E-12 RB=20 RC=0.1 RE=0.1 TR=250E-9 TF=350E-12 ITF=1 VTF=2 XTF=3 Vceo=40 Icrating=200m)
.model QBD139 NPN(IS=1E-13 BF=100 NF=1 ISE=1E-13 NE=1.5 IKF=0.8 VAF=100 BR=10 RB=5 RE=0.1 RC=0.2 CJE=100p CJC=30p TF=1n Vceo=80 Icrating=1.5)
.model D1N4148 D(Is=2.52n Rs=.568 N=1.752 Cjo=4p M=.4 tt=20n)
.model D1N4007 D(Is=90p Rs=40m Cjo=30p N=1.4 TT=5u)
.model D1N5819 D(Is=31.7u Rs=.051 N=1.373 Cjo=110p M=.35 Eg=.69 Xti=2)
.model D1N4734 D(Is=1f Rs=2 Cjo=100p Bv=5.6 Ibv=10m Nbv=2)
.model DIR D(Is=1e-14 N=1.8 Rs=2 Cjo=20p)
.model DLED D(Is=1e-18 N=1.9 Rs=3 Cjo=20p)
* IRFZ44N_P (propio, calibrado con la hoja de datos): Rds(on) ~0.02 ohm a Vgs=10 V, ~0.07 ohm a 4.4 V; Vth tipico 3 V (2 a 4 V segun el lote); Qg ~ 42 nC
.model IRFZ44N_P VDMOS(Rg=4 Vto=3 Rd=6m Rs=3m Rb=6m Kp=12 mtriode=1 Cgdmax=600p Cgdmin=60p Cgs=1.5n Cjo=300p Is=1e-12)
* Comparador tipo LM393 (propio, simplificado): salida de colector abierto, Ron 60 ohm, Vos 0
.model SWCMP SW(Ron=60 Roff=100Meg Vt=0 Vh=1m)
.subckt LM393 inp inm vcc vee out
Rip inp vee 100Meg
Rim inm vee 100Meg
S1 out vee inm inp SWCMP
.ends LM393
* Amplificador operacional tipo LM358 (propio, simplificado): Avol 100k, polo dominante a 10 Hz (GBW 1 MHz),
* salida de 20 mV sobre tierra hasta 1.5 V bajo Vcc, impedancia de salida 60 ohm. Sin offset, sin corrientes de entrada.
.subckt LM358 inp inm vcc vee out
Rin inp inm 2Meg
E1 n1 0 value={limit(100k*V(inp,inm),-30,30)}
Rp n1 n2 1k
Cp n2 0 15.9u
B2 oi 0 V=limit(V(n2),V(vee)+0.02,V(vcc)-1.5)
Ro oi out 60
.ends LM358
