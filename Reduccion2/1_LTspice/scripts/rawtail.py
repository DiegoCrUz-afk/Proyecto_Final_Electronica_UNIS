import sys; sys.path.insert(0,"scripts")
from simlib import read_raw
d,_=read_raw(sys.argv[1]); t=d["time"]; print(len(t), t[-1]); print([k for k in d][:12])
