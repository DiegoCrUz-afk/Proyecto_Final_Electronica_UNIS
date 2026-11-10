"""Ayudas para correr LTspice en lote y leer sus resultados (.raw y .log).

Uso: from simlib import run, read_raw, measures
"""
import os
import re
import struct
import subprocess

import numpy as np

LTSPICE = os.path.expandvars(r"%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe")
AQUI = os.path.dirname(os.path.abspath(__file__))


def run(cir, timeout=900):
    """Corre LTspice -b sobre un .cir o .asc. Devuelve la ruta sin extension."""
    cir = os.path.abspath(cir)
    for ext in (".raw", ".log"):
        p = os.path.splitext(cir)[0] + ext
        if os.path.exists(p):
            os.remove(p)
    subprocess.run([LTSPICE, "-b", cir], timeout=timeout, cwd=os.path.dirname(cir),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = os.path.splitext(cir)[0]
    if not os.path.exists(base + ".log"):
        raise RuntimeError("LTspice no genero log: " + cir)
    return base


def log_errors(base):
    txt = open(base + ".log", encoding="latin1").read()
    return [l for l in txt.splitlines() if re.search(r"error|fatal|singular|failed|could not", l, re.I)]


def read_raw(path):
    """Lee un .raw binario de LTspice. Devuelve dict nombre->array (en pasos .step todo concatenado)
    y la lista de indices donde empieza cada paso."""
    data = open(path, "rb").read()
    idx = data.find("Binary:\n".encode("utf-16le"))
    if idx < 0:
        raise RuntimeError("raw sin seccion binaria (¿ascii?)")
    head = data[:idx].decode("utf-16le")
    body = data[idx + len("Binary:\n".encode("utf-16le")):]
    nvar = int(re.search(r"No\. Variables:\s*(\d+)", head).group(1))
    npts = int(re.search(r"No\. Points:\s*(\d+)", head).group(1))
    flags = re.search(r"Flags:\s*(.*)", head).group(1)
    names = []
    for line in head.split("Variables:\n")[1].splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            names.append(parts[2])
    cplx = "complex" in flags
    dbl = "double" in flags
    out = {n: [] for n in names}
    if cplx:
        arr = np.frombuffer(body, dtype=np.float64, count=npts * nvar * 2).reshape(npts, nvar, 2)
        for i, n in enumerate(names):
            out[n] = arr[:, i, 0] + 1j * arr[:, i, 1]
    else:
        if dbl:
            arr = np.frombuffer(body, dtype=np.float64, count=npts * nvar).reshape(npts, nvar)
            for i, n in enumerate(names):
                out[n] = arr[:, i]
        else:
            rec = np.dtype([("t", "<f8")] + [("v%d" % i, "<f4") for i in range(nvar - 1)])
            arr = np.frombuffer(body, dtype=rec, count=npts)
            out[names[0]] = arr["t"].astype(float)
            for i, n in enumerate(names[1:]):
                out[n] = arr["v%d" % i].astype(float)
    x = out[names[0]]
    xr = np.real(x)
    starts = [0] + [i for i in range(1, len(xr)) if abs(xr[i]) < abs(xr[i - 1]) and (xr[i] <= xr[0] + 1e-30)]
    return {k: np.asarray(v) for k, v in out.items()}, starts


def steps(d, starts):
    """Parte las curvas en una lista de dicts, uno por paso .step."""
    ends = starts[1:] + [len(next(iter(d.values())))]
    return [{k: v[s:e] for k, v in d.items()} for s, e in zip(starts, ends)]


def measures(base):
    """Lee las mediciones .meas del log: nombre -> lista de valores (uno por paso)."""
    txt = open(base + ".log", encoding="latin1").read()
    res = {}
    for m in re.finditer(r"Measurement: (\S+)\s*\n\s*step.*\n((?:\s*\d+\s+.*\n?)+)", txt):
        rows = [r.split() for r in m.group(2).strip().splitlines()]
        res[m.group(1).lower()] = [float(r[1]) for r in rows if len(r) > 1]
    # formato de .tran/.ac sin pasos: "nombre: expresion=valor at x"
    for m in re.finditer(r"^(\w+): .*?=\(?([-+0-9.eE]+)", txt, re.M):
        res.setdefault(m.group(1).lower(), [float(m.group(2))])
    return res
