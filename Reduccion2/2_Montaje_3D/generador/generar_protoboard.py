"""Montaje en PROTOBOARDS v3 (guia para armar junto al esquematico). Uso: python generar_protoboard.py
Cambios respecto a v2:
- Las placas A, B y C son las 3 protoboards de la PRO'S KIT BX-4135: los rieles de en medio se comparten entre dos protoboards vecinas.
- Las piezas se colocan por BLOQUES (cada bloque en su franja de filas), con la huella real de cada pieza (ancho del cuerpo,
  disipador, etc.) y una fila libre entre piezas: nada se sobrepone.
- verificar(): cada red queda en un solo grupo y ninguna tira mezcla redes.
"""
import copy
import json
import os
import random
import sys
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import datos_r2 as D

ROWS = 63
LCOLS, RCOLS = [0, 1, 2, 3, 4], [6, 7, 8, 9, 10]          # canal en x = 5
POWER = {"0", "v5"}
NAMES = "ABC"
BX = ["A", "B", "C"]                                     # protoboards de la BX-4135


def offset(name):
    i = NAMES.index(name)
    return 15 * i if i < 3 else 54 + 22 * (i - 3)


def rails_of(name):
    """red de cada riel de la placa (izq +,-  y  der +,-). En la BX los rieles de en medio los comparten dos protoboards vecinas."""
    return {-3: "v5", -2: "0", 12: "v5", 13: "0"}


def canon(bn, x):
    """identidad fisica de un riel (el riel derecho de A es el izquierdo de B, y asi con C)."""
    if bn in ("B", "C") and x in (-3, -2):
        return (NAMES[NAMES.index(bn) - 1], x + 15)
    return (bn, x)


datos, zonas, ics = D.construir_todo()
parts = [d for d in datos]
# Reduccion 2: A = entrada de 5 V, potencia y LED rojo; B = sensor IR; C = logica, entradas y LED de objeto
ORDEN = ["ALIM", "POTENCIA", "LED_ROJO", "SENSOR_IR", "ENTRADAS", "PESTILLO", "LOGICA"]
NUEVA_PLACA = {"SENSOR_IR", "PESTILLO"}      # A: alimentacion, potencia, LED rojo | B: sensor IR + entradas | C: pestillo + decision
TITULOS = dict(D.TITULOS)
GAP_BLOQUES = 3

# huella de cada pieza: k = filas entre patas; cl/cr = columnas que ocupa el cuerpo a izquierda/derecha de la columna de las patas;
# rb/ra = filas ocupadas antes/despues de las patas (el cuerpo y una fila libre de separacion)
FP = {
    "R": dict(k=4, cl=0, cr=0, rb=0, ra=1), "D": dict(k=4, cl=0, cr=0, rb=0, ra=1), "DZ": dict(k=4, cl=0, cr=0, rb=0, ra=1),
    "RW": dict(k=5, cl=0, cr=1, rb=0, ra=1), "CC": dict(k=2, cl=0, cr=0, rb=0, ra=1),
    "LED": dict(k=2, cl=1, cr=1, rb=0, ra=1), "BUZZER": dict(k=3, cl=0, cr=2, rb=1, ra=2, cols=(0, 10)),
    "TRIM": dict(k=1, cl=0, cr=1, rb=1, ra=2), "Q92": dict(k=1, cl=0, cr=1, rb=0, ra=1),
    "Q126": dict(k=1, cl=1, cr=0, rb=1, ra=2), "MOS": dict(k=1, cl=3, cr=0, rb=1, ra=2, cols=(4,), side="L"),
    "TB": dict(k=2, cl=0, cr=0, rb=0, ra=1), "TCRT": dict(k=1, cl=0, cr=1, rb=0, ra=1),
}
ESPECIALES = {"MOS", "Q126", "BUZZER", "CE"}


def fp_of(d):
    f = dict(FP.get(d["kind"], {}))
    if d["kind"] == "CE":
        f = dict(k=3, cl=2, cr=1, rb=0, ra=1) if d.get("big") else dict(k=2, cl=1, cr=1, rb=0, ra=1)
    if d["kind"] == "CC" and "µF" in str(d["val"]):
        f = dict(k=2, cl=0, cr=1, rb=0, ra=1)            # capacitor de pelicula: cuerpo de unos 6.6 x 3.4 mm
    return f


