"""Genera 6_Montaje_3D/Maquina_3D_banda.html: la banda con motor, disco, opto y cada cable hacia su protoboard.
Los cables y sus numeros salen de Protoboards_3D_miniestacion_v3.html (mismos numeros que en la guia v3).
Uso: python exportar_maquina3d.py"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.abspath(os.path.join(AQUI, "..", ".."))
FUENTE = os.path.join(PROY, "6_Montaje_3D", "Protoboards_3D_miniestacion_v3.html")
SALIDA = os.path.join(PROY, "6_Montaje_3D", "Maquina_3D_banda.html")
LIB = os.path.join(AQUI, "..", "montaje3d", "lib3d")

s = open(FUENTE, encoding="utf-8").read()
datos, _ = json.JSONDecoder().raw_decode(s[s.index("const DATA = ") + len("const DATA = "):])
chico = dict(
    offs=datos["offs"],
    boards=datos["boards_list"],
    wires=[dict(i=w["i"], net=w["net"], color=w["color"], kind=w["kind"], a=w["a"], b=w["b"]) for w in datos["wires"] if w["kind"] == "ext"],
)
tpl = open(os.path.join(AQUI, "plantilla_maquina3d.html"), encoding="utf-8").read()
three = open(os.path.join(LIB, "three.min.js"), encoding="utf-8").read()
orbit = open(os.path.join(LIB, "OrbitControls.js"), encoding="utf-8").read()
html = tpl.replace("/*__THREE__*/", three).replace("/*__ORBIT__*/", orbit).replace("/*__DATA__*/", json.dumps(chico, ensure_ascii=False))
open(SALIDA, "w", encoding="utf-8").write(html)
print("ok:", len(chico["wires"]), "cables ->", SALIDA)
