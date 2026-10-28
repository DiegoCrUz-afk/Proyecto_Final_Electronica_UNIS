"""Genera el HTML 3D interactivo del montaje de la miniestacion (3 placas perforadas).
Uso: python exportar_montaje3d.py <salida.html>
Verifica antes de escribir: cada red del netlist queda en un solo grupo electrico (cables + buses) y no se mezclan redes.
"""
import json
import math
import os
import sys
from collections import defaultdict

import generar_montaje3d as g

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "6_Montaje_3D", "Montaje_3D_miniestacion.html")
OFFS = {"A": 0, "B": 56, "C": 112}           # desplazamiento x de cada placa (agujeros)
POWER = {"0": "GND", "v5": "5V", "vm": "12V"}
PCOL = {"0": "#1a1a1a", "v5": "#e53935", "vm": "#ff8f00"}
PAL = ["#00bcd4", "#8bc34a", "#ffeb3b", "#e91e63", "#9c27b0", "#03a9f4", "#ff5722", "#cddc39", "#795548", "#4caf50", "#f06292", "#7e57c2",
       "#26a69a", "#ffa726", "#5c6bc0", "#d4e157", "#29b6f6", "#ec407a", "#66bb6a", "#ab47bc", "#ffca28", "#26c6da", "#ef5350", "#9ccc65"]
BUS_X = {"0": -6.0, "v5": -4.5, "vm": -3.0}


