"""Mide los cables del 3D (largo, giros, altura) leyendo datos_r2.json. Uso: py -3.13 medir_cables.py [archivo.json]"""
import json, math, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "datos_r2.json"), encoding="utf-8"))
tot_len = tot_turns = 0; n = 0; alt = []
for w in D["wires"]:
    pts = w.get("pts")
    if not pts: continue
    n += 1
    L = 0; turns = 0; prev = None
    for a, b in zip(pts, pts[1:]):
        d = (b[0] - a[0], b[2] - a[2])
        L += math.hypot(*d)
        if math.hypot(*d) > 1e-6:
            u = (round(d[0] / math.hypot(*d)), round(d[1] / math.hypot(*d)))
            if prev and u != prev: turns += 1
            prev = u
    tot_len += L; tot_turns += turns; alt.append(max(p[1] for p in pts))
print("cables:", n, "| largo total (agujeros):", round(tot_len), "| giros totales:", tot_turns, "| giros por cable:", round(tot_turns / n, 2), "| altura maxima (mm):", round(max(alt), 1))
