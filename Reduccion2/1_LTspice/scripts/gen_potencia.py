# Genera prueba_potencia_*.cir: IRLZ44N + Rs + puente (2N3904 o MOSFET) con motor supuesto, y barrido de Rs
import os
d=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def netlist(puente="bjt", rs_list="10", Ra=12, La="3m", Ke=0.035, Tl=0.004, titulo=""):
    L=[f"* Reduccion 2 - potencia a 5 V ({titulo}). Motor SUPUESTO Ra={Ra} La={La} Ke={Ke} Tl={Tl} (no es el Steren medido)",
    ".include modelos.inc",".include reduccion2.inc",
    "Vcc v5 0 5","Cb v5 0 100u","Cc v5 0 100n",
    "* m = permiso del motor (74HC08, 0/5 V); n = velocidad normal (0 = objeto)",
    "Vm m 0 PWL(0 0 0.3 0 0.3001 5 3.9 5 3.9001 0)",
    "Vn n 0 PWL(0 0 0.3 0 0.3001 5 1.5 5 1.5001 0 2.7 0 2.7001 5)",
    "Rpd m 0 10k",
    "M1 ds m 0 0 IRLZ44N_P",
    "* motor entre 5 V y dm; Rs entre dm y ds; diodo de dm a 5 V",
    f"Lm v5 x {La}", f"Rm x n2 {Ra}", "Beb n2 dm V=Ke*V(w)",
    "Dfw dm v5 D1N5819", "Rs dm ds {Rs}"]
    if puente=="bjt":
        L+=["Rb n bq 1k","Qp dm bq ds Q2N3904"]
    elif puente=="mos":
        L+=["Mp dm n ds ds IRLZ44N_P"]
    L+=["* mecanica del motor (igual que el original)",
    "Cw w 0 {J} ic=0","Bw 0 w I=Ke*I(Lm)-Bfr*V(w)-Tl*tanh(V(w))",
    f".param Ke={Ke} J=1e-5 Bfr=7.2e-6 Tl={Tl} Rs={rs_list.split()[0]}"]
    if len(rs_list.split())>1: L.append(f".step param Rs list {rs_list}")
    L+=[".tran 0 4.2 0 100u",".options plotwinsize=0",
    ".save V(w) I(Lm) V(dm) V(ds) V(m) V(n) V(bq)",
    ".meas tran w_normal find V(w) at=1.4",".meas tran w_lento find V(w) at=2.6",".meas tran w_normal2 find V(w) at=3.8",
    ".meas tran i_normal find I(Lm) at=1.4",".meas tran i_lento find I(Lm) at=2.6",
    ".meas tran vds_normal find V(dm) at=1.4",".meas tran vmotor_lento find V(dm) at=2.6",
    ".meas tran vpk_gate max V(m)",
    ".meas tran ipico_arranque max I(Lm) from=0.3 to=0.8",
    ".end"]
    return "\n".join(L)+"\n"
w=lambda n,**k: open(os.path.join(d,n),"w").write(netlist(**k))
w("prueba_potencia_barrido_bjt.cir",puente="bjt",rs_list="1 4.7 10 15 22 33 47",titulo="puente 2N3904, barrido Rs")
w("prueba_potencia_barrido_mos.cir",puente="mos",rs_list="1 4.7 10 15 22 33 47",titulo="puente MOSFET, barrido Rs")
print("ok")
# --- corrida final Rs=15 (con medicion de la corriente del puente) y barrido fino
def extra(s):
    mas = [".save I(Qp) V(bq)", ".meas tran icmax_puente max abs(Ic(Qp))", ".meas tran vce_normal find V(dm)-V(ds) at=1.4",
           ".meas tran vrs_lento find V(dm)-V(ds) at=2.6", ".meas tran vbe_normal find V(bq)-V(ds) at=1.4", ".meas tran vbe_lento find V(bq)-V(ds) at=2.6",
           ".meas tran vdm_parado find V(dm) at=0.2", ".meas tran vgate_on find V(m) at=1.4", ".meas tran i_parado find I(Lm) at=0.2", ".end"]
    return s.replace(".end", chr(10).join(mas))
open(os.path.join(d,"prueba_potencia_Rs15_bjt.cir"),"w").write(extra(netlist(puente="bjt",rs_list="15",titulo="puente 2N3904, Rs=15")).replace(".save V(w) I(Lm) V(dm) V(ds) V(m) V(n) V(bq)\n",".save V(w) I(Lm) V(dm) V(ds) V(m) V(n) V(bq) I(Qp)\n").replace("\n.save I(Qp) V(bq)",""))
open(os.path.join(d,"prueba_potencia_Rs15_mos.cir"),"w").write(netlist(puente="mos",rs_list="15",titulo="puente MOSFET, Rs=15"))
open(os.path.join(d,"prueba_potencia_fino_bjt.cir"),"w").write(netlist(puente="bjt",rs_list="11 12 13 14 15 16 17 18 19",titulo="barrido fino"))
