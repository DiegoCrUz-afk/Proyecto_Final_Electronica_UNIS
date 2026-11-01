import subprocess, json, os, sys
def start():
    env = dict(os.environ); la = os.environ["LOCALAPPDATA"]
    env["MULTISIM_MCP_EWD"] = la + r"\ewtools\dist\ewd.js"
    env["MULTISIM_MCP_EWE"] = la + r"\ewtools\dist\ewe.js"
    env["MULTISIM_MCP_TEMPLATE_DIR"] = la + r"\multisim_pack"
    env["MULTISIM_MCP_WORK_DIR"] = r"C:\ms_work"
    p = subprocess.Popen([la + r"\Programs\Python\Python312-32\Scripts\multisim-mcp.exe", "serve"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env, text=True, encoding="utf-8")
    s = lambda o: (p.stdin.write(json.dumps(o)+"\n"), p.stdin.flush())
    s({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"c","version":"1"}}})
    p.stdout.readline()
    s({"jsonrpc":"2.0","method":"notifications/initialized"})
    return p, s
def call(p, s, i, name, args):
    s({"jsonrpc":"2.0","id":i,"method":"tools/call","params":{"name":name,"arguments":args}})
    while True:
        m = json.loads(p.stdout.readline())
        if m.get("id") == i: return m
