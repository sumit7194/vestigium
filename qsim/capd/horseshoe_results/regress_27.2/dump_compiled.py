"""macOS 27.2 regression: every B15b task through both compiled maps; values as float.hex (bit-exact compare old vs rebuilt).
Usage: dump_compiled.py <out.json>"""
import sys, json, numpy as np
from pathlib import Path
H = Path("/Users/sumit/Github/quantum/qsim/capd/horseshoe"); sys.path.insert(0, str(H))
import kerr_compiled as K
tasks = json.loads((H.parent / "horseshoe_results/kerr/b15b_gates/tasks.json").read_text())
out = {}
for name, path in (("rust", K.RUST), ("c++", K.CPP)):
    f = K.CompiledFlow(path); res = {}
    for t in tasks:
        w = np.array(t["w"]); f.plunges.clear()
        try:
            if t["call"] == "P":
                r = f.P(w, 1, jac=t["jac"], tmax=t["tmax"], rtol=t["tol"], atol=t["tol"])
                v = None if r is None else [r[0][0], r[0][1], r[1]] + (list(np.asarray(r[2]).ravel()) if t["jac"] else [])
            else:
                r = f.Pinv(w, tmax=t["tmax"], rtol=t["tol"], atol=t["tol"]); v = None if r is None else [r[0], r[1]]
            res[t["id"]] = None if v is None else [float(x).hex() for x in v]
            if v is None: res[t["id"]] = "plunge" if f.plunges else "none"
        except K.MapCheckFailed as e:
            res[t["id"]] = "MapCheckFailed: %s" % e
    out[name] = res
Path(sys.argv[1]).write_text(json.dumps(out, indent=0)); print("dumped", {k: len(v) for k, v in out.items()})
