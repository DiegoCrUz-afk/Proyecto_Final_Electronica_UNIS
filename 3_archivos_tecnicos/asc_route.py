"""Cableado automatico de esquematicos de LTspice (.asc generados con asc_lib).

Las etiquetas de nodo de los nombres internos de un bloque (th, ref, pk...) se sustituyen por CABLES de verdad:
- las piezas son obstaculos (su caja + margen), los cables ya dibujados y los pines no se pueden pisar;
- dos cables solo se cruzan en perpendicular y nunca en una esquina o extremo (en LTspice un cruce asi no conecta);
- cada red se une con un arbol de cables y conserva UNA etiqueta con su nombre.
Las etiquetas de alimentacion (v5, vm, 0) y las de los pines del bloque (IOPIN) no se tocan.
"""
import heapq
from collections import defaultdict

from asc_lib import rot_pt

G = 8                              # rejilla de ruteo (unidades de LTspice)
POWER = {"0", "v5", "vm", "vin"}


def _bbox(c):
    s = c.s
    pts = []
    for x1, y1, x2, y2 in s.lines:
        pts += [(x1, y1), (x2, y2)]
    for x1, y1, x2, y2 in s.rects:
        pts += [(x1, y1), (x2, y2)]
    for x1, y1, x2, y2 in s.circles:
        pts += [(x1, y1), (x2, y2)]
    for a in s.arcs:
        pts += [(a[0], a[1]), (a[2], a[3])]
    for p in s.pins:
        pts.append((p[0], p[1]))
    if not pts:
        return None
    pts = [rot_pt(x, y, c.rot) for x, y in pts]
    xs = [int(round(c.x + p[0])) for p in pts]
    ys = [int(round(c.y + p[1])) for p in pts]
    return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))


