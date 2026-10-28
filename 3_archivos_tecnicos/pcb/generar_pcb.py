"""PCB de una sola cara para el metodo del planchado (toner), a partir de sistema.inc.

Entrada : el mismo netlist que se simula (3_archivos_tecnicos\\sistema.inc) y el reparto en circuitos integrados de
          montaje3d\\generar_montaje3d.py.
Salida  : por cada placa (A, B, C): cobre espejado listo para imprimir (PDF a escala 1:1), vista de componentes,
          lista de taladros y un reporte de verificacion. Todo en pcb\\salida\\.
Metodo  : placa de una cara, agujeros pasantes, pistas de 0.8 mm (1.6 mm en las de corriente), rejilla de 1.27 mm,
          GND como plano de cobre (relleno). Lo que no cabe en pistas se une con un puente de alambre por el lado de
          componentes (se listan). La verificacion comprueba que cada red queda en un solo grupo de cobre/puentes y que
          no hay dos redes tocandose.
Uso     : python generar_pcb.py
"""
import heapq
import os
import sys
import math
import csv
from collections import defaultdict

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "montaje3d"))
import generar_montaje3d as g3

OUT = os.path.join(AQUI, "salida")
CELL = 1.27                  # mm, rejilla de ruteo (media separacion de agujeros)
PITCH = 2.54
W_TRACE, W_WIDE = 0.8, 1.6   # mm
PAD_D, PAD_BIG = 2.0, 2.6    # mm
HOLE_D = 0.9
CLEAR = 0.5                  # mm de separacion minima de cobre (relleno de GND)
PXMM = 20                    # pixeles por mm en los dibujos (508 dpi)
WIDE_NETS = {"vin", "vm", "dm", "sh"}
POUR_NET = "0"
BOARD_W_HOLES = 46           # ancho de las zonas en agujeros (la placa completa mide 38 agujeros = 96.5 mm: cabe en una de 10 x 10 cm)
MARGIN = 3                   # agujeros de margen alrededor de la placa
BOARDS = list('ABCDEFGHIJ')

# ---------------------------------------------------------------- piezas
bl, parts, xs = g3.construir()
ics, usados = g3.secciones_ic(xs)


def bbox(p):
    """(ancho, alto) en agujeros incluyendo el cuerpo."""
    k = p["kind"]
    if k == "IC":
        return p["w"], 4
    return {"R": (5, 2), "RW": (6, 3), "CC": (3, 3), "CE": (4, 4), "D": (5, 2), "DZ": (5, 2), "LED": (3, 3), "Q92": (3, 3), "Q126": (3, 4),
            "MOS": (3, 6), "TRIM": (4, 3), "BUZZER": (5, 5), "TB": (None, 4), "TCRT": (4, 2), "OPTO": (4, 2)}[k]


items = []
for p in parts:
    w, h, pp = g3.formas(p)
    bw, bh = bbox(p)
    if bw is None:
        bw = w + 1
    if p["kind"] == "CE" and p.get("big"):
        bw, bh = 5, 5
    items.append(dict(ref=p["ref"], kind=p["kind"], val=p["val"], blk=p["blk"], bw=bw, bh=bh, ext=p.get("ext"),
                      pins=[(nm, net, dx, dy) for (nm, net), (dx, dy) in zip(p["pins"], pp)], note=p.get("note", "")))
