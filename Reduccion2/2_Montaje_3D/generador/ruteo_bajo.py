"""Ruteo de cables pegados a la protoboard: corren bajitos y solo saltan donde hay una pieza.
Cada cable: sube en su agujero, avanza en filas, avanza en columnas, baja. Se prueban las dos formas (filas primero o columnas primero)
y niveles de altura 0,1,2... hasta que no toque a ningun otro cable (distancia minima 1.1 mm entre tubos)."""
import math
import generar_protoboard as GP
from collections import defaultdict

PITCH = 2.54
def tope(p):
    """altura real (mm) de lo mas alto de la pieza, medida en el modelo 3D de la plantilla"""
    k, v = p["kind"], str(p.get("val", ""))
    if k == "R":
        return 4.5
    if k in ("D", "DZ"):
        return 4.2
    if k == "RW":
        return 5.6
    if k == "CC":
        return 7.6 if "µF" in v else 8.4
    if k == "CE":
        try:
            u = float(v.split()[0])
        except ValueError:
            u = 10
        return 14.6 if p.get("big") else 12.5 if u >= 100 else 9.5
    if k == "LED":
        return 10.6
    if k == "BUZZER":
        return 11.0
    if k == "Q92":
        return 7.8
    if k == "Q126":
        return 12.8
    if k == "MOS":
        return 20.6
    if k == "TRIM":
        return 11.3
    if k == "TCRT":
        return 7.9
    if k == "TB":
        return 7.9
    if k == "OPTO":
        return 1.0
    return 7.4          # circuitos integrados

BASE0, PASO, HOLG = 3.2, 1.3, 1.6      # altura del nivel 0, paso entre niveles, holgura sobre una pieza (mm)
EVITAR = set()                         # celdas del opto: los cables lo rodean en vez de pasar por encima
SEP = 1.2                             # separacion minima entre cables (mm, entre ejes)


def celdas_obstaculo(parts, offs):
    """celda global (gx, gy) -> altura de la pieza que la ocupa"""
    ob = {}
    for p in parts:
        h = tope(p)
        xs = [offs[p["board"]] + q["x"] for q in p["pins"]]
        ys = [q["y"] for q in p["pins"]]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        if p["kind"] in GP.FP or p["kind"] == "CE":          # el cuerpo ocupa mas que las patas (huella real)
            f = GP.fp_of(p)
            ex = max(f["cl"], f["cr"])
            x0, x1, y0, y1 = x0 - ex, x1 + ex, y0 - f["rb"], y1 + f["ra"] - 1
        for gx in range(x0, x1 + 1):
            for gy in range(y0, y1 + 1):
                ob[(gx, gy)] = max(ob.get((gx, gy), 0), h)
    return ob


def tramo(p0, p1, base, ob, propios):
    """puntos (gx, h, gy) de un tramo recto horizontal de p0 a p1 a altura 'base', con saltos sobre piezas"""
    (x0, y0), (x1, y1) = p0, p1
    n = int(math.ceil(max(abs(x1 - x0), abs(y1 - y0)) - 1e-9))
    if n == 0:
        return []
    dx, dy = (x1 - x0) / n, (y1 - y0) / n
    celdas = [(x0 + dx * i, y0 + dy * i) for i in range(n + 1)]
    alt = []
    for i, c in enumerate(celdas):
        k = (int(round(c[0])), int(round(c[1])))
        alt.append(0 if (k in propios) else ob.get(k, 0))
    pts = []
    i = 0
    while i <= n:
        if alt[i] > 0 and alt[i] + HOLG > base:
            j = i
            hh = alt[i]
            gap = 0
            k = i
            while k <= n and (alt[k] > 0 or gap < 2):
                if alt[k] > 0:
                    j = k
                    hh = max(hh, alt[k])
                    gap = 0
                else:
                    gap += 1
                k += 1
            hh = max(base, hh + HOLG)
            i0, j0 = max(0, i - 1), min(n, j + 1)          # el cable sube y baja una celda antes/despues: el cuerpo ocupa casi toda su celda
            a = (x0 + dx * i0, y0 + dy * i0)
            b = (x0 + dx * j0, y0 + dy * j0)
            pts += [(a[0], base, a[1]), (a[0], hh, a[1]), (b[0], hh, b[1]), (b[0], base, b[1])]
            i = j + 1
        else:
            i += 1
    return pts


def esquinas(a, b, forma):
    (ax, ay), (bx, by) = a, b
    t = forma[0]
    if t == "L0":
        return [a, (ax, by), b]
    if t == "L1":
        return [a, (bx, ay), b]
    if t == "Zx":
        return [a, (forma[1], ay), (forma[1], by), b]
    return [a, (ax, forma[1]), (bx, forma[1]), b]


