"""Agrega el bloque 7 (buzzer de falla) a la placa A del 3D YA verificado, SIN mover ninguna pieza ni cable existente.
Parte de ../respaldo_antes_buzzer/generador/datos_r2.json (el 3D de antes del buzzer), le suma 4 piezas y 5 cables en las filas libres 4-22 de la placa A,
y escribe datos_r2.json y ../Protoboards_3D_reduccion2.html. NO usar exportar_r2.py despues de esto (reacomodaria todo). Uso: py -3.13 agregar_buzzer.py"""
import json
import os
import copy

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(AQUI, "..", "respaldo_antes_buzzer", "generador", "datos_r2.json")
LET = {0: "J", 1: "I", 2: "H", 3: "G", 4: "F", 6: "E", 7: "D", 8: "C", 9: "B", 10: "A"}
D = json.load(open(BASE, encoding="utf-8"))
import pruebas_r2 as PR            # noqa: E402
import pruebas_buzzer              # noqa: E402,F401  (agrega las pruebas del buzzer a PR.M)


def hole(x, y):
    if x in LET:
        return "A-%s%d" % (LET[x], 62 - y)
    return "A-riel %s %s fila %d" % ("+5 V" if x in (-3, 12) else "GND", "izq" if x < 5 else "der", 62 - y)


def pin(n, net, x, y):
    return dict(n=n, net=net, x=x, y=y)


def cells(cols, y0, y1):
    return [[c, r] for r in range(y0, y1 + 1) for c in cols]


NEW = [
    dict(ref="BZ.Rb", blk="BUZZER", kind="R", val="4.7k", board="A", x=9, y=40, w=5, h=1, short="Rbz",
         pins=[pin("1", "BZ.b", 9, 40), pin("2", "f", 9, 44)], cells=cells([9], 40, 45)),
    dict(ref="BZ.Q", blk="BUZZER", kind="Q92", val="2N3904", board="A", x=7, y=39, w=3, h=1, short="Qz",
         pins=[pin("E", "0", 7, 39), pin("B", "BZ.b", 7, 40), pin("C", "BZ.c", 7, 41)], cells=cells([6, 7], 39, 41)),
    dict(ref="BZ.D", blk="BUZZER", kind="D", val="1N4148", board="A", x=8, y=41, w=5, h=1, short="Dz",
         pins=[pin("A", "BZ.c", 8, 41), pin("K", "v5", 8, 45)], cells=cells([8], 41, 46)),
    dict(ref="BZ.Z", blk="BUZZER", kind="BUZZER", val="Buzzer activo (12 V, se usa a 5 V)", board="A", x=10, y=58, w=4, h=1, short="Buzzer",
         pins=[pin("-", "BZ.c", 10, 58), pin("+", "v5", 10, 61)], cells=cells([8, 9, 10], 57, 61)),
]
# cables: (red, (x1,y1), (x2,y2), altura, vertices intermedios [(x, y)]). Ningun extremo cae sobre la ruta de un cable ya armado (filas y 47, 52, 55 y 56).
COL = "#ffb3d9"
CAB = [("f", (10, 44), (10, 31), 3.9, [(11, 44), (11, 31)]),
       ("0", (10, 39), (13, 40), 2.6, [(12, 39), (12, 40)]),
       ("v5", (10, 45), (12, 45), 3.9, []),
       ("BZ.c", (10, 41), (7, 58), 9.1, [(10, 50), (7, 50)]),
       ("v5", (6, 61), (6, 45), 5.2, [])]
n0 = len(D["wires"])
W = []
for k, (net, a, b, h, via) in enumerate(CAB):
    xs = [a] + via + [b]
    pts = [[a[0], -2.5, a[1]]] + [[x, h, y] for (x, y) in xs] + [[b[0], -2.5, b[1]]]
    color = "#1a1a1a" if net == "0" else "#e53935" if net == "v5" else COL
    W.append(dict(i=n0 + 1 + k, net=net, color=color, kind="signal", blk="BUZZER", h=h, pts=pts,
                  a=dict(board="A", x=a[0], y=a[1], hole=hole(*a)), b=dict(board="A", x=b[0], y=b[1], hole=hole(*b))))

# ---- sumar al modelo (nada de lo existente cambia) ----
D["parts"] += NEW
D["wires"] += W
D["nets"]["BZ.b"] = dict(color="#ff9800", label="BZ.b")
D["nets"]["BZ.c"] = dict(color="#8bc34a", label="BZ.c")
refs = [p["ref"] for p in NEW]
TIT = "7 Buzzer de falla (alarma acústica)"
D["blocks"]["BUZZER"] = dict(title=TIT, boards=["A"], refs=refs)
D["zones"].append(dict(id="BUZZER", title=TIT, board="A", x=0, y=39, w=11, h=22))
D["meas"] = PR.M
D["med"]["BUZZER"] = [x["id"] for x in PR.M if x["blk"] == "BUZZER"]
D["tests"] = dict(D["med"])

tpl = open(os.path.join(AQUI, "plantilla_r2.html"), encoding="utf-8").read()
three = open(os.path.join(AQUI, "lib3d", "three.min.js"), encoding="utf-8").read()
orbit = open(os.path.join(AQUI, "lib3d", "OrbitControls.js"), encoding="utf-8").read()
html = tpl.replace("/*__THREE__*/", three).replace("/*__ORBIT__*/", orbit).replace("/*__DATA__*/", "const DATA = " + json.dumps(D, ensure_ascii=False) + ";")
open(os.path.join(AQUI, "..", "Protoboards_3D_reduccion2.html"), "w", encoding="utf-8").write(html)
json.dump(D, open(os.path.join(AQUI, "datos_r2.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("ok:", len(D["parts"]), "piezas,", len(D["wires"]), "cables")
