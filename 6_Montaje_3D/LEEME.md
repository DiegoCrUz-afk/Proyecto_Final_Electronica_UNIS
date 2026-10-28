# Montaje 3D de la miniestacion

Abrir con Chrome o Edge (un solo archivo cada uno, sin internet). Cada pagina tiene un boton arriba para pasar a la otra.

- `Protoboards_3D_miniestacion.html`: guia para armar en 5 protoboards de 830 puntos junto al esquematico. Cada pata va en una tira de 5 agujeros, los CI sobre el canal, rieles de GND, 5 V y 12 V, y 275 cables numerados. Se verifico que ninguna tira mezcla redes.
- `Placas_de_cobre_3D_miniestacion.html` (solo de referencia, el montaje final es en protoboard): 3 placas de cobre de UNA cara (A alimentacion/potencia, B sensores/logica, C control de velocidad), cada una cabe en una placa de 15x20 cm. Pistas, pads y puentes de alambre; casilla para ver el cobre por debajo. Los PDF para planchar (espejo) estan en `3_archivos_tecnicos\pcb\salida`.
- Los dos salen de `3_archivos_tecnicos\sistema.inc` (el mismo circuito que se simula).
- "Que medir": 24 medidas guiadas con el valor esperado. "Armado paso a paso": pieza por pieza. "Funcionamiento (simulacion)": reproduce la simulacion de LTspice (4.6 s).

Regenerar: `3_archivos_tecnicos\protoboard\exportar_protoboard3d.py` y `3_archivos_tecnicos\pcb\exportar_pcb3d.py`.
La posicion de cada pieza la decide un acomodo automatico: es una referencia, no un montaje probado.
