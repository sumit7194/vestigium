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
CKPT = os.path.join(HERE, "chl_controls_nodes_v3.jsonl")
T_MAX = 4.0
XS = [3*math.pi/4, math.pi/2]
# v3 quadrature (2026-09-23). History: v1 plain product GL failed its gate at
# 1e-5 (diagonal ridge); v2 two-panel GL failed at 1e-7..1.7e-5. A single-t test
# with nested Clenshaw-Curtis localised the v2 fault to the exponential TAIL panel
# (8 points there cost 3e-6..5e-5; the plateau and core were fine).
#  q, per t: three NESTED Clenshaw-Curtis panels, plateau [0,t-1.5], core
#     [t-1.5,t+1.5], tail [t+1.5,t+7.5]; coarse (8,16,16) is a subset of fine
#     (16,32,32), so the convergence check costs no extra nodes.
#  t: Gauss-Legendre in s with t = sinh(s): moves the sech^2 poles at t = i/2 to
#     distance pi/2 (rho ~ 2.5); coarse n_s = 16, fine n_s = 22 (not nested; 12 measured at 2.7e-6 on t^3 sech^2).
S_TAIL, RIDGE_HALF = 7.5, 1.5
CC_COARSE, CC_FINE = (8, 16, 16), (16, 32, 32)
NS = {"coarse": 16, "fine": 22}
RESOLUTIONS = ["coarse", "fine"]


def cc(n, lo, hi):
    k = np.arange(n + 1); x = np.cos(np.pi*k/n)
    w = np.zeros(n + 1)
    for j in range(n + 1):
        ssum = sum((1.0 if m == n//2 else 2.0)*math.cos(2*m*j*math.pi/n)/(4*m*m - 1)
                   for m in range(1, n//2 + 1))
        w[j] = (1.0 if j in (0, n) else 2.0)/n*(1 - ssum)
    return 0.5*(hi - lo)*(x + 1) + lo, 0.5*(hi - lo)*w


def q_rule(t, levels):
    split = t - RIDGE_HALF
    panels = [(0.0, split), (split, t + RIDGE_HALF), (t + RIDGE_HALF, t + S_TAIL)]
    if split <= 0.05:                     # no plateau panel yet: core starts at 0
        panels = [(0.0, t + RIDGE_HALF), (t + RIDGE_HALF, t + S_TAIL)]
        levels = levels[1:]
    out = {}
    for (lo, hi), n in zip(panels, levels):
        qn, qw = cc(n, lo, hi)
        for q, w in zip(qn, qw):
            k = round(float(q), 13)
            out[k] = out.get(k, 0.0) + float(w)
    return out


def t_rule(ns):
    s_max = math.asinh(T_MAX)
    x, w = np.polynomial.legendre.leggauss(ns)
    s = 0.5*s_max*(x + 1); ws = 0.5*s_max*w
    return [(float(math.sinh(si)), float(wi*math.cosh(si))) for si, wi in zip(s, ws)]


def nodes(res):
    lev = CC_COARSE if res == "coarse" else CC_FINE
    out = []
    for t, wt in t_rule(NS[res]):
        for q, wq in q_rule(t, lev).items():
            if q > 1e-14:                 # the q^2 factor makes q = 0 contribute nothing
                out.append((t, wt, q, wq))
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
    grid = nodes(res)
    acc = {f"{x:.12f}": 0.0 for x in XS}
    acc.update(c2=0.0, c4=0.0, c6=0.0)
    last_t = {f"{x:.12f}": 0.0 for x in XS}
    missing = []
    tmax_node = max(t for t, _, _, _ in grid)
    for t, wt, q, wq in grid:
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
        for t, _, q, _ in nodes(res):
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
    summary = dict(T_MAX=T_MAX, S_TAIL=S_TAIL, RIDGE_HALF=RIDGE_HALF, CC=[CC_COARSE, CC_FINE], NS=NS, xs=XS, resolutions={})
    for res in RESOLUTIONS:
        acc, tail, missing = integrate(res, done)
        summary["resolutions"][res] = dict(values=acc, t_tail_bound=tail,
                                                           missing=missing)
    with open(OUT, "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary["resolutions"], indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