for ic in ics:
    n = g3.IC_PINS[ic["model"]][1]
    pins = []
    for i in range(1, n + 1):
        dx, dy = g3.pos_dip(n, i)
        pins.append((str(i), ic["pins"][i], dx, dy))
    items.append(dict(ref=ic["id"], kind="IC", val=ic["model"], blk=g3.IC_ZONA[ic["id"]], bw=n // 2, bh=4, ext=None, pins=pins, note="", w=n // 2))

ENC_A = {"ENC.OPTO", "ENC.Rled", "ENC.Rpe", "ENC.Ru1", "ENC.Ru2", "ENC.Rpq", "ENC.Rhe", "U3"}
LOG_A = {"LOG.Rpe", "LOG.Rse", "LOG.Cef", "LOG.Rpg", "LOG.Rsg", "LOG.Cgf", "LOG.Rpr", "LOG.Rsr", "LOG.Crf", "LOG.Cpor", "LOG.Rpor", "LOG.Dpor", "U11", "ENT.TBE", "ENT.TBG", "ENT.TBR"}
for it in items:
    z = it["blk"]
    if z == "ENCODER_FV" or it["ref"] == "U12":
        z = "ENC_A" if it["ref"] in ENC_A else "ENC_B"
    if z == "LOGICA" or it["ref"] in ("U8", "U9", "U11"):
        z = "LOG_A" if it["ref"] in LOG_A else "LOG_B"
    it["zone"] = z
PLAN = {"A": ["ENTRADA", "REG5V", "POTENCIA", "ALARMA", "TEMPERATURA"], "B": ["SENSOR_IR", "SOBRECORRIENTE", "LOG_A", "LOG_B"], "C": ["REFVEL", "ERROR_AMP", "PWM_GEN", "ENC_A", "ENC_B"]}
BOARDS = [b for b in BOARDS if b in PLAN]
TITLES = {"A": "PLACA A · Alimentación y potencia", "B": "PLACA B · Sensores, protecciones y lógica", "C": "PLACA C · Control de velocidad"}
ZTITLE = dict((k, v[1]) for k, v in g3.BLOQUES.items())
ZTITLE.update({"ENTRADA": "0 Entrada de 12 V", "LOG_A": "5 Lógica: entradas y antirrebote", "LOG_B": "5 Lógica: pestillo y decisión", "ENC_A": "8 Encoder: sensor y comparador", "ENC_B": "8 Encoder: 555 y filtro F-V"})
ZB = {z: b for b, zl in PLAN.items() for z in zl}
for it in items:
    it["board"] = ZB[it["zone"]]
ZBOARD = {"ENTRADA": "A"}
for k, v in g3.BLOQUES.items():
    ZBOARD[k] = v[2]
ZORDER = g3.ZONAS


# ---------------------------------------------------------------- colocacion
def redes_cruzadas():
    nb = defaultdict(set)
    for it in items:
        for (nm, net, dx, dy) in it["pins"]:
            if net != "NC":
                nb[net].add(it["board"])
    return sorted(n for n, bs in nb.items() if len(bs) > 1), nb


cross, net_boards = redes_cruzadas()
PER_ROW = (BOARD_W_HOLES + 2 * MARGIN - 2 * 1) // 3


def filas_cabecera(b):
    n = sum(1 for x in cross if b in net_boards[x])
    return max(1, -(-n // PER_ROW))


def colocar():
    zonas = {}
    cur = {b: MARGIN + 2 + 3 * filas_cabecera(b) for b in BOARDS}          # deja arriba la franja de puntos de union entre placas
    by_z = defaultdict(list)
    for it in items:
        by_z[it["zone"]].append(it)
    for b in BOARDS:
        for z in PLAN[b]:
            its = by_z[z]
            its.sort(key=lambda it: (0 if it["kind"] == "IC" else 1))
            x0, y0 = MARGIN, cur[b] + 2
            x, y, rowh = x0, y0, 0
            for it in its:
                if x + it["bw"] > x0 + BOARD_W_HOLES:
                    x, y, rowh = x0, y + rowh + 3, 0
                it["x"], it["y"] = x, y
                x += it["bw"] + 2
                rowh = max(rowh, it["bh"])
            zonas[z] = (b, x0 - 1, cur[b], BOARD_W_HOLES + 2, y + rowh + 3 - cur[b])
            cur[b] = y + rowh + 3
    dims = {b: (BOARD_W_HOLES + 2 * MARGIN, cur[b] + MARGIN) for b in BOARDS}
    return zonas, dims


zonas, dims = colocar()
for b in BOARDS:
    if dims[b][1] > 78 or dims[b][0] > 59:
        print("AVISO: la placa %s mide %.0f x %.0f mm (mas que una placa de 15 x 20 cm)" % (b, dims[b][0] * 2.54, dims[b][1] * 2.54))

# ---------------------------------------------------------------- pads
pads = []          # dict(board, ref, pin, net, cx, cy)  (celdas de 1.27 mm)
for it in items:
    for k_, (nm, net, dx, dy) in enumerate(it["pins"]):
        if it["kind"] == "IC":
            pref = [(0, -1), (0, 1)] if dy == 0 else [(0, 1), (0, -1)]
        else:
            pref = [(0, -1), (0, 1)] if k_ % 2 == 0 else [(0, 1), (0, -1)]
        big = it["kind"] in ("TB", "RW", "BUZZER", "MOS", "Q126") or it["ref"] in ("U6",)
        pads.append(dict(board=it["board"], ref=it["ref"], pin=nm, net=net, cx=(it["x"] + dx) * 2, cy=(it["y"] + dy) * 2, big=big, kind=it["kind"], pref=pref + [(1, 0), (-1, 0)]))
for b in BOARDS:
    mine = [n for n in cross if b in net_boards[n]]
    for k, n in enumerate(mine):
        row, col = divmod(k, PER_ROW)
        pads.append(dict(board=b, ref="X", pin=("GND" if n == "0" else "+5V" if n == "v5" else "+12V" if n == "vm" else n), net=n, cx=(MARGIN + 1 + col * 3) * 2, cy=(MARGIN + 1 + row * 3) * 2,
                         big=True, kind="XP", pref=[(0, 1), (1, 0), (-1, 0)]))

# ---------------------------------------------------------------- ruteo
class Board:
    def __init__(self, name):
        self.name = name
        self.wh = dims[name]
        self.W, self.H = self.wh[0] * 2 + 1, self.wh[1] * 2 + 1
        self.own = {}
        self.halo = defaultdict(set)
        self.paths = defaultdict(list)       # net -> lista de caminos [(cx,cy),...]
        self.jumpers = []                    # (net, padA, padB)
        self.pads = [p for p in pads if p["board"] == name]
        self.netid = {}
        for p in self.pads:
            nid = p["net"] if p["net"] != "NC" else "NC:" + p["ref"] + p["pin"]
            p["nid"] = nid
            c = (p["cx"], p["cy"])
            self.own[c] = nid
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                self.halo[(c[0] + d[0], c[1] + d[1])].add(nid)
        # salida reservada de cada pad (2 celdas) para que ninguna pista lo encierre
        cnt = defaultdict(int)
        for p in self.pads:
            if p["net"] != "NC":
                cnt[p["net"]] += 1
        self.stubs = {}
        for p in self.pads:
            if p["net"] == "NC" or cnt[p["net"]] < 2:
                continue
            for d in p["pref"]:
                cells = [(p["cx"] + d[0] * k, p["cy"] + d[1] * k) for k in (1, 2)]
                if all(self.ok(c, p["nid"]) and c not in self.own for c in cells):
                    for c in cells:
                        self.own[c] = p["nid"]
                    self.stubs[(p["cx"], p["cy"])] = [(p["cx"], p["cy"])] + cells
                    break

    def ok(self, c, net):
        if not (0 <= c[0] < self.W and 0 <= c[1] < self.H):
            return False
        o = self.own.get(c)
        if o is not None and o != net:
            return False
        h = self.halo.get(c)
        if h and (h - {net}):
            return False
        return True

    def route(self, net, src, tree, wide):
        """Dijkstra desde src hasta cualquier celda de tree (celdas ya conectadas de la misma red)."""
        pq = [(0.0, 0, src, None)]
        dist = {(src, None): 0.0}
        prev = {}
        cnt = 0
        goal = None
        while pq:
            d, _, c, dr = heapq.heappop(pq)
            if dist.get((c, dr), 1e18) < d:
                continue
            if c in tree and c != src:
                goal = (c, dr)
                break
            for nd in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + nd[0], c[1] + nd[1])
                if not self.ok(n, net):
                    continue
                if wide and any(self.own.get((n[0] + e[0], n[1] + e[1])) not in (None, net) for e in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    continue
                nc = d + 1 + (0.4 if dr is not None and nd != dr else 0.0)
                if nc < dist.get((n, nd), 1e18):
                    dist[(n, nd)] = nc
                    prev[(n, nd)] = (c, dr)
                    cnt += 1
                    heapq.heappush(pq, (nc, cnt, n, nd))
        if goal is None:
            return None
        path = []
        cur = goal
        while cur is not None and cur[0] != src:
            path.append(cur[0])
            cur = prev.get(cur)
        path.append(src)
        return path[::-1]

    def claim(self, net, path, wide):
        for c in path:
            self.own[c] = net
            if wide:
                for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    self.halo[(c[0] + d[0], c[1] + d[1])].add(net)


def mst(points):
    """Prim sobre pads de una red (distancia manhattan)."""
    n = len(points)
    if n < 2:
        return []
    done = {0}
    edges = []
    while len(done) < n:
        best = None
        for i in done:
            for j in range(n):
                if j in done:
                    continue
                d = abs(points[i]["cx"] - points[j]["cx"]) + abs(points[i]["cy"] - points[j]["cy"])
                if best is None or d < best[0]:
                    best = (d, i, j)
        _, i, j = best
        done.add(j)
        edges.append((i, j))
    return edges


def rutear():
    """Ruteo por negociacion de congestion (tipo PathFinder): las redes pueden compartir celdas al principio y se
    van separando con costos de historial; lo que no se logre separar o este bloqueado por pads se une con puente."""
    boards = {b: Board(b) for b in BOARDS}
    stats = {}
    NB = ((1, 0), (-1, 0), (0, 1), (0, -1))
    for b, B in boards.items():
        bynet = defaultdict(list)
        for p in B.pads:
            if p["net"] != "NC":
                bynet[p["net"]].append(p)
        order = sorted((n for n in bynet if len(bynet[n]) > 1),
                       key=lambda n: (-1 if n in WIDE_NETS else 0, len(bynet[n]), sum(abs(p["cx"] - bynet[n][0]["cx"]) + abs(p["cy"] - bynet[n][0]["cy"]) for p in bynet[n])))
        usage = defaultdict(dict)            # celda -> {red: cuantas veces}
        hist = defaultdict(float)
        routes = {}                          # red -> dict(paths, jumpers, cells)
        pf = 0.6

        def pads_hard_ok(c, net):
            if not (0 <= c[0] < B.W and 0 <= c[1] < B.H):
                return False
            o = B.own.get(c)
            if o is not None and o != net:
                return False
            h = B.halo.get(c)
            return not (h and (h - {net}))

        def cell_cost(c, net, wide):
            others = sum(1 for m in usage.get(c, ()) if m != net)
            k = 1.0 + hist.get(c, 0.0) + pf * others
            if wide:
                for d in NB:
                    n2 = (c[0] + d[0], c[1] + d[1])
                    k += 0.5 * pf * sum(1 for m in usage.get(n2, ()) if m != net)
            return k

        def dijkstra(net, src, tree, wide):
            pq = [(0.0, 0, src, None)]
            dist = {(src, None): 0.0}
            prev = {}
            cnt = 0
            goal = None
            while pq:
                d, _, c, dr = heapq.heappop(pq)
                if dist.get((c, dr), 1e18) < d:
                    continue
                if c in tree and c != src:
                    goal = (c, dr)
                    break
                for nd in NB:
                    n = (c[0] + nd[0], c[1] + nd[1])
                    if not pads_hard_ok(n, net):
                        continue
                    if wide and any(B.own.get((n[0] + e[0], n[1] + e[1])) not in (None, net) for e in NB):
                        continue
                    nc = d + cell_cost(n, net, wide) + (0.4 if dr is not None and nd != dr else 0.0)
                    if nc < dist.get((n, nd), 1e18):
                        dist[(n, nd)] = nc
                        prev[(n, nd)] = (c, dr)
                        cnt += 1
                        heapq.heappush(pq, (nc, cnt, n, nd))
            if goal is None:
                return None
            path, cur = [], goal
            while cur is not None and cur[0] != src:
                path.append(cur[0])
                cur = prev.get(cur)
            path.append(src)
            return path[::-1]

        def route_net(n):
            pl = bynet[n]
            wide = n in WIDE_NETS
            tree = set(B.stubs.get((pl[0]["cx"], pl[0]["cy"]), [(pl[0]["cx"], pl[0]["cy"])]))
            connected = [0]
            rest = list(range(1, len(pl)))
            paths, jumpers = [], []
            if len(tree) > 1:
                paths.append(list(B.stubs[(pl[0]["cx"], pl[0]["cy"])]))
            while rest:
                best = None
                for j in rest:
                    for t in tree:
                        d = abs(pl[j]["cx"] - t[0]) + abs(pl[j]["cy"] - t[1])
                        if best is None or d < best[0]:
                            best = (d, j)
                j = best[1]
                rest.remove(j)
                stub = B.stubs.get((pl[j]["cx"], pl[j]["cy"]))
                src = stub[-1] if stub else (pl[j]["cx"], pl[j]["cy"])
                path = dijkstra(n, src, tree, wide)
                if path is None:
                    cand = min(connected, key=lambda i: abs(pl[i]["cx"] - src[0]) + abs(pl[i]["cy"] - src[1]))
                    jumpers.append((n, pl[j], pl[cand]))
                    tree.update(stub or [(pl[j]["cx"], pl[j]["cy"])])
                    if stub:
                        paths.append(list(stub))
                else:
                    paths.append(path)
                    tree.update(path)
                    if stub:
                        paths.append(list(stub))
                        tree.update(stub)
                connected.append(j)
            cells = set()
            for pth in paths:
                cells.update(pth)
            return dict(paths=paths, jumpers=jumpers, cells=cells, wide=wide)

        def reg(n, r):
            for c in r["cells"]:
                usage[c][n] = usage[c].get(n, 0) + 1
                if r["wide"]:
                    for d in NB:
                        n2 = (c[0] + d[0], c[1] + d[1])
                        usage[n2][n] = usage[n2].get(n, 0) + 1

        def unreg(n, r):
            for c in r["cells"]:
                usage[c].pop(n, None)
                if r["wide"]:
                    for d in NB:
                        usage[(c[0] + d[0], c[1] + d[1])].pop(n, None)

        redo = set(order)
        for it in range(int(os.environ.get('PCB_ITERS', '14'))):
            for n in order:
                if n not in redo:
                    continue
                if n in routes:
                    unreg(n, routes[n])
                routes[n] = route_net(n)
                reg(n, routes[n])
            conf = [c for c, u in usage.items() if len(u) > 1]
            if not conf:
                break
            redo = set()
            for c in conf:
                redo.update(usage[c])
            for c in conf:
                hist[c] += 1.0
            pf *= 1.4
        # conflictos que quedan: las redes menos importantes se pasan a puentes con ruteo duro
        conf_nets = set()
        for c, u in usage.items():
            if len(u) > 1:
                conf_nets.update(u)
        fallos = 0
        B.paths.clear()
        B.jumpers = []
        for n in order:
            if n not in conf_nets:
                r = routes[n]
                for pth in r["paths"]:
                    B.claim(n, pth, r["wide"])
                    B.paths[n].append(pth)
                B.jumpers.extend(r["jumpers"])
                fallos += len(r["jumpers"])
        firm = [n for n in order if n in conf_nets]
        for n in firm:
            pl = bynet[n]
            wide = n in WIDE_NETS
            tree = set(B.stubs.get((pl[0]["cx"], pl[0]["cy"]), [(pl[0]["cx"], pl[0]["cy"])]))
            if (pl[0]["cx"], pl[0]["cy"]) in B.stubs:
                B.paths[n].append(list(B.stubs[(pl[0]["cx"], pl[0]["cy"])]))
            connected = [0]
            rest = list(range(1, len(pl)))
            while rest:
                best = None
                for j in rest:
                    for t in tree:
                        d = abs(pl[j]["cx"] - t[0]) + abs(pl[j]["cy"] - t[1])
                        if best is None or d < best[0]:
                            best = (d, j)
                j = best[1]
                rest.remove(j)
                stub = B.stubs.get((pl[j]["cx"], pl[j]["cy"]))
                src = stub[-1] if stub else (pl[j]["cx"], pl[j]["cy"])
                path = B.route(n, src, tree, wide)
                if path is None:
                    cand = min(connected, key=lambda i: abs(pl[i]["cx"] - src[0]) + abs(pl[i]["cy"] - src[1]))
                    B.jumpers.append((n, pl[j], pl[cand]))
                    fallos += 1
                    tree.update(stub or [(pl[j]["cx"], pl[j]["cy"])])
                else:
                    B.claim(n, path, wide)
                    B.paths[n].append(path)
                    tree.update(path)
                if stub:
                    B.paths[n].append(list(stub))
                    tree.update(stub)
                connected.append(j)
        stats[b] = dict(redes=len(order), puentes=fallos, iteraciones=it + 1, conflictos=len(conf_nets))
    return boards, stats


# ---------------------------------------------------------------- dibujo
def mm2px(v):
    return int(round(v * PXMM))


def fuente(sz):
    for f in ("arial.ttf", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            continue
    return ImageFont.load_default()


def cell_mm(c):
    return c[0] * CELL, c[1] * CELL


def copper_masks(B):
    """Devuelve (mascara de cobre que NO es GND, mascara de cobre GND propio: pads+pistas, tamano en px)."""
    Wmm, Hmm = B.wh[0] * PITCH, B.wh[1] * PITCH
    size = (mm2px(Wmm), mm2px(Hmm))
    nong = Image.new("L", size, 0)
    gnd = Image.new("L", size, 0)
    dn, dg = ImageDraw.Draw(nong), ImageDraw.Draw(gnd)

    def disc(d, c, r):
        x, y = c[0] * CELL * PXMM, c[1] * CELL * PXMM
        d.ellipse([x - r * PXMM, y - r * PXMM, x + r * PXMM, y + r * PXMM], fill=255)

    def line(d, a, b, w):
        d.line([a[0] * CELL * PXMM, a[1] * CELL * PXMM, b[0] * CELL * PXMM, b[1] * CELL * PXMM], fill=255, width=max(1, mm2px(w)))
        disc(d, a, w / 2)
        disc(d, b, w / 2)

    for p in B.pads:
        d = dg if p["net"] == POUR_NET else dn
        disc(d, (p["cx"], p["cy"]), (PAD_BIG if p["big"] else PAD_D) / 2)
    for n, paths in B.paths.items():
        w = W_WIDE if n in WIDE_NETS else W_TRACE
        d = dg if n == POUR_NET else dn
        for path in paths:
            for a, b in zip(path, path[1:]):
                line(d, a, b, w)
    return nong, gnd, size


def relleno(B, nong, gnd, size):
    """Plano de GND: todo el cobre libre a CLEAR mm del cobre de otras redes, dentro de la placa con 1 mm de borde."""
    k = mm2px(CLEAR) * 2 + 1
    grown = nong.filter(ImageFilter.MaxFilter(k if k % 2 else k + 1))
    inside = Image.new("L", size, 0)
    ImageDraw.Draw(inside).rectangle([mm2px(1.2), mm2px(1.2), size[0] - mm2px(1.2), size[1] - mm2px(1.2)], fill=255)
    a = np.array(inside) > 0
    a &= ~(np.array(grown) > 0)
    a |= np.array(gnd) > 0
    return a


def flood(mask, seeds, step=2):
    """Region conexa (a escala reducida) alcanzada desde seeds (lista de (x,y) en px)."""
    m = mask[::step, ::step] & mask[1::step, ::step][:mask[::step, ::step].shape[0]] if False else mask[::step, ::step]
    reach = np.zeros_like(m)
    for (x, y) in seeds:
        xx, yy = int(x // step), int(y // step)
        # buscar celda del plano cerca del pad
        for dy in range(-6, 7):
            for dx in range(-6, 7):
                if 0 <= yy + dy < m.shape[0] and 0 <= xx + dx < m.shape[1] and m[yy + dy, xx + dx]:
                    reach[yy + dy, xx + dx] = True
        break
    while True:
        new = reach.copy()
        new[1:] |= reach[:-1]
        new[:-1] |= reach[1:]
        new[:, 1:] |= reach[:, :-1]
        new[:, :-1] |= reach[:, 1:]
        new &= m
        if (new == reach).all():
            break
        reach = new
    return reach


def conectar_gnd(B, plano, size):
    """Comprueba que todos los pads de GND estan en el mismo plano; los que no, se unen con puente."""
    gp = [p for p in B.pads if p["net"] == POUR_NET]
    if len(gp) < 2:
        return 0, np.zeros((1, 1), bool)
    step = 3
    reach = flood(plano, [(gp[0]["cx"] * CELL * PXMM, gp[0]["cy"] * CELL * PXMM)], step)
    aisl = []
    for p in gp:
        x, y = p["cx"] * CELL * PXMM / step, p["cy"] * CELL * PXMM / step
        ok = False
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                yy, xx = int(y + dy), int(x + dx)
                if 0 <= yy < reach.shape[0] and 0 <= xx < reach.shape[1] and reach[yy, xx]:
                    ok = True
        if not ok:
            aisl.append(p)
    ok_pads = [p for p in gp if p not in aisl]
    for p in aisl:
        cand = min(ok_pads, key=lambda q: abs(q["cx"] - p["cx"]) + abs(q["cy"] - p["cy"]))
        B.jumpers.append((POUR_NET, p, cand))
        ok_pads.append(p)
    return len(aisl), reach


def render_cobre(B, plano, nong, gnd, size, espejo=True):
    img = Image.new("L", size, 255)       # blanco = sin tinta = se graba (sale cobre solo donde hay tinta negra)
    arr = np.zeros((size[1], size[0]), np.uint8)
    arr[plano] = 255
    cu = Image.fromarray(arr)
    cu = Image.fromarray(np.maximum(np.array(cu), np.array(nong)))
    cu = Image.fromarray(np.maximum(np.array(cu), np.array(gnd)))
    out = Image.new("L", size, 255)
    out.paste(0, mask=cu)
    d = ImageDraw.Draw(out)
    for p in B.pads:   # marca blanca del taladro en cada pad
        x, y = p["cx"] * CELL * PXMM, p["cy"] * CELL * PXMM
        r = mm2px(0.28)
        d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    # borde de la placa (fino) y cruces de corte
    d.rectangle([0, 0, size[0] - 1, size[1] - 1], outline=0, width=2)
    return ImageOps_mirror(out) if espejo else out


def ImageOps_mirror(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


def render_componentes(B, items_b, size):
    img = Image.new("RGB", size, (252, 250, 240))
    d = ImageDraw.Draw(img)
    f1, f2, f3 = fuente(mm2px(1.9)), fuente(mm2px(1.4)), fuente(mm2px(1.15))
    for it in items_b:
        x0, y0 = it["x"] * PITCH * PXMM, it["y"] * PITCH * PXMM
        xs_ = [it["x"] + dx for (_, _, dx, dy) in it["pins"]]
        ys_ = [it["y"] + dy for (_, _, dx, dy) in it["pins"]]
        bx0, bx1 = (min(xs_) - .6) * PITCH * PXMM, (max(xs_) + .6) * PITCH * PXMM
        by0, by1 = (min(ys_) - .7) * PITCH * PXMM, (max(ys_) + .7) * PITCH * PXMM
        if it["kind"] in ("R", "RW"):
            by0, by1 = (min(ys_) - .35) * PITCH * PXMM, (max(ys_) + .35) * PITCH * PXMM
        d.rectangle([bx0, by0, bx1, by1], outline=(40, 40, 40), width=3)
        if it["kind"] == "IC":
            d.arc([bx0 - 8, (by0 + by1) / 2 - 12, bx0 + 16, (by0 + by1) / 2 + 12], 270, 90, fill=(40, 40, 40), width=3)
        lab = it["ref"].split(".")[-1]
        d.text((bx0, by0 - mm2px(2.2)), lab, fill=(0, 0, 160), font=f1)
        d.text((bx0, by1 + 2), str(it["val"])[:14], fill=(90, 90, 90), font=f2)
        if it["kind"] in ("CE",):
            for (nm, net, dx, dy) in it["pins"]:
                if nm == "+":
                    d.text(((it["x"] + dx) * PITCH * PXMM - 8, (it["y"] + dy) * PITCH * PXMM - mm2px(3.8)), "+", fill=(200, 0, 0), font=f1)
        if it["kind"] in ("D", "DZ"):
            for (nm, net, dx, dy) in it["pins"]:
                if nm == "K":
                    d.text(((it["x"] + dx) * PITCH * PXMM - 6, (it["y"] + dy) * PITCH * PXMM + mm2px(1.8)), "K", fill=(200, 0, 0), font=f2)
        if it["kind"] in ("Q92", "Q126", "MOS", "TRIM", "TCRT", "OPTO"):
            for (nm, net, dx, dy) in it["pins"]:
                d.text(((it["x"] + dx) * PITCH * PXMM - 6, (it["y"] + dy) * PITCH * PXMM + mm2px(1.8)), nm, fill=(0, 100, 0), font=f2)
        if it["kind"] == "IC":
            for (nm, net, dx, dy) in it["pins"]:
                if nm in ("1",):
                    d.text(((it["x"] + dx) * PITCH * PXMM - 6, (it["y"] + dy) * PITCH * PXMM + mm2px(1.9)), "1", fill=(200, 0, 0), font=f2)
    for p in B.pads:
        x, y = p["cx"] * CELL * PXMM, p["cy"] * CELL * PXMM
        r = mm2px((PAD_BIG if p["big"] else PAD_D) / 2)
        gndp = p["net"] == POUR_NET
        d.ellipse([x - r, y - r, x + r, y + r], outline=(30, 80, 190) if gndp else (150, 100, 20), width=3, fill=(170, 200, 245) if gndp else (235, 215, 150))
        r2 = mm2px(HOLE_D / 2)
        d.ellipse([x - r2, y - r2, x + r2, y + r2], fill=(60, 60, 60))
        nom = "GND" if gndp else "+5V" if p["net"] == "v5" else "+12V" if p["net"] == "vm" else "NC" if p["net"] == "NC" else p["net"]
        d.text((x + r + 2, y - mm2px(1.8)), nom, fill=(30, 80, 190) if gndp else (120, 0, 0), font=f3)
        if p["ref"] == "X":
            d.text((x - mm2px(2.5), y - mm2px(6.2)), p["pin"], fill=(0, 0, 0), font=f2)
    for k, (n, a, b) in enumerate(B.jumpers, 1):
        d.line([a["cx"] * CELL * PXMM, a["cy"] * CELL * PXMM, b["cx"] * CELL * PXMM, b["cy"] * CELL * PXMM], fill=(220, 40, 160), width=5)
        mx, my = (a["cx"] + b["cx"]) / 2 * CELL * PXMM, (a["cy"] + b["cy"]) / 2 * CELL * PXMM
        d.text((mx + 4, my - mm2px(2)), "P%d" % k, fill=(220, 40, 160), font=f1)
    d.rectangle([0, 0, size[0] - 1, size[1] - 1], outline=(0, 0, 0), width=3)
    d.text((mm2px(3), mm2px(1.2)), "PLACA %s · vista de componentes (lado de piezas, sin espejo) · magenta = puentes de alambre · azul = GND (tierra) · rojo = nombre de la red" % B.name, fill=(0, 0, 0), font=f1)
    return img


def guia_conexiones(B, path):
    """PDF con la lista de patas: pieza, pata, red y a donde va (para saber que une cada agujero)."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    est = getSampleStyleSheet()
    nom = lambda n: "GND (tierra)" if n == POUR_NET else "+5 V" if n == "v5" else "+12 V" if n == "vm" else n
    por_red = defaultdict(list)
    for p in B.pads:
        por_red[p["net"]].append(p)
    pj = {}
    for k, (n, a, b) in enumerate(B.jumpers, 1):
        pj[(a["ref"], a["pin"])] = pj[(b["ref"], b["pin"])] = "P%d" % k
    filas = [["Pieza", "Pata", "Red", "Se une con"]]
    for p in sorted(B.pads, key=lambda q: (q["ref"], q["pin"])):
        otros = [q for q in por_red[p["net"]] if q is not p]
        if p["net"] == "NC":
            va = "sin conexion (solo soldar la pata)"
        elif p["net"] == POUR_NET:
            va = "toda la zona de cobre de GND (%d patas)" % len(por_red[p["net"]])
        else:
            otros.sort(key=lambda q: abs(q["cx"] - p["cx"]) + abs(q["cy"] - p["cy"]))
            va = ", ".join("%s.%s" % (q["ref"], q["pin"]) for q in otros[:6]) + (" y %d mas" % (len(otros) - 6) if len(otros) > 6 else "")
            if not otros:
                va = "sale de esta placa (conector entre placas)"
        if (p["ref"], p["pin"]) in pj:
            va += "  [puente de alambre %s]" % pj[(p["ref"], p["pin"])]
        filas.append([p["ref"], p["pin"], nom(p["net"]), Paragraph(va, est["BodyText"])])
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    t = Table(filas, colWidths=[90, 40, 90, 310], repeatRows=1)
    t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    enlaces = [[Paragraph("<b>Red</b>", est["BodyText"]), Paragraph("<b>Agujero de esta placa</b>", est["BodyText"]), Paragraph("<b>Se une con cable a</b>", est["BodyText"])]]
    for n in cross:
        if B.name in net_boards[n]:
            otras = ", ".join("placa " + x for x in sorted(net_boards[n]) if x != B.name)
            enlaces.append([nom(n), "agujero rotulado '%s' en la fila de arriba" % nom(n), "el mismo agujero rotulado '%s' de la %s" % (nom(n), otras)])
    te = Table(enlaces, colWidths=[70, 200, 260])
    te.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    doc.build([Paragraph("PLACA %s - a donde va cada pata (cada agujero)" % B.name, est["Heading2"]),
               Paragraph("<b>Agujeros de la fila de arriba:</b> son los puntos para unir las placas entre si con cable (GND, +5 V, +12 V y las senales). Cada uno se conecta a las piezas de esta placa (con pista o con el puente de alambre magenta que sale de el) y, por fuera, con un cable al agujero del mismo nombre de la otra placa.", est["BodyText"]), Spacer(1, 4), te, Spacer(1, 10),
               Paragraph("El cobre que rodea las pistas es GND (tierra). Los puentes P1, P2... son alambres por el lado de piezas (ver vista de componentes).", est["BodyText"]), Spacer(1, 8), t])


def guardar_pdf(im, path, wmm, hmm, extra_title=""):
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    tmp = path + ".png"
    im.convert("L").save(tmp)
    pw, ph = 210 * mm, 297 * mm
    if wmm > 200 or hmm > 287:
        pw, ph = 297 * mm, 420 * mm
    c = canvas.Canvas(path, pagesize=(pw, ph))
    ox, oy = (pw - wmm * mm) / 2, (ph - hmm * mm) / 2
    c.drawImage(tmp, ox, oy, wmm * mm, hmm * mm)
    c.setFont("Helvetica", 7)
    c.drawString(12 * mm, 8 * mm, extra_title + " - imprimir al 100 por ciento (sin ajustar a la pagina). Ancho {:.1f} mm, alto {:.1f} mm.".format(wmm, hmm))
    for (cx_, cy_) in ((ox, oy), (ox + wmm * mm, oy), (ox, oy + hmm * mm), (ox + wmm * mm, oy + hmm * mm)):
        c.setLineWidth(.3)
        c.line(cx_ - 4 * mm, cy_, cx_ - 1 * mm, cy_)
        c.line(cx_ + 1 * mm, cy_, cx_ + 4 * mm, cy_)
        c.line(cx_, cy_ - 4 * mm, cx_, cy_ - 1 * mm)
        c.line(cx_, cy_ + 1 * mm, cx_, cy_ + 4 * mm)
    c.save()
    os.remove(tmp)


# ---------------------------------------------------------------- verificacion
def verificar(B):
    """Union de pads por pistas (celdas contiguas), puentes y plano de GND; cada red = un grupo; sin mezclas."""
    par = {}

    def f(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    def u(a, b):
        par[f(a)] = f(b)
    pad_at = {(p["cx"], p["cy"]): p for p in B.pads}
    for n, paths in B.paths.items():
        for path in paths:
            for a, b in zip(path, path[1:]):
                u(("c", a), ("c", b))
    for c, p in pad_at.items():
        f(("c", c))
        # un pad toca las celdas vecinas de su misma red
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (c[0] + d[0], c[1] + d[1])
            if B.own.get(nb) == p["nid"] and ("c", nb) in par:
                u(("c", c), ("c", nb))
    for n, a, b in B.jumpers:
        u(("c", (a["cx"], a["cy"])), ("c", (b["cx"], b["cy"])))
    grupos = defaultdict(set)
    por_red = defaultdict(set)
    for p in B.pads:
        if p["net"] == "NC":
            continue
        r = f(("c", (p["cx"], p["cy"])))
        grupos[r].add(p["net"])
        por_red[p["net"]].add(r)
    partidas = {n: len(s) for n, s in por_red.items() if len(s) != 1}
    mezcladas = [sorted(v) for v in grupos.values() if len(v) > 1]
    # una celda no puede pertenecer a dos redes
    return partidas, mezcladas


def main():
    os.makedirs(OUT, exist_ok=True)
    boards, stats = rutear()
    reporte = []
    total_puentes = 0
    for b, B in boards.items():
        nong, gnd, size = copper_masks(B)
        plano = relleno(B, nong, gnd, size)
        aisl = 0
        partidas, mezcladas = verificar(B)
        assert not mezcladas, (b, mezcladas)
        assert not partidas, (b, partidas)
        wmm, hmm = B.wh[0] * PITCH, B.wh[1] * PITCH
        cobre = render_cobre(B, plano, nong, gnd, size, espejo=True)
        cobre_n = render_cobre(B, plano, nong, gnd, size, espejo=False)
        comp = render_componentes(B, [it for it in items if it["board"] == b], size)
        cobre.save(os.path.join(OUT, "PLACA_%s_cobre_para_planchado_ESPEJO.png" % b))
        cobre_n.save(os.path.join(OUT, "PLACA_%s_cobre_vista_normal.png" % b))
        comp.save(os.path.join(OUT, "PLACA_%s_componentes.png" % b))
        guardar_pdf(cobre, os.path.join(OUT, "PLACA_%s_cobre_para_planchado_ESPEJO.pdf" % b), wmm, hmm, "PLACA %s cobre ESPEJADO (toner)" % b)
        guardar_pdf(comp, os.path.join(OUT, "PLACA_%s_componentes.pdf" % b), wmm, hmm, "PLACA %s componentes" % b)
        guia_conexiones(B, os.path.join(OUT, "PLACA_%s_guia_de_conexiones.pdf" % b))
        with open(os.path.join(OUT, "PLACA_%s_taladros_y_puentes.csv" % b), "w", newline="", encoding="utf8") as fh:
            w = csv.writer(fh)
            w.writerow(["tipo", "pieza", "pata", "red", "x_mm", "y_mm", "diametro_mm"])
            for p in B.pads:
                w.writerow(["taladro", p["ref"], p["pin"], p["net"], round(p["cx"] * CELL, 2), round(p["cy"] * CELL, 2), 1.0 if p["big"] else 0.9])
            for k, (n, a, c) in enumerate(B.jumpers, 1):
                w.writerow(["puente P%d" % k, "%s.%s -> %s.%s" % (a["ref"], a["pin"], c["ref"], c["pin"]), "", n, round(a["cx"] * CELL, 2), round(a["cy"] * CELL, 2), ""])
        trazas = sum(len(pt) - 1 for ps in B.paths.values() for pt in ps)
        reporte.append("PLACA %s: %.1f x %.1f mm, %d pads, %d redes ruteadas, %d segmentos de pista, %d puentes de alambre (%d de ellos por GND aislado)" % (
            b, wmm, hmm, len(B.pads), stats[b]["redes"], trazas, len(B.jumpers), aisl))
        total_puentes += len(B.jumpers)
    import json
    datos = {"cell_mm": CELL, "pitch_mm": PITCH, "w_trace": W_TRACE, "w_wide": W_WIDE, "pad_d": PAD_D, "pad_big": PAD_BIG, "wide_nets": sorted(WIDE_NETS), "cross": cross,
             "dims": {b_: dims[b_] for b_ in BOARDS}, "zonas": {k: list(v) for k, v in zonas.items()}, "titulos": TITLES, "ztitulos": ZTITLE, "boards_list": BOARDS,
             "items": [dict(ref=it["ref"], kind=it["kind"], val=it["val"], blk=it["blk"], zone=it["zone"], board=it["board"], x=it["x"], y=it["y"], bw=it["bw"], bh=it["bh"], ext=it.get("ext"), note=it.get("note", ""),
                            pins=[dict(n=nm, net=net, x=it["x"] + dx, y=it["y"] + dy) for (nm, net, dx, dy) in it["pins"]]) for it in items],
             "boards": {}}
    for b_, B_ in boards.items():
        datos["boards"][b_] = dict(
            pads=[dict(ref=p_["ref"], pin=p_["pin"], net=p_["net"], cx=p_["cx"], cy=p_["cy"], big=p_["big"]) for p_ in B_.pads],
            tracks=[dict(net=n_, cells=[list(c_) for c_ in pth]) for n_, ps_ in B_.paths.items() for pth in ps_],
            jumpers=[dict(net=n_, a=dict(ref=a_["ref"], pin=a_["pin"], cx=a_["cx"], cy=a_["cy"]), b=dict(ref=c_["ref"], pin=c_["pin"], cx=c_["cx"], cy=c_["cy"])) for n_, a_, c_ in B_.jumpers])
    json.dump(datos, open(os.path.join(OUT, "pcb_datos.json"), "w"))
    reporte.append("VERIFICACION: cada red de cada placa queda en un solo grupo (pistas + puentes + plano de GND) y no hay redes mezcladas.")
    reporte.append("Cruces entre placas (puntos de union): %s" % ", ".join(("GND" if n == "0" else "+5V" if n == "v5" else "+12V" if n == "vm" else n) for n in cross))
    open(os.path.join(OUT, "REPORTE.txt"), "w", encoding="utf8").write("\n".join(reporte) + "\n")
    print("\n".join(reporte))


if __name__ == "__main__":
    main()
