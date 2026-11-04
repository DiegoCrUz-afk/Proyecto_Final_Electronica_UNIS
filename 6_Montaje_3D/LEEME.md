# Montaje 3D de la miniestacion

Abrir con Chrome o Edge (un solo archivo cada uno, sin internet). Cada pagina tiene un boton arriba para pasar a la otra.

- `Protoboards_3D_miniestacion.html`: guia para armar en 5 protoboards de 830 puntos junto al esquematico. Las piezas estan repartidas por toda la protoboard (no pegadas) y los 278 cables corren bajitos, pegados a la placa, con esquinas en angulo recto; solo saltan donde hay una pieza. Cada pata va en una tira de 5 agujeros, los CI sobre el canal, rieles de GND, 5 V y 12 V.
  - Clic en una PIEZA: el panel muestra, por cada pata, el agujero, la red y "conectada con" (las otras patas que quedan unidas por tira + cables, y el riel si es de 5 V, 12 V o GND). En el 3D se marcan esas patas con anillos celestes y se resaltan sus cables.
  - Clic en un CABLE: el panel muestra sus dos extremos y todas las patas que une.
  - Verificacion: `3_archivos_tecnicos\protoboard\verificar_3d.py` lee el HTML y comprueba que ningun agujero este repetido, que ninguna tira mezcle redes y que cada red quede completa (81 redes). 19 de los 278 cables no encontraron un camino libre sin tocar otro y suben hasta unos 22 mm; los cables a dispositivos externos (jack, motor, interruptores) van mas altos.
- Los dos salen de `3_archivos_tecnicos\sistema.inc` (el mismo circuito que se simula).
- "Que medir": 24 medidas guiadas con el valor esperado. "Armado paso a paso": pieza por pieza. "Funcionamiento (simulacion)": reproduce la simulacion de LTspice (4.6 s).

Regenerar: `3_archivos_tecnicos\protoboard\exportar_protoboard3d.py` (usa `generar_protoboard.py`, `ruteo_bajo.py` y la plantilla).
La posicion de cada pieza la decide un acomodo automatico: es una referencia, no un montaje probado.

## v2 (menos cables)
- `Protoboards_3D_miniestacion_v2.html`: mismo circuito (mismas 118 piezas, 373 patas y 81 redes) con **225 cables en vez de 278**. Las piezas se cuelgan de las tiras que ya tienen su red (tambien GND, 5 V y 12 V) y se deja un agujero libre por tira para los cables. La v1 se conserva tal cual.
- Cables v2: 193 de senal y alimentacion, 12 puentes entre rieles, 20 a dispositivos externos.
- Verificacion: `3_archivos_tecnicos\protoboard_v2\verificar_3d.py` da OK (redes completas, sin mezclas, sin agujeros repetidos). La pata->red es identica a la v1. La pagina carga en Chrome sin errores de JavaScript; no se reviso a ojo el acomodo de cables.
- Regenerar: `3_archivos_tecnicos\protoboard_v2\exportar_protoboard3d.py`.
