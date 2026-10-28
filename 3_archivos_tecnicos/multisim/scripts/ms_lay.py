import sys, os, re, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ms_nativo as N
sys.path.insert(0, N.P)
from asc_lib import parse_asc
import mcp_call
SC = 1.9


def tam(nombre, vert):
    """Tamano aproximado (ancho, alto) de una pieza de Multisim con sus textos, para que no se monten."""
    k = nombre[0]
    if k in "RC":
        return (125, 115) if nombre in vert else (140, 80)
    return {"A": (150, 95), "X": (200, 115), "U": (200, 115), "Q": (130, 105), "D": (115, 95), "M": (140, 105), "V": (115, 115), "I": (115, 115)}.get(k, (115, 100))


def separar(pos, vert, vueltas=400):
    """Empuja un poco las piezas que quedan montadas una sobre otra (como se ve en Multisim) hasta que no se toquen."""
    nombres = list(pos)
    vs = set(vert)
    for _ in range(vueltas):
        mov = False
        for i in range(len(nombres)):
            for j in range(i + 1, len(nombres)):
                a, b = nombres[i], nombres[j]
                wa, ha = tam(a, vs)
                wb, hb = tam(b, vs)
                dx, dy = pos[b][0] - pos[a][0], pos[b][1] - pos[a][1]
                ox, oy = (wa + wb) / 2 - abs(dx), (ha + hb) / 2 - abs(dy)
                if ox > 0 and oy > 0:
                    mov = True
                    if ox < oy:                                   # separar en horizontal (la menor penetracion)
                        s = 1 if dx >= 0 else -1
                        pos[a][0] -= s * (ox / 2 + 1)
                        pos[b][0] += s * (ox / 2 + 1)
                    else:
                        s = 1 if dy >= 0 else -1
                        pos[a][1] -= s * (oy / 2 + 1)
                        pos[b][1] += s * (oy / 2 + 1)
        if not mov:
            break
    for k in pos:
        pos[k] = [round(pos[k][0]), round(pos[k][1])]


NN = {"R": 2, "C": 2, "L": 2, "D": 2, "V": 2, "I": 2, "Q": 3, "M": 4}


def canales(blk, pos):
    """Redes con 3 o mas pines (menos tierra, v5 y vm), ordenadas por su posicion media en x."""
    cnt, xs = {}, {}
    for l in N.cuerpo(blk).splitlines() + N.TB[blk].splitlines():
        t = l.split()
        if not t:
            continue
        k = t[0][0]
        n = NN.get(k, 5 if k == "X" else (len(t) - 2 if k == "A" else 0))
        for x in t[1:1 + n]:
            cnt[x] = cnt.get(x, 0) + 1
            xs.setdefault(x, []).append(pos.get(t[0], [0, 0])[0])
    return sorted((n for n, c in cnt.items() if c >= 3 and n not in ("0", "v5", "vm")), key=lambda n: sum(xs[n]) / len(xs[n]))


def patas_x(nombre, x, vs):
    """Posiciones x aproximadas de las patas de una pieza (las que bajan o suben por un cable vertical)."""
    if nombre[0] in "RCDVI" and nombre in vs or nombre[0] in "VI":
        return [x]
    return [x - 42, x + 42]


def distintas_x(pos, vert, sep=26):
    """Que ninguna pata comparta columna con la de otra pieza: asi los cables verticales solo se cruzan y no se montan."""
    vs = set(vert)
    usadas = []
    for nombre in sorted(pos, key=lambda n: pos[n][0]):
        for _ in range(200):
            px = patas_x(nombre, pos[nombre][0], vs)
            if all(abs(a - b) >= sep for a in px for b in usadas):
                break
            pos[nombre][0] += 13
        usadas += patas_x(nombre, pos[nombre][0], vs)


