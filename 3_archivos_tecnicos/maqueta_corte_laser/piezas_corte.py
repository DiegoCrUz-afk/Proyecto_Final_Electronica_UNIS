"""Maqueta de la banda transportadora: piezas de carton de 1 mm para corte laser (medidas coherentes).
Todo se calcula en MILIMETROS y el archivo se escribe en CENTIMETROS. Sistema de coordenadas del ensamble:
  x = largo de la banda (0 = extremo trasero de los laterales), y = ancho (0 = cara EXTERIOR del lateral del motor, hacia afuera = y negativo), z = altura sobre la mesa.
Uso: python piezas_corte.py y despues python textos.py (salen en 8_Maqueta_corte_laser; los DWG se sacan abriendo los DXF en AutoCAD y guardando como 2010)"""
import math
import os
import sys
import numpy as np
import ezdxf
from matplotlib.path import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "8_Maqueta_corte_laser")
DXF = os.path.join(OUT, "DXF_respaldo")
os.makedirs(DXF, exist_ok=True)

# ===================== PARAMETROS (mm) =====================
T = 1.0                      # grosor del carton
K = 0.0                      # ancho de corte del laser (sin medir)
BELT_W, BELT_L = 120.0, 250.0            # banda: 12 cm de ancho, 25 cm de largo (de borde a borde de los tubos)
D_MIN, D_MAX = 20.0, 40.0                # tubos (rodillos) de 2 a 4 cm de diametro
STICK = 6.0                              # palillo / eje de 0.6 cm
HOLE_LAT = 6.6                           # agujero del lateral (el palillo gira suelto)
HOLE_GEAR = 6.0                          # agujero de engranes y discos (el palillo va pegado)
INNER = BELT_W + 10                      # espacio libre entre laterales (5 mm de holgura por lado)
HA = 36.0                                # ALTURA DEL EJE sobre la mesa (centro de los palillos y del eje del motor)
Z_BASE = T                               # la base queda sobre la mesa; los laterales se paran sobre ella
H_LAT = 64.0                             # altura del lateral (sin pestanas)
Z_AX_LAT = HA - Z_BASE                   # altura del eje medida desde el borde inferior del lateral = 35
X1 = 25.0                                # rodillo 1 (el que mueve el motor): distancia desde el extremo trasero
X2_MIN, X2_MAX = X1 + (BELT_L - D_MAX), X1 + (BELT_L - D_MIN)   # rodillo 2: ranura para tubos de 4 a 2 cm
LAT_L = X2_MAX + 25.0                    # largo del lateral = 280
# motor (medidas dadas)
MOT_H, MOT_W, MOT_BODY, MOT_SHAFT = 10.0, 12.0, 25.0, 10.0     # alto 1 cm, ancho 1.2 cm, cuerpo 2.5 cm, eje 1 cm (total 3.5)
SHAFT_D, SHAFT_FLAT = 4.0, 3.0                                   # eje de 4 mm con un corte plano: 3 mm entre el plano y el lado redondo
CL = 0.1                                 # holgura del agujero en D
# engranes (modulo 1.5, 20 grados, con desplazamiento de perfil para que el de 12 dientes no se socave)
M, ALPHA = 1.5, math.radians(20)
Z1, Z2, X_1, X_2 = 12, 36, +0.3, -0.3
BACKLASH = 0.10                          # cada diente se hace 0.1 mm mas delgado (juego total 0.2 mm)
A_CENTROS = M * (Z1 + Z2) / 2            # 36 mm entre el eje del rodillo 1 y el eje del motor
X_P = X1 - A_CENTROS                     # el motor queda DETRAS del rodillo 1, a la misma altura: x = -11
# posiciones hacia afuera del lateral del motor (d = distancia a la cara exterior; y = -d)
D_GEAR0, D_GEAR1 = 5.0, 8.0              # capa de engranes (3 capas de carton)
D_DISC0, D_DISC1 = 10.0, 12.0            # disco del encoder (2 capas)
D_FACE = 14.0                            # cara frontal del motor (de ahi sale el eje de 10 mm hacia el lateral)
D_END = D_FACE + MOT_BODY                # extremo trasero del motor = 39
# soporte (cuna) del motor
CAV_W = MOT_W + 0.4                      # ancho libre entre paredes
Z_FLOOR = HA - MOT_H / 2 - T             # parte baja del piso = 30
Z_WALL_TOP = HA + MOT_H / 2 + 3.0        # tope de las paredes = 44
WALL_D0, WALL_D1 = D_FACE - 1.0, D_END + 1.0     # las paredes van de d=13 a d=40
# opto (medidas provisionales hasta medirlo): ranura a 8 mm sobre su base
OPTO_SLOT_OVER_BASE = 8.0
R_SLOT_MID = 19.0                        # radio medio de las ranuras del disco
# tubos
HUB_WALL = 2.0                           # grosor supuesto de la pared del tubo (por lado)