class Board:
    def __init__(self, name):
        self.name = name
        self.strip = {}                      # (side, row) -> red
        self.cols = defaultdict(set)         # (side, row) -> columnas ocupadas por patas
        self.cells = set()                   # (side, col, row) ocupadas (patas y cuerpos)
        self.cursor = 0                      # primera fila libre para el siguiente bloque
        self.blocks = {}                     # bloque -> [fila min, fila max]

    def free_holes(self, side, row):
        return [c for c in (RCOLS if side == "R" else LCOLS) if c not in self.cols[(side, row)] and (side, c, row) not in self.cells]

    def free_strip(self, side, row, net=None):
        s = self.strip.get((side, row))
        return 0 <= row < ROWS and (s is None or (net is not None and s == net))


boards = []
pos = {}            # (ref, pin) -> (board, side, col, row)
nstr = defaultdict(list)   # red -> [(board, side, row)]
partinfo = {}       # ref -> dict(board, rows)


def new_board():
    boards.append(Board(NAMES[len(boards)]))
    assert len(boards) <= len(NAMES), "faltan placas"
    return boards[-1]


def put(b, ref, pin, net, side, col, row):
    b.strip[(side, row)] = net
    b.cols[(side, row)].add(col)
    b.cells.add((side, col, row))
    pos[(ref, pin)] = (b.name, side, col, row)
    if (b.name, side, row) not in nstr[net]:
        nstr[net].append((b.name, side, row))


def sidecols(side):
    return RCOLS if side == "R" else LCOLS


def snapshot():
    return copy.deepcopy((boards, pos, dict(nstr), partinfo))


def restore(s):
    s = copy.deepcopy(s)          # la copia guardada no se toca: se puede volver a ella varias veces
    boards[:] = s[0]
    pos.clear(); pos.update(s[1])
    nstr.clear(); nstr.update(s[2])
    partinfo.clear(); partinfo.update(s[3])


def ic_rows(d):
    return len(d["pins"]) // 2


def place_ic(b, d, r0):
    n = len(d["pins"])
    h = n // 2
    for q in d["pins"]:
        i = int(q["n"])
        if i <= h:
            put(b, d["ref"], q["n"], q["net"], "L", 4, r0 + i - 1)
        else:
            put(b, d["ref"], q["n"], q["net"], "R", 6, r0 + (n - i))
    partinfo[d["ref"]] = dict(board=b.name, rows=(r0, r0 + h - 1), area=[(c, rw) for c in (4, 5, 6) for rw in range(r0, r0 + h)])


def find_ic_rows(b, h, start):
    r = start
    while r + h <= ROWS:
        if all(b.strip.get((s, rr)) is None and (s, 4 if s == "L" else 6, rr) not in b.cells for s in "LR" for rr in range(r, r + h)):
            return r
        r += 1
    return None


def candidates(b, d, row_from, row_to):
    """todas las posiciones validas de una pieza: (lado, columna de las patas, fila de la 1a pata, filas, area que ocupa)."""
    f = fp_of(d)
    pins = d["pins"]
    n = len(pins)
    span = f["k"] * (n - 1)
    out = []
    for r in range(max(0, row_from), min(ROWS - 1 - span, row_to) + 1):
        for side in "LR":
            if f.get("side") and f["side"] != side:
                continue
            sc = sidecols(side)
            for col in sc:
                if f.get("cols") and col not in f["cols"]:
                    continue
                for mir in (0, 1):
                    cl, cr = (f["cl"], f["cr"]) if not mir else (f["cr"], f["cl"])
                    if mir and f["cl"] == f["cr"]:
                        continue
                    if col - cl < sc[0] or col + cr > sc[-1]:
                        continue
                    rows = [r + f["k"] * i for i in range(n)]
                    r_lo, r_hi = r - f["rb"], r + span + f["ra"]
                    if r_lo < 0 or r_hi >= ROWS:
                        continue
                    if any(not b.free_strip(side, rr, q["net"]) for rr, q in zip(rows, pins)):
                        continue
                    area = [(side, c, rr) for rr in range(r_lo, r_hi + 1) for c in range(col - cl, col + cr + 1)]
                    if any(a in b.cells for a in area):
                        continue
                    ok = True
                    for rr in range(r_lo, r_hi + 1):
                        if (side, rr) in b.strip or rr in rows:
                            libres = [c for c in sc if c not in b.cols[(side, rr)] and (side, c, rr) not in b.cells and not (col - cl <= c <= col + cr)]
                            if not libres:
                                ok = False
                                break
                    if ok:
                        out.append((side, col, r, rows, area))
    return out


