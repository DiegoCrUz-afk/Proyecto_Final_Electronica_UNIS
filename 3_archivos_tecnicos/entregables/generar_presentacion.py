"""Presentacion breve (PDF 16:9) para la defensa. Uso: py -3.13 generar_presentacion.py"""
import json
import os
import sys

from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
ENT = os.path.join(RAIZ, "9_Entregables_profesor")
OND = os.path.join(ENT, "02_Simulacion_y_capturas", "ondas")
LOG = os.path.join(ENT, "02_Simulacion_y_capturas", "logica")
OUT = os.path.join(ENT, "07_Presentacion_y_defensa", "Presentacion.pdf")
DAT = json.load(open(os.path.join(OND, "datos_ondas.json"), encoding="utf-8"))
RES = json.load(open(os.path.join(LOG, "resultado_logica.json"), encoding="utf-8"))

W = os.environ.get("WINDIR", r"C:\Windows")
pdfmetrics.registerFont(TTFont("A", os.path.join(W, "Fonts", "arial.ttf")))
pdfmetrics.registerFont(TTFont("AB", os.path.join(W, "Fonts", "arialbd.ttf")))
PW, PH = 960, 540
AZUL = (0.12, 0.23, 0.37)
c = canvas.Canvas(OUT, pagesize=(PW, PH))
c.setTitle("Miniestación industrial automatizada - presentación")
N = [0]


