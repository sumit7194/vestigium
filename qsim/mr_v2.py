"""
iahub v2 driver (PREREG_iahub_v2.md, registered 33321aa): certified monodromy of the NON-reduced xi1 system
    Y' = [[0, 1], [-q, -p]] Y,   p = -(A'/A - X'/(2X)),  q = A B / X
built from the SAME exact field code as v1 (axial: Q(x,E), mr_mn_axis.QxE; equatorial: Q(t,E1..E3),
mr_mn_equatorial.QtE), compiled to straight-line programs, transported by the Rust/Arb core in parallel.

Search policy (A5, frozen): nearest-first generators, incremental testing of generators and pairwise products,
first certified pair. Certificate: scale-free GL(2) form (ia_native.certificate_gl2).
Two-implementation rule: a v2 certificate counts only after replay_v1() reproduces it with the frozen v1 hub on
the REDUCED form (different equation, different code), using the SL(2) certificate there.
"""
import json, os, sys, time
import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ia_native as IN
import ia_hub as IA
import mr_mn_axis as MA
import mr_mn_equatorial as ME


# ----------------------------------------------------------------------------------------------
# building the first-order system from the exact fields
# ----------------------------------------------------------------------------------------------
def _pq(A, B, X):
    p = -(A.D()/A - X.D()/(X*2))
    q = A*B/X
    return p, q


def system_equatorial(kind, pt, En, L, mu2):
    G, (A, B, X), cd, src = ME.build(kind, pt, En, L, mu2)
    p, q = _pq(A, B, X)
    gens = ME.QtE.GENS
    def eregs(b, t):
        regs = []
        for g in cd["gens"]:
            gn, gd = sp.fraction(sp.cancel(g))
            n = b.poly_t([sp.Rational(c) for c in sp.Poly(gn, ME.T_).all_coeffs()], t)
            d = b.poly_t([sp.Rational(c) for c in sp.Poly(gd, ME.T_).all_coeffs()], t)
            regs.append(b.exp(b.mul(n, b.inv(d))))
        return regs
    bad = ME.BAD if cd["gens"] else []
    return dict(p=p, q=q, gens=gens, eregs=eregs, var=ME.T_, bad=bad, kind="equatorial",
                to_expr=lambda e, part: e.to_expr(part), reduced=lambda: ME.form_t(A, B, X, "r_xi1"),
                skip_near=ME.BAD, skip=ME.BAD_SKIP)


def system_axial(kind, pt, En, mu2):
    if kind == "mn":
        fname, beta = MA.MN_POINTS[pt]
        C, x, y = MA.load(fname)
    elif kind == "kerr":
        C, x, y = MA.load(MA.KERR_POINTS[pt]); beta = 0
    else:                                                   # ZV delta=2 (same lower components as v1)
        C, x, y, beta = ME.source("zv")
    A, B, X = MA.axial_nve(C, x, y, En, mu2)
    Es = sp.Symbol("E")
    Aq, Bq, Xq = (MA.QxE.from_expr(e, x, Es, beta) for e in (A, B, X))
    p, q = _pq(Aq, Bq, Xq)
    gens = (x, Es)
    def eregs(b, t):
        if not beta:
            return []
        return [b.exp(b.mul(b.const(2*sp.Rational(beta)), b.inv(b.powi(t, 3))))]
    def to_expr(e, part):
        poly = e.P if part == "P" else e.Q
        ex = poly.as_expr()
        return ex.subs(Es, sp.exp(2*beta/x**3)) if beta else ex
    def reduced():
        F = MA.reduced_forms_QxE(Aq, Bq, Xq)
        return F["r_xi1"]
    return dict(p=p, q=q, gens=gens, eregs=eregs, var=x, bad=[0] if beta else [], kind="axial",
                to_expr=to_expr, reduced=reduced, skip_near=[0] if beta else [], skip=0.35)


def compile_system(S):
    b = IN.SLPBuilder()
    t = b.var()
    E = S["eregs"](b, t)
    def reg(poly):
        return b.poly_tE(poly, S["gens"], E, t)
    mq, mp = -S["q"], -S["p"]
    zero, one = b.const(0), b.const(1)
    entries = [[(zero, one), (one, one)], [(reg(mq.P), reg(mq.Q)), (reg(mp.P), reg(mp.Q))]]
    return b, entries


