"""Genera el esquematico jerarquico del sistema completo (2_LTspice\\SISTEMA_COMPLETO.asc) y los simbolos de bloque.
Cada bloque es un simbolo (BLOQUE_*.asy) que apunta a su hoja BLOQUE_*.asc; los bloques se unen con etiquetas de nodo.
La hoja principal tambien lleva la fuente, las entradas, los sensores simulados y el motor, asi que se simula tal cual
(LTspice arma los subcircuitos de las hojas al generar el netlist). Es el mismo guion de eventos de sim\\sistema_completo.cir.
Uso: python generar_sistema.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asc_lib import Schematic
import crear_simbolos
from generar_esquematicos import vr, vc, hd, fl, titulo, nota, DEST

# nombre, titulo del simbolo, pines a la izquierda, pines a la derecha, columna, fila
BLOQUES = [
    ("BLOQUE_REG5V", "1 REGULADOR 5 V", ["vm"], ["v5"], 0, 0),
    ("BLOQUE_SENSOR_IR", "2 SENSOR IR", ["v5", "b"], ["tin", "p"], 0, 1),
    ("BLOQUE_SOBRECORRIENTE", "3 SOBRECORRIENTE", ["vm", "v5", "sh"], ["setn"], 0, 2),
    ("BLOQUE_TEMPERATURA", "4 TEMPERATURA", ["v5", "tnode"], ["setn"], 0, 3),
    ("BLOQUE_LOGICA", "5 LOGICA", ["v5", "ein", "gin", "rin", "p", "setn"], ["m", "n", "l", "f", "fn"], 1, 0),
    ("BLOQUE_ALARMA", "11 ALARMA", ["vm", "f"], [], 1, 1),
    ("BLOQUE_REFVEL", "9 REF. VELOCIDAD", ["v5", "l"], ["vref"], 1, 2),
    ("BLOQUE_ENCODER_FV", "8 ENCODER F-V", ["v5", "enc"], ["vspd"], 1, 3),
    ("BLOQUE_ERROR_AMP", "10 AMP. DE ERROR", ["vm", "v5", "vref", "vspd"], ["vctrl"], 2, 0),
    ("BLOQUE_PWM_GEN", "6 GENERADOR PWM", ["v5", "vctrl"], ["pwm"], 2, 1),
    ("BLOQUE_POTENCIA", "7 POTENCIA", ["v5", "vm", "pwm", "m"], ["dm", "sh"], 2, 2),
]
ANCHO = 200
COL_X = [0, 620, 1240]
FILA_Y = [0, 260, 520, 700]

# guion de eventos (identico a sim\sistema_completo.cir)
PWL_V12 = "PWL(0 0 10m 12)"
PWL_E = "PWL(0 0 0.05 0 0.0501 5)"
PWL_G = "PWL(0 0 0.05 0 0.0501 5 1.40 5 1.4001 0 1.60 0 1.6001 5)"
PWL_R = "PWL(0 0 2.60 0 2.6001 5 2.75 5 2.7501 0 3.55 0 3.5501 5 3.70 5 3.7001 0 4.20 0 4.2001 5 4.35 5 4.3501 0)"
PWL_IPH = "PWL(0 2u 0.6 2u 0.6001 50u 1.1 50u 1.1001 2u)"
PWL_TC = "PWL(0 25 3.0 25 3.5 60 3.8 25)"
PWL_TL = "PWL(0 0.004 1.9 0.004 1.9001 0.03 2.3 0.03 2.3001 0.004)"


def dibujar_externos(s):
    """Fuente de 12 V, entradas con su guion de eventos, sensores simulados y motor (para simular)."""
    # ---- alimentacion: fuente 12 V (se conecta en t=0), diodo contra polaridad inversa y condensador de entrada
    ox, oy = -896, 0
    s.add("voltage", "V12", PWL_V12, ox, oy)
    fl(s, ox, oy + 16, "vin")
    fl(s, ox, oy + 96, "0")
    hd(s, "D1", "D1N4007", ox + 80, oy + 16)
    fl(s, ox + 80, oy + 16, "vin")
    fl(s, ox + 144, oy + 16, "vm")
    vc(s, "Cin", "1000u", ox + 264, oy + 16, pol=True)
    fl(s, ox + 264, oy + 16, "vm")
    fl(s, ox + 264, oy + 80, "0")
    nota(s, ox - 20, oy + 130, ["Entrada: fuente externa de 12 V.", "D1 protege contra polaridad inversa."])

    # ---- entradas del usuario: E (interruptor), G (cubierta cerrada), reset
    ex, ey = -896, 256
    for k, (ref, val, nodo) in enumerate([("Ve", PWL_E, "ein"), ("Vg", PWL_G, "gin"), ("Vr", PWL_R, "rin")]):
        xx = ex + 144 * k
        s.add("voltage", ref, val, xx, ey)
        fl(s, xx, ey + 16, nodo)
        fl(s, xx, ey + 96, "0")
    nota(s, ex - 20, ey + 130, ["E, G (cubierta) y boton de reset con su guion de eventos."])

    # ---- sensores simulados
    sx, sy = -896, 520
    s.add("current", "Iph", PWL_IPH, sx, sy)
    fl(s, sx, sy, "v5")
    fl(s, sx, sy + 80, "b")
    s.text(sx - 20, sy + 120, "fototransistor: 2 uA sin objeto, 50 uA con objeto (0.6 a 1.1 s)", size=2)
    s.add("voltage", "Vtc", PWL_TC, sx + 120, sy + 224)
    fl(s, sx + 120, sy + 240, "tc")
    fl(s, sx + 120, sy + 320, "0")
    s.add("bi", "Bn", "I=V(v5,tnode)/(10k*exp(3950*(1/(V(tc)+273.15)-1/298.15)))", sx + 360, sy)
    fl(s, sx + 360, sy, "v5")
    fl(s, sx + 360, sy + 80, "tnode")
    s.text(sx + 120, sy + 360, "NTC 10 k (B 3950): temperatura 25 C -> 60 C entre 3.0 y 3.5 s", size=2)
    s.add("bv", "Bsl", "V=0.3+4.4*u(sin(2*pi*V(ph)))", sx + 600, sy)
    fl(s, sx + 600, sy + 16, "encs")
    fl(s, sx + 600, sy + 96, "0")
    vr(s, "Renc", "1k", sx + 720, sy)
    fl(s, sx + 720, sy, "encs")
    fl(s, sx + 720, sy + 80, "enc")
    s.text(sx + 560, sy + 140, "encoder de 20 ranuras", size=2)

    # ---- motor (modelo supuesto): Lm, Rm, fuerza contraelectromotriz, inercia y carga
    mx, my = 1696, 520
    s.add("ind", "Lm", "3m", mx - 16, my)
    fl(s, mx, my + 16, "vm")
    vr(s, "Rm", "12", mx, my + 96)
    fl(s, mx, my + 176, "n2")
    s.add("bv", "Eb", "V=Ke*V(w)", mx + 160, my)
    fl(s, mx + 160, my + 16, "n2")
    fl(s, mx + 160, my + 96, "dm")
    s.text(mx - 20, my + 215, "motor DC 12 V (modelo supuesto): Ra 12, La 3 mH, Ke = Kt = 0.035", size=2)
    vc(s, "Cw", "{J} ic=0", mx + 360, my + 16)
    fl(s, mx + 360, my + 16, "w")
    fl(s, mx + 360, my + 80, "0")
    s.add("bi", "Bw", "I=Ke*I(Lm)-Bfr*V(w)-V(tl)*tanh(V(w))", mx + 480, my)
    fl(s, mx + 480, my, "0")
    fl(s, mx + 480, my + 80, "w")
    s.add("voltage", "Vtl", PWL_TL, mx + 640, my)
    fl(s, mx + 640, my + 16, "tl")
    fl(s, mx + 640, my + 96, "0")
    vc(s, "Cph", "1 ic=0", mx + 800, my + 16)
    fl(s, mx + 800, my + 16, "ph")
    fl(s, mx + 800, my + 80, "0")
    s.add("bi", "Bph", "I=20*V(w)/(2*pi)", mx + 920, my)
    fl(s, mx + 920, my, "0")
    fl(s, mx + 920, my + 80, "ph")
    s.text(mx + 300, my + 140, "w = velocidad (rad/s) como voltaje; ph = fase del disco del encoder", size=2)



def main():
    s = Schematic(2400, 1500)
    titulo(s, -900, -200, "SISTEMA COMPLETO - MINIESTACION INDUSTRIAL AUTOMATIZADA",
           ["Cada recuadro es una hoja (BLOQUE_*.asc). Los bloques se conectan por nombre de nodo: v5 = 5 V, vm = 12 V despues del diodo, 0 = tierra.",
            "Entradas del usuario: ein (E), gin (G, cubierta cerrada = 5 V), rin (reset); sensores: b (fototransistor), enc (encoder), tnode (NTC).",
            "Se simula tal cual: la fuente, los eventos (objeto, cubierta, carga extra, calor, reset) y el motor estan en esta hoja."])
    for nombre, tit, izq, der, col, fila in BLOQUES:
        crear_simbolos.bloque(nombre, tit, izq, der, ancho=ANCHO)
        x, y = COL_X[col], FILA_Y[fila]
        c = s.add(nombre, "X" + nombre.split("_", 1)[1].replace("_", "")[:6], None, x, y)
        m = {i + 1: n for i, n in enumerate(izq + der)}
        s.net(c, m, stub=40)

    dibujar_externos(s)

    # ---- directivas de simulacion
    s.text(-900, 1000, ".include ..\\3_archivos_tecnicos\\modelos.inc\\n.include ..\\3_archivos_tecnicos\\sistema.inc\\n"
                       ".lib NE555.sub\\n.param Ke=0.035 J=1e-5 Bfr=7.2e-6\\n.tran 0 4.6 0 4u startup\\n"
                       ".save V(v5) V(vm) V(p) V(setn) V(m) V(n) V(l) V(f) V(fn) V(vref) V(vspd) V(vctrl) V(pwm) V(dm) V(sh) V(tnode) V(tc) V(w) I(Lm) I(D1)",
           size=2, directive=True)
    path = os.path.join(DEST, "SISTEMA_JERARQUICO.asc")
    s.save(path)
    print("creado", path)


if __name__ == "__main__":
    main()
