"""Tabla de verdad, mapas de Karnaugh y comprobacion en LTspice de la logica (bloque 5).
Salidas en 9_Entregables_profesor\\02_Simulacion_y_capturas\\logica
Uso: py -3.13 logica_tabla.py
"""
import itertools
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
TEC = os.path.dirname(AQUI)
RAIZ = os.path.dirname(TEC)
sys.path.insert(0, TEC)
from simlib import run, read_raw, log_errors  # noqa: E402

OUT = os.path.join(RAIZ, "9_Entregables_profesor", "02_Simulacion_y_capturas", "logica")
os.makedirs(OUT, exist_ok=True)


def modelo(E, G, P, F):
    M = int(E and G and not F)
    return dict(M=M, N=int(M and not P), L=int(M and P), A=int(F))


# ---------------------------------------------------------------- LTspice: 16 combinaciones
SEG = 0.08
combos = list(itertools.product([0, 1], repeat=4))   # E G P F
pw = {"e": [], "g": [], "p": [], "r": [], "fc": []}
for i, (E, G, P, F) in enumerate(combos):
    t0 = i * SEG
    for k, v in (("e", E), ("g", G), ("p", P)):
        pw[k].append((t0, 5 * v))
    # reset de 0 a 15 ms (borra la falla anterior), falla de 20 a 25 ms si F = 1
    pw["r"] += [(t0, 5), (t0 + 0.015, 0)]
    pw["fc"] += [(t0, 0), (t0 + 0.02, 5 * F), (t0 + 0.025, 0)]


def pwl(nombre, lista):
    pts, prev = [(0, lista[0][1])], lista[0][1]
    for t, v in lista[1:]:
        if v != prev:
            pts += [(t - 1e-6, prev), (t, v)]
            prev = v
    return "V%s %s 0 PWL(%s)" % (nombre, nombre + "_n", " ".join("%.6f %.2f" % q for q in pts))


deck = [
    "* prueba de la logica: 16 combinaciones E G P F",
    '.include "%s"' % os.path.join(TEC, "modelos.inc").replace("\\", "/"),
    '.include "%s"' % os.path.join(TEC, "sistema.inc").replace("\\", "/"),
    "Vv5 v5 0 5",
    pwl("e", pw["e"]), pwl("g", pw["g"]), pwl("p", pw["p"]), pwl("r", pw["r"]), pwl("fc", pw["fc"]),
    "Re e_n ein 100", "Rg g_n gin 100", "Rr r_n rin 100", "Rp p_n p 100",
    ".model SWF SW(Ron=10 Roff=1G Vt=2.5 Vh=0.1)",
    "Sf setn 0 fc_n 0 SWF",
    "XL v5 ein gin rin p setn m n l f fn LOGICA",
    ".tran 0 %.3f 0 20u" % (SEG * 16),
    ".end",
]
cir = os.path.join(OUT, "prueba_logica_16.cir")
open(cir, "w", encoding="utf-8").write("\n".join(deck) + "\n")
base = run(cir)
err = log_errors(base)
d, _ = read_raw(base + ".raw")
t = d["time"]
import numpy as np  # noqa: E402

filas = []
ok_todo = True
for i, (E, G, P, F) in enumerate(combos):
    tm = i * SEG + SEG - 0.004
    j = int(np.argmin(abs(t - tm)))
    sim = {k: int(d["V(%s)" % k.lower()][j] > 2.5) for k in "MNL"}
    sim["A"] = int(d["V(f)"][j] > 2.5)
    esp = modelo(E, G, P, F)
    ok = all(sim[k] == esp[k] for k in "MNLA")
    ok_todo &= ok
    filas.append(dict(E=E, G=G, P=P, F=F, esperado=esp, simulado=sim, ok=ok))

json.dump(dict(filas=filas, errores_ltspice=err, todo_ok=ok_todo),
          open(os.path.join(OUT, "resultado_logica.json"), "w", encoding="utf-8"), indent=1)
print("16 combinaciones, todas OK:", ok_todo, "| errores LTspice:", err)
for f in filas:
    print(f["E"], f["G"], f["P"], f["F"], "->", f["esperado"], f["simulado"], "OK" if f["ok"] else "FALLA")

