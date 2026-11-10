"""Comprueba que los valores de la guía de pruebas coinciden con las simulaciones de LTspice (los .log de 1_LTspice).
Cada prueba con `sim` guarda (log, medicion, minimo, maximo); aquí se lee el valor simulado y se verifica que cae en el rango. Uso: py -3.13 check_sim_vs_guia.py"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
LT = os.path.join(AQUI, "..", "1_LTspice")
D = json.load(open(os.path.join(AQUI, "..", "2_Montaje_3D", "generador", "datos_r2.json"), encoding="utf-8"))
cache = {}


def log(nombre):
    if nombre not in cache:
        txt = open(os.path.join(LT, nombre + ".log"), encoding="latin1").read()
        cache[nombre] = {m.group(1).lower(): float(m.group(2)) for m in re.finditer(r"^(\w+): [^=\n]+=([-\d.e+]+)", txt, re.M)}
    return cache[nombre]


filas = ["| Prueba | Simulación | Valor simulado | Rango de la guía | Resultado |", "|---|---|---|---|---|"]
mal = 0; n = 0
for m in D["meas"]:
    for (arch, nom, lo, hi) in m["sim"]:
        v = log(arch)[nom.lower()]; ok = lo <= v <= hi; mal += (not ok); n += 1
        filas.append("| %s | %s · %s | %.4g | %g a %g | %s |" % (m["id"], arch, nom, v, lo, hi, "OK" if ok else "FUERA DE RANGO"))
res = open(os.path.join(LT, "resultado_logica.md"), encoding="utf-8").read()
logica_ok = "Errores: 0" in res
filas.append("| lógica (16 combinaciones + pestillo + LED) | prueba_logica | ver resultado_logica.md | 0 errores | %s |" % ("OK" if logica_ok else "HAY ERRORES"))
mal += (not logica_ok)
# E y G limpios: deben coincidir con la combinacion que se aplico
meta = json.load(open(os.path.join(LT, "scripts", "logica_meta.json"), encoding="utf-8"))
L = log("prueba_logica"); bad_eg = 0
for name, t, (e, g, p, f) in meta["meas"]:
    ve, vg = L["elimpio_" + name.lower()], L["glimpio_" + name.lower()]
    bad_eg += (int(ve > 2.5) != e) + (int(vg > 2.5) != g)
filas.append("| E y G limpios (U11) | prueba_logica | 16 combinaciones | = lo aplicado | %s |" % ("OK" if bad_eg == 0 else "%d FUERA" % bad_eg))
mal += bad_eg
filas.append("| RST limpio (U11) | prueba_logica | %.2f V pulsado / %.3f V suelto | 5 V / 0 V | %s |" % (L["rstlimpio_l2_reset_con_falla_pulsada"], L["rstlimpio_l3_falla_suelta_sin_reset"], "OK" if L["rstlimpio_l2_reset_con_falla_pulsada"] > 4.9 and L["rstlimpio_l3_falla_suelta_sin_reset"] < 0.1 else "FUERA"))
out = ["# Verificación: guía de pruebas contra LTspice", "", "Las pruebas que citan una simulación se comparan con los .log actuales. Lo marcado *a medir* no tiene simulación.", ""] + filas + ["", "Comprobaciones fuera de rango: %d" % mal]
open(os.path.join(AQUI, "Verificacion_sim_vs_guia.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
