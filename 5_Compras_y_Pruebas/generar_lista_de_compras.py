"""Lista de compras en PDF: cantidades salen del mismo netlist (sistema.inc / montaje3d), precios reales de La Electronica
(consultados el 27/10/2026), y lo que Diego ya tiene (inventario del proyecto del amplificador).
Uso: python generar_lista_de_compras.py"""
import json
import math
import os
import sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(AQUI, "..", "3_archivos_tecnicos")
sys.path.insert(0, os.path.join(T, "montaje3d"))
sys.path.insert(0, os.path.join(T, "tienda"))
import generar_montaje3d as g3
import precios_la_electronica as PR

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

for n, f in (("Arial", "arial.ttf"), ("Arial-Bold", "arialbd.ttf")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", f)))

datos, zonas, ics = g3.construir_todo()
cnt = Counter()
for d in datos:
    cnt[(d["kind"], d["val"])] += 1

# ---------------- resistencias: todas se arman con valores que Diego ya tiene
SUBST = {"150": ["100", "47"], "270": ["220", "47"], "22k": ["20k", "2k"], "26.8k": ["20k", "6.8k"], "{Kerr*10k}": ["100k"], "{10k*kvn}": ["10k"], "{10k*kvr}": ["10k"]}
res = Counter()
for (k, v), n in cnt.items():
    if k == "R":
        for u in SUBST.get(v, [v]):
            res[u] += n
cuantas_r = sum(res.values())
PIEZAS_ABSOLUTAS = {"CC": Counter(), "CE": Counter()}
for (k, v), n in cnt.items():
    if k in ("CC", "CE"):
        PIEZAS_ABSOLUTAS[k][v] += n
ic = Counter(d["val"] for d in datos if d["kind"] == "IC")
q = Counter(d["val"] for d in datos if d["kind"] in ("Q92", "Q126", "MOS"))
dd = Counter(d["val"] for d in datos if d["kind"] == "D")
n_tb = sum(1 for d in datos if d["kind"] == "TB" and d["val"] != "Entrada 12 V (jack)")
n_trim10 = sum(1 for d in datos if d["kind"] == "TRIM" and d["val"] == "10k")
n_trim100 = sum(1 for d in datos if d["kind"] == "TRIM" and d["val"].startswith("100"))
try:
    D = json.load(open(os.path.join(T, "pcb", "salida", "pcb_datos.json")))
    n_placas = len(D["boards_list"])
    n_postes = sum(1 for b in D["boards"].values() for p in b["pads"] if p["ref"] == "X")
    n_puentes = sum(len(b["jumpers"]) for b in D["boards"].values())
except Exception:
    n_placas, n_postes, n_puentes = 10, 70, 70

# ---------------- listas
def p(clave):
    return PR.P[clave]


TIENES = [  # (cantidad, pieza, nota)
    (cuantas_r, "Resistencias de 1/4 W (valores: %s)" % ", ".join("%s x%d" % (k, v) for k, v in sorted(res.items(), key=lambda kv: float(kv[0].replace("k", "e3").replace("M", "e6")))),
     "Ya tienes todos los valores (inventario del amplificador). Cuenta cuantas de cada una te quedan."),
    (q["2N3904"], "Transistor 2N3904", "Tienes 5."),
    (q["2N3906"], "Transistor 2N3906", "Tienes 5."),
    (dd["1N4148"], "Diodo 1N4148", "Tienes 10."),
    (dd["1N4007"], "Diodo 1N4007", "Tienes 6."),
    (sum(v for k, v in PIEZAS_ABSOLUTAS["CC"].items() if k.startswith("1 ")), "Capacitor de 1 µF (electrolitico de 50 V, + al nodo de mayor voltaje)", "Tienes 5."),
    (PIEZAS_ABSOLUTAS["CE"].get("10 µF", 0), "Capacitor electrolitico de 10 µF", "Tienes 5."),
]


def fila_compra(cantidad, clave, nota="", nombre=None):
    desc, precio, hay, hand = p(clave)
    return (cantidad, nombre or desc, precio, nota)


COMPRAR = [
    ("Circuitos integrados", [
        fila_compra(ic["LM393"], "LM393", "5 comparadores en 5 chips (uno por protoboard)"),
        fila_compra(ic["LM358"], "LM358", ""),
        fila_compra(ic["LM324"], "LM324", ""),
        fila_compra(ic["NE555"], "NE555", ""),
        fila_compra(ic["74HC00"], "74HC00", ""),
        fila_compra(ic["74HC08"], "74HC08", "6 compuertas AND en 3 chips"),
        fila_compra(ic["74HC14"], "74HC14", ""),
        (ic["LM393"] + ic["LM358"] + ic["NE555"], "Base para IC de 8 pines", 1.00, "uno por cada chip de 8 patas"),
        (ic["LM324"] + ic["74HC00"] + ic["74HC08"] + ic["74HC14"], "Base para IC de 16 pines (para los de 14 patas)", 1.50, "la tienda no muestra de 14; la de 16 sirve"),
    ]),
    ("Transistores y diodos", [
        fila_compra(q["BD139"], "BD139", "si ya lo compraste para el amplificador, no lo repitas"),
        fila_compra(q["IRFZ44N"], "IRFZ44N", "reemplaza al IRLZ44N, que la tienda no vende (ver notas)"),
        fila_compra(dd["1N5819"], "1N5819", ""),
        fila_compra(1, "ZENER5V6", "equivale al 1N4734A"),
        fila_compra(1, "LED", "alarma luminosa"),
    ]),
    ("Sensores y senal", [
        fila_compra(1, "TCRT5000", "sensor de objeto"),
        fila_compra(1, "OPTO", "para el encoder (junto con el disco de 20 ranuras que haces tu)"),
        fila_compra(1, "NTC10K", ""),
        fila_compra(n_trim10, "TRIM10K", "ajustes de umbral y referencias"),
        fila_compra(n_trim100, "TRIM100", "ajuste del regulador; si ya lo compraste para el amplificador, no lo repitas"),
        fila_compra(1, "BUZZER12", "alarma sonora"),
        (1, "Resistencia 0.5 Ω a 5 W (shunt)", 4.00, "reemplaza a la de 0.47 Ω 1 W; la tienda la tiene"),
    ]),
    ("Capacitores", [
        fila_compra(PIEZAS_ABSOLUTAS["CC"].get("100 nF", 0), "C100N", ""),
        fila_compra(PIEZAS_ABSOLUTAS["CC"].get("10 nF", 0), "C10N", ""),
        fila_compra(PIEZAS_ABSOLUTAS["CC"].get("1 nF", 0), "C1N", ""),
        fila_compra(PIEZAS_ABSOLUTAS["CE"].get("100 µF", 0), "CE100", "si ya los compraste para el amplificador, no los repitas"),
        fila_compra(PIEZAS_ABSOLUTAS["CE"].get("1000 µF", 0), "CE1000", "idem"),
    ]),
    ("Conexion y mecanica", [
        fila_compra(1, "JACK", "entrada de la fuente de 12 V"),
        fila_compra(1, "SW", "interruptor E"),
        fila_compra(1, "PULSADOR", "reset"),
        fila_compra(1, "FINAL", "micro-switch de la cubierta"),
        fila_compra(2, "DISIP", "BD139 y IRFZ44N"),
        fila_compra(1, "MOTOR", "OJO: la tienda no publica la corriente; debe ser menor a 500 mA (ver notas)"),
        fila_compra(1, "FUENTE", "12 V, 2 A"),
        fila_compra(1, "FUSIBLE", "portafusible 5 x 20 mm (el fusible de 1 A no lo encontre)"),
    ]),
    ("Protoboards", [
        (5, "Protoboard de 1 galleta (confirma que sea de 830 puntos)", 39.00, "5 protoboards segun el 3D; hay uno de 4 galletas a Q242"),
        (3, "Alambre para protoboard 24 AWG (rollo)", 2.75, "para los cables de colores y las uniones entre protoboards"),
    ]),
]
total = sum(c * pr for _, filas in COMPRAR for (c, _, pr, _) in filas)

# ---------------- PDF
AZUL = colors.HexColor("#1f4e8c")
GRIS = colors.HexColor("#f1f4f8")
VERDE = colors.HexColor("#e5f5e8")
est = lambda **k: ParagraphStyle("s", fontName=k.pop("font", "Arial"), **k)
H1, H2 = est(fontSize=18, leading=22, textColor=AZUL, font="Arial-Bold"), est(fontSize=11.5, leading=14, textColor=AZUL, font="Arial-Bold", spaceBefore=8, spaceAfter=3)
TX, SM, TXR = est(fontSize=9.2, leading=11.6), est(fontSize=8, leading=10, textColor=colors.HexColor("#555555")), est(fontSize=9.2, leading=11.6, alignment=2)
doc = SimpleDocTemplate(os.path.join(AQUI, "Lista_de_compras_La_Electronica.pdf"), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=13 * mm, bottomMargin=12 * mm,
                        title="Lista de compras - miniestacion industrial", author="Diego Rodrigo Cruz Duarte")
S = []
S.append(Paragraph("Lista de compras · miniestación industrial automatizada", H1))
S.append(Paragraph("Todo se compra en <b>La Electrónica</b> (laelectronica.com.gt). Precios y existencias consultados en su buscador el 27/10/2026; pueden cambiar. "
                   "Las cantidades salen del esquemático que se simula. Verde = ya lo tienes (inventario del proyecto del amplificador).", TX))
S.append(Spacer(1, 5))
S.append(Paragraph("Ya lo tienes (no comprar)", H2))
t = Table([["Cant.", "Pieza", "Nota"]] + [[str(c), Paragraph(d, TX), Paragraph(n, SM)] for c, d, n in TIENES], colWidths=[14 * mm, 98 * mm, 70 * mm])
t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e7d32")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONT", (0, 0), (-1, 0), "Arial-Bold", 9),
                       ("BACKGROUND", (0, 1), (-1, -1), VERDE), ("FONT", (0, 1), (0, -1), "Arial", 9.2), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#b7d7bb")),
                       ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