# ----------------------------------------------------------------------------------------------
# singular points (float; loop choice only) -- zeros of the denominators of p and q
# ----------------------------------------------------------------------------------------------
def locate(S, box_=6.0, grid=120):
    import mpmath as mp
    v = S["var"]
    found = []
    for e in (S["p"], S["q"]):
        den = S["to_expr"](e, "Q")
        f = sp.lambdify(v, den, "numpy")
        g = sp.lambdify(v, den, "mpmath")
        xs = np.linspace(-box_, box_, grid)
        Z = xs[None, :] + 1j*xs[:, None] + 1e-3*(1 + 1j)
        with np.errstate(all="ignore"):
            V = np.abs(f(Z))
        V[~np.isfinite(V)] = np.inf
        cands = [Z[i, j] for i in range(1, grid - 1) for j in range(1, grid - 1)
                 if np.isfinite(V[i, j]) and V[i, j] == V[i-1:i+2, j-1:j+2].min()]
        for c0 in cands:
            try:
                c = complex(mp.findroot(g, mp.mpc(c0), tol=1e-25, maxsteps=80))
            except Exception:
                continue
            if abs(c) <= box_ and all(abs(c - d) > 1e-6 for d in found) and \
                    all(abs(c - bp) >= S["skip"] for bp in S["skip_near"]):
                found.append(c)
    return sorted(found, key=lambda c: (round(c.real, 6), round(c.imag, 6)))


def locate_a6(S, box_=6.0, grid=480):
    """A6 (post-failure, bridge-approved): complete float locator -- 4x finer grid, Newton on the denominators of
    p and q, closure under complex conjugation (valid: real coefficients), and t -> 1/t images tried ONLY as
    Newton-verified candidates (not a symmetry: R(1/t) = -R(t) on the rational branch). Dedupe at 1e-8."""
    import mpmath as mp
    v = S["var"]
    dens = [S["to_expr"](e, "Q") for e in (S["p"], S["q"])]
    fs = [sp.lambdify(v, d, "numpy") for d in dens]
    gs = [sp.lambdify(v, d, "mpmath") for d in dens]
    found = []
    def add(c):
        if abs(c) <= box_ and all(abs(c - d) > 1e-8 for d in found) and \
                all(abs(c - bp) >= S["skip"] for bp in S["skip_near"]):
            found.append(c)
    def newton(g, c0):
        """findroot raises unless it converges to tol; a converged root is returned, else None."""
        try:
            return complex(mp.findroot(g, mp.mpc(c0), tol=1e-25, maxsteps=80))
        except Exception:
            return None
    xs = np.linspace(-box_, box_, grid)
    Z = xs[None, :] + 1j*xs[:, None] + 1e-4*(1 + 1j)
    for f, g in zip(fs, gs):
        with np.errstate(all="ignore"):
            V = np.abs(f(Z))
        V[~np.isfinite(V)] = np.inf
        for i in range(1, grid - 1):
            for j in range(1, grid - 1):
                if np.isfinite(V[i, j]) and V[i, j] == V[i-1:i+2, j-1:j+2].min():
                    c = newton(g, Z[i, j])
                    if c is not None:
                        add(c)
    # closure: conjugates (verified), and 1/t images as candidates (verified; many rejected)
    for c in list(found):
        for cand in (c.conjugate(), 1/c if c != 0 else None):
            if cand is None:
                continue
            for g in gs:
                r = newton(g, cand)
                if r is not None and abs(r - cand) < 1e-6:
                    add(r)
                    break
    return sorted(found, key=lambda c: (round(c.real, 6), round(c.imag, 6)))


