"""Adapta plantilla_r2.html (copia de la v3 del original) a la Reduccion 2. Se corre UNA vez sobre la copia sin modificar (hace respaldo plantilla_v3_original.html)."""
import os, re, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(AQUI, "plantilla_r2.html")
BK = os.path.join(AQUI, "plantilla_v3_original.html")
if not os.path.exists(BK):
    shutil.copy(P, BK)
s = open(BK, encoding="utf-8").read()


def cut(a, b, new="", incl_b=False):
    """reemplaza desde el texto a hasta justo antes de b (o incluyendo b)"""
    global s
    i = s.index(a); j = s.index(b, i)
    s = s[:i] + new + s[j + (len(b) if incl_b else 0):]


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


# ---------- texto ----------
rep('rails = shL ? [12, 13] : [-3, -2, 12, 13]', 'rails = [-3, -2, 12, 13]')      # cada placa dibuja sus 2 pares de rieles (el de en medio se repite en la misma posicion)
rep('(shL ? [12.5] : [-2.5, 12.5]).forEach', '[-2.5, 12.5].forEach')

rep("decal('0.5 Ω 5 W',", "decal(String(p.val).replace(/ \(ajustar\)/, ''),")      # la resistencia de potencia dice su valor real

rep(": 'Suelda ' + p.short", ": 'Coloca ' + p.short")        # en protoboard no se suelda
rep("Protoboards 3D v3 · miniestación industrial", "Protoboards 3D · Reducción 2 (5 V)")
s = re.sub(r"<title>.*?</title>", "<title>Reducción 2 · Protoboards 3D</title>", s, count=1)
cut('<div class="sub">', '</div>', '<div class="sub">Guía para armar la <b>Reducción 2</b> (sensor IR, lógica, pestillo de falla, LED de objeto y potencia a <b>5 V directos</b>). Placas <b>A, B y C</b> = las 3 protoboards de la <b>PRO\'S KIT BX-4135</b> (63 filas, letras J-F a la izquierda y E-A a la derecha, filas numeradas desde 0 abajo como en tu tablero; los rieles de en medio se comparten). Reparto parejo: A: entrada de 5 V, potencia y LED rojo · B: sensor IR y entradas E, G, RESET (74HC14) · C: pestillo, decisión (74HC00, 74HC08) y LED de objeto. Es una versión de validación por fases, no la entrega final.', incl_b=False)
rep("(o teclas 1-5; 0 = todas)", "(o teclas 1-3; 0 = todas)")
rep("(GND, 5 V, 12 V)", "(GND, 5 V)")

# ---------- trimpot: tornillo visible (antes quedaba dentro del cuerpo) con ranura, y etiquetas 1 / W / 3 sobre cada pata ----------
rep("""    const sc = new THREE.Mesh(new THREE.CylinderGeometry(1.7, 1.7, .7, 20), mat(0xd6b24a, {metalness: .7, roughness: .35})); sc.position.set(cx, 1 + 9.8, cz); g.add(sc);
    decal(p.val, 8, 2.2, 40, '#fff', cx, 6, cz + 2.4, false);""",
"""    // Bourns 3296W (datasheet): tornillo chico (2.19 mm) en la cara de arriba, a 1.27 mm del extremo del lado de la pata 1 (CCW); pata 2 = cursor W; pata 3 = CW
    const sgn = pts[0].x < pts[2].x ? -1 : 1, sx = cx + sgn * (P + 2.5 - 1.27);
    const sc = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.1, .9, 24), mat(0xd6b24a, {metalness: .7, roughness: .35})); sc.position.set(sx, 10.9, cz); g.add(sc);
    const ranura = new THREE.Mesh(new THREE.BoxGeometry(2.0, 1.0, .5), mat(0x3a2f10, {roughness: .8})); ranura.position.set(sx, 10.9, cz); g.add(ranura);
    decal(p.val, 8, 2.2, 40, '#fff', cx, 8, cz + 2.4, false);
    p.pins.forEach((q, i) => decal(q.n, 2.6, 2.6, 56, q.n === 'W' ? '#ffd24a' : '#ffffff', pts[i].x, 4, pts[i].z + 2.4, false));""")

# ---------- panel: se quitan simulacion, 'que medir' generico, resaltar red y 'Mostrar' (los controles quedan ocultos para que el codigo siga andando) ----------
cut('<div class="sec"><h2>Funcionamiento (simulación)</h2>', '<div class="sec"><h2>Moverte</h2>')
cut('<div class="sec"><h2>Qué medir (multímetro / osciloscopio)</h2>', '<div class="sec"><h2>Buscar pieza</h2>')
i = s.index('<div class="sec"><h2>Resaltar una red (quita el resto)</h2>'); j = s.index('<div class="sec"><h2>Armado paso a paso</h2>')
bloque = s[i:j]
ocultos = '<div id="ocultos" style="display:none"><div id="measList"></div><div id="nets"></div>' + "".join(re.findall(r'<label class="chk">.*?</label>', bloque, re.S)) + '</div>\n\n  '
s = s[:i] + ocultos + s[j:]

