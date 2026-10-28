import sys
sys.path.insert(0,'..')
import numpy as np
from simlib import read_raw
d,_=read_raw('sistema_desde_asc.raw'); tm=np.real(d['time'])
print('puntos',len(tm),'senales',[n for n in d if n.startswith('V(') or n.startswith('I(')])
def avg(n,a,b):
    m=(tm>=a)&(tm<=b); return float(d[n][m].mean())
rpm=lambda w:w*60/(2*np.pi)
filas=[(0.25,0.40,'normal'),(0.80,1.05,'objeto presente (velocidad reducida)'),(1.20,1.35,'objeto retirado'),(1.45,1.58,'cubierta abierta'),(1.75,1.88,'cubierta cerrada de nuevo'),
       (2.40,2.55,'falla de corriente enclavada'),(2.85,2.95,'tras reset'),(3.60,3.75,'falla de temperatura (caliente)'),(3.95,4.10,'enfriado, falla sigue enclavada'),(4.40,4.55,'tras reset con todo normal')]
print('%-36s %5s %5s %4s %4s %4s %4s %4s | %6s %6s %6s | %7s %5s'%('situacion','v5','vm','P','M','N','L','A','Vref','Vspd','Vctrl','rpm','Im'))
for a,b,l in filas:
    f=lambda n:avg(n,a,b)
    print('%-36s %5.2f %5.2f %4.1f %4.1f %4.1f %4.1f %4.1f | %6.3f %6.3f %6.2f | %7.0f %5.3f'%(l,f('V(v5)'),f('V(vm)'),f('V(p)'),f('V(m)'),f('V(n)'),f('V(l)'),f('V(f)'),f('V(vref)'),f('V(vspd)'),f('V(vctrl)'),rpm(f('V(w)')),f('I(Lm)')))
# tiempos de evento
def first(cond,t0,t1):
    idx=np.where(cond&(tm>=t0)&(tm<=t1))[0]; return tm[idx[0]] if len(idx) else None
print('disparo por sobrecorriente (setn<2.5 V) en t =',first(d['V(setn)']<2.5,1.85,2.4))
print('f sube (alarma) en t =',first(d['V(f)']>2.5,1.85,2.4), ' ; Im max tras carga extra: %.3f A'%d['I(Lm)'][(tm>1.9)&(tm<2.1)].max())
print('disparo por temperatura en t =',first(d['V(setn)']<2.5,3.0,3.6),' temperatura entonces %.1f C'%np.interp(first(d['V(setn)']<2.5,3.0,3.6),tm,d['V(tc)']))
print('M cae al abrir la cubierta en t =',first(d['V(m)']<2.5,1.40,1.6),' (cubierta abre en 1.40)')
print('reset 3.55-3.70 (el NTC ya bajo de 47 C, limpia): f en 3.75 =%.2f (debe ser 0)'%np.interp(3.75,tm,d['V(f)']))
# regulador y fuente
m=(tm>0.25)
print('v5 minimo/maximo con motor: %.3f / %.3f V ; vm min %.2f V'%(d['V(v5)'][m].min(),d['V(v5)'][m].max(),d['V(vm)'][m].min()))
print('I(D1) maxima %.3f A'%d['I(D1)'][m].max())
print('arranque: Im max entre 0.1 y 0.4 s = %.3f A'%d['I(Lm)'][(tm>0.1)&(tm<0.4)].max())
# compuerta y MOSFET en regimen normal
mm=(tm>0.30)&(tm<0.31)
print('compuerta: min %.2f max %.2f V ; Vds max %.1f V'%(d['V(xpot:gate)'][mm].min(),d['V(xpot:gate)'][mm].max(),d['V(dm)'][mm].max()))
np.savez_compressed('sistema_desde_asc_resumen.npz',**{k:d[k][::50] for k in ['time','V(v5)','V(vm)','V(p)','V(setn)','V(m)','V(n)','V(l)','V(f)','V(vref)','V(vspd)','V(vctrl)','V(w)','I(Lm)','V(tc)','V(tnode)','V(xoc:dl)']})