S = 0.1                                  # mm -> cm


# ===================== ENGRANES =====================
def inv(a):
    return math.tan(a) - a


def gear_outline(z, x, m=M, alpha=ALPHA, backlash=BACKLASH, n_flank=14):
    r = m * z / 2
    rb = r * math.cos(alpha)
    ra = r + (1 + x) * m
    rf = r - (1.25 - x) * m
    s = m * (math.pi / 2 + 2 * x * math.tan(alpha)) - backlash
    th_p = s / (2 * r)

    def phi(rho):
        return th_p + inv(alpha) - inv(math.acos(min(1.0, rb / rho)))
    rs = max(rb, rf + 1e-6)
    pts = []
    for i in range(z):
        c = i * 2 * math.pi / z
        c_next = (i + 1) * 2 * math.pi / z
        # flanco izquierdo hacia arriba
        for k in range(n_flank + 1):
            rho = rs + (ra - rs) * k / n_flank
            pts.append((rho, c - phi(rho)))
        # punta
        a0, a1 = c - phi(ra), c + phi(ra)
        for k in range(1, 4):
            pts.append((ra, a0 + (a1 - a0) * k / 4))
        # flanco derecho hacia abajo
        for k in range(n_flank, -1, -1):
            rho = rs + (ra - rs) * k / n_flank
            pts.append((rho, c + phi(rho)))
        # base: bajar al circulo de raiz y recorrerlo hasta el siguiente diente
        e0, e1 = c + phi(rs), c_next - phi(rs)
        if rs > rf + 1e-6:
            pts.append((rf, e0))
        for k in range(1, 5):
            pts.append((rf, e0 + (e1 - e0) * k / 5))
        if rs > rf + 1e-6:
            pts.append((rf, e1))
    return [(rho * math.cos(a), rho * math.sin(a)) for rho, a in pts], dict(r=r, rb=rb, ra=ra, rf=rf, s=s)


def verificar_engrane():
    g1, d1 = gear_outline(Z1, X_1)
    g2, d2 = gear_outline(Z2, X_2)
    a = A_CENTROS
    p1 = np.array(g1); p2 = np.array(g2)
    rot = lambda p, t: p @ np.array([[math.cos(t), math.sin(t)], [-math.sin(t), math.cos(t)]])
    delta = math.pi * (1 - 1 / Z2)           # el hueco de la rueda queda frente al diente del pinon
    peor, minima = 0, 1e9
    for k in range(48):
        th = k * (2 * math.pi / Z1) / 48
        q1 = rot(p1, th)
        q2 = rot(p2, delta - th * Z1 / Z2) + np.array([a, 0.0])
        d1c = np.hypot(q1[:, 0], q1[:, 1]); d2c = np.hypot(q2[:, 0] - a, q2[:, 1])
        in1 = Path(q1).contains_points(q2)       # puntos de la rueda dentro del pinon
        in2 = Path(q2).contains_points(q1)
        peor = max(peor, int(in1.sum() + in2.sum()))
        # distancia minima entre los dos bordes (muestreo)
        i1 = q1[np.hypot(q1[:, 0] - a / 2, q1[:, 1]) < a]; i2 = q2[np.hypot(q2[:, 0] - a / 2, q2[:, 1]) < a]
        if len(i1) and len(i2):
            dd = np.sqrt(((i1[:, None, :] - i2[None, :, :]) ** 2).sum(-1)).min()
            minima = min(minima, dd)
    return dict(pinon=d1, rueda=d2, a=a, solapes=peor, holgura_min=minima)


