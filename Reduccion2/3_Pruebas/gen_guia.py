"""Genera Guia_de_pruebas_Reduccion2.md desde las mismas pruebas del 3D (2_Montaje_3D/generador/pruebas_r2.py + datos_r2.json). Uso: py -3.13 gen_guia.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(AQUI, "..", "2_Montaje_3D", "generador", "datos_r2.json"), encoding="utf-8"))
LET = {0: "J", 1: "I", 2: "H", 3: "G", 4: "F", 6: "E", 7: "D", 8: "C", 9: "B", 10: "A"}
parts = {p["ref"]: p for p in D["parts"]}


def pin(ref, n):
    p = parts[ref]; q = next(q for q in p["pins"] if q["n"] == n)
    return "%s pata %s (**%s-%s%d**)" % (p["short"], n, p["board"], LET[q["x"]], 62 - q["y"])


def punto(spec, board_def=None):
    if spec is None:
        b = board_def
        return "riel azul (−, GND) de la placa %s, agujero **%s-riel GND izq fila %d**" % (b, b, 62 - D["gnd"][b]["y"])
    if isinstance(spec, dict):
        if "txt" in spec:
            return spec["txt"]
        nm = "+5 V" if spec["rail"] == "v5" else "GND"
        return "riel de %s de la placa %s, agujero **%s-riel %s izq fila %d**" % (nm, spec["board"], spec["board"], nm, 62 - D["gnd"][spec["board"]]["y"])
    return pin(*spec)


def placa(spec):
    if spec is None or "txt" in (spec if isinstance(spec, dict) else {}):
        return None
    if isinstance(spec, dict):
        return spec["board"]
    return parts[spec[0]]["board"]


TIT = {b: D["blocks"][b]["title"] for b in D["med"]}
PLACA = {"ALIM": "A", "SENSOR_IR": "B", "ENTRADAS": "B", "PESTILLO": "C", "LOGICA": "C", "POTENCIA": "A", "LED_ROJO": "A", "BUZZER": "A"}
L = ["# Guía de pruebas · Reducción 2 (5 V)", "",
     "**Regla:** al terminar de armar cada bloque haces SUS pruebas, una a una, de la primera a la última. Si una no pasa, **no avances al siguiente bloque**. Son las mismas pruebas que el *Modo medición* del 3D (`2_Montaje_3D/Protoboards_3D_reduccion2.html`).", "",
     "- Los valores esperados salen de **simulación en LTspice** o del **diseño original**, y cada prueba dice cuál. **No son mediciones de la máquina.** Lo que dice *a medir* aún no tiene valor.",
     "- Lo marcado **NO validado** depende del motor real (Steren MOT-125, de 6 V) y hoy solo tiene valores con un motor *supuesto* (12 Ω, 3 mH).",
     "- Agujeros: placa-letra-fila, como está impreso (ej. `B-A50`). Antes de energizar cada bloque nuevo, haz la prueba de resistencia 5 V–GND.",
     "- Puntas: **ROJA (+)** y **NEGRA (−)** del multímetro. La negra casi siempre va al riel azul de GND de la placa.",
     "- **Pendiente:** si los rieles de en medio de la BX-4135 están partidos a la mitad (hay que confirmarlo con la placa física). Las pruebas marcadas *depende de los rieles* y los puentes de 5 V y GND del 3D pueden cambiar con esa respuesta.", ""]
n = 0
resumen = []
for b, ids in D["med"].items():
    L += ["## " + TIT[b] + "  (placa %s)" % PLACA[b], ""]
    for i in ids:
        m = next(x for x in D["meas"] if x["id"] == i); n += 1
        bd = placa(m["red"]) or "A"
        L += ["### Prueba %d · %s" % (n, m["t"]), "",
              "- **Qué estamos midiendo:** " + m["mide"],
              "- **Para qué sirve:** " + m["sirve"],
              "- **Antes de medir:** " + m["cond"],
              "- **Modo del multímetro:** " + m["mode"],
              "- **Punta ROJA (+):** " + punto(m["red"]),
              "- **Punta NEGRA (−):** " + punto(m["black"], bd),
              "- **Debe dar:** " + m["exp"]]
        if m["tabla"]:
            L += ["", "| Condición | Valor esperado |", "|---|---|"] + ["| %s | %s |" % (r[0], r[1]) for r in m["tabla"]]
        L += ["- **De dónde sale el valor:** " + m["fuente"]]
        if m["nova"]:
            L += ["- **NO validado todavía:** depende del " + m["nova"] + "."]
        if m["rieles"]:
            L += ["- **Depende de los rieles de la BX-4135** (por confirmar con la placa física)."]
        L += ["- **Si no da, revisa en este orden:**"] + ["  %d. %s" % (k + 1, p) for k, p in enumerate(m["pasos"])]
        L += ["- **Medido:** ________", ""]
L += ["## Cables a los dispositivos externos (se confirman con multímetro, no se dan por hechos)", "", "| Dispositivo | Pata del dispositivo | Agujero | Red |", "|---|---|---|---|"]
for w in D["wires"]:
    if w["kind"] == "ext":
        L.append("| %s | %s | **%s** | %s |" % (w["b"]["ext"], w["b"]["term"], w["a"]["hole"], w["net"]))
L += ["", "Confirmar con el multímetro: TCRT5000 (modo diodo: LED entre A y K), toggle (continuidad: la pata central es COM), micro-switch (COM, NO, NC con la palanca) y las 4 patas del pulsador (las dos de un mismo lado están unidas por dentro).", "",
      "Lógica que debe cumplirse: M = E·G·F', N = M·P', L = M·P (solo mueve el motor E = 1, G = 1, F = 0). Simulada en `1_LTspice/resultado_logica.md`.", ""]
open(os.path.join(AQUI, "Guia_de_pruebas_Reduccion2.md"), "w", encoding="utf-8").write("\n".join(L))
print("ok", n, "pruebas")
