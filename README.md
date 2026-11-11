# Miniestación industrial automatizada (proyecto final de Electrónica, UNIS)

**Integrantes del grupo:** Sharly Abraham Alvarado Alvarez, Kenneth Raúl Bernales Yee, Diego Rodrigo Cruz Duarte, José Javier de León Aguilar, Oscar Mauricio Fletes Marroquín, Jorge André Gil Leonardo, Jose Eduardo Piedrasanta García, Josué Darío Sacol Cojón.

Minibanda transportadora con motor DC de 12 V (máx. 500 mA), hecha con electrónica analógica y compuertas 74HC, sin microcontroladores. Se arma en protoboard.

- `1_Arquitectura`: diagrama general.
- `2_LTspice`: esquemáticos (completo y por bloques), `SISTEMA_SOLO_CIRCUITO.asc` (la misma hoja con títulos y notas fuera de los cables; solo el circuito en una fila, igual que el 3D, sin fuentes de simulación; no simula) y sus PNG.
- `3_archivos_tecnicos`: el circuito en texto (`sistema.inc`), los modelos, los scripts que generan los esquemáticos, el 3D y la lista de compras, y las simulaciones.
- `4_Documentacion`: guía de componentes, explicación por bloques y dos guías del esquemático por bloques con imágenes: una de Multisim (`Guia_del_esquematico_por_bloques.html`) y una de LTspice (`Guia_del_esquematico_LTspice.html`).
- `5_Compras_y_Pruebas`: lista de compras (PDF) y guía de pruebas.
- `6_Montaje_3D`: paginas 3D (abrir el `.html` en el navegador):
  - `Protoboards_3D_miniestacion_v3.html`: la guia 3D VIGENTE (placas A, B y C = las 3 protoboards de la PRO'S KIT BX-4135, D y E sueltas; 120 piezas, 252 cables a ras sin cruces; pasos y pruebas por bloque; modo medición para encontrar errores bloque por bloque; piezas externas dibujadas como son). Ver en linea: https://diegocruz-afk.github.io/Proyecto_Final_Electronica_UNIS/6_Montaje_3D/Protoboards_3D_miniestacion_v3.html
  - `Lista_conexiones_v3.html`: lista de conexiones pata por pata de cada bloque, con agujeros, cables y pruebas. Ver en linea: https://diegocruz-afk.github.io/Proyecto_Final_Electronica_UNIS/6_Montaje_3D/Lista_conexiones_v3.html
  - `Protoboards_3D_miniestacion_v2.html` (anterior; su muesca de los CI esta en el extremo equivocado, usar la v3): la guia 3D anterior (5 protoboards, 120 piezas, 229 cables, con el LED de objeto en la placa B). Ver en linea: https://diegocruz-afk.github.io/Proyecto_Final_Electronica_UNIS/6_Montaje_3D/Protoboards_3D_miniestacion_v2.html
  - `Maquina_3D_banda.html`: la banda con motor, disco, opto y los 20 cables numerados, con vista desarmable y WASD. Ver en linea: https://diegocruz-afk.github.io/Proyecto_Final_Electronica_UNIS/6_Montaje_3D/Maquina_3D_banda.html
  - `Protoboards_3D_miniestacion.html` (v1) y `Motor_opto_desmontado.html` (diagrama del motor): retiradas; se conservan en el repo pero ya no se publican en linea ni se actualizan.
- `7_Multisim`: esquemáticos de Multisim (11 bloques, `SISTEMA_COMPLETO.ms14` con su imagen y `SISTEMA_SOLO_CIRCUITO.ms14`, el circuito sin fuentes de prueba, con su imagen) y los scripts que los generan; ver `LEEME_MULTISIM.md`.
- `8_Maqueta_corte_laser`: piezas de la maqueta de la banda para corte láser (DWG de AutoCAD 2010, en centímetros, cartón de 1 mm), `LISTA_DE_PIEZAS.txt` y `MEMORIA_DE_MEDIDAS.txt`; los DXF de respaldo están en `DXF_respaldo`.
- `9_Entregables_profesor`: el paquete de entrega (informe técnico en PDF y Word, simulaciones y capturas, montaje y maqueta, lista de compras, guía de pruebas, guion del video, presentación y preguntas de defensa). Empezar por `00_LEEME_Entregables.md`.
- `CONTEXTO_PARA_CLAUDE_WEB.md`: resumen del proyecto para pegar en una conversación nueva de Claude.
