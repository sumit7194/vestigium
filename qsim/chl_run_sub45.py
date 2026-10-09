"""
Stage-2 sub-45 run (PREREG_cuspis_sub45_check.md, STAGE 2 ADDENDUM, db54aa0). Instrument UNCHANGED from Stage 1 v3:
the quadrature rules, resolutions, node solver, dps = 30 + 3M and T_MAX are all imported from chl_run_controls.
Only the angle list differs: cuspis's reported scalar angles (literal decimals, math.radians), the arctan(1/2)
HHCWM16 anchor, 45 deg (join) and 90 deg (consistency with Stage 1). Per-node checkpoint; restart skips completed nodes.
Run with the repo's sims/.venv.   python chl_run_sub45.py [workers]
"""
import json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chl_run_controls as R          # frozen Stage-1 v3 rules: nodes(), key(), T_MAX, CC, NS, RESOLUTIONS

ANGLES_DEG = {"15": 15.0, "20": 20.0, "26.565": 26.565, "30": 30.0, "40": 40.0, "45": 45.0, "90": 90.0}
XS = sorted([math.radians(v) for v in ANGLES_DEG.values()] + [math.atan(0.5)], reverse=True)
CKPT = os.path.join(HERE, "chl_sub45_nodes.jsonl")
OUT = os.path.join(HERE, "chl_sub45_run.json")


def _init():
    sys.path.insert(0, HERE)


def _work(tq):
    import chl_node as nd
    t, q = tq
    try:
        r = nd.compute_node(t, q, XS)
        r["ok"] = True
    except Exception as e:                      # recorded, never silently dropped
        r = dict(t=t, q=q, ok=False, error=f"{type(e).__name__}: {e}")
    return r


def load_done():
    done = {}
    if os.path.exists(CKPT):
        with open(CKPT) as fh:
            for line in fh:
                r = json.loads(line)
                done[R.key(r["t"], r["q"])] = r
    return done


def integrate(res, done):
    """Same quadrature sum as chl_run_controls.integrate, over this stage's XS."""
    grid = R.nodes(res)
    acc = {f"{x:.12f}": 0.0 for x in XS}
    last_t = {f"{x:.12f}": 0.0 for x in XS}
    missing = []
    tmax_node = max(t for t, _, _, _ in grid)
    for t, wt, q, wq in grid:
        r = done.get(R.key(t, q))
        if r is None or not r["ok"]:
            missing.append((t, q, None if r is None else r.get("error")))
            continue
        w = wt*wq*q*q/math.cosh(math.pi*t)**2
        for x in XS:
            xv = [k for k in r["trG"] if abs(float(k) - x) < 1e-9][0]
            acc[f"{x:.12f}"] += w*r["trG"][xv][0]
            if abs(t - tmax_node) < 1e-12:
                last_t[f"{x:.12f}"] += wq*q*q*r["trG"][xv][0]
    tail = {k: v*(1 - math.tanh(math.pi*R.T_MAX))/math.pi for k, v in last_t.items()}
    return acc, tail, missing


def main(workers=3):
    from multiprocessing import Pool
    done = load_done()
    todo = []
    for res in R.RESOLUTIONS:
        for t, _, q, _ in R.nodes(res):
            if R.key(t, q) not in done and (t, q) not in todo:
                todo.append((t, q))
    print(f"{len(done)} nodes done, {len(todo)} to run, {workers} workers", flush=True)
    t0 = time.time()
    if todo:
        with Pool(workers, initializer=_init) as pool, open(CKPT, "a") as fh:
            for i, r in enumerate(pool.imap_unordered(_work, todo), 1):
                fh.write(json.dumps(r) + "\n"); fh.flush()
                if i % 20 == 0 or not r["ok"]:
                    print(f"  {i}/{len(todo)}  ({time.time()-t0:.0f}s)"
                          + ("" if r["ok"] else f"  FAILED t={r['t']:.3f} q={r['q']:.3f}: {r['error']}"), flush=True)
    done = load_done()
    summary = dict(stage="sub45 stage 2", angles_deg=ANGLES_DEG, xs=XS, T_MAX=R.T_MAX, CC=[R.CC_COARSE, R.CC_FINE],
                   NS=R.NS, resolutions={})
    for res in R.RESOLUTIONS:
        acc, tail, missing = integrate(res, done)
        summary["resolutions"][res] = dict(values=acc, t_tail_bound=tail, missing=missing)
    with open(OUT, "w") as fh:
        json.dump(summary, fh, indent=1)
    print("RUN DONE", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
