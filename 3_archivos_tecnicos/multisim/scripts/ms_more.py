from ms_blocks import run
print("== SOBRECORRIENTE (tension en sh) ==")
for sh in (0.20, 0.30, 0.34, 0.38, 0.50):
    r = run("oc", "V12 vm 0 12\nV5 v5 0 5\nVs sh 0 %s\nXo vm v5 sh setn SOBRECORRIENTE\nRsn v5 setn 10k\n" % sh)
    print("sh=%.2f V (I=%.2f A) dl=%.2f setn=%.2f" % (sh, sh/0.47, r["V(dl:xo)"], r["V(setn)"]))
print("== POTENCIA (motor 12 ohm + 3 mH entre vm y dm) ==")
for pwm, m in ((5, 5), (5, 0), (0, 5)):
    r = run("pt", "V12 vm 0 12\nV5 v5 0 5\nVp pwm 0 %d\nVm m 0 %d\nXp v5 vm pwm m dm sh POTENCIA\nRmot vm dm 12\n" % (pwm, m))
    print("pwm=%d m=%d gate=%.2f V dm=%.3f V sh=%.3f V (I=%.3f A)" % (pwm, m, r["V(gate:xp)"], r["V(dm)"], r["V(sh)"], r["V(sh)"]/0.47))
