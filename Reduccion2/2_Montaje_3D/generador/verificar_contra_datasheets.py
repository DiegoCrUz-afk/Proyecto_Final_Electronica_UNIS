"""Verificacion independiente del 3D contra los DATASHEETS (no usa las tablas de generar_montaje3d.py).
1) Cada pata de cada circuito integrado del 3D se compara con la tabla de patas del datasheet (TI, hojas leidas el 10/11/2026).
2) Se arma un netlist SOLO con lo que dice el 3D (datos_r2.json) + las patas del datasheet, y se corre en LTspice con el circuito completo
   (sensor, entradas, pestillo, logica, potencia, LED rojo y motor supuesto). Uso: py -3.13 verificar_contra_datasheets.py"""
import io, json, os, re, subprocess, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
LT = os.path.abspath(os.path.join(AQUI, "..", "..", "1_LTspice")).replace("\\", "/")
OUT = os.path.abspath(os.path.join(AQUI, "..", "verificacion_conexiones"))
os.makedirs(OUT, exist_ok=True)
LTSPICE = os.path.expandvars(r"%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe")
D = json.load(open(os.path.join(AQUI, "datos_r2.json"), encoding="utf-8"))
parts = {p["ref"]: p for p in D["parts"]}

# ---------------- tablas de patas COPIADAS DE LOS DATASHEETS (pagina 3 de cada hoja de TI) ----------------
DS = {
    "74HC00": {1: "1A", 2: "1B", 3: "1Y", 4: "2A", 5: "2B", 6: "2Y", 7: "GND", 8: "3Y", 9: "3A", 10: "3B", 11: "4Y", 12: "4A", 13: "4B", 14: "VCC"},   # SN74HC00 SCLS181H, Table 5-1
    "74HC08": {1: "1A", 2: "1B", 3: "1Y", 4: "2A", 5: "2B", 6: "2Y", 7: "GND", 8: "3Y", 9: "3A", 10: "3B", 11: "4Y", 12: "4A", 13: "4B", 14: "VCC"},  # SN74HC08 SCLS081J, Pin Functions
    "74HC14": {1: "1A", 2: "1Y", 3: "2A", 4: "2Y", 5: "3A", 6: "3Y", 7: "GND", 8: "4Y", 9: "4A", 10: "5Y", 11: "5A", 12: "6Y", 13: "6A", 14: "VCC"},  # SN74HC14 SCLS085L, Pin Functions
    "LM393": {1: "1OUT", 2: "1IN-", 3: "1IN+", 4: "GND", 5: "2IN+", 6: "2IN-", 7: "2OUT", 8: "VCC"},                                              # LM393 SLCS005AH, Table 4-1
}
# nombres que usa el 3D -> nombre del datasheet
ALIAS = {"OUT A": "1OUT", "IN- A": "1IN-", "IN+ A": "1IN+", "IN+ B": "2IN+", "IN- B": "2IN-", "OUT B": "2OUT"}
# discretos (datasheets): 2N3904 TO-92 vista de frente: 1 = E, 2 = B, 3 = C (onsemi 2N3904/D, p.1) | IRLZ44N TO-220AB: 1 = G, 2 = D, 3 = S (IR PD-94831, p.8)
# 1N5819: la franja es el CATODO (Vishay 88525, p.1) | TCRT5000: A = anodo del LED, K = catodo; C = colector y E = emisor del fototransistor (Vishay 83760, p.1 y 4)
mal = []
n_ok = 0
rep = ["# Verificación de las conexiones del 3D contra los datasheets", "",
       "Fuentes (leídas el 10/11/2026): SN74HC00 (SCLS181H), SN74HC08 (SCLS081J), SN74HC14 (SCLS085L), LM393 (SLCS005AH) de Texas Instruments; 2N3904 (onsemi 2N3904/D, rev. 3); IRLZ44NPbF (International Rectifier PD-94831); 1N5817-1N5819 (Vishay 88525); TCRT5000 (Vishay 83760).", ""]