# ===================== DIBUJO =====================
def new_doc():
    d = ezdxf.new("R2010", setup=True)
    d.units = ezdxf.units.CM
    d.header["$MEASUREMENT"] = 1
    d.layers.add("CORTE", color=1)
    d.layers.add("ETIQUETA", color=5)
    return d


def poly(msp, pts, close=True):
    msp.add_lwpolyline([(x * S, y * S) for x, y in pts], close=close, dxfattribs={"layer": "CORTE"})


def circ(msp, cx, cy, d):
    msp.add_circle((cx * S, cy * S), d * S / 2, dxfattribs={"layer": "CORTE"})


def label(msp, x, y, text, h=3.0):
    msp.add_text(text, height=h * S, dxfattribs={"layer": "ETIQUETA", "insert": (x * S, y * S)})


def rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def stadium(cx0, cx1, cy, d, n=16):
    """ranura con extremos redondos: de (cx0, cy) a (cx1, cy), ancho d"""
    r = d / 2
    pts = [(cx1 + r * math.cos(-math.pi / 2 + math.pi * k / n), cy + r * math.sin(-math.pi / 2 + math.pi * k / n)) for k in range(n + 1)]
    pts += [(cx0 + r * math.cos(math.pi / 2 + math.pi * k / n), cy + r * math.sin(math.pi / 2 + math.pi * k / n)) for k in range(n + 1)]
    return pts


def dhole(cx, cy):
    R = (SHAFT_D + CL) / 2
    across = SHAFT_FLAT + CL
    th0 = math.pi - math.acos((across - R) / R) if False else math.acos(-(R - across) / R)
    n = 36
    return [(cx + R * math.cos(-th0 + 2 * th0 * k / n), cy + R * math.sin(-th0 + 2 * th0 * k / n)) for k in range(n + 1)]


# --------- piezas: cada una dibuja en (ox, oy) y devuelve (ancho, alto, nombre) ----------
X_MIN, Y_OUT = -30.0, 45.0
BASE_L = LAT_L - X_MIN
BASE_W = Y_OUT + 2 * T + INNER
TABS_X = (40.0, 130.0, 220.0)            # pestanas de los laterales (20 mm de ancho)
TRAV_X = (60.0, 140.0, 220.0)            # travesanos
X_W1 = X_P - CAV_W / 2 - T               # pared izquierda del soporte del motor (borde menor en x)
X_W2 = X_P + CAV_W / 2                   # pared derecha
WALL_TABS_D = ((WALL_D0 + 3.0, WALL_D0 + 11.0), (WALL_D1 - 11.0, WALL_D1 - 3.0))   # pestanas de pared (hacia la base) y de piso (hacia las paredes)


def placa_base(msp, ox, oy):
    poly(msp, rect(ox, oy, BASE_L, BASE_W))
    ux = lambda x: ox + (x - X_MIN)
    vy = lambda y: oy + (y + Y_OUT)
    for tx in TABS_X:
        for yy in (0.0, T + INNER):
            poly(msp, rect(ux(tx), vy(yy), 20.0 + K, T + K))
    for xw in (X_W1, X_W2):
        for d0, d1 in WALL_TABS_D:
            poly(msp, rect(ux(xw), vy(-d1), T + K, (d1 - d0) + K))
    # marca donde va el pedestal del opto (solo guia)
    dc = (D_DISC0 + D_DISC1) / 2                                  # el pedestal del opto va centrado en el plano del disco
    msp.add_lwpolyline([(ux(X_P - 6) * S, vy(-dc - 5) * S), (ux(X_P + 6) * S, vy(-dc - 5) * S), (ux(X_P + 6) * S, vy(-dc + 5) * S), (ux(X_P - 6) * S, vy(-dc + 5) * S)],
                       close=True, dxfattribs={"layer": "ETIQUETA"})
    label(msp, ux(X_P - 6), vy(-dc + 7), "guia: pedestal del opto", 2.4)
    return BASE_L, BASE_W, "Placa base"


