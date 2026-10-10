"""Diagnostic D3 (pre-registered f656fe6): method-parameter stability of Stage-2 nodes. The 20 fine-grid nodes with
the largest M plus the 10 with the largest |weight x trG(15)|, recomputed with taylor_N 45, N 40, eps0 0.075 (dps as
before). Reports the per-node relative change and the implied delta a(theta) = sum(weight x delta trG)."""
import json, math, os, sys
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chl_run_controls as R, chl_run_sub45 as S
ANG = {"15": 15.0, "20": 20.0, "26.565": 26.565, "30": 30.0, "40": 40.0}

def pick(r, deg):
    x = math.radians(deg); return [v[0] for k, v in r["trG"].items() if abs(float(k) - x) < 1e-9][0]

def work(tq):
    import chl_node as nd, chl_run_sub45 as S2
    t, q = tq
    try:
        r = nd.compute_node(t, q, S2.XS, N=40, eps0="0.075", taylor_N=45); r["ok"] = True
    except Exception as e:
        r = dict(t=t, q=q, ok=False, error=f"{type(e).__name__}: {e}")
    return r

if __name__ == "__main__":
    done = S.load_done()
    grid = R.nodes("fine")
    W = {(t, q): wt*wq*q*q/math.cosh(math.pi*t)**2 for t, wt, q, wq in grid}
    byM = sorted(W, key=lambda k: -done[R.key(*k)]["M"])[:20]
    byW = sorted(W, key=lambda k: -abs(W[k]*pick(done[R.key(*k)], 15.0)))[:10]
    sel = list(dict.fromkeys(byM + byW))
    with Pool(2) as pool:
        got = pool.map(work, sel)
    rows, dA = [], {a: 0.0 for a in ANG}
    for (t, q), r in zip(sel, got):
        base = done[R.key(t, q)]
        row = dict(t=t, q=q, M=base["M"], ok=r["ok"], error=r.get("error"))
        if r["ok"]:
            for a, deg in ANG.items():
                b, n = pick(base, deg), pick(r, deg)
                row[f"rel_{a}"] = abs(n - b)/max(abs(b), 1e-300)
                dA[a] += W[(t, q)]*(n - b)
        rows.append(row)
    a_stage2 = json.load(open(os.path.join(HERE, "chl_sub45_eval.json")))["per_angle"]
    out = dict(nodes=rows, implied_delta_a={a: dict(abs=dA[a], rel=dA[a]/a_stage2[a]["fine"]) for a in ANG})
    json.dump(out, open(os.path.join(HERE, "chl_sub45_D3.json"), "w"), indent=1)
    print(json.dumps(out["implied_delta_a"], indent=1))
    print("failed:", sum(1 for r in rows if not r["ok"]), "of", len(rows))
    print("D3 DONE", flush=True)