# ---------------- 1) circuitos integrados: pata por pata contra el datasheet ----------------
rep += ["## 1. Patas de los circuitos integrados contra el datasheet", "", "| CI | Modelo | Patas | Resultado |", "|---|---|---|---|"]
for ref, p in parts.items():
    if p["kind"] != "IC":
        continue
    tabla = DS[p["val"]]; bad = []
    for q in p["pins"]:
        nom = ALIAS.get(q["name"], q["name"]); esp = tabla[int(q["n"])]
        if nom != esp:
            bad.append("pata %s: el 3D dice %s, el datasheet %s" % (q["n"], q["name"], esp))
    # alimentacion y tierra
    pv = {tabla[int(q["n"])]: q["net"] for q in p["pins"]}
    if pv["VCC"] != "v5": bad.append("VCC no va a 5 V (%s)" % pv["VCC"])
    if pv["GND"] != "0": bad.append("GND no va a tierra (%s)" % pv["GND"])
    # compuertas sin usar: entradas a GND (no flotantes)
    if p["val"] in ("74HC00", "74HC08"):
        for g in "1234":
            if pv[g + "Y"] == "NC" and (pv[g + "A"] != "0" or pv[g + "B"] != "0"):
                bad.append("compuerta %s sin usar con entradas flotando" % g)
    mal += ["%s: %s" % (ref, b) for b in bad]; n_ok += len(p["pins"]) - len(bad)
    rep.append("| %s | %s | %d | %s |" % (ref, p["val"], len(p["pins"]), "OK" if not bad else "; ".join(bad)))

# ---------------- 2) netlist desde el 3D ----------------
def valor(v):
    """'15 Ω 1 W (ajustar)' -> 15 ; '100 nF' -> 1e-7 ; '26.8k' -> 26800 (se lee el primer numero y su unidad)"""
    tok = str(v).replace("Ω", " ").split()
    m = re.match(r"([\d.]+)(k|M)?$", tok[0]); x = float(m.group(1)); u = m.group(2) or ""
    if not u and len(tok) > 1 and tok[1] in ("µF", "uF", "nF", "pF"):
        u = tok[1]
    return {"k": x * 1e3, "M": x * 1e6, "µF": x * 1e-6, "uF": x * 1e-6, "nF": x * 1e-9, "pF": x * 1e-12, "": x}[u]


nm = lambda n: "0" if n == "0" else re.sub(r"[^\w]", "_", n)
L = ["* Netlist generado SOLO desde el 3D (datos_r2.json) + patas del datasheet. verificar_contra_datasheets.py",
     ".include \"" + LT + "/modelos.inc\"", ".include \"" + LT + "/sistema.inc\"", ".include \"" + LT + "/reduccion2.inc\"",
     ".model SWB SW(Ron=0.1 Roff=1G Vt=0.5 Vh=0.1)", ".param kir=0.55"]