# ----------------------------------------------------------------------------------------------
# incremental certificate search (A5 policy), loops transported in parallel batches
# ----------------------------------------------------------------------------------------------
def search(S, sing, threads=3, log=print, max_gen=40, skip_failed=False):   # 2026-10-04: 6 -> 3 (bridge CPU budget, <= 5 threads total); resource only, same search order
    b, entries = compile_system(S)
    obst = list(sing) + [complex(c) for c in S["bad"]]
    if len(sing) < 2:
        return dict(found=False, why=f"only {len(sing)} located singular points")
    dmin = lambda q: min(abs(q - c) for c in obst)
    sep = {c: min(abs(c - d) for d in obst if d != c) for c in sing}
    rng = np.random.default_rng(7)
    span = max(abs(c) for c in sing) + 1.0
    z0 = max((complex(rng.uniform(-span, span), rng.uniform(-span, span)) for _ in range(4000)), key=dmin)
    pts = sorted(sing, key=lambda c: abs(c - z0))[:max_gen]
    gens, cand, tried, steps = [], [], 0, 0
    geo = {}
    skipped = []
    for k0 in range(0, len(pts), threads):
        batch = pts[k0:k0 + threads]
        loops = []
        for c in batch:
            rad = 0.3*sep[c]
            name = f"g[{c.real:.6f}{c.imag:+.6f}j,r{rad:.5f}]"
            geo[name] = dict(center=[c.real, c.imag], radius=rad, base=[z0.real, z0.imag])
            loops.append((name, IA.loop_points(z0, c, rad)))
        job = IN.write_job(b, entries, loops, bad=S["bad"], obst=obst, threads=threads)
        t0 = time.time()
        res = IN.run_job(job)
        os.remove(job)
        for name, _ in loops:
            r = res[name]
            if not r["status"].startswith("ok"):
                if skip_failed:                       # A6 (b): skip, do not abort -- only removes candidates
                    skipped.append(dict(loop=name, status=r["status"]))
                    log(f"  skipped {name}: {r['status']}")
                    continue
                return dict(found=False, why=f"transport failed on {name}: {r['status']}", base=str(z0))
            steps += r["steps"]
            Y = r["M"]
            new = [(name, Y)] + [(f"{gn}*{name}", IN.matmul(GY, Y)) for gn, GY in gens]
            gens.append((name, Y))
            for nn, NY in new:
                for on, OY in cand:
                    tried += 1
                    ok, info = IN.certificate_gl2(OY, NY)
                    if ok:
                        return dict(found=True, g=on, h=nn, base=str(z0), **info, pairs_tried=tried,
                                    n_generators=len(gens), steps=steps, geometry=geo, skipped=skipped)
                cand.append((nn, NY))
        log(f"  batch {k0//threads + 1}: {len(gens)} generators, {tried} pairs, {steps} steps, {time.time()-t0:.1f}s")
    return dict(found=False, why="no certified pair in the registered candidate list", base=str(z0), skipped=skipped,
                generator_w={gn: str(IN.tr(GY)**2/IN.det(GY)) for gn, GY in gens}, pairs_tried=tried,
                n_generators=len(gens), steps=steps, geometry=geo)


# ----------------------------------------------------------------------------------------------
# two-implementation rule: replay a v2 certificate with the frozen v1 hub on the REDUCED form
# ----------------------------------------------------------------------------------------------
_RCTX = {}


def _ser_ball(x):
    """Exact, outward-rounded serialisation of an acb ball (mid as mantissa/exponent; radius rounded up)."""
    from flint import arb
    def one(a):
        m, e = a.mid().man_exp(); rm, re_ = a.rad().man_exp()
        return (int(m), int(e), int(rm), int(re_))
    return (one(x.real), one(x.imag))


def _de_ball(t):
    from flint import arb, acb
    def one(u):
        m, e, rm, re_ = u
        return arb(arb(m)*arb(2)**e, arb(rm)*arb(2)**re_)     # contains the original ball (outward rounding)
    return acb(one(t[0]), one(t[1]))


def _replay_worker(name):
    rc, dmin, geo = _RCTX["rc"], _RCTX["dmin"], _RCTX["geo"]
    gm = geo[name]
    Y = IA.transport(rc, IA.loop_points(complex(*gm["base"]), complex(*gm["center"]), gm["radius"]), dist=dmin)
    return name, [[_ser_ball(Y[i][j]) for j in range(2)] for i in range(2)]


def replay_v1(S, cert, sing, procs=3):
    """Recompute the certifying loops with ia_hub (v1, reduced form r = P/Q, SL(2) certificate).
    2026-10-04: the 2-4 certifying loops run in parallel forked processes (resource only; identical computation),
    results returned by exact outward-rounded ball serialisation."""
    import multiprocessing as mpr
    r1 = S["reduced"]()
    rc = IA.RationalFn(S["to_expr"](r1, "P"), S["to_expr"](r1, "Q"), S["var"], S["bad"])
    obst = list(sing) + [complex(c) for c in S["bad"]]
    dmin = lambda q: min(abs(q - c) for c in obst)
    geo = cert["geometry"]
    names = sorted(set(cert["g"].split("*") + cert["h"].split("*")))
    _RCTX.update(rc=rc, dmin=dmin, geo=geo)
    with mpr.get_context("fork").Pool(processes=min(procs, len(names))) as pool:
        got = dict(pool.map(_replay_worker, names))
    cache = {n: [[_de_ball(got[n][i][j]) for j in range(2)] for i in range(2)] for n in names}
    def elem(expr):
        parts = expr.split("*")
        Y = cache[parts[0]]
        for p_ in parts[1:]:
            Y = IA._matmul(Y, cache[p_])
        return Y
    g, h = elem(cert["g"]), elem(cert["h"])
    ok, info = IA.certificate(g, h)
    c = IA.tr(IA._matmul(IA._matmul(g, h), IA._matmul(IA.inv(g), IA.inv(h))))
    return dict(replayed=ok, **info, tr_g_midrad=IN.midrad(IA.tr(g)), tr_h_midrad=IN.midrad(IA.tr(h)),
                tr_comm_midrad=IN.midrad(c), loops_replayed=names)
