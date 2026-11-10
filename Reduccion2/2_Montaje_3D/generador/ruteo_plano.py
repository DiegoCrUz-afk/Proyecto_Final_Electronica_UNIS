"""Ruteo a ras de la placa: cada cable sale de su agujero, corre pegado a la protoboard por agujeros libres (sin pasar por encima de ninguna pieza)
y baja en el otro agujero. Si dos cables se cruzan, uno pasa un poco mas alto (niveles de 1.3 mm). Los cables van en angulo recto.
Si un cable no encuentra camino por el suelo (agujero rodeado de piezas), usa el ruteo con saltos de ruteo_bajo (se cuenta aparte)."""
import heapq
import math
from collections import defaultdict

import generar_protoboard as GP
import ruteo_bajo as RB

BASE0, PASO, MAXN = 2.6, 1.3, 9          # altura del nivel 0, paso entre niveles (mm), niveles probados
GIRO = 2.5                                # costo extra por girar (menos esquinas)
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def huellas(parts, offs):
    ob = {}
    for p in parts:
        t = RB.tope(p)
        if p.get("cells"):                                  # celdas reales que ocupa la pieza (cuerpo, disipador...)
            for (c, r) in p["cells"]:
                ob[(offs[p["board"]] + c, r)] = max(ob.get((offs[p["board"]] + c, r), 0), t)
            continue
        for q in p["pins"]:
            ob[(offs[p["board"]] + q["x"], q["y"])] = max(ob.get((offs[p["board"]] + q["x"], q["y"]), 0), t)
    return ob


def astar(a, b, bloqueado, lim):
    """camino ortogonal de a a b por celdas libres. lim = (x0, x1, y0, y1)."""
    x0, x1, y0, y1 = lim
    h = lambda c: abs(c[0] - b[0]) + abs(c[1] - b[1])
    ini = (a[0], a[1], -1)
    g = {ini: 0.0}
    padre = {}
    pq = [(h(a), 0.0, ini)]
    while pq:
        f, gc, cur = heapq.heappop(pq)
        if gc > g.get(cur, 1e18) + 1e-9:
            continue
        cx, cy, d = cur
        if (cx, cy) == b:
            ruta = [(cx, cy)]
            while cur in padre:
                cur = padre[cur]
                ruta.append((cur[0], cur[1]))
            ruta.reverse()
            return ruta
        for nd, (dx, dy) in enumerate(DIRS):
            nx, ny = cx + dx, cy + dy
            if not (x0 <= nx <= x1 and y0 <= ny <= y1):
                continue
            if (nx, ny) != b and (nx, ny) in bloqueado:
                continue
            ng = gc + 1 + (GIRO if d not in (-1, nd) else 0)
            st = (nx, ny, nd)
            if ng < g.get(st, 1e18) - 1e-9:
                g[st] = ng
                padre[st] = cur
                heapq.heappush(pq, (ng + h((nx, ny)), ng, st))
    return None


def astar_fila(a, fila, bloqueado, lim):
    """camino ortogonal desde a hasta cualquier celda de la fila dada (el pasillo)"""
    x0, x1, y0, y1 = lim
    ini = (a[0], a[1], -1)
    g = {ini: 0.0}
    padre = {}
    pq = [(abs(a[1] - fila), 0.0, ini)]
    while pq:
        f, gc, cur = heapq.heappop(pq)
        if gc > g.get(cur, 1e18) + 1e-9:
            continue
        cx, cy, d = cur
        if cy == fila:
            ruta = [(cx, cy)]
            while cur in padre:
                cur = padre[cur]
                ruta.append((cur[0], cur[1]))
            ruta.reverse()
            return ruta
        for nd, (dx, dy) in enumerate(DIRS):
            nx, ny = cx + dx, cy + dy
            if not (x0 <= nx <= x1 and y0 <= ny <= y1) or (nx, ny) in bloqueado:
                continue
            ng = gc + 1 + (GIRO if d not in (-1, nd) else 0)
            st = (nx, ny, nd)
            if ng < g.get(st, 1e18) - 1e-9:
                g[st] = ng
                padre[st] = cur
                heapq.heappush(pq, (ng + abs(ny - fila), ng, st))
    return None


