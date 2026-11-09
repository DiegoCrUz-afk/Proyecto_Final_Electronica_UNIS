"""Compara TODO el 3D v3 con SISTEMA_COMPLETO.asc (el esquematico completo): entrada de 12 V, motor, trimpots, conectores a dispositivos y todos los bloques.
LTspice -netlist lee el .asc; las patas que comparten un nodo en el esquematico deben ser EXACTAMENTE las que comparten una red en el 3D.
Uso: python comparar_sistema_completo.py [Protoboards_3D...v3.html]"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import shutil
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.abspath(os.path.join(AQUI, ".."))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "Protoboards_3D_miniestacion_v3.html")
sys.argv = sys.argv[:1]
sys.path.insert(0, os.path.join(PROY, "montaje3d"))
import generar_montaje3d as g3   # noqa: E402

LT = os.path.expandvars(r"%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe")
ASC = os.path.abspath(os.path.join(PROY, "..", "2_LTspice"))
txt = open(SRC, encoding="utf-8").read()
D, _ = json.JSONDecoder().raw_decode(txt[txt.index("const DATA = ") + 13:])
parts = {p["ref"]: p for p in D["parts"]}

# netlist del esquematico completo (en una carpeta temporal, sin tocar la del proyecto)
tmp = tempfile.mkdtemp()
for f in os.listdir(ASC):
    if f.endswith((".asc", ".asy")):
        shutil.copy(os.path.join(ASC, f), tmp)
subprocess.run([LT, "-netlist", os.path.join(tmp, "SISTEMA_COMPLETO.asc")], cwd=tmp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
net_path = os.path.join(tmp, "SISTEMA_COMPLETO.net")
net = {}
for l in open(net_path, encoding="latin1").read().splitlines():
    l = l.split(";")[0].strip()
    if not l or l[0] in "*.+":
        continue
    t = l.split()
    nombre = re.sub(r"[^A-Za-z0-9_]", "", t[0]).lower()
    net[nombre] = [x.lower() for x in t[1:]]
nodo = lambda n: n.lower()


def el(nombre):
    return net.get(nombre.lower())


pin_nodo = {}
sin_esquema = []


def asignar(ref, pares):
    for pata, nd in pares:
        pin_nodo[(ref, pata)] = nodo(nd)


for ref, p in parts.items():
    k = p["kind"]
    ab, _, nm = ref.partition(".")
    if k == "IC":
        continue
    # --- entrada, motor y conectores a dispositivos (no son componentes de un bloque)
    if ref == "ENT.J1":
        v = el("V12"); asignar(ref, [("+12V", v[0]), ("GND", v[1])]); continue
    if ref == "ENT.D1":
        v = el("D1"); asignar(ref, [("A", v[0]), ("K", v[1])]); continue
    if ref == "ENT.Cin":
        v = el("Cin"); asignar(ref, [("+", v[0]), ("-", v[1])]); continue
    if ref == "ENT.TBM":
        asignar(ref, [("M+", el("Lm")[0]), ("M-", el("BEb")[1])]); continue
    if ref in ("ENT.TBE", "ENT.TBG", "ENT.TBR"):
        fuente, pin = {"ENT.TBE": ("Ve", "E"), "ENT.TBG": ("Vg", "G"), "ENT.TBR": ("Vr", "RST")}[ref]
        asignar(ref, [(pin, el(fuente)[0]), ("5V", "v5")]); continue
    if ref == "ENT.TBN":
        b = el("Bn"); asignar(ref, [("5V", b[0]), ("NTC", b[1])]); continue
    if ref == "SEN.TCRT":
        d, i = el("Dled_SEN"), el("Iph"); asignar(ref, [("A", d[0]), ("K", d[1]), ("C", i[0]), ("E", i[1])]); continue
    if ref == "ENC.OPTO":
        d, r = el("Dled_ENC"), el("Renc"); asignar(ref, [("A", d[0]), ("K", d[1]), ("C", r[1]), ("E", "0")]); continue
    if ref.startswith("LOG.Rlo") or ref.startswith("LOG.Dlo"):
        sin_esquema.append(ref); continue
    # --- componentes de bloque: nombre_ABR
    if k == "TRIM":
        if ref == "REG.Rtr":
            r = el("Rtr_REG"); asignar(ref, [("1", r[0]), ("W", r[1])]); continue
        if ref in ("REF.T1", "REF.T2"):
            r = el("Rp%s_REF" % ref[-1]); asignar(ref, [("1", r[0]), ("W", r[1])]); continue
        r1, r2 = el("Rp1_" + ab), el("Rp2_" + ab)
        if r1 and r2:
            asignar(ref, [("1", r1[0]), ("W", r1[1]), ("3", r2[1])]); continue
    e = el("Rbz_ALA" if ref == "ALA.BZ" else "%s_%s" % (nm, ab))
    if e is None:
        sin_esquema.append(ref)
        continue
    if k in ("R", "RW", "CC"):
        asignar(ref, [("1", e[0]), ("2", e[1])])
    elif k == "CE":
        asignar(ref, [("+", e[0]), ("-", e[1])])
    elif k in ("D", "DZ", "LED"):
        asignar(ref, [("A", e[0]), ("K", e[1])])
    elif k in ("Q92", "Q126"):
        asignar(ref, [("C", e[0]), ("B", e[1]), ("E", e[2])])
    elif k == "MOS":
        asignar(ref, [("D", e[0]), ("G", e[1]), ("S", e[2])])
    elif k == "BUZZER":
        asignar(ref, [("+", e[0]), ("-", e[1])])
    else:
        sin_esquema.append(ref)

# circuitos integrados: cada seccion es una instancia X del esquematico
for uid, (modelo, abbr, sec) in g3.IC_ASSIGN.items():
    for s, inst in sec.items():
        nm = inst.split(".")[-1]
        e = el("X%s_%s" % (nm, abbr))               # LTspice antepone una X al nombre de las instancias de subcircuito
        if e is None:
            sin_esquema.append(uid + " sec " + str(s))
            continue
        nodos, tipo = e[:-1], e[-1]
        if modelo in ("LM393", "LM358", "LM324"):
            ip, im, out = g3.OPAMP_SEC[modelo][s]
            vcc, gnd = g3.VCC_GND[modelo]
            inp, inm, vc, ve, o = nodos
            asignar(uid, [(str(ip), inp), (str(im), inm), (str(out), o), (str(vcc), vc), (str(gnd), ve)])
        elif modelo == "NE555":
            for i, nd in enumerate(nodos[:8], 1):
                if i == 3 and nd.endswith("tri_o"):
                    continue
                asignar(uid, [(str(i), nd)])
        elif modelo in ("74HC00", "74HC08"):
            vcc, _g = g3.VCC_GND[modelo]
            ia, ib, iy = g3.GATE_SEC[modelo][s]
            if tipo == "hc_buf":
                a, y, vc = nodos
                asignar(uid, [(str(ia), a), (str(ib), a), (str(iy), y), (str(vcc), vc)])
            else:
                a, b, y, vc = nodos
                asignar(uid, [(str(ia), a), (str(ib), b), (str(iy), y), (str(vcc), vc)])
        elif modelo == "74HC14":
            a, y, vc = nodos
            ia, iy = g3.INV_SEC[s]
            vcc, _g = g3.VCC_GND[modelo]
            asignar(uid, [(str(ia), a), (str(iy), y), (str(vcc), vc)])

pin_red = {}
for (ref, pata) in pin_nodo:
    q = next(x for x in parts[ref]["pins"] if x["n"] == pata)
    pin_red[(ref, pata)] = q["net"]
REOSTATOS = {"REG.Rtr", "REF.T1", "REF.T2"}          # trimpot usado como reostato (patas 1 y W): sus dos extremos son equivalentes
simetrica = lambda ref, pata: (parts[ref]["kind"] in ("R", "RW", "CC") and pata in ("1", "2")) or (ref in REOSTATOS and pata in ("1", "W"))
g_esq, g_3d = defaultdict(lambda: defaultdict(int)), defaultdict(lambda: defaultdict(int))
for (ref, pata), nd in pin_nodo.items():
    lab = (ref, "-" if simetrica(ref, pata) else pata)
    g_esq[nd][lab] += 1
    g_3d[pin_red[(ref, pata)]][lab] += 1
a = {frozenset(v.items()) for v in g_esq.values()}
b = {frozenset(v.items()) for v in g_3d.values()}
print("patas comparadas:", len(pin_nodo), "| piezas del 3D con esquema:", len({r for r, _ in pin_nodo}), "de", len(parts))
print("piezas del 3D sin elemento en el esquematico completo:", sorted(set(sin_esquema)))
usados = {x.lower() for x in []}
if a == b:
    print("RESULTADO: TODO COINCIDE (los", len(a), "grupos de patas son iguales en el esquematico y en el 3D)")
else:
    print("RESULTADO: HAY DIFERENCIAS")
    solo_a, solo_b = list(a - b), list(b - a)
    for ga in solo_a:
        mejor = max(solo_b, key=lambda gb: len(ga & gb), default=frozenset())
        print("   grupo del esquematico:", sorted(k for k, _ in ga)[:8], "...")
        print("      falta en el 3D:", sorted(set(ga) - set(mejor)))
        print("      sobra en el 3D:", sorted(set(mejor) - set(ga)))
shutil.rmtree(tmp, ignore_errors=True)
