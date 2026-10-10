"""Diagnostic D2a (pre-registered 7e955c5): measure the q-integrand beyond the Stage-2 cut q = t + 7.5, at 15 and 40 deg,
for t in {0.3, 1.37, 3.0}, q = t + 7.5 ... t + 30 step 1.5. Integrand (per unit q, t-weight included):
  f(t, q) = sech^2(pi t) q^2 Re trG(x, sqrt(1/4 + q^2), 1/2 - i t). Checkpointed per node."""
import json, math, os, sys
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
XS = [math.radians(40.0), math.radians(15.0)]
TS = [0.3, 1.37, 3.0]
CK = os.path.join(HERE, "chl_sub45_D2a_nodes.jsonl")

def work(tq):
    import chl_node as nd
    t, q = tq
    try:
        r = nd.compute_node(t, q, XS); r["ok"] = True
    except Exception as e:
        r = dict(t=t, q=q, ok=False, error=f"{type(e).__name__}: {e}")
    return r

if __name__ == "__main__":
    done = set()
    if os.path.exists(CK):
        for line in open(CK):
            r = json.loads(line); done.add((round(r["t"], 6), round(r["q"], 6)))
    todo = [(t, t + 7.5 + 1.5*k) for t in TS for k in range(16) if (round(t, 6), round(t + 7.5 + 1.5*k, 6)) not in done]
    print(len(todo), "nodes to run", flush=True)
    with Pool(2) as pool, open(CK, "a") as fh:
        for r in pool.imap_unordered(work, todo):
            fh.write(json.dumps(r) + "\n"); fh.flush()
            print(f"t={r['t']:.2f} q={r['q']:.2f} ok={r['ok']}", flush=True)
    print("D2a DONE", flush=True)
