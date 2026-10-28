"""HTML 3D de los protoboards (guia de armado). Uso: python exportar_protoboard3d.py"""
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(AQUI, "..", "pcb")
sys.path.insert(0, os.path.join(AQUI, "..", "montaje3d"))
sys.argv = sys.argv[:1] + [os.devnull]
import generar_protoboard as P          # noqa: E402
import exportar_montaje3d as E          # noqa: E402

OUT = os.path.join(AQUI, "..", "..", "6_Montaje_3D", "Protoboards_3D_miniestacion.html")
BL = [b.name for b in P.boards]
offs = {b: i * 22 for i, b in enumerate(BL)}
dims = {b: dict(x0=offs[b] - 4.5, x1=offs[b] + 14.5, z1=64) for b in BL}
LET = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 6: "F", 7: "G", 8: "H", 9: "I", 10: "J"}


def hole(b, x, y):
    if x in LET:
        return "%s-%s%d" % (b, LET[x], y + 1)
    return "%s-riel %s fila %d" % (b, {-3: "+5 V izq", -2: "GND izq", 12: "GND der", 13: "+12 V der"}.get(x, "?"), y + 1)


parts = []
for d in P.parts:
    pins = []
    for q in d["pins"]:
        bn, side, col, row = P.pos[(d["ref"], q["n"])]
        pins.append(dict(n=q["n"], net=q["net"], x=col, y=row, **({"name": q["name"]} if "name" in q else {})))
    bn = P.pos[(d["ref"], d["pins"][0]["n"])][0]
    p = dict(d, board=bn, pins=pins, short=d["ref"].split(".")[-1], x=min(q["x"] for q in pins), y=min(q["y"] for q in pins), blk=d["blk"])
    parts.append(p)
by_ref = {p["ref"]: p for p in parts}
nets = E.nets
W = []
for w in P.wires:
    a, b = dict(w["a"]), dict(w["b"])
    for e in (a, b):
        e["hole"] = hole(e["board"], e["x"], e["y"])
    W.append(dict(i=len(W) + 1, net=w["net"], color=nets[w["net"]]["color"], kind="signal", a=a, b=b))
for p in parts:
    if p.get("ext") or p["kind"] in ("TCRT", "OPTO"):
        dev = p.get("ext") or ("TCRT" if p["kind"] == "TCRT" else "OPTO")
        for q in p["pins"]:
            W.append(dict(i=len(W) + 1, net=q["net"], color=nets[q["net"]]["color"] if q["net"] in nets else "#bbbbbb", kind="ext",
                          a=dict(board=p["board"], x=q["x"], y=q["y"], hole=hole(p["board"], q["x"], q["y"]), part=p["ref"], pin=q["n"]),
                          b=dict(ext=dev, term=q["n"], hole="dispositivo " + dev + " · " + q["n"])))
# cables entre rieles de protoboards (GND, 5 V, 12 V)
for n, xs in (("0", (-2, -2)), ("v5", (-3, -3)), ("vm", (13, 13))):
    for i in range(1, len(BL)):
        W.append(dict(i=len(W) + 1, net=n, color=nets[n]["color"], kind="bus", a=dict(board=BL[0], x=xs[0], y=1 + 2 * i, hole=hole(BL[0], xs[0], 1 + 2 * i)),
                      b=dict(board=BL[i], x=xs[1], y=1 + 2 * i, hole=hole(BL[i], xs[1], 1 + 2 * i))))
gnd = {b: dict(x=-2, y=3) for b in BL}
titles = {b: "PROTOBOARD %s · 830 puntos" % b for b in BL}
data = dict(parts=parts, wires=W, tracks=[], zones=[], nets=nets, meas=E.MEAS, offs=offs, dims=dims, gnd=gnd, cu={b: "" for b in BL}, power=E.POWER, cell=1.27, pitch=2.54, w_trace=.8, w_wide=1.6,
            sim=E.datos_sim(), titles=titles, boards_list=BL, blocks={})
tpl = open(os.path.join(AQUI, "plantilla_proto3d.html"), encoding="utf-8").read()
three = open(os.path.join(AQUI, "..", "montaje3d", "lib3d", "three.min.js"), encoding="utf-8").read()
orbit = open(os.path.join(AQUI, "..", "montaje3d", "lib3d", "OrbitControls.js"), encoding="utf-8").read()
html = tpl.replace("/*__THREE__*/", three).replace("/*__ORBIT__*/", orbit).replace("/*__DATA__*/", "const DATA = " + json.dumps(data, ensure_ascii=False) + ";")
open(OUT, "w", encoding="utf-8").write(html)
print("ok:", len(BL), "protoboards,", len(parts), "piezas,", len(W), "cables ->", OUT)
