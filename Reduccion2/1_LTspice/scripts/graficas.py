import sys, os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from simlib import read_raw
d=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); cap=os.path.join(d,"capturas")
# sensor
r,_=read_raw(os.path.join(d,"prueba_sensor_ir.raw")); t=r["time"]
fig,ax=plt.subplots(2,1,figsize=(8,5),sharex=True)
ax[0].plot(t,r["V(b)"],label="b (base Q2)"); ax[0].plot(t,r["V(xs:c)"],label="c (colector Q2)"); ax[0].plot(t,r["V(xs:th)"],"--",label="th (umbral)"); ax[0].legend(); ax[0].set_ylabel("V"); ax[0].grid(alpha=.3)
ax[1].plot(t,r["V(p)"],color="C3"); ax[1].set_ylabel("p (V)"); ax[1].set_xlabel("t (s)"); ax[1].grid(alpha=.3)
ax[0].set_title("Sensor IR a 5 V: objeto entre 0.5 y 1.0 s (p: 0.03 V -> 4.93 V)")
fig.tight_layout(); fig.savefig(os.path.join(cap,"sensor_ir.png"),dpi=110); plt.close(fig)
# potencia
for v in ("bjt","mos"):
    r,_=read_raw(os.path.join(d,f"prueba_potencia_Rs15_{v}.raw")); t=r["time"]
    fig,ax=plt.subplots(4,1,figsize=(8,8),sharex=True)
    ax[0].plot(t,r["V(m)"],label="m"); ax[0].plot(t,r["V(n)"],label="n"); ax[0].legend(loc="right"); ax[0].set_ylabel("V")
    ax[1].plot(t,r["V(w)"]*60/(2*np.pi)); ax[1].set_ylabel("rpm (motor supuesto)")
    ax[2].plot(t,r["I(Lm)"]*1000); ax[2].set_ylabel("I motor (mA)")
    ax[3].plot(t,r["V(dm)"]-r["V(ds)"]); ax[3].set_ylabel("V entre dm y ds (V)"); ax[3].set_xlabel("t (s)")
    for a in ax: a.grid(alpha=.3)
    ax[0].set_title(f"Potencia 5 V, Rs=15 ohm, puente {'2N3904' if v=='bjt' else 'MOSFET'}: parado / normal / objeto / normal / parado")
    fig.tight_layout(); fig.savefig(os.path.join(cap,f"potencia_Rs15_{v}.png"),dpi=110); plt.close(fig)
    if v=="bjt":
        k="Ic(Qp)"; ic=np.abs(r[k]); print("2N3904: tiempo con Ic>200 mA (s):", float(np.sum(np.diff(t,prepend=0)[ic>0.2])), " pico mA", ic.max()*1000)
# logica
r,_=read_raw(os.path.join(d,"prueba_logica.raw")); t=r["time"]
fig,ax=plt.subplots(5,1,figsize=(9,7),sharex=True)
for a,(k,c) in zip(ax,[("V(p)","C0"),("V(f)","C3"),("V(m)","C2"),("V(n)","C1"),("V(l)","C4")]):
    a.plot(t,r[k],color=c); a.set_ylabel(k); a.grid(alpha=.3)
ax[0].set_title("Logica: 8 combinaciones con F=0 (0.15-0.31 s), FALLA, 8 combinaciones con F=1, prueba del pestillo (0.51-0.67 s)")
ax[-1].set_xlabel("t (s)"); fig.tight_layout(); fig.savefig(os.path.join(cap,"logica.png"),dpi=110); plt.close(fig)
