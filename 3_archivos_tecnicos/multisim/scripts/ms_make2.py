import sys, json, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_call import start, call

P = r"C:\Users\Diego Cruz\Documents\Proyecto_Final_Electronica_UNIS\3_archivos_tecnicos"
models = open(P + r"\modelos.inc", encoding="latin1").read()
sis = open(P + r"\sistema.inc", encoding="latin1").read()
models = "\n".join(x for x in models.splitlines() if not x.startswith(".model IRFZ44N_P"))
NM = ".model IRFZ44N_P NMOS(Level=1 Vto=3 Kp=12 Cbd=300p Cgso=1n Cgdo=0.3n Rd=6m Rs=3m)"


def subs(name):
    out = [".model SWSCH SW(Ron=1 Roff=1G Vt=2.5 Vh=0.5)"]
    for g in ("HC_AND2", "HC_NAND2", "HC_BUF", "HC_SCHINV", name):
        m = re.search(r"\.subckt %s .*?\.ends" % g, sis, re.S)
        out.append(m.group(0))
    return "\n".join(out) + "\n"


TB = {
    "REG5V": "V12 vm 0 12\nXr vm v5 REG5V\nIl v5 0 DC 75m\n",
    "SENSOR_IR": "V5 v5 0 5\nIph v5 b 50u\nXs v5 b tin p SENSOR_IR\nRtin tin 0 100Meg\n",
    "SOBRECORRIENTE": "V12 vm 0 12\nV5 v5 0 5\nVs sh 0 0.5\nXo vm v5 sh setn SOBRECORRIENTE\nRsn v5 setn 10k\n",
    "TEMPERATURA": "V5 v5 0 5\nRn v5 tnode 3.6k\nXt v5 tnode setn TEMPERATURA\nRsn v5 setn 10k\n",
    "LOGICA": "V5 v5 0 5\nVe ein 0 5\nVg gin 0 5\nVp p 0 0\nVr rin 0 0\nVs setn 0 5\nXl v5 ein gin rin p setn m n l f fn LOGICA\n",
    "PWM_GEN": "V5 v5 0 5\nVc vctrl 0 2.4\nXp v5 vctrl pwm PWM_GEN\n",
    "POTENCIA": "V12 vm 0 12\nV5 v5 0 5\nVp pwm 0 5\nVm m 0 5\nXp v5 vm pwm m dm sh POTENCIA\nRmot vm dm 12\n",
    "ENCODER_FV": "V5 v5 0 5\nVenc enc 0 PULSE(0.3 4.7 0 1u 1u 1m 2m)\nXe v5 enc vspd ENCODER_FV\n",
    "REFVEL": "V5 v5 0 5\nVl l 0 0\nXr v5 l vref REFVEL\n",
    "ERROR_AMP": "V12 vm 0 12\nV5 v5 0 5\nVr vref 0 0.526\nVs vspd 0 0.45\nXe vm v5 vref vspd vctrl ERROR_AMP\n",
    "ALARMA": "V12 vm 0 12\nVf f 0 5\nXa vm f ALARMA\n",
}

if __name__ == "__main__":
    p, s = start()
    call(p, s, 1, "connect", {})
    os.makedirs(r"C:\ms_work\bloques", exist_ok=True)
    only = sys.argv[1:] or list(TB)
    for i, name in enumerate(only):
        net = "* " + name + "\n" + models + "\n" + NM + "\n" + subs(name) + TB[name] + ".end\n"
        out = r"C:\ms_work\bloques\BLOQUE_%s.ms14" % name
        r = call(p, s, 10 + i, "create_schematic_from_netlist",
                 {"netlist": net, "output_ms14": out, "open_after_build": False, "overwrite": True})
        t = r["result"]["content"][0]["text"]
        if r["result"].get("isError"):
            print(name, "ERROR", t[:200], flush=True)
            continue
        d = json.loads(t)
        print(name, "success=", d.get("success"), "ms14:", os.path.exists(out), flush=True)
    p.kill()
