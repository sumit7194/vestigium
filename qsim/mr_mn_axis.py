"""
MN on the symmetry axis: certified-monodromy (Ziglin-form) obstruction test, exactly as registered in
PREREG_mn_axis_certified_monodromy.md (ed09512 + 248b3bd). Gates G0 (integrator validation), G1 (omega on
the axis, exact), G2 (controls), G3 (target). Each gate is a guarded child; logs in qsim/.

Usage:  python mr_mn_axis.py G0|G1|G2|G3      |      python mr_mn_axis.py --one <task> out.json
"""
import cmath, json, math, os, sys, time
import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ia_hub as IA
from flint import acb, ctx

ctx.prec = 192
PKG = "/Users/sumit/Github/conjecture_machine/data/MN_for_quantum/"
MN_POINTS = {"p1": ("mn_metric_components_p1.txt", sp.Rational(1, 5)),
             "p2": ("mn_metric_components_p2.txt", sp.Rational(-1, 3))}
KERR_POINTS = {"p1": "mn_metric_components_KERR_p1.txt", "p2": "mn_metric_components_KERR_p2.txt"}
LEVELS = [(1, 4), (1, 9)]                        # (E, mu^2), L = 0 on the axis
z = sp.Symbol("z")


# ----------------------------------------------------------------------------------------------
# G0: validation on equations with known monodromy
# ----------------------------------------------------------------------------------------------
def riemann_P(lam, mu, nu, w):
    return ((lam**2 - 1)/(4*w**2) + (mu**2 - 1)/(4*(w - 1)**2) - (lam**2 + mu**2 - nu**2 - 1)/(4*w*(w - 1)))


def g0():
    R_ = sp.Rational
    lam, mu, nu = R_(1, 3), R_(1, 5), R_(1, 7)
    out = {}
    rP = IA.Compiled(riemann_P(lam, mu, nu, z), z)
    exp_tr = lambda l: -2*math.cos(math.pi*float(l))
    from flint import arb
    def contains(t, l):
        e = -2*(arb.pi()*arb(int(l.p))/int(l.q)).cos()
        return bool(t.real.contains(e) and t.imag.contains(arb(0)))
    for name, c, l in (("(a) around 0", 0, lam), ("(a) around 1", 1, mu)):
        Y = IA.transport(rP, IA.loop_points(0.5 + 0.5j, c, 0.25), dist=lambda q: min(abs(q), abs(q - 1)))
        t = IA.tr(Y)
        out[name] = dict(trace=str(t), expected=exp_tr(l), contains=contains(t, l), digits=IA.radius_digits(t),
                         det=str(IA.det(Y)))
    # (b) pullback by w = exp(2/x^3): coefficients in Q(x, E), essential singularity at 0
    x = z
    phi = sp.exp(2/x**3)
    lp = sp.diff(sp.log(sp.diff(phi, x)), x)            # phi''/phi' = -4/x - 6/x^4 (rational)
    lp = sp.simplify(lp)
    rb = sp.together(lp**2/4 - sp.diff(lp, x)/2) + sp.diff(phi, x)**2*riemann_P(lam, mu, nu, phi)
    rB = IA.Compiled(rb, x)
    x1 = complex(sp.N((-sp.I/sp.pi)**sp.Rational(1, 3), 30))       # principal root of x^3 = 2/(2 pi i)
    check = abs(cmath.exp(2/x1**3) - 1)
    Y = IA.transport(rB, IA.loop_points(x1 + 0.01, x1, 0.01, ngon=32), hmax=0.004)
    t = IA.tr(Y)
    out["(b) pullback, loop around E=1 root x1"] = dict(x1=str(x1), E_minus_1_at_x1=check, trace=str(t),
                                                         expected=exp_tr(mu), contains=contains(t, mu),
                                                         digits=IA.radius_digits(t), det=str(IA.det(Y)))
    ok = all(v["contains"] for v in out.values()) and all(v["digits"] >= 10 for v in out.values())
    out["G0_PASS"] = ok
    return out


# ----------------------------------------------------------------------------------------------
# metric loading and the axial / equatorial NVE
# ----------------------------------------------------------------------------------------------
def load(fname):
    C = {}
    for line in open(PKG + fname):
        if " = " in line and not line.startswith("#"):
            k, v = line.split(" = ", 1)
            C[k.strip()] = sp.parse_expr(v.strip())
    syms = {s.name: s for e in C.values() for s in e.free_symbols}
    return C, syms["x"], syms["y"]


def exp_to_E(expr, x, beta, E):
    """Replace every exp(arg) with E**m, where arg = m * 2 beta/x^3 for a rational m (checked)."""
    base = 2*beta/x**3
    def rep(e):
        m = sp.simplify(e.args[0]/base)
        if not m.is_Rational:
            raise ValueError(f"exp argument {e.args[0]} is not a rational multiple of 2 beta/x^3")
        return E**m
    return expr.replace(lambda e: isinstance(e, sp.exp), rep)


