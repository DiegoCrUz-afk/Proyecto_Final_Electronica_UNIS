"""Esquematico COMPLETO de la Reduccion 2 en una sola hoja (SISTEMA_COMPLETO_R2.asc): junta las hojas BLOQUE_SENSOR_IR, BLOQUE_LOGICA,
BLOQUE_POTENCIA_R2 y BLOQUE_BUZZER (ya dibujadas y cableadas) + la fuente de 5 V, E, G, RESET, el pulsador FALLA, el fototransistor y el motor
(SUPUESTO) con un guion de eventos, para simularlo tal cual con Run en LTspice.
Usa la libreria del proyecto original (solo se LEE). Uso: py -3.13 gen_sistema_completo_r2.py"""
import os
import sys

ORIG = r"C:\Users\Diego Cruz\Documents\Proyecto_Final_Electronica_UNIS\3_archivos_tecnicos"
sys.path.insert(0, ORIG)
from asc_lib import Schematic, parse_asc, asc_to_png          # noqa: E402
import generar_esquematicos as ge                             # noqa: E402
from generar_esquematicos import titulo, nota, vr, vc, fl     # noqa: E402
import asc_route                                              # noqa: E402

DEST = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ABBR = {"SENSOR_IR": "SEN", "LOGICA": "LOG", "POTENCIA_R2": "POT", "BUZZER": "BZ"}
FILAS = [["SENSOR_IR", "LOGICA"], ["POTENCIA_R2", "BUZZER"]]
KEEP = {"0", "v5"}
MAXLEN = 1900
PWL_V5 = "PWL(0 0 1m 5)"
PWL_E = "PWL(0 0 0.05 0 0.0501 5)"                    # E: interruptor de marcha
PWL_G = "PWL(0 0 0.05 0 0.0501 5)"                    # G: cubierta cerrada
PWL_R = "PWL(0 0 1.60 0 1.6001 5 1.70 5 1.7001 0)"    # RESET (pulso)
PWL_F = "PWL(0 5 1.20 5 1.2001 0 1.25 0 1.2501 5)"    # pulsador FALLA a GND (pulso); setn queda en 5 V en reposo
PWL_IPH = "PWL(0 2u 0.4 2u 0.4001 50u 0.9 50u 0.9001 2u)"   # fototransistor: 2 uA sin objeto, 50 uA con objeto


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
        ys += [y, y + 16]
    return min(xs), min(ys), max(xs), max(ys)


def externos(s):
    ox, oy = 0, 0
    s.add("voltage", "V5", PWL_V5, ox, oy)
    fl(s, ox, oy + 16, "v5")
    fl(s, ox, oy + 96, "0")
    s.text(ox - 20, oy + 130, "Fuente de 5 V (cargador USB / power bank)", size=2)
    for k, (ref, val, nodo, txt) in enumerate([("Ve", PWL_E, "ein", "E (interruptor)"), ("Vg", PWL_G, "gin", "G (cubierta cerrada)"), ("Vr", PWL_R, "rin", "RESET")]):
        xx = ox + 200 + 144 * k
        s.add("voltage", ref, val, xx, oy)
        fl(s, xx, oy + 16, nodo)
        fl(s, xx, oy + 96, "0")
        s.text(xx - 20, oy + 130, txt, size=2)
    s.add("voltage", "Vf", PWL_F, ox + 660, oy)
    vr(s, "Rf", "100", ox + 760, oy)
    fl(s, ox + 660, oy + 16, "vfal")
    fl(s, ox + 760, oy, "vfal")
    fl(s, ox + 760, oy + 80, "setn")
    fl(s, ox + 660, oy + 96, "0")
    s.text(ox + 640, oy + 130, "Pulsador FALLA (lleva setn a GND)", size=2)
    sx, sy = ox + 1000, oy
    s.add("current", "Iph", PWL_IPH, sx, sy)
    fl(s, sx, sy, "v5")
    fl(s, sx, sy + 80, "b")
    s.text(sx - 20, sy + 120, "fototransistor: 2 uA sin objeto, 50 uA con objeto (0.4 a 0.9 s)", size=2)
    mx, my = ox + 1500, oy
    s.add("ind", "Lm", "3m", mx - 16, my)
    fl(s, mx, my + 16, "v5")
    vr(s, "Rm", "12", mx, my + 96)
    fl(s, mx, my + 176, "dm")
    s.text(mx - 20, my + 215, "Motor (SUPUESTO): 12 ohm en serie con 3 mH, entre v5 y dm. El N20 real se mide aparte.", size=2)


