"""
Stage-1 production run: the known-answer controls that need NO small angle.

  s(3pi/4), s(pi/2)          -- control 1 (90 deg), plus 135 deg
  c2, c4, c6 at x = pi        -- smooth end: sigma = 1/256 exact, c4 exact, c6
The sub-45 region is NOT computed here. Per the pre-registration it is touched
only after these pass.

  s(x) = int_0^3 dt sech^2(pi t) int_0^8 dq q^2 Re trG(x, sqrt(1/4+q^2), 1/2 - it)

Two Gauss-Legendre resolutions, so convergence is SHOWN. Every node is appended
to a checkpoint file as it finishes, and a restart skips completed nodes.
Run with the repo's sims/.venv (mpmath). Workers default to 3 on a shared box.
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CKPT = os.path.join(HERE, "chl_controls_nodes.jsonl")
OUT = os.path.join(HERE, "chl_controls_run.json")
CKPT = os.path.join(HERE, "chl_controls_nodes_v2.jsonl")
T_MAX = 4.0
XS = [3*math.pi/4, math.pi/2]
# Ridge-adapted quadrature (diagnosed 2026-09-23 after the first stage-1 pass
# failed its own convergence gate, 1-7e-5 between resolutions):
#  - every integrand has a PLATEAU for q < t (tr G -> -2 ln sin(x/2) exactly;
#    c2-integrand -> 1/4), a sigmoid step at q ~ t, and decay ~ e^{-2x(q-t)}.
#  - so q runs over [0, t + S] with S = 7.5 (90 deg: e^{-pi*7.5} ~ 6e-11), in two
#    panels: plateau [0, t-1.5] and ridge+tail [t-1.5, t+S].
#  - t runs to 4 (tail ~ t^3 e^{-2 pi t}: ~1e-8 relative; bounded below).
S_TAIL, RIDGE_HALF = 7.5, 1.5
RESOLUTIONS = [(16, 8, 20), (22, 12, 30)]      # (n_t, n_plateau, n_ridge)


def _gl(n, lo, hi):
    x, w = np.polynomial.legendre.leggauss(n)
    return 0.5*(hi - lo)*(x + 1) + lo, 0.5*(hi - lo)*w


def nodes(nt, n1, n2):
    out = []
    tn, tw = _gl(nt, 0.0, T_MAX)
    for t, wt in zip(tn, tw):
        split = max(0.0, t - RIDGE_HALF)
        panels = [(n2, split, t + S_TAIL)]
        if split > 0.05:
            panels.insert(0, (n1, 0.0, split))
        for n, lo, hi in panels:
            qn, qw = _gl(n, lo, hi)
            out += [(float(t), float(wt), float(q), float(wq)) for q, wq in zip(qn, qw)]
    return out


def key(t, q):
    return f"{t:.15f}|{q:.15f}"


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
                done[key(r["t"], r["q"])] = r
    return done


def integrate(res, done):
    nt, nq = res
    acc = {f"{x:.12f}": 0.0 for x in XS}
    acc.update(c2=0.0, c4=0.0, c6=0.0)
    last_t = {f"{x:.12f}": 0.0 for x in XS}
    missing = []
    tmax_node = max(t for t, _, _, _ in nodes(nt, nq))
    for t, wt, q, wq in nodes(nt, nq):
        r = done.get(key(t, q))
        if r is None or not r["ok"]:
            missing.append((t, q, None if r is None else r.get("error")))
            continue
        w = wt*wq*q*q/math.cosh(math.pi*t)**2
        for x in XS:
            xv = [k for k in r["trG"] if abs(float(k) - x) < 1e-9][0]
            acc[f"{x:.12f}"] += w*r["trG"][xv][0]
            if abs(t - tmax_node) < 1e-12:
                last_t[f"{x:.12f}"] += wq*q*q*r["trG"][xv][0]
        for c in ("c2", "c4", "c6"):
            acc[c] += w*r["smooth"][c][0]
    # t-tail bound beyond T_MAX: integrand <= sech^2(pi t) * (q-integral at the last t node)
    tail = {k: v*(1 - math.tanh(math.pi*T_MAX))/math.pi for k, v in last_t.items()}
    return acc, tail, missing


def main(workers=3):
    from multiprocessing import Pool
    done = load_done()
    todo = []
    for res in RESOLUTIONS:
        for t, _, q, _ in nodes(*res):
            if key(t, q) not in done and (t, q) not in todo:
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
    summary = dict(T_MAX=T_MAX, S_TAIL=S_TAIL, RIDGE_HALF=RIDGE_HALF, xs=XS, resolutions={})
    for res in RESOLUTIONS:
        acc, tail, missing = integrate(res, done)
        summary["resolutions"]["x".join(map(str, res))] = dict(values=acc, t_tail_bound=tail,
                                                           missing=missing)
    with open(OUT, "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary["resolutions"], indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