def ruta(a, b, nivel, forma, ob):
    base = BASE0 + PASO * nivel
    cs = esquinas(a, b, forma)
    propios = {(int(round(a[0])), int(round(a[1]))), (int(round(b[0])), int(round(b[1])))}
    pts = [(a[0], -2.5, a[1]), (a[0], base, a[1])]
    for c0, c1 in zip(cs, cs[1:]):
        if abs(c0[0] - c1[0]) + abs(c0[1] - c1[1]) < 1e-9:
            continue
        pts += tramo(c0, c1, base, ob, propios)
        pts += [(c1[0], base, c1[1])]
    pts += [(b[0], base, b[1]), (b[0], -2.5, b[1])]
    out = []
    for p in pts:
        if not out or math.dist(out[-1], p) > 1e-6:
            out.append(p)
    return out


def costo(a, b, forma, ob):
    """cuantas celdas con algo debajo recorre (sin contar sus propias patas) + un poco por largo"""
    propios = {(int(round(a[0])), int(round(a[1]))), (int(round(b[0])), int(round(b[1])))}
    cs = esquinas(a, b, forma)
    c = 0.0
    for c0, c1 in zip(cs, cs[1:]):
        n = int(math.ceil(max(abs(c1[0] - c0[0]), abs(c1[1] - c0[1])) - 1e-9))
        for k in range(n + 1):
            t = k / n if n else 0
            cell = (int(round(c0[0] + (c1[0] - c0[0]) * t)), int(round(c0[1] + (c1[1] - c0[1]) * t)))
            if cell not in propios and ob.get(cell, 0) > 0:
                c += 1
            if cell not in propios and cell in EVITAR:
                c += 40
        c += n * 0.02
    return c + 0.3 * (len(cs) - 2)


