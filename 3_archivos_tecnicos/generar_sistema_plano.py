"""Esquematico COMPLETO en una sola hoja (como el del amplificador): todos los bloques con sus cables, en orden de
lectura, mas la fuente, los sensores simulados y el motor, de modo que se simula tal cual (Run) en LTspice.

Toma las hojas BLOQUE_*.asc (ya cableadas por generar_esquematicos.py) y las junta en una hoja:
 - los nombres de las piezas llevan el sufijo del bloque (Ra_SEN, Q2_SEN...) para que no se repitan;
 - los nombres de nodos internos llevan el prefijo del bloque (sen_th...); los pines de bloque (v5, vm, p, setn...) y la
   tierra se dejan con su nombre, asi los bloques se unen por nombre en las etiquetas azules entre una etapa y otra.
Uso: python generar_sistema_plano.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asc_lib import Schematic, parse_asc
from generar_esquematicos import DEST, titulo, nota, vr, vc, hd, fl
import generar_sistema as gs
import asc_route

ABBR = {"REG5V": "REG", "SENSOR_IR": "SEN", "SOBRECORRIENTE": "OC", "TEMPERATURA": "TMP", "LOGICA": "LOG", "ALARMA": "ALA", "REFVEL": "REF", "ENCODER_FV": "ENC",
        "ERROR_AMP": "ERR", "PWM_GEN": "PWM", "POTENCIA": "POT"}
# orden de lectura: (fila, bloques)
FILAS = [["REG5V", "SENSOR_IR", "SOBRECORRIENTE"], ["TEMPERATURA", "LOGICA"], ["REFVEL", "ENCODER_FV", "ERROR_AMP"], ["PWM_GEN", "POTENCIA", "ALARMA"]]
KEEP = {"0", "v5", "vm", "vin"}
MAXLEN = 1900               # una red entre bloques se une con cable solo si cabe en esta distancia (si no, etiqueta)


def bbox(sch):
    xs, ys = [], []
    for (x1, y1, x2, y2) in sch.wires:
        xs += [x1, x2]
        ys += [y1, y2]
    for (x, y, _) in sch.flags:
        xs.append(x)
        ys.append(y)
    for c in sch.comps:
        xs += [c.x - 40, c.x + 120]
        ys += [c.y - 40, c.y + 120]
    for (x, y, al, sz, txt) in sch.texts:
        xs += [x, x + 7 * max(len(l) for l in txt[1:].split("\\n"))]
        ys.append(y)
        ys.append(y + 16)
    return min(xs), min(ys), max(xs), max(ys)


def pref(ref, ab):
    return ref + "_" + ab


def main():
    out = Schematic(9000, 6000)
    ox0, oy = 0, 0
    GAP = 240
    placed = {}
    y = 0
    params = set()
    for fila in FILAS:
        x = 0
        hmax = 0
        for blk in fila:
            sch = parse_asc(os.path.join(DEST, "BLOQUE_%s.asc" % blk))
            ab = ABBR[blk].lower()
            AB = ABBR[blk]
            x0, y0, x1, y1 = bbox(sch)
            dx = (x - x0) // 16 * 16
            dy = (y - y0) // 16 * 16
            ports = {(a, b) for a, b, _ in sch.iopins}
            portnames = {nm for (fx_, fy_, nm) in sch.flags if (fx_, fy_) in ports}
            for (a, b, c, d) in sch.wires:
                out.wires.append((a + dx, b + dy, c + dx, d + dy))
            for (fx, fy, name) in sch.flags:
                if name in KEEP or name == "0" or (fx, fy) in ports or name in portnames:
                    nn = name
                else:
                    nn = ab + "_" + name
                out.flags.append((fx + dx, fy + dy, nn))
            for c in sch.comps:
                ref = c.ref
                if ref and ref[0] in "RCDLQMXBVIE":
                    ref = pref(ref, AB)
                c2 = out.add(c.s.name, ref, c.value, c.x + dx, c.y + dy, c.rot)
            for (tx, ty, al, sz, txt) in sch.texts:
                if txt.startswith("!"):
                    params.add(txt)
                    continue
                out.texts.append((tx + dx, ty + dy, al, sz, txt))
            placed[blk] = (x + 0, y)
            x += (x1 - x0) + GAP
            hmax = max(hmax, y1 - y0)
        y += hmax + 280
    # ---- entradas, sensores simulados y motor (a la derecha de la ultima fila)
    ex, ey = 0, (y + 60) // 16 * 16
    titulo(out, ex, ey - 120, "ENTRADAS DE PRUEBA, FUENTE Y MOTOR (para simular)", ["La fuente de 12 V, los eventos (objeto, cubierta, carga extra, calor, reset) y el motor estan aqui; los bloques se unen a ellos por el nombre de la etiqueta azul."])
    # reutilizar la parte de gs.main() que dibuja estas piezas: se replica con un esquema auxiliar
    aux = Schematic(2400, 1500)
    gs.dibujar_externos(aux)
    for (a, b, c, d) in aux.wires:
        out.wires.append((a + ex + 1000, b + ey, c + ex + 1000, d + ey))
    for (fx, fy, nm) in aux.flags:
        out.flags.append((fx + ex + 1000, fy + ey, nm))
    for c in aux.comps:
        out.add(c.s.name, c.ref, c.value, c.x + ex + 1000, c.y + ey, c.rot)
    for (tx, ty, al, sz, txt) in aux.texts:
        if txt.startswith("!"):
            params.add(txt)
        else:
            out.texts.append((tx + ex + 1000, ty + ey, al, sz, txt))
    out.text(0, 20 - 120, "SISTEMA COMPLETO - MINIESTACION INDUSTRIAL AUTOMATIZADA (esquematico completo, se simula con Run)", size=4)
    ps = [p[1:] for p in sorted(params)]
    ps += [".include ..\\3_archivos_tecnicos\\modelos.inc", ".include ..\\3_archivos_tecnicos\\sistema.inc", ".lib NE555.sub", ".param Ke=0.035 J=1e-5 Bfr=7.2e-6",
           ".tran 0 4.6 0 4u startup",
           ".save V(v5) V(vm) V(p) V(setn) V(m) V(n) V(l) V(f) V(fn) V(vref) V(vspd) V(vctrl) V(pwm) V(dm) V(sh) V(tnode) V(tc) V(w) I(Lm) I(D1)"]
    out.text(0, ey + 900, "\\n".join(ps), size=2, directive=True)
    unidas, fallidas = asc_route.autoroute(out, max_len=MAXLEN)
    if fallidas:
        u2, fallidas = asc_route.autoroute(out, margin=0, max_len=MAXLEN)
        unidas += u2
    print("redes entre bloques unidas con cable:", unidas, "sin ruta (quedan con etiqueta):", fallidas)
    path = os.path.join(DEST, "SISTEMA_COMPLETO.asc")
    out.w, out.h = 9000, int(ey + 1300)
    out.save(path)
    print("creado", path)


if __name__ == "__main__":
    main()
