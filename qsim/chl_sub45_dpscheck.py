"""Registered precision floor (Stage 2 addendum): the 30 nodes with the largest |weight x integrand| at 15 deg are
recomputed at dps + 15; per-node trG(15 deg) must agree to <= 1e-12 relative."""
import json, math, os, sys
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chl_run_controls as R, chl_run_sub45 as S
X15 = math.radians(15.0)

def work(tq):
    import chl_node as nd, chl_run_sub45 as S2
    t, q, dps0 = tq
    r = nd.compute_node(t, q, S2.XS, dps=dps0 + 15)
    k = [k for k in r["trG"] if abs(float(k) - X15) < 1e-9][0]
    return t, q, r["trG"][k][0], r["dps"]

if __name__ == "__main__":
    done = S.load_done()
    w = {}
    for t, wt, q, wq in R.nodes("fine"):
        r = done[R.key(t, q)]
        k = [k for k in r["trG"] if abs(float(k) - X15) < 1e-9][0]
        w[(t, q)] = (abs(wt*wq*q*q/math.cosh(math.pi*t)**2*r["trG"][k][0]), r["trG"][k][0], r["dps"])
    top = sorted(w, key=lambda k: -w[k][0])[:30]
    with Pool(2) as pool:
        got = pool.map(work, [(t, q, w[(t, q)][2]) for t, q in top])
    rows = [dict(t=t, q=q, dps=w[(t, q)][2], dps_hi=dh, base=w[(t, q)][1], hi=v, rel=abs(v - w[(t, q)][1])/abs(v))
            for t, q, v, dh in got]
    worst = max(r["rel"] for r in rows)
    out = dict(nodes=rows, worst_rel=worst, pass_=worst <= 1e-12)
    json.dump(out, open(os.path.join(HERE, "chl_sub45_dpscheck.json"), "w"), indent=1)
    print("worst rel", worst, "PASS" if worst <= 1e-12 else "FAIL")