def autoroute(sch, margin=8, extra_blocked=(), only=None, seed=None, max_len=None):
    """Sustituye las etiquetas de nodo internas por cables. Devuelve (redes_unidas, redes_sin_ruta)."""
    iop = {(x, y) for x, y, _ in sch.iopins}
    groups = defaultdict(list)
    for (x, y, name) in sch.flags:
        if only:
            if name not in only:
                continue
        elif name in POWER or (x, y) in iop or name == "0":
            continue
        groups[name].append((x, y))
    groups = {n: sorted(set(p)) for n, p in groups.items() if len(set(p)) >= 2}
    if only:                                          # riel: se unen solo los pines en rejilla, los demas siguen con etiqueta
        groups = {n: [p for p in pp if int(p[0]) % G == 0 and int(p[1]) % G == 0] for n, pp in groups.items()}
        groups = {n: pp for n, pp in groups.items() if len(pp) >= 2}
    else:
        groups = {n: p for n, p in groups.items() if all(int(x) % G == 0 and int(y) % G == 0 for x, y in p)}   # fuera de rejilla: se queda con etiqueta
    if max_len:                                       # redes muy largas: se quedan con etiqueta (un cable de punta a punta de la hoja no se entiende)
        groups = {n: p for n, p in groups.items() if (max(q[0] for q in p) - min(q[0] for q in p)) + (max(q[1] for q in p) - min(q[1] for q in p)) <= max_len}
    if not groups:
        return 0, []
    cell = lambda p: (int(round(p[0])) // G, int(round(p[1])) // G)

    blocked = set()
    for c in sch.comps:
        bb = _bbox(c)
        if not bb:
            continue
        x0, y0, x1, y1 = bb
        for cx in range((x0 - margin) // G, (x1 + margin) // G + 1):
            for cy in range((y0 - margin) // G, (y1 + margin) // G + 1):
                blocked.add((cx, cy))
    orient = defaultdict(set)         # celda -> {'H','V'} de cables ya puestos
    corner = set()                    # extremos y esquinas de cables existentes (no se cruzan)
    for (x1, y1, x2, y2) in sch.wires:
        a, b = cell((x1, y1)), cell((x2, y2))
        corner.add(a)
        corner.add(b)
        if a[1] == b[1]:
            for cx in range(min(a[0], b[0]), max(a[0], b[0]) + 1):
                orient[(cx, a[1])].add("H")
        else:
            for cy in range(min(a[1], b[1]), max(a[1], b[1]) + 1):
                orient[(a[0], cy)].add("V")
    for c in sch.comps:               # los pines nunca se cruzan
        for i in range(1, len(c.s.pins) + 1):
            corner.add(cell(c.pin(i)))
    for (x, y, _) in sch.flags:
        corner.add(cell((x, y)))
    allpts = [cell((x, y)) for g in groups.values() for (x, y) in g]
    xs = [p[0] for p in allpts] + [cell((c.x, c.y))[0] for c in sch.comps]
    ys = [p[1] for p in allpts] + [cell((c.x, c.y))[1] for c in sch.comps]
    xmin, xmax, ymin, ymax = min(xs) - 60, max(xs) + 60, min(ys) - 60, max(ys) + 60
    NB = ((1, 0, "H"), (-1, 0, "H"), (0, 1, "V"), (0, -1, "V"))

    def route(src, goals, net_cells):
        """Dijkstra desde src hasta cualquier celda de goals. Devuelve lista de celdas."""
        pq = [(0.0, 0, src, None)]
        dist = {(src, None): 0.0}
        prev = {}
        cnt = 0
        end = None
        while pq:
            d, _, c, dr = heapq.heappop(pq)
            if dist.get((c, dr), 1e18) < d:
                continue
            if c in goals and c != src:
                end = (c, dr)
                break
            for dx, dy, o in NB:
                n = (c[0] + dx, c[1] + dy)
                if not (xmin <= n[0] <= xmax and ymin <= n[1] <= ymax):
                    continue
                ngoal = n in goals
                if n in blocked and not ngoal and n not in starts and n not in near:
                    continue
                oc = orient.get(n)
                cost = 1.0
                if oc and not ngoal and n not in net_cells:
                    if n in corner or o in oc:
                        continue
                    # cruce perpendicular: hay que seguir recto
                    if dr is not None and (dx, dy) != dr:
                        continue
                    cost += 3.0
                if n in corner and not ngoal and n not in net_cells and n not in starts:
                    continue
                if dr is not None and (dx, dy) != dr:
                    cost += 0.6
                if oc and not ngoal and n not in net_cells:
                    # la siguiente celda tambien debe poder seguir recto: se comprueba al expandir
                    pass
                nd = d + cost
                key = (n, (dx, dy))
                if nd < dist.get(key, 1e18):
                    dist[key] = nd
                    prev[key] = (c, dr)
                    cnt += 1
                    heapq.heappush(pq, (nd, cnt, n, (dx, dy)))
        if end is None:
            return None
        path, cur = [], end
        while cur is not None:
            path.append(cur[0])
            cur = prev.get(cur)
        return path[::-1]

    unidas, fallidas = 0, []
    starts = set()
    near = set()
    # redes pequenas primero
    for name in sorted(groups, key=lambda n: (len(groups[n]), n)):
        pts = [cell(p) for p in groups[name]]
        starts = set(pts)
        near = {(q[0] + dx_, q[1] + dy_) for q in pts for dx_ in range(-2, 3) for dy_ in range(-2, 3)}
        tree = {pts[0]}
        pending = list(pts[1:])
        if seed and name in seed:                     # el riel ya dibujado forma parte del arbol de la red
            tree = set(seed[name])
            pending = list(pts)
        net_cells = set(tree)
        ok = True
        paths = []
        while pending:
            pending.sort(key=lambda p: min(abs(p[0] - t[0]) + abs(p[1] - t[1]) for t in tree))
            p = pending.pop(0)
            path = route(p, set(tree), net_cells)
            if path is None:
                ok = False
                break
            paths.append(path)
            for c in path:
                tree.add(c)
                net_cells.add(c)
        if not ok:
            fallidas.append(name)
            continue
        # registrar y emitir cables
        for path in paths:
            for i in range(len(path) - 1):
                a, b = path[i], path[i + 1]
                o = "H" if a[1] == b[1] else "V"
                orient[a].add(o)
                orient[b].add(o)
            for i in range(1, len(path) - 1):
                if (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]) != (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]):
                    corner.add(path[i])
            corner.add(path[0])
            corner.add(path[-1])
            # fusionar tramos rectos
            i = 0
            while i < len(path) - 1:
                j = i + 1
                d0 = (path[j][0] - path[i][0], path[j][1] - path[i][1])
                while j < len(path) - 1 and (path[j + 1][0] - path[j][0], path[j + 1][1] - path[j][1]) == d0:
                    j += 1
                sch.wires.append((path[i][0] * G, path[i][1] * G, path[j][0] * G, path[j][1] * G))
                i = j
        unidas += 1
        # dejar una sola etiqueta (la primera) para que la red conserve su nombre
        keep = groups[name][0]
        first = True
        nf = []
        for (x, y, nm) in sch.flags:
            if nm == name and (x, y) not in iop and (x, y) in set(groups[name]):
                if (x, y) == keep and first:
                    nf.append((x, y, nm))
                    first = False
                continue
            nf.append((x, y, nm))
        sch.flags = nf
    return unidas, fallidas


def buses(sch, spec=(("v5", "up", 48), ("vm", "up", 96), ("0", "down", 48))):
    """Dibuja un RIEL (linea horizontal) para v5, vm y tierra y une cada pin con cable hasta el riel (ruteo automatico).
    Lo que no se pueda unir queda con su etiqueta. Devuelve {nombre: (pines, redes_sin_ruta)}."""
    res = {}
    boxes = [_bbox(c) for c in sch.comps if _bbox(c)]
    top, bottom = min(b[1] for b in boxes), max(b[3] for b in boxes)
    for name, side, gap in spec:
        pts = sorted({(int(x), int(y)) for (x, y, n) in sch.flags if n == name})
        pts = [p for p in pts if p[0] % G == 0 and p[1] % G == 0]
        if len(pts) < 2:
            continue
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        yb = (top - gap) // G * G if side == "up" else (bottom + gap + G - 1) // G * G
        # el riel no debe tocar cables, pines ni etiquetas
        pinpts = {(int(round(c.pin(i)[0])), int(round(c.pin(i)[1]))) for c in sch.comps for i in range(1, len(c.s.pins) + 1)}
        for _ in range(20):
            clash = any(y == yb and x0 - 8 <= x <= x1 + 8 for (x, y) in pinpts) or any(y == yb and x0 - 8 <= x <= x1 + 8 for (x, y, _) in sch.flags)
            clash = clash or any(b == d == yb and not (max(a, c) < x0 or min(a, c) > x1) for (a, b, c, d) in sch.wires)
            clash = clash or any(a == c and min(b, d) <= yb <= max(b, d) and x0 <= a <= x1 and yb in (b, d) for (a, b, c, d) in sch.wires)
            if not clash:
                break
            yb += -16 if side == "up" else 16
        sch.wires.append((x0 - 16, yb, x1, yb))
        sch.flags.append((x0 - 16, yb, name))
        seed = {(x // G, yb // G) for x in range(x0 - 16, x1 + 1, G)}
        n_ok, mal = autoroute(sch, margin=8, only={name}, seed={name: seed})
        res[name] = (len(pts), mal)
    return res
