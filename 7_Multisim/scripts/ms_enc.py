import sys, os
sys.path.insert(0, ".")
import ms_blocks
exec(open("ms_555.py").read().split('print("== PWM_GEN')[0])
for f in (100, 500, 1000):
    per = 1.0 / f
    r = run("enc", "V5 v5 0 PWL(0 0 10u 5)\nVenc encs 0 PULSE(0.3 4.7 1m 1u 1u %.6g %.6g)\nRenc encs enc 1k\nXe v5 enc vspd ENCODER_FV\n" % (per / 2, per), cmd="tran 2u 0.2", timeout=900)
    if isinstance(r, list):
        i = r[0].index("V(vspd)")
        v = [float(x[i]) for x in r[-200:]]
        print("f=%d Hz  vspd=%.3f V (LTspice %.3f)  mV/Hz=%.2f" % (f, sum(v) / len(v), {100: 0.119, 500: 0.557, 1000: 1.106}[f], 1000 * sum(v) / len(v) / f), flush=True)
