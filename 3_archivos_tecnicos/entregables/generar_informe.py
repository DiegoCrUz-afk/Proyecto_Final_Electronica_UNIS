"""Informe tecnico (docx) de la miniestacion. Usa los resultados de logica_tabla.py y capturas_ondas.py.
Uso: py -3.13 generar_informe.py   (despues se exporta a PDF con exportar_pdf.ps1)
"""
import json
import math
import os
import sys

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
ENT = os.path.join(RAIZ, "9_Entregables_profesor")
SIM = os.path.join(ENT, "02_Simulacion_y_capturas")
OND = os.path.join(SIM, "ondas")
LOG = os.path.join(SIM, "logica")
IMG = os.path.join(RAIZ, "4_Documentacion", "img")
OUT = os.path.join(ENT, "01_Informe_tecnico")
os.makedirs(OUT, exist_ok=True)
DAT = json.load(open(os.path.join(OND, "datos_ondas.json"), encoding="utf-8"))
RES = json.load(open(os.path.join(LOG, "resultado_logica.json"), encoding="utf-8"))

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.0)
sec.top_margin = sec.bottom_margin = Cm(2.0)
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.paragraph_format.space_after = Pt(4)
st.paragraph_format.line_spacing = 1.08
for n, sz in (("Heading 1", 15), ("Heading 2", 12), ("Heading 3", 11)):
    h = doc.styles[n]
    h.font.name = "Calibri"
    h.font.size = Pt(sz)
    h.font.bold = True
    h.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    h.paragraph_format.space_before = Pt(10 if n != "Heading 3" else 6)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True

# pie de pagina con numero
def numero_pagina(par):
    run = par.add_run()
    for tipo, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tipo:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), tipo)
        else:
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = txt
        run._r.append(e)


fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fp.add_run("Miniestación industrial automatizada · UNIS · página ").font.size = Pt(8.5)
numero_pagina(fp)

NFIG = [0]


def H1(t): doc.add_heading(t, 1)
def H2(t): doc.add_heading(t, 2)
def H3(t): doc.add_heading(t, 3)


def P(t, bold=False, italic=False, size=None, align=None, after=None):
    p = doc.add_paragraph()
    r = p.add_run(t)
    r.bold, r.italic = bold, italic
    if size:
        r.font.size = Pt(size)
    if align:
        p.alignment = align
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    return p


