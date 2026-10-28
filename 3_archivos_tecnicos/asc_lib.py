"""Generador de esquematicos de LTspice (.asc) y dibujo en SVG/PNG.

- Lee los simbolos (.asy) de la libreria de LTspice o de la carpeta del proyecto para conocer sus pines.
- Los pines se pueden unir con cables dibujados a mano (wire/join) o con etiquetas de nodo (net).
- render_svg() dibuja el .asc a partir de los mismos simbolos, para revisar el esquema sin abrir LTspice.
"""
import math
import os
import re

LIB_SYM = os.path.expandvars(r"%LOCALAPPDATA%\LTspice\lib\sym")
AQUI = os.path.dirname(os.path.abspath(__file__))
PROY_SYM = os.path.join(AQUI, "..", "2_LTspice")  # simbolos propios (.asy) junto a los .asc


def _find_asy(name):
    n = name.replace("\\", os.sep).replace("/", os.sep)
    for base in (PROY_SYM, LIB_SYM):
        p = os.path.join(base, n + ".asy")
        if os.path.exists(p):
            return p
    raise FileNotFoundError("simbolo no encontrado: " + name)


class Sym:
    def __init__(self, name):
        self.name = name
        self.path = _find_asy(name)
        self.lines, self.rects, self.circles, self.arcs, self.texts = [], [], [], [], []
        self.pins = []          # (x, y, nombre, orden)
        self.windows = {}       # n -> (x, y, align, size)
        self.attrs = {}
        self._parse(open(self.path, encoding="latin1").read())

    def _parse(self, txt):
        cur = None
        for raw in txt.splitlines():
            t = raw.split()
            if not t:
                continue
            k = t[0]
            if k == "LINE":
                self.lines.append(tuple(float(v) for v in t[2:6]))
            elif k == "RECTANGLE":
                self.rects.append(tuple(float(v) for v in t[2:6]))
            elif k == "CIRCLE":
                self.circles.append(tuple(float(v) for v in t[2:6]))
            elif k == "ARC":
                self.arcs.append(tuple(float(v) for v in t[2:10]))
            elif k == "TEXT":
                self.texts.append((float(t[1]), float(t[2]), t[3], int(t[4]), " ".join(t[5:])))
            elif k == "PIN":
                cur = [float(t[1]), float(t[2]), "", len(self.pins) + 1]
                self.pins.append(cur)
            elif k == "PINATTR" and cur is not None:
                if t[1] == "PinName":
                    cur[2] = t[2]
                elif t[1] == "SpiceOrder":
                    cur[3] = int(t[2])
            elif k == "WINDOW":
                self.windows[int(t[1])] = (float(t[2]), float(t[3]), t[4], int(t[5]) if len(t) > 5 else 2)
            elif k == "SYMATTR":
                self.attrs[t[1]] = " ".join(t[2:])
        self.pins = [tuple(p) for p in self.pins]
        self.pins.sort(key=lambda p: p[3])


_SYMS = {}


def sym(name):
    if name not in _SYMS:
        _SYMS[name] = Sym(name)
    return _SYMS[name]


