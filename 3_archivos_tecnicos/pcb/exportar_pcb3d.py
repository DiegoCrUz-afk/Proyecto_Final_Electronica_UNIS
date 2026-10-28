"""HTML 3D de las placas de cobre (pistas reales de generar_pcb.py). Uso: python exportar_pcb3d.py [salida.html]
Necesita pcb\\salida\\pcb_datos.json (lo escribe generar_pcb.py) y las imagenes del cobre."""
import base64
import io
import json
import os
import sys

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "montaje3d"))
sys.argv = sys.argv[:1] + [os.devnull]            # exportar_montaje3d lee argv[1]; aqui no escribimos su HTML
import exportar_montaje3d as E                    # noqa: E402  (mediciones, simulacion y colores de redes)
import generar_montaje3d as g3                    # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != os.devnull else os.path.join(AQUI, "..", "..", "6_Montaje_3D", "Placas_de_cobre_3D_miniestacion.html")
SAL = os.path.join(AQUI, "salida")
D = json.load(open(os.path.join(SAL, "pcb_datos.json")))
P = D["pitch_mm"]
CELL = D["cell_mm"]
NAMES = g3.NAMES
BL = D["boards_list"]

# ---- desplazamiento de cada placa en el 3D (en agujeros)
offs, x = {}, 0
for b in BL:
    offs[b] = x
    x += D["dims"][b][0] + 10
dims = {b: dict(x0=offs[b], x1=offs[b] + D["dims"][b][0], z1=D["dims"][b][1]) for b in BL}

# ---- piezas
ics = {p["ref"]: p for p in E.datos if p["kind"] == "IC"}
parts = []
for it in D["items"]:
    pins = []
    for q in it["pins"]:
        d = dict(n=q["n"], net=q["net"], x=q["x"], y=q["y"])
        if it["kind"] == "IC":
            d["name"] = NAMES[it["val"]][int(q["n"])]
        pins.append(d)
    p = dict(ref=it["ref"], blk=it["zone"], kind=it["kind"], val=it["val"], board=it["board"], x=it["x"], y=it["y"], w=it["bw"], h=it["bh"], pins=pins, short=it["ref"].split(".")[-1], note=it.get("note", ""))
    if it["kind"] == "IC":
        p["spare"] = ics[it["ref"]].get("spare", [])
        p["secs"] = ics[it["ref"]].get("secs", {})
    if it.get("ext"):
        p["ext"] = it["ext"]
    if it["kind"] == "CE":
        p["big"] = it["val"].startswith("1000")
    parts.append(p)
by_ref = {p["ref"]: p for p in parts}

# ---- puntos de union entre placas como piezas (soldar un poste de alambre)
hdr = []
for b in BL:
    for pd in D["boards"][b]["pads"]:
        if pd["ref"] == "X":
            ref = "XP.%s.%s" % (b, pd["net"])
            hdr.append(dict(ref=ref, blk="ENTRADA", kind="HDR", val=pd["pin"], board=b, x=pd["cx"] / 2, y=pd["cy"] / 2, w=1, h=1, short=pd["pin"], note="punto de union entre placas: se suelda un cable a la misma red de la otra placa",
                            pins=[dict(n="1", net=pd["net"], x=pd["cx"] / 2, y=pd["cy"] / 2)]))
parts += hdr
by_ref = {p["ref"]: p for p in parts}

# ---- cables
nets = E.nets
W = []


def pad_ep(b, pd):
    ref = pd["ref"] if pd["ref"] != "X" else "XP.%s.%s" % (b, pd["net"])
    pin = pd["pin"] if pd["ref"] != "X" else "1"
    return dict(board=b, x=pd["cx"] / 2, y=pd["cy"] / 2, hole="%s-%s%d" % (b, E.colname(int(pd["cx"] / 2)), int(pd["cy"] / 2) + 1), part=ref, pin=pin)


for b in BL:
    for jp in D["boards"][b]["jumpers"]:
        a = [pd for pd in D["boards"][b]["pads"] if pd["ref"] == jp["a"]["ref"] and pd["pin"] == jp["a"]["pin"]][0]
        c = [pd for pd in D["boards"][b]["pads"] if pd["ref"] == jp["b"]["ref"] and pd["pin"] == jp["b"]["pin"]][0]
        n = jp["net"]
        W.append(dict(i=len(W) + 1, net=n, color=nets[n]["color"] if n in nets else "#e91e8c", kind="signal", a=pad_ep(b, a), b=pad_ep(b, c)))
