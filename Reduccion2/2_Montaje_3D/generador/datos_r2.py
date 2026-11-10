"""Piezas de la Reduccion 2 (5 V, 3 protoboards). Sensor IR y logica salen de sistema.inc (el mismo circuito del original, via generar_montaje3d);
entrada de 5 V, potencia (IRLZ44N + Rs + puente 2N3904), LED rojo de falla y LED de objeto se definen aqui."""
import generar_montaje3d as g

g.BLOQUES = {k: v for k, v in g.BLOQUES.items() if k in ("SENSOR_IR", "LOGICA")}
g.IC_ASSIGN = {k: v for k, v in g.IC_ASSIGN.items() if k in ("U1", "U8", "U9", "U11")}
g.IC_ZONA = {k: v for k, v in g.IC_ZONA.items() if k in g.IC_ASSIGN}
g.IC_ZONA.update({"U1": "SENSOR_IR", "U11": "ENTRADAS", "U8": "PESTILLO", "U9": "LOGICA"})
BLOQUE_DE = {}
for _r in ("LOG.Rpe", "LOG.Rse", "LOG.Cef", "LOG.Rpg", "LOG.Rsg", "LOG.Cgf", "LOG.Rpr", "LOG.Rsr", "LOG.Crf", "ENT.TBE", "ENT.TBG", "ENT.TBR"):
    BLOQUE_DE[_r] = "ENTRADAS"
for _r in ("LOG.Rsn", "LOG.Cpor", "LOG.Rpor", "LOG.Dpor", "ENT.TBF"):
    BLOQUE_DE[_r] = "PESTILLO"
for _r in ("LOG.Rlo", "LOG.Dlo"):
    BLOQUE_DE[_r] = "LOGICA"
for _r in ("ENT.J1", "ENT.Cin"):
    BLOQUE_DE[_r] = "ALIM"

TITULOS = {"ALIM": "0 Alimentación de 5 V", "SENSOR_IR": "1 Sensor IR", "ENTRADAS": "2 Entradas E, G y RESET (74HC14)", "PESTILLO": "3 Pestillo de falla (74HC00)",
           "LOGICA": "4 Lógica de decisión (74HC08) y LED de objeto", "POTENCIA": "5 Potencia con motor", "LED_ROJO": "6 LED rojo y ajuste de la velocidad lenta"}
ORDEN_BLOQUES = ["ALIM", "SENSOR_IR", "ENTRADAS", "PESTILLO", "LOGICA", "POTENCIA", "LED_ROJO"]
# valor de Rs: sale de la simulacion con motor supuesto (ver 1_LTspice); se ajusta con el motor real
RS_VAL = "15 Ω 1 W (ajustar)"


def construir():
    bl, parts, xs = g.construir()
    keep = []
    for p in parts:
        if p["blk"] not in ("SENSOR_IR", "LOGICA") or p["ref"] in ("ENT.TBN",):
            continue
        keep.append(p)
    # los dispositivos externos de la logica: E, G, RESET (a 5 V) y el pulsador FALLA (a GND, activa setn)
    keep.append(dict(ref="ENT.TBF", blk="LOGICA", kind="TB", val="Pulsador FALLA", pins=[("GND", "0"), ("setn", "setn")], ext="SW_F"))

    def add(ref, blk, kind, val, pins, **k):
        d = dict(ref=ref, blk=blk, kind=kind, val=val, pins=pins); d.update(k); keep.append(d)
    add("ENT.J1", "ENTRADA", "TB", "Entrada 5 V (cargador USB / power bank)", [("+5V", "v5"), ("GND", "0")], ext="FUENTE")
    add("ENT.Cin", "ENTRADA", "CE", "1000 µF", [("+", "v5"), ("-", "0")], big=True)
    add("ENT.TBM", "POTENCIA", "TB", "Motor", [("M+", "v5"), ("M-", "dm")], ext="MOTOR")
    add("POT.M1", "POTENCIA", "MOS", "IRLZ44N", [("G", "m"), ("D", "ds"), ("S", "0")])
    add("POT.Rpd", "POTENCIA", "R", "10k", [("1", "m"), ("2", "0")])
    add("POT.Rs", "POTENCIA", "RW", RS_VAL, [("1", "dm"), ("2", "ds")])
    add("POT.Qp", "POTENCIA", "Q92", "2N3904", [("E", "ds"), ("B", "POT.bq"), ("C", "dm")])
    add("POT.Rb", "POTENCIA", "R", "1k", [("1", "n"), ("2", "POT.bq")])
    add("POT.Dfw", "POTENCIA", "D", "1N5819", [("A", "dm"), ("K", "v5")])
    add("POT.Cb", "POTENCIA", "CE", "100 µF", [("+", "v5"), ("-", "0")])
    add("POT.C2", "POTENCIA", "CC", "100 nF", [("1", "v5"), ("2", "0")])
    add("ALA.Rl", "ALARMA", "R", "470", [("1", "f"), ("2", "ALA.nl")])
    add("ALA.Dl", "ALARMA", "LED", "LED rojo (falla)", [("A", "ALA.nl"), ("K", "0")])
    add("LOG.Rlo", "LED_OBJ", "R", "680", [("1", "v5"), ("2", "LOG.lo")])
    add("LOG.Dlo", "LED_OBJ", "LED", "LED verde (objeto)", [("A", "LOG.lo"), ("K", "LOG.pn")])
    for d in keep:
        if d["ref"] in BLOQUE_DE:
            d["blk"] = BLOQUE_DE[d["ref"]]
        elif d["ref"].startswith("POT.") or d["ref"] == "ENT.TBM":
            d["blk"] = "POTENCIA"
        elif d["ref"].startswith("ALA."):
            d["blk"] = "LED_ROJO"
    return bl, keep, xs


def construir_todo():
    bl, parts, xs = construir()
    ics, usados = g.secciones_ic({k: v for k, v in xs.items()})
    datos = []
    for p in parts:
        w, h, pp = g.formas(p)
        pins = [dict(n=nm, net=red, x=dx, y=dy) for (nm, red), (dx, dy) in zip(p["pins"], pp)]
        d = dict(ref=p["ref"], blk=p["blk"], kind=p["kind"], val=p["val"], board="A", x=0, y=0, w=w, h=h, pins=pins)
        for k in ("note", "ext", "big"):
            if k in p:
                d[k] = p[k]
        datos.append(d)
    for ic in ics:
        n = g.IC_PINS[ic["model"]][1]
        pins = []
        for i in range(1, n + 1):
            dx, dy = g.pos_dip(n, i)
            pins.append(dict(n=str(i), name=ic["names"][i], net=ic["pins"][i], x=dx, y=dy))
        datos.append(dict(ref=ic["id"], blk=g.IC_ZONA[ic["id"]], kind="IC", val=ic["model"], board="A", x=0, y=0, w=n // 2, h=4,
                          pins=pins, secs={str(k): v for k, v in ic["sec"].items()}, spare=ic["spare"]))
    return datos, {}, ics


if __name__ == "__main__":
    d, z, ics = construir_todo()
    print(len(d), "piezas")
    for x in d:
        print(x["ref"], x["kind"], x["val"], [(q["n"], q["net"]) for q in x["pins"]][:14])