RNG = None          # generador de ruido para la busqueda; None = decision fija
NOISE = 0.0


def costo(b, d, side, col, r, rows):
    """menos cables: patas que comparten tira con su red, cercania a las tiras de sus redes y lado con el riel que le toca."""
    share = 0
    dist = 0
    for rr, q in zip(rows, d["pins"]):
        net = q["net"]
        if b.strip.get((side, rr)) == net:
            share += 1
        if net in POWER or net == "NC":
            continue
        ex = [row for (bn, s, row) in nstr.get(net, []) if bn == b.name]
        if ex:
            dist += min(abs(rr - e) for e in ex)
    cfg = rails_of(b.name)
    sc = (-3, -2) if side == "L" else (12, 13)
    mal = sum(1 for q in d["pins"] if q["net"] in POWER and q["net"] not in [cfg[c] for c in sc])
    ruido = RNG.random() * NOISE * 3 if RNG else 0
    return (-share, mal, dist + ruido, r, col)


def place_free(b, d, row_from, row_to):
    cs = candidates(b, d, row_from, row_to)
    if not cs:
        return False
    side, col, r, rows, area = min(cs, key=lambda c: costo(b, d, c[0], c[1], c[2], c[3]))
    for rr, q in zip(rows, d["pins"]):
        put(b, d["ref"], q["n"], q["net"], side, col, rr)
    for a in area:
        b.cells.add(a)
    partinfo[d["ref"]] = dict(board=b.name, rows=(min(rows), max(rows)), area=[(c, rw) for (sd, c, rw) in area])
    return True


def place_opto(b, d, row_from, row_to):
    """Optointerruptor ranurado: 2 patas por brazo. A K a un lado del canal y C E al otro (a horcajadas, como la pieza real)."""
    pa = {q["n"]: q for q in d["pins"]}
    lc = [4, 3, 2, 1, 0]
    rc = [6, 7, 8, 9, 10]
    for r in range(max(0, row_from), min(ROWS - 2, row_to) + 1):
        want = [("L", r, "A"), ("L", r + 1, "K"), ("R", r, "C"), ("R", r + 1, "E")]
        if any(not b.free_strip(s, rr, pa[n]["net"]) for s, rr, n in want):
            continue
        cols = []
        for s, rr, n in want:
            cols.append(next((c for c in (lc if s == "L" else rc) if c not in b.cols[(s, rr)] and (s, c, rr) not in b.cells), None))
        if None in cols or any(len(b.cols[(s, rr)]) >= 4 for s, rr, n in want):
            continue
        for (s, rr, n), c in zip(want, cols):
            put(b, d["ref"], n, pa[n]["net"], s, c, rr)
        partinfo[d["ref"]] = dict(board=b.name, rows=(r, r + 1))
        return True
    return False


def place_block(b, z, items):
    """Pone un bloque en la placa b a partir de su cursor. Devuelve True si todo cabe."""
    ci = sorted([d for d in items if d["kind"] == "IC"], key=lambda d: d["ref"])
    if RNG:
        RNG.shuffle(ci)
    rest = [d for d in items if d["kind"] != "IC"]
    start = b.cursor
    row = start
    for d in ci:
        r0 = find_ic_rows(b, ic_rows(d), row)
        if r0 is None:
            return False
        place_ic(b, d, r0)
        row = r0 + ic_rows(d) + 2                  # dos filas libres entre circuitos integrados
    pend = list(rest)
    while pend:
        # se crece desde lo ya puesto: primero la pieza que mas patas tiene en redes ya presentes en esta placa
        def score(d):
            conn = sum(1 for q in d["pins"] if q["net"] not in POWER and q["net"] != "NC" and any(bn == b.name for bn, s, rw in nstr.get(q["net"], [])))
            return (-(conn + (3 if d["kind"] in ESPECIALES else 0)) + (RNG.random() * NOISE * 2 if RNG else 0), d["ref"])
        d = min(pend, key=score)
        pend.remove(d)
        ok = False
        for hi in (start + 14, start + 24, start + 34, ROWS):
            hi = min(hi, ROWS - 1)
            ok = place_opto(b, d, start, hi) if d["kind"] == "OPTO" else place_free(b, d, start, hi)
            if ok:
                break
        if not ok:
            return False
    refs = {x["ref"] for x in items}
    rws = [r for ref, info in partinfo.items() if ref in refs for r in info["rows"]]
    b.blocks[z] = [min(rws), max(rws)]
    b.cursor = max(rws) + 2 + GAP_BLOQUES
    return True


