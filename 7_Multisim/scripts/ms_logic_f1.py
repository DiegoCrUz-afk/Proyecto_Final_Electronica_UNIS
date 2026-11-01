import itertools
from ms_blocks import run
def last(r):
    return dict(zip(r[0], [float(x) for x in r[-1]])) if isinstance(r, list) else r
bad = 0
for e, g, pp in itertools.product((0, 1), repeat=3):
    r = run("lg", "V5 v5 0 PWL(0 0 1m 5)\nVe ein 0 %d\nVg gin 0 %d\nVp p 0 %d\nVr rin 0 0\nVs setn 0 PWL(0 5 120m 5 120.01m 0 125m 0 125.01m 5)\nXl v5 ein gin rin p setn m n l f fn LOGICA\n" % (e*5, g*5, pp*5), cmd="tran 50u 150m", timeout=600)
    r = last(r)
    ok = r["V(m)"] < 2.5 and r["V(n)"] < 2.5 and r["V(l)"] < 2.5 and r["V(f)"] > 2.5
    bad += not ok
    print("E%d G%d P%d F1 -> M%.1f N%.1f L%.1f F%.1f  %s" % (e, g, pp, r["V(m)"], r["V(n)"], r["V(l)"], r["V(f)"], "OK" if ok else "FALLA"))
print("combinaciones con falla:", bad)