def lateral(msp, ox, oy):
    y0 = oy + T
    pts = [(ox, y0)]
    for tx in TABS_X:
        pts += [(ox + tx, y0), (ox + tx, oy), (ox + tx + 20, oy), (ox + tx + 20, y0)]
    pts += [(ox + LAT_L, y0), (ox + LAT_L, y0 + H_LAT), (ox, y0 + H_LAT)]
    poly(msp, pts)
    circ(msp, ox + X1, y0 + Z_AX_LAT, HOLE_LAT)                                                # rodillo 1 (fijo, el del engrane)
    poly(msp, stadium(ox + X2_MIN, ox + X2_MAX, y0 + Z_AX_LAT, HOLE_LAT))                    # rodillo 2 (ranura: tubos de 4 a 2 cm)
    for tx in TRAV_X:
        poly(msp, rect(ox + tx - T / 2, y0 + H_LAT - 5.0, T + K, 4.0 + K))                    # ranura del travesano
    label(msp, ox + 4, y0 + H_LAT - 9, "eje a %.1f mm del borde inferior" % Z_AX_LAT, 2.4)
    return LAT_L, H_LAT + T, "Lateral (2 iguales)"


def travesano(msp, ox, oy):
    L = INNER + 2 * T
    pts = [(ox + T, oy), (ox + T + INNER, oy), (ox + T + INNER, oy + 1), (ox + L, oy + 1), (ox + L, oy + 5), (ox + T + INNER, oy + 5),
           (ox + T + INNER, oy + 6), (ox + T, oy + 6), (ox + T, oy + 5), (ox, oy + 5), (ox, oy + 1), (ox + T, oy + 1)]
    poly(msp, pts)
    return L, 6.0, "Travesano (3)"


def pared_motor(msp, ox, oy):
    Lw = WALL_D1 - WALL_D0
    Hw = Z_WALL_TOP - Z_BASE
    y0 = oy + T
    pts = [(ox, y0)]
    for d0, d1 in WALL_TABS_D:
        pts += [(ox + (d0 - WALL_D0), y0), (ox + (d0 - WALL_D0), oy), (ox + (d1 - WALL_D0), oy), (ox + (d1 - WALL_D0), y0)]
    pts += [(ox + Lw, y0), (ox + Lw, y0 + Hw), (ox, y0 + Hw)]
    poly(msp, pts)
    for d0, d1 in WALL_TABS_D:                                         # ranuras del piso
        poly(msp, rect(ox + (d0 - WALL_D0), y0 + (Z_FLOOR - Z_BASE), (d1 - d0) + K, T + K))
    label(msp, ox + 2, y0 + Hw + 3, "piso a %.0f mm de la mesa" % Z_FLOOR, 2.4)
    return Lw, Hw + T, "Pared del soporte del motor (2)"


def piso_motor(msp, ox, oy):
    Lw = WALL_D1 - WALL_D0
    pts = []
    pts += [(ox, oy + T)]
    # lado inferior con pestanas hacia abajo? no: las pestanas salen a los costados (hacia las paredes)
    body = [(ox, oy + T), (ox + Lw, oy + T), (ox + Lw, oy + T + CAV_W), (ox, oy + T + CAV_W)]
    out = [body[0]]
    # costado de abajo (y = oy + T) pestanas hacia -y
    for d0, d1 in WALL_TABS_D:
        out += [(ox + (d0 - WALL_D0), oy + T), (ox + (d0 - WALL_D0), oy), (ox + (d1 - WALL_D0), oy), (ox + (d1 - WALL_D0), oy + T)]
    out += [body[1], body[2]]
    for d0, d1 in reversed(WALL_TABS_D):
        out += [(ox + (d1 - WALL_D0), oy + T + CAV_W), (ox + (d1 - WALL_D0), oy + 2 * T + CAV_W), (ox + (d0 - WALL_D0), oy + 2 * T + CAV_W), (ox + (d0 - WALL_D0), oy + T + CAV_W)]
    out += [body[3]]
    poly(msp, out)
    return Lw, CAV_W + 2 * T, "Piso del soporte del motor (1)"


