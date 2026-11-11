# Guía de pruebas · Reducción 2 (5 V)

**Regla:** al terminar de armar cada bloque haces SUS pruebas, una a una, de la primera a la última. Si una no pasa, **no avances al siguiente bloque**. Son las mismas pruebas que el *Modo medición* del 3D (`2_Montaje_3D/Protoboards_3D_reduccion2.html`).

- Los valores esperados salen de **simulación en LTspice** o del **diseño original**, y cada prueba dice cuál. **No son mediciones de la máquina.** Lo que dice *a medir* aún no tiene valor.
- Lo marcado **NO validado** depende del motor real (Steren MOT-125, de 6 V) y hoy solo tiene valores con un motor *supuesto* (12 Ω, 3 mH).
- Agujeros: placa-letra-fila, como está impreso (ej. `B-A50`). Antes de energizar cada bloque nuevo, haz la prueba de resistencia 5 V–GND.
- Puntas: **ROJA (+)** y **NEGRA (−)** del multímetro. La negra casi siempre va al riel azul de GND de la placa.
- **Pendiente:** si los rieles de en medio de la BX-4135 están partidos a la mitad (hay que confirmarlo con la placa física). Las pruebas marcadas *depende de los rieles* y los puentes de 5 V y GND del 3D pueden cambiar con esa respuesta.

## 0 Alimentación de 5 V  (placa A)

### Prueba 1 · Resistencia entre 5 V y GND (sin energía)

