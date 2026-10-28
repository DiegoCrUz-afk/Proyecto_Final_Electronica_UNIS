import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_call import start, call
P = r"C:\Users\Diego Cruz\Documents\Proyecto_Final_Electronica_UNIS\3_archivos_tecnicos"
sis = open(P + r"\sistema.inc", encoding="latin1").read()
mod = open(P + r"\modelos.inc", encoding="latin1").read()
MODELS = "\n".join(l for l in mod.splitlines() if l.startswith(".model") and "VDMOS" not in l and "SWCMP" not in l)
MODELS = MODELS.replace("{B3904}", "200")
MODELS += "\n.model IRFZ44N_P NMOS(Level=1 Vto=3 Kp=12 Cbd=300p Cgso=1n Cgdo=0.3n Rd=6m Rs=3m)"
PARAMS = dict(kir=0.55, koc=0.2, ktm=0.5, kvn=0.8, kvr=0.7, Kerr=10)
TB = {
 "REG5V": "V12 vm 0 DC 12\nIl v5 0 DC 75m\n",
 "SENSOR_IR": "V5 v5 0 DC 5\nIph v5 b DC 50u\nRtin tin 0 100Meg\n",
 "SOBRECORRIENTE": "V12 vm 0 DC 12\nV5 v5 0 DC 5\nVs sh 0 DC 0.5\nRsn v5 setn 10k\n",
 "TEMPERATURA": "V5 v5 0 DC 5\nRn v5 tnode 3.6k\nRsn v5 setn 10k\n",
 "LOGICA": "V5 v5 0 DC 5\nVe ein 0 DC 5\nVg gin 0 DC 5\nVp p 0 DC 0\nVr rin 0 DC 0\nVs setn 0 DC 5\n",
 "PWM_GEN": "V5 v5 0 DC 5\nVc vctrl 0 DC 2.4\n",
 "POTENCIA": "V12 vm 0 DC 12\nV5 v5 0 DC 5\nVp pwm 0 DC 5\nVm m 0 DC 5\nRmot vm dm 12\nRbanda vm nbanda 1k\nDbanda nbanda dm DLED\n",
 "ENCODER_FV": "V5 v5 0 DC 5\nVenc enc 0 PULSE(0.3 4.7 0 1u 1u 1m 2m)\n",
 "REFVEL": "V5 v5 0 DC 5\nVl l 0 DC 0\n",
 "ERROR_AMP": "V12 vm 0 DC 12\nV5 v5 0 DC 5\nVr vref 0 DC 0.526\nVs vspd 0 DC 0.45\n",
 "ALARMA": "V12 vm 0 DC 12\nVf f 0 DC 5\n",
}


def num(expr):
    e = expr.strip("{}")
    e = re.sub(r"(\d+(?:\.\d+)?)k", r"(\1*1e3)", e)
    return "%g" % eval(e, {}, PARAMS)


def ne555(t):
    """NE555 con partes nativas (el paquete local no trae el 555): divisor 3 x 5k, 2 comparadores, latch SR con AND/OR/NOT, transistor de descarga."""
    k = t[0][1:]
    g, trig, o, rst, ctl, thr, dis, vcc = t[1:9]
    n = lambda s: "%s%s" % (s, k)
    return [
        "R%sa %s %s 5k" % (k, vcc, ctl), "R%sb %s n%slo 5k" % (k, ctl, k), "R%sc n%slo %s 5k" % (k, k, g),
        "X%sa %s %s %s %s n%sr LM358" % (k, thr, ctl, vcc, g, k),             # umbral > 2/3 -> reset
        "X%sb n%slo %s %s %s n%ss LM358" % (k, k, trig, vcc, g, k),         # disparo < 1/3 -> set
        "A%sa n%sr n%srb %s 0 NOT" % (k, k, k, vcc),
        "A%sb n%ss n%sq n%st %s 0 OR" % (k, k, k, k, vcc),
        "A%sc n%st n%srb n%sq %s 0 AND" % (k, k, k, k, vcc),
        "A%sd n%sq n%sqb %s 0 NOT" % (k, k, k, vcc),
        "A%se n%sq n%sq %s %s 0 AND" % (k, k, k, o, vcc),
        "R%sd n%sqb bd%s 1k" % (k, k, k),
        "Q%sa %s bd%s %s Q2N3904" % (k, dis, k, g),
    ]


def cuerpo(blk):
    m = re.search(r"\.subckt %s .*?\.ends" % blk, sis, re.S).group(0).splitlines()[1:-1]
    out = []
    for l in m:
        l = l.strip()
        if not l or l.startswith("*") or l.lower().startswith(".param"):
            continue
        l = re.sub(r"\{[^}]*\}", lambda mo: num(mo.group(0)), l)
        t = l.split()
        if t[0][0] == "X":
            mod_ = t[-1]
            if mod_ == "NE555":
                out.extend(ne555(t))
                continue
            if mod_ in ("LM393", "LM358"):
                l = " ".join(t[:-1]) + " LM358"
            elif mod_ == "HC_AND2":
                l = "A%s %s %s %s %s 0 AND" % (t[0][1:], t[1], t[2], t[3], t[4])
            elif mod_ == "HC_NAND2":
                l = "A%s %s %s %s %s 0 NAND" % (t[0][1:], t[1], t[2], t[3], t[4])
            elif mod_ == "HC_BUF":
                l = "A%s %s %s %s %s 0 AND" % (t[0][1:], t[1], t[1], t[2], t[3])
            elif mod_ == "HC_SCHINV":
                l = "A%s %s %s %s 0 NOT" % (t[0][1:], t[1], t[2], t[3])
        elif t[0][0] == "M":
            l = l.replace("IRFZ44N_P", "IRFZ44N_P")
        t = l.split()
        if t[0][0] == "X" and len(t) == 7 and t[2] == t[5]:      # seguidor: salida unida a la entrada -
            o2 = t[5] + "_o"
            out.append(" ".join(t[:5]) + " " + o2 + " LM358")
            out.append("Rz%s %s %s 1m" % (t[0][1:], o2, t[5]))
            continue
        out.append(l)
    return "\n".join(out)


if __name__ == "__main__":
    p, s = start(); call(p, s, 1, "connect", {})
    os.makedirs(r"C:\ms_work\nat", exist_ok=True)
    for blk in sys.argv[1:] or list(TB):
        net = "* %s\n%s\n%s\n%s\n.end\n" % (blk, MODELS, cuerpo(blk), TB[blk])
        out = r"C:\ms_work\nat\BLOQUE_%s.ms14" % blk
        r = call(p, s, 5, "create_schematic_from_netlist", {"netlist": net, "output_ms14": out, "open_after_build": True, "overwrite": True})
        ok = not r["result"].get("isError")
        if ok:
            call(p, s, 6, "get_circuit_image", {"path": r"C:\ms_work\nat\%s.bmp" % blk})
        print(blk, "ok" if ok else "ERR " + r["result"]["content"][0]["text"][:120], flush=True)
    p.kill()