def calza_opto(msp, ox, oy):
    poly(msp, rect(ox, oy, 12, 10))
    return 12, 10, "Calza del pedestal del opto (%d)" % N_CALZAS


N_CALZAS = int(round(HA - R_SLOT_MID - OPTO_SLOT_OVER_BASE - Z_BASE))


def disco_encoder(msp, ox, oy):
    R = 25.0
    cx, cy = ox + R, oy + R
    circ(msp, cx, cy, 2 * R)
    poly(msp, dhole(cx, cy))
    for i in range(20):                                   # 20 ranuras CERRADAS: el disco no se parte ni se sueltan "dientes"
        a = i * 2 * math.pi / 20
        c, s = math.cos(a), math.sin(a)
        r0, r1, hw = R_SLOT_MID - 3.0, R_SLOT_MID + 3.0, 1.0
        poly(msp, [(cx + r0 * c - hw * s, cy + r0 * s + hw * c), (cx + r1 * c - hw * s, cy + r1 * s + hw * c),
                   (cx + r1 * c + hw * s, cy + r1 * s - hw * c), (cx + r0 * c + hw * s, cy + r0 * s - hw * c)])
    return 2 * R, 2 * R, "Disco del encoder, 20 ranuras (2)"


def pinon(msp, ox, oy):
    g, dat = gear_outline(Z1, X_1)
    cx, cy = ox + dat["ra"], oy + dat["ra"]
    poly(msp, [(cx + x, cy + y) for x, y in g]); poly(msp, dhole(cx, cy))
    return 2 * dat["ra"], 2 * dat["ra"], "Pinon 12 dientes, modulo 1.5 (3 capas)"


def rueda(msp, ox, oy):
    g, dat = gear_outline(Z2, X_2)
    cx, cy = ox + dat["ra"], oy + dat["ra"]
    poly(msp, [(cx + x, cy + y) for x, y in g]); circ(msp, cx, cy, HOLE_GEAR)
    return 2 * dat["ra"], 2 * dat["ra"], "Rueda 36 dientes, modulo 1.5 (3 capas)"


def disco_tubo(D):
    def f(msp, ox, oy):
        d = D - 2 * HUB_WALL
        circ(msp, ox + d / 2, oy + d / 2, d); circ(msp, ox + d / 2, oy + d / 2, HOLE_GEAR)
        return d, d, "Tapa para tubo de %d mm (12)" % D
    f.__name__ = "tapa_tubo_%dmm" % D
    return f


PIEZAS = [(placa_base, 1), (lateral, 2), (travesano, 3), (pared_motor, 2), (piso_motor, 1), (calza_opto, N_CALZAS), (pinon, 3), (rueda, 3), (disco_encoder, 2),
          (disco_tubo(20), 12), (disco_tubo(30), 12), (disco_tubo(40), 12)]


def cotas(msp, ox, oy, w, h):
    st = {"dimtxt": 2.4 * S, "dimasz": 1.8 * S, "dimexe": 1 * S, "dimexo": 1 * S, "dimlfac": 1.0, "dimdec": 2, "dimzin": 8}
    a = lambda p: (p[0] * S, p[1] * S)
    msp.add_linear_dim(base=a((ox, oy - 5)), p1=a((ox, oy)), p2=a((ox + w, oy)), override=st, dxfattribs={"layer": "ETIQUETA"}).render()
    msp.add_linear_dim(base=a((ox + w + 5, oy)), p1=a((ox + w, oy)), p2=a((ox + w, oy + h)), angle=90, override=st, dxfattribs={"layer": "ETIQUETA"}).render()


def poner(msp, f, ox, oy, cant):
    w, h, nombre = f(msp, ox, oy)
    cotas(msp, ox, oy, w, h)
    label(msp, ox, oy + h + 11, nombre)
    label(msp, ox, oy + h + 6, "cortar x%d   (carton de %.1f mm)" % (cant, T))
    return w, h, nombre


