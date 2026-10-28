import sys
sys.path.insert(0, '..')
from simlib import run, log_errors
base = run('sistema_desde_asc.cir', timeout=2400)
print(log_errors(base))
