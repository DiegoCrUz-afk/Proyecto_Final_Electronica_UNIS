"""Sistema completo en el motor de Multisim (via multisim-mcp). Uso: py ms_sistema.py <tstop> <escenario: corto|largo>"""
import sys, os, re, json, csv, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_call import start, call

P = r"C:\Users\Diego Cruz\Documents\Proyecto_Final_Electronica_UNIS\3_archivos_tecnicos"
models = open(P + r"\modelos.inc", encoding="latin1").read().replace("u(", "uu(")
sis = open(P + r"\sistema.inc", encoding="latin1").read().replace("u(", "uu(")
models = "\n".join(x for x in models.splitlines() if not x.startswith(".model IRFZ44N_P"))
NM = ".model IRFZ44N_P NMOS(Level=1 Vto=3 Kp=12 Cbd=300p Cgso=1n Cgdo=0.3n Rd=6m Rs=3m)"
NE555 = """
.func uu(x) {0.5*(1+tanh((x)/0.02))}
.subckt NE555 gnd trig out rst cv thr dis vcc
R1 vcc cv 5k
R2 cv nn 5k
R3 nn gnd 5k
Bq qd gnd V=V(vcc)*(uu(V(cv)/2-V(trig))+(1-uu(V(cv)/2-V(trig)))*(1-uu(V(thr)-V(cv)))*uu(V(q)-V(vcc)/2))*uu(V(rst)-0.7)
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
# el 555 y las compuertas del sistema.inc: se quita .param inline (ngspice lo acepta) y nada mas
DECK = {
 "corto": """* sistema completo (escenario corto: arranque, objeto, cubierta)
V12 vin 0 PWL(0 0 10m 12)
D1 vin vm D1N4007
Cin vm 0 1000u
Xreg vm v5 REG5V
Iph v5 b PWL(0 2u 0.06 2u 0.0601 50u 0.10 50u 0.1001 2u)
Xsen v5 b tin p SENSOR_IR
Rtin tin 0 100Meg
Ve ein 0 PWL(0 0 0.01 0 0.0101 5)
Vg gin 0 PWL(0 0 0.01 0 0.0101 5 0.13 5 0.1301 0 0.15 0 0.1501 5)
Vr rin 0 0
Xlog v5 ein gin rin p setn m n l f fn LOGICA
Xref v5 l vref REFVEL
Xerr vm v5 vref vspd vctrl ERROR_AMP
Xpwm v5 vctrl pwm PWM_GEN
Xpot v5 vm pwm m dm sh POTENCIA
Xenc v5 enc vspd ENCODER_FV
Xal vm f ALARMA
Xoc vm v5 sh setn SOBRECORRIENTE
Vtc tc 0 25
Bn v5 tnode I=V(v5,tnode)/(10k*exp(3950*(1/(V(tc)+273.15)-1/298.15)))
Xtm v5 tnode setn TEMPERATURA
Lm vm n1 3m
Rm n1 n2 12
Eb n2 dm value={Ke*V(w)}
Cw w 0 {J} ic=0
Bw 0 w I={Ke*I(Lm)-Bfr*V(w)-V(tl)*tanh(V(w))}
Vtl tl 0 0.004
Cph ph 0 1 ic=0
Rph ph 0 1G
Rw w 0 1G
Bph 0 ph I=20*V(w)/(2*pi)
Bsl encs 0 V=0.3+4.4*uu(sin(2*pi*V(ph)))
Renc encs enc 1k
.param Ke=0.035 J=1e-5 Bfr=7.2e-6
.options method=gear reltol=0.01 abstol=1e-9 vntol=1e-4 itl4=200 gmin=1e-9 trtol=10
""",
}
DECK["largo"] = DECK["corto"].replace("Iph v5 b PWL(0 2u 0.06 2u 0.0601 50u 0.10 50u 0.1001 2u)", "Iph v5 b PWL(0 2u 0.35 2u 0.3501 50u 0.55 50u 0.5501 2u)") \
    .replace("PWL(0 0 0.01 0 0.0101 5 0.13 5 0.1301 0 0.15 0 0.1501 5)", "PWL(0 0 0.01 0 0.0101 5 0.70 5 0.7001 0 0.80 0 0.8001 5)") \
    .replace("Vr rin 0 0", "Vr rin 0 PWL(0 0 1.25 0 1.2501 5 1.30 5 1.3001 0 1.60 0 1.6001 5 1.70 5 1.7001 0 1.95 0 1.9501 5 2.00 5 2.0001 0)") \
    .replace("Vtc tc 0 25", "Vtc tc 0 PWL(0 25 1.45 25 1.65 60 1.85 25)") \
    .replace("Vtl tl 0 0.004", "Vtl tl 0 PWL(0 0.004 0.95 0.004 0.9501 0.03 1.15 0.03 1.1501 0.004)")


def main():
    tstop = sys.argv[1] if len(sys.argv) > 1 else "0.15"
    esc = sys.argv[2] if len(sys.argv) > 2 else "corto"
    net = "* sistema\n" + models + "\n" + NM + "\n" + sis + "\n" + NE555 + DECK[esc] + ".end\n"
    p, s = start()
    call(p, s, 1, "connect", {})
    t0 = time.time()
    r = call(p, s, 5, "run_spice_netlist", {"netlist": net, "commands": "tran 10u %s 0 20u uic" % tstop, "timeout": 3500, "max_points": 100000, "output_dir": r"C:\ms_work\sistema_" + esc, "overwrite": True})
    t = r["result"]["content"][0]["text"]
    print("tiempo %.0f s" % (time.time() - t0), flush=True)
    if r["result"].get("isError"):
        print("ERROR", t[:500]); return
    d = json.loads(t)
    print({k: d[k] for k in ("state", "timed_out", "last_error", "csv") if k in d}, flush=True)
    print(d.get("log_tail", "")[-600:])
    p.kill()


main()
