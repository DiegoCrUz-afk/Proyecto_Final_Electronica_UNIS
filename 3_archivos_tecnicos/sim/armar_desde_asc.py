"""Arma bloques_desde_asc.inc a partir de los netlists de los esquematicos dibujados (BLOQUE_*.net).
Sirve para simular lo que esta DIBUJADO (no sistema.inc): cada .net se envuelve como subcircuito con los
mismos nombres y orden de pines que sistema.inc. Antes hay que generar los .net con LTspice -netlist."""
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
ASC = os.path.join(AQUI, "..", "..", "2_LTspice")
INC = os.path.join(AQUI, "..", "sistema.inc")
MAPA = {"BLOQUE_REG5V": "REG5V", "BLOQUE_SENSOR_IR": "SENSOR_IR", "BLOQUE_SOBRECORRIENTE": "SOBRECORRIENTE",
        "BLOQUE_TEMPERATURA": "TEMPERATURA", "BLOQUE_LOGICA": "LOGICA", "BLOQUE_ALARMA": "ALARMA",
        "BLOQUE_REFVEL": "REFVEL", "BLOQUE_ENCODER_FV": "ENCODER_FV", "BLOQUE_ERROR_AMP": "ERROR_AMP",
        "BLOQUE_PWM_GEN": "PWM_GEN", "BLOQUE_POTENCIA": "POTENCIA"}


def limpiar(b):
    b = b.replace(b"\xc2\xb5", b"u").replace(b"\xb5", b"u")
    t = b.decode("latin1").replace("Â", "")
    return re.sub(r"(?m)^X§", "", t).replace("§", "")


inc = open(INC, encoding="latin1").read().splitlines()
pines, params, ordenes = {}, {}, []
cur = None
for l in inc:
    m = re.match(r"\.subckt (\w+) (.*)", l, re.I)
    if m:
        cur = m.group(1)
        pines[cur] = m.group(2).strip()
        params[cur] = []
        ordenes.append(cur)
    elif l.lower().startswith(".param") and cur:
        params[cur].append(l)
    elif l.lower().startswith(".ends"):
        cur = None

out = ["* Subcircuitos armados desde los esquematicos dibujados (BLOQUE_*.asc) - generado por armar_desde_asc.py"]
# compuertas 74HC (modelos de comportamiento): se toman tal cual de sistema.inc
txt = "\n".join(inc)
out.append(".model SWSCH SW(Ron=1 Roff=1G Vt=2.5 Vh=0.5)")
for g in ("HC_AND2", "HC_NAND2", "HC_BUF", "HC_SCHINV"):
    m = re.search(r"\.subckt %s .*?\.ends" % g, txt, re.S | re.I)
    out.append(m.group(0))
for bloque, sub in MAPA.items():
    net = open(os.path.join(ASC, bloque + ".net"), "rb").read()
    lin = limpiar(net).splitlines()
    out.append(".subckt %s %s" % (sub, pines[sub]))
    for l in lin:
        s = l.strip()
        if not s or s.startswith("*") or s.lower() in (".backanno", ".end"):
            continue
        if s.lower().startswith((".model", ".lib")):
            continue
        s = s.split(";")[0].rstrip()
        out.append(s)
    out += params[sub]
    out.append(".ends")
open(os.path.join(AQUI, "bloques_desde_asc.inc"), "w", encoding="ascii", newline="\n").write("\n".join(out) + "\n")
print("bloques_desde_asc.inc listo:", len(out), "lineas")
