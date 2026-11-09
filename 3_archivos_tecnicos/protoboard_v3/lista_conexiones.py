"""Lista 2D de conexiones del montaje v3 (pata por pata, por bloque). Uso: python lista_conexiones.py [HTML_3D] [salida.html]
Lee los datos (const DATA) del HTML 3D del v3, asi la lista y el 3D siempre dicen lo mismo."""
import html
import json
import os
import sys
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "Protoboards_3D_miniestacion_v3_PRUEBA.html")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(AQUI, "Lista_conexiones_v3.html")
txt = open(SRC, encoding="utf-8").read()
D, _ = json.JSONDecoder().raw_decode(txt[txt.index("const DATA = ") + 13:])

LET = {0: "J", 1: "I", 2: "H", 3: "G", 4: "F", 6: "E", 7: "D", 8: "C", 9: "B", 10: "A"}
NR = 63
RAILX = {-3, -2, 12, 13}
parts, wires, nets, blocks = D["parts"], D["wires"], D["nets"], D["blocks"]
POWER = D["power"]
esc = html.escape


def hole(p, q):
    return "%s-%s%d" % (p["board"], LET.get(q["x"], "?"), NR - 1 - q["y"])


def skey(b, x, y):
    return ("R", b, x) if x in RAILX else (b, "L" if x <= 4 else "R", y)


def netname(n):
    if n == "NC":
        return "sin conexión"
    if n == "0":
        return "GND (0 V)"
    if n == "v5":
        return "+5 V"
    if n == "vm":
        return "+12 V"
    return n


by_net = defaultdict(list)
strip_parts = defaultdict(list)
for p in parts:
    for q in p["pins"]:
        by_net[q["net"]].append((p, q))
        strip_parts[skey(p["board"], q["x"], q["y"])].append(p)
short = lambda p: p["ref"].split(".")[-1]
order = D["blocks"].keys()

h = ['<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Lista de conexiones v3</title><style>',
     ':root{--bg:#fff;--tx:#1b2128;--mut:#5a6672;--line:#d5dbe1;--hd:#eef2f6;--acc:#0b63c5;--gnd:#1a237e;--v5:#b71c1c;--vm:#b25a00}',
     '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#171c22;--tx:#e8edf2;--mut:#9aa7b4;--line:#33404c;--hd:#202831;--acc:#6db3ff;--gnd:#8f9bff;--v5:#ff7a7a;--vm:#ffb454}}',
     'body{background:var(--bg);color:var(--tx);font:15px/1.45 system-ui,Segoe UI,Arial,sans-serif;margin:0;padding:16px;max-width:1100px;margin-inline:auto}',
     'h1{font-size:22px;margin:0 0 4px}h2{font-size:18px;margin:26px 0 6px;padding-top:10px;border-top:2px solid var(--line)}h3{font-size:15px;margin:14px 0 4px}',
     '.mut{color:var(--mut)}table{border-collapse:collapse;width:100%;margin:6px 0 10px;font-size:13.5px}th,td{border:1px solid var(--line);padding:3px 6px;text-align:left;vertical-align:top}th{background:var(--hd)}',
     '.g{color:var(--gnd);font-weight:600}.v5{color:var(--v5);font-weight:600}.vm{color:var(--vm);font-weight:600}.warn{background:var(--hd);border-left:4px solid var(--acc);padding:6px 10px;margin:8px 0}',
     'nav a{color:var(--acc);margin-right:10px;white-space:nowrap}@media print{nav{display:none}h2{break-before:page}}',
     '</style></head><body>',
     '<h1>Lista de conexiones · pata por pata</h1>',
     '<div class="mut">Miniestación industrial automatizada. Generada del mismo dato que el 3D v3, así que ambos dicen lo mismo. El agujero se lee <b>placa-letra+fila</b> (ejemplo <b>B-F42</b> = placa B, columna F, fila 42; las filas se cuentan desde abajo como en el tablero). Una pata que dice "va a GND" se une con un cable corto al riel de tierra.</div>',
     '<nav>' + "".join('<a href="#b_%s">%s</a>' % (z, esc(blocks[z]["title"])) for z in order) + '<a href="#rieles">Rieles y puentes</a></nav>']