# ---------- dispositivos externos ----------
cut("  const shaft = new THREE.Mesh", "  term('MOTOR', 'M+'")                      # eje y disco de 20 ranuras (no van en la Reduccion 2)
rep("label(['MOTOR DC 12 V', 'caja reductora + disco de 20 ranuras']", "label(['MOTOR (Steren MOT-125, 6 V: se prueba a 5 V)', 'caja reductora 100:1 · mide su corriente antes de conectarlo']")
cut("  const ox = mx - 18, oz = bz + 52", "  const sx = bx - 70;")                    # optointerruptor
cut("  const cvG = new THREE.Group()", "  // ---- piezas externas dibujadas como son")  # cubierta transparente de la banda
cut("  const ntc = new THREE.Mesh", "  const px0 = X(")                              # NTC
rep("term('FUENTE', '+12V'", "term('FUENTE', '+5V'")
rep("label(['FUENTE EXTERNA 12 V ≥ 2 A', 'certificada']", "label(['FUENTE EXTERNA 5 V', 'cargador USB o power bank · jack o cable USB']")
rep("label(['BANDA TRANSPORTADORA', 'con un objeto de prueba']", "label(['BANDA (referencia)', 'el motor mueve la banda · objeto de prueba']")
# pulsador: se convierte en funcion para dibujar RESET y FALLA
i = s.index("  // pulsador normalmente abierto 6 x 6 x 15 mm"); j = s.index("})();", i)
blk = s[i:j]
blk = blk.replace("  {\n    const K = 2.1, gp = V3(px0 + 84, -4, pz + 6), bg", "  const pulsador = (dx, devName, devA, devB, titulo, sub) => {\n    const K = 2.1, gp = V3(px0 + dx, -4, pz + 6), bg")
blk = blk.replace("term('SW_R', dev, w, ORO)", "term(devName, dev, w, ORO)")
blk = blk.replace("leg('A1', -1, 1, '5V'); leg('A2', -1, -1, null); leg('B1', 1, 1, null); leg('B2', 1, -1, 'RST');", "leg('A1', -1, 1, devA); leg('A2', -1, -1, null); leg('B1', 1, 1, null); leg('B2', 1, -1, devB);")
blk = blk.replace("label(['PULSADOR RESET', 'NA 6×6×15 de 4 patas (dibujado 2.1×) · A1 y B2 en diagonal']", "label([titulo, sub]")
assert blk.rstrip().endswith("}")
blk = blk.rstrip()[:-1] + "};\n  pulsador(84, 'SW_R', '5V', 'RST', 'PULSADOR RESET', 'NA 6×6×15 de 4 patas (2.1×) · A1 → 5V y B2 → RST, en diagonal');\n  pulsador(150, 'SW_F', 'GND', 'setn', 'PULSADOR FALLA', 'NA de 4 patas (2.1×) · A1 → GND y B2 → setn, en diagonal. Simula la falla de corriente o temperatura');\n"
s = s[:i] + blk + s[j:]

# ---------- simulacion fuera: se dejan solo las variables y funciones vacias que usa el resto ----------
cut("// ---------- funcionamiento (reproduce la simulacion de LTspice) ----------", "// ---------- bucle ----------",
    "// ---------- (sin simulacion en la Reduccion 2) ----------\nlet simOn = false, simT = 0;\nfunction simOnSet(){} function simUpdate(){} function colorWires(){} function resetSimObjects(){} function simTick(){}\n\n")

# ---------- modo medicion: resumen 'rojo en ..., negro en ... -> valor' y punto exacto de la punta negra ----------
rep("""  else neg = 'la barra de <b>GND</b> de la placa <b>' + po.data.board + '</b>';
  return {""", """  else neg = 'el riel azul (−, GND) de la placa <b>' + po.data.board + '</b>, agujero <b>' + gndHole(po.data.board) + '</b>';
  return {""")
rep("function medPts(m){", "function gndHole(b){ const gp = DATA.gnd[b]; return b + '-riel GND izq fila ' + (NR - 1 - gp.y); }\nfunction medPts(m){")
rep("  if (!quiet) $('info').innerHTML", "  if (!quiet) $('info').innerHTML")
# resumen corto en cada medicion
rep("""  let h = head + '<div class="hint">Medición ' + (medK + 1) + ' de ' + ids.length + '</div><div style="margin:6px 0"><b>' + m.t + '</b></div><div class="hint">' + m.mode + '</div>' +""",
    """  const po0 = partObjs[m.red[0]], q0 = po0.data.pins.find(r => r.n === m.red[1]);
  const negS = m.black ? (partObjs[m.black[0]].data.short + ' pata ' + m.black[1]) : ('riel GND ' + gndHole(po0.data.board));
  let h = head + '<div class="hint">Medición ' + (medK + 1) + ' de ' + ids.length + '</div><div style="margin:6px 0"><b>' + m.t + '</b></div>' +
    '<div style="margin:6px 0;padding:6px 8px;border-left:3px solid #ff5a4d;background:#1d2530"><b style="color:#ff5a4d">ROJO</b> en ' + po0.data.short + ' pata ' + q0.n + ' (' + holeName(po0.data, q0) + ') · <b>NEGRO</b> en ' + negS + ' → <b>' + m.exp.split(';')[0] + '</b></div><div class="hint">' + m.mode + '</div>' +""")
rep("neg = 'la barra de <b>GND</b>", "neg = 'la barra de <b>GND</b>") if False else None
# ---------- pruebas con 6 campos (Reduccion 2) ----------
js = open(os.path.join(AQUI, "medicion_r2.js"), encoding="utf-8").read()
rep("// ---------- vistas ----------", js + chr(10) + "// ---------- vistas ----------")
open(P, "w", encoding="utf-8").write(s)
print("plantilla adaptada:", len(s))