- **Qué estamos midiendo:** La resistencia entre 5 V y GND de este bloque, con la fuente desconectada.
- **Para qué sirve:** Detecta un corto (5 V pegado a GND) antes de encender y dañar algo.
- **Antes de medir:** Fuente de 5 V DESCONECTADA. El bloque recién armado. Todavía sin sensor, chips ni motor.
- **Modo del multímetro:** Ω (resistencia)
- **Punta ROJA (+):** J1 pata +5V (**A-E62**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa A, agujero **A-riel GND izq fila 61**
- **Debe dar:** Mayor de 1 kΩ (no cerca de 0 Ω). Valor exacto: a medir (anótalo).
- **De dónde sale el valor:** regla de seguridad; valor exacto a medir
- **Si no da, revisa en este orden:**
  1. Cerca de 0 Ω: hay un corto. NO conectes la fuente.
  2. Revisa la polaridad de los electrolíticos y de los LED, y que ningún chip esté al revés (muesca).
  3. Busca un cable que una 5 V con GND y quita las piezas del bloque una por una hasta que la resistencia suba.
- **Medido:** ________

### Prueba 2 · 5 V que entran (cargador USB o power bank)

- **Qué estamos midiendo:** El voltaje que entrega la fuente de 5 V.
- **Para qué sirve:** Confirma que la fuente alimenta bien antes de armar lo demás.
- **Antes de medir:** Fuente conectada y encendida. Nada más armado.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** J1 pata +5V (**A-E62**)
- **Punta NEGRA (−):** J1 pata GND (**A-E60**)
- **Debe dar:** 5.0 V (entre 4.75 y 5.25 V)
- **De dónde sale el valor:** especificación del enunciado (5 V ± 5 %)
- **Si no da, revisa en este orden:**
  1. Si marca 0 V: fuente apagada, cable USB flojo o polaridad invertida (si marca −5 V, están al revés + y −).
  2. Menos de 4.75 V: la fuente no alcanza; prueba otro cargador o power bank.
- **Medido:** ________

### Prueba 3 · 5 V en el condensador de 1000 µF

- **Qué estamos midiendo:** El voltaje en el condensador grande de la entrada.
- **Para qué sirve:** Confirma que el condensador está bien puesto y filtra la fuente.
- **Antes de medir:** Fuente conectada.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Cin pata + (**A-I62**)
- **Punta NEGRA (−):** Cin pata - (**A-I59**)
- **Debe dar:** 5.0 V, igual que la fuente (4.75 a 5.25 V)
- **De dónde sale el valor:** igual que la fuente
- **Si no da, revisa en este orden:**
  1. Menos que la fuente: el condensador está al revés (la franja marca el −, y va a GND).
  2. Revisa que el cable del + llegue al riel de 5 V.
- **Medido:** ________

### Prueba 4 · 5 V llegan a la placa B

- **Qué estamos midiendo:** El voltaje entre el riel de 5 V y el de GND de la placa B.
- **Para qué sirve:** Confirma que la alimentación llega a las otras placas por los puentes de riel.
- **Antes de medir:** Fuente conectada; puentes de riel puestos.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** riel de +5 V de la placa B, agujero **B-riel +5 V izq fila 61**
- **Punta NEGRA (−):** riel de GND de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** 5.0 V (entre 4.75 y 5.25 V)
- **De dónde sale el valor:** igual que la fuente
- **Depende de los rieles de la BX-4135** (por confirmar con la placa física).
- **Si no da, revisa en este orden:**
  1. 0 V: falta el puente de 5 V o de GND hacia esta placa.
  2. Revisa que no se hayan cruzado el riel rojo y el azul.
  3. Pendiente: si los rieles de en medio de la BX-4135 están partidos a la mitad, hace falta un puente por mitad.
- **Medido:** ________

### Prueba 5 · 5 V llegan a la placa C

- **Qué estamos midiendo:** El voltaje entre el riel de 5 V y el de GND de la placa C.
- **Para qué sirve:** Confirma que la alimentación llega a las otras placas por los puentes de riel.
- **Antes de medir:** Fuente conectada; puentes de riel puestos.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** riel de +5 V de la placa C, agujero **C-riel +5 V izq fila 61**
- **Punta NEGRA (−):** riel de GND de la placa C, agujero **C-riel GND izq fila 61**
- **Debe dar:** 5.0 V (entre 4.75 y 5.25 V)
- **De dónde sale el valor:** igual que la fuente
- **Depende de los rieles de la BX-4135** (por confirmar con la placa física).
- **Si no da, revisa en este orden:**
  1. 0 V: falta el puente de 5 V o de GND hacia esta placa.
  2. Revisa que no se hayan cruzado el riel rojo y el azul.
  3. Pendiente: si los rieles de en medio de la BX-4135 están partidos a la mitad, hace falta un puente por mitad.
- **Medido:** ________

## 1 Sensor IR  (placa B)

### Prueba 6 · Resistencia entre 5 V y GND (sin energía)

- **Qué estamos midiendo:** La resistencia entre 5 V y GND de este bloque, con la fuente desconectada.
- **Para qué sirve:** Detecta un corto (5 V pegado a GND) antes de encender y dañar algo.
- **Antes de medir:** Fuente de 5 V DESCONECTADA. El bloque recién armado. Sensor TCRT5000 sin conectar o conectado, da igual.
- **Modo del multímetro:** Ω (resistencia)
- **Punta ROJA (+):** R1 pata 1 (**B-I52**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** Mayor de 1 kΩ (no cerca de 0 Ω). Valor exacto: a medir (anótalo).
- **De dónde sale el valor:** regla de seguridad; valor exacto a medir
- **Si no da, revisa en este orden:**
  1. Cerca de 0 Ω: hay un corto. NO conectes la fuente.
  2. Revisa la polaridad de los electrolíticos y de los LED, y que ningún chip esté al revés (muesca).
  3. Busca un cable que una 5 V con GND y quita las piezas del bloque una por una hasta que la resistencia suba.
- **Medido:** ________

### Prueba 7 · Alimentación del LM393 (U1)

- **Qué estamos midiendo:** El voltaje entre VCC (pata 8) y GND (pata 4) del LM393.
- **Para qué sirve:** Confirma que el chip recibe energía.
- **Antes de medir:** Fuente conectada.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U1 pata 8 (**B-E62**)
- **Punta NEGRA (−):** U1 pata 4 (**B-F59**)
- **Debe dar:** 5.0 V (entre 4.75 y 5.25 V)
- **De dónde sale el valor:** igual que la fuente
- **Si no da, revisa en este orden:**
  1. 0 V: falta el cable de 5 V o de GND del chip.
  2. Revisa la muesca: la pata 1 va junto a la muesca, con el chip al revés VCC queda en GND.
  3. Cable flojo o agujero equivocado.
- **Medido:** ________

### Prueba 8 · LED infrarrojo del TCRT5000

- **Qué estamos midiendo:** El voltaje en el LED infrarrojo del sensor (ánodo contra cátodo).
- **Para qué sirve:** Confirma que el LED del sensor está encendido (si no, el sensor no ve nada).
- **Antes de medir:** Fuente conectada. TCRT5000 conectado.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** TCRT pata A (**B-H51**)
- **Punta NEGRA (−):** TCRT pata K (**B-H50**)
- **Debe dar:** ≈ 1.2 V (con la cámara del celular se ve una luz violeta)
- **De dónde sale el valor:** diseño original (no simulado en la Reducción 2)
- **Si no da, revisa en este orden:**
  1. 5 V: no pasa corriente; A y K están al revés (confírmalo con el multímetro en modo diodo).
  2. 0 V: falta 5 V o la resistencia Rled (270 Ω) está abierta.
  3. Las patas del TCRT5000 hay que confirmarlas con el multímetro.
- **Medido:** ________

### Prueba 9 · Base de Q2 (b)

- **Qué estamos midiendo:** El voltaje en la entrada del transistor que amplifica la señal del sensor.
- **Para qué sirve:** Confirma el divisor de polarización y que el sensor inyecta corriente.
- **Antes de medir:** Fuente conectada. Primero SIN objeto y luego CON objeto frente al sensor (distancia: a medir).
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Q2 pata B (**B-D48**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| Sin objeto | ≈ 0.85 V |
| Con objeto | ≈ 1.15 V |
- **De dónde sale el valor:** simulación LTspice (prueba_sensor_ir)
- **Si no da, revisa en este orden:**
  1. 0 V: falta R1 (47 kΩ) o el cable del TCRT al nodo b.
  2. 5 V: falta R2 (10 kΩ) a GND.
  3. Revisa Q2: E, B, C del 2N3904 en el orden correcto.
- **Medido:** ________

### Prueba 10 · Colector de Q2

- **Qué estamos midiendo:** El voltaje en la salida del transistor amplificador.
- **Para qué sirve:** Confirma que el transistor amplifica: con objeto este voltaje baja.
- **Antes de medir:** Fuente conectada. Sin objeto y con objeto.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Q2 pata C (**B-D47**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| Sin objeto | ≈ 4.2 V |
| Con objeto | ≈ 2.9 V |
- **De dónde sale el valor:** simulación LTspice (prueba_sensor_ir)
- **Si no da, revisa en este orden:**
  1. 5 V siempre: Q2 no conduce (revisa la base y el orden de patas).
  2. Cerca de 1 V siempre: Q2 saturado o falta la resistencia RE (150 Ω).
  3. Falta Rc (680 Ω).
- **Medido:** ________

### Prueba 11 · Umbral del comparador (cursor del trimpot)

- **Qué estamos midiendo:** El voltaje de referencia con el que el comparador decide si hay objeto.
- **Para qué sirve:** Confirma el ajuste del trimpot; debe quedar entre los dos voltajes del colector.
- **Antes de medir:** Fuente conectada.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** T1 pata W (**B-C57**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** ≈ 3.3 V; debe quedar entre 2.9 V y 4.2 V. Gira el trimpot para ajustarlo.
- **De dónde sale el valor:** simulación LTspice (prueba_sensor_ir)
- **Si no da, revisa en este orden:**
  1. 0 V o 5 V fijo: el trimpot está en un extremo o falta Ra (10 kΩ) o Rb (26.8 kΩ; puedes usar 27 kΩ).
  2. Si el valor no cambia al girar: revisa las patas 1, W y 3 del trimpot.
- **Medido:** ________

### Prueba 12 · p: salida del sensor (U1 pata 1)

- **Qué estamos midiendo:** El voltaje de salida del sensor, que dice si ve un objeto o no.
- **Para qué sirve:** Confirma que el bloque completo funciona: 0 sin objeto, 5 con objeto.
- **Antes de medir:** Fuente conectada. Sin objeto y con objeto.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U1 pata 1 (**B-F62**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| Sin objeto | ≈ 0.03 V (casi 0) |
| Con objeto | ≈ 4.9 V |
- **De dónde sale el valor:** simulación LTspice (prueba_sensor_ir)
- **Si no da, revisa en este orden:**
  1. Siempre igual: ajusta el trimpot o revisa el TCRT5000 y el cable al nodo b.
  2. Siempre 0 V: revisa el LM393 (pata 3 al umbral, pata 2 al colector).
  3. Siempre 5 V: falta la resistencia Rpu (10 kΩ) o Rh está en corto.
- **Medido:** ________

## 2 Entradas E, G y RESET (74HC14)  (placa B)

### Prueba 13 · Resistencia entre 5 V y GND (sin energía)

- **Qué estamos midiendo:** La resistencia entre 5 V y GND de este bloque, con la fuente desconectada.
- **Para qué sirve:** Detecta un corto (5 V pegado a GND) antes de encender y dañar algo.
- **Antes de medir:** Fuente de 5 V DESCONECTADA. El bloque recién armado. Con el sensor ya verificado.
- **Modo del multímetro:** Ω (resistencia)
- **Punta ROJA (+):** U11 pata 14 (**B-E39**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** Mayor de 1 kΩ (no cerca de 0 Ω). Valor exacto: a medir (anótalo).
- **De dónde sale el valor:** regla de seguridad; valor exacto a medir
- **Si no da, revisa en este orden:**
  1. Cerca de 0 Ω: hay un corto. NO conectes la fuente.
  2. Revisa la polaridad de los electrolíticos y de los LED, y que ningún chip esté al revés (muesca).
  3. Busca un cable que una 5 V con GND y quita las piezas del bloque una por una hasta que la resistencia suba.
- **Medido:** ________

### Prueba 14 · Alimentación del 74HC14 (U11)

- **Qué estamos midiendo:** El voltaje entre VCC (pata 14) y GND (pata 7).
- **Para qué sirve:** Confirma que el chip recibe energía.
- **Antes de medir:** Fuente conectada.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U11 pata 14 (**B-E39**)
- **Punta NEGRA (−):** U11 pata 7 (**B-F33**)
- **Debe dar:** 5.0 V (entre 4.75 y 5.25 V)
- **De dónde sale el valor:** igual que la fuente
- **Si no da, revisa en este orden:**
  1. 0 V: falta 5 V o GND del chip.
  2. Muesca al revés: pata 14 con GND y pata 7 con 5 V dañan el chip.
  3. Cable flojo.
- **Medido:** ________

### Prueba 15 · E: entrada del toggle

- **Qué estamos midiendo:** El voltaje que llega del interruptor E.
- **Para qué sirve:** Confirma que el interruptor está bien cableado.
- **Antes de medir:** Fuente conectada. Toggle encendido y apagado.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** TBE pata E (**B-J29**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| Toggle encendido | ≈ 5 V |
| Toggle apagado | 0 V |
- **De dónde sale el valor:** simulación LTspice (prueba_logica: E = 1 o 0)
- **Si no da, revisa en este orden:**
  1. Revisa Rpe (10 kΩ a GND) y los cables del toggle: la pata central es COM y va a 5 V.
  2. Revisa Rse y Cef (filtro) y los inversores de U11.
  3. Cable flojo o agujero equivocado.
- **Medido:** ________

### Prueba 16 · E limpio (salida del 74HC14, U11)

- **Qué estamos midiendo:** La señal E ya limpia, después del filtro y los dos inversores.
- **Para qué sirve:** Confirma el filtro y el 74HC14 de esta entrada.
- **Antes de medir:** Igual que arriba.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U11 pata 4 (**B-F36**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** Igual que E: 5 V encendido, 0 V apagado.
- **De dónde sale el valor:** simulación LTspice (prueba_logica)
- **Si no da, revisa en este orden:**
  1. Si E llega bien pero esta no cambia: revisa Rse, Cef y las patas 1 a 4 de U11.
  2. Chip al revés o sin alimentación.
- **Medido:** ________

### Prueba 17 · G: micro-switch de la cubierta

- **Qué estamos midiendo:** El voltaje que llega del micro-switch de la cubierta.
- **Para qué sirve:** Confirma que el micro-switch está bien cableado.
- **Antes de medir:** Fuente conectada. Palanca presionada (cubierta cerrada) y suelta.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** TBG pata G (**B-B25**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| Palanca presionada (cubierta cerrada) | ≈ 5 V |
| Palanca suelta (cubierta abierta) | 0 V |
- **De dónde sale el valor:** simulación LTspice (prueba_logica: G = 1 o 0)
- **Si no da, revisa en este orden:**
  1. 0 V siempre: usa COM y NO (no COM y NC). Las patas del micro-switch se confirman con el multímetro.
  2. 5 V siempre: usaste COM y NC o falta Rpg (10 kΩ a GND).
  3. Cable flojo.
- **Medido:** ________

### Prueba 18 · G limpio (U11 pata 8)

- **Qué estamos midiendo:** La señal G ya limpia.
- **Para qué sirve:** Confirma el filtro y el 74HC14 de esta entrada.
- **Antes de medir:** Igual que arriba.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U11 pata 8 (**B-E33**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** Igual que G.
- **De dónde sale el valor:** simulación LTspice (prueba_logica)
- **Si no da, revisa en este orden:**
  1. Revisa Rsg, Cgf y las patas 9 y 8 de U11.
  2. Chip sin alimentación.
- **Medido:** ________

### Prueba 19 · RST: pulsador de reset

- **Qué estamos midiendo:** El voltaje que llega del pulsador RESET.
- **Para qué sirve:** Confirma que el pulsador está bien cableado.
- **Antes de medir:** Fuente conectada. Pulsador suelto y pulsado.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** TBR pata RST (**B-B29**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| Suelto | 0 V |
| Pulsado | ≈ 5 V |
- **De dónde sale el valor:** simulación LTspice (prueba_logica: RESET)
- **Si no da, revisa en este orden:**
  1. 5 V siempre: usaste dos patas del mismo lado del pulsador (usa las de la diagonal) o falta Rpr (10 kΩ a GND).
  2. 0 V al pulsar: revisa los cables del pulsador.
  3. Cable flojo.
- **Medido:** ________

### Prueba 20 · RST limpio (U11 pata 12)

- **Qué estamos midiendo:** La señal de reset ya limpia.
- **Para qué sirve:** Confirma el filtro y el 74HC14 de esta entrada.
- **Antes de medir:** Igual que arriba.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U11 pata 12 (**B-E37**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa B, agujero **B-riel GND izq fila 61**
- **Debe dar:** 0 V en reposo; ≈ 5 V mientras pulsas (también un pulso corto al encender).
- **De dónde sale el valor:** simulación LTspice (prueba_logica)
- **Si no da, revisa en este orden:**
  1. Revisa Rsr, Crf y las patas 13 y 12 de U11.
  2. Chip sin alimentación.
- **Medido:** ________

## 3 Pestillo de falla (74HC00)  (placa C)

### Prueba 21 · Resistencia entre 5 V y GND (sin energía)

- **Qué estamos midiendo:** La resistencia entre 5 V y GND de este bloque, con la fuente desconectada.
- **Para qué sirve:** Detecta un corto (5 V pegado a GND) antes de encender y dañar algo.
- **Antes de medir:** Fuente de 5 V DESCONECTADA. El bloque recién armado. Bloques anteriores verificados.
- **Modo del multímetro:** Ω (resistencia)
- **Punta ROJA (+):** U8 pata 14 (**C-E62**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa C, agujero **C-riel GND izq fila 61**
- **Debe dar:** Mayor de 1 kΩ (no cerca de 0 Ω). Valor exacto: a medir (anótalo).
- **De dónde sale el valor:** regla de seguridad; valor exacto a medir
- **Si no da, revisa en este orden:**
  1. Cerca de 0 Ω: hay un corto. NO conectes la fuente.
  2. Revisa la polaridad de los electrolíticos y de los LED, y que ningún chip esté al revés (muesca).
  3. Busca un cable que una 5 V con GND y quita las piezas del bloque una por una hasta que la resistencia suba.
- **Medido:** ________

### Prueba 22 · Alimentación del 74HC00 (U8)

- **Qué estamos midiendo:** El voltaje entre VCC (pata 14) y GND (pata 7).
- **Para qué sirve:** Confirma que el chip recibe energía.
- **Antes de medir:** Fuente conectada.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U8 pata 14 (**C-E62**)
- **Punta NEGRA (−):** U8 pata 7 (**C-F56**)
- **Debe dar:** 5.0 V (entre 4.75 y 5.25 V)
- **De dónde sale el valor:** igual que la fuente
- **Si no da, revisa en este orden:**
  1. 0 V: falta 5 V o GND del chip.
  2. Revisa la muesca (chip al revés).
  3. Cable flojo.
- **Medido:** ________

### Prueba 23 · setn: señal de falla (activa en bajo)

- **Qué estamos midiendo:** El voltaje de la línea que avisa una falla (0 V = hay falla).
- **Para qué sirve:** Confirma el pulsador FALLA y su resistencia de 10 kΩ a 5 V.
- **Antes de medir:** Fuente conectada. Pulsador FALLA suelto y pulsado.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Rsn pata 2 (**C-I51**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa C, agujero **C-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| FALLA suelto | 5 V |
| FALLA pulsado | ≈ 0 V |
- **De dónde sale el valor:** simulación LTspice (prueba_logica)
- **Si no da, revisa en este orden:**
  1. 0 V siempre: el pulsador FALLA está en corto o mal puesto (va entre setn y GND).
  2. 5 V al pulsar: cable del pulsador flojo.
  3. Falta Rsn (10 kΩ a 5 V).
- **Medido:** ________

### Prueba 24 · F: la falla guardada (U8 pata 6)

- **Qué estamos midiendo:** Si el pestillo tiene una falla guardada (5 V) o no (0 V).
- **Para qué sirve:** Confirma que la falla se guarda y que solo el RESET la borra.
- **Antes de medir:** Fuente conectada. Sigue la secuencia de la tabla en orden.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U8 pata 6 (**C-F57**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa C, agujero **C-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| 1. Recién encendido (reset automático) | 0 V |
| 2. Pulsas FALLA y sueltas | ≈ 5 V (queda guardada) |
| 3. Pulsas RESET con FALLA todavía pulsada | sigue ≈ 5 V |
| 4. Sueltas FALLA y pulsas RESET | 0 V |
- **De dónde sale el valor:** simulación LTspice (prueba_logica)
- **Si no da, revisa en este orden:**
  1. No se guarda al soltar FALLA: revisa las compuertas de U8 (patas 4 a 6 y 8 a 10).
  2. No se borra con RESET: la falla sigue pulsada (el reset solo actúa si ya no hay falla).
  3. Siempre 5 V: revisa el reset automático (Cpor 1 µF, Rpor 47 kΩ, Dpor 1N4148).
- **Medido:** ________

### Prueba 25 · F' (U8 pata 8): lo contrario de F

- **Qué estamos midiendo:** La señal contraria a F: 5 V = todo bien.
- **Para qué sirve:** Confirma la segunda compuerta del pestillo, la que habilita el motor.
- **Antes de medir:** Igual que la prueba anterior.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U8 pata 8 (**C-E56**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa C, agujero **C-riel GND izq fila 61**
- **Debe dar:** 5 V sin falla; 0 V con falla guardada.
- **De dónde sale el valor:** simulación LTspice (prueba_logica)
- **Si no da, revisa en este orden:**
  1. Debe ser lo contrario de F; si no, revisa la compuerta de U8 que da F'.
- **Medido:** ________

## 4 Lógica de decisión (74HC08) y LED de objeto  (placa C)

### Prueba 26 · Resistencia entre 5 V y GND (sin energía)

- **Qué estamos midiendo:** La resistencia entre 5 V y GND de este bloque, con la fuente desconectada.
- **Para qué sirve:** Detecta un corto (5 V pegado a GND) antes de encender y dañar algo.
- **Antes de medir:** Fuente de 5 V DESCONECTADA. El bloque recién armado. Motor y potencia desconectados.
- **Modo del multímetro:** Ω (resistencia)
- **Punta ROJA (+):** U9 pata 14 (**C-E44**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa C, agujero **C-riel GND izq fila 61**
- **Debe dar:** Mayor de 1 kΩ (no cerca de 0 Ω). Valor exacto: a medir (anótalo).
- **De dónde sale el valor:** regla de seguridad; valor exacto a medir
- **Si no da, revisa en este orden:**
  1. Cerca de 0 Ω: hay un corto. NO conectes la fuente.
  2. Revisa la polaridad de los electrolíticos y de los LED, y que ningún chip esté al revés (muesca).
  3. Busca un cable que una 5 V con GND y quita las piezas del bloque una por una hasta que la resistencia suba.
- **Medido:** ________

### Prueba 27 · Alimentación del 74HC08 (U9)

- **Qué estamos midiendo:** El voltaje entre VCC (pata 14) y GND (pata 7).
- **Para qué sirve:** Confirma que el chip recibe energía.
- **Antes de medir:** Fuente conectada. Motor desconectado.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U9 pata 14 (**C-E44**)
- **Punta NEGRA (−):** U9 pata 7 (**C-F38**)
- **Debe dar:** 5.0 V (entre 4.75 y 5.25 V)
- **De dónde sale el valor:** igual que la fuente
- **Si no da, revisa en este orden:**
  1. 0 V: falta 5 V o GND del chip.
  2. Revisa la muesca (chip al revés).
  3. Cable flojo.
- **Medido:** ________

### Prueba 28 · M: permiso del motor (U9 pata 6)

- **Qué estamos midiendo:** Si la máquina tiene permiso de mover el motor.
- **Para qué sirve:** Confirma M = E·G·F' (el motor solo corre con E = 1, G = 1 y sin falla).
- **Antes de medir:** Fuente conectada. MOTOR DESCONECTADO. Cambia E, G y FALLA según la tabla.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U9 pata 6 (**C-F39**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa C, agujero **C-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| E = 1, G = 1, sin falla | 5 V |
| E = 0, o G = 0, o hay falla | 0 V |
- **De dónde sale el valor:** simulación LTspice (prueba_logica: 16 de 16 combinaciones)
- **Si no da, revisa en este orden:**
  1. 0 V con todo bien: revisa E, G y F' en la entrada de U9.
  2. Revisa la muesca y las patas 4 a 6 de U9.
  3. Cable flojo.
- **Medido:** ________

### Prueba 29 · N: velocidad normal (U9 pata 8)

- **Qué estamos midiendo:** Si debe correr a velocidad normal (permiso y sin objeto).
- **Para qué sirve:** Confirma N = M·P'.
- **Antes de medir:** Motor desconectado. Con permiso (M = 5 V); sin objeto y con objeto.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U9 pata 8 (**C-E38**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa C, agujero **C-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| M = 5 V y sin objeto | 5 V |
| M = 5 V y con objeto | 0 V |
| M = 0 V | 0 V |
- **De dónde sale el valor:** simulación LTspice (prueba_logica)
- **Si no da, revisa en este orden:**
  1. Siempre 0 V: revisa p' (U8 pata 11) y U9 (patas 9, 10 y 8).
  2. Cable flojo.
- **Medido:** ________

### Prueba 30 · L: velocidad reducida (U9 pata 11), sin uso en el hardware

- **Qué estamos midiendo:** Si debería ir lento (permiso y objeto).
- **Para qué sirve:** Confirma L = M·P. Esta salida no va a ninguna pieza; solo sirve para probar la lógica.
- **Antes de medir:** Motor desconectado. M = 5 V; sin objeto y con objeto.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** U9 pata 11 (**C-E41**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa C, agujero **C-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| M = 5 V y con objeto | 5 V |
| M = 5 V y sin objeto | 0 V |
| M = 0 V | 0 V |
- **De dónde sale el valor:** simulación LTspice (prueba_logica)
- **Si no da, revisa en este orden:**
  1. Siempre 0 V: revisa p y las patas 12, 13 y 11 de U9.
- **Medido:** ________

### Prueba 31 · LED de objeto

- **Qué estamos midiendo:** El voltaje en el LED verde de objeto (ánodo contra cátodo).
- **Para qué sirve:** Confirma que el LED enciende cuando el sensor ve un objeto.
- **Antes de medir:** Fuente conectada. Sin objeto y con objeto.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Dlo pata A (**C-D33**)
- **Punta NEGRA (−):** Dlo pata K (**C-D31**)
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| Con objeto | ≈ 2.0 V (enciende, unos 4.4 mA) |
| Sin objeto | ≈ 5 V (apagado) |
- **De dónde sale el valor:** simulación LTspice (prueba_logica)
- **Si no da, revisa en este orden:**
  1. Nunca enciende: LED al revés (la pata larga es el ánodo A) o Rlo (680 Ω) abierta.
  2. Siempre encendido: p' (U8 pata 11) siempre en 0 V; revisa el sensor.
  3. Cable flojo.
- **Medido:** ________

## 5 Potencia con motor  (placa A)

### Prueba 32 · Resistencia entre 5 V y GND (sin energía)

- **Qué estamos midiendo:** La resistencia entre 5 V y GND de este bloque, con la fuente desconectada.
- **Para qué sirve:** Detecta un corto (5 V pegado a GND) antes de encender y dañar algo.
- **Antes de medir:** Fuente de 5 V DESCONECTADA. El bloque recién armado. MOTOR DESCONECTADO (sin los cables M+ y M−).
- **Modo del multímetro:** Ω (resistencia)
- **Punta ROJA (+):** Cb pata + (**A-D48**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa A, agujero **A-riel GND izq fila 61**
- **Debe dar:** Mayor de 1 kΩ (no cerca de 0 Ω). Valor exacto: a medir (anótalo).
- **De dónde sale el valor:** regla de seguridad; valor exacto a medir
- **Si no da, revisa en este orden:**
  1. Cerca de 0 Ω: hay un corto. NO conectes la fuente.
  2. Revisa la polaridad de los electrolíticos y de los LED, y que ningún chip esté al revés (muesca).
  3. Busca un cable que una 5 V con GND y quita las piezas del bloque una por una hasta que la resistencia suba.
- **Medido:** ________

### Prueba 33 · Compuerta del IRLZ44N (señal m)

- **Qué estamos midiendo:** El voltaje en la compuerta del MOSFET que da corriente al motor.
- **Para qué sirve:** Confirma que el permiso M llega al MOSFET.
- **Antes de medir:** Fuente conectada. MOTOR DESCONECTADO. M = 0 y M = 1.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** M1 pata G (**A-F40**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa A, agujero **A-riel GND izq fila 61**
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| M = 0 | 0 V |
| M = 1 | ≈ 5 V |
- **De dónde sale el valor:** simulación LTspice (prueba_potencia_Rs15_bjt; el chip real puede dar un poco menos)
- **Si no da, revisa en este orden:**
  1. Siempre 0 V: M = 0 o el cable de m no llega desde la placa C.
  2. Rpd (10 kΩ a GND) no debe estar en corto.
  3. Revisa el orden G-D-S del IRLZ44N.
- **Medido:** ________

### Prueba 34 · Puente 2N3904: base contra emisor

- **Qué estamos midiendo:** El voltaje de la base del transistor que puentea a Rs.
- **Para qué sirve:** Confirma que N enciende el puente (sin objeto) y lo apaga (con objeto).
- **Antes de medir:** Fuente conectada. MOTOR DESCONECTADO. N = 1 y N = 0.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Qp pata B (**A-G44**)
- **Punta NEGRA (−):** Qp pata E (**A-G45**)
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| N = 1 (sin objeto) | ≈ 0.9 V (entre 0.7 y 0.95 V) |
| N = 0 (con objeto) | ≈ 0 V |
- **De dónde sale el valor:** simulación LTspice (prueba_potencia_Rs15_bjt)
- **Si no da, revisa en este orden:**
  1. 0 V siempre: falta Rb (1 kΩ) o el cable de n desde la placa C.
  2. Revisa E, B y C del 2N3904.
  3. El 2N3904 aguanta 200 mA y el arranque pide más (ver informe): puede ser un problema con el motor puesto.
- **Medido:** ________

### Prueba 35 · Corriente del motor a 5 V

- **Qué estamos midiendo:** La corriente que realmente pide el motor Steren a 5 V.
- **Para qué sirve:** Con este dato se elige Rs y se decide si el 2N3904 alcanza.
- **Antes de medir:** Fuente conectada. M = 1. El multímetro en serie: abre el cable M+ y pon el multímetro en medio.
- **Modo del multímetro:** A DC (en serie)
- **Punta ROJA (+):** TBM pata M+ (**A-A45**)
- **Punta NEGRA (−):** el hilo M+ del motor (no está en la placa)
- **Debe dar:** A medir. La simulación usa un motor SUPUESTO (12 Ω, ≈ 134 mA en marcha y ≈ 390 mA al arrancar).
- **De dónde sale el valor:** a medir (motor real)
- **NO validado todavía:** depende del motor real.
- **Si no da, revisa en este orden:**
  1. Más de 200 mA al arrancar: el 2N3904 queda corto; usa un MOSFET como puente.
  2. Muy distinta de 134 mA: hay que reajustar Rs.
- **Medido:** ________

### Prueba 36 · dm: lado negativo del motor (contra GND)

- **Qué estamos midiendo:** El voltaje en el lado negativo del motor.
- **Para qué sirve:** Muestra cuánto voltaje pierde el motor en el MOSFET y en Rs.
- **Antes de medir:** Fuente conectada. MOTOR CONECTADO.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Dfw pata A (**A-B43**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa A, agujero **A-riel GND izq fila 61**
- **Debe dar:** Ver tabla (motor supuesto: valores a medir con el Steren)

| Condición | Valor esperado |
|---|---|
| Motor parado (M = 0) | ≈ 5 V |
| Sin objeto (N = 1) | ≈ 0.1 V (a medir) |
| Con objeto (N = 0) | ≈ 1.9 V (a medir; depende del motor) |
- **De dónde sale el valor:** simulación LTspice con motor SUPUESTO; NO validado con el motor real
- **NO validado todavía:** depende del motor real.
- **Si no da, revisa en este orden:**
  1. Siempre 5 V con M = 1: el IRLZ44N no conduce (¿es de nivel lógico?, ¿patas G-D-S al revés?).
  2. Mide primero la corriente del motor (prueba anterior).
- **Medido:** ________

## 6 LED rojo y ajuste de la velocidad lenta  (placa A)

### Prueba 37 · Resistencia entre 5 V y GND (sin energía)

- **Qué estamos midiendo:** La resistencia entre 5 V y GND de este bloque, con la fuente desconectada.
- **Para qué sirve:** Detecta un corto (5 V pegado a GND) antes de encender y dañar algo.
- **Antes de medir:** Fuente de 5 V DESCONECTADA. El bloque recién armado. Potencia y motor ya verificados.
- **Modo del multímetro:** Ω (resistencia)
- **Punta ROJA (+):** Rl pata 1 (**A-B31**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa A, agujero **A-riel GND izq fila 61**
- **Debe dar:** Mayor de 1 kΩ (no cerca de 0 Ω). Valor exacto: a medir (anótalo).
- **De dónde sale el valor:** regla de seguridad; valor exacto a medir
- **Si no da, revisa en este orden:**
  1. Cerca de 0 Ω: hay un corto. NO conectes la fuente.
  2. Revisa la polaridad de los electrolíticos y de los LED, y que ningún chip esté al revés (muesca).
  3. Busca un cable que una 5 V con GND y quita las piezas del bloque una por una hasta que la resistencia suba.
- **Medido:** ________

### Prueba 38 · LED rojo de falla

- **Qué estamos midiendo:** El voltaje en el LED rojo (ánodo contra cátodo).
- **Para qué sirve:** Confirma que la alarma luminosa enciende cuando hay una falla guardada.
- **Antes de medir:** Fuente conectada. Sin falla y con falla guardada (pulsa FALLA y suelta).
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Dl pata A (**A-D27**)
- **Punta NEGRA (−):** Dl pata K (**A-D25**)
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| Sin falla | 0 V (apagado) |
| Con falla guardada | ≈ 2 V (enciende; a medir) |
- **De dónde sale el valor:** diseño original (≈ 6 mA); no simulado en la Reducción 2
- **Si no da, revisa en este orden:**
  1. Hay falla y no enciende: LED al revés (la pata larga es el ánodo A) o Rl (470 Ω) abierta.
  2. Siempre encendido: F está en 1; revisa el pestillo (bloque 3).
- **Medido:** ________

### Prueba 39 · Caída en Rs (entre dm y ds)

- **Qué estamos midiendo:** El voltaje que se pierde en la resistencia Rs.
- **Para qué sirve:** Es lo que baja la velocidad cuando hay objeto.
- **Antes de medir:** Fuente conectada. Motor conectado. Sin objeto y con objeto.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Rs pata 1 (**A-E43**)
- **Punta NEGRA (−):** Rs pata 2 (**A-E38**)
- **Debe dar:** Ver tabla (motor supuesto)

| Condición | Valor esperado |
|---|---|
| Sin objeto | ≈ 0.1 V |
| Con objeto | ≈ 1.9 V (con Rs = 15 Ω y el motor supuesto; a medir) |
- **De dónde sale el valor:** simulación LTspice con motor SUPUESTO; NO validado con el motor real
- **NO validado todavía:** depende del motor real.
- **Si no da, revisa en este orden:**
  1. Siempre alta: el 2N3904 no puentea a Rs (revisa Rb y n).
  2. No sube con objeto: Rs en corto.
  3. Se ajusta por prueba: prueba 10, 15 y 22 Ω.
- **Medido:** ________

### Prueba 40 · Velocidad lenta contra velocidad normal

- **Qué estamos midiendo:** Cuántas vueltas da el eje con objeto comparado con sin objeto.
- **Para qué sirve:** Confirma que con objeto la velocidad baja a 40-60 % de la normal.
- **Antes de medir:** Fuente conectada. Motor conectado. Mide sin objeto y con objeto.
- **Modo del multímetro:** vueltas por segundo
- **Punta ROJA (+):** no se mide con multímetro
- **Punta NEGRA (−):** cuenta las vueltas del eje con el celular (video) o un tacómetro
- **Debe dar:** Entre 40 % y 60 % de la velocidad normal. Valor exacto: a medir.
- **De dónde sale el valor:** a medir (motor real); simulación solo orientativa
- **NO validado todavía:** depende del motor real.
- **Si no da, revisa en este orden:**
  1. Menos de 40 %: baja Rs (prueba 10 Ω).
  2. Más de 60 %: sube Rs (prueba 22 Ω).
  3. Con la simulación (motor supuesto): 10 Ω da 66 %, 15 Ω da 50 % y 22 Ω da 29 %; con el motor real saldrá distinto.
- **Medido:** ________

## 7 Buzzer de falla (alarma acústica)  (placa A)

### Prueba 41 · Resistencia entre 5 V y GND (sin energía)

- **Qué estamos midiendo:** La resistencia entre 5 V y GND de este bloque, con la fuente desconectada.
- **Para qué sirve:** Detecta un corto (5 V pegado a GND) antes de encender y dañar algo.
- **Antes de medir:** Fuente de 5 V DESCONECTADA. El bloque recién armado. Placa A: buzzer, 2N3904, 4.7 kΩ y diodo ya puestos. El buzzer es magnético: puede marcar poco al principio mientras el multímetro lo carga; espera a que se estabilice.
- **Modo del multímetro:** Ω (resistencia)
- **Punta ROJA (+):** Dz pata K (**A-C17**)
- **Punta NEGRA (−):** riel azul (−, GND) de la placa A, agujero **A-riel GND izq fila 61**
- **Debe dar:** Mayor de 1 kΩ (no cerca de 0 Ω). Valor exacto: a medir (anótalo).
- **De dónde sale el valor:** regla de seguridad; valor exacto a medir
- **Si no da, revisa en este orden:**
  1. Cerca de 0 Ω: hay un corto. NO conectes la fuente.
  2. Revisa la polaridad de los electrolíticos y de los LED, y que ningún chip esté al revés (muesca).
  3. Busca un cable que una 5 V con GND y quita las piezas del bloque una por una hasta que la resistencia suba.
- **Medido:** ________

### Prueba 42 · Colector del 2N3904 sin falla (buzzer en silencio)

- **Qué estamos midiendo:** El voltaje entre el colector y el emisor del 2N3904 del buzzer.
- **Para qué sirve:** Confirma que sin falla el transistor está apagado y el buzzer no suena.
- **Antes de medir:** Fuente conectada. Cubierta cerrada y sin pulsar FALLA (F = 0). Buzzer en silencio.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Qz pata C (**A-D21**)
- **Punta NEGRA (−):** Qz pata E (**A-D23**)
- **Debe dar:** ≈ 5 V (entre 4.8 y 5.1 V)

| Condición | Valor esperado |
|---|---|
| Sin falla (F = 0) | ≈ 5 V |
| Con falla guardada (F = 1) | 0.05 a 0.3 V (a medir) |
- **De dónde sale el valor:** simulación LTspice (prueba_buzzer.cir) con buzzer SUPUESTO de 400 Ω (12.5 mA); el buzzer real: a medir
- **NO validado todavía:** depende del buzzer real.
- **Si no da, revisa en este orden:**
  1. Cerca de 0 V y suena: F = 1 (revisa el pestillo, bloque 3) o la base está pegada a 5 V o a f sin la resistencia de 4.7 kΩ.
  2. Marca 0 V y no suena: el colector no llega al buzzer (revisa el cable entre las filas del colector y del buzzer) o el buzzer está al revés/abierto.
  3. Entre 1 y 4 V: el transistor conduce a medias; revisa que la base no toque otra fila.
- **Medido:** ________

### Prueba 43 · Base del 2N3904 del buzzer

- **Qué estamos midiendo:** El voltaje entre la base y el emisor del 2N3904 del buzzer.
- **Para qué sirve:** Confirma que f llega a la base por la resistencia de 4.7 kΩ y que el transistor conduce con falla.
- **Antes de medir:** Fuente conectada. Mide sin falla y luego con falla guardada (pulsa FALLA y suelta).
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Qz pata B (**A-D22**)
- **Punta NEGRA (−):** Qz pata E (**A-D23**)
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| Sin falla (F = 0) | ≈ 0 V (menos de 0.1 V) |
| Con falla guardada (F = 1) | 0.65 a 0.85 V |
- **De dónde sale el valor:** simulación LTspice (prueba_buzzer.cir) con buzzer SUPUESTO de 400 Ω (12.5 mA); el buzzer real: a medir
- **NO validado todavía:** depende del buzzer real.
- **Si no da, revisa en este orden:**
  1. Con falla marca 0 V: la resistencia de 4.7 kΩ no llega a f (revisa el cable de f) o la base está en otra fila.
  2. Con falla marca más de 0.9 V: la resistencia o el transistor están mal (¿patas E-B-C al revés?).
  3. Sin falla marca más de 0.1 V: f no baja a 0 V; revisa el pestillo.
- **Medido:** ________

### Prueba 44 · Caída en la resistencia de base de 4.7 kΩ

- **Qué estamos midiendo:** El voltaje entre los dos extremos de la resistencia de 4.7 kΩ (la corriente de base es ese voltaje entre 4.7 kΩ).
- **Para qué sirve:** Da la corriente de base real: debe ser suficiente para saturar el transistor.
- **Antes de medir:** Fuente conectada. Falla guardada (pulsa FALLA y suelta).
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Rbz pata 1 (**A-B22**)
- **Punta NEGRA (−):** Rbz pata 2 (**A-B18**)
- **Debe dar:** 2.9 a 4.2 V (corriente de base de 0.6 a 0.9 mA)
- **De dónde sale el valor:** simulación LTspice (prueba_buzzer.cir) con buzzer SUPUESTO de 400 Ω (12.5 mA); el buzzer real: a medir
- **NO validado todavía:** depende del buzzer real.
- **Si no da, revisa en este orden:**
  1. Casi 0 V: no pasa corriente por la base (transistor abierto o resistencia mal puesta).
  2. Menos de 2.9 V: f está débil; revisa que el LED rojo y el 74HC00 no estén sobrecargados.
  3. Calcula Ib = voltaje / 4700; para un buzzer de 12.5 mA con ganancia 100 basta 0.13 mA.
- **Medido:** ________

### Prueba 45 · 5 V en el buzzer con falla

- **Qué estamos midiendo:** El voltaje que recibe el buzzer (entre sus dos patas).
- **Para qué sirve:** Confirma que, con falla, el buzzer recibe casi los 5 V completos y suena.
- **Antes de medir:** Fuente conectada. Mide sin falla y con falla guardada.
- **Modo del multímetro:** V DC
- **Punta ROJA (+):** Buzzer pata + (**A-A1**)
- **Punta NEGRA (−):** Buzzer pata - (**A-A4**)
- **Debe dar:** Ver tabla

| Condición | Valor esperado |
|---|---|
| Sin falla (F = 0) | ≈ 0 V (menos de 0.3 V) |
| Con falla guardada (F = 1) | ≈ 4.9 V (4.5 a 5 V; a medir) |
- **De dónde sale el valor:** simulación LTspice (prueba_buzzer.cir) con buzzer SUPUESTO de 400 Ω (12.5 mA); el buzzer real: a medir
- **NO validado todavía:** depende del buzzer real.
- **Si no da, revisa en este orden:**
  1. Con falla marca poco (menos de 4.5 V): el transistor no satura; revisa la prueba de la base y la caída en 4.7 kΩ.
  2. Con falla marca 5 V y no suena: el buzzer está al revés (la pata + o la marcada va a 5 V) o está dañado: pruébalo directo a 5 V.
  3. Sin falla marca más de 0.3 V: hay fuga por el transistor; revisa que la base no toque otra fila.
- **Medido:** ________

### Prueba 46 · El buzzer suena con la falla y se apaga con RESET

- **Qué estamos midiendo:** Si el buzzer suena exactamente cuando enciende el LED rojo.
- **Para qué sirve:** Es la alarma acústica que pide el enunciado, ligada a la misma señal f del LED rojo.
- **Antes de medir:** Fuente conectada. Cubierta cerrada y E en 1.
- **Modo del multímetro:** oído
- **Punta ROJA (+):** no se mide con multímetro: se escucha
- **Punta NEGRA (−):** oído (y el LED rojo como referencia)
- **Debe dar:** Suena con falla guardada y se apaga con RESET (ver tabla)

| Condición | Valor esperado |
|---|---|
| Sin falla | silencio, LED rojo apagado |
| Pulso FALLA | suena, LED rojo enciende, motor parado |
| Suelto FALLA | sigue sonando (falla guardada) |
| RESET con FALLA suelta | se apaga el buzzer y el LED rojo |
- **De dónde sale el valor:** lógica del pestillo (simulada en 1_LTspice/resultado_logica.md); el sonido del buzzer real: a medir
- **NO validado todavía:** depende del buzzer real.
- **Si no da, revisa en este orden:**
  1. Suena al encender sin pulsar nada: el reset automático no limpió F; revisa el pestillo (bloque 3).
  2. Suena al soltar FALLA y deja de sonar solo: el pestillo no guarda; revisa el bloque 3.
  3. No se apaga con RESET: suelta FALLA antes de pulsar RESET (con FALLA pulsada el RESET no limpia).
- **Medido:** ________

## Cables a los dispositivos externos (se confirman con multímetro, no se dan por hechos)

| Dispositivo | Pata del dispositivo | Agujero | Red |
|---|---|---|---|
| FUENTE | +5V | **A-E62** | v5 |
| FUENTE | GND | **A-E60** | 0 |
| TCRT | A | **B-H51** | SEN.nled |
| TCRT | K | **B-H50** | 0 |
| TCRT | C | **B-H49** | v5 |
| TCRT | E | **B-H48** | b |
| SW_E | 5V | **B-J31** | v5 |
| SW_R | 5V | **B-B31** | v5 |
| SW_E | E | **B-J29** | ein |
| SW_R | RST | **B-B29** | rin |
| SW_G | 5V | **B-B27** | v5 |
| SW_G | G | **B-B25** | gin |
| SW_F | GND | **C-G53** | 0 |
| SW_F | setn | **C-G51** | setn |
| MOTOR | M+ | **A-A45** | v5 |
| MOTOR | M- | **A-A43** | dm |

Confirmar con el multímetro: TCRT5000 (modo diodo: LED entre A y K), toggle (continuidad: la pata central es COM), micro-switch (COM, NO, NC con la palanca) y las 4 patas del pulsador (las dos de un mismo lado están unidas por dentro).

Lógica que debe cumplirse: M = E·G·F', N = M·P', L = M·P (solo mueve el motor E = 1, G = 1, F = 0). Simulada en `1_LTspice/resultado_logica.md`.
