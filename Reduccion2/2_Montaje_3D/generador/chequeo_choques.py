"""Chequeo independiente del 3D v3: ningun cable atraviesa una pieza ni otro cable.
Lee las rutas (pts) de los cables en el HTML y las compara con el cuerpo de cada pieza (huella y altura reales).
Uso: python chequeo_choques.py [archivo.html]"""
import io
import json
import math
import os
import sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "../Protoboards_3D_reduccion2.html")
txt = open(SRC, encoding="utf-8").read()
D, _ = json.JSONDecoder().raw_decode(txt[txt.index("const DATA = ") + 13:])
sys.argv = sys.argv[:1] + [os.devnull]
import generar_protoboard as GP   # noqa: E402
import ruteo_bajo as RB           # noqa: E402

P = 2.54
RW = .55            # radio del cable
offs = D["offs"]
solid = defaultdict(list)          # celda global -> [(ref, tope)]
for p in D["parts"]:
    top = RB.tope(p)
    cells = p.get("cells") or [(q["x"], q["y"]) for q in p["pins"]]
    for (c, r) in cells:
        solid[(offs[p["board"]] + c, r)].append((p["ref"], top))


def samples(pts):
    out = []
    for a, b in zip(pts, pts[1:]):
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        n = max(1, int(max(abs(dx) * P, abs(dz) * P, abs(dy)) / .3))
        for i in range(n + 1):
            t = i / n
            out.append((a[0] + dx * t, a[1] + dy * t, a[2] + dz * t))
    return out


choques_pieza = []
muestras = {}
for w in D["wires"]:
    pts = w.get("pts")
    if not pts:
        continue
    ms = samples(pts)
    muestras[w["i"]] = ms
    own = {(round(pts[0][0]), round(pts[0][2])), (round(pts[-1][0]), round(pts[-1][2]))}
    hit = set()
    marg = .5 + RW / P
    for (gx, h, gy) in ms:
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                c = (round(gx) + ix, round(gy) + iy)
                if c in own:
                    continue
                for ref, top in solid.get(c, ()):
                    if abs(gx - c[0]) < marg and abs(gy - c[1]) < marg and h - RW < top - .05 and h + RW > .3:
                        hit.add(ref)
    if hit:
        choques_pieza.append((w["i"], sorted(hit)))

# cable contra cable: dos muestras a menos de 2 radios
grid = defaultdict(list)
for i, ms in muestras.items():
    for (gx, h, gy) in ms:
        grid[(int(gx * P // 1.2), int(gy * P // 1.2))].append((i, gx * P, h, gy * P))
choques_cable = set()
for k, lst in grid.items():
    for ix in (-1, 0, 1):
        for iy in (-1, 0, 1):
            for (i, x, h, z) in lst:
                for (j, x2, h2, z2) in grid.get((k[0] + ix, k[1] + iy), ()):
                    if i < j and (x - x2) ** 2 + (h - h2) ** 2 + (z - z2) ** 2 < (2 * RW - .05) ** 2:
                        choques_cable.add((i, j))
print("cables con ruta:", len(muestras))
print("cables que atraviesan una pieza:", len(choques_pieza))
for i, r in choques_pieza[:25]:
    print("  cable [%d] toca %s" % (i, ", ".join(r)))
print("pares de cables que se atraviesan entre si:", len(choques_cable))
for i, j in sorted(choques_cable)[:12]:
    wi, wj = D["wires"][i - 1], D["wires"][j - 1]
    print("  cruce: [%d] %s (%s, h=%.1f) con [%d] %s (%s, h=%.1f)" % (i, wi["kind"], wi["net"], wi["h"], j, wj["kind"], wj["net"], wj["h"]))
