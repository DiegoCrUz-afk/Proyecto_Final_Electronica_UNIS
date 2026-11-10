"""HTML 3D de la Reduccion 2 (3 protoboards BX-4135). Uso: py -3.13 exportar_r2.py  ->  ../Protoboards_3D_reduccion2.html"""
import json
import os
import sys
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.argv = sys.argv[:1] + [os.devnull]
import generar_protoboard as P            # noqa: E402
import ruteo_plano as ruteo               # noqa: E402

OUT = os.path.join(AQUI, "..", "Protoboards_3D_reduccion2.html")
LET = {0: "J", 1: "I", 2: "H", 3: "G", 4: "F", 6: "E", 7: "D", 8: "C", 9: "B", 10: "A"}
ROWS_N = 63
row_lbl = lambda y: ROWS_N - 1 - y
POWER = {"0": "GND", "v5": "5V"}
PCOL = {"0": "#1a1a1a", "v5": "#e53935"}
PAL = ["#00bcd4", "#8bc34a", "#ffeb3b", "#e91e63", "#9c27b0", "#03a9f4", "#ff5722", "#cddc39", "#795548", "#4caf50", "#f06292", "#7e57c2",
       "#26a69a", "#ffa726", "#5c6bc0", "#d4e157", "#29b6f6", "#ec407a", "#66bb6a", "#ab47bc", "#ffca28", "#26c6da", "#ef5350", "#9ccc65"]


def hole(b, x, y):
    if x in LET:
        return "%s-%s%d" % (b, LET[x], row_lbl(y))
    nom = {"0": "GND", "v5": "+5 V"}[P.rails_of(b)[x]]
    return "%s-riel %s %s fila %d" % (b, nom, "izq" if x < 5 else "der", row_lbl(y))


BL = [b.name for b in P.boards]
offs = {b: P.offset(b) for b in BL}
dims = {b: dict(x0=offs[b] - 4.5, x1=offs[b] + 14.5, z1=64) for b in BL}
POLAR_1U = {"LOG.Cpor"}
parts = []
for d in P.parts:
    pins = []
    for q in d["pins"]:
        bn, side, col, row = P.pos[(d["ref"], q["n"])]
        pins.append(dict(n=q["n"], net=q["net"], x=col, y=row, **({"name": q["name"]} if "name" in q else {})))
    bn = P.pos[(d["ref"], d["pins"][0]["n"])][0]
    p = dict(d, board=bn, pins=pins, short=d["ref"].split(".")[-1], x=min(q["x"] for q in pins), y=min(q["y"] for q in pins))
    if d["ref"] in POLAR_1U:
        p["kind"] = "CE"
        for q in p["pins"]:
            q["n"] = {"1": "+", "2": "-"}[q["n"]]
    p["cells"] = sorted({tuple(c) for c in P.partinfo.get(d["ref"], {}).get("area", [])})
    parts.append(p)
by_ref = {p["ref"]: p for p in parts}
net_pins = defaultdict(list)
for p in parts:
    for q in p["pins"]:
        if q["net"] != "NC":
            net_pins[q["net"]].append((p["ref"], q))
nets = {}
colores = {n: PAL[i % len(PAL)] for i, n in enumerate(sorted(n for n in net_pins if n not in POWER))}
for n in net_pins:
    nets[n] = dict(color=PCOL.get(n, colores.get(n, "#aaaaaa")), label=("GND" if n == "0" else n))
W = []
for w in P.wires:
    a, b = dict(w["a"]), dict(w["b"])
    for e in (a, b):
        e["hole"] = hole(e["board"], e["x"], e["y"])
    W.append(dict(i=len(W) + 1, net=w["net"], color=nets[w["net"]]["color"], kind="signal", a=a, b=b))
for p in parts:
    if p.get("ext") or p["kind"] in ("TCRT", "OPTO"):
        dev = p.get("ext") or "TCRT"
        for q in p["pins"]:
            W.append(dict(i=len(W) + 1, net=q["net"], color=nets[q["net"]]["color"] if q["net"] in nets else "#bbbbbb", kind="ext",
                          a=dict(board=p["board"], x=q["x"], y=q["y"], hole=hole(p["board"], q["x"], q["y"]), part=p["ref"], pin=q["n"]),
                          b=dict(ext=dev, term=q["n"], hole="dispositivo " + dev + " · " + q["n"])))
for w in P.bus:
    a, b = dict(w["a"]), dict(w["b"])
    for e in (a, b):
        e["hole"] = hole(e["board"], e["x"], e["y"])
    W.append(dict(i=len(W) + 1, net=w["net"], color=nets[w["net"]]["color"], kind="bus", a=a, b=b))
