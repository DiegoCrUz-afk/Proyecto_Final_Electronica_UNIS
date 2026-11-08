# Montaje 3D de la miniestacion

Abrir con Chrome o Edge (un solo archivo cada uno, sin internet).

## Paginas
- `Protoboards_3D_miniestacion_v2.html` (VIGENTE): guia para armar en 5 protoboards de 830 puntos (63 filas, 0 abajo) junto al esquematico. 120 piezas, 377 patas, 82 redes, 229 cables. Sale de `3_archivos_tecnicos\sistema.inc` (el mismo circuito que se simula) mas el LED de objeto de la placa B (solo esta aqui).
- `Maquina_3D_banda.html`: la banda con el motor, el disco, el opto, el sensor IR, el micro-switch, el NTC, la fuente, el interruptor, el reset y las 5 protoboards, con los 20 cables numerados igual que en la v2. WASD (Q/E suben y bajan, Shift mas rapido), vista desarmable (explosionada) y clic en una pieza o cable para ver sus datos. Los engranes extra son una propuesta ilustrativa, no estan en el diseno.
- `Protoboards_3D_miniestacion.html` (v1) y `Motor_opto_desmontado.html` (diagrama del motor): RETIRADAS. Se conservan en el repo, ya no se publican en GitHub Pages ni se actualizan a menos que se pida.

## Como usar la v2
- Piezas con letras J I H G F | E D C B A como las protoboards reales; rieles azul (-) y rojo (+) cortados a la mitad con puentes. Las piezas estan repartidas por toda la placa y los cables corren bajitos, solo saltan donde hay una pieza.
- Clic en una PIEZA: por cada pata, el agujero, la red y "conectada con". Clic en un CABLE: sus dos extremos y las patas que une.
- Enfocar una placa (botones Solo A-E o teclas 1-5, 0 = todas), ocultar cables a otras placas o de alimentacion, "Por donde empezar" y Armado paso a paso por placa (pieza y su cable; al final lo que va a otras placas y a dispositivos). WASD para moverse.
- "Que medir": 24 medidas guiadas. "Funcionamiento (simulacion)": reproduce la simulacion de LTspice (4.6 s); el LED de objeto se enciende cuando el sensor detecta el objeto.
- El opto va junto al disco del motor (no en la protoboard): sus 4 cables entran a la placa D (F33, F32, E33, E32). A anodo (+), K catodo (-), C colector, E emisor; tiene polaridad.

## Verificacion
- `3_archivos_tecnicos\protoboard_v2\verificar_3d.py <html>`: ningun agujero repetido, ninguna tira mezcla redes y cada red completa. Da OK.
- Cables encimados: chequeo propio de distancia entre tubos de redes distintas, 0 pares a menos de 1 mm. 3 cables suben a mas de 21 mm (maximo ~42 mm) para pasar por encima de otros.
- La posicion de cada pieza la decide un acomodo automatico: es una referencia, no un montaje probado.

## Regenerar (tarda ~3 min)
- v2: `3_archivos_tecnicos\protoboard_v2\exportar_protoboard3d.py` (usa `generar_protoboard.py`, `ruteo_bajo.py` y `plantilla_proto3d.html`).
- Maquina: `3_archivos_tecnicos\maquina3d\exportar_maquina3d.py` (lee los cables de la v2; regenerar despues de la v2).
