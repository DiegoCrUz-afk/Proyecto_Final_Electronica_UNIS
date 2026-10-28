import itertools, json
from ms_blocks import run, show

def last(r):
    if isinstance(r, list):
        return dict(zip(r[0], [float(x) for x in r[-1]]))
    return r

res = {}
# 1 regulador: linea y carga
print("== REG5V (Vin x carga) ==")
for vin in (11, 12, 13):
    for il in ("30m", "75m", "120m"):
        r = run("reg", "Vin vm 0 %d\nXr vm v5 REG5V\nIl v5 0 DC %s\n" % (vin, il))
        print(vin, il, round(r["V(v5)"], 3) if r else None)
# 2 sensor Vc con y sin objeto
print("== SENSOR_IR ==")
for lab, i in (("sin", "2u"), ("con", "50u")):
    r = run("s", "V5 v5 0 5\nIph v5 b %s\nXs v5 b tin p SENSOR_IR\nRtin tin 0 100Meg\n" % i)
    print(lab, "Vc=%.3f p=%.3f" % (r["V(c:xs)"], r["V(p)"]))
# 3 referencia de velocidad
print("== REFVEL ==")
for l in (0, 5):
    r = run("rv", "V5 v5 0 5\nVl l 0 %d\nXr v5 l vref REFVEL\n" % l)
    print("l=%d vref=%.4f" % (l, r["V(vref)"]))
# 4 amplificador de error
print("== ERROR_AMP ==")
for vref, vspd in ((0.526, 0.45), (0.526, 0.526), (0.526, 0.60)):
    r = run("ea", "V12 vm 0 12\nV5 v5 0 5\nVr vref 0 %s\nVs vspd 0 %s\nXe vm v5 vref vspd vctrl ERROR_AMP\n" % (vref, vspd))
    print("vref=%.3f vspd=%.3f vctrl=%.3f (teorico %.3f)" % (vref, vspd, r["V(vctrl)"], 10 * (vref - vspd) + 2.55))
# 5 alarma
print("== ALARMA ==")
for f in (0, 5):
    r = run("al", "V12 vm 0 12\nVf f 0 %d\nXa vm f ALARMA\n" % f)
    print("f=%d vcz=%.3f I(vf)=%.4f" % (f, r["V(cz:xa)"], r["I(vf)"]))
# 6 temperatura: umbral
print("== TEMPERATURA ==")
import math
for T in (40, 45, 50, 55, 60):
    rn = 10e3 * math.exp(3950 * (1 / (T + 273.15) - 1 / 298.15))
    r = run("t", "V5 v5 0 5\nRn v5 tnode %.1f\nXt v5 tnode setn TEMPERATURA\n" % rn)
    print("T=%d C setn=%.2f" % (T, r["V(setn)"]))
# 7 logica, 8 combinaciones con F=0
print("== LOGICA (F=0) ==")
bad = 0
for e, g, pp in itertools.product((0, 1), repeat=3):
    r = run("lg", "V5 v5 0 PWL(0 0 1m 5)\nVe ein 0 %d\nVg gin 0 %d\nVp p 0 %d\nVr rin 0 0\nVs setn 0 5\nXl v5 ein gin rin p setn m n l f fn LOGICA\n" % (e*5, g*5, pp*5), cmd="tran 2u 8m")
    r = last(r)
    M = e & g; N = M & (1 - pp); L = M & pp
    ok = (r["V(m)"] > 2.5) == bool(M) and (r["V(n)"] > 2.5) == bool(N) and (r["V(l)"] > 2.5) == bool(L) and r["V(f)"] < 2.5
    bad += not ok
    print("E%d G%d P%d F0 -> M%.1f N%.1f L%.1f F%.1f  %s" % (e, g, pp, r["V(m)"], r["V(n)"], r["V(l)"], r["V(f)"], "OK" if ok else "FALLA"))
print("== LOGICA (F=1, falla enclavada) ==")
for e, g, pp in itertools.product((0, 1), repeat=3):
    r = run("lg", "V5 v5 0 PWL(0 0 1m 5)\nVe ein 0 %d\nVg gin 0 %d\nVp p 0 %d\nVr rin 0 0\nVs setn 0 PWL(0 5 3m 5 3.001m 0 4m 0 4.001m 5)\nXl v5 ein gin rin p setn m n l f fn LOGICA\n" % (e*5, g*5, pp*5), cmd="tran 2u 10m")
    r = last(r)
    ok = r["V(m)"] < 2.5 and r["V(n)"] < 2.5 and r["V(l)"] < 2.5 and r["V(f)"] > 2.5
    bad += not ok
    print("E%d G%d P%d F1 -> M%.1f N%.1f L%.1f F%.1f  %s" % (e, g, pp, r["V(m)"], r["V(n)"], r["V(l)"], r["V(f)"], "OK" if ok else "FALLA"))
print("LOGICA: combinaciones con falla =", bad)
