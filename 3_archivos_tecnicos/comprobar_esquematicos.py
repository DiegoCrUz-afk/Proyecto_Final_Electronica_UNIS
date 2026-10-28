"""Comprueba que cada esquematico de bloque (.asc) tiene EXACTAMENTE las mismas conexiones y valores que el
subcircuito de sistema.inc que se simula. Usa LTspice -netlist sobre el .asc y compara por nombre de componente.
Uso: python comprobar_esquematicos.py [BLOQUE_X ...]
"""
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
LT = os.path.expandvars(r"%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe")
ASC = os.path.join(AQUI, "..", "2_LTspice")
MAPA = {"BLOQUE_REG5V": "REG5V", "BLOQUE_SENSOR_IR": "SENSOR_IR", "BLOQUE_SOBRECORRIENTE": "SOBRECORRIENTE",
        "BLOQUE_TEMPERATURA": "TEMPERATURA", "BLOQUE_LOGICA": "LOGICA", "BLOQUE_PWM_GEN": "PWM_GEN",
        "BLOQUE_POTENCIA": "POTENCIA", "BLOQUE_ENCODER_FV": "ENCODER_FV", "BLOQUE_REFVEL": "REFVEL",
        "BLOQUE_ERROR_AMP": "ERROR_AMP", "BLOQUE_ALARMA": "ALARMA"}
# cuantos nodos tiene cada dispositivo segun su letra (el resto de la linea es modelo/valor)
NNODOS = {"r": 2, "c": 2, "l": 2, "d": 2, "v": 2, "i": 2, "q": 3, "m": 4, "b": 2, "s": 2, "e": 2}


def lineas_logicas(txt):
    out = []
    for l in txt.splitlines():
        l = l.split(";")[0].rstrip()
        if l.startswith("+") and out:
            out[-1] += " " + l[1:].strip()
        elif l.strip() and not l.startswith("*") and not l.startswith(";"):
            out.append(l.strip())
    return out


def parse_dispositivos(lineas):
    """-> {nombre: (nodos, resto)}"""
    d = {}
    for l in lineas:
        if l.startswith("."):
            continue
        t = l.split()
        n = re.sub(r"^X[^A-Za-z0-9_]+", "", t[0], flags=re.I)
        k = n[0].lower()
        if k == "x":
            nodos, resto = t[1:-1], t[-1]
            # parametros al final: nombre=valor
            while resto.find("=") >= 0 and nodos:
                resto = nodos.pop() + " " + resto
            d[n.lower()] = ([x.lower() for x in nodos], resto)
        elif k in NNODOS:
            nn = NNODOS[k]
            resto = " ".join(t[1 + nn:])
            if k == "q" and resto.startswith("0 "):      # LTspice agrega el sustrato (nodo 0) a los BJT
                resto = resto[2:]
            nodos = [x.lower() for x in t[1:1 + nn]]
            d[n.lower()] = (nodos, resto)
    return d


def subckt_inc(nombre):
    txt = open(os.path.join(AQUI, "sistema.inc"), encoding="utf8").read()
    m = re.search(r"^\.subckt %s\s+(.*?)\n(.*?)^\.ends" % nombre, txt, re.M | re.S | re.I)
    puertos = m.group(1).split()
    cuerpo = lineas_logicas(m.group(2))
    return puertos, parse_dispositivos(cuerpo)


def netlist_asc(nombre):
    asc = os.path.join(ASC, nombre + ".asc")
    net = os.path.join(ASC, nombre + ".net")
    if os.path.exists(net):
        os.remove(net)
    subprocess.run([LT, "-netlist", asc], cwd=ASC, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    for _ in range(30):
        if os.path.exists(net):
            break
        import time
        time.sleep(0.3)
    txt = open(net, encoding="latin1").read()
    return parse_dispositivos(lineas_logicas(txt))


def particion(dev):
    nets = {}
    for n, (nodos, _) in dev.items():
        for i, x in enumerate(nodos):
            if n[0] in "rc":                              # sin polaridad: el orden de los pines no importa
                i = 0
            nets.setdefault(x, set()).add((n, i))
    return {frozenset(v) for v in nets.values()}


def norm(v):
    v = v.lower().replace(" ", "")
    return re.sub(r"[^-]+", "u", v)               # micro (u) mal codificado


def comparar(bloque):
    sub = MAPA[bloque]
    puertos, esperado = subckt_inc(sub)
    real = netlist_asc(bloque)
    errores = []
    for n in sorted(set(esperado) - set(real)):
        errores.append("falta en el esquema: " + n)
    for n in sorted(set(real) - set(esperado)):
        errores.append("sobra en el esquema: " + n)
    comunes = set(esperado) & set(real)
    pe = particion({n: esperado[n] for n in comunes})
    pr = particion({n: real[n] for n in comunes})
    for g in pe - pr:
        errores.append("conexion del subcircuito que NO esta en el esquema: " + ", ".join("%s.%d" % (a, b + 1) for a, b in sorted(g)))
    for g in pr - pe:
        errores.append("conexion del esquema que NO esta en el subcircuito: " + ", ".join("%s.%d" % (a, b + 1) for a, b in sorted(g)))
    for n in sorted(comunes):
        ve, vr = norm(esperado[n][1]), norm(real[n][1])
        if ve != vr:
            errores.append("valor distinto en %s: subcircuito '%s' / esquema '%s'" % (n, esperado[n][1], real[n][1]))
    return errores, len(comunes)


if __name__ == "__main__":
    sel = sys.argv[1:] or list(MAPA)
    ok = True
    for b in sel:
        err, n = comparar(b)
        print("%-24s %s (%d componentes)" % (b, "OK" if not err else "DIFERENCIAS", n))
        for e in err:
            print("    -", e)
        ok &= not err
    print("TODO COINCIDE" if ok else "HAY DIFERENCIAS")