def layout(blk, path, sc=SC, normalizar=True):
    """Posiciones de las piezas (a partir del esquematico de LTspice), rieles y tamano de hoja."""
    sch = parse_asc(os.path.join(N.P, "..", "2_LTspice", "BLOQUE_%s.asc" % blk))
    pos, vert, tim = {}, [], []
    for c in sch.comps:
        if not c.ref:
            continue
        name = c.ref
        if name[0] == "X" and (name[1:2] in "agi" or name.startswith(("Xa", "Xg", "Xi", "Xb1"))) and c.s.name.startswith("HC_"):
            name = "A" + name[1:]
        if "NE555" in c.s.name.upper():
            tim.append((name[1:], c.x * sc, c.y * sc))
            continue
        pos[name] = [round(c.x * sc), round(c.y * sc)]
        if name[0] in "RC" and c.rot in ("R0", "R180", "M0", "M180"):      # vertical solo si lo es en LTspice
            vert.append(name)
    for r in re.findall(r"^(Rz\w+)", N.cuerpo(blk), re.M):      # R de 1 mohm de los seguidores
        x = pos.get("X" + r[2:], [0, 0])
        pos[r] = [x[0] + 140, x[1] + 120]
    ybase = max([v[1] for v in pos.values()] + [0]) + 260
    for k, x0, y0 in tim:                                          # el 555 armado va en un cuadro propio, debajo
        for j, r in enumerate(re.findall(r"^([RXAQ]%s[a-e]) " % k, N.cuerpo(blk), re.M)):
            pos[r] = [round(x0 + 300 * (j % 5)), round(ybase + 250 * (j // 5))]
            if r[0] == "R":
                vert.append(r)
    if normalizar:                                                 # fuentes y cargas de prueba: columna ordenada a la izquierda
        x_izq = min(v[0] for v in pos.values()) - 220
        y_arr = min(v[1] for v in pos.values())
        for k, l in enumerate(N.TB[blk].splitlines()):
            if l.strip():
                nm = l.split()[0]
                pos[nm] = [x_izq, y_arr + 170 * k]
                if nm[0] in "RC":
                    vert.append(nm)
    separar(pos, vert)
    distintas_x(pos, vert)
    xs = [v[0] for v in pos.values()]
    ys = [v[1] for v in pos.values()]
    tr = {"v5": ["h", min(ys) - 90], "vm": ["h", min(ys) - 150], "0": ["h", max(ys) + 230]}
    for k, n in enumerate(canales(blk, pos)):                      # cada red de 3 o mas pines tiene su propio carril (sin estrellas ni cables encimados)
        tr[n] = ["h", min(ys) - 150 - 40 * (k + 1)]
    dx, dy = 0, 0
    if normalizar:                                                 # todo dentro de la hoja blanca
        dx, dy = 100 - min(xs), 80 - min(v[1] for v in tr.values())
        pos = {k: [v[0] + dx, v[1] + dy] for k, v in pos.items()}
        tr = {k: [v[0], v[1] + dy] for k, v in tr.items()}
    W = max(v[0] for v in pos.values()) + 320
    H = tr["0"][1] + 160
    lay = {"positions": pos, "vertical": vert, "trunks": tr}
    if path:
        json.dump(lay, open(path, "w"))
    return lay, (W, H)


def run(blk):
    lp = r"C:\ms_work\nat\lay_%s.json" % blk
    lay, (W, H) = layout(blk, lp)
    os.environ["MULTISIM_MCP_LAYOUT"] = lp
    os.environ["MULTISIM_MCP_SHEET"] = "%d,%d" % (W, H)
    p, s = mcp_call.start()
    mcp_call.call(p, s, 1, "connect", {})
    net = "* %s\n%s\n%s\n%s\n.end\n" % (blk, N.MODELS, N.cuerpo(blk), N.TB[blk])
    out = r"C:\ms_work\nat\BLOQUE_%s.ms14" % blk
    r = mcp_call.call(p, s, 5, "create_schematic_from_netlist", {"netlist": net, "output_ms14": out, "open_after_build": False, "overwrite": True})
    ok = not r["result"].get("isError")
    if ok:
        mcp_call.call(p, s, 7, "open_circuit", {"path": out})
        mcp_call.call(p, s, 6, "get_circuit_image", {"path": r"C:\ms_work\nat\%s.bmp" % blk})
    print(blk, "ok" if ok else "ERR " + r["result"]["content"][0]["text"][:150], "hoja %dx%d" % (W, H), flush=True)
    p.kill()


if __name__ == "__main__":
    for b in sys.argv[1:] or list(N.TB):
        run(b)