def verificar_ensamble(ver):
    """comprobaciones de coherencia del ensamble (mm). Devuelve lista de (texto, valor, ok)"""
    ra2 = ver["rueda"]["ra"]; ra1 = ver["pinon"]["ra"]
    L = []
    add = lambda t, v, ok: L.append((t, v, ok))
    add("Rueda grande: radio exterior %.2f mm (%.2f cm); punto mas bajo a %.2f mm de la mesa (minimo 5)" % (ra2, ra2 / 10, HA - ra2), HA - ra2, HA - ra2 >= 5)
    add("Rueda grande sobre la base (1 mm): holgura %.2f mm" % (HA - ra2 - Z_BASE), HA - ra2 - Z_BASE, HA - ra2 - Z_BASE >= 3)
    add("Tubo de %.0f mm: parte baja a %.1f mm de la mesa" % (D_MAX, HA - D_MAX / 2), HA - D_MAX / 2, HA - D_MAX / 2 >= Z_BASE + 5)
    top_belt = HA + D_MAX / 2 + 1.0
    add("Cara superior de la banda con tubo de 4 cm: %.1f mm; tope del lateral: %.1f mm" % (top_belt, Z_BASE + H_LAT), Z_BASE + H_LAT - top_belt, Z_BASE + H_LAT - top_belt >= 3)
    add("Travesano: su parte baja (%.1f mm) queda sobre la banda (%.1f mm)" % (Z_BASE + H_LAT - 6, top_belt), Z_BASE + H_LAT - 6 - top_belt, Z_BASE + H_LAT - 6 - top_belt >= 1.5)
    add("Ranura del rodillo 2: centros de %.0f a %.0f mm = tubos de 4 a 2 cm con banda de %.0f mm" % (X2_MIN, X2_MAX, BELT_L), (X2_MIN, X2_MAX), abs((X2_MAX - X1) - (BELT_L - D_MIN)) < 1e-6 and abs((X2_MIN - X1) - (BELT_L - D_MAX)) < 1e-6)
    add("Tubo de 4 cm en el rodillo 1 cabe en el lateral (sobra %.1f mm atras)" % (X1 - D_MAX / 2), X1 - D_MAX / 2, X1 - D_MAX / 2 >= 3)
    add("Engranes: centros a %.1f mm (= modulo x (12+36)/2); huella minima entre bordes %.3f mm; solapes en 48 posiciones: %d" % (ver["a"], ver["holgura_min"], ver["solapes"]), ver["solapes"], ver["solapes"] == 0 and ver["holgura_min"] > 0)
    add("Raiz de la rueda libre de la punta del pinon: %.2f mm" % (ver["a"] - ra1 - ver["rueda"]["rf"]), ver["a"] - ra1 - ver["rueda"]["rf"], ver["a"] - ra1 - ver["rueda"]["rf"] >= 0.25)
    add("Eje del motor a la MISMA altura que los palillos (%.0f mm) y a %.0f mm detras del rodillo 1" % (HA, A_CENTROS), A_CENTROS, True)
    add("Eje del motor: punta a %.0f mm del lateral; pinon entre %.0f y %.0f mm cabe en el eje de %.0f mm (de %.0f a %.0f)" % (D_FACE - MOT_SHAFT, D_GEAR0, D_GEAR1, MOT_SHAFT, D_FACE - MOT_SHAFT, D_FACE), D_FACE - MOT_SHAFT, D_FACE - MOT_SHAFT >= 2 and D_FACE - MOT_SHAFT <= D_GEAR0 and D_GEAR1 <= D_DISC0 - 1 and D_DISC1 <= D_FACE - 1)
    add("Disco del encoder (radio 25): parte baja a %.0f mm de la mesa; no toca el palillo del rodillo 1 (separacion %.0f mm)" % (HA - 25, abs(X1 - X_P) - 25 - STICK / 2), HA - 25, HA - 25 >= Z_BASE + 5 and abs(X1 - X_P) - 25 - STICK / 2 >= 3)
    add("Capas: engranes d=%.0f-%.0f, disco d=%.0f-%.0f, paredes del soporte desde d=%.0f: sin choques entre capas" % (D_GEAR0, D_GEAR1, D_DISC0, D_DISC1, WALL_D0), WALL_D0 - D_DISC1, WALL_D0 - D_DISC1 >= 1)
    add("Motor %.0f x %.0f mm entra en la cuna de %.1f mm; piso a %.0f mm: motor apoyado a %.0f mm y eje a %.0f mm" % (MOT_W, MOT_H, CAV_W, Z_FLOOR + T, Z_FLOOR + T, HA), Z_FLOOR + T + MOT_H / 2 - HA, abs(Z_FLOOR + T + MOT_H / 2 - HA) < 1e-6)
    add("Paredes (hasta %.0f mm) pasan el tope del motor (%.0f mm)" % (Z_WALL_TOP, HA + MOT_H / 2), Z_WALL_TOP - (HA + MOT_H / 2), Z_WALL_TOP > HA + MOT_H / 2)
    add("La base cubre el soporte: x desde %.0f (pared en %.1f) y hacia afuera %.0f mm (motor hasta %.0f)" % (X_MIN, X_W1, Y_OUT, D_END + 1), min(X_W1 - X_MIN, Y_OUT - (D_END + 1)), X_W1 - X_MIN >= 5 and Y_OUT - (D_END + 1) >= 3)
    add("Pedestal del opto: %d calzas de %.0f mm -> ranura a %.0f mm (= eje %.0f - radio %.0f)" % (N_CALZAS, T, Z_BASE + N_CALZAS + OPTO_SLOT_OVER_BASE, HA, R_SLOT_MID), Z_BASE + N_CALZAS + OPTO_SLOT_OVER_BASE, abs(Z_BASE + N_CALZAS + OPTO_SLOT_OVER_BASE - (HA - R_SLOT_MID)) < 1e-6)
    return L