def candidatas(a, b, ob, k=30):
    (ax, ay), (bx, by) = a, b
    fs = [("L0",), ("L1",)]
    x0, x1 = int(min(ax, bx)) - 2, int(max(ax, bx)) + 2
    y0, y1 = int(min(ay, by)) - 2, int(max(ay, by)) + 2
    for mx in range(x0, x1 + 1, max(1, (x1 - x0) // 80)):
        fs.append(("Zx", mx))
    for my in range(y0, y1 + 1, max(1, (y1 - y0) // 80)):
        fs.append(("Zy", my))
    fs.sort(key=lambda f: costo(a, b, f, ob))
    return fs[:k]


def muestras(pts):
    """(gx, gy, h_lo, h_hi) cada ~0.3 de recorrido"""
    s = []
    for p, q in zip(pts, pts[1:]):
        dh = math.hypot(q[0] - p[0], q[2] - p[2])
        if dh < 1e-6:
            s.append((p[0], p[2], min(p[1], q[1]), max(p[1], q[1])))
        else:
            n = max(1, int(dh / .3))
            for i in range(n + 1):
                t = i / n
                h = p[1] + (q[1] - p[1]) * t
                s.append((p[0] + (q[0] - p[0]) * t, p[2] + (q[2] - p[2]) * t, h, h))
    return s


class Ocupacion:
    def __init__(self):
        self.celda = defaultdict(list)

    def choca(self, ms, ign=None):
        for (x, y, lo, hi) in ms:
            cx, cy = int(x // .6), int(y // .6)
            for ix in (cx - 1, cx, cx + 1):
                for iy in (cy - 1, cy, cy + 1):
                    for (ox, oy, olo, ohi, oid) in self.celda.get((ix, iy), ()):
                        if oid != ign and (ox - x) ** 2 + (oy - y) ** 2 < (.5) ** 2 and lo - SEP < ohi and olo - SEP < hi:
                            return True
        return False

    def cuenta(self, ms, ign=None):
        n = 0
        for (x, y, lo, hi) in ms:
            cx, cy = int(x // .6), int(y // .6)
            hit = False
            for ix in (cx - 1, cx, cx + 1):
                for iy in (cy - 1, cy, cy + 1):
                    for (ox, oy, olo, ohi, oid) in self.celda.get((ix, iy), ()):
                        if oid != ign and (ox - x) ** 2 + (oy - y) ** 2 < .25 and lo - SEP < ohi and olo - SEP < hi:
                            hit = True
            n += hit
        return n

    def poner(self, ms, wid=None):
        for (x, y, lo, hi) in ms:
            self.celda[(int(x // .6), int(y // .6))].append((x, y, lo, hi, wid))

    def quitar(self, ms, wid):
        for k in {(int(x // .6), int(y // .6)) for (x, y, lo, hi) in ms}:
            self.celda[k] = [o for o in self.celda[k] if o[4] != wid]


def rutear(W, parts, offs):
    ob0 = celdas_obstaculo(parts, offs)
    EVITAR.clear()
    for p in parts:
        if p["kind"] == "OPTO":
            xs = [offs[p["board"]] + q["x"] for q in p["pins"]]
            ys = [q["y"] for q in p["pins"]]
            for gx in range(min(xs), max(xs) + 1):
                for gy in range(min(ys), max(ys) + 1):
                    EVITAR.add((gx, gy))
    def pt(e, net, kind):
        gy = e["y"] + ((0 if net == "0" else 6 if net == "v5" else 12) / PITCH if kind == "bus" else 0)
        return (offs[e["board"]] + e["x"], gy)
    items = []
    for w in W:
        if w["kind"] == "ext":
            continue
        a, b = pt(w["a"], w["net"], w["kind"]), pt(w["b"], w["net"], w["kind"])
        items.append((abs(a[0] - b[0]) + abs(a[1] - b[1]), w, a, b))
    items.sort(key=lambda t: t[0])
    n = len(items)
    celda = lambda e: (int(round(e[0])), int(round(e[1])))
    EP = 14.0                                  # altura que se asume al principio para la pata de otro cable al pasar por encima de su agujero

    def con_patas(ep):
        ob = dict(ob0)
        for k, h in ep.items():
            ob[k] = max(ob.get(k, 0), h)
        return ob

    ep0 = {}
    for _, w, a_, b_ in items:
        for e in (a_, b_):
            ep0[celda(e)] = EP
    ob = con_patas(ep0)
    cands = [candidatas(a_, b_, ob) for (_, w, a_, b_) in items]
    oc = Ocupacion()
    res = [None] * n                           # i -> (nivel, ruta, muestras)
    # 1) primera pasada: del cable mas corto al mas largo, cada uno al nivel de altura mas bajo que no toque a los anteriores
    for i in range(n):
        _, w, a_, b_ = items[i]
        elegido = None
        for nivel in range(0, 30):
            for f in cands[i]:
                r = ruta(a_, b_, nivel, f, ob)
                ms = muestras(r)
                if not oc.choca(ms):
                    elegido = (nivel, r, ms)
                    break
            if elegido:
                break
        if not elegido:
            mejor = None
            for nivel in range(0, 16):
                for f in cands[i][:12]:
                    r = ruta(a_, b_, nivel, f, ob)
                    ms = muestras(r)
                    c = oc.cuenta(ms)
                    if mejor is None or c < mejor[0]:
                        mejor = (c, nivel, r, ms)
            elegido = (mejor[1], mejor[2], mejor[3])
        res[i] = elegido
        oc.poner(elegido[2], i)

    # 2) reparar: la pata de un cable sube hasta su altura real, asi que otro que pase por encima de su agujero debe saltar mas alto.
    #    Cada cable que aun toca a otro se vuelve a trazar con las alturas reales de las patas de todos los demas.
    def patas_reales(excepto):
        ep = {}
        for _, w, a_, b_ in items:
            for e in (a_, b_):
                ep[celda(e)] = EP
        for j in range(n):
            if j == excepto:
                continue
            base = BASE0 + PASO * res[j][0]
            for e in (items[j][2], items[j][3]):
                k = celda(e)
                ep[k] = max(ep.get(k, EP), base)
        return ep

    for ronda in range(12):
        malos = [i for i in range(n) if oc.cuenta(res[i][2], i) > 0]
        if not malos:
            break
        mejoro = False
        for i in malos:
            _, w, a_, b_ = items[i]
            if oc.cuenta(res[i][2], i) == 0:
                continue
            c_ant = oc.cuenta(res[i][2], i)
            oc.quitar(res[i][2], i)
            obi = con_patas(patas_reales(i))
            cs = candidatas(a_, b_, obi, 60)
            mejor = None
            for nivel in range(0, 34):
                for f in cs:
                    r = ruta(a_, b_, nivel, f, obi)
                    ms = muestras(r)
                    c = oc.cuenta(ms, i)
                    if mejor is None or c < mejor[0]:
                        mejor = (c, nivel, r, ms)
                    if c == 0:
                        break
                if mejor[0] == 0:
                    break
            if mejor[0] < c_ant:
                res[i] = (mejor[1], mejor[2], mejor[3])
                mejoro = True
            oc.poner(res[i][2], i)
        if not mejoro:
            break

    malos = sum(1 for i in range(n) if oc.cuenta(res[i][2], i) > 0)
    mx = max(r[0] for r in res)
    for i in range(n):
        w = items[i][1]
        w["pts"] = [[round(p[0], 3), round(p[1], 2), round(p[2], 3)] for p in res[i][1]]
        w["h"] = BASE0 + PASO * res[i][0]
    j = 0
    for w in W:
        if w["kind"] == "ext":
            w["h"] = 17 + 1.5 * (j % 6)
            j += 1
    return dict(niveles=mx + 1, sin_lugar=malos, altura_max=round(BASE0 + PASO * mx, 1))