def costo_bloque(b, items):
    """cables estimados del bloque: por cada red, cuanto se separan sus tiras (filas) y cuantas tiras hay; piezas de alimentacion en el lado sin su riel."""
    refs = {x["ref"] for x in items}
    redes = defaultdict(set)
    c = 0.0
    cfg = rails_of(b.name)
    for d in items:
        for q in d["pins"]:
            bn, side, col, row = pos[(d["ref"], q["n"])]
            if q["net"] == "NC":
                continue
            if q["net"] in POWER:
                sc = (-3, -2) if side == "L" else (12, 13)
                if q["net"] not in [cfg[x] for x in sc]:
                    c += 12
                continue
            redes[q["net"]].add((side, row))
    for net, st in redes.items():
        todas = [(sd, rw) for (bn, sd, rw) in nstr[net] if bn == b.name]
        if len(todas) < 2:
            continue
        rws = [rw for sd, rw in todas]
        c += (max(rws) - min(rws)) + 1.5 * (len(todas) - 1) + 3 * len({sd for sd, rw in todas}) - 3
        if any(bn != b.name for (bn, sd, rw) in nstr[net]):
            c += 15
    return c


INTENTOS = 1200


def colocar():
    global RNG, NOISE
    zonas_p = defaultdict(list)
    for d in parts:
        zonas_p[d["blk"]].append(d)
    new_board()
    for z in ORDEN:
        if z in NUEVA_PLACA:
            new_board()
        items = zonas_p[z]
        mejor = None
        for intento in range(INTENTOS):
            snap = snapshot()
            RNG = random.Random(intento) if intento else None
            NOISE = 0 if not intento else 0.6 + (intento % 5) * 0.5
            nb = len(boards)
            ok = place_block(boards[-1], z, items)
            nueva = False
            if not ok:
                restore(snap)
                new_board()
                nueva = True
                ok = place_block(boards[-1], z, items)
            if ok:
                c = costo_bloque(boards[-1], items) + (1000 if nueva else 0) + boards[-1].cursor * 0.15
                if mejor is None or c < mejor[0]:
                    mejor = (c, intento, nueva)
            restore(snap)
        RNG = None
        NOISE = 0
        assert mejor, ("el bloque no cabe en una placa", z)
        intento = mejor[1]
        RNG = random.Random(intento) if intento else None
        NOISE = 0 if not intento else 0.6 + (intento % 5) * 0.5
        if mejor[2]:
            new_board()
        assert place_block(boards[-1], z, items), z
        RNG = None
        NOISE = 0


colocar()

# electroliticos de 1 uF (lista de compras): cuerpo de 5 mm, mas ancho que el capacitor de pelicula con el que se coloco. Si el cuerpo toca otra pieza,
# SOLO ese capacitor se vuelve a colocar (el resto no se mueve; las placas A y B no se tocan nunca).
POLAR_1U = {"LOG.Cpor"}
PLACAS_LIBRES = {"A", "B", "C"}


def quitar_pieza(b, d):
    area = set(partinfo[d["ref"]].get("area", []))
    for q in d["pins"]:
        _, side, col, row = pos.pop((d["ref"], q["n"]))
        b.cols[(side, row)].discard(col)
        b.cells.discard((side, col, row))
        if not b.cols[(side, row)]:
            b.strip.pop((side, row), None)
            if (b.name, side, row) in nstr[q["net"]]:
                nstr[q["net"]].remove((b.name, side, row))
    for (c, rw) in area:
        for sd in "LR":
            b.cells.discard((sd, c, rw)) if (sd == "L") == (c <= 4) else None
    del partinfo[d["ref"]]


