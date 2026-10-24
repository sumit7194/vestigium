"""B15b: checkpointed MNFlow reference worker. Usage: b15b_mnflow_worker.py <worker index> <number of workers>
Takes every task of tasks.json whose position i satisfies i % n == index, in order, skipping task ids already in its
results file (resume after a kill or a reboot). Each result is one JSON line, flushed and fsync'ed:
  id, ok, value (P: [x, px, T, DP 2x2] / Pinv: [x, px]) or None, route (for a None: 'tmax', 'status -1', 'other'),
  seconds.
The route comes from wrapping the solve_ivp NAME that mn_numerics calls (MNFlow's code is untouched): every call's
sol.status and whether t_events was non-empty are recorded."""
import json, os, sys, time, numpy as np, sympy as sp
from pathlib import Path
import mn_numerics as MNN

OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "kerr" / "b15b_gates"
idx, nw = int(sys.argv[1]), int(sys.argv[2])
tasks = [t for i, t in enumerate(json.loads((OUT / "tasks.json").read_text())) if i % nw == idx]
res_path = OUT / ("mnflow_w%d.jsonl" % idx)
done = set()
if res_path.exists():
    for line in res_path.read_text().splitlines():
        try: done.add(json.loads(line)["id"])
        except Exception: pass                                 # a torn last line is recomputed
_real = MNN.solve_ivp; LOG = []
def _rec(*a, **k):
    sol = _real(*a, **k); LOG.append((sol.status, bool(len(sol.t_events[0])) if sol.t_events is not None else False, float(sol.t[-1]))); return sol
MNN.solve_ivp = _rec
kerr = MNN.MNFlow(89, 80, 0, sp.Rational(49, 50), sp.Rational(445, 2))
with open(res_path, "a") as fh:
    for t in tasks:
        if t["id"] in done: continue
        LOG.clear(); t0 = time.time(); w = np.array(t["w"])
        try:
            if t["call"] == "P":
                r = kerr.P(w, 1, jac=t["jac"], tmax=t["tmax"], rtol=t["tol"], atol=t["tol"])
                val = None if r is None else [float(r[0][0]), float(r[0][1]), float(r[1])] + ([float(v) for v in np.asarray(r[2]).ravel()] if t["jac"] else [])
            else:
                r = kerr.Pinv(w, tmax=t["tmax"], rtol=t["tol"], atol=t["tol"]); val = None if r is None else [float(r[0]), float(r[1])]
            ok = True; err = None
        except Exception as ex:
            val = None; ok = False; err = repr(ex)
        st = LOG[-1] if LOG else None
        route = None if val is not None else ("tmax" if st and st[0] == 0 and not st[1] else "status -1" if st and st[0] == -1 else "other")
        rec = dict(id=t["id"], ok=ok, value=val, route=route, solve_ivp=LOG[:], error=err, seconds=time.time() - t0)
        fh.write(json.dumps(rec) + "\n"); fh.flush(); os.fsync(fh.fileno())
        print("%s %s %.0fs" % (t["id"], "None(%s)" % route if val is None else "ok", rec["seconds"]), flush=True)
print("worker %d done" % idx)
