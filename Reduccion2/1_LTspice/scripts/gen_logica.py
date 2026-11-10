# Genera 1_LTspice/prueba_logica.cir: 16 combinaciones E,G,P,F + prueba del pestillo (usa LOGICA de sistema.inc)
import os
d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T0, SL = 0.150, 0.020          # inicio de pruebas y duracion de cada combinacion (s)
combos = [(e,g,p) for e in (0,1) for g in (0,1) for p in (0,1)]
def pwl(ev, hi=1.0):           # ev = lista (t, nivel 0/1) -> PWL con escalones de 10 us
    pts=[(0,0)]; cur=0
    for t,v in ev:
        pts += [(t,cur),(t+1e-5,v)]; cur=v
    return "PWL(" + " ".join(f"{t:.6f} {v}" for t,v in pts) + ")"
E=[];G=[];P=[];S=[];R=[]
meas=[]
def slot(k, base): return base + k*SL
# Fase A: F=0
for k,(e,g,p) in enumerate(combos):
    t=slot(k,T0); E.append((t,e));G.append((t,g));P.append((t,p))
    meas.append((f"A_{e}{g}{p}", t+SL-0.002, (e,g,p,0)))
# FALLA 310-330 ms con E=G=1,P=0
tF=T0+8*SL
E.append((tF,1));G.append((tF,1));P.append((tF,0)); S+= [(tF,1),(tF+0.020,0)]
# Fase B: F=1
B0=T0+10*SL
for k,(e,g,p) in enumerate(combos):
    t=slot(k,B0); E.append((t,e));G.append((t,g));P.append((t,p))
    meas.append((f"B_{e}{g}{p}", t+SL-0.002, (e,g,p,1)))
# Prueba del pestillo con E=G=1,P=0
L0=B0+8*SL    # 510 ms
E.append((L0,1));G.append((L0,1));P.append((L0,0))
S += [(L0,1),(L0+0.050,0)]       # FALLA pulsada 510-560
R += [(L0+0.010,1),(L0+0.030,0)] # RESET 520-540 con FALLA pulsada
S_t_release = L0+0.050
R += [(L0+0.090,1),(L0+0.110,0)] # RESET 600-620 con FALLA suelta
lat = [("L1_FALLA_pulsada", L0+0.008),("L2_RESET_con_FALLA_pulsada", L0+0.028),
       ("L3_FALLA_suelta_sin_reset", L0+0.085),("L4_RESET_con_FALLA_suelta", L0+0.140)]
tend = L0+0.160
def collapse(ev):  # S y R vienen como (t,nivel) ya ordenados
    return sorted(ev)
net=[f"* Reduccion 2 - prueba de la logica (E,G,P,F -> M,N,L) y del pestillo; generado por scripts/gen_logica.py",
".include modelos.inc",".include sistema.inc",".include reduccion2.inc",
"Vcc v5 0 PWL(0 0 1m 5)",
"* P = salida del sensor (0 sin objeto, 5 V con objeto)",
f"Vp p 0 {pwl(P).replace('PWL(','PWL(').replace(' 1',' 5')}" ]
# arreglo: P en voltios (0 o 5)
def pwlv(ev,hi):
    pts=[(0,0)]; cur=0
    for t,v in sorted(ev):
        pts += [(t,cur*hi),(t+1e-5,v*hi)]; cur=v
    return "PWL(" + " ".join(f"{t:.6f} {x:g}" for t,x in pts) + ")"
net[-1]=f"Vp p 0 {pwlv(P,5)}"
net += [f"* Toggle E y micro-switch G: 5 V -> entrada (control 1 = cerrado)",
f"Ve ce 0 {pwlv(E,1)}", f"Vg cg 0 {pwlv(G,1)}",
f"Vs cs 0 {pwlv(S,1)}", f"Vr cr 0 {pwlv(R,1)}",
".model SWB SW(Ron=0.1 Roff=1G Vt=0.5 Vh=0.1)",
"Se v5 ein ce 0 SWB","Sg v5 gin cg 0 SWB","Sr v5 rin cr 0 SWB",
"* Pulsador FALLA: setn a GND (10k a 5 V ya esta dentro de LOGICA)","Sf setn 0 cs 0 SWB",
"XL v5 ein gin rin p setn m n l f fn LOGICA_R2",
f".tran 0 {tend:.3f} 0 10u", ".options plotwinsize=0"]
for name,t,(e,g,p,f) in meas:
    for s in ("m","n","l","f"):
        net.append(f".meas tran {s}_{name} find V({s}) at={t:.4f}")
    net.append(f".meas tran lo_{name} find V(xl:lo) at={t:.4f}")
    for sg in ("e", "g"):
        net.append(f".meas tran {sg}limpio_{name} find V(xl:{sg}) at={t:.4f}")
for name,t in lat:
    for s in ("m","f"):
        net.append(f".meas tran {s}_{name} find V({s}) at={t:.4f}")
    net.append(f".meas tran setn_{name} find V(setn) at={t:.4f}")
    net.append(f".meas tran fn_{name} find V(fn) at={t:.4f}")
    net.append(f".meas tran rstlimpio_{name} find V(xl:rst) at={t:.4f}")
net.insert(-1,".save V(xl:lo) V(xl:e) V(xl:g) V(xl:rst) V(setn) V(m) V(n) V(l) V(f) V(fn) V(p) V(ein)")
net.append(".end")
open(os.path.join(d,"prueba_logica.cir"),"w").write("\n".join(net)+"\n")
import json
json.dump({"meas":[(n,t,list(c)) for n,t,c in meas],"lat":lat},open(os.path.join(d,"scripts","logica_meta.json"),"w"))
print("ok", tend)