# entre placas
netb = {}
for b in BL:
    for pd in D["boards"][b]["pads"]:
        if pd["ref"] == "X":
            netb.setdefault(pd["net"], {})[b] = pd
for n, bs in netb.items():
    order = [b for b in BL if b in bs]
    for i in range(1, len(order)):
        a_b = order[0] if n in ("0", "v5", "vm") else order[i - 1]
        b_b = order[i]
        W.append(dict(i=len(W) + 1, net=n, color=nets[n]["color"], kind="bus", a=pad_ep(a_b, bs[a_b]), b=pad_ep(b_b, bs[b_b])))
# a dispositivos
for p in parts:
    if p.get("ext") or p["kind"] in ("TCRT", "OPTO"):
        dev = p.get("ext") or ("TCRT" if p["kind"] == "TCRT" else "OPTO")
        for q in p["pins"]:
            col = nets[q["net"]]["color"] if q["net"] in nets else "#bbbbbb"
            W.append(dict(i=len(W) + 1, net=q["net"], color=col, kind="ext",
                          a=dict(board=p["board"], x=q["x"], y=q["y"], hole="%s-%s%d" % (p["board"], E.colname(int(q["x"])), int(q["y"]) + 1), part=p["ref"], pin=q["n"]),
                          b=dict(ext=dev, term=q["n"], hole="dispositivo " + dev + " · " + q["n"])))

# ---- pistas
tracks = []
wide = set(D["wide_nets"])
for b in BL:
    for tk in D["boards"][b]["tracks"]:
        tracks.append(dict(board=b, net=tk["net"], cells=tk["cells"], wide=tk["net"] in wide))

# ---- texturas del cobre (vista desde el lado de piezas, el cobre en color cobre y el resto transparente)
cu = {}
for b in BL:
    im = Image.open(os.path.join(SAL, "PLACA_%s_cobre_vista_normal.png" % b)).convert("L")
    w = 1100
    im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    rgba = Image.new("RGBA", im.size, (0, 0, 0, 0))
    px = rgba.load()
    src = im.load()
    for yy in range(im.height):
        for xx in range(im.width):
            if src[xx, yy] < 128:
                px[xx, yy] = (184, 115, 51, 235)
    buf = io.BytesIO()
    rgba.save(buf, "PNG", optimize=True)
    cu[b] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

zones = [dict(id=z, title=D["ztitulos"][z], board=v[0], x=v[1], y=v[2], w=v[3], h=v[4]) for z, v in D["zonas"].items() if not z.startswith("_")]
gnd = {}
for b in BL:
    for pd in D["boards"][b]["pads"]:
        if pd["net"] == "0":
            gnd[b] = dict(x=pd["cx"] / 2, y=pd["cy"] / 2)
            break

data = dict(parts=parts, wires=W, tracks=tracks, zones=zones, nets=nets, meas=E.MEAS, offs=offs, dims=dims, gnd=gnd, cu=cu, power=E.POWER, cell=CELL, pitch=P, w_trace=D["w_trace"], w_wide=D["w_wide"],
            sim=E.datos_sim(), titles=D["titulos"], boards_list=BL, blocks={k: dict(title=v) for k, v in D["ztitulos"].items()})
tpl = open(os.path.join(AQUI, "plantilla_pcb3d.html"), encoding="utf-8").read()
three = open(os.path.join(AQUI, "..", "montaje3d", "lib3d", "three.min.js"), encoding="utf-8").read()
orbit = open(os.path.join(AQUI, "..", "montaje3d", "lib3d", "OrbitControls.js"), encoding="utf-8").read()
html = tpl.replace("/*__THREE__*/", three).replace("/*__ORBIT__*/", orbit).replace("/*__DATA__*/", "const DATA = " + json.dumps(data, ensure_ascii=False) + ";")
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(html)
print("ok:", len(parts), "piezas,", len(W), "cables/puentes,", len(tracks), "pistas,", round(len(html) / 1e6, 2), "MB ->", OUT)