ctrl = []     # fuentes de control de los interruptores
for ref, p in parts.items():
    k = p["kind"]; pin = {q["n"]: nm(q["net"]) for q in p["pins"]}; nom = ref.replace(".", "_")
    if k in ("R", "RW"):
        L.append("R%s %s %s %g" % (nom, pin["1"], pin["2"], valor(p["val"])))
    elif k in ("CC", "CE"):
        a, b = (pin["+"], pin["-"]) if "+" in pin else (pin["1"], pin["2"])
        L.append("C%s %s %s %g" % (nom, a, b, valor(p["val"])))
    elif k == "D":
        L.append("D%s %s %s D%s" % (nom, pin["A"], pin["K"], "1N" + p["val"][2:] if p["val"].startswith("1N") else p["val"]))
    elif k == "LED":
        L.append("D%s %s %s DLED" % (nom, pin["A"], pin["K"]))
    elif k == "Q92":
        L.append("Q%s %s %s %s Q2N3904" % (nom, pin["C"], pin["B"], pin["E"]))      # C B E, nombres del 3D = datasheet (E=1, B=2, C=3)
    elif k == "MOS":
        L.append("M%s %s %s %s %s IRLZ44N_P" % (nom, pin["D"], pin["G"], pin["S"], pin["S"]))
    elif k == "TRIM":
        L.append("R%sa %s %s {10k*(1-kir)}" % (nom, pin["1"], pin["W"])); L.append("R%sb %s %s {10k*kir}" % (nom, pin["W"], pin["3"]))
    elif k == "TCRT":
        L.append("D%sled %s %s DIR" % (nom, pin["A"], pin["K"]))          # LED infrarrojo
        L.append("I%sph %s %s PWL(0 2u 0.9 2u 0.9001 50u 1.6 50u 1.6001 2u)" % (nom, pin["C"], pin["E"]))   # fototransistor: corriente del colector al emisor (2 uA sin objeto, 50 uA con objeto)
    elif k == "TB":
        dev = p.get("ext")
        a, b = [nm(q["net"]) for q in p["pins"]]
        if dev == "FUENTE":
            L.append("V%s %s %s PWL(0 0 1m 5)" % (nom, a, b))
        elif dev == "MOTOR":
            motor = (a, b)
        else:
            ctrl.append((nom, a, b, dev))
    elif k == "IC":
        tabla = DS[p["val"]]; pv = {tabla[int(q["n"])]: nm(q["net"]) for q in p["pins"]}
        if p["val"] in ("74HC00", "74HC08"):
            tipo = "HC_NAND2" if p["val"] == "74HC00" else "HC_AND2"
            for g in "1234":
                if pv[g + "Y"] != "NC":
                    L.append("X%s_%s %s %s %s %s %s" % (nom, g, pv[g + "A"], pv[g + "B"], pv[g + "Y"], pv["VCC"], tipo))
        elif p["val"] == "74HC14":
            for g in "123456":
                if pv[g + "Y"] != "NC":
                    L.append("X%s_%s %s %s %s HC_SCHINV" % (nom, g, pv[g + "A"], pv[g + "Y"], pv["VCC"]))
        elif p["val"] == "LM393":
            L.append("X%s %s %s %s %s %s LM393" % (nom, pv["1IN+"], pv["1IN-"], pv["VCC"], pv["GND"], pv["1OUT"]))
# interruptores externos: control 1 = cerrado. Escenario: E y G cerrados desde 0.15 s; cubierta (G) abierta 2.2-2.4 s; FALLA pulsada 2.8-2.82 s; RESET 3.4-3.42 s
ESC = {"SW_E": [(0.15, 1)], "SW_G": [(0.15, 1), (2.2, 0), (2.4, 1)], "SW_F": [(2.8, 1), (2.82, 0)], "SW_R": [(3.4, 1), (3.42, 0)]}
for nom, a, b, dev in ctrl:
    pts = [(0, 0)]; cur = 0
    for t, v in ESC[dev]:
        pts += [(t, cur), (t + 1e-5, v)]; cur = v
    L.append("V%sc c%s 0 PWL(%s)" % (nom, nom, " ".join("%g %g" % x for x in pts)))
    L.append("S%s %s %s c%s 0 SWB" % (nom, a, b, nom))
# motor supuesto (igual que en la simulacion de potencia)
L += ["Lm %s xm 3m" % motor[0], "Rm xm n2 12", "Beb n2 %s V=Ke*V(w)" % motor[1], "Cw w 0 {J} ic=0", "Bw 0 w I=Ke*I(Lm)-Bfr*V(w)-Tl*tanh(V(w))",
      ".param Ke=0.035 J=1e-5 Bfr=7.2e-6 Tl=0.004", ".tran 0 4.2 0 100u", ".options plotwinsize=0"]
for nombre, t in (("t_normal", 0.8), ("t_objeto", 1.5), ("t_normal2", 2.1), ("t_cubierta", 2.38), ("t_falla", 3.1), ("t_reset", 4.0)):
    for s_, v_ in (("w", "V(w)"), ("m", "V(m)"), ("n", "V(n)"), ("f", "V(f)"), ("p", "V(p)"), ("lo", "V(LOG_lo)"), ("led", "V(ALA_nl)"), ("dm", "V(dm)")):
        L.append(".meas tran %s_%s find %s at=%g" % (s_, nombre, v_, t))
