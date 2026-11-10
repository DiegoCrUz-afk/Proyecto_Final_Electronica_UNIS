# Genera los esquematicos .asc de la Reduccion 2 con la misma libreria del proyecto original (solo se LEE de la original).
# Sensor IR = igual al original; Logica = original + LED de objeto; Potencia = nueva (IRLZ44N + Rs + puente 2N3904).
import os, sys
ORIG=r"C:\Users\Diego Cruz\Documents\Proyecto_Final_Electronica_UNIS\3_archivos_tecnicos"
sys.path.insert(0, ORIG)
import generar_esquematicos as ge
from asc_lib import Schematic, asc_to_png
AQUI=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ge.DEST=AQUI
orig_guardar=ge.guardar
def guardar(s, nombre):
    if nombre=="BLOQUE_LOGICA":
        ge.vr(s,"Rlo","680",1000,520); ge.fl(s,1000,520,"v5")
        ge.vd(s,"Dlo","DLED",1000,600,sym="LED"); ge.fl(s,1000,664,"pn")
        ge.vr(s,"Rl","470",1400,520); ge.fl(s,1400,520,"f")
        ge.vd(s,"Dl","DLED",1400,600,sym="LED"); ge.fl(s,1400,664,"0")
        s.text(1430,590,"LED rojo de falla (A = F): 470 ohm, ~6 mA",size=2)
        s.text(1030,590,"LED de objeto (verde): enciende cuando pn = 0 (hay objeto), 4.4 mA",size=2)
        s.texts[:]=[t for t in s.texts if not (t[1] < 0 and t[0] < 0)]
        s.text(-80,-170,"REDUCCION 2 - LOGICA",size=3); s.text(-80,-130,"Reduccion 2: igual al original + LED de objeto (Rlo, Dlo). A = F se usa solo como LED rojo (ver bloque de potencia/placa A).",size=2)
    return orig_guardar(s,nombre)
ge.guardar=guardar
ge.b_sensor(); ge.b_logica()
def b_potencia_r2():
    s=Schematic(1500,600)
    ge.titulo(s,-80,-190,"REDUCCION 2 - POTENCIA (5 V)",["m (permiso) abre el IRLZ44N. El motor lleva SIEMPRE Rs en serie; con n = 1 el 2N3904 (Qp) puentea a Rs y el motor corre normal.",
        "Con objeto n = 0: Qp se abre y el motor queda con Rs en serie (mas lento). Rs se ajusta por prueba (40 a 60 %). PROPUESTA NO VERIFICADA con el motor real."])
    s.wire((640,96),(560,96)); ge.fl(s,560,96,"m*")
    ge.vr(s,"Rpd","10k",600,96); ge.fl(s,600,176,"0")
    s.add("nmos","M1","IRLZ44N_P",640,16)       # D (688,16) G (640,96) S (688,112)
    ge.fl(s,688,112,"0")
    s.wire((688,16),(800,16),(1064,16))
    ge.fl(s,744,16,"ds")
    ge.vr(s,"Rs","15",800,-64)                    # dm (800,-64) -> ds (800,16); 15 ohm segun simulacion con motor supuesto
    ge.fl(s,800,-64,"dm*")
    ge.vd_up(s,"Dfw","D1N5819",900,-64,sym="diode"); ge.fl(s,900,-128,"v5*")
    s.wire((800,-64),(900,-64),(1064,-64),(1064,-48))
    ge.npn(s,"Qp","Q2N3904",1000,-48)             # C (1064,-48) B (1000,0) E (1064,48)
    s.wire((1064,48),(1064,16))
    s.wire((980,0),(1000,0)); ge.hr(s,"Rb","1k",900,0); ge.fl(s,900,0,"n*")
    ge.vc(s,"Cb","100u",1200,-64,pol=True); ge.fl(s,1200,-64,"v5"); ge.fl(s,1200,0,"0")
    ge.vc(s,"Cin","1000u",1360,-64,pol=True); ge.fl(s,1360,-64,"v5"); ge.fl(s,1360,0,"0")
    s.text(1330,-90,"Cin (entrada de 5 V)",size=2)
    ge.vc(s,"C2","100n",1280,-64); ge.fl(s,1280,-64,"v5"); ge.fl(s,1280,0,"0")
    ge.nota(s,-80,300,["El motor va entre v5 (M+) y dm (M-). Los condensadores Cb y C2 van cerca del motor.",
        "Rs = 15 ohm sale de la simulacion con un motor SUPUESTO (12 ohm, 3 mH): 10 ohm daba 66 %, 15 ohm da 50 %. Con el motor real hay que reajustar.",
        "IRLZ44N = MOSFET de nivel logico (modelo propio aproximado). Arranque: ~390 mA pico > 200 mA del 2N3904 (ver informe de simulacion)."])
    return orig_guardar(s,"BLOQUE_POTENCIA_R2")
b_potencia_r2()
for n in ("BLOQUE_SENSOR_IR","BLOQUE_LOGICA","BLOQUE_POTENCIA_R2"):
    try: asc_to_png(os.path.join(AQUI,n+".asc"), os.path.join(AQUI,"capturas","esq_"+n+".png"))
    except Exception as e: print("png",n,e)
print("ok")
