"""Crea los simbolos (.asy) propios del proyecto en 2_LTspice: compuertas 74HC (modelo de comportamiento)
y los bloques del sistema (simbolos jerarquicos con sus pines)."""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(AQUI, "..", "2_LTspice")


def write(name, txt):
    with open(os.path.join(DEST, name + ".asy"), "w", encoding="latin1", newline="\r\n") as f:
        f.write(txt)


def gate(name, label, pins_in, desc):
    """Compuerta cuadrada: entradas a la izquierda, salida a la derecha, vcc arriba."""
    n = len(pins_in)
    s = ["Version 4", "SymbolType CELL", "RECTANGLE Normal -32 -32 32 32", "TEXT 0 0 Center 2 %s" % label,
         "WINDOW 0 36 -16 Left 2", "WINDOW 3 36 16 Left 2",
         "SYMATTR Prefix X", "SYMATTR Value %s" % name, "SYMATTR Description %s" % desc]
    order = 1
    ys = [-16, 16] if n == 2 else [0]
    for nm, y in zip(pins_in, ys):
        s += ["PIN -32 %d LEFT 8" % y, "PINATTR PinName %s" % nm, "PINATTR SpiceOrder %d" % order]
        order += 1
    s += ["PIN 32 0 RIGHT 8", "PINATTR PinName y", "PINATTR SpiceOrder %d" % order]
    order += 1
    s += ["PIN 0 -32 TOP 8", "PINATTR PinName vcc", "PINATTR SpiceOrder %d" % order]
    write(name, "\n".join(s) + "\n")


def bloque(name, titulo, izq, der, arr=(), aba=(), ancho=160):
    """Simbolo jerarquico: rectangulo con el titulo y pines (nombre, ...) por lado. El orden SPICE sigue la lista completa."""
    alto = max(len(izq), len(der)) * 32 + 32
    s = ["Version 4", "SymbolType BLOCK", "RECTANGLE Normal 0 0 %d %d" % (ancho, alto),
         "TEXT %d %d Center 3 %s" % (ancho // 2, alto // 2, titulo),
         "WINDOW 0 %d -12 Center 2" % (ancho // 2), "WINDOW 3 %d %d Center 1" % (ancho // 2, alto + 14),
         ]
    order = 1
    for i, nm in enumerate(izq):
        s += ["PIN 0 %d LEFT 8" % (32 + 32 * i), "PINATTR PinName %s" % nm, "PINATTR SpiceOrder %d" % order]
        order += 1
    for i, nm in enumerate(der):
        s += ["PIN %d %d RIGHT 8" % (ancho, 32 + 32 * i), "PINATTR PinName %s" % nm, "PINATTR SpiceOrder %d" % order]
        order += 1
    for i, nm in enumerate(arr):
        s += ["PIN %d 0 TOP 8" % (32 + 48 * i), "PINATTR PinName %s" % nm, "PINATTR SpiceOrder %d" % order]
        order += 1
    for i, nm in enumerate(aba):
        s += ["PIN %d %d BOTTOM 8" % (32 + 48 * i, alto), "PINATTR PinName %s" % nm, "PINATTR SpiceOrder %d" % order]
        order += 1
    write(name, "\n".join(s) + "\n")


if __name__ == "__main__":
    os.makedirs(DEST, exist_ok=True)
    gate("HC_AND2", "AND", ["a", "b"], "74HC08 una compuerta AND (modelo de comportamiento)")
    gate("HC_NAND2", "NAND", ["a", "b"], "74HC00 una compuerta NAND (modelo de comportamiento)")
    gate("HC_BUF", "BUF", ["a"], "74HC buffer (modelo de comportamiento)")
    gate("HC_SCHINV", "1 S", ["a"], "74HC14 inversor Schmitt (modelo de comportamiento)")
    print("simbolos creados")
