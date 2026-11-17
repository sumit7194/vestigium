"""macOS 27.2 regression: recompute the 6 fastest finished MNFlow reference tasks (P with jac where available) and compare
BIT FOR BIT with the stored values. Usage: mnflow_recheck.py"""
import sys, json, glob, numpy as np, sympy as sp
from pathlib import Path
H = Path("/Users/sumit/Github/quantum/qsim/capd/horseshoe"); sys.path.insert(0, str(H))
import mn_numerics as MNN
G = H.parent / "horseshoe_results/kerr/b15b_gates"
tasks = {t["id"]: t for t in json.loads((G / "tasks.json").read_text())}
ref = {}
for p in glob.glob(str(G / "mnflow_*.jsonl")):
    for line in open(p):
        try: r = json.loads(line); ref[r["id"]] = r
        except Exception: pass
pick = sorted([r for r in ref.values() if r["value"] is not None and r["seconds"] > 0.5], key=lambda r: (not tasks[r["id"]].get("jac"), r["seconds"]))[:6]
kerr = MNN.MNFlow(89, 80, 0, sp.Rational(49, 50), sp.Rational(445, 2)); bad = 0
for r in pick:
    t = tasks[r["id"]]; w = np.array(t["w"])
    if t["call"] == "P":
        o = kerr.P(w, 1, jac=t["jac"], tmax=t["tmax"], rtol=t["tol"], atol=t["tol"])
        v = [float(o[0][0]), float(o[0][1]), float(o[1])] + ([float(x) for x in np.asarray(o[2]).ravel()] if t["jac"] else [])
    else:
        o = kerr.Pinv(w, tmax=t["tmax"], rtol=t["tol"], atol=t["tol"]); v = [float(o[0]), float(o[1])]
    same = v == r["value"]; bad += not same
    print("%-12s %-4s jac=%-5s %s" % (r["id"], t["call"], t.get("jac"), "IDENTICAL" if same else "DIFFERS %s vs %s" % (v, r["value"])))
print("MNFLOW", "IDENTICAL" if bad == 0 else "DIFFERS", "%d/%d" % (len(pick) - bad, len(pick)))
