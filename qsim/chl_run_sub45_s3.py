"""
Stage-3 sub-45 run (PREREG_cuspis_sub45_check.md, STAGE 3 ADDENDUM da2c63b; NON-BLIND). Stage-2 nodes are reused
from chl_sub45_nodes.jsonl unchanged. This adds, per t node of BOTH t rules, two q extension panels
[t+7.5, t+10.5] and [t+10.5, t+13.5] (nested Clenshaw-Curtis: 8 coarse / 16 fine) computed with method set B, plus
the two panel endpoints (t+10.5, t+13.5) recomputed with method set C for the per-t stability cut.
Checkpointed per node; restart-safe. Small t first (they carry the weight).   python chl_run_sub45_s3.py [workers]
"""
import json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chl_run_controls as R
import chl_run_sub45 as S2

XS = S2.XS
PANELS = (7.5, 10.5, 13.5)
N_EXT = {"coarse": 8, "fine": 16}
SETS = {"B": dict(N=54, eps0="0.05", taylor_N=60, dplus=15), "C": dict(N=72, eps0="0.035", taylor_N=80, dplus=30)}
CK = {s: os.path.join(HERE, f"chl_s3_nodes{s}.jsonl") for s in SETS}


def ext_nodes(res):
    out = []
    for t, wt in R.t_rule(R.NS[res]):
        for k, (a, b) in enumerate(zip(PANELS[:-1], PANELS[1:])):
            qn, qw = R.cc(N_EXT[res], t + a, t + b)
            for q, w in zip(qn, qw):
                out.append((t, wt, float(q), float(w), k))
    return out


def key(t, q):
    return f"{t:.12f}|{q:.12f}"


def _init():
    sys.path.insert(0, HERE)


def _work(job):
    import chl_node as nd
    t, q, s = job
    p = SETS[s]
    M = math.sqrt(0.25 + q*q)
    t0 = time.time()
    try:
        r = nd.compute_node(t, q, XS, N=p["N"], eps0=p["eps0"], taylor_N=p["taylor_N"], dps=int(30 + 3*M) + p["dplus"])
        r["ok"] = True
    except Exception as e:
        r = dict(t=t, q=q, ok=False, error=f"{type(e).__name__}: {e}")
    r["set"] = s; r["seconds"] = round(time.time() - t0, 1)
    return r


def load(s):
    done = {}
    if os.path.exists(CK[s]):
        for line in open(CK[s]):
            r = json.loads(line); done[key(r["t"], r["q"])] = r
    return done


def main(workers=2):
    from multiprocessing import Pool
    jobs = []
    seen = set()
    for res in R.RESOLUTIONS:
        for t, _, q, _, _ in ext_nodes(res):
            if key(t, q) not in seen:
                seen.add(key(t, q)); jobs.append((t, q, "B"))
    endpoints = sorted({(t, t + PANELS[1]) for res in R.RESOLUTIONS for t, _ in R.t_rule(R.NS[res])} |
                       {(t, t + PANELS[2]) for res in R.RESOLUTIONS for t, _ in R.t_rule(R.NS[res])})
    jobs += [(t, q, "C") for t, q in endpoints]
    doneB, doneC = load("B"), load("C")
    todo = [j for j in jobs if key(j[0], j[1]) not in (doneB if j[2] == "B" else doneC)]
    todo.sort(key=lambda j: (j[0], j[2]))              # small t first: they carry the weight
    print(f"{len(jobs)} jobs ({sum(1 for j in jobs if j[2] == 'C')} C endpoints), {len(todo)} to run, {workers} workers",
          flush=True)
    t0 = time.time()
    fh = {s: open(CK[s], "a") for s in SETS}
    with Pool(workers, initializer=_init) as pool:
        for i, r in enumerate(pool.imap_unordered(_work, todo), 1):
            fh[r["set"]].write(json.dumps(r) + "\n"); fh[r["set"]].flush()
            if i % 20 == 0 or not r["ok"]:
                print(f"  {i}/{len(todo)} ({time.time()-t0:.0f}s)" + ("" if r["ok"] else
                      f"  FAILED t={r['t']:.3f} q={r['q']:.3f} set={r['set']}: {r['error'][:80]}"), flush=True)
    print("S3 RUN DONE", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