S.append(t)
S.append(Paragraph("Resistencias que no tienes con ese valor exacto se arman con las que sí tienes: 150 Ω = 100 + 47 en serie, 270 Ω = 220 + 47, 22 kΩ = 20 k + 2 k, 26.8 kΩ = 20 k + 6.8 k. "
                   "Se pidieron valores y no cantidades: cuenta cuántas te quedan de cada una antes de comprar. Si falta alguna, cuesta Q0.75 (1/4 W).", SM))
S.append(Paragraph("Hay que comprar", H2))
filas = [["Cant.", "Pieza (como la muestra la tienda)", "Q c/u", "Q total", "Nota"]]
estilos = []
for grupo, items in COMPRAR:
    filas.append([Paragraph("<b>%s</b>" % grupo, TX), "", "", "", ""])
    estilos.append(("SPAN", (0, len(filas) - 1), (-1, len(filas) - 1)))
    estilos.append(("BACKGROUND", (0, len(filas) - 1), (-1, len(filas) - 1), colors.HexColor("#dfe8f5")))
    for c, d, pr, n in items:
        filas.append([str(c), Paragraph(d, TX), "%.2f" % pr, "%.2f" % (c * pr), Paragraph(n, SM)])
filas.append(["", Paragraph("<b>TOTAL a comprar</b>", TX), "", Paragraph("<b>Q %.2f</b>" % total, TXR), Paragraph("sin envío", SM)])
t = Table(filas, colWidths=[12 * mm, 70 * mm, 14 * mm, 17 * mm, 69 * mm], repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), AZUL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONT", (0, 0), (-1, 0), "Arial-Bold", 9),
                       ("FONT", (0, 1), (-1, -1), "Arial", 9.2), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#c8d1dc")),
                       ("ALIGN", (2, 0), (3, -1), "RIGHT"), ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
                       ("BACKGROUND", (0, -1), (-1, -1), GRIS), ("LINEABOVE", (0, -1), (-1, -1), 1, AZUL)] + estilos))