def g1_omega(point):
    fname, beta = MN_POINTS[point]
    C, x, y = load(fname)
    om = -C["g_tphi"]/C["g_tt"]
    E = sp.Symbol("E")
    res = {}
    for yv in (1, -1):
        e = om.subs(y, yv)
        e = exp_to_E(e, x, beta, E) if e.has(sp.exp) else e
        v = sp.cancel(sp.together(e))
        res[f"omega(y={yv})"] = str(v)
        res[f"zero(y={yv})"] = bool(v == 0)
    return res


def axial_nve(C, x, y, En, mu2):
    """Axial Gamma: y = cos theta, theta = 0, p_theta = 0, L = 0. Returns (r_xi2, r_xi1, xdot2) as
    expressions in x with exp() (no sqrt left: at y = 1, R = sqrt(x^2) = x for positive x).
    g^tt = -1/f + f omega^2/rho^2, rho^2 = g_tphi^2 - g_tt g_phiphi (vanishes at y = 1; omega(1) = 0 by G1):
      at y = 1:  g^tt -> -1/f,   d_y g^tt -> f_y/f^2 + f omega_y^2 / d_y(rho^2)."""
    gtt, gtp, gpp, gxx, gyy = (C[k] for k in ("g_tt", "g_tphi", "g_phiphi", "g_xx", "g_yy"))
    f = -gtt
    om = -gtp/gtt
    rho2 = gtp**2 - gtt*gpp
    at1 = lambda e: sp.sympify(e).subs(y, 1)
    f1, fy1 = at1(f), at1(sp.diff(f, y))
    omy1 = at1(sp.diff(om, y))
    rho2y1 = at1(sp.diff(rho2, y))
    Gtt1 = -1/f1
    Gtty1 = fy1/f1**2 + f1*omy1**2/rho2y1
    gxxinv = 1/gxx
    Gxx1, Gxxy1 = at1(gxxinv), at1(sp.diff(gxxinv, y))
    A = at1(1/(gyy*(1 - y**2)))                           # g^{theta theta} at theta = 0
    V1, Vy1 = Gtt1*En**2, Gtty1*En**2
    px2 = (-mu2 - V1)/Gxx1
    xdot2 = Gxx1*(-mu2 - V1)
    B = -(sp.Rational(1, 2)*px2*Gxxy1 + sp.Rational(1, 2)*Vy1)    # d^2H/dtheta^2 = -d_y H at y = 1
    return A, B, xdot2


def reduced_forms(A, B, xdot2, x):
    out = {}
    if sp.simplify(B) != 0:
        p2 = -(sp.diff(B, x)/B - sp.diff(xdot2, x)/(2*xdot2))
        out["r_xi2"] = p2**2/4 + sp.diff(p2, x)/2 - A*B/xdot2
    p1 = -(sp.diff(A, x)/A - sp.diff(xdot2, x)/(2*xdot2))
    out["r_xi1"] = p1**2/4 + sp.diff(p1, x)/2 - A*B/xdot2
    return out


def to_rational_in_E(expr, x, beta, E):
    """Exact simplification over Q(x, E), then E -> exp(2 beta/x^3) for evaluation. Returns (r_eval, r_QxE)."""
    e = exp_to_E(expr, x, beta, E) if expr.has(sp.exp) else expr
    e = sp.cancel(sp.together(e))
    num, den = sp.fraction(e)
    rE = sp.factor(num)/sp.factor(den)
    return rE.subs(E, sp.exp(2*beta/x**3)), e


# ----------------------------------------------------------------------------------------------
# singular points (float, only to CHOOSE loops) and the certificate search
# ----------------------------------------------------------------------------------------------
def locate_singular(r_eval, x, box_=6.0, rho0=0.35, grid=90):
    """Float estimates of poles of r: local maxima of |r| on a grid refined by Newton on 1/r.
    Only used to choose loops; rigour does not depend on them."""
    f = sp.lambdify(x, r_eval, "numpy")
    g = sp.lambdify(x, 1/sp.together(r_eval), "mpmath")
    import mpmath as mp
    xs = np.linspace(-box_, box_, grid)
    Z = xs[None, :] + 1j*xs[:, None]
    with np.errstate(all="ignore"):
        V = np.abs(f(Z))
    V[~np.isfinite(V)] = 1e300
    cands = []
    for i in range(1, grid - 1):
        for j in range(1, grid - 1):
            if V[i, j] > 10*np.median(V) and V[i, j] == V[i-1:i+2, j-1:j+2].max():
                cands.append(Z[i, j])
    found = []
    for c0 in cands:
        try:
            c = complex(mp.findroot(g, mp.mpc(c0), tol=1e-20, maxsteps=60))
        except Exception:
            continue
        if abs(c) >= rho0 and abs(c) <= box_ and all(abs(c - d) > 1e-6 for d in found):
            found.append(c)
    return sorted(found, key=lambda c: (round(c.real, 6), round(c.imag, 6)))