# ---- rieles
h.append('<h2 id="rieles">Rieles y puentes entre placas (PRO\'S KIT BX-4135 + protoboards sueltas)</h2>')
h.append('<div class="warn">Las placas A, B y C son las 3 protoboards de la BX-4135: el par de rieles de en medio lo comparten dos protoboards vecinas. Cada riel viene cortado a la mitad (filas 0 a 32 y 33 a 62): los dos puentes del medio los unen.</div>')
h.append('<table><tr><th>Placa</th><th>Riel izquierdo +</th><th>Riel izquierdo −</th><th>Riel derecho +</th><th>Riel derecho −</th></tr>')
for b in D["boards_list"]:
    r = D["rails"][b]
    h.append("<tr><td><b>%s</b>%s</td>%s</tr>" % (b, " (BX-4135)" if b in D["bx"] else " (suelta)", "".join("<td>%s</td>" % esc(netname(r[k])) for k in ("-3", "-2", "12", "13"))))
h.append("</table>")
h.append("<h3>Puentes entre rieles</h3><table><tr><th>Cable</th><th>Red</th><th>De</th><th>A</th></tr>")
for w in wires:
    if w["kind"] == "bus":
        h.append("<tr><td>[%d]</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (w["i"], esc(netname(w["net"])), esc(w["a"]["hole"]), esc(w["b"]["hole"])))
h.append("</table>")

# ---- bloques
for z in order:
    B = blocks[z]
    ps = [p for p in parts if p["blk"] == z]
    h.append('<h2 id="b_%s">%s · placa %s</h2>' % (z, esc(B["title"]), " y ".join(B["boards"])))
    g = {}
    for p in ps:
        g.setdefault((p["kind"], p["val"]), []).append(short(p))
    h.append('<h3>Componentes de este bloque (sepáralos antes de armar)</h3><table><tr><th>Cant.</th><th>Componente</th><th>Nombres</th></tr>')
    for (k, v), refs in sorted(g.items(), key=lambda kv: (0 if kv[0][0] == "IC" else 1, kv[1][0])):
        h.append("<tr><td>%d</td><td>%s</td><td>%s</td></tr>" % (len(refs), esc(str(v)), esc(", ".join(refs))))
    h.append("</table>")
    h.append("<h3>Conexiones pata por pata</h3><table><tr><th>Pieza</th><th>Pata</th><th>Nombre</th><th>Agujero</th><th>Va a</th></tr>")
    for p in sorted(ps, key=lambda p: (0 if p["kind"] == "IC" else 1, p["ref"])):
        n = len(p["pins"])
        for i, q in enumerate(p["pins"]):
            net = q["net"]
            if net in POWER:
                va = '<span class="%s">%s</span> (riel)' % ({"0": "g", "v5": "v5", "vm": "vm"}[net], esc(netname(net)))
            elif net == "NC":
                va = '<span class="mut">sin conexión</span>'
            else:
                otros = [o for o in by_net[net] if not (o[0]["ref"] == p["ref"] and o[1]["n"] == q["n"])]
                va = ", ".join("%s pata %s" % (short(o[0]), o[1]["n"]) for o in otros) or "—"
                va = esc(netname(net)) + " → " + esc(va)
            first = "<td rowspan=%d><b>%s</b><br>%s</td>" % (n, esc(short(p)), esc(str(p["val"]))) if i == 0 else ""
            h.append("<tr>%s<td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (first, esc(q["n"]), esc(q.get("name", "")), hole(p, q), va))
    h.append("</table>")
    # cables del bloque: los que tocan una tira con piezas de este bloque
    mis = {(p["board"], q["x"] if q["x"] in RAILX else None, q["y"]) for p in ps for q in p["pins"]}
    cs = []
    for w in wires:
        if w["kind"] == "bus":
            continue
        toca = False
        for e in (w["a"], w["b"]):
            if "board" in e and e["x"] not in RAILX and any(pp["blk"] == z for pp in strip_parts.get(skey(e["board"], e["x"], e["y"]), [])):
                toca = True
        if toca:
            cs.append(w)
    h.append("<h3>Cables de este bloque</h3><table><tr><th>Cable</th><th>Red</th><th>De</th><th>A</th></tr>")
    for w in cs:
        h.append("<tr><td>[%d]</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (w["i"], esc(netname(w["net"])), esc(w["a"]["hole"]), esc(w["b"]["hole"])))
    h.append("</table>")
    # pruebas
    ids = D["tests"].get(z, [])
    if ids:
        h.append("<h3>Pruebas al terminar el bloque</h3><table><tr><th>Medida</th><th>Esperado</th><th>Si no coincide</th></tr>")
        for i in ids:
            m = next(x for x in D["meas"] if x["id"] == i)
            h.append("<tr><td>%s<br><span class=mut>%s</span></td><td>%s</td><td>%s</td></tr>" % (esc(m["t"]), esc(m["mode"]), esc(m["exp"]), esc(m["bad"])))
        h.append("</table>")
h.append("</body></html>")
open(OUT, "w", encoding="utf-8").write("\n".join(h))
print("ok ->", OUT, len(wires), "cables,", len(parts), "piezas")