NIV = ruteo.rutear(W, parts, offs)
print("niveles de altura usados:", NIV)
# ---------------- cables ordenados: numeracion por bloque (en el orden de armado) y colores por funcion ----------------
import pruebas_r2 as PR
ORD = {b: i for i, b in enumerate(PR.BLOQUES)}
strip_parts = defaultdict(list)
for (ref_, pin_), (bn_, side_, col_, row_) in P.pos.items():
    strip_parts[(bn_, side_, row_)].append(ref_)
COLOR_BLOQUE = {"ALIM": "#bdbdbd", "SENSOR_IR": "#f4d03f", "ENTRADAS": "#00bcd4", "PESTILLO": "#c06cff", "LOGICA": "#3ddc84", "POTENCIA": "#ff9f43", "LED_ROJO": "#ff6b9d"}


def bloque_cable(w):
    if w["kind"] == "bus":
        return "ALIM"
    if w["kind"] == "ext":
        return by_ref[w["a"]["part"]]["blk"]
    bl = []
    for e in (w["a"], w["b"]):
        if e["x"] in (-3, -2, 12, 13):
            continue
        for r in strip_parts[(e["board"], "L" if e["x"] <= 4 else "R", e["y"])]:
            bl.append(by_ref[r]["blk"])
    return max(bl, key=lambda b: ORD[b]) if bl else "ALIM"


for w in W:
    w["blk"] = bloque_cable(w)
W.sort(key=lambda w: (ORD[w["blk"]], {"signal": 0, "ext": 1, "bus": 2}[w["kind"]], w["a"]["board"], w["a"]["y"], w["a"]["x"]))
for k, w in enumerate(W):
    w["i"] = k + 1
    w["color"] = "#1a1a1a" if w["net"] == "0" else "#e53935" if w["net"] == "v5" else COLOR_BLOQUE[w["blk"]]
gnd = {b: dict(x=-2, y=1) for b in BL}        # punta negra: riel GND izquierdo, fila 1
titles = {b: "BX-4135 · protoboard %d (placa %s)" % (BL.index(b) + 1, b) for b in BL}
zones = []
for b in P.boards:
    for z, (r0, r1) in b.blocks.items():
        zones.append(dict(id=z, title=P.TITULOS[z], board=b.name, x=0, y=r0 - 2, w=11, h=r1 - r0 + 3))
blocks = {}
for z in P.ORDEN:
    refs = [p["ref"] for p in parts if p["blk"] == z]
    blocks[z] = dict(title=P.TITULOS[z], boards=sorted({by_ref[r]["board"] for r in refs}), refs=refs)
rails = {b: {str(c): n for c, n in P.rails_of(b).items()} for b in BL}

# ---------------- mediciones: vienen de pruebas_r2.py (mismas para el 3D, la guia y el verificador de simulacion) ----------------
MEAS = PR.M


def _chk(e):
    if e is None or isinstance(e, dict):
        return
    assert e[0] in by_ref and any(q["n"] == e[1] for q in by_ref[e[0]]["pins"]), ("pata que no existe", e)


for x in MEAS:
    _chk(x["red"]); _chk(x["black"])
med = {b: [x["id"] for x in MEAS if x["blk"] == b] for b in PR.BLOQUES}
data = dict(parts=parts, wires=W, tracks=[], zones=zones, nets=nets, meas=MEAS, offs=offs, dims=dims, gnd=gnd, cu={b: "" for b in BL}, power=POWER, cell=1.27, pitch=2.54,
            w_trace=.8, w_wide=1.6, sim=None, titles=titles, boards_list=BL, blocks=blocks, rails=rails, bx=P.BX, tests=dict(med), med=med)
tpl = open(os.path.join(AQUI, "plantilla_r2.html"), encoding="utf-8").read()
three = open(os.path.join(AQUI, "lib3d", "three.min.js"), encoding="utf-8").read()
orbit = open(os.path.join(AQUI, "lib3d", "OrbitControls.js"), encoding="utf-8").read()
html = tpl.replace("/*__THREE__*/", three).replace("/*__ORBIT__*/", orbit).replace("/*__DATA__*/", "const DATA = " + json.dumps(data, ensure_ascii=False) + ";")
open(OUT, "w", encoding="utf-8").write(html)
json.dump(data, open(os.path.join(AQUI, "datos_r2.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("ok:", len(BL), "protoboards,", len(parts), "piezas,", len(W), "cables ->", os.path.abspath(OUT))
