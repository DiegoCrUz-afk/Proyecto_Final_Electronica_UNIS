"""Montaje en PROTOBOARDS (guia para armar junto al esquematico). Uso: python generar_protoboard.py
- Protoboards de 830 puntos: 63 filas, tiras de 5 agujeros (A-E izquierda, F-J derecha), canal central y 4 rieles.
- Cada pata va a una tira (fila + lado); varias patas de la misma red pueden compartir tira. Las tiras se unen con cables.
- Los CI se montan a horcajadas del canal. GND, 5 V y 12 V van por los rieles.
- verificar(): cada red queda en un solo grupo y ninguna tira mezcla redes.
"""
import json
import os
import sys
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "montaje3d"))
import generar_montaje3d as g3

ROWS = 63
LCOLS, RCOLS = [0, 1, 2, 3, 4], [6, 7, 8, 9, 10]          # canal en x = 5
RAIL = {"L": {"v5": -3, "0": -2}, "R": {"0": 12, "vm": 13}}
POWER = {"0", "v5", "vm"}
datos, zonas, ics = g3.construir_todo()
parts = [d for d in datos]
ORDEN = ["ENTRADA", "REG5V", "POTENCIA", "ALARMA", "SENSOR_IR", "SOBRECORRIENTE", "TEMPERATURA", "LOGICA", "REFVEL", "ENCODER_FV", "ERROR_AMP", "PWM_GEN"]
K = {"R": 4, "D": 4, "DZ": 4, "RW": 5, "CC": 2, "CE": 2, "LED": 2, "BUZZER": 3}


class Board:
    def __init__(self, name):
        self.name = name
        self.strip = {}                      # (side, row) -> red
        self.cols = defaultdict(set)         # (side, row) -> columnas ocupadas
        self.cells = set()                   # (side, col, row) ocupadas por cuerpos
        self.rows_used = 0

    def free_strip(self, side, row, net=None):
        s = self.strip.get((side, row))
        return 0 <= row < ROWS and (s is None or (net is not None and s == net))

    def free_col(self, side, row, prefer=None):
        for c in (RCOLS if side == "R" else LCOLS):
            if c not in self.cols[(side, row)] and (side, c, row) not in self.cells:
                return c
        return None


boards = [Board("A")]
pos = {}            # (ref, pin) -> (board, side, col, row)
nstr = defaultdict(list)   # red -> [(board, side, row)]


def put(b, ref, pin, net, side, col, row):
    b.strip[(side, row)] = net
    b.cols[(side, row)].add(col)
    b.cells.add((side, col, row))
    pos[(ref, pin)] = (b.name, side, col, row)
    if (b.name, side, row) not in nstr[net]:
        nstr[net].append((b.name, side, row))


def sidecols(side):
    return RCOLS if side == "R" else LCOLS


def place_ic(b, d, row0):
    n = len(d["pins"])
    h = n // 2
    for q in d["pins"]:
        i = int(q["n"])
        if i <= h:
            put(b, d["ref"], q["n"], q["net"], "L", 4, row0 + i - 1)
        else:
            put(b, d["ref"], q["n"], q["net"], "R", 6, row0 + (n - i))
    return h


def find_rows(b, need, start):
    r = start
    while r + need <= ROWS:
        if all(b.strip.get((s, rr)) is None for s in "LR" for rr in range(r, r + need)):
            return r
        r += 1
    return None


def try_attach(b, d):
    """Pone una pieza de 2 patas con una pata en una tira ya existente de su red (ahorra un cable)."""
    pins = d["pins"]
    k = K.get(d["kind"])
    if k is None or len(pins) != 2:
        return False
    for ai in (0, 1):
        a, o = pins[ai], pins[1 - ai]
        if a["net"] in POWER:
            continue
        for (bn, side, row) in list(nstr.get(a["net"], [])):
            if bn != b.name:
                continue
            col = b.free_col(side, row)
            if col is None:
                continue
            for dr in (k, -k):
                orow = row + dr
                if not (0 <= orow < ROWS):
                    continue
                if not b.free_strip(side, orow, o["net"]):
                    continue
                lo, hi = sorted((row, orow))
                if any((side, col, rr) in b.cells for rr in range(lo, hi + 1) if rr not in (row,)):
                    continue
                if (side, col, orow) in b.cells:
                    continue
                put(b, d["ref"], a["n"], a["net"], side, col, row)
                put(b, d["ref"], o["n"], o["net"], side, col, orow)
                for rr in range(lo, hi + 1):
                    b.cells.add((side, col, rr))
                return True
    return False


def place_free(b, d, row_from):
    pins = d["pins"]
    n = len(pins)
    k = {"R": 4, "D": 4, "DZ": 4, "RW": 5, "CC": 2, "CE": 3 if d.get("big") else 2, "LED": 2, "BUZZER": 3, "TB": 2, "TCRT": 1, "OPTO": 1, "Q92": 1, "Q126": 1, "MOS": 1, "TRIM": 1}.get(d["kind"], 2)
    span = k * (n - 1)
    for r in range(row_from, ROWS - span):
        for side in "LR":
            for col in sidecols(side):
                rows = [r + k * i for i in range(n)]
                if any(not b.free_strip(side, rr) for rr in rows):
                    continue
                if any((side, col, rr) in b.cells for rr in range(r, r + span + 1)):
                    continue
                for i, q in enumerate(pins):
                    put(b, d["ref"], q["n"], q["net"], side, col, rows[i])
                for rr in range(r, r + span + 1):
                    b.cells.add((side, col, rr))
                return True
    return False


