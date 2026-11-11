"""Capturas de senales (simulacion LTspice): amplificador BJT, PWM + compuerta + MOSFET, encoder + F-V
y sistema completo (a partir de sim\\sistema_desde_asc_resumen.npz).
Salida: 9_Entregables_profesor\\02_Simulacion_y_capturas\\ondas
Uso: py -3.13 capturas_ondas.py
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
TEC = os.path.dirname(AQUI)
RAIZ = os.path.dirname(TEC)
sys.path.insert(0, TEC)
from simlib import run, read_raw, log_errors  # noqa: E402

OUT = os.path.join(RAIZ, "9_Entregables_profesor", "02_Simulacion_y_capturas", "ondas")
os.makedirs(OUT, exist_ok=True)
INC = ['.include "%s"' % os.path.join(TEC, f).replace("\\", "/") for f in ("modelos.inc", "sistema.inc")] + [".lib NE555.sub"]
datos = {}


def correr(nombre, lineas):
    cir = os.path.join(OUT, nombre + ".cir")
    open(cir, "w", encoding="utf-8").write("\n".join(["* " + nombre] + INC + lineas + [".end"]) + "\n")
    base = run(cir)
    e = log_errors(base)
    if e:
        print(nombre, "errores:", e)
    d, _ = read_raw(base + ".raw")
    d["time"] = np.abs(d["time"])
    return d, base


def limpiar(base):
    for ext in (".raw", ".log", ".op.raw"):
        try:
            os.remove(base + ext)
        except OSError:
            pass


# ------------------------------------------------------------ 1) amplificador BJT del sensor IR
# corriente del fototransistor (modelo): 2 uA sin objeto, 50 uA con objeto, mas 2.5 uA de senal de 1 kHz
d, base = correr("ondas_sensor_ir", [
    "Vv5 v5 0 5",
    "Bi 0 b I=(2u+48u*u(time-0.012))+2.5u*sin(2*pi*1k*time)",
    "XS v5 b p SENSOR_IR",
    ".save V(b) V(p) V(xs:c)",
    ".tran 0 0.024 0 2u",
])
t = d["time"] * 1000
fig, ax = plt.subplots(3, 1, figsize=(9, 6.2), sharex=True)
ax[0].plot(t, d["V(b)"] * 1000, color="#1f77b4")
ax[0].set_ylabel("base Q2\n(mV)")
ax[1].plot(t, d["V(xs:c)"], color="#d62728")
ax[1].set_ylabel("colector Q2\n(V)")
ax[2].plot(t, d["V(p)"], color="#2ca02c")
ax[2].set_ylabel("salida p\n(V)")
ax[2].set_xlabel("tiempo (ms)    sin objeto hasta 12 ms, luego con objeto")
for a in ax:
    a.grid(alpha=.3)
    a.axvline(12, color="#888", lw=.8, ls="--")
ax[0].set_title("Sensor IR: senal de base, senal amplificada del BJT en emisor comun y salida logica")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "bjt_sensor_ir.png"), dpi=130)
plt.close(fig)
# ganancia de pequena senal medida en la simulacion (pico a pico del 1 kHz en cada estado)
i0 = (t > 6) & (t < 11)
i1 = (t > 18) & (t < 23)
for nom, ii in (("sin_objeto", i0), ("con_objeto", i1)):
    vb = np.ptp(d["V(b)"][ii])
    vc = np.ptp(d["V(xs:c)"][ii])
    datos["ganancia_" + nom] = round(float(vc / vb), 2)
datos["vc_sin_objeto"] = round(float(np.mean(d["V(xs:c)"][(t > 8) & (t < 11)])), 2)
datos["vc_con_objeto"] = round(float(np.mean(d["V(xs:c)"][(t > 20) & (t < 23)])), 2)
datos["p_sin_objeto"] = round(float(np.mean(d["V(p)"][(t > 8) & (t < 11)])), 2)
datos["p_con_objeto"] = round(float(np.mean(d["V(p)"][(t > 20) & (t < 23)])), 2)
limpiar(base)

# ------------------------------------------------------------ 2) PWM, compuerta y MOSFET con carga RL
d, base = correr("ondas_pwm_potencia", [
    "Vvm vm 0 12", "Vv5 v5 0 5", "Vm m 0 5", "Vc vctrl 0 2.4",
    "XP v5 vctrl pwm PWM_GEN",
    "XW v5 vm pwm m dm sh POTENCIA",
    "Rmot vm mot 12", "Lmot mot dm 3m",
    ".save V(pwm) V(xp:tri) V(xw:gate) V(dm) V(sh)",
    ".tran 0 0.012 0.010 0.1u",
])
t = (d["time"] - d["time"][0]) * 1e6
fig, ax = plt.subplots(5, 1, figsize=(9, 8.5), sharex=True)
ax[0].plot(t, d["V(xp:tri)"], color="#555"); ax[0].set_ylabel("rampa 555\n(V)")
ax[0].axhline(2.4, color="#d62728", lw=.8, ls="--")
ax[0].text(t[-1], 2.45, "vctrl = 2.4 V", ha="right", color="#d62728", fontsize=8)
ax[1].plot(t, d["V(pwm)"], color="#1f77b4"); ax[1].set_ylabel("PWM\n(V)")
ax[2].plot(t, d["V(xw:gate)"], color="#2ca02c"); ax[2].set_ylabel("compuerta\n(V)")
ax[3].plot(t, d["V(dm)"], color="#9467bd"); ax[3].set_ylabel("drenaje\n(V)")
ax[4].plot(t, d["V(sh)"] / 0.5 * 1000, color="#ff7f0e"); ax[4].set_ylabel("corriente\n(mA)")
ax[4].set_xlabel("tiempo (us)")
for a in ax:
    a.grid(alpha=.3)
ax[0].set_title("PWM del 555 + comparador, compuerta del MOSFET y carga del motor (12 ohm + 3 mH)")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "pwm_compuerta_mosfet.png"), dpi=130)
plt.close(fig)
pw = d["V(pwm)"]
alto = pw > 2.5
cruces = np.where(np.diff(alto.astype(int)) == 1)[0]
per = float(np.mean(np.diff(d["time"][cruces]))) if len(cruces) > 1 else float("nan")
datos["pwm_frecuencia_hz"] = round(1 / per)
datos["pwm_ciclo"] = round(float(np.mean(alto)), 3)
datos["gate_max_v"] = round(float(d["V(xw:gate)"].max()), 2)
datos["vds_max_v"] = round(float(d["V(dm)"].max()), 2)
limpiar(base)

# ------------------------------------------------------------ 3) encoder + conversor frecuencia-voltaje
d, base = correr("ondas_encoder_fv", [
    "Vv5 v5 0 5",
    "Be enc_s 0 V=5*u(sin(2*pi*(200*min(time,.1)+500*max(min(time,.2)-.1,0)+1000*max(time-.2,0))))",
    "Re enc_s enc 100",
    "XE v5 enc vspd ENCODER_FV",
    ".save V(enc) V(vspd)",
    ".ic V(vspd)=0 V(xe:vf1)=0",
    ".tran 0 0.3 0 3u",
])
t = d["time"] * 1000
fig, ax = plt.subplots(2, 1, figsize=(9, 5.2))
ax[0].plot(t, d["V(enc)"], lw=.7, color="#1f77b4")
ax[0].set_xlim(180, 200)
ax[0].set_ylabel("encoder (V)")
ax[0].set_title("Encoder: pulsos de la ranura (zona de 500 Hz) y salida F-V")
ax[0].set_xlabel("tiempo (ms)")
ax[1].plot(t, d["V(vspd)"], color="#d62728")
ax[1].set_ylabel("vspd (V)")
ax[1].set_xlabel("tiempo (ms)   200 Hz hasta 100 ms, 500 Hz hasta 200 ms, 1 kHz despues")
for a in ax:
    a.grid(alpha=.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "encoder_fv.png"), dpi=130)
plt.close(fig)
for f, (a, b) in ((200, (90, 100)), (500, (190, 200)), (1000, (290, 300))):
    datos["vspd_%dhz" % f] = round(float(np.mean(d["V(vspd)"][(t > a) & (t < b)])), 3)
limpiar(base)

# ------------------------------------------------------------ 4) sistema completo (simulacion ya guardada)
z = np.load(os.path.join(TEC, "sim", "sistema_desde_asc_resumen.npz"), allow_pickle=True)
t = z["time"]
rpm = z["V(w)"] * 60 / (2 * np.pi)


def cruces(x, nivel=2.5):
    s = np.where(np.diff((x > nivel).astype(int)) != 0)[0]
    return [(float(t[i]), int(x[i + 1] > nivel)) for i in s]


ev = {"p (objeto)": cruces(z["V(p)"]), "M": cruces(z["V(m)"]), "F (falla)": cruces(z["V(f)"]), "setn": cruces(z["V(setn)"], 2.5)}
datos["eventos"] = {k: [(round(a, 3), b) for a, b in v][:12] for k, v in ev.items()}
fig, ax = plt.subplots(5, 1, figsize=(10, 10), sharex=True)
ax[0].plot(t, z["V(v5)"], label="v5"); ax[0].plot(t, z["V(vm)"], label="vm")
ax[0].set_ylabel("V"); ax[0].legend(ncol=2, loc="center right"); ax[0].set_ylim(0, 13.5)
for k, col in (("V(p)", "#2ca02c"), ("V(m)", "#d62728"), ("V(n)", "#1f77b4"), ("V(l)", "#ff7f0e"), ("V(f)", "#9467bd")):
    ax[1].plot(t, z[k], lw=1, color=col, label=k[2:-1].upper())
ax[1].legend(ncol=5, loc="center right"); ax[1].set_ylabel("logica (V)")
ax[2].plot(t, rpm, color="#444"); ax[2].set_ylabel("velocidad (rpm)")
ax[3].plot(t, z["I(Lm)"] * 1000, color="#ff7f0e"); ax[3].set_ylabel("corriente\nmotor (mA)")
ax[4].plot(t, z["V(vref)"], label="vref"); ax[4].plot(t, z["V(vspd)"], label="vspd")
ax[4].plot(t, z["V(vctrl)"], label="vctrl"); ax[4].legend(ncol=3, loc="upper right"); ax[4].set_ylabel("lazo (V)")
ax[4].set_xlabel("tiempo (s)")
for a in ax:
    a.grid(alpha=.3)
ax[0].set_title("Sistema completo simulado: motor supuesto de 12 V (no es el motor real)")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "sistema_completo_eventos.png"), dpi=120)
plt.close(fig)
fig, ax = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
ax[0].plot(t, z["V(xoc:dl)"], color="#d62728"); ax[0].set_ylabel("Vdl (V)\nshunt amplificado")
ax[1].plot(t, z["V(tc)"], color="#1f77b4"); ax[1].set_ylabel("temperatura\n(C)")
ax[1].set_xlabel("tiempo (s)")
for a in ax:
    a.grid(alpha=.3)
ax[0].set_title("Sobrecorriente (shunt amplificado) y temperatura del NTC en la misma simulacion")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "sistema_proteccion_corriente_temperatura.png"), dpi=120)
plt.close(fig)

json.dump(datos, open(os.path.join(OUT, "datos_ondas.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(datos, indent=1, ensure_ascii=False))