for _d in parts:
    if _d["ref"] in POLAR_1U:
        _bn = pos[(_d["ref"], _d["pins"][0]["n"])][0]
        _b = next(x for x in boards if x.name == _bn)
        _ce = dict(_d, kind="CE")
        _side, _col = pos[(_d["ref"], _d["pins"][0]["n"])][1:3]
        _rows = [pos[(_d["ref"], q["n"])][3] for q in _d["pins"]]
        _f = fp_of(_ce)
        _propias = set(partinfo[_d["ref"]].get("area", []))
        _choca = any((_side, c, r) in _b.cells and (c, r) not in _propias
                     for r in range(min(_rows) - _f["rb"], max(_rows) + _f["ra"] + 1) for c in range(_col - _f["cl"], _col + _f["cr"] + 1))
        if _choca:
            assert _bn in PLACAS_LIBRES, ("no se puede mover una pieza de las placas A o B", _d["ref"])
            quitar_pieza(_b, _d)
            assert place_free(_b, _ce, 0, ROWS - 1), ("no hay lugar para", _d["ref"])
            print("recolocado:", _d["ref"], "en la placa", _bn)
BN = {b.name: b for b in boards}

# ---------------- cables
wires = []
bus = []
RAIL_USED = set()
# punto fijo para la punta NEGRA del multimetro: riel GND izquierdo de cada placa, fila 1 (ningun cable lo usa)
for _b in NAMES:
    RAIL_USED.add((canon(_b, -2), 1))
    RAIL_USED.add((canon(_b, -3), 1))      # y el riel de +5 V (punta roja de las pruebas de alimentacion)
# el cuerpo del buzzer (12 mm) tapa los agujeros del riel que tiene al lado
for _d in parts:
    if _d["kind"] == "BUZZER":
        _bn, _side, _col, _row = pos[(_d["ref"], _d["pins"][0]["n"])]
        _rws = [pos[(_d["ref"], q["n"])][3] for q in _d["pins"]]
        for _x in ((-3, -2) if _side == "L" else (12, 13)):
            for _yy in range(min(_rws) - 1, max(_rws) + 2):
                RAIL_USED.add((canon(_bn, _x), _yy))


def hole_for(bn, side, row, net):
    b = BN[bn]
    fr = b.free_holes(side, row)
    c = fr[-1] if side == "L" else fr[0]
    b.cols[(side, row)].add(c)
    b.cells.add((side, c, row))
    return c


def rail_cols(bn, net):
    cfg = rails_of(bn)
    return [c for c in (-3, -2, 12, 13) if cfg[c] == net]


def rail_y(bn, x, y):
    """Agujero libre del riel mas cercano a la fila y (en un agujero cabe un solo cable). Los rieles tienen un hueco cada 6 filas."""
    key = canon(bn, x)
    for d in range(0, ROWS):
        for yy in (y + d, y - d):
            if 0 <= yy < ROWS and yy % 6 != 5 and yy not in (28, 29, 30) and (key, yy) not in RAIL_USED:
                RAIL_USED.add((key, yy))
                return yy
    raise AssertionError("riel lleno")


def pick_rail(bn, side, net):
    """riel de la red mas cercano: el del mismo lado, el del otro lado y, si la placa no lo tiene, el de otra placa."""
    for s in (["L", "R"] if side == "L" else ["R", "L"]):
        for c in ((-3, -2) if s == "L" else (12, 13)):
            if rails_of(bn)[c] == net:
                return bn, c
    best = None
    for o in boards:
        for c in rail_cols(o.name, net):
            dx = abs(offset(o.name) + c - offset(bn))
            if best is None or dx < best[0]:
                best = (dx, o.name, c)
    return best[1], best[2]


