import re, json, os
d=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
meta=json.load(open(os.path.join(d,"scripts","logica_meta.json")))
v={}
for m in re.finditer(r"^(\w+): V\(([\w.:]+)\)=([-\d.e+]+)", open(os.path.join(d,"prueba_logica.log")).read(), re.M):
    v[m.group(1).lower()]=float(m.group(3))
bit=lambda x:1 if x>2.5 else 0
out=["| E | G | P | F | M | N | L | esperado M N L | LED objeto (mA) | ok |","|---|---|---|---|---|---|---|---|---|---|"]
bad=0
for name,t,(e,g,p,f) in meta["meas"]:
    n=name.lower()
    M=e&g&(1-f); N=M&(1-p); L=M&p
    got=[bit(v[f"{s}_{n}"]) for s in "mnl"]; F=bit(v[f"f_{n}"])
    iled=(5-v[f"lo_{n}"])/680*1000
    okled=(iled>2) if p else (iled<0.1)
    ok = got==[M,N,L] and F==f and okled; bad+= not ok
    out.append(f"| {e} | {g} | {p} | {F} | {got[0]} | {got[1]} | {got[2]} | {M} {N} {L} | {iled:.1f} | {'OK' if ok else 'ERROR'} |")
exp={"L1_FALLA_pulsada":(1,0),"L2_RESET_con_FALLA_pulsada":(1,0),"L3_FALLA_suelta_sin_reset":(1,0),"L4_RESET_con_FALLA_suelta":(0,1)}
out+=["","| Pestillo | F | M | esperado F,M | ok |","|---|---|---|---|---|"]
for name,t in meta["lat"]:
    F=bit(v[f"f_{name.lower()}"]);M=bit(v[f"m_{name.lower()}"]); ok=(F,M)==exp[name]; bad+=not ok
    out.append(f"| {name} | {F} | {M} | {exp[name][0]},{exp[name][1]} | {'OK' if ok else 'ERROR'} |")
out.append(f"\nErrores: {bad}")
open(os.path.join(d,"resultado_logica.md"),"w").write("\n".join(out)+"\n"); print("\n".join(out))