def certificate_search(r_eval, x, sing, stats, max_pairs=400, rho0=0.35):
    rc = IA.Compiled(r_eval, x)
    pts = [c for c in sing if abs(c) >= rho0]
    if len(pts) < 2:
        return dict(found=False, why=f"only {len(pts)} located singular points")
    dmin = lambda q: min([abs(q - c) for c in sing] + [abs(q)])
    sep = {c: min([abs(c - d) for d in sing if d != c] + [abs(c)]) for c in pts}
    # base point: best clearance among seeded candidates (loops need only be closed and certified)
    rng = np.random.default_rng(7)
    span = max(abs(c) for c in pts) + 1.0
    z0 = max((complex(rng.uniform(-span, span), rng.uniform(-span, span)) for _ in range(4000)), key=dmin)
    gens = {}
    for c in pts:
        rad = 0.3*sep[c]
        gens[c] = IA.transport(rc, IA.loop_points(z0, c, rad), dist=dmin, stats=stats)
    cand = [(f"g[{c:.4f}]", Y) for c, Y in gens.items()]
    keys = list(gens)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            cand.append((f"g[{keys[i]:.4f}]*g[{keys[j]:.4f}]", IA._matmul(gens[keys[i]], gens[keys[j]])))
    tried = 0
    for a in range(len(cand)):
        if not IA.certainly_not_in_segment(IA.tr(cand[a][1])):
            continue
        for b in range(a + 1, len(cand)):
            tried += 1
            ok, det_ = IA.certificate(cand[a][1], cand[b][1])
            if ok:
                return dict(found=True, g=cand[a][0], h=cand[b][0], base=str(z0), **det_, pairs_tried=tried,
                            n_generators=len(gens))
            if tried >= max_pairs:
                break
    traces = {k: str(IA.tr(Y)) for k, Y in cand[:len(gens)]}
    return dict(found=False, why="no certified pair in the registered candidate list", base=str(z0),
                generator_traces=traces, pairs_tried=tried, n_generators=len(gens))


# ----------------------------------------------------------------------------------------------
# tasks (each run as a guarded child)
# ----------------------------------------------------------------------------------------------
def _task_rows():
    rows = []
    rows.append(("G2", "ZV d=2 equatorial (1,0,4) [must FIND]", "zv_eq", True))
    for p in ("p1", "p2"):
        for En, mu2 in LEVELS:
            rows.append(("G2", f"Kerr {p} axial (E={En}, mu2={mu2}) [must NOT find]", ("kerr_ax", p, En, mu2), False))
    rows.append(("G2i", "ZV d=2 axial (1,0,4) [info]", "zv_ax", None))
    for p in ("p1", "p2"):
        for En, mu2 in LEVELS:
            rows.append(("G3", f"MN {p} axial (E={En}, mu2={mu2})", ("mn_ax", p, En, mu2), None))
    return rows


