import sys, json, glob, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
G = "/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/kerr/b15b_gates/"
T = {t["id"]: t for t in json.load(open(G + "tasks.json"))}
OLD = {json.loads(l)["id"]: json.loads(l) for f in glob.glob(G + "mnflow_*.jsonl") for l in open(f)}
kerr = MNN.MNFlow(89, 80, 0, sp.Rational(49, 50), sp.Rational(445, 2))
_r = MNN.solve_ivp; mode = [None]; LOG = []
def rec(fun, span, y0, **k):
    if mode[0] == "new":
        ev0 = k.pop("events"); hi = [-np.inf]
        def ev(t, s): hi[0] = max(hi[0], t); return ev0(t, s)
        ev.direction = ev0.direction; ev.terminal = getattr(ev0, "terminal", False)
        sol = _r(fun, span, y0, t_eval=np.array([]), events=ev, **k); tl = float(hi[0])
    else: sol = _r(fun, span, y0, **k); tl = float(sol.t[-1])
    LOG.append((sol.status, bool(len(sol.t_events[0])), tl)); return sol
MNN.solve_ivp = rec
def run(t):
    w = np.array(t["w"])
    if t["call"] == "P":
        r = kerr.P(w, 1, jac=t["jac"], tmax=t["tmax"], rtol=t["tol"], atol=t["tol"])
        return None if r is None else [float(r[0][0]), float(r[0][1]), float(r[1])] + ([float(v) for v in np.asarray(r[2]).ravel()] if t["jac"] else [])
    r = kerr.Pinv(w, tmax=t["tmax"], rtol=t["tol"], atol=t["tol"]); return None if r is None else [float(r[0]), float(r[1])]
allok = True
for i in sys.argv[1:]:
    out = {}
    for m in ("old", "new"):
        mode[0] = m; LOG.clear(); out[m] = (run(T[i]), LOG[:])
    same = out["old"][0] == out["new"][0] == OLD[i]["value"]
    st = [x[:2] for x in out["old"][1]] == [x[:2] for x in out["new"][1]]
    allok &= same and st
    print(i, "values bit-identical (old-run, t_eval=[] run, jsonl):", same, "| status/events same:", st, "| final t sol.t[-1] vs last event-eval t:", out["old"][1][-1][2], out["new"][1][-1][2])
print("ALL IDENTICAL" if allok else "DIFFERENCE")