def esquinas(ruta):
    out = [ruta[0]]
    for i in range(1, len(ruta) - 1):
        a, b, c = ruta[i - 1], ruta[i], ruta[i + 1]
        if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
            out.append(b)
    out.append(ruta[-1])
    return out


def rutear(W, parts, offs):
    ob = huellas(parts, offs)
    pt = lambda e: (offs[e["board"]] + e["x"], e["y"])
    items = []
    for w in W:
        if w["kind"] == "ext":
            continue
        a, b = pt(w["a"]), pt(w["b"])
        items.append((abs(a[0] - b[0]) + abs(a[1] - b[1]), w, a, b))
    items.sort(key=lambda t: t[0])
    extremos = set()
    for _, w, a, b in items:
        extremos.add(a)
        extremos.add(b)
    xs = [c[0] for c in ob] + [e[0] for e in extremos]
    lim = (min(xs) - 4, max(xs) + 30, -5, 68)
    ocup = [set() for _ in range(MAXN)]          # celdas ocupadas por un tramo de cable en cada nivel
    niveles = defaultdict(int)
    nivel_de = {}                                # cable -> nivel
    fin_de = defaultdict(list)                   # celda -> cables que terminan ahi
    for _, w, a, b in items:
        fin_de[a].append(w["i"])
        fin_de[b].append(w["i"])

    rutas = {}                                   # cable -> (a, b, ruta, nivel)

    def poner(w, a, b, ruta, n):
        rutas[w["i"]] = (w, a, b, ruta, n)
        es = esquinas(ruta)
        hgt = BASE0 + PASO * n
        pts = [(a[0], -2.5, a[1]), (a[0], hgt, a[1])] + [(c[0], hgt, c[1]) for c in es[1:-1]] + [(b[0], hgt, b[1]), (b[0], -2.5, b[1])]
        for c in ruta[1:-1]:
            ocup[n].add(c)
        w["h"] = hgt
        nivel_de[w["i"]] = n
        niveles[n] += 1
        guardar(w, pts)

    def guardar(w, pts):
        out = []
        for p_ in pts:
            if not out or math.dist(out[-1], p_) > 1e-6:
                out.append(p_)
        w["pts"] = [[round(p_[0], 3), round(p_[1], 3), round(p_[2], 3)] for p_ in out]

    ext_ini = {pt(w_["a"]) for w_ in W if w_["kind"] == "ext"}     # patas de las que sale un cable a un dispositivo: nadie pasa por encima de su subida

    def bloqueo(a, b, n, estricto):
        hn = BASE0 + PASO * n
        blq = {c for c, t in ob.items() if t + .55 + .3 > hn} | ocup[n] | (ext_ini - {a, b})
        for c, ids in fin_de.items():
            if c in (a, b):
                continue
            # la pata de otro cable sube hasta su altura: se puede pasar por encima solo si ese cable ya esta puesto y es mas bajo
            if estricto or any(nivel_de.get(i, 99) >= n for i in ids):
                blq.add(c)
        return blq
    pendientes = []
    for _, w, a, b in items:
        ruta = None
        for n in range(MAXN):
            ruta = astar(a, b, bloqueo(a, b, n, True), lim)
            if ruta:
                break
        if ruta:
            poner(w, a, b, ruta, n)
        else:
            pendientes.append((w, a, b))
    salto = 0
    for w, a, b in pendientes:                    # segunda vuelta: ahora se conoce la altura de todas las patas ajenas
        ruta = None
        for n in range(MAXN):
            ruta = astar(a, b, bloqueo(a, b, n, False), lim)
            if ruta:
                break
        if ruta:
            poner(w, a, b, ruta, n)
            continue
        mejor = None                              # sin camino por el suelo: salta la pieza (ruteo_bajo), lo mas bajo posible
        for nv in range(0, 20):
            for f in RB.candidatas(a, b, ob)[:10]:
                r = RB.ruta(a, b, nv, f, ob)
                if mejor is None or max(p[1] for p in r) < max(p[1] for p in mejor):
                    mejor = r
            if mejor:
                break
        pts = [tuple(p) for p in mejor]
        w["h"] = max(p[1] for p in pts)
        salto += 1
        guardar(w, pts)
    suelo = len(items) - salto
    # mejora: cada cable alto se vuelve a trazar mas bajo ahora que se conoce el resto (varias vueltas)
    for _vuelta in range(4):
        cambios = 0
        for wid, (w, a, b, ruta, n) in sorted(rutas.items(), key=lambda kv: -kv[1][4]):
            if n == 0:
                continue
            for c in ruta[1:-1]:
                ocup[n].discard(c)
            nivel_de[wid] = 99
            nuevo = None
            for m in range(n):
                r2 = astar(a, b, bloqueo(a, b, m, False), lim)
                if r2:
                    nuevo = (r2, m)
                    break
            if nuevo:
                niveles[n] -= 1
                poner(w, a, b, nuevo[0], nuevo[1])
                cambios += 1
            else:
                for c in ruta[1:-1]:
                    ocup[n].add(c)
                nivel_de[wid] = n
        if not cambios:
            break
    # cables a dispositivos externos: salen de su agujero por el suelo hasta el pasillo de enfrente (filas 63 a 66, sin piezas),
    # corren por el pasillo en su propio carril y nivel y salen de la placa; el resto del camino (en el aire, fuera de las placas) lo traza la plantilla.
    BL = sorted(offs, key=lambda b: offs[b])
    x_ult = offs[BL[-1]] + 14.5 + 4
    x_front = {("FUENTE", "+12V"): offs[BL[0]] + 12 - 24.4, ("FUENTE", "GND"): offs[BL[0]] + 12 - 24.4, ("SW_E", "5V"): offs[BL[0]] + 12 + 5.5, ("SW_E", "E"): offs[BL[0]] + 12 + 10.2,
               ("SW_R", "5V"): offs[BL[0]] + 12 + 25.2, ("SW_R", "RST"): offs[BL[0]] + 12 + 29.9}
    exts = [w for w in W if w["kind"] == "ext"]
    exts.sort(key=lambda w: (w["b"]["ext"], w["b"]["term"]))
    carril_usado = defaultdict(set)                  # (nivel, fila) -> columnas ocupadas por un tramo del pasillo
    sin_pasillo = 0
    for w in exts:
        a = pt(w["a"])
        xe = int(round(x_front.get((w["b"]["ext"], w["b"]["term"]), x_ult)))
        hecho = False
        for n in range(MAXN):
            for lane in (63, 64, 65, 66):
                blq = bloqueo(a, (xe, lane), n, False)
                ruta = astar_fila(a, lane, blq, lim)
                if not ruta:
                    continue
                fin = ruta[-1]
                paso = 1 if xe >= fin[0] else -1
                tramo = [(x, lane) for x in range(fin[0], xe + paso, paso)]
                if any(c in ocup[n] for c in tramo[1:]):
                    continue
                if any(x in carril_usado[(n, lane)] for x, _ in tramo):
                    continue
                for x, _ in tramo:
                    carril_usado[(n, lane)].add(x)
                for c in ruta[1:]:
                    ocup[n].add(c)
                for c in tramo[1:]:
                    ocup[n].add(c)
                full = ruta + tramo[1:]
                es = esquinas(full)
                hgt = BASE0 + PASO * n
                pts = [(a[0], -2.5, a[1]), (a[0], hgt, a[1])] + [(c[0], hgt, c[1]) for c in es[1:]]
                guardar(w, pts)
                w["h"] = hgt
                w["salida"] = True
                hecho = True
                break
            if hecho:
                break
        if not hecho:
            sin_pasillo += 1
    return dict(suelo=suelo, saltos=salto, ext_sin_pasillo=sin_pasillo, niveles=dict(niveles))