def slide(titulo):
    if N[0]:
        c.showPage()
    N[0] += 1
    c.setFillColorRGB(*AZUL)
    c.rect(0, PH - 70, PW, 70, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("AB", 28)
    c.drawString(40, PH - 47, titulo)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.setFont("A", 11)
    c.drawRightString(PW - 30, 18, "Miniestación industrial automatizada · UNIS · %d" % N[0])
    c.setFillColorRGB(0.1, 0.1, 0.1)


def texto(x, y, lineas, size=20, paso=None, bullet=True):
    paso = paso or size * 1.5
    c.setFont("A", size)
    for l in lineas:
        if l.startswith("##"):
            c.setFont("AB", size)
            c.drawString(x, y, l[2:].strip())
            c.setFont("A", size)
        else:
            c.drawString(x, y, ("•  " if bullet else "") + l)
        y -= paso
    return y


def img(ruta, x, y, w, h=None):
    ir = ImageReader(ruta)
    iw, ih = ir.getSize()
    if h is None:
        h = w * ih / iw
    elif w is None:
        w = h * iw / ih
    c.drawImage(ir, x, y, w, h, mask="auto")


# 1 portada
c.setFillColorRGB(*AZUL)
c.rect(0, 0, PW, PH, fill=1, stroke=0)
c.setFillColorRGB(1, 1, 1)
c.setFont("AB", 40)
c.drawString(60, 330, "MINIESTACIÓN INDUSTRIAL")
c.drawString(60, 280, "AUTOMATIZADA")
c.setFont("A", 22)
c.drawString(60, 220, "Banda transportadora con amplificación, regulación,")
c.drawString(60, 190, "lógica combinacional y control de potencia")
c.setFont("A", 15)
_nom = ["Sharly Abraham Alvarado Alvarez", "Kenneth Raúl Bernales Yee", "Diego Rodrigo Cruz Duarte",
        "José Javier de León Aguilar", "Oscar Mauricio Fletes Marroquín", "Jorge André Gil Leonardo",
        "Jose Eduardo Piedrasanta García", "Josué Darío Sacol Cojón"]
for _i, _t in enumerate(_nom):
    c.drawString(60 + (_i // 4) * 400, 140 - (_i % 4) * 22, _t)
c.setFont("A", 13)
c.drawString(60, 38, "Electrónica · UNIS · Segundo semestre 2026")
N[0] = 1

# 2 que hace
slide("Qué hace la máquina")
texto(50, 440, [
    "Banda de escritorio sin microcontroladores: todo con transistores,",
    "    operacionales, comparadores, 555 y compuertas 74HC.",
    "Sin objeto → velocidad normal. Con objeto → velocidad reducida (40–60 %).",
    "La velocidad se mide con un encoder y se regula en lazo cerrado.",
    "El motor se detiene si: interruptor E apagado, cubierta abierta",
    "    o falla de corriente / temperatura.",
    "Las fallas quedan guardadas hasta pulsar el reset.",
    "Alarma sonora (buzzer) y luminosa (LED).",
], size=22, paso=44, bullet=False)

# 3 bloques
slide("11 bloques")
bloques = [("Entrada\n12 V", 0), ("1 Regulador\n5 V", 1), ("2 Sensor IR\n(BJT)", 2), ("3 Sobre-\ncorriente", 3), ("4 Temperatura", 4), ("5 Lógica\nE G P F", 5),
           ("6 PWM\n(555)", 6), ("7 Potencia\n(MOSFET)", 7), ("8 Encoder\nF–V", 8), ("9 Referencia", 9), ("10 Error\n(op-amp)", 10), ("11 Alarma", 11)]
bw, bh = 200, 75
for i, (t, k) in enumerate(bloques):
    col, fila = i % 4, i // 4
    x, y = 50 + col * 225, 370 - fila * 120
    c.setFillColorRGB(0.86, 0.9, 0.95)
    c.setStrokeColorRGB(*AZUL)
    c.roundRect(x, y, bw, bh, 8, fill=1, stroke=1)
    c.setFillColorRGB(*AZUL)
    c.setFont("AB", 17)
    for j, ln in enumerate(t.split("\n")):
        c.drawCentredString(x + bw / 2, y + bh / 2 + 6 - j * 20, ln)
c.setFillColorRGB(0.1, 0.1, 0.1)
c.setFont("A", 16)
c.drawString(50, 50, "Cada bloque se calculó, se simuló por separado y luego juntos (LTspice).")

# 4 regulador
slide("1 · Regulador de 5 V (Zener + BD139)")
texto(50, 440, ["Vsalida ≈ Vz − VBE = 5.6 − 0.7 ≈ 4.9 V",
                "Iz = (Vin − Vz)/Rz = (11 − 5.7)/510 ≈ 10 mA  (13 V: 14 mA)",
                "P(BD139) = (13 − 4.9) × 0.12 A ≈ 0.97 W  →  lleva disipador",
                "Trimpot de 100 Ω en serie con el Zener corrige la tolerancia"], size=22, paso=44)
c.setFont("AB", 26)
c.drawString(50, 230, "Simulado: 4.84 a 4.95 V")
c.setFont("A", 20)
c.drawString(50, 195, "Vin 11–13 V, carga 30–120 mA, hFE 40–250 → cumple 5 V ± 5 %")

# 5 sensor
slide("2 · Sensor IR y amplificador BJT")
img(os.path.join(OND, "bjt_sensor_ir.png"), 30, 90, None, 330)
texto(550, 430, ["Emisor común, RE = 150 Ω",
                 "Av = −Rc/(RE + re) = −680/(150 + 21)",
                 "  ≈ −4  (simulado −%.2f)" % DAT["ganancia_sin_objeto"],
                 "Colector: %.2f V sin objeto," % DAT["vc_sin_objeto"],
                 "  %.2f V con objeto (no satura)" % DAT["vc_con_objeto"],
                 "Comparador con histéresis:",
                 "  umbrales 3.30 y 3.52 V",
                 "p: %.2f V → %.2f V" % (DAT["p_sin_objeto"], DAT["p_con_objeto"])], size=16, paso=30, bullet=False)

# 6 logica
slide("5 · Lógica: variables y funciones")
texto(50, 445, ["E = habilitado   G = cubierta cerrada   P = objeto   F = falla guardada",
                "M = permiso del motor   N = normal   L = reducida   A = alarma"], size=17, paso=28, bullet=False)
c.setFont("AB", 24)
c.drawString(50, 370, "M = E·G·F'     N = M·P'     L = M·P     A = F")
for k, f in enumerate(("karnaugh_M.png", "karnaugh_N.png", "karnaugh_L.png", "karnaugh_A.png")):
    img(os.path.join(LOG, f), 40 + k * 225, 130, 215)
c.setFont("A", 17)
c.drawString(50, 85, "Pestillo de falla con NAND 74HC00; entradas filtradas y con inversores Schmitt 74HC14.")
c.drawString(50, 55, "Probadas las 16 combinaciones en LTspice con el circuito real: todas coinciden.")

# 7 tabla
slide("5 · Tabla de verdad (16 combinaciones)")
c.setFont("AB", 15)
cols = ["E", "G", "P", "F", "M", "N", "L", "A"]
x0, y0 = 60, 450
for j, h in enumerate(cols):
    c.drawCentredString(x0 + 22 + j * 44 + 22, y0, h)
c.setFont("A", 14)
for i, f in enumerate(RES["filas"]):
    e = f["esperado"]
    vals = [f["E"], f["G"], f["P"], f["F"], e["M"], e["N"], e["L"], e["A"]]
    if e["M"]:
        c.setFillColorRGB(0.85, 0.95, 0.85)
        c.rect(x0 + 22, y0 - 28 - i * 22 - 4, 8 * 44, 20, fill=1, stroke=0)
        c.setFillColorRGB(0.1, 0.1, 0.1)
    for j, v in enumerate(vals):
        c.drawCentredString(x0 + 22 + j * 44 + 22, y0 - 28 - i * 22, str(v))
texto(520, 420, ["Verde = el motor puede andar.", "", "Solo con E = 1, G = 1 y F = 0",
                 "hay permiso (M = 1).", "", "Sin objeto → N = 1.", "Con objeto → L = 1.", "", "A = F siempre."], size=18, paso=28, bullet=False)

# 8 PWM
slide("6 y 7 · PWM y MOSFET")
img(os.path.join(OND, "pwm_compuerta_mosfet.png"), 40, 55, None, 420)
texto(520, 430, ["555 astable: f = 1.44/((Ra + 2Rb)·Ct)",
                 "  = 6.9 kHz  (simulado %d Hz)" % DAT["pwm_frecuencia_hz"],
                 "Ciclo = (vctrl − 1.67)/1.67 = 0.44",
                 "  (simulado %.2f)" % DAT["pwm_ciclo"],
                 "AND con M: sin permiso no pasa PWM",
                 "Excitador 2N3904/2N3906, Rg = 47 Ω",
                 "Compuerta máx. %.1f V" % DAT["gate_max_v"],
                 "Diodo 1N5819 recircula la corriente",
                 "  del motor"], size=16, paso=30, bullet=False)

# 9 lazo
slide("Lazo cerrado de velocidad")
texto(50, 440, ["Encoder de 20 ranuras → 555 monoestable (220 µs) → filtro RC",
                "  vspd = 5 V × 220 µs × f = 1.1 mV/Hz",
                "vctrl = 10 × (vref − vspd) + 2.6 V",
                "vref normal 0.53 V; con objeto ≈ 49 % (Q5 pone un 2.º trimpot)",
                "Simulación: error 2 %; con carga extra baja 6.5 %",
                "  (en lazo abierto baja 25.9 %)",
                "Reducida = 56 % de la normal (criterio 40–60 %)"], size=20, paso=40, bullet=False)

# 10 protecciones
slide("Protecciones")
img(os.path.join(OND, "sistema_completo_eventos.png"), 30, 20, None, 440)
texto(500, 430, ["Cubierta abierta → M cae en 1 ms",
                 "Sobrecorriente: shunt 0.5 Ω ×7.8",
                 "  → dispara a ≈ 0.7 A; el arranque no",
                 "Temperatura: NTC 10 k, 45–55 °C",
                 "  ajustable (histéresis 2.6 °C)",
                 "Falla guardada hasta el reset;",
                 "  el reset no actúa si la causa sigue",
                 "Alarma: BJT saturado + buzzer + LED"], size=17, paso=30, bullet=False)

# 11 criterios
slide("Criterios de aceptación (simulación)")
filas = [("5 V ± 5 %", "4.84–4.95 V"), ("Objeto: p", "%.2f → %.2f V" % (DAT["p_sin_objeto"], DAT["p_con_objeto"])),
         ("Velocidad reducida", "56 % (40–60 %)"), ("Error ante carga ≤ 20 %", "6.5 %"),
         ("Umbral térmico 45–55 °C", "44.0–56.8 °C"), ("Sobrecorriente", "≈ 0.71 A"),
         ("Enclavamiento", "permanece hasta el reset"), ("Interbloqueo de cubierta", "M cae en 1 ms")]
c.setFont("AB", 20)
c.drawString(60, 440, "Prueba")
c.drawString(520, 440, "Resultado")
c.setFont("A", 20)
for i, (a, b) in enumerate(filas):
    c.drawString(60, 400 - i * 38, a)
    c.drawString(520, 400 - i * 38, b)
c.setFont("A", 15)
c.drawString(60, 70, "Resultados de simulación con un motor supuesto; las mediciones reales se comparan en la defensa.")

# 12 demo
slide("Demostración en vivo (10 pruebas)")
texto(50, 440, ["01 Operación normal        06 Seguridad de cubierta",
                "02 Detección de objeto    07 Falla de corriente",
                "03 Amplificador BJT        08 Umbral térmico",
                "04 Etapa operacional       09 Reset seguro",
                "05 Realimentación          10 Regulación y PWM"], size=24, paso=48, bullet=False)
c.setFont("A", 18)
c.drawString(50, 130, "Puntos de prueba: v5, vm, b, p, sh, setn, f, vspd, vref, vctrl, pwm, gate, enc.")
c.drawString(50, 95, "Gracias. ¿Preguntas?")
c.save()
print("presentacion:", OUT, "diapositivas:", N[0])
