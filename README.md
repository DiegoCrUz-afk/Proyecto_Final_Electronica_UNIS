# Miniestación industrial automatizada (proyecto final de Electrónica, UNIS)

Minibanda transportadora con motor DC de 12 V (máx. 500 mA), hecha con electrónica analógica y compuertas 74HC, sin microcontroladores. Se arma en protoboard.

- `1_Arquitectura`: diagrama general.
- `2_LTspice`: esquemáticos (completo y por bloques), `SISTEMA_SOLO_CIRCUITO.asc` (la misma hoja con títulos y notas fuera de los cables; solo el circuito en una fila, igual que el 3D, sin fuentes de simulación; no simula) y sus PNG.
- `3_archivos_tecnicos`: el circuito en texto (`sistema.inc`), los modelos, los scripts que generan los esquemáticos, el 3D y la lista de compras, y las simulaciones.
- `4_Documentacion`: guía de componentes, explicación por bloques y dos guías del esquemático por bloques con imágenes: una de Multisim (`Guia_del_esquematico_por_bloques.html`) y una de LTspice (`Guia_del_esquematico_LTspice.html`).
- `5_Compras_y_Pruebas`: lista de compras (PDF) y guía de pruebas.
- `6_Montaje_3D`: paginas 3D (abrir el `.html` en el navegador):
  - `Protoboards_3D_miniestacion_v2.html`: la guia 3D vigente (5 protoboards, 120 piezas, 229 cables, con el LED de objeto en la placa B). Ver en linea: https://diegocruz-afk.github.io/Proyecto_Final_Electronica_UNIS/6_Montaje_3D/Protoboards_3D_miniestacion_v2.html
  - `Maquina_3D_banda.html`: la banda con motor, disco, opto y los 20 cables numerados, con vista desarmable y WASD. Ver en linea: https://diegocruz-afk.github.io/Proyecto_Final_Electronica_UNIS/6_Montaje_3D/Maquina_3D_banda.html
  - `Protoboards_3D_miniestacion.html` (v1) y `Motor_opto_desmontado.html` (diagrama del motor): retiradas; se conservan en el repo pero ya no se publican en linea ni se actualizan.
- `7_Multisim`: esquemáticos de Multisim (11 bloques, `SISTEMA_COMPLETO.ms14` con su imagen y `SISTEMA_SOLO_CIRCUITO.ms14`, el circuito sin fuentes de prueba, con su imagen) y los scripts que los generan; ver `LEEME_MULTISIM.md`.