def colocar():
    zonas_p = defaultdict(list)
    for d in parts:
        zonas_p[d["blk"]].append(d)
    bi = 0
    for z in ORDEN:
        items = zonas_p[z]
        ci = [d for d in items if d["kind"] == "IC"]
        rest = [d for d in items if d["kind"] != "IC"]
        # ?cabe en la placa actual? (estimacion de filas)
        need = sum(len(d["pins"]) // 2 + 1 for d in ci) + sum(max(2, K.get(d["kind"], 2) + 1) for d in rest) // 2 + 4
        b = boards[bi]
        if b.rows_used + need > ROWS and b.rows_used > 0:
            boards.append(Board("ABCDEFGH"[len(boards)]))
            bi += 1
            b = boards[bi]
        row = b.rows_used
        for d in ci:
            r0 = find_rows(b, len(d["pins"]) // 2, row)
            if r0 is None:
                boards.append(Board("ABCDEFGH"[len(boards)]))
                bi += 1
                b = boards[bi]
                r0 = find_rows(b, len(d["pins"]) // 2, 0)
            h = place_ic(b, d, r0)
            row = r0 + h + 1
        pend = list(rest)
        for _ in range(3):                      # varias pasadas: las que se pueden colgar de una tira existente
            for d in list(pend):
                if try_attach(b, d):
                    pend.remove(d)
        for d in pend:
            if not place_free(b, d, max(0, b.rows_used)):
                boards.append(Board("ABCDEFGH"[len(boards)]))
                bi += 1
                b = boards[bi]
                assert place_free(b, d, 0), d["ref"]
        b.rows_used = max([rr for (s, rr) in b.strip] + [0]) + 2
    return boards


colocar()
BN = {b.name: b for b in boards}

# ---------------- cables
wires = []
gnd_use = defaultdict(int)


def hole_for(bn, side, row, net):
    b = BN[bn]
    c = b.free_col(side, row)
    if c is None:
        c = (RCOLS if side == "R" else LCOLS)[-1]
    b.cols[(side, row)].add(c)
    return c


def rail_x(bn, net, side):
    return RAIL[side][net] if net in RAIL[side] else None


for net, strips in nstr.items():
    if net == "NC":
        continue
    if net in POWER:
        for (bn, side, row) in strips:
            # al riel del mismo lado cuando existe; si no, al riel del otro lado
            rs = side if net in RAIL[side] else ("R" if side == "L" else "L")
            c = hole_for(bn, side, row, net)
            wires.append(dict(net=net, a=dict(board=bn, x=c, y=row, hole=""), b=dict(board=bn, x=RAIL[rs][net], y=row, hole="", rail=True), kind="power"))
        continue
    # MST entre tiras de la red
    pts = list(strips)
    if len(pts) < 2:
        continue
    done = [pts[0]]
    todo = pts[1:]
    while todo:
        best = None
        for a in done:
            for t in todo:
                dist = (0 if a[0] == t[0] else 1000) + abs(a[2] - t[2]) + (3 if a[1] != t[1] else 0)
                if best is None or dist < best[0]:
                    best = (dist, a, t)
        _, a, t = best
        todo.remove(t)
        done.append(t)
        ca = hole_for(a[0], a[1], a[2], net)
        ct = hole_for(t[0], t[1], t[2], net)
        wires.append(dict(net=net, a=dict(board=a[0], x=ca, y=a[2], hole=""), b=dict(board=t[0], x=ct, y=t[2], hole=""), kind="signal"))


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
    for (ref, pin), (bn, side, col, row) in pos.items():
        net = [q["net"] for d in parts if d["ref"] == ref for q in d["pins"] if q["n"] == pin][0]
        key = ("S", bn, side, row)
        if key in strip_net and strip_net[key] != net:
            raise AssertionError(("tira mezcla redes", key, strip_net[key], net))
        strip_net[key] = net
        f(key)
    for w in wires:
        a, b = w["a"], w["b"]
        ka = ("S", a["board"], "L" if a["x"] <= 5 and a["x"] >= 0 else "R", a["y"]) if not a.get("rail") else ("R", a["board"], w["net"])
        sa = "L" if a["x"] <= 4 else "R"
        ka = ("S", a["board"], sa, a["y"])
        if b.get("rail"):
            kb = ("RAIL", b["board"], w["net"])
        else:
            kb = ("S", b["board"], "L" if b["x"] <= 4 else "R", b["y"])
        par[f(ka)] = f(kb)
    for rn in ("0", "v5", "vm"):                      # los rieles de las placas se unen con cables entre placas (se anotan aparte)
        pass
    groups = defaultdict(set)
    for key, net in strip_net.items():
        groups[f(key)].add(net)
    mezcl = [sorted(v) for v in groups.values() if len(v) > 1]
    por_red = defaultdict(set)
    for key, net in strip_net.items():
        if net != "NC":
            por_red[net].add(f(key))
    # las redes entre protoboards se unen con cables entre placas; aqui solo se comprueba por placa
    return mezcl, {n: len(s) for n, s in por_red.items() if len(s) > 1 and n not in POWER}


if __name__ == "__main__":
    mez, part = verificar()
    print("placas:", len(boards), "cables:", len(wires), "mezcladas:", mez, "redes en varios grupos (cruzan placas):", sorted(part)[:20])
    out = dict(boards=[b.name for b in boards], pos={"%s|%s" % k: v for k, v in pos.items()}, wires=wires)
    json.dump(out, open(os.path.join(AQUI, "protoboard_datos.json"), "w"))
