"""Verifica el 3D leyendo SOLO los datos del HTML (piezas, patas, agujeros, cables):
 1) ningun agujero tiene dos patas / dos cables
 2) ninguna tira de 5 agujeros ni riel mezcla redes
 3) todas las patas de una misma red quedan unidas (por tiras, rieles y cables) en UN solo grupo
 4) dos redes distintas nunca quedan unidas
Uso: py -3.13 verificar_3d.py archivo.html"""
import io
import json
import sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
html = open(sys.argv[1], encoding="utf-8").read()
d, _ = json.JSONDecoder().raw_decode(html[html.index("const DATA = ") + 13:])
RIEL = {-3, -2, 12, 13}


BX = d.get("bx", [])
BL = d["boards_list"]


def nodo(board, x, y):
    if x in RIEL:
        if board in BX and BX.index(board) > 0 and x in (-3, -2):      # el riel izquierdo de B y C es el derecho de la protoboard vecina (BX-4135)
            return ("RIEL", BX[BX.index(board) - 1], x + 15)
        return ("RIEL", board, x)
    return ("TIRA", board, "L" if x <= 4 else "R", y)


par = {}


def f(a):
    par.setdefault(a, a)
    while par[a] != a:
        par[a] = par[par[a]]
        a = par[a]
    return a


def union(a, b):
    par[f(a)] = f(b)


problemas = []
agujeros = defaultdict(list)
nets_de = defaultdict(set)      # nodo -> redes esperadas
for p in d["parts"]:
    for q in p["pins"]:
        n = nodo(p["board"], q["x"], q["y"])
        f(n)
        nets_de[n].add(q["net"])
        agujeros[(p["board"], q["x"], q["y"])].append("pata " + p["ref"] + "." + q["n"])
for w in d["wires"]:
    ext = []
    for e in (w["a"], w["b"]):
        if "ext" in e:
            n = ("DISP", e["ext"], e["term"])
        else:
            n = nodo(e["board"], e["x"], e["y"])
            if w["kind"] != "ext":      # el cable a un dispositivo sale de la pata del conector (misma pieza): no cuenta como agujero repetido
                agujeros[(e["board"], e["x"], e["y"])].append("cable %d" % w["i"])
        f(n)
        nets_de[n].add(w["net"])
        ext.append(n)
    union(ext[0], ext[1])
for b_ in BL:                                    # cada riel fisico lleva la red que dice DATA.rails
    for c_, n_ in d.get("rails", {}).get(b_, {}).items():
        nr = nodo(b_, int(c_), 0)
        f(nr)
        nets_de[nr].add(n_)
# 1) agujeros repetidos
for k, v in agujeros.items():
    if len(v) > 1:
        problemas.append("agujero %s usado %d veces: %s" % (k, len(v), v))
# 2) y 4) componentes con mas de una red
comp = defaultdict(set)
for n, ns in nets_de.items():
    for x in ns:
        comp[f(n)].add(x)
for c, ns in comp.items():
    ns = {x for x in ns if x != "NC"}
    if len(ns) > 1:
        problemas.append("grupo que mezcla redes: %s" % sorted(ns))
# 3) cada red en un solo grupo
grupos = defaultdict(set)
for n, ns in nets_de.items():
    for x in ns:
        if x != "NC":
            grupos[x].add(f(n))
partidas = {x: len(g) for x, g in grupos.items() if len(g) > 1}
for x, k in sorted(partidas.items()):
    problemas.append("la red %s queda en %d grupos separados (no se conecta del todo)" % (x, k))
npatas = sum(len(p["pins"]) for p in d["parts"])
print("piezas:", len(d["parts"]), " patas:", npatas, " cables:", len(d["wires"]), " redes:", len(grupos))
if problemas:
    print("PROBLEMAS (%d):" % len(problemas))
    for t in problemas[:40]:
        print(" -", t)
else:
    print("OK: todas las redes completas, sin mezclas y sin agujeros repetidos")