def main():
    out = Schematic(9000, 6000)
    GAP = 240
    y = 0
    params = set()
    for fila in FILAS:
        x = 0
        hmax = 0
        for blk in fila:
            sch = parse_asc(os.path.join(DEST, "BLOQUE_%s.asc" % blk))
            AB = ABBR[blk]
            ab = AB.lower()
            x0, y0, x1, y1 = bbox(sch)
            dx = (x - x0) // 16 * 16
            dy = (y - y0) // 16 * 16
            ports = {(a, b) for a, b, _ in sch.iopins}
            portnames = {nm for (fx_, fy_, nm) in sch.flags if (fx_, fy_) in ports}
            for (a, b, c, d) in sch.wires:
                out.wires.append((a + dx, b + dy, c + dx, d + dy))
            for (fx, fy, name) in sch.flags:
                nn = name if (name in KEEP or (fx, fy) in ports or name in portnames) else ab + "_" + name
                out.flags.append((fx + dx, fy + dy, nn))
            for c in sch.comps:
                ref = c.ref
                if ref and ref[0] in "RCDLQMXBVIE":
                    ref = ref + "_" + AB
                out.add(c.s.name, ref, c.value, c.x + dx, c.y + dy, c.rot)
            for (tx, ty, al, sz, txt) in sch.texts:
                if txt.startswith("!"):
                    params.add(txt)
                    continue
                out.texts.append((tx + dx, ty + dy, al, sz, txt))
            x += (x1 - x0) + GAP
            hmax = max(hmax, y1 - y0)
        y += hmax + 280
    ex, ey = 0, (y + 60) // 16 * 16
    titulo(out, ex, ey - 120, "FUENTE, ENTRADAS DE PRUEBA Y MOTOR (para simular)",
           ["La fuente de 5 V, los eventos (E, G, objeto, FALLA, RESET) y el motor supuesto estan aqui; los bloques se unen a ellos por el nombre de la etiqueta."])
    aux = Schematic(2400, 1500)
    externos(aux)
    for (a, b, c, d) in aux.wires:
        out.wires.append((a + ex, b + ey, c + ex, d + ey))
    for (fx, fy, nm) in aux.flags:
        out.flags.append((fx + ex, fy + ey, nm))
    for c in aux.comps:
        out.add(c.s.name, c.ref, c.value, c.x + ex, c.y + ey, c.rot)
    for (tx, ty, al, sz, txt) in aux.texts:
        out.texts.append((tx + ex, ty + ey, al, sz, txt))
    out.text(0, -120, "SISTEMA COMPLETO - REDUCCION 2 (5 V): sensor IR, logica, potencia con motor, alarma luminosa y acustica (esquematico completo, se simula con Run)", size=4)
    ps = [p[1:] for p in sorted(params)] + [".include modelos.inc", ".include sistema.inc", ".include reduccion2.inc", ".tran 0 2 0 20u",
          ".save V(v5) V(p) V(setn) V(m) V(n) V(l) V(f) V(fn) V(dm) V(bz_bzc) V(bz_bzb)",
          ".meas tran m_sin_objeto find V(m) at=0.3", ".meas tran n_sin_objeto find V(n) at=0.3", ".meas tran n_con_objeto find V(n) at=0.7", ".meas tran l_con_objeto find V(l) at=0.7",
          ".meas tran f_falla find V(f) at=1.4", ".meas tran m_falla find V(m) at=1.4", ".meas tran bzc_falla find V(bz_bzc) at=1.4",
          ".meas tran f_tras_reset find V(f) at=1.9", ".meas tran m_tras_reset find V(m) at=1.9", ".meas tran bzc_sin_falla find V(bz_bzc) at=0.3"]
    out.text(0, ey + 400, "\\n".join(ps), size=2, directive=True)
    unidas, fallidas = asc_route.autoroute(out, max_len=MAXLEN)
    if fallidas:
        u2, fallidas = asc_route.autoroute(out, margin=0, max_len=MAXLEN)
        unidas += u2
    print("redes entre bloques unidas con cable:", unidas, "sin ruta (quedan con etiqueta):", fallidas)
    path = os.path.join(DEST, "SISTEMA_COMPLETO_R2.asc")
    out.w, out.h = 9000, int(ey + 700)
    out.save(path)
    print("creado", path)
    asc_to_png(path, os.path.join(DEST, "capturas", "SISTEMA_COMPLETO_R2_esquematico.png"))
    print("png listo")


if __name__ == "__main__":
    main()
