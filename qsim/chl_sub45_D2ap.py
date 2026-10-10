"""Diagnostic D2a' (pre-registered 7c631cd): the q-integrand beyond the cut under two method-parameter sets A and B;
only nodes where A and B agree to <= 1e-6 count."""
import json, math, os, sys
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
XS = [math.radians(40.0), math.radians(15.0)]
TS = [0.3, 1.37]
SETS = {"A": dict(N=40, eps0="0.075", taylor_N=45, dplus=0), "B": dict(N=54, eps0="0.05", taylor_N=60, dplus=15)}
CK = os.path.join(HERE, "chl_sub45_D2ap_nodes.jsonl")

def work(job):
    import chl_node as nd
    t, q, s = job
    p = SETS[s]
    M = math.sqrt(0.25 + q*q)
    try:
        r = nd.compute_node(t, q, XS, N=p["N"], eps0=p["eps0"], taylor_N=p["taylor_N"], dps=int(30 + 3*M) + p["dplus"])
        r["ok"] = True
    except Exception as e:
        r = dict(t=t, q=q, ok=False, error=f"{type(e).__name__}: {e}")
    r["set"] = s
    return r

if __name__ == "__main__":
    done = set()
    if os.path.exists(CK):
        for line in open(CK):
            r = json.loads(line); done.add((round(r["t"], 6), round(r["q"], 6), r["set"]))
    jobs = [(t, t + 7.5 + 1.5*k, s) for t in TS for k in range(10) for s in SETS
            if (round(t, 6), round(t + 7.5 + 1.5*k, 6), s) not in done]
    print(len(jobs), "jobs", flush=True)
    with Pool(2) as pool, open(CK, "a") as fh:
        for r in pool.imap_unordered(work, jobs):
            fh.write(json.dumps(r) + "\n"); fh.flush()
            print(f"t={r['t']:.2f} q={r['q']:.2f} set={r['set']} ok={r['ok']}", flush=True)
    print("D2ap DONE", flush=True)
