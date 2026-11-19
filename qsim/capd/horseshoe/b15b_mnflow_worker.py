"""B15b: checkpointed MNFlow reference worker.
Usage: b15b_mnflow_worker.py <worker index> <number of workers>      (original mode: every task i with i % n == index)
       b15b_mnflow_worker.py fast|grind <index> <number>             (scheduling mode, 2026-10-24, the Bridge agreed)
Scheduling mode takes only the tasks grind_prediction.json marks as non-grinding (fast) or grinding (grind), in task
order, k of n. The compiled map is used ONLY to ORDER the tasks; it never supplies or alters a reference value, and a
misclassified task just runs where it lands, under the same memory cap. Results go to mnflow_<mode><k>.jsonl, and ids
finished in ANY mnflow_*.jsonl are skipped. B15B_SKIP_MOD=n:k leaves out the tasks with position i % n == k (an original-mode
worker still running its share), so no task runs twice.
Takes every task of tasks.json whose position i satisfies i % n == index, in order, skipping task ids already in its
results file (resume after a kill or a reboot). Each result is one JSON line, flushed and fsync'ed:
  id, ok, value (P: [x, px, T, DP 2x2] / Pinv: [x, px]) or None, route (for a None: 'tmax', 'status -1', 'other'),
  seconds.
The route comes from wrapping the solve_ivp NAME that mn_numerics calls (MNFlow's code is untouched): every call's
sol.status and whether t_events was non-empty are recorded."""
import json, os, subprocess, sys, time, numpy as np, sympy as sp
from pathlib import Path
import mn_numerics as MNN

OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "kerr" / "b15b_gates"
ALL = json.loads((OUT / "tasks.json").read_text())
CLAIM = sys.argv[1] == "claim"
if CLAIM:                                              # claim mode (2026-11-19, the Bridge relayed Sumit's GO): every grind task,
    k = int(sys.argv[2])                               # taken dynamically through per-task claim files; one jsonl per worker
    grinds = {r["id"]: r["grinds"] for r in json.loads((OUT / "grind_prediction.json").read_text())}
    tasks = [t for t in ALL if grinds[t["id"]]]; res_path = OUT / ("mnflow_claim%d.jsonl" % k)
elif sys.argv[1] in ("fast", "grind"):
    mode, idx, nw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    grinds = {r["id"]: r["grinds"] for r in json.loads((OUT / "grind_prediction.json").read_text())}
    skip = os.environ.get("B15B_SKIP_MOD")             # "i%n==k": leave that original-mode worker's share alone
    sk = tuple(int(v) for v in skip.split(":")) if skip else None
    sel = [t for j, t in enumerate(ALL) if grinds[t["id"]] == (mode == "grind") and not (sk and j % sk[0] == sk[1])]
    tasks = [t for i, t in enumerate(sel) if i % nw == idx]; res_path = OUT / ("mnflow_%s%d.jsonl" % (mode, idx))
else:
    idx, nw = int(sys.argv[1]), int(sys.argv[2])
    tasks = [t for i, t in enumerate(ALL) if i % nw == idx]; res_path = OUT / ("mnflow_w%d.jsonl" % idx)
done = set()
for rp in OUT.glob("mnflow_*.jsonl"):
    for line in rp.read_text().splitlines():
        try: done.add(json.loads(line)["id"])
        except Exception: pass                                 # a torn last line is recomputed
# Gate overrides (claim-mechanism gate only; their outputs must not be named mnflow_*.jsonl in OUT):
#   B15B_TASKS=id,id,...  replaces the task list;  B15B_RES=path  the result file;  B15B_IGNORE_DONE=1  recompute done ids;
#   B15B_CLAIMS=dir  the claim directory;  B15B_DUMMY=seconds  sleep instead of computing (claim smoke test; value None).
# (B15B_DEFER was dropped on 2026-11-19: its only target, G1_00_P, was already done; it had been a no-op.)
if os.environ.get("B15B_TASKS"):
    want = os.environ["B15B_TASKS"].split(","); byid = {t["id"]: t for t in ALL}; tasks = [byid[i] for i in want]
if os.environ.get("B15B_RES"): res_path = Path(os.environ["B15B_RES"])
if os.environ.get("B15B_IGNORE_DONE"): done = set()
CLAIMS = Path(os.environ.get("B15B_CLAIMS", str(OUT / "claims"))); DUMMY = float(os.environ.get("B15B_DUMMY", "0"))
MYCMD = " ".join(sys.argv)
def _alive_same(pid, cmd):
    r = subprocess.run(["ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
    return r.endswith(cmd)
def all_done():
    if os.environ.get("B15B_IGNORE_DONE"):                  # gate runs: only the gate's own result files (same directory)
        return set(json.loads(l)["id"] for f in res_path.parent.glob("*.jsonl") for l in open(f) if l.strip())
    d = set()
    for rp in OUT.glob("mnflow_*.jsonl"):
        for line in rp.read_text().splitlines():
            try: d.add(json.loads(line)["id"])
            except Exception: pass
    return d
def claim(tid):
    """Atomic claim: O_CREAT|O_EXCL on CLAIMS/<id>. A claim whose PID is not alive with the same command line is stale: it is
    replaced by an atomic rename, then re-read after 1 s; the task is ours only if the file then names this PID."""
    CLAIMS.mkdir(parents=True, exist_ok=True); c = CLAIMS / tid; me = "%d %s\n" % (os.getpid(), MYCMD)
    try:
        fd = os.open(str(c), os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, me.encode()); os.close(fd); return True
    except FileExistsError:
        pid, _, cmd = c.read_text().strip().partition(" ")
        if pid.isdigit() and _alive_same(int(pid), cmd): return False
        tmp = CLAIMS / (".%s.%d" % (tid, os.getpid())); tmp.write_text(me); os.replace(tmp, c); time.sleep(1)
        return c.read_text() == me
# Memory fix (2026-11-18, teval_probe/FINDING.md, the Bridge approved): t_eval=[] stops solve_ivp storing every step
# (sol.t/sol.y grew ~62 MB/min on G1_00_P; MNFlow uses only t_events/y_events; bit-identical on 8 tasks). The logged
# final t is now the largest t the event function was evaluated at (= the last accepted step's end), not sol.t[-1].
# CAVEAT: untested on a status -1 run; flag any status -1 row to the Bridge before trusting its logged t.
_real = MNN.solve_ivp; LOG = []
def _rec(fun, span, y0, **k):
    ev0 = k.pop("events"); hi = [-np.inf]
    def ev(t, s): hi[0] = max(hi[0], t); return ev0(t, s)
    ev.direction = ev0.direction; ev.terminal = getattr(ev0, "terminal", False)
    sol = _real(fun, span, y0, t_eval=np.array([]), events=ev, **k)
    LOG.append((sol.status, bool(len(sol.t_events[0])) if sol.t_events is not None else False, float(hi[0]))); return sol
MNN.solve_ivp = _rec
kerr = MNN.MNFlow(89, 80, 0, sp.Rational(49, 50), sp.Rational(445, 2))
with open(res_path, "a") as fh:
    for t in tasks:
        if t["id"] in done: continue
        if CLAIM or os.environ.get("B15B_CLAIMS"):
            if t["id"] in all_done() or not claim(t["id"]): continue
        LOG.clear(); t0 = time.time(); w = np.array(t["w"])
        try:
            if DUMMY:
                time.sleep(DUMMY); val = None; ok = True; err = None
            elif t["call"] == "P":
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
print("worker %s done" % " ".join(sys.argv[1:]))