# grafica de la simulacion
fig, ax = plt.subplots(7, 1, figsize=(10, 7.5), sharex=True)
for a, (nom, key) in zip(ax, [("E", "V(ein)"), ("G", "V(gin)"), ("P", "V(p)"), ("F (setn)", "V(setn)"),
                              ("M", "V(m)"), ("N", "V(n)"), ("L", "V(l)")]):
    a.plot(t * 1000, d[key], lw=1)
    a.set_ylabel(nom, rotation=0, ha="right", va="center")
    a.set_ylim(-0.5, 5.8)
    a.set_yticks([0, 5])
    a.grid(alpha=.3)
ax[-1].set_xlabel("tiempo (ms): 16 combinaciones de 80 ms, en orden binario EGPF = 0000 ... 1111")
for k in range(17):
    for a in ax:
        a.axvline(k * SEG * 1000, color="#888", lw=.4)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "logica_16_combinaciones.png"), dpi=130)
plt.close(fig)


# ---------------------------------------------------------------- Karnaugh
ordenGray = [(0, 0), (0, 1), (1, 1), (1, 0)]    # se lee (bit alto, bit bajo)


def karnaugh(nombre, f, grupos, titulo, archivo):
    """f(E,G,P,F) -> 0/1; filas = EG, columnas = PF. grupos: lista de (fila0, col0, nfilas, ncols, color)"""
    fig, ax = plt.subplots(figsize=(4.4, 3.7))
    for r, (E, G) in enumerate(ordenGray):
        for c, (P, F) in enumerate(ordenGray):
            ax.add_patch(Rectangle((c, 3 - r), 1, 1, fill=False, lw=1, ec="#222"))
            ax.text(c + .5, 3 - r + .5, str(f(E, G, P, F)), ha="center", va="center", fontsize=15)
    for (r0, c0, nr, nc, col) in grupos:
        for (rr, cc, w, h) in _trozos(r0, c0, nr, nc):
            ax.add_patch(Rectangle((cc + .08, 3 - (rr + h - 1) + .08), w - .16, h - .16, fill=False, lw=2.2, ec=col, joinstyle="round"))
    for c, (P, F) in enumerate(ordenGray):
        ax.text(c + .5, 4.18, "%d%d" % (P, F), ha="center", fontsize=11)
    for r, (E, G) in enumerate(ordenGray):
        ax.text(-.15, 3 - r + .5, "%d%d" % (E, G), ha="right", va="center", fontsize=11)
    ax.text(2, 4.6, "P F", ha="center", fontsize=11, weight="bold")
    ax.text(-.75, 2, "E G", ha="center", va="center", fontsize=11, weight="bold", rotation=90)
    ax.set_xlim(-1, 4.1)
    ax.set_ylim(-.1, 4.9)
    ax.axis("off")
    ax.set_title(titulo, fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, archivo), dpi=150)
    plt.close(fig)


def _trozos(r0, c0, nr, nc):
    """Si el grupo da la vuelta por los bordes del mapa lo parte en dos rectangulos."""
    out = []
    cols = [(c0, nc)] if c0 + nc <= 4 else [(c0, 4 - c0), (0, c0 + nc - 4)]
    rows = [(r0, nr)] if r0 + nr <= 4 else [(r0, 4 - r0), (0, r0 + nr - 4)]
    for rr, h in rows:
        for cc, w in cols:
            out.append((rr, cc, w, h))
    return out


karnaugh("M", lambda E, G, P, F: modelo(E, G, P, F)["M"],
         [(2, 3, 1, 2, "#d62728")], "M = E·G·F'   (grupo de 2: P no importa)", "karnaugh_M.png")
karnaugh("N", lambda E, G, P, F: modelo(E, G, P, F)["N"],
         [(2, 0, 1, 1, "#1f77b4")], "N = E·G·P'·F'   (1 celda)", "karnaugh_N.png")
karnaugh("L", lambda E, G, P, F: modelo(E, G, P, F)["L"],
         [(2, 3, 1, 1, "#2ca02c")], "L = E·G·P·F'   (1 celda)", "karnaugh_L.png")
karnaugh("A", lambda E, G, P, F: modelo(E, G, P, F)["A"],
         [(0, 1, 4, 2, "#9467bd")], "A = F   (grupo de 8)", "karnaugh_A.png")
print("graficas listas en", OUT)
