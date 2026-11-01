import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ms_make2 as M
from ms_blocks import run

# 555 de comportamiento compatible con el motor de Multisim (sin dispositivos A de LTspice)
NE555 = """
.subckt NE555 gnd trig out rst cv thr dis vcc
R1 vcc cv 5k
R2 cv nn 5k
R3 nn gnd 5k
Bq qd gnd V=V(vcc)*(u(V(cv)/2-V(trig))+(1-u(V(cv)/2-V(trig)))*(1-u(V(thr)-V(cv)))*u(V(q)-V(vcc)/2))*u(V(rst)-0.7)
Rq qd q 100
Cq q gnd 100p
Ro q out 20
Bn nq gnd V=V(vcc)-V(q)
S1 dis gnd nq gnd SW5
.model SW5 SW(Ron=10 Roff=1G Vt=2.5 Vh=0.2)
Rg1 trig gnd 1G
Rg2 thr gnd 1G
.ends
"""
M.models = "\n".join(l for l in M.models.splitlines())
import ms_blocks
ms_blocks.base = ms_blocks.base + NE555

print("== PWM_GEN (vctrl -> ciclo) ==")
for vc in (1.9, 2.4, 3.0):
    r = run("pwm", "V5 v5 0 PWL(0 0 10u 5)\nVc vctrl 0 %s\nXp v5 vctrl pwm PWM_GEN\n" % vc, cmd="tran 0.5u 6m", timeout=600)
    if isinstance(r, list):
        hdr = r[0]
        t = [float(x[0]) for x in r[1:]]
        ip = hdr.index("V(pwm)")
        it = hdr.index("V(tri:xp)") if "V(tri:xp)" in hdr else None
        v = [float(x[ip]) for x in r[1:]]
        sel = [(a, b) for a, b in zip(t, v) if a > 2e-3]
        duty = sum(1 for a, b in sel if b > 2.5) / len(sel)
        cross = [sel[i][0] for i in range(1, len(sel)) if sel[i - 1][1] < 2.5 <= sel[i][1]]
        f = (len(cross) - 1) / (cross[-1] - cross[0]) if len(cross) > 2 else 0
        print("vctrl=%.2f ciclo=%.3f (teorico %.3f) f=%.0f Hz" % (vc, duty, (vc - 1.667) / 1.667, f))
    else:
        print("vctrl", vc, "->", r if r is None else list(r)[:5])