def B(t, nivel=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Cm(0.6 + 0.6 * nivel)
    p.paragraph_format.space_after = Pt(1.5)
    # permite **negrita** al inicio: "titulo: texto"
    if "::" in t:
        a, b = t.split("::", 1)
        p.add_run(a + ":").bold = True
        p.add_run(b)
    else:
        p.add_run(t)
    return p


def EQ(t):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(t)
    r.font.name = "Cambria Math"
    r.font.size = Pt(10.5)
    return p


def sombrear(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def T(filas, anchos=None, enc=True, size=9, centro=()):
    t = doc.add_table(rows=len(filas), cols=len(filas[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, fila in enumerate(filas):
        for j, v in enumerate(fila):
            c = t.cell(i, j)
            c.text = ""
            par = c.paragraphs[0]
            par.paragraph_format.space_after = Pt(0)
            run = par.add_run(str(v))
            run.font.size = Pt(size)
            if enc and i == 0:
                run.bold = True
                sombrear(c, "DCE6F2")
            if j in centro:
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if anchos:
                c.width = Cm(anchos[j])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def FIG(ruta, ancho, pie):
    NFIG[0] += 1
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_after = Pt(1)
    p.add_run().add_picture(ruta, width=Cm(ancho))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run("Figura %d. %s" % (NFIG[0], pie))
    r.italic = True
    r.font.size = Pt(9)


def salto():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# =============================================================== PORTADA
for _ in range(5):
    doc.add_paragraph()
P("Universidad del Istmo de Guatemala (UNIS)", size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
P("Electrónica · Segundo semestre 2026", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, after=24)
P("MINIESTACIÓN INDUSTRIAL AUTOMATIZADA", bold=True, size=24, align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
P("Banda transportadora con amplificación, regulación,\nlógica combinacional y control de potencia", size=14, align=WD_ALIGN_PARAGRAPH.CENTER, after=30)
P("Informe técnico del proyecto integrador", italic=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, after=36)
P("Integrantes del grupo", italic=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
for _n in ["Sharly Abraham Alvarado Alvarez", "Kenneth Raúl Bernales Yee", "Diego Rodrigo Cruz Duarte",
           "José Javier de León Aguilar", "Oscar Mauricio Fletes Marroquín", "Jorge André Gil Leonardo",
           "Jose Eduardo Piedrasanta García", "Josué Darío Sacol Cojón"]:
    P(_n, bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, after=1)
P("Noviembre de 2026", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, after=30)
P("Los valores de este informe vienen de cálculos y de simulaciones en LTspice. El motor de la simulación es un modelo "
  "(no el motor definitivo). Las mediciones de laboratorio se anotan en la Guía de pruebas que acompaña esta entrega.",
  italic=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
salto()

# =============================================================== 1
H1("1. Resumen, objetivos y especificaciones")
P("La miniestación es una banda transportadora de escritorio sin microcontroladores. Un sensor infrarrojo detecta si hay un objeto; "
  "con objeto la banda baja a una velocidad reducida y sin objeto va a la velocidad normal. La velocidad se mide con un encoder y se "
  "regula con realimentación analógica. Si aparece una falla (sobrecorriente o sobretemperatura), o si se abre la cubierta, "
  "o si el interruptor general está apagado, el motor se detiene. Las fallas quedan guardadas hasta que se pulsa el reset.")
P("Objetivo general. Diseñar, simular y construir un sistema que use diodos, transistores BJT, amplificadores operacionales, "
  "regulación, lógica combinacional y control de potencia con MOSFET, y comprobar que cumple las pruebas de aceptación del enunciado.")
H3("Especificaciones de diseño")
T([
    ["Requisito del enunciado", "Valor de diseño"],
    ["Alimentación 12 V DC, fuente externa ≥ 2 A", "Entrada de 11 a 13 V, protegida con diodo 1N4007"],
    ["Regulación 5 V ± 5 % (Vin 11–13 V, 30–120 mA)", "Zener 5.6 V + BD139 de paso, con trimpot de ajuste"],
    ["Motor DC de 12 V, ≤ 500 mA", "Modelo de simulación: 12 Ω, 3 mH (arranque 0.88 A durante ~30 ms)"],
    ["Dos consignas de velocidad (reducida 40–60 %)", "Referencia normal 0.53 V; reducida ≈ 49 % (por cálculo)"],
    ["Umbral térmico ajustable 45–55 °C", "NTC 10 k, ajustable de 44 a 57 °C"],
    ["Sobrecorriente por método controlado", "Shunt 0.5 Ω + LM358 (ganancia 7.8); disparo ≈ 0.7 A, ajustable"],
    ["Cubierta, falla enclavada, reset manual", "Entrada G, pestillo con NAND y botón de reset"],
    ["Sin microcontroladores", "Lógica 74HC00/08/14, comparadores LM393, 555, LM324/LM358"],
], anchos=[8.0, 9.0])

# =============================================================== 2
H1("2. Arquitectura de bloques y señales")
P("El sistema tiene 11 bloques. Cada uno se dibujó y se simuló por separado y luego se unieron en el esquemático completo (Anexo A). "
  "Los nombres de las señales son los mismos en el esquemático, en la simulación y en el montaje en protoboard.")
T([
    ["Bloque", "Qué hace", "Entradas → salidas"],
    ["Entrada", "Protege contra polaridad invertida (1N4007) y filtra con 1000 µF", "12 V → vm"],
    ["1 Regulador 5 V", "Zener + BD139 de paso", "vm → v5"],
    ["2 Sensor IR", "TCRT5000 + BJT emisor común + comparador con histéresis", "luz IR → P"],
    ["3 Sobrecorriente", "Shunt + LM358 + detector de picos + comparador", "corriente del motor → setn"],
    ["4 Temperatura", "NTC + comparador con histéresis", "temperatura → setn"],
    ["5 Lógica", "Filtros, Schmitt, pestillo de falla y compuertas", "E, G, reset, P, setn → M, N, L, F"],
    ["6 PWM", "555 astable (rampa) + comparador con vctrl", "vctrl → pwm"],
    ["7 Potencia", "AND de seguridad, excitador BJT, MOSFET, diodo, shunt", "pwm, M → corriente del motor"],
    ["8 Encoder y F-V", "Optointerruptor, 555 monoestable y filtro RC", "pulsos → vspd"],
    ["9 Referencia de velocidad", "Divisor con trimpots; Q5 cambia a velocidad reducida", "L → vref"],
    ["10 Amplificador de error", "LM324/LM358: restador con ganancia 10", "vref, vspd → vctrl"],
    ["11 Alarma", "BJT como interruptor para buzzer y LED", "F → buzzer y LED"],
], anchos=[3.6, 8.2, 5.2], size=8.5)
P("Señales principales: vm (12 V después del diodo), v5 (5 V regulados), p (objeto), setn (falla de corriente o temperatura, activa en bajo), "
  "f/fn (falla guardada), m (permiso del motor), n/l (velocidad normal / reducida), vref, vspd, vctrl y pwm.")

# =============================================================== 3
H1("3. Esquemáticos y cálculos")
P("Los esquemáticos están en el Anexo A (sistema completo) y en el Anexo B (un dibujo por bloque). Los cálculos usan las hojas de datos "
  "típicas de cada componente; los valores simulados salen de LTspice con modelos propios (marcados en el archivo modelos.inc).")

H2("3.1 Entrada y regulador de 5 V (RF-01)")
P("El diodo 1N4007 en serie con la entrada protege contra polaridad invertida: con 12 V cae unos 0.7 V y vm queda cerca de 11.2 V con carga. "
  "Soporta 1 A continuo, más que la corriente máxima del motor. El condensador de 1000 µF en vm absorbe los picos del motor.")
P("El regulador usa el Zener de 5.6 V como referencia y el BD139 como transistor de paso (seguidor de emisor):")
EQ("Vsalida ≈ Vz − VBE ≈ 5.6 V − 0.7 V ≈ 4.9 V")
EQ("Iz = (Vin − Vz) / Rz → con Rz = 510 Ω: Iz(11 V) = (11 − 5.7)/510 ≈ 10.4 mA,  Iz(13 V) ≈ 14.3 mA")
EQ("Ib(peor caso) = 120 mA / hFE(mín = 40) = 3 mA → el Zener sigue con más de 7 mA, y su potencia máxima es 14.3 mA × 5.6 V ≈ 80 mW")
EQ("P(BD139, peor caso) = (13 − 4.9) V × 0.12 A ≈ 0.97 W")
P("Con ese calor el BD139 necesita disipador (sin disipador su resistencia térmica a ambiente es del orden de 100 °C/W). "
  "El trimpot de 100 Ω en serie con el Zener (Rtr, ajustado cerca de 10 Ω) corrige la tolerancia del Zener. "
  "Cout = 100 µF y C2 = 100 nF desacoplan la salida. En la simulación, con Vin de 11 a 13 V, carga de 30 a 120 mA y hFE de 40 a 250, "
  "la salida queda entre 4.84 y 4.95 V sin ajuste, dentro de 5 V ± 5 %. Si el Zener fuera 5 % bajo, hace falta ajustar Rtr (a 38–45 Ω queda en 4.79–5.23 V).")
P("Retorno de corrientes: la corriente del motor sale de vm y no pasa por el regulador; el regulador solo alimenta los 30 a 120 mA de control. "
  "Todo vuelve a la misma tierra de la fuente, y el shunt está en la fuente del MOSFET, así que solo mide la corriente del motor. "
  "El desacople es de 1000 µF en vm y de 100 µF + 100 nF en v5.")

H2("3.2 Sensor óptico IR y amplificador BJT en emisor común (RF-02)")
P("El LED infrarrojo del TCRT5000 va con Rled = 270 Ω: I = (5 − 1.2)/270 ≈ 14 mA. El fototransistor inyecta su corriente en la base de Q2 (2N3904). "
  "El modelo de simulación usa 2 µA sin objeto y 50 µA con objeto. Q2 trabaja en emisor común con RE = 150 Ω sin puentear:")
EQ("Polarización de la base: Vb = 5 V × 10k/(47k+10k) = 0.88 V  (Thevenin 8.3 kΩ)")
EQ("Sin objeto: Ic ≈ (5 − %.2f)/680 = %.1f mA  →  re = 26 mV/Ic ≈ %d Ω" % (DAT["vc_sin_objeto"], (5 - DAT["vc_sin_objeto"]) / 0.68, round(26 / ((5 - DAT["vc_sin_objeto"]) / 0.68))))
EQ("Ganancia: Av = −Rc/(RE + re) = −680/(150 + %d) ≈ −%.1f   (simulado: −%.2f)" % (round(26 / ((5 - DAT["vc_sin_objeto"]) / 0.68)), 680 / (150 + 26 / ((5 - DAT["vc_sin_objeto"]) / 0.68)), DAT["ganancia_sin_objeto"]))
EQ("Con objeto: Ic ≈ (5 − %.2f)/680 = %.1f mA,  Ve = Ic·RE ≈ %.2f V,  Vce ≈ %.1f V  → no satura" % (DAT["vc_con_objeto"], (5 - DAT["vc_con_objeto"]) / 0.68, (5 - DAT["vc_con_objeto"]) / 0.68 * 0.15, DAT["vc_con_objeto"] - (5 - DAT["vc_con_objeto"]) / 0.68 * 0.15))
P("El punto Q queda con el colector en %.2f V (sin objeto) y %.2f V (con objeto), lejos de saturación y de corte, con excursión de señal de varios cientos de mV. "
  "La impedancia de entrada es de unos 7 kΩ y la de salida es Rc = 680 Ω. El margen contra saturación es amplio: el transistor solo saturaría con más de 100 µA de corriente del fototransistor."
  % (DAT["vc_sin_objeto"], DAT["vc_con_objeto"]))
FIG(os.path.join(OND, "bjt_sensor_ir.png"), 13.5, "Señal en la base (arriba), señal amplificada en el colector (centro) y salida lógica p (abajo). Se superpuso una señal de 1 kHz de 2.5 µA para medir la ganancia.")

H2("3.3 Comparadores con histéresis (RF-02)")
P("Un LM393 compara el colector de Q2 con el umbral th. Una resistencia Rh de 220 kΩ de la salida al umbral da histéresis, para que el ruido no haga oscilar la salida:")
EQ("th = 5 V × (Rb + Rp2)/(Ra + 10k + Rb) = 5 × (26.8k + 5.5k)/46.8k = 3.45 V (con el trimpot en 0.55)")
P("El trimpot mueve el umbral entre 2.86 y 3.93 V. En la simulación los umbrales reales son 3.30 V (al bajar) y 3.52 V (al subir): 0.22 V de histéresis. "
  "El mismo esquema (con un divisor distinto) se usa en los bloques de sobrecorriente y temperatura. La salida del LM393 es de colector abierto con pull-up de 10 kΩ.")

H2("3.4 Sobrecorriente con amplificador operacional (RF-02)")
P("El shunt de 0.5 Ω en la fuente del MOSFET convierte la corriente del motor en voltaje. Un LM358 no inversor amplifica la señal:")
EQ("Av = 1 + Rf/Rg = 1 + 6.8k/1k = 7.8")
P("Después, un diodo 1N4148 con Cpk = 100 nF y Rbl = 22 kΩ forma un detector de picos, y Rd = 10 kΩ con Cd = 10 µF (≈ 0.1 s) da el filtro que ignora el arranque. "
  "El comparador dispara cuando ese nivel pasa la referencia:")
EQ("Vref = 5 V × (10k + 2k)/(10k + 10k + 10k) = 2.0 V   →   Vsh = (2.0 + 0.6)/7.8 = 0.33 V   →   I ≈ 0.33/0.5 ≈ 0.67 A")
P("En la simulación el disparo es de 0.71 A. Un arranque de 1.5 A durante 30 ms deja el nivel en 1.11 V y no dispara; 0.55 A sostenidos no disparan; 0.9 A sostenidos disparan a los 56 ms. "
  "La falla queda guardada en el pestillo (ver sección 4).")

H2("3.5 Sobretemperatura")
P("El NTC de 10 kΩ (B = 3950) forma un divisor con Rfix = 10 kΩ. A temperatura T la tensión es V = 5 × 10k/(Rntc + 10k). El umbral sale de Ra = 22 kΩ, el trimpot de 10 kΩ y Rb = 68 kΩ:")
ref = 5 * (68 + 5) / (22 + 10 + 68)
rn = 10 * (5 / ref - 1)
T0 = 298.15
tk = 1 / (1 / T0 + math.log(rn / 10) / 3950)
lo = 5 * (68 + 0) / 100
hi = 5 * (68 + 10) / 100
def tc(v):
    r = 10 * (5 / v - 1)
    return 1 / (1 / T0 + math.log(r / 10) / 3950) - 273.15
EQ("Vref(0.5) = 5 × (68k + 5k)/100k = %.2f V  →  Rntc = %.2f kΩ  →  T = %.1f °C" % (ref, rn, tk - 273.15))
EQ("Con el trimpot en los extremos: Vref = %.2f V → %.1f °C  y  Vref = %.2f V → %.1f °C" % (lo, tc(lo), hi, tc(hi)))
P("La simulación da un umbral ajustable de 44.0 a 56.8 °C (centro 49.9 °C) y una histéresis de 2.5 a 2.7 °C (Rh = 1 MΩ). Cubre el rango de 45 a 55 °C del enunciado.")

H2("3.6 PWM y velocidad (RF-05)")
P("Un NE555 astable genera una rampa triangular en el condensador Ct (entre 1/3 y 2/3 de Vcc, es decir de 1.67 a 3.33 V). Un LM393 compara esa rampa con la señal de control vctrl:")
EQ("f = 1.44/((Ra + 2Rb)·Ct) = 1.44/((1k + 20k)·10 nF) = 6.9 kHz     (simulado: %d Hz)" % DAT["pwm_frecuencia_hz"])
EQ("Ciclo = (vctrl − 1.67)/1.67 → con vctrl = 2.4 V: 0.44    (simulado: %.2f)" % DAT["pwm_ciclo"])

H2("3.7 MOSFET, excitación y protección de la carga inductiva (RF-05)")
P("Una compuerta AND 74HC08 une el PWM con el permiso M, así la seguridad tiene prioridad sobre el PWM. La salida (5 V) excita un par complementario "
  "(2N3904 / 2N3906) con Rg = 47 Ω y Rpd = 10 kΩ a tierra. La compuerta llega a %.2f V. Si falla el 5 V la compuerta queda a 0 V y el MOSFET se apaga." % DAT["gate_max_v"])
P("Se usa un IRFZ44N de canal N. Con la compuerta a 4.3 V conduce con unos 0.07 Ω en la simulación (a 10 V serían 0.02 Ω). Con 0.5 A la pérdida de conducción es I²R ≈ 0.02 W, "
  "pero su Vgs(th) va de 2 a 4 V según el lote, así que se mide Vds con el motor andando y, si pasa de 0.3 V, se cambia por un MOSFET de nivel lógico. "
  "El diodo Schottky 1N5819 (1 A, 40 V) en antiparalelo con el motor recircula la corriente del inductor cuando el MOSFET se apaga: "
  "con 12 V y un inductor de 3 mH el pico de corriente es menor a 1 A, y un Schottky tiene caída baja (≈ 0.4 V) y rapidez de conmutación suficiente para 6.9 kHz.")
FIG(os.path.join(OND, "pwm_compuerta_mosfet.png"), 13.0, "Rampa del 555, PWM, compuerta del MOSFET, voltaje de drenaje y corriente del motor (carga de 12 Ω y 3 mH, vctrl = 2.4 V).")

H2("3.8 Alarma con BJT como interruptor")
P("La señal F maneja un 2N3904 en saturación que enciende el buzzer de 12 V; en paralelo, un LED con 470 Ω da la señal luminosa.")
EQ("Ib = (5 − 0.7)/1k ≈ 4.3 mA;  Ic = 12/(400 Ω) ≈ 30 mA;  Ic/Ib ≈ 7 (< hFE/10 = 10 → saturado)")
EQ("P(2N3904) = Vce(sat) × Ic ≈ 0.2 V × 30 mA = 6 mW")
P("La corriente del LED es (5 − 2)/470 ≈ 6 mA.")

H2("3.9 Encoder y conversión frecuencia–voltaje (RF-06)")
P("El optointerruptor ranurado (LED con Rled = 220 Ω y fototransistor con 10 kΩ) lee un disco de 20 ranuras. Un LM393 con histéresis cuadra la señal; un derivador (1 nF, 10 kΩ, 1N4148) dispara un 555 monoestable cuyo pulso dura:")
EQ("t = 1.1 × Rt × Ct = 1.1 × 20k × 10 nF = 220 µs")
EQ("vspd = Vcc × t × f = 5 V × 220 µs × f = 1.1 mV/Hz   (simulado: %.2f V a 200 Hz, %.2f V a 500 Hz, %.2f V a 1 kHz)" % (DAT["vspd_200hz"], DAT["vspd_500hz"], DAT["vspd_1000hz"]))
EQ("rpm = f × 60 / 20 ranuras → 1400 rpm = 467 Hz → vspd ≈ 0.51 V")
P("Un filtro RC doble (10 kΩ + 1 µF, dos veces) suaviza el pulso; el rizado queda entre 14 y 26 mV pico a pico.")
FIG(os.path.join(OND, "encoder_fv.png"), 12.5, "Pulsos del encoder (arriba) y salida vspd del conversor F-V con tres frecuencias (abajo).")

# =============================================================== 4
H1("4. Lógica combinacional: tabla de verdad, Karnaugh y funciones")
P("Variables de entrada: E (sistema habilitado), G (cubierta cerrada), P (objeto detectado) y F (falla crítica enclavada). "
  "Salidas: M (permiso del motor), N (velocidad normal), L (velocidad reducida) y A (alarma).")
P("Las reglas del enunciado se traducen así: el motor se detiene si E = 0, G = 0 o F = 1; con E = 1, G = 1 y F = 0 se elige N si no hay objeto y L si hay objeto; la alarma es igual a F.")
filas = [["E", "G", "P", "F", "M", "N", "L", "A", "Simulación"]]
for f in RES["filas"]:
    e = f["esperado"]
    filas.append([f["E"], f["G"], f["P"], f["F"], e["M"], e["N"], e["L"], e["A"], "coincide" if f["ok"] else "NO"])
T(filas, anchos=[1.2] * 8 + [2.6], size=9, centro=range(9))
P("Funciones booleanas (tras simplificar con los mapas de Karnaugh de la Figura %d):" % (NFIG[0] + 1), after=2)
EQ("M = E · G · F'          N = M · P' = E · G · P' · F'          L = M · P = E · G · P · F'          A = F")
FIG(os.path.join(LOG, "karnaugh_M.png"), 7.2, "Mapa de Karnaugh de M (grupo de 2 celdas con vuelta por el borde: P no importa).")
t = doc.add_table(rows=1, cols=3)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, a in enumerate(("karnaugh_N.png", "karnaugh_L.png", "karnaugh_A.png")):
    c = t.cell(0, j)
    c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraphs[0].add_run().add_picture(os.path.join(LOG, a), width=Cm(5.4))
cap = doc.add_paragraph()
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = cap.add_run("Figura %d. Mapas de Karnaugh de N (1 celda), L (1 celda) y A (grupo de 8 celdas)." % (NFIG[0] + 1))
r.italic = True
r.font.size = Pt(9)
NFIG[0] += 1
H3("Implementación con compuertas")
B("Entradas:: E, G y reset llevan una resistencia de 10 kΩ a tierra (nunca quedan flotantes), un filtro RC de 10 kΩ y 100 nF (τ = 1 ms) y dos inversores Schmitt 74HC14 en serie (sin rebotes y en lógica positiva).")
B("Pestillo de falla:: tres NAND 74HC00. setn (activa en bajo, viene de los comparadores de corriente y temperatura) lo pone en 1; solo el reset lo borra, y reset_n = NAND(rst, setn) hace que el reset no actúe mientras la causa siga presente.")
B("Reset automático al encender:: Cpor 1 µF + Rpor 47 kΩ + 1N4148 dan un pulso al conectar la fuente.")
B("Decisión:: 74HC08: M1 = E·G; M = M1·F'; N = M·P' (P' sale de un NAND con las dos entradas juntas); L = M·P; A = F.")
B("Prioridad de la seguridad:: la AND del bloque de potencia combina PWM y M; si M = 0 no pasa PWM.")
P("Simulación de compuertas: se probaron en LTspice las 16 combinaciones con el circuito real (pestillo, reset, Schmitt y filtros). "
  "En cada combinación primero se hizo un reset, después se aplicaron E, G y P y, si F = 1, un pulso de falla. "
  "Resultado: las 16 coinciden con la tabla (Figura 8).")

# =============================================================== 5
H1("5. Lazo de realimentación de velocidad")
P("La referencia sale de un divisor entre 5 V, Rt = 68 kΩ y el trimpot Rp1 (8 kΩ): Vref = 5 × 8/(68 + 8) = 0.526 V. "
  "Cuando L = 1, un transistor Q5 pone un segundo trimpot Rp2 (7 kΩ) en paralelo con Rp1 y la referencia baja a 5 × 3.73/(68 + 3.73) = 0.26 V (49 % de la normal).")
P("El amplificador de error (LM358/LM324) resta la velocidad medida de la referencia:")
EQ("vctrl = Kerr × (vref − vspd) + Voff,    Kerr = 10 (100 kΩ/10 kΩ),    Voff = 5 × 5.1k/(4.7k + 5.1k) = 2.6 V")
P("Tres seguidores aíslan vref, vspd y Voff, y un condensador de 10 nF en la realimentación limita el ancho de banda. Si la velocidad baja, vspd baja, el error crece, vctrl sube y el PWM se alarga. "
  "No hay término integral, así que queda un error estacionario pequeño, que fue de 2 % en la simulación. Un valor de Kerr más alto reduce ese error, pero aumenta el sobreimpulso (hoy 18 %).")
P("Con el motor de simulación, el sistema llega al 95 % de la velocidad en 0.08 s y se estabiliza en 0.19 s tras cambiar de normal a reducida. Con una carga extra (perturbación ligera), la velocidad baja 6.5 % en lazo cerrado frente a 25.9 % en lazo abierto con el mismo vctrl.")

# =============================================================== 6
H1("6. Resultados de simulación")
P("La Figura %d es la simulación del sistema completo (4.6 s) con un guion de eventos: arranque, objeto presente (0.6–1.1 s), cubierta abierta (1.4–1.6 s), "
  "carga extra que provoca la falla de corriente (disparo a 2.098 s), reset (2.6 s), calentamiento del NTC (falla de temperatura a 3.356 s) y reset (3.609 s)." % (NFIG[0] + 1))
FIG(os.path.join(OND, "sistema_completo_eventos.png"), 13.8, "Sistema completo: alimentaciones, señales lógicas, velocidad, corriente del motor y variables del lazo.")
T([
    ["Evento (simulación)", "Resultado"],
    ["Operación normal", "≈ 1394 rpm, corriente media 0.15 A, M = 1, N = 1, L = 0"],
    ["Objeto presente", "L = 1, N = 0, velocidad ≈ 789 rpm (56 % de la normal)"],
    ["Cubierta abierta (t = 1.40 s)", "M cae en 1.4010 s; corriente del motor 0 A; al cerrar reanuda a ≈ 1392 rpm"],
    ["Falla de corriente (2.098 s)", "F = 1 (alarma 4.8 V), M = 0, motor parado, la falla sigue después de quitar la carga"],
    ["Reset (2.6 s)", "Limpia la falla; el motor reanuda ≈ 1409 rpm"],
    ["Falla de temperatura (3.356 s, 49.9 °C)", "Alarma y paro; el reset a 3.609 s solo actúa cuando el NTC ya se enfrió"],
    ["Regulación 5 V", "v5 = 5.012–5.018 V en el sistema; vm mínimo 11.13 V; I(D1) máx. 0.95 A"],
], anchos=[5.5, 11.5], size=9)
FIG(os.path.join(OND, "sistema_proteccion_corriente_temperatura.png"), 13.0, "Señal del shunt amplificado (arriba) y temperatura del NTC (abajo) en la misma simulación.")
FIG(os.path.join(LOG, "logica_16_combinaciones.png"), 13.5, "Prueba de la lógica con las 16 combinaciones de E, G, P y F (80 ms por combinación).")

# =============================================================== 7
H1("7. Ensayos de aceptación, decisiones y conclusiones")
T([
    ["Prueba (sección 6 del enunciado)", "Criterio", "Resultado de simulación / cálculo"],
    ["Salida de regulación", "5 V ± 5 %, Vin 11–13 V, 30–120 mA", "4.84–4.95 V (sin ajuste)"],
    ["Detección de objetos", "9 de 10 intentos", "p = %.2f V sin objeto y %.2f V con objeto; umbrales 3.30/3.52 V" % (DAT["p_sin_objeto"], DAT["p_con_objeto"])],
    ["Velocidades", "Reducida 40–60 % de la normal", "56 % (referencia 49 %)"],
    ["Regulación ante carga", "Error ≤ 20 % con carga ligera", "6.5 % en lazo cerrado (25.9 % en abierto)"],
    ["Alarma térmica", "45–55 °C seleccionable", "44.0–56.8 °C ajustable"],
    ["Sobrecorriente", "Disparo controlado", "≈ 0.71 A; arranque de 1.5 A / 30 ms no dispara"],
    ["Enclavamiento", "Alarma hasta reset manual", "La falla permanece; el reset solo limpia sin causa"],
    ["Interbloqueo de cubierta", "Abrir la cubierta retira el permiso", "M cae en 1 ms"],
    ["Ondas pedidas", "BJT, amplificada, encoder, PWM, control", "Figuras 1, 2, 3 y 6 (vctrl en la Figura 6)"],
], anchos=[4.6, 5.0, 7.4], size=8.5)
H3("Decisiones de diseño y rediseños")
B("Convertidor F–V:: el LM2907 se reemplazó por un 555 monoestable más filtro RC, con componentes que se consiguen en tienda.")
B("Sensor IR:: sin modulación del LED; el acople es en continua con la corriente inyectada en la base, y un trimpot ajusta el umbral.")
B("MOSFET:: IRFZ44N con excitador complementario a 5 V; si el 5 V falla, la compuerta queda a 0 V y el MOSFET se apaga.")
B("Reset:: manual con botón y automático al encender; el reset no actúa mientras la falla siga presente.")
B("Cubierta:: no enclava: solo corta M. Las fallas críticas sí quedan guardadas.")
B("Condensador de acople Cac:: se quitó del sensor IR; no era necesario con el acople en continua.")
B("Verificación del montaje:: el 3D de protoboards se verificó contra el esquemático (11 bloques y 328 pines coinciden).")
H3("Conclusiones")
P("El diseño cumple en simulación cada criterio de la sección 6 del enunciado y las reglas de seguridad: el motor se detiene con E = 0, G = 0 o F = 1, la falla queda guardada hasta el reset manual y el PWM nunca pasa si M = 0. "
  "El punto más delicado es el motor: la simulación usa un modelo y, con el motor real, hay que recalibrar el trimpot de sobrecorriente y la referencia de velocidad, y comprobar que su corriente no pase de 500 mA. "
  "Las mediciones reales de cada prueba se anotan en la Guía de pruebas para compararlas con estos resultados.")

# =============================================================== ANEXOS
salto()
H1("Anexo A. Esquemático completo")
P("Archivo editable: 02_Simulacion_y_capturas\\LTspice\\SISTEMA_COMPLETO.asc (LTspice) y SISTEMA_COMPLETO.ms14 (Multisim). La imagen también está en esa misma carpeta.")
FIG(os.path.join(RAIZ, "2_LTspice", "SISTEMA_COMPLETO_esquematico.png"), 14.5, "Esquemático completo del sistema (LTspice).")
salto()
H1("Anexo B. Esquemáticos por bloque")
for nom, tit in (("REG5V", "1 Regulador 5 V"), ("SENSOR_IR", "2 Sensor IR"), ("SOBRECORRIENTE", "3 Sobrecorriente"), ("TEMPERATURA", "4 Temperatura"),
                 ("LOGICA", "5 Lógica"), ("PWM_GEN", "6 PWM"), ("POTENCIA", "7 Potencia"), ("ENCODER_FV", "8 Encoder y F-V"),
                 ("REFVEL", "9 Referencia de velocidad"), ("ERROR_AMP", "10 Amplificador de error"), ("ALARMA", "11 Alarma")):
    FIG(os.path.join(IMG, "BLOQUE_%s.png" % nom), 11.0, "Bloque " + tit)
H1("Anexo C. Lista de materiales (BOM) y costo")
P("La lista completa con cantidades, precios de La Electrónica (consultados el 27/10/2026) y lo que ya se tiene en inventario está en 04_BOM_y_hojas_de_datos\\Lista_de_compras_La_Electronica.pdf. "
  "El total de lo que hay que comprar es Q495.00 con esos precios; los precios y las existencias pueden cambiar.")
T([
    ["Grupo", "Piezas principales"],
    ["Circuitos integrados", "LM393P ×5, LM358P, LM324N, NE555N ×2, 74HC00N, 74HC08N ×3, 74HC14N, bases para IC"],
    ["Transistores y diodos", "BD139, IRFZ44N, 1N5819, Zener 5.6 V 1 W, LED rojo; (ya en inventario: 2N3904, 2N3906, 1N4148, 1N4007)"],
    ["Sensores y señal", "TCRT5000L, optointerruptor ranurado, NTC 10 k, trimpots 3296W (5 × 10 k y 1 × 100 Ω)"],
    ["Potencia y mecánica", "Shunt 0.5 Ω, motorreductor, buzzer 12 V, fuente 12 V, portafusible y fusible, borneras"],
    ["Pasivos (inventario)", "59 resistencias de 1/4 W, condensadores 1 µF, 10 µF, 100 µF, 1000 µF y 100 nF"],
], anchos=[4.0, 13.0], size=8.5)
H1("Anexo D. Hojas de datos usadas")
P("Se consultaron las hojas de datos de los fabricantes para cada componente crítico. Los puntos que se verificaron y que afectan el montaje:")
T([
    ["Componente", "Dato usado"],
    ["74HC00 / 74HC08 / 74HC14", "Alimentación en pin 14 (Vcc) y pin 7 (GND); entradas no usadas a un nivel definido"],
    ["NE555", "Pines 8 (Vcc), 1 (GND), 2 (disparo), 6 (umbral), 7 (descarga), 3 (salida), 5 (control)"],
    ["LM393 / LM358 / LM324", "Pines de alimentación y entradas según el encapsulado DIP (LM393 y LM358 de 8 pines, LM324 de 14)"],
    ["BD139", "Orden de patas E–C–B"],
    ["2N3904 / 2N3906", "Orden de patas E–B–C (cara plana hacia ti)"],
    ["IRFZ44N", "Compuerta–Drenaje–Fuente (G–D–S); Vgs(th) de 2 a 4 V"],
    ["1N4007 / 1N5819 / 1N4148", "La banda marca el cátodo"],
    ["TCRT5000, optointerruptor", "LED (ánodo–cátodo) y fototransistor (colector–emisor); ambos tienen polaridad"],
], anchos=[5.0, 12.0], size=8.5)
H1("Anexo E. Archivos originales")
B("Repositorio:: https://github.com/DiegoCrUz-afk/Proyecto_Final_Electronica_UNIS")
B("Simulaciones:: carpeta 02_Simulacion_y_capturas (LTspice, Multisim, scripts y capturas).")
B("Montaje:: 03_Montaje_y_maqueta (3D de protoboards, lista de conexiones y piezas de corte láser).")
H1("Anexo F. Archivos de las simulaciones de lógica y de ondas")
P("Los archivos .cir de cada prueba están en 02_Simulacion_y_capturas\\ondas y 02_Simulacion_y_capturas\\logica, junto con los scripts que las generan "
  "(3_archivos_tecnicos\\entregables). Se pueden abrir y correr en LTspice.")

ruta = os.path.join(OUT, "Informe_tecnico.docx")
doc.save(ruta)
print("guardado", ruta)