def run_task(spec):
    stats = {}
    t0 = time.time()
    x = sp.Symbol("x", positive=True)
    out = dict(spec=str(spec), forms={})
    if spec == "zv_eq":
        import mr_nve as N
        xs, ys = sp.symbols("x y")
        n = N.nve_equatorial(N.zipoy_voorhees(2, xs, ys), xs, ys, E=1, L=0, mu=2)
        forms = {k: n[k] for k in ("r_xi2", "r_xi1") if n[k] is not None}
        var = xs
        evals = {k: sp.cancel(v) for k, v in forms.items()}
    else:
        if spec == "zv_ax":
            import mr_ts2 as T2
            X, Y = T2.X, T2.Y
            inv = T2.zv2_wp(1)
            # lower components for the axial builder
            C = {"g_tt": -((X - 1)/(X + 1))**2, "g_tphi": sp.Integer(0),
                 "g_phiphi": (X**2 - 1)*(1 - Y**2)/((X - 1)/(X + 1))**2,
                 "g_xx": (X**2 - 1)**4/(X**2 - Y**2)**4*(X**2 - Y**2)/((X**2 - 1)*((X - 1)/(X + 1))**2),
                 "g_yy": (X**2 - 1)**4/(X**2 - Y**2)**4*(X**2 - Y**2)/((1 - Y**2)*((X - 1)/(X + 1))**2)}
            xx, yy, beta, En, mu2 = X, Y, None, 1, 4
        elif spec[0] == "kerr_ax":
            _, p, En, mu2 = spec
            C, xx, yy = load(KERR_POINTS[p]); beta = None
        else:
            _, p, En, mu2 = spec
            fname, beta = MN_POINTS[p]
            C, xx, yy = load(fname)
        A, B, xdot2 = axial_nve(C, xx, yy, En, mu2)
        forms = reduced_forms(A, B, xdot2, xx)
        Esym = sp.Symbol("E")
        evals = {}
        for k, v in forms.items():
            if beta is None:
                evals[k] = sp.factor(sp.cancel(sp.together(v)))
            else:
                ev, qxe = to_rational_in_E(v, xx, beta, Esym)
                evals[k] = ev
                out.setdefault("QxE_size", {})[k] = len(str(qxe))
        var = xx
        out["degenerate_xi2"] = "r_xi2" not in forms
    print(f"[{time.time()-t0:.1f}s] NVE built: forms {list(evals)}", flush=True)
    for k, rv in evals.items():
        sing = locate_singular(rv, var)
        print(f"[{time.time()-t0:.1f}s] {k}: {len(sing)} located singular points", flush=True)
        try:
            res = certificate_search(rv, var, sing, stats)
        except Exception as e:
            res = dict(found=False, why=f"{type(e).__name__}: {e}")
        res["located"] = [str(complex(round(c.real, 5), round(c.imag, 5))) for c in sing]
        out["forms"][k] = res
        print(f"[{time.time()-t0:.1f}s] {k}: certificate found = {res['found']}  {res.get('why', '')}", flush=True)
    out["steps"] = stats.get("steps", 0)
    out["seconds"] = round(time.time() - t0, 1)
    return out


def run_gate(gate):
    import mr_watchdog as W
    py = sys.executable
    if gate in ("G0", "G1"):
        outp = os.path.join(HERE, f"mr_mn_{gate}.json")
        g = W.run_guarded([py, "-u", os.path.abspath(__file__), "--one", gate, outp], mem_limit_mb=2048,
                          time_limit_s=1800, cwd=HERE, log=os.path.join(HERE, f"mr_mn_{gate}.log"))
        res = json.load(open(outp)) if g["status"] == "ok" and os.path.exists(outp) else dict(failed=g["status"])
        res["guard"] = g
        print(json.dumps(res, indent=1, default=str))
        return res
    rows = [r for r in _task_rows() if r[0].startswith(gate)]
    allrows = _task_rows()
    results = []
    for tag, name, spec, expect in rows:
        i = allrows.index((tag, name, spec, expect))
        outp = os.path.join(HERE, f"mr_mn_row_{i}.json")
        g = W.run_guarded([py, "-u", os.path.abspath(__file__), "--one", f"row{i}", outp], mem_limit_mb=2048,
                          time_limit_s=1800, cwd=HERE, log=os.path.join(HERE, f"mr_mn_row_{i}.log"))
        res = json.load(open(outp)) if g["status"] == "ok" and os.path.exists(outp) else dict(forms={}, failed=g["status"])
        found = any(f.get("found") for f in res.get("forms", {}).values())
        if expect is True:
            verdict = "PASS" if found else "FAIL (certificate not found)"
        elif expect is False:
            verdict = "FAIL (certificate FOUND on an integrable control)" if found else ("PASS" if res.get("forms") else "FAIL (did not run)")
        else:
            verdict = ("OBSTRUCTION (certificate)" if found else "INCONCLUSIVE") if tag == "G3" else ("INFO: found" if found else "INFO: not found")
        res.update(tag=tag, name=name, assessment=verdict, guard=g)
        results.append(res)
        print(f"{i:>2} {tag:<4} {name:<44} => {verdict:<30} "
              f"{ {k: v.get('found') for k, v in res.get('forms', {}).items()} } [guard {g['status']}, "
              f"peak {g['peak_mb']} MB, {g['seconds']} s]", flush=True)
        json.dump(results, open(os.path.join(HERE, f"mr_mn_{gate}_run.json"), "w"), indent=1, default=str)
        if expect is not None and verdict != "PASS":
            print("CONTROL MISBEHAVED: stopping, per the registration", flush=True)
            break
    return results


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--one":
        task, outp = sys.argv[2], sys.argv[3]
        if task == "G0":
            res = g0()
        elif task == "G1":
            res = {p: g1_omega(p) for p in MN_POINTS}
            res["G1_PASS"] = all(v["zero(y=1)"] for k, v in res.items() if isinstance(v, dict))
        else:
            res = run_task(_task_rows()[int(task[3:])][2])
        json.dump(res, open(outp, "w"), indent=1, default=str)
    else:
        run_gate(sys.argv[1])