def rot_pt(x, y, rot):
    r = rot[0]
    a = int(rot[1:])
    if r == "M":
        x = -x
    for _ in range((a // 90) % 4):
        x, y = -y, x
    return x, y


class Comp:
    def __init__(self, s, ref, value, x, y, rot):
        self.s, self.ref, self.value, self.x, self.y, self.rot = s, ref, value, x, y, rot

    def pin(self, i):
        """Coordenadas absolutas del pin numero i (orden SPICE, desde 1)."""
        p = self.s.pins[i - 1]
        dx, dy = rot_pt(p[0], p[1], self.rot)
        return (self.x + dx, self.y + dy)

    def pin_dir(self, i):
        """Direccion en la que sale el pin respecto al centro del simbolo (para poner la etiqueta)."""
        xs = [p[0] for p in self.s.pins] + [r[0] for r in self.s.rects] + [r[2] for r in self.s.rects]
        ys = [p[1] for p in self.s.pins] + [r[1] for r in self.s.rects] + [r[3] for r in self.s.rects]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        p = self.s.pins[i - 1]
        a, b = rot_pt(p[0] - cx, p[1] - cy, self.rot)
        if abs(a) >= abs(b):
            return (1 if a > 0 else -1, 0)
        return (0, 1 if b > 0 else -1)


class Schematic:
    def __init__(self, width=1600, height=1000):
        self.w, self.h = width, height
        self.wires, self.flags, self.comps, self.texts, self.iopins = [], [], [], [], []
        self.n_auto = 0

    # ---- elementos
    def add(self, symname, ref, value, x, y, rot="R0"):
        c = Comp(sym(symname), ref, value, x, y, rot)
        self.comps.append(c)
        return c

    def wire(self, *pts):
        for a, b in zip(pts, pts[1:]):
            if a != b:
                self.wires.append((a[0], a[1], b[0], b[1]))

    def join(self, c1, p1, c2, p2, via=None):
        a, b = c1.pin(p1), c2.pin(p2)
        if via is not None:
            self.wire(a, via, b)
        elif a[0] == b[0] or a[1] == b[1]:
            self.wire(a, b)
        else:
            self.wire(a, (b[0], a[1]), b)

    def flag(self, x, y, name, io=None):
        self.flags.append((x, y, name))
        if io:
            self.iopins.append((x, y, io))

    def net(self, comp, mapping, stub=16):
        """Pone etiquetas de nodo en los pines: mapping {pin: 'nombre'}. '0' = tierra."""
        for i, name in mapping.items():
            x, y = comp.pin(i)
            dx, dy = comp.pin_dir(i)
            ex, ey = x + dx * stub, y + dy * stub
            self.wire((x, y), (ex, ey))
            io = name.endswith("*")      # "nombre*" = pin de entrada/salida del bloque (jerarquia)
            name = name.rstrip("*")
            self.flags.append((ex, ey, name))
            if io:
                self.iopins.append((ex, ey, "BiDir"))

    def text(self, x, y, txt, size=2, align="Left", directive=False):
        self.texts.append((x, y, align, size, ("!" if directive else ";") + txt))

    # ---- salida .asc
    def save(self, path):
        out = ["Version 4", "SHEET 1 %d %d" % (self.w, self.h)]
        for w in self.wires:
            out.append("WIRE %d %d %d %d" % w)
        for f in self.flags:
            out.append("FLAG %d %d %s" % f)
        for io in self.iopins:
            out.append("IOPIN %d %d %s" % io)
        for c in self.comps:
            out.append("SYMBOL %s %d %d %s" % (c.s.name.replace("/", "\\"), c.x, c.y, c.rot))
            out.append("SYMATTR InstName %s" % c.ref)
            if c.value is not None:
                out.append("SYMATTR Value %s" % c.value)
        for t in self.texts:
            out.append("TEXT %d %d %s %d %s" % t)
        with open(path, "w", encoding="latin1", newline="\r\n") as f:
            f.write("\n".join(out) + "\n")

    # ---- dibujo
    def render_svg(self, path, margin=40):
        return render_asc_svg(self, path, margin)


def _font(size):
    return {0: 7, 1: 10, 2: 14, 3: 18, 4: 24, 5: 32, 6: 40, 7: 56}.get(size, 14)


def _anchor(align):
    a = align.lower()
    if a.startswith("v"):
        a = a[1:]
    return {"left": "start", "right": "end", "center": "middle", "top": "start", "bottom": "start"}.get(a, "start")


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_asc_svg(sch, path, margin=40):
    el = []
    xs, ys = [], []

    def track(x, y):
        xs.append(x)
        ys.append(y)

    for x1, y1, x2, y2 in sch.wires:
        el.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#1a6e1a" stroke-width="2"/>' % (x1, y1, x2, y2))
        track(x1, y1)
        track(x2, y2)
    # puntos de union (3 o mas extremos coinciden)
    cnt = {}
    for x1, y1, x2, y2 in sch.wires:
        for p in ((x1, y1), (x2, y2)):
            cnt[p] = cnt.get(p, 0) + 1
    for c in sch.comps:
        for i in range(1, len(c.s.pins) + 1):
            p = c.pin(i)
            cnt[p] = cnt.get(p, 0) + 1
    for p, n in cnt.items():
        if n >= 3:
            el.append('<circle cx="%g" cy="%g" r="3.5" fill="#1a6e1a"/>' % p)
    for x, y, name in sch.flags:
        track(x, y)
        if name == "0":
            el.append('<path d="M%g,%g v8 M%g,%g h16 M%g,%g h8 M%g,%g h0" stroke="#222" stroke-width="2" fill="none"/>' % (x, y, x - 8, y + 8, x - 4, y + 12, x, y + 16))
        else:
            el.append('<text x="%g" y="%g" font-size="13" font-weight="bold" fill="#1a1aa0" text-anchor="middle">%s</text>' % (x, y - 4, _esc(name)))
            el.append('<circle cx="%g" cy="%g" r="2.5" fill="#1a1aa0"/>' % (x, y))
    for c in sch.comps:
        s = c.s

        def T(px, py):
            dx, dy = rot_pt(px, py, c.rot)
            return c.x + dx, c.y + dy
        col = "#8b0000"
        for x1, y1, x2, y2 in s.lines:
            a, b = T(x1, y1), T(x2, y2)
            el.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="2"/>' % (a[0], a[1], b[0], b[1], col))
            track(*a)
            track(*b)
        for x1, y1, x2, y2 in s.rects:
            pts = [T(x1, y1), T(x2, y1), T(x2, y2), T(x1, y2)]
            el.append('<polygon points="%s" fill="#fffbe8" stroke="%s" stroke-width="2"/>' % (" ".join("%g,%g" % p for p in pts), col))
            for p in pts:
                track(*p)
        for x1, y1, x2, y2 in s.circles:
            a, b = T(x1, y1), T(x2, y2)
            el.append('<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="none" stroke="%s" stroke-width="2"/>' % ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, abs(a[0] - b[0]) / 2, abs(a[1] - b[1]) / 2, col))
            track(*a)
            track(*b)
        for (x1, y1, x2, y2, x3, y3, x4, y4) in s.arcs:
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            rx, ry = abs(x2 - x1) / 2, abs(y2 - y1) / 2
            a0 = math.atan2(-(y3 - cy), x3 - cx)
            a1 = math.atan2(-(y4 - cy), x4 - cx)
            P0 = T(cx + rx * math.cos(a0), cy - ry * math.sin(a0))
            P1 = T(cx + rx * math.cos(a1), cy - ry * math.sin(a1))
            el.append('<path d="M%g,%g A%g,%g 0 0 0 %g,%g" fill="none" stroke="%s" stroke-width="2"/>' % (P0[0], P0[1], rx, ry, P1[0], P1[1], col))
        for tx, ty, al, sz, txt in s.texts:
            p = T(tx, ty)
            el.append('<text x="%g" y="%g" font-size="%d" fill="%s" text-anchor="%s">%s</text>' % (p[0], p[1] + 5, _font(sz) - 3, col, _anchor(al), _esc(txt)))
        # nombre y valor
        for wn, txt in ((0, c.ref), (3, c.value)):
            if txt is None or txt == "":
                continue
            wx, wy, al, sz = s.windows.get(wn, (36, 40 + 24 * (wn // 3), "Left", 2))
            p = T(wx, wy)
            if c.rot in ("R90", "R270"):
                pass
            el.append('<text x="%g" y="%g" font-size="12" fill="#333" text-anchor="%s">%s</text>' % (p[0], p[1] + 5, _anchor(al) if c.rot in ("R0", "R180") else "start", _esc(txt)))
            track(*p)
        for i in range(1, len(s.pins) + 1):
            p = c.pin(i)
            el.append('<rect x="%g" y="%g" width="4" height="4" fill="#8b0000"/>' % (p[0] - 2, p[1] - 2))
            track(*p)
    for x, y, al, sz, txt in sch.texts:
        cmd = txt[0]
        body = txt[1:]
        fill = "#555" if cmd == ";" else "#0a3d91"
        for k, line in enumerate(body.split("\\n")):
            el.append('<text x="%g" y="%g" font-size="%d" fill="%s" text-anchor="%s" font-family="Consolas,monospace">%s</text>' % (x, y + 16 * k + 12, _font(sz) - 2, fill, _anchor(al), _esc(line)))
        track(x, y)
        track(x + 7 * max(len(l) for l in body.split("\\n")), y + 16 * body.count("\\n") + 16)
    x0, y0 = min(xs) - margin, min(ys) - margin
    x1, y1 = max(xs) + margin, max(ys) + margin
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="%g %g %g %g" width="%g" height="%g" font-family="Arial,sans-serif">' % (x0, y0, x1 - x0, y1 - y0, (x1 - x0), (y1 - y0)),
           '<rect x="%g" y="%g" width="%g" height="%g" fill="white"/>' % (x0, y0, x1 - x0, y1 - y0)] + el + ["</svg>"]
    with open(path, "w", encoding="utf8") as f:
        f.write("\n".join(svg))
    return path


def parse_asc(path):
    """Lee un .asc existente a un Schematic (para dibujarlo o revisarlo)."""
    sch = Schematic()
    cur = None
    for raw in open(path, encoding="latin1").read().splitlines():
        t = raw.split()
        if not t:
            continue
        k = t[0]
        if k == "SHEET":
            sch.w, sch.h = int(t[2]), int(t[3])
        elif k == "WIRE":
            sch.wires.append(tuple(int(v) for v in t[1:5]))
        elif k == "FLAG":
            sch.flags.append((int(t[1]), int(t[2]), t[3]))
        elif k == "IOPIN":
            sch.iopins.append((int(t[1]), int(t[2]), t[3]))
        elif k == "SYMBOL":
            cur = sch.add(t[1].replace("\\", "/"), "", None, int(t[2]), int(t[3]), t[4])
        elif k == "SYMATTR" and cur is not None:
            if t[1] == "InstName":
                cur.ref = t[2]
            elif t[1] == "Value":
                cur.value = " ".join(t[2:])
        elif k == "TEXT":
            sch.texts.append((int(t[1]), int(t[2]), t[3], int(t[4]), " ".join(t[5:])))
    return sch


def asc_to_png(asc_path, png_path, scale=1.0):
    """asc -> svg -> png (con Chrome sin ventana)."""
    import subprocess
    png_path = os.path.abspath(png_path)
    svg = os.path.splitext(png_path)[0] + ".svg"
    sch = parse_asc(asc_path)
    render_asc_svg(sch, svg)
    txt = open(svg, encoding="utf8").read()
    m = re.search(r'width="([\d.]+)" height="([\d.]+)"', txt)
    w, h = int(float(m.group(1)) * scale) + 4, int(float(m.group(2)) * scale) + 4
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome):
        chrome = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    html = os.path.splitext(png_path)[0] + "_tmp.html"
    open(html, "w", encoding="utf8").write('<html><body style="margin:0;background:#fff"><img src="file:///%s" width="%d"></body></html>' % (svg.replace("\\", "/"), w))
    subprocess.run([chrome, "--headless=old", "--disable-gpu", "--hide-scrollbars", "--window-size=%d,%d" % (w, h), "--timeout=6000", "--screenshot=" + png_path, "file:///" + html.replace("\\", "/")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(html)
    return png_path
