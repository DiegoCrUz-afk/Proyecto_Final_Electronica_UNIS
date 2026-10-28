"""Retoque de los .ms14 ya generados: cables mas gruesos y nombres de red visibles sobre los cables.
Uso: python ms_post.py [nombre ...]   (lee de multisim\\, deja el resultado en C:\\ms_work\\post y lo copia de vuelta si abre bien)"""
import sys, os, re, glob, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mcp_call

D = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
W = r"C:\ms_work\post"
os.makedirs(W, exist_ok=True)


def txt(r):
    return r["result"]["content"][0]["text"]


def setkey(x, key, val):
    pat = re.compile(r'(<Element Key="&amp;ASC%s">\s*<Item Value=")[^"]*(")' % re.escape(key))
    x, n = pat.subn(r"\g<1>&amp;ASC%s\g<2>" % val, x)
    return x, n


def main(nombres):
    p, s = mcp_call.start()
    mcp_call.call(p, s, 1, "connect", {})
    i = 10
    for f in sorted(glob.glob(os.path.join(D, "*.ms14"))):
        nm = os.path.basename(f)[:-5]
        if nombres and nm not in nombres:
            continue
        xml = os.path.join(W, nm + ".xml")
        i += 1
        r = mcp_call.call(p, s, i, "decode_ms14", {"path": f, "output_xml": xml})
        if r["result"].get("isError"):
            print(nm, "no se pudo leer", flush=True)
            continue
        x = open(xml, encoding="utf8").read()
        x, a = setkey(x, "Wire Width", "3")
        x, b = setkey(x, "Show Node Names", "0")
        x, c = re.subn(r'(<CIITLinkComp [^>]*?)Pen-Width="1"', r'\g<1>Pen-Width="3"', x)
        open(xml, "w", encoding="utf8").write(x)
        out = os.path.join(W, nm + ".ms14")
        i += 1
        r = mcp_call.call(p, s, i, "encode_ms14", {"source_xml": xml, "output_ms14": out})
        ok = not r["result"].get("isError") and os.path.exists(out)
        if ok:
            i += 1
            r = mcp_call.call(p, s, i, "open_circuit", {"path": out})
            ok = not r["result"].get("isError") and not json.loads(txt(r)).get("last_error")
        print(nm, "ok" if ok else "ERROR", "(ancho %d, nombres %d, cables %d)" % (a, b, c), flush=True)
        if ok:
            shutil.copy(out, f)
        os.remove(xml)
        for z in glob.glob(os.path.join(D, "*.xml")):
            os.remove(z)
    p.kill()


if __name__ == "__main__":
    main(sys.argv[1:])
