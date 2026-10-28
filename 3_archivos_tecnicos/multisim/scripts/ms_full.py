"""Sistema completo en UN solo .ms14: los 11 bloques en una fila, con rieles v5 / vm / GND compartidos y las senales entre bloques.
Uso: python ms_full.py   ->  C:\\ms_work\\nat\\SISTEMA_COMPLETO.ms14"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ms_nativo as N
import ms_lay as L
import mcp_call
from asc_lib import parse_asc

ABBR = {"REG5V": "REG", "SENSOR_IR": "SEN", "SOBRECORRIENTE": "OC", "TEMPERATURA": "TMP", "LOGICA": "LOG", "ALARMA": "ALA", "REFVEL": "REF",
        "ENCODER_FV": "ENC", "ERROR_AMP": "ERR", "PWM_GEN": "PWM", "POTENCIA": "POT"}
ORDEN = ["REG5V", "SENSOR_IR", "SOBRECORRIENTE", "TEMPERATURA", "LOGICA", "ALARMA", "POTENCIA", "PWM_GEN", "ERROR_AMP", "REFVEL", "ENCODER_FV"]
KEEP = {"0", "v5", "vm"}
NNODOS = {"R": 2, "C": 2, "L": 2, "D": 2, "V": 2, "I": 2, "Q": 3, "M": 4}


def puertos(blk):
    sch = parse_asc(os.path.join(N.P, "..", "2_LTspice", "BLOQUE_%s.asc" % blk))
    pp = {(a, b) for a, b, _ in sch.iopins}
    return {nm for (x, y, nm) in sch.flags if (x, y) in pp}


def renombrar(blk, linea):
    ab = ABBR[blk]
    p = puertos(blk)
    t = linea.split()
    k = t[0][0]
    if k in NNODOS:
        n = NNODOS[k]
    elif k == "X":
        n = 5
    elif k == "A":
        n = len(t) - 2
    else:
        return linea
    nodos = []
    for x in t[1:1 + n]:
        nodos.append(x if (x in KEEP or x in p) else ab.lower() + "_" + x)
    return " ".join([t[0] + ab] + nodos + t[1 + n:])


def main():
    cuerpo, pos, vert = [], {}, []
    x0 = 0
    ys = []
    for blk in ORDEN:
        lay, (W, H) = L.layout(blk, None, sc=1.6, normalizar=False)
        ab = ABBR[blk]
        mnx = min(v[0] for v in lay["positions"].values())
        for r, v in lay["positions"].items():
            pos[r + ab] = [v[0] - mnx + x0, v[1]]
            ys.append(v[1])
        vert += [r + ab for r in lay["vertical"]]
        mxx = max(v[0] for v in lay["positions"].values()) - mnx
        x0 += mxx + 330
        cuerpo += [renombrar(blk, l) for l in N.cuerpo(blk).splitlines()]
    # redes entre bloques con 3 o mas pines: un riel propio ARRIBA de todo (cada pin sube a su riel), en vez de una estrella en el centro
    cnt, xs_net = {}, {}
    for l in cuerpo:
        tt = l.split()
        k = tt[0][0]
        n = NNODOS.get(k, 5 if k == "X" else (len(tt) - 2 if k == "A" else 0))
        for x in tt[1:1 + n]:
            cnt[x] = cnt.get(x, 0) + 1
            xs_net.setdefault(x, []).append(pos.get(tt[0], [0, 0])[0])
    canales = sorted((n for n, c in cnt.items() if c >= 3 and n not in KEEP and not re.match(r"^[a-z]{2,3}_", n) and n not in ("0",)),
                     key=lambda n: sum(xs_net[n]) / len(xs_net[n]))
    top = min(ys) - 150
    vm_y = 70 + 36 * (len(canales) + 1)
    dy = vm_y - top
    for r in pos:
        pos[r][1] += dy
        pos[r][0] += 100
    tr = {"v5": ["h", min(ys) - 90 + dy], "vm": ["h", min(ys) - 150 + dy], "0": ["h", max(ys) + 230 + dy]}
    for k, n in enumerate(canales):
        tr[n] = ["h", vm_y - 36 * (k + 1)]
    print("redes con riel propio:", canales, flush=True)
    yb = tr["vm"][1] + 700
    pos["Rmot"] = [x0 + 200, yb]
    pos["Rbanda"] = [x0 + 500, yb]
    pos["Dbanda"] = [x0 + 500, yb + 330]
    vert += ["Rmot", "Rbanda"]
    W, H = x0 + 800, tr["0"][1] + 200
    ext = ["V12 vm 0 DC 12", "Ve ein 0 DC 5", "Vg gin 0 DC 5", "Vr rin 0 DC 0", "Iph v5 b DC 50u", "Rtin tin 0 100Meg", "Rn v5 tnode 10k",
           "Venc enc 0 PULSE(0.3 4.7 0 1u 1u 1m 2m)", "Rmot vm dm 12", "Rbanda vm nbanda 1k", "Dbanda nbanda dm DLED"]  # LED encendido = banda funcionando
    ep = [(r, [x0 // 2, 0]) for r in ()]
    lay = {"positions": pos, "vertical": vert, "trunks": tr}
    lp = r"C:\ms_work\nat\lay_SISTEMA.json"
    json.dump(lay, open(lp, "w"))
    os.environ["MULTISIM_MCP_LAYOUT"] = lp
    os.environ["MULTISIM_MCP_SHEET"] = "%d,%d" % (W, H)
    net = "* SISTEMA COMPLETO\n%s\n%s\n%s\n.end\n" % (N.MODELS, "\n".join(cuerpo), "\n".join(ext))
    open(r"C:\ms_work\nat\sistema_nativo.cir", "w").write(net)
    print("hoja", W, "x", H, "piezas", len(pos), flush=True)
    return net


if __name__ == "__main__":
    net = main()
    p, s = mcp_call.start()
    mcp_call.call(p, s, 1, "connect", {})
    out = r"C:\ms_work\nat\SISTEMA_COMPLETO.ms14"
    r = mcp_call.call(p, s, 5, "create_schematic_from_netlist", {"netlist": net, "output_ms14": out, "open_after_build": False, "overwrite": True})
    print("crear", "ERR " + str(r["result"]["content"][0]["text"])[:300] if r["result"].get("isError") else "ok", flush=True)
    p.kill()
