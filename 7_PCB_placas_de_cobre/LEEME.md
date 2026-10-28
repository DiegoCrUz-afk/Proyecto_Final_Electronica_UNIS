> El montaje final es en protoboard. Estas placas de cobre ya no se fabrican; se dejan solo como referencia de como quedarian las conexiones.

# Placas de cobre (PCB) para planchado

3 placas de UNA sola cara (A, B y C). Cada una cabe en una placa de cobre de 15 x 20 cm.
Medidas: A 132.1 x 167.6 mm (19 puentes), B 132.1 x 188.0 mm (49 puentes), C 132.1 x 182.9 mm (29 puentes).

Por cada placa hay 3 PDF (A4, imprimir al 100 %, sin ajustar a la página):
- `PLACA_X_cobre_para_planchado_ESPEJO.pdf`: las pistas en espejo, para el papel termotransferible y planchar sobre la cara de cobre.
- `PLACA_X_componentes.pdf`: lado de piezas. Cada agujero lleva escrito el nombre de su red (GND en azul, +5V, +12V, f, m...). Las líneas magenta (P1, P2...) son puentes de alambre.
- `PLACA_X_guia_de_conexiones.pdf`: lista de cada pata (pieza, pata, red y con qué otras patas se une) y los cables entre placas.

Los agujeros de la fila de arriba de cada placa son los puntos para unir las placas entre sí con cable (GND, +5 V, +12 V y las señales); cada uno se conecta a las piezas con pista o con un puente de alambre.
Antes de planchar, medir con una regla la hoja impresa (debe dar 132.1 mm de ancho).
La lista de taladros está en `3_archivos_tecnicos\pcb\salida`.
