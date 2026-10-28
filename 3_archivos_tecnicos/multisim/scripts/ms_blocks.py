import sys, json, csv, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_call import start, call

P = r"C:\Users\Diego Cruz\Documents\Proyecto_Final_Electronica_UNIS\3_archivos_tecnicos"
models = open(P + r"\modelos.inc", encoding="latin1").read()
sis = open(P + r"\sistema.inc", encoding="latin1").read()
models = "\n".join(x for x in models.splitlines() if not x.startswith(".model IRFZ44N_P"))
NM = ".model IRFZ44N_P NMOS(Level=1 Vto=3 Kp=12 Cbd=300p Cgso=1n Cgdo=0.3n Rd=6m Rs=3m)"
base = models + "\n" + NM + "\n" + sis + "\n"

p, s = start()
call(p, s, 1, "connect", {})
n = [10]


def run(title, body, cmd="op", timeout=240):
    n[0] += 1
    net = "* " + title + "\n" + base + body + "\n.end\n"
    r = call(p, s, n[0], "run_spice_netlist", {"netlist": net, "commands": cmd, "timeout": timeout})
    t = r["result"]["content"][0]["text"]
    if r["result"].get("isError"):
        print(title, "ERROR", t[:300])
        return None
    d = json.loads(t)
    if d.get("csv") and os.path.exists(d["csv"]):
        rows = list(csv.reader(open(d["csv"])))
        if len(rows) == 2:
            return dict(zip(rows[0], [float(x) for x in rows[1]]))
        return rows
    print(title, "sin csv", d.get("log_tail", "")[-500:])
    return None


def show(title, r, keys):
    if isinstance(r, dict):
        print(title, {k: round(v, 3) for k, v in r.items() if k in keys})


if __name__ == "__main__":
    SEN = "V5 v5 0 5\nIph v5 b %s\nXs v5 b tin p SENSOR_IR\nRtin tin 0 100Meg\n"
    for lab, i in (("sin objeto", "2u"), ("con objeto", "50u")):
        r = run("sensor " + lab, SEN % i)
        show("sensor " + lab, r, ("V(p)", "V(b)"))
        if r:
            print([k for k in r][:30])