for net, strips in nstr.items():
    if net == "NC":
        continue
    if net in POWER:
        for (bn, side, row) in strips:
            c = hole_for(bn, side, row, net)
            rb_, rc_ = pick_rail(bn, side, net)
            wires.append(dict(net=net, a=dict(board=bn, x=c, y=row, hole=""), b=dict(board=rb_, x=rc_, y=rail_y(rb_, rc_, row), hole="", rail=True), kind="power"))
        continue
    pts = list(strips)
    if len(pts) < 2:
        continue
    cap = {t: len(BN[t[0]].free_holes(t[1], t[2])) for t in pts}
    done = [pts[0]]
    todo = pts[1:]
    while todo:
        best = None
        for a in done:
            if cap[a] < 1:
                continue
            for t in todo:
                if cap[t] < 1:
                    continue
                resto = sum(cap[x] for x in done) - 1 + cap[t] - 1      # agujeros que quedan para seguir conectando
                if len(todo) > 1 and resto < 1:
                    continue
                dist = (0 if a[0] == t[0] else 1000) + abs(a[2] - t[2]) + (3 if a[1] != t[1] else 0)
                if best is None or dist < best[0]:
                    best = (dist, a, t)
        assert best, ("no queda agujero libre para el cable de la red", net, pts)
        _, a, t = best
        todo.remove(t)
        done.append(t)
        cap[a] -= 1
        cap[t] -= 1
        ca = hole_for(a[0], a[1], a[2], net)
        ct = hole_for(t[0], t[1], t[2], net)
        wires.append(dict(net=net, a=dict(board=a[0], x=ca, y=a[2], hole=""), b=dict(board=t[0], x=ct, y=t[2], hole=""), kind="signal"))

# ---------------- puentes entre rieles: cada red une todos sus rieles fisicos de izquierda a derecha
for net in ("0", "v5"):
    fis = {}
    for b in boards:
        for c in rail_cols(b.name, net):
            fis.setdefault(canon(b.name, c), (b.name, c))
    ordenados = sorted(fis.values(), key=lambda bc: offset(bc[0]) + bc[1])
    for i in range(1, len(ordenados)):
        (ba, ca), (bb, cb) = ordenados[i - 1], ordenados[i]
        bus.append(dict(net=net, a=dict(board=ba, x=ca, y=rail_y(ba, ca, 56 - 2 * i), hole="", rail=True),
                        b=dict(board=bb, x=cb, y=rail_y(bb, cb, 56 - 2 * i), hole="", rail=True), kind="bus"))


# ---------------- verificacion
def verificar():
    par = {}

    def f(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    strip_net = {}
    netof = {(d["ref"], q["n"]): q["net"] for d in parts for q in d["pins"]}
    for (ref, pin), (bn, side, col, row) in pos.items():
        net = netof[(ref, pin)]
        key = ("S", bn, side, row)
        if key in strip_net and strip_net[key] != net:
            raise AssertionError(("tira mezcla redes", key, strip_net[key], net))
        strip_net[key] = net
        f(key)

    def nodo(e):
        if e["x"] in (-3, -2, 12, 13):
            return ("RAIL",) + canon(e["board"], e["x"])
        return ("S", e["board"], "L" if e["x"] <= 4 else "R", e["y"])
    for w in wires + bus:
        par[f(nodo(w["a"]))] = f(nodo(w["b"]))
    for b in boards:
        for c, n in rails_of(b.name).items():
            k = ("RAIL",) + canon(b.name, c)
            strip_net[k] = n
            f(k)
    groups = defaultdict(set)
    for key, net in strip_net.items():
        groups[f(key)].add(net)
    mezcl = [sorted(v) for v in groups.values() if len(v) > 1]
    por_red = defaultdict(set)
    for key, net in strip_net.items():
        if net != "NC":
            por_red[net].add(f(key))
    return mezcl, {n: len(s) for n, s in por_red.items() if len(s) > 1}


if __name__ == "__main__":
    mez, part = verificar()
    print("placas:", len(boards), "cables:", len(wires), "puentes de riel:", len(bus), "mezcladas:", mez, "redes en varios grupos:", sorted(part)[:20])
    for b in boards:
        print(b.name, b.blocks)
    json.dump(dict(boards=[b.name for b in boards], pos={"%s|%s" % k: v for k, v in pos.items()}, wires=wires, bus=bus),
              open(os.path.join(AQUI, "protoboard_datos.json"), "w"))
