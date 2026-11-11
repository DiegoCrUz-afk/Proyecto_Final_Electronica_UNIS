import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import piezas_corte as P

R = json.load(open(os.path.join(P.DXF, "resultado.json"), encoding="utf-8"))
ver, lista, chk = R["ver"], R["lista"], R["chk"]
T = P.T
stick1 = P.INNER + 2 * T + 2 + P.D_DISC1 + 2
stick2 = P.INNER + 2 * T + 4
NL = "\n"
with open(os.path.join(P.OUT, "LISTA_DE_PIEZAS.txt"), "w", encoding="utf-8") as fh:
    fh.write("MAQUETA DE LA BANDA - piezas de CARTON de %.1f mm (0.1 cm). Archivos en CENTIMETROS." % T + NL)
    fh.write("Capas: CORTE (rojo) = cortar; ETIQUETA (azul) = cotas y textos, NO cortar." + NL + NL)
    fh.write("PIEZAS A CORTAR" + NL)
    for a, n, q, w, h in lista:
        fh.write("  %-18s cortar x%-3d  %6.2f x %5.2f cm   %s" % (a, q, w / 10, h / 10, n) + NL)
    fh.write(NL + "OTROS MATERIALES (no se cortan)" + NL)
    fh.write("  Palillo del rodillo 1 (el del engrane): diametro 6 mm, largo minimo %.0f mm (%.1f cm)" % (stick1, stick1 / 10) + NL)
    fh.write("  Palillo del rodillo 2: diametro 6 mm, largo minimo %.0f mm (%.1f cm)" % (stick2, stick2 / 10) + NL)
    fh.write("  2 tubos del mismo diametro, de %.0f a %.0f mm, y de %.0f mm de largo; banda de %.0f x %.0f mm" % (P.D_MIN, P.D_MAX, P.BELT_W, P.BELT_L, P.BELT_W) + NL)
    fh.write("  Motor: cuerpo de %.0f x %.0f x %.0f mm + eje de %.0f mm (redondo de %.0f mm con un plano a %.0f mm)" % (P.MOT_W, P.MOT_H, P.MOT_BODY, P.MOT_SHAFT, P.SHAFT_D, P.SHAFT_FLAT) + NL)

with open(os.path.join(P.OUT, "MEMORIA_DE_MEDIDAS.txt"), "w", encoding="utf-8") as fh:
    w = lambda s="": fh.write(s + NL)
    w("MEMORIA DE MEDIDAS Y COMPROBACIONES (todo en mm salvo que se diga otra cosa)")
    w()
    w("Sistema: x = largo de la banda (0 = extremo trasero de los laterales); y = ancho (0 = cara exterior del lateral del motor; hacia afuera es negativo); z = altura sobre la mesa.")
    w()
    w("DECISIONES DE DISENO")
    w("- Altura de los ejes (palillos y eje del motor): %.0f mm sobre la mesa = %.0f mm sobre el borde inferior del lateral. La rueda grande (radio %.2f mm) queda a %.2f mm de la mesa." % (P.HA, P.Z_AX_LAT, ver["rueda"]["ra"], P.HA - ver["rueda"]["ra"]))
    w("- Laterales de %.0f x %.0f mm. Rodillo 1 (el del engrane) a %.0f mm del extremo. El rodillo 2 va en una RANURA (centros de %.0f a %.0f mm) para tubos de 2 a 4 cm con banda de 25 cm." % (P.LAT_L, P.H_LAT, P.X1, P.X2_MIN, P.X2_MAX))
    w("- Engranes: modulo 1.5, 20 grados, perfil de evolvente. Pinon de 12 dientes con desplazamiento +0.3 y rueda de 36 con -0.3 (un pinon de 12 sin desplazamiento se socava). Distancia entre centros %.1f mm. Radio exterior: pinon %.2f mm, rueda %.2f mm (%.2f cm). Cada diente se rebajo %.1f mm para dar juego al carton y al pegamento." % (ver["a"], ver["pinon"]["ra"], ver["rueda"]["ra"], ver["rueda"]["ra"] / 10, P.BACKLASH))
    w("- El motor va DETRAS del rodillo 1, a la misma altura, con el eje apuntando al lateral. Pinon y rueda en la misma capa (a 5-8 mm del lateral), disco del encoder en el eje del motor (10-12 mm), cara del motor a 14 mm y paredes del soporte desde 13 mm: nada se cruza.")
    w("- Cada engrane va en 3 capas pegadas (3 mm de carton). El disco del encoder en 2 capas.")
    w("- El soporte del motor es una cuna: 2 paredes + un piso, con pestanas que entran en la base. El piso deja el motor apoyado a %.0f mm, con su eje a %.0f mm." % (P.Z_FLOOR + T, P.HA))
    w()
    w("COMPROBACIONES (las calcula el programa que dibuja las piezas)")
    for t, ok in chk:
        w("  [%s] %s" % ("OK" if ok else "FALLA", t))
    w()
    w("SUPUESTOS QUE HAY QUE CONFIRMAR")
    w("- Eje del motor: redondo de %.0f mm con un plano a %.0f mm (asi interprete '4 mm' y '3 mm'). Si es otro, cambia el agujero en D del pinon y del disco." % (P.SHAFT_D, P.SHAFT_FLAT))
    w("- El eje del motor sale por el centro de la cara de 12 x 10 mm.")
    w("- Pared de los tubos supuesta de 2 mm por lado: las tapas miden el diametro del tubo menos 4 mm. Mide el diametro INTERIOR del tubo y ajusta la tapa si hace falta.")
    w("- Opto ranurado: sin medir. Se supone 8 mm de la base a la ranura, 10 mm de ancho y ranura de 4 mm o mas. El pedestal de %d calzas pone la ranura a 17 mm de la mesa; si tu opto es distinto, cambia el numero de calzas." % P.N_CALZAS)
    w("- Ancho de corte del laser: no medido (se usa 0). Si el laser quita 0.2 mm por lado, los agujeros salen mas grandes y las piezas mas chicas.")
    w("- Grosor del carton: se uso 1.0 mm. Si el carton real mide otro valor cambian las ranuras y las pestanas.")
print("textos escritos")