S.append(t)
S.append(PageBreak())
S.append(Paragraph("Notas importantes", H1))
NOTAS = [
    "<b>MOSFET.</b> El diseño original usaba un IRLZ44N (nivel lógico). La Electrónica no lo vende; sí vende el <b>IRFZ44N</b> (Q10). Se rehízo la simulación con el IRFZ44N: con la compuerta a 4.3 V "
    "conduce con unos 0.07 Ω (a 10 V serían 0.02 Ω) y el sistema funciona igual (1393 rpm normal, 789 rpm con objeto, dispara la sobrecorriente, la temperatura y el reset). "
    "Su Vgs(th) va de 2 a 4 V según el lote: si el tuyo es de 4 V se calentará más; mide Vds con el motor andando y, si pasa de 0.3 V, avísame.",
    "<b>Shunt.</b> No encontré 0.47 Ω 1 W; se usa <b>0.5 Ω 5 W</b> (Q4). El disparo de sobrecorriente queda en unos 0.67 A y se ajusta con el trimpot.",
    "<b>Motor.</b> La tienda lista un motorreductor de 12 V y 60 RPM (Q34) pero <b>no publica la corriente</b>. El enunciado pide máximo 500 mA: mídela con tu multímetro (en vacío y frenando poco) antes de seguir. "
    "Si pasa de 500 mA hay que buscar otro. Las 60 RPM del eje de salida no son las rpm de la simulación: la simulación usa un motor supuesto.",
    "<b>Zócalos.</b> Para los chips de 14 patas la tienda solo muestra bases de 8, 16 y 40 patas: se usa la de 16 (sobran 2 agujeros) o se corta una de 40.",
    "<b>Otra tienda.</b> Todo lo de arriba aparece en La Electrónica. Todo se arma en protoboard.",
    "<b>No encontré en la tienda:</b> fusible de 1 A, cable de calibre 22–24 y estaño. Si no tienes, búscalos.",
    "<b>Disco del encoder.</b> Se hace a mano: 20 ranuras. Cualquier disco opaco de unos 30 mm con 20 ranuras de 2 mm sirve.",
]
for n in NOTAS:
    S.append(Paragraph("• " + n, TX))
    S.append(Spacer(1, 3))
S.append(Paragraph("Productos de referencia (búsqueda en la tienda): LM358P, LM393P, LM324N, NE555N, 74HC00N/08N/14N, 2N3904, 2N3906, BD139, IRFZ44N, 1N4007, 1N4148, 1N5819, Zener 5.6 V 1 W, "
                   "TCRT5000L, Optointerruptor infrarrojo, NTC 10 K, Trimpot 3296W, Buzzer 12 V activo.", SM))
doc.build(S)
print("PDF listo. Total a comprar: Q %.2f; %d resistencias" % (total, cuantas_r))