L.append(".save V(w) V(m) V(n) V(f) V(p) V(LOG_lo) V(ALA_nl) V(dm)")
L.append(".end")
cir = os.path.join(OUT, "circuito_desde_3D.cir")
open(cir, "w", encoding="utf-8").write("\n".join(L) + "\n")
logf = os.path.join(OUT, "circuito_desde_3D.log")
if os.path.exists(logf): os.remove(logf)
subprocess.run([LTSPICE, "-b", cir], cwd=OUT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900)
txt = open(logf, encoding="latin1").read()
V = {m.group(1).lower(): float(m.group(2)) for m in re.finditer(r"^(\w+): [^=\n]+=([-\d.e+]+)", txt, re.M)}
rpm = lambda t: V["w_" + t] * 60 / 6.2832
filas = [("Normal (E=1, G=1, sin objeto)", "t_normal"), ("Con objeto", "t_objeto"), ("Objeto retirado", "t_normal2"), ("Cubierta abierta (G=0)", "t_cubierta"), ("Falla guardada (FALLA pulsada y soltada)", "t_falla"), ("Después de RESET", "t_reset")]
rep += ["", "## 2. Circuito completo simulado desde el netlist armado con el 3D", "",
        "El netlist (`verificacion_conexiones/circuito_desde_3D.cir`) se genera **solo** con las piezas y redes del HTML y las patas del datasheet. Motor SUPUESTO (12 Ω, 3 mH), fototransistor simulado como corriente (2 µA / 50 µA), chips con modelos de comportamiento.", "",
        "| Situación | p (sensor) | M | N | F | LED objeto (V) | LED rojo (V) | Velocidad (rpm) |", "|---|---|---|---|---|---|---|---|"]
for t_nom, t in filas:
    rep.append("| %s | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.0f |" % (t_nom, V["p_" + t], V["m_" + t], V["n_" + t], V["f_" + t], V["lo_" + t], V["led_" + t], rpm(t)))
chk = []
def esp(cond, texto):
    global mal
    chk.append((cond, texto))
    if not cond: mal.append("simulación: " + texto)
esp(V["p_t_normal"] < 0.5 and V["p_t_objeto"] > 4.5, "p = 0 sin objeto y 5 V con objeto")
esp(V["m_t_normal"] > 4.5 and V["n_t_normal"] > 4.5, "sin objeto: M = N = 1")
esp(V["m_t_objeto"] > 4.5 and V["n_t_objeto"] < 0.5, "con objeto: M = 1, N = 0")
esp(0.35 < rpm("t_objeto") / rpm("t_normal") < 0.65, "velocidad con objeto entre 35 y 65 por ciento de la normal (valor %.0f por ciento)" % (100 * rpm("t_objeto") / rpm("t_normal")))
esp(V["m_t_cubierta"] < 0.5 and rpm("t_cubierta") < 0.8 * rpm("t_normal"), "cubierta abierta: M = 0 y el motor frena")
esp(V["f_t_falla"] > 4.5 and V["m_t_falla"] < 0.5 and V["led_t_falla"] > 1.5, "falla guardada: F = 1, M = 0 y el LED rojo enciende")
esp(V["f_t_reset"] < 0.5 and V["m_t_reset"] > 4.5 and rpm("t_reset") > 0.9 * rpm("t_normal"), "después de RESET: F = 0 y el motor vuelve a correr")
esp(V["lo_t_objeto"] < 2.5 and V["lo_t_normal"] > 4.5, "LED de objeto: enciende con objeto y apaga sin objeto")
rep += ["", "| Comprobación | Resultado |", "|---|---|"] + ["| %s | %s |" % (t, "OK" if c else "FALLA") for c, t in chk]
rep += ["", "## Resultado", "", "Diferencias: %d. %s" % (len(mal), "TODO COINCIDE con los datasheets y el circuito armado desde el 3D funciona en simulación." if not mal else "; ".join(mal)), "",
        "Límites: los chips son modelos de comportamiento y el motor y el fototransistor son supuestos. Para el 2N3904, el IRLZ44N, el 1N5819 y el TCRT5000 el script confirma que los NOMBRES de pata del 3D (E-B-C, G-D-S, A-K, C-E) se conectan como dice el datasheet; la orientación física al insertar la pieza se confirma con el multímetro (TCRT5000: modo diodo)."]
open(os.path.join(OUT, "Verificacion_conexiones_datasheets.md"), "w", encoding="utf-8").write("\n".join(rep) + "\n")
print("\n".join(rep))
