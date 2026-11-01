import sys, re, numpy as np, pickle
fn = sys.argv[1]
f = open(fn, "rb")
head = b""
while True:
    l = f.readline()
    head += l
    if l.startswith(b"Values:"): break
head = head.decode("latin1")
nv = int(re.search(r"No. Variables: (\d+)", head).group(1))
names = [l.split("\t")[-1].strip() for l in head.split("Variables:")[-1].split("Values:")[0].split("\n") if l.count("\t") >= 3]
want = ["time", "V(v5)", "V(vm)", "V(p)", "V(m)", "V(n)", "V(l)", "V(f)", "V(vref)", "V(vspd)", "V(vctrl)", "V(w)", "V(setn)", "V(gate:xpot)", "V(dm)", "V(pwm)", "V(ein)", "V(gin)"]
ix = [names.index(w) for w in want]
cols = {w: [] for w in want}
k = 0; buf = []
for raw in f:
    s = raw.strip()
    if not s: continue
    v = s.split(b"\t")[-1]
    if k == 0 and b"\t" in s and not s.startswith(b"\t"): pass
    buf.append(v)
    k += 1
    if k == nv:
        for w, j in zip(want, ix): cols[w].append(buf[j])
        buf = []; k = 0
a = {w: np.array(cols[w], dtype=float) for w in want}
pickle.dump(a, open(sys.argv[2], "wb"))
print("puntos", len(a["time"]), "t final %.4f" % a["time"][-1])
