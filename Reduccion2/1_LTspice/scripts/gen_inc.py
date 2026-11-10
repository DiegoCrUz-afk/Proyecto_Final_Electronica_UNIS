# Crea reduccion2.inc: LOGICA_R2 = LOGICA del original + LED de objeto (680 ohm, de v5 a pn), copiada por codigo de sistema.inc
import re, os
d=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src=open(os.path.join(d,"sistema.inc"),encoding="utf-8").read()
m=re.search(r"\.subckt LOGICA .*?\.ends",src,re.S).group(0)
m=m.replace(".subckt LOGICA ",".subckt LOGICA_R2 ").replace(".ends","* LED de objeto (verde): se enciende cuando hay objeto (pn = 0)\nRlo v5 lo 680\nDlo lo pn DLED\n.ends LOGICA_R2")
extra="""
* IRLZ44N (nivel logico). MODELO PROPIO aproximado de la hoja de datos (NO del fabricante): Vth ~1.8 V (1 a 2 V), Rds(on) ~25 mohm a Vgs=5 V
.model IRLZ44N_P VDMOS(Rg=4 Vto=1.8 Rd=6m Rs=3m Rb=6m Kp=15 mtriode=1 Cgdmax=600p Cgdmin=60p Cgs=1.5n Cjo=300p Is=1e-12)
"""
open(os.path.join(d,"reduccion2.inc"),"w",encoding="utf-8").write("* Reduccion 2 - generado por scripts/gen_inc.py\n"+extra+"\n"+m+"\n")
print("ok")