if __name__ == "__main__":
    ver = verificar_engrane()
    lista = []
    for f, cant in PIEZAS:
        d = new_doc(); msp = d.modelspace()
        w, h, nombre = poner(msp, f, 12, 12, cant)
        d.saveas(os.path.join(DXF, f.__name__ + ".dxf"))
        lista.append((f.__name__, nombre, cant, w, h))
    # hoja con todo (separado, sin tocarse)
    FILAS = [[placa_base], [lateral, lateral], [pared_motor, pared_motor, piso_motor, travesano, travesano, travesano],
             [pinon, rueda, disco_encoder, disco_encoder], [disco_tubo(20), disco_tubo(30), disco_tubo(40), calza_opto, calza_opto, calza_opto, calza_opto]]
    d = new_doc(); msp = d.modelspace()
    y = 0
    cant = dict((f.__name__, c) for f, c in PIEZAS)
    for fila in FILAS:
        x = 0; alto = 0; vistos = set()
        for f in fila:
            if f.__name__ not in vistos:
                vistos.add(f.__name__)
                w, h, nom = poner(msp, f, x + 12, y + 12, cant[f.__name__])
            else:
                w, h, nom = f(msp, x + 12, y + 12)
            x += max(w, len(nom) * 2.8) + 38; alto = max(alto, h)
        y += alto + 55
    d.saveas(os.path.join(DXF, "TODAS_las_piezas.dxf"))
    chk = verificar_ensamble(ver)
    for t, v, ok in chk:
        print(("OK   " if ok else "FALLA"), t)
    print("ENGRANE:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in ver.items() if k not in ("pinon", "rueda")})
    print("pinon:", {k: round(v, 3) for k, v in ver["pinon"].items()}, "| rueda:", {k: round(v, 3) for k, v in ver["rueda"].items()})
    for a, n, q, w, h in lista:
        print("%-18s x%-3d %6.1f x %5.1f mm  %s" % (a, q, w, h, n))
    import json
    json.dump(dict(lista=lista, chk=[(t, bool(ok)) for t, v, ok in chk], ver=dict(a=ver["a"], holgura_min=float(ver["holgura_min"]), pinon=ver["pinon"], rueda=ver["rueda"])), open(os.path.join(DXF, "resultado.json"), "w", encoding="utf-8"))


