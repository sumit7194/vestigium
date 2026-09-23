"""
Taylor coefficients c2..c16 of s(x) about x = pi, for hypothesis R (registered in
PREREG_cuspis_sub45_check.md before this ran). Start series only: I(eps) is even,
so c_{2k} integrand = 8 pi a(1-a) H_{2k-1} / (2k). Same v3 node sets and weights
as chl_run_controls.py, both resolutions, checkpointed.
"""
import json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chl_run_controls as R
CKPT = os.path.join(HERE, "chl_coeffs_nodes.jsonl")
OUT = os.path.join(HERE, "chl_coeffs_run.json")
KMAX = 8
N = 26


def _work(tq):
    import mpmath as mpm
    sys.path.insert(0, HERE)
    import chl_mp as cm
    t, q = tq
    try:
        M = mpm.sqrt(mpm.mpf("0.25") + mpm.mpf(q)**2)
        dps = int(30 + 3*float(M))
        a = mpm.mpc("0.5", -mpm.mpf(t))
        F, info = cm.solve_series_btf(a, M, N, dps=dps)
        mpm.mp.dps = dps
        K = 8*mpm.pi*a*(1 - a)
        c = {f"c{2*k}": float((K*F["H"][2*k - 1]/(2*k)).real) for k in range(1, KMAX + 1)}
        return dict(t=t, q=q, ok=True, c=c, redundant=float(info["redundant_residual"]))
    except Exception as e:
        return dict(t=t, q=q, ok=False, error=f"{type(e).__name__}: {e}")


def main(workers=3):
    from multiprocessing import Pool
    done = {}
    if os.path.exists(CKPT):
        for line in open(CKPT):
            r = json.loads(line); done[R.key(r["t"], r["q"])] = r
    todo = []
    for res in R.RESOLUTIONS:
        for t, _, q, _ in R.nodes(res):
            if R.key(t, q) not in done and (t, q) not in todo:
                todo.append((t, q))
    print(f"{len(done)} done, {len(todo)} to run", flush=True)
    t0 = time.time()
    if todo:
        with Pool(workers) as pool, open(CKPT, "a") as fh:
            for i, r in enumerate(pool.imap_unordered(_work, todo), 1):
                fh.write(json.dumps(r) + "\n"); fh.flush()
                if i % 100 == 0 or not r["ok"]:
                    print(f"  {i}/{len(todo)} ({time.time()-t0:.0f}s)" + ("" if r["ok"] else f" FAILED {r['error']}"), flush=True)
    done = {}
    for line in open(CKPT):
        r = json.loads(line); done[R.key(r["t"], r["q"])] = r
    out = {}
    for res in R.RESOLUTIONS:
        acc = {f"c{2*k}": 0.0 for k in range(1, KMAX + 1)}
        missing = 0
        for t, wt, q, wq in R.nodes(res):
            r = done.get(R.key(t, q))
            if r is None or not r["ok"]:
                missing += 1; continue
            w = wt*wq*q*q/math.cosh(math.pi*t)**2
            for k in acc:
                acc[k] += w*r["c"][k]
        out[res] = dict(values=acc, missing=missing)
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