def colname(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def hole(board, x, y):
    return "%s-%s%d" % (board, colname(int(x)), int(y) + 1)


datos, zonas, ics = g.construir_todo()
by_ref = {d["ref"]: d for d in datos}

# ---------- redes ----------
net_pins = defaultdict(list)
for d in datos:
    for q in d["pins"]:
        if q["net"] != "NC":
            net_pins[q["net"]].append((d["ref"], q))
nets = {}
colores = {}
for i, n in enumerate(sorted(n for n in net_pins if n not in POWER)):
    colores[n] = PAL[i % len(PAL)]
for n in net_pins:
    nets[n] = dict(color=PCOL.get(n, colores.get(n, "#aaaaaa")), label=("GND" if n == "0" else n))


def world(d, q):
    return OFFS[d["board"]] + q["x"], q["y"]


# ---------- cables (MST por red, solo redes que no son de potencia) ----------
wires = []
for n, pl in sorted(net_pins.items()):
    if n in POWER:
        continue
    pts = []
    for ref, q in pl:
        d = by_ref[ref]
        x, y = world(d, q)
        pts.append((ref, q, d, x, y))
    # Prim: costo = distancia + penalizacion por cambiar de placa; no unir patas de la misma pieza si hay otra opcion
    def cost(a, b):
        c = math.hypot(a[3] - b[3], a[4] - b[4])
        if a[2]["board"] != b[2]["board"]:
            c += 1000
        if a[0] == b[0]:
            c += 30
        return c
    done = {0}
    todo = set(range(1, len(pts)))
    while todo:
        best = None
        for i in done:
            for j in todo:
                c = cost(pts[i], pts[j])
                if best is None or c < best[0]:
                    best = (c, i, j)
        _, i, j = best
        done.add(j)
        todo.discard(j)
        a, b = pts[i], pts[j]
        if a[0] == b[0] and a[1]["n"] == b[1]["n"]:
            continue
        wires.append(dict(net=n, a=a, b=b))

# numeracion: por placa, de arriba hacia abajo; cables entre placas al final; luego cables a dispositivos
def key(w):
    a, b = w["a"], w["b"]
    cross = a[2]["board"] != b[2]["board"]
    return (cross, a[2]["board"], min(a[4], b[4]), w["net"])
wires.sort(key=key)


def endpoint(t):
    ref, q, d, x, y = t
    return dict(board=d["board"], x=q["x"], y=q["y"], hole=hole(d["board"], q["x"], q["y"]), part=ref, pin=q["n"], ext=None)


W = []
for k, w in enumerate(wires):
    W.append(dict(i=k + 1, net=w["net"], color=nets[w["net"]]["color"], a=endpoint(w["a"]), b=endpoint(w["b"]), kind="signal"))

# cables entre buses de las placas (alimentacion): GND, 5 V y 12 V de A hacia B y C
bus_w = []
for n in ("0", "v5", "vm"):
    for tgt in ("B", "C"):
        bus_w.append(dict(net=n, a=dict(board="A", bus=n, y=2, hole="bus %s placa A" % POWER[n]), b=dict(board=tgt, bus=n, y=2, hole="bus %s placa %s" % (POWER[n], tgt)), kind="bus"))
for w in bus_w:
    W.append(dict(i=len(W) + 1, net=w["net"], color=PCOL[w["net"]], a=w["a"], b=w["b"], kind="bus"))

# cables a dispositivos externos (terminales de tornillo y conectores de 4 patas)
EXT_W = []
for d in datos:
    if d.get("ext") or d["kind"] in ("TCRT", "OPTO"):
        dev = d.get("ext") or ("TCRT" if d["kind"] == "TCRT" else "OPTO")
        for q in d["pins"]:
            EXT_W.append(dict(net=q["net"], a=dict(board=d["board"], x=q["x"], y=q["y"], hole=hole(d["board"], q["x"], q["y"]), part=d["ref"], pin=q["n"]),
                              b=dict(ext=dev, term=q["n"], hole="dispositivo " + dev + " · " + q["n"])))
for w in EXT_W:
    col = PCOL.get(w["net"]) or nets.get(w["net"], {}).get("color", "#bbbbbb")
    W.append(dict(i=len(W) + 1, net=w["net"], color=col, a=w["a"], b=w["b"], kind="ext"))

# ---------- gotas de potencia (cobre por debajo): pata -> bus de su placa ----------
drops = []
for n in POWER:
    for ref, q in net_pins.get(n, []):
        d = by_ref[ref]
        drops.append(dict(net=n, board=d["board"], part=ref, pin=q["n"], x=q["x"], y=q["y"]))

# ---------- verificacion electrica ----------
par = {}


def f(x):
    par.setdefault(x, x)
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x


def u(a, b):
    par[f(a)] = f(b)


for d in datos:
    for q in d["pins"]:
        if q["net"] != "NC":
            f(("P", d["ref"], q["n"]))
for w in W:
    if w["kind"] == "signal":
        u(("P", w["a"]["part"], w["a"]["pin"]), ("P", w["b"]["part"], w["b"]["pin"]))
for dr in drops:
    u(("P", dr["part"], dr["pin"]), ("B", dr["board"], dr["net"]))
for w in W:
    if w["kind"] == "bus":
        u(("B", w["a"]["board"], w["net"]), ("B", w["b"]["board"], w["net"]))
for d in datos:
    for q in d["pins"]:
        if d.get("ext") or d["kind"] in ("TCRT", "OPTO"):
            u(("P", d["ref"], q["n"]), ("X", d["ref"], q["n"]))     # el cable a un dispositivo no une redes entre si
roots = defaultdict(set)
split, merged = {}, []
grupo_red = defaultdict(set)
for n, pl in net_pins.items():
    rs = {f(("P", ref, q["n"])) for ref, q in pl}
    # los terminales externos van aparte: solo cuentan las patas de la placa
    ext = {f(("P", ref, q["n"])) for ref, q in pl}
    if len(rs) != 1:
        split[n] = len(rs)
    for r in rs:
        grupo_red[r].add(n)
merged = [sorted(v) for v in grupo_red.values() if len(v) > 1]
assert not split and not merged, ("redes partidas", split, "redes mezcladas", merged)
# ningun circuito integrado con patas sin red (salidas sin usar = NC, entradas libres a tierra)
for ic in ics:
    for i, red in ic["pins"].items():
        assert red is not None, (ic["id"], i)

# ---------- mediciones guiadas ----------
def pin_of(net, prefer=None, only_kind=None):
    for ref, q in net_pins[net]:
        d = by_ref[ref]
        if only_kind and d["kind"] not in only_kind:
            continue
        if prefer and not ref.startswith(prefer):
            continue
        return [ref, q["n"]]
    raise KeyError((net, prefer))


MEAS = []


def m(id_, grp, t, red, exp, bad, mode="V DC", black=None):
    MEAS.append(dict(id=id_, grp=grp, t=t, red=red, black=black, mode=mode, exp=exp, bad=bad))


G0 = "0 · Alimentación"
m("m_vin", G0, "12 V que entran por el jack", ["ENT.J1", "+12V"], "12 V (fuente externa)", "0 V: el jack no está conectado o la fuente está apagada.")
m("m_vm", G0, "vm: 12 V después del diodo D1 (cátodo)", ["ENT.D1", "K"], "11.1 a 11.3 V con el motor andando (simulación: mínimo 11.13 V)", "0 V: D1 puesto al revés (la banda va hacia vm). 12 V sin caída con el motor parado es normal.")
m("m_v5", G0, "v5: salida del regulador (emisor de Q1)", pin_of("v5", "REG.Q1"), "5.0 V (simulación: 5.012 a 5.018 V). Debe estar entre 4.75 y 5.25 V", "Fuera de rango: ajusta el trimpot Rtr (100 Ω) y revisa Q1 y el Zener.")
m("m_bz", G0, "Base de Q1 (cátodo del Zener)", ["REG.Q1", "B"], "≈ 5.7 V", "0 V: el Zener está al revés o falta Rz. 12 V: Rz sin carga (Zener abierto).")
G2 = "2 · Sensor IR"
m("m_vb", G2, "Base de Q2 (b)", ["SEN.Q2", "B"], "≈ 0.85 V sin objeto, 1.15 V con objeto", "0 V: falta R1 (47 k). 5 V: falta R2 (10 k).")
m("m_vc", G2, "Colector de Q2", ["SEN.Q2", "C"], "≈ 4.2 V sin objeto, ≈ 2.9 V con objeto", "5 V: Q2 no conduce. Cerca de 1 V: Q2 saturado.")
m("m_p", G2, "p: salida del comparador (U1 pata 1)", ["U1", "1"], "≈ 0.03 V sin objeto, ≈ 4.9 V con objeto", "Siempre igual: ajusta el trimpot del umbral (SEN.T1) o revisa el TCRT5000.")
G3 = "3 · Sobrecorriente"
m("m_sh", G3, "sh: caída en el shunt (0.5 Ω)", pin_of("sh", "POT.Rsh"), "≈ 0.075 V con 0.15 A (motor andando); 0.33 V ≈ 0.67 A dispara", "0 V con el motor andando: shunt abierto. Mucho mayor: motor frenado o corto.", mode="V DC (usa el rango de mV)")
m("m_oa", G3, "Salida del LM358 (ganancia 7.8)", ["U4", "1"], "≈ 0.55 V con 0.15 A (7.8 × sh)", "0 V: falta Rg o Rf mal. Sin ganancia: Rf abierta.")
m("m_setn", G3, "setn: 5 V normal, 0 V en falla", pin_of("setn", "LOG.Rsn"), "5.0 V sin falla; ≈ 0 V cuando dispara corriente o temperatura", "0 V siempre: umbral muy bajo; ajusta el trimpot de OC.T1 o TMP.T1.")
G4 = "4 · Temperatura"
m("m_tn", G4, "tnode: divisor del NTC", ["ENT.TBN", "NTC"], "≈ 2.5 V a 25 °C; ≈ 3.7 V a 50 °C (dispara a ≈ 49.9 °C)", "0 V: NTC desconectado o Rfix en corto. 5 V: Rfix abierta.")
G5 = "5 · Lógica y alarma"
m("m_m", G5, "M: permiso de motor (U9 pata 11 → ver la salida de Xa2)", pin_of("m", None), "5 V con E=1, G=1, sin falla; 0 V si abres la cubierta o hay falla", "0 V con todo bien: revisa E, G, F y U9.")
m("m_f", G5, "f: falla enclavada (U8 pata 3)", pin_of("f", None), "0 V normal; ≈ 4.5 a 4.8 V con falla (queda hasta pulsar reset)", "Se queda en 5 V después del reset: la causa de la falla aún existe.")
m("m_cz", G5, "Colector de Q6 (buzzer)", ["ALA.Q6", "C"], "12 V apagado; ≈ 0.04 V con alarma (suena)", "Siempre 12 V: revisa Rb y Q6.")
G6 = "6 · Velocidad (referencia, encoder y error)"
m("m_vref", G6, "vref: referencia de velocidad", pin_of("vref", "REF.T1"), "≈ 0.53 V normal; ≈ 0.26 V reducida (con objeto)", "Si la reducida no baja a la mitad: revisa Q5 y los trimpots REF.T1/REF.T2.")
m("m_vspd", G6, "vspd: velocidad medida (sale del filtro doble)", pin_of("vspd", "ENC.Rfv2"), "≈ 0.51 V a 1394 rpm; 1.1 mV por Hz de encoder", "0 V con el motor girando: el encoder no da pulsos.")
m("m_vctrl", G6, "vctrl: salida del amplificador de error", pin_of("vctrl", "ERR.Ro"), "≈ 2.6 a 2.7 V en normal; sube a 7.6 V con el motor parado por falla", "Fijo: el lazo no está cerrado.")
G7 = "7 · PWM y potencia"
m("m_tri", G7, "tri: rampa del 555 (U6 pata 6)", ["U6", "6"], "rampa de 1.7 a 3.3 V a ≈ 6.9 kHz (osciloscopio)", "Sin rampa: revisa Ct (10 nF), Ra5 y Rb5.", mode="osciloscopio")
m("m_pwm", G7, "pwm: salida del comparador", pin_of("pwm", "PWM.Rpu"), "pulsos de 0 a 5 V, ≈ 6.9 kHz; ciclo ≈ 44 % con vctrl = 2.4 V", "Sin pulsos: revisa U2 pata 7.", mode="osciloscopio")
m("m_gate", G7, "gate: compuerta del IRFZ44N", ["POT.M1", "G"], "pulsos de 0 a ≈ 4.4 V; con M = 0 queda en 0 V", "Siempre 0 V: M = 0 o falla U10. Siempre 4.4 V: el PWM está al 100 %.", mode="osciloscopio")
m("m_dm", G7, "dm: drenaje (motor)", ["POT.M1", "D"], "conmuta entre ≈ 0.5 V y ≈ 11.5 V", "Siempre 11.5 V: el MOSFET no conduce.", mode="osciloscopio")

# ---------- vistas y zonas ----------
board_dims = {b: dict(x0=OFFS[b] - 8, x1=OFFS[b] + 39, z1=zonas["_alto_" + b] + 3) for b in "ABC"}
zones = []
for z, v in zonas.items():
    if z.startswith("_"):
        continue
    placa, x0, y0, w, h = v
    zones.append(dict(id=z, title=g.TITULO_ZONA[z], board=placa, x=x0, y=y0, w=w, h=h))
parts = []
for d in datos:
    short = d["ref"].split(".")[-1]
    parts.append(dict(d, short=short, bx=OFFS[d["board"]]))
def datos_sim():
    """Simulacion de LTspice del sistema completo (esquematicos dibujados), remuestreada cada 5 ms."""
    import numpy as np
    z = np.load(os.path.join(HERE, "..", "sim", "sistema_desde_asc_resumen.npz"))
    t = z["time"]
    dt = 0.005
    n = int(round(t[-1] / dt)) + 2
    idx = np.minimum((t / dt).astype(int), n - 1)
    cnt = np.bincount(idx, minlength=n).astype(float)
    cnt[cnt == 0] = 1
    s = {}
    for k in ("V(v5)", "V(vm)", "V(p)", "V(setn)", "V(m)", "V(n)", "V(l)", "V(f)", "V(vref)", "V(vspd)", "V(vctrl)", "V(w)", "I(Lm)", "V(tc)", "V(tnode)"):
        v = np.bincount(idx, weights=z[k], minlength=n) / cnt
        # compartimentos vacios: repetir el ultimo valor
        for i in range(1, n):
            if np.bincount(idx, minlength=n)[i] == 0:
                v[i] = v[i - 1]
        s[k] = [round(float(x), 4) for x in v]
    ev = [(0.0, "Arranque", "E = 1 a los 0.05 s"), (0.6, "Objeto", "p = 1, L = 1: velocidad reducida"), (1.15, "Objeto retirado", "vuelve a velocidad normal"),
          (1.4, "Cubierta abierta", "M cae en 1 ms"), (1.6, "Cubierta cerrada", "reanuda"), (1.9, "Carga extra", "sube la corriente"), (2.1, "Falla de corriente", "F = 1: alarma, motor parado"),
          (2.6, "Reset", "limpia la falla"), (3.2, "Se calienta", "NTC sube"), (3.36, "Falla de temperatura", "dispara a 49.9 C"), (4.2, "Reset final", "todo normal")]
    return dict(dt=dt, n=n, t_end=float(t[-1]), s=s, events=ev, cover=[[1.40, 1.60]], load=[[1.9, 2.3]], object=[[0.6, 1.1]], reset=[[2.6, 2.75], [3.55, 3.70], [4.2, 4.35]])


if __name__ == "__main__":
    data = dict(parts=parts, wires=W, drops=drops, zones=zones, nets=nets, meas=MEAS, offs=OFFS, dims=board_dims, busx=BUS_X, power=POWER,
                sim=datos_sim(), titles=g.PLACAS, blocks={k: dict(abbr=v[0], title=v[1], board=v[2]) for k, v in g.BLOQUES.items()})
    tpl = open(os.path.join(HERE, "plantilla_montaje3d.html"), encoding="utf-8").read()
    LIB = os.path.join("C:\\Users\\Diego Cruz\\Documents\\electronica-1-amp\\claude\\3_archivos_tecnicos\\lib3d")
    three = open(os.path.join(HERE, "lib3d", "three.min.js"), encoding="utf-8").read()
    orbit = open(os.path.join(HERE, "lib3d", "OrbitControls.js"), encoding="utf-8").read()
    html = tpl.replace("/*__THREE__*/", three).replace("/*__ORBIT__*/", orbit).replace("/*__DATA__*/", "const DATA = " + json.dumps(data, ensure_ascii=False) + ";")
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(html)
    nsig = sum(1 for w in W if w["kind"] == "signal")
    print("ok:", len(parts), "piezas,", len(W), "cables (%d de senal)," % nsig, len(drops), "conexiones de potencia,", round(len(html) / 1e6, 2), "MB")
    print("verificacion electrica: todas las redes completas y sin mezclas")
