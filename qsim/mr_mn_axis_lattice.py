"""
Certified monodromy on the MN symmetry-axis lattice near x = 0: PREREG_mn_axis_lattice_certified.md (61b84a3 + bacb91a),
with Amendment A1 (10fb580): Newton in sigma for the locator (A1.1); transport in u = (x - x_c)/eps (A1.2).
Claude Opus 5.5 (Quantum-personal), testing Claude Fable 5.2's design (fable_work/mn_general_theorem/DESIGN.md).

Reuses ia_hub.py (Arb ball transport, certificate) and mr_mn_axis.py (metric package, exact axial NVE in Q(x, E))
UNCHANGED. Floats are used only to place loops; every reported trace is a certified Arb ball, and the set of lattice
points inside every loop is certified by an argument-principle count (gate Q2).

Usage:  python mr_mn_axis_lattice.py --task <name> <out.json>     (one guarded child per task)
        python mr_mn_axis_lattice.py --phase 1|2                    (runs the phase's tasks under mr_watchdog)
Tasks:  Q1_S1 Q1_S2 Q1_R1 Q1_R2 | Q3_<j> | Q4_<j> | S1_<j> S2_<j> R1_<j> R2_<j> | C0
"""
import cmath, json, math, os, sys, time
import numpy as np
import sympy as sp
import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ia_hub as IA
import mr_mn_axis as AX                       # sets ctx.prec = 192 (as 2ce8b41)
from flint import acb, arb, ctx

OUTDIR = os.path.join(HERE, "mn_lattice")
R_ = sp.Rational
ROWS = {
    "S1": dict(kind="static", beta=R_(1, 5), En=1, mu2=4),
    "S2": dict(kind="static", beta=R_(-1, 3), En=1, mu2=9),
    "R1": dict(kind="mn", point="p1", beta=R_(1, 5), M=5, a=3, k=4, En=1, mu2=9),
    "R2": dict(kind="mn", point="p1", beta=R_(1, 5), M=5, a=3, k=4, En=1, mu2=4),
}
JS = (10, 100, 1000)
T_LIMIT = -(4 + 2*mp.cosh(mp.pi*mp.sqrt(3)))          # [B2] signed prediction, normal form y'' = r y
TL_ARB = lambda: -(4 + 2*(arb.pi()*arb(3).sqrt()).cosh())    # the same, as an Arb ball
VAC = 1e-10                                            # [B1] vacuity guard on ball radius
SCOPE = ("A T-L6 PASS at a row is a pointwise certified obstruction there. Like 2ce8b41, it covers that row only, "
         "the L = 0 sector, and meromorphic integrals near the complexified axis orbit, here including complex x "
         "near 0. The S-row T-limit checks the static model's limit, not the general theorem.")
mp.mp.dps = 50


# ---------------------------------------------------------------------------------------------- the axis P
def P_parts(row, x, W):
    """P = E^2 - mu^2 f0(x, 1) = N/D with N, D polynomials in (x, W), W = exp(2 beta/x^3).
    static (alpha = 0): f0 = W (x-1)/(x+1);  MN p1: f0 = W (r^2 - 2Mr + a^2)/(r^2 + a^2 W^2), r = kx + M (Lemma 3,
    confirmed by V21 C1; used here only through gate Q1, which checks it against the package exactly)."""
    p = ROWS[row]; En, mu2 = p["En"], p["mu2"]
    if p["kind"] == "static":
        return En**2*(x + 1) - mu2*W*(x - 1), (x + 1)
    M, a, k = p["M"], p["a"], p["k"]
    r = k*x + M
    return En**2*(r**2 + a**2*W**2) - mu2*W*(r**2 - 2*M*r + a**2), (r**2 + a**2*W**2)


def static_components(beta, x, y):
    """The alpha = 0 member of the MN family in the package's form (_mn_build.py with alpha = 0, k = 1):
    f = e^{2 psi} (x-1)/(x+1), omega = 0, e^{2 gamma} = E_Q E_A/E_B (x^2-1)/(x^2-y^2)."""
    R = sp.sqrt(x**2 + y**2 - 1)
    u = x*y/R
    P = lambda n: sp.legendre(n, u)
    Sa = sum((x - y)*P(l)/R**(l + 1) for l in range(3))
    Sb = sum((-1)**(3 - l)*(x + y)*P(l)/R**(l + 1) for l in range(3))
    EA, EB = sp.exp(2*beta*(Sa - 1)), sp.exp(2*beta*(Sb + 1))
    EP, EQ = sp.exp(2*beta*P(2)/R**3), sp.exp(3*beta**2*(P(3)**2 - P(2)**2)/R**6)
    f = EP*(x - 1)/(x + 1)
    e2g = EQ*EA/EB*(x**2 - 1)/(x**2 - y**2)
    return {"g_tt": -f, "g_tphi": sp.Integer(0), "g_phiphi": (x**2 - 1)*(1 - y**2)/f,
            "g_xx": e2g*(x**2 - y**2)/(f*(x**2 - 1)), "g_yy": e2g*(x**2 - y**2)/(f*(1 - y**2))}


def exact_r_xi1(row):
    """The certified pipeline's exact normal form r_xi1 in Q(x, E) (mr_mn_axis.axial_nve -> reduced_forms_QxE)."""
    p = ROWS[row]
    if p["kind"] == "static":
        x, y = sp.symbols("x y", positive=True)
        C = static_components(p["beta"], x, y)
    else:
        C, x, y = AX.load(AX.MN_POINTS[p["point"]][0])
    A, B, X = AX.axial_nve(C, x, y, p["En"], p["mu2"])
    Es = sp.Symbol("E")
    Aq, Bq, Xq = (AX.QxE.from_expr(e, x, Es, p["beta"]) for e in (A, B, X))
    return AX.reduced_forms_QxE(Aq, Bq, Xq)["r_xi1"], x, Es


def task_Q1(row):
    """Gate Q1: r_xi1 + (3/16)(P_x/P)^2 == 0 identically in Q(x, E)."""
    t0 = time.time()
    r1, x, Es = exact_r_xi1(row)
    N, D = P_parts(row, x, Es)
    Pq = AX.QxE.from_expr(sp.together(N/D), x, Es, ROWS[row]["beta"])
    lhs = r1 + (Pq.D()/Pq)*(Pq.D()/Pq)*R_(3, 16)
    return dict(task=f"Q1_{row}", identity_zero=bool(lhs.is_zero()), r_xi1_terms=[len(r1.P.terms()), len(r1.Q.terms())],
                seconds=round(time.time() - t0, 1))


def rational_r(row):
    """(Pnum, Qden, bad) for ia_hub.RationalFn. S rows: r = -(3/16)(P_x/P)^2 built from N; R rows: the exact r_xi1."""
    p = ROWS[row]
    x = sp.Symbol("z")
    W = sp.exp(2*p["beta"]/x**3)
    if p["kind"] == "static":
        Es = sp.Symbol("Es")
        N, D = P_parts(row, x, Es)                       # D = x + 1
        Nx4 = sp.expand(x**4*sp.diff(N, x) + Es*(-6*p["beta"])*sp.diff(N, Es))     # x^4 dN/dx, with dW/dx = -6 beta W/x^4
        num = -3*sp.expand(Nx4*(x + 1) - x**4*N)**2
        den = 16*x**8*sp.expand(N)**2*(x + 1)**2
        return num.subs(Es, W), den.subs(Es, W), [0, -1], x
    r1, xs, Es = exact_r_xi1(row)
    num = r1.P.as_expr().subs({Es: sp.exp(2*p["beta"]/xs**3)}).subs(xs, x)
    den = r1.Q.as_expr().subs({Es: sp.exp(2*p["beta"]/xs**3)}).subs(xs, x)
    return num, den, [0], x


# ---------------------------------------------------------------------------------------------- sigma <-> x, lattice
def xmap(beta, s):
    return complex((2*float(beta)/complex(s))**(1.0/3.0))           # principal cube root (Python complex power)


def sigma_of(beta, xv):
    return 2*float(beta)/complex(xv)**3


def lattice(row, j):
    """Float (mpmath 50-digit Newton) lattice points near x = 0 for cells j, j+1 (static: j, j+1, j+2).
    Returns ordered dict name -> (x, sigma, kind 'zero'|'pole'). Used only to place loops."""
    p = ROWS[row]; beta = p["beta"]; En, mu2 = p["En"], p["mu2"]
    xs = sp.Symbol("xs")
    W = sp.exp(2*beta/xs**3)
    N, D = P_parts(row, xs, W)
    fN, fD = sp.lambdify(xs, N, "mpmath"), sp.lambdify(xs, D, "mpmath")
    xsig = lambda s: mp.power(2*mp.mpf(beta.p)/beta.q/s, mp.mpf(1)/3)          # principal cube root (A1.1)
    seeds = []
    if p["kind"] == "static":
        for i in (j, j + 1, j + 2):
            seeds.append((f"Z_{i}", "zero", math.log(En**2/mu2) + 1j*math.pi*(2*i + 1)))
    else:
        M, a, k = p["M"], p["a"], p["k"]
        Wz = sorted(np.roots([a**2*En**2, mu2*k**2, En**2*M**2]), key=abs)     # both negative real (x -> 0 limit)
        for i in (j, j + 1):
            seeds += [(f"Z1_{i}", "zero", math.log(abs(Wz[0])) + 1j*math.pi*(2*i + 1)),
                      (f"Z2_{i}", "zero", math.log(abs(Wz[1])) + 1j*math.pi*(2*i + 1)),
                      (f"P+_{i}", "pole", math.log(M/a) + 1j*(2*math.pi*i + math.pi/2)),
                      (f"P-_{i}", "pole", math.log(M/a) + 1j*(2*math.pi*i - math.pi/2))]
    out = {}
    for name, kind, s0 in seeds:
        g = fN if kind == "zero" else fD
        sr = mp.findroot(lambda s: g(xsig(s)), mp.mpc(s0), tol=mp.mpf(10)**-40, maxsteps=200)   # A1.1: Newton in sigma
        xr = complex(xsig(sr))
        out[name] = (xr, complex(sr), kind)
    return out


def sigma_polyline(beta, pts_sigma, spacing=0.25):
    """Map a polyline given in sigma (vertices) to x, sampling each sigma-segment at <= spacing."""
    out = []
    for a, b in zip(pts_sigma[:-1], pts_sigma[1:]):
        n = max(1, int(math.ceil(abs(b - a)/spacing)))
        out += [xmap(beta, a + (b - a)*t/n) for t in range(n)]
    out.append(xmap(beta, pts_sigma[-1]))
    return out


def circle_sigma(c, rho, entry_dir, n=64):
    """Vertices of the CCW 64-gon in sigma around c, starting at the vertex in direction entry_dir; closed."""
    ph = cmath.phase(entry_dir)
    return [c + rho*cmath.exp(1j*(ph + 2*math.pi*k/n)) for k in range(n + 1)]


def loop_element(beta, base, path_to, c, rho, entry_dir):
    """x-polyline of the loop element: base -> (path_to vertices) -> entry -> CCW 64-gon -> back the same way."""
    circ = circle_sigma(c, rho, entry_dir)
    fwd = [base] + list(path_to) + [circ[0]]
    return sigma_polyline(beta, fwd)[:-1] + sigma_polyline(beta, circ) + sigma_polyline(beta, list(reversed(fwd)))[1:], circ


# ---------------------------------------------------------------------------------------------- certified winding (Q2)
def winding(gc, pts, max_depth=12):
    """Certified winding number of an analytic g (Compiled) along the closed x-polyline pts, or None.
    Per segment: the enclosure of g over the segment's box must exclude 0 (then it lies in an open half-plane through
    0 and the continuous arg change on the segment is the principal Arg(g(b)/g(a)) in (-pi, pi)); bisect otherwise."""
    total = arb(0)
    def seg(a, b, d):
        nonlocal total
        mid, rad = (a + b)/2, abs(b - a)/2
        B = gc(IA.box(mid, rad))
        if B.is_finite() and not (B.real.contains(0) and B.imag.contains(0)):
            ga, gb = gc(acb(a.real, a.imag)), gc(acb(b.real, b.imag))
            ang = (gb/ga).arg()
            if ang.rad() < 0.5:
                total += ang
                return True
        if d >= max_depth:
            return False
        m = (a + b)/2
        return seg(a, m, d + 1) and seg(m, b, d + 1)
    for a, b in zip(pts[:-1], pts[1:]):
        if a == b:
            continue
        if not seg(complex(a), complex(b), 0):
            return None
    w = total/(2*arb.pi())
    n = int(round(float(w.mid())))
    return n if bool(abs(w - n) < arb(0.5)) else None


def enclosed(row, circ_x):
    """(#zeros, #poles) of P inside the closed x-polyline circ_x, certified, or (None, None)."""
    p = ROWS[row]
    z = sp.Symbol("z")
    N, D = P_parts(row, z, sp.exp(2*p["beta"]/z**3))
    return winding(IA.Compiled(N, z), circ_x), winding(IA.Compiled(D, z), circ_x)


# ---------------------------------------------------------------------------------------------- A1.2: local rescaled frame
def frame(beta, sig_c):
    """Exact rational x_c (complex) and eps > 0 with x_c ~ x(sig_c), eps ~ |x_c|/(3|sig_c|)."""
    xc = xmap(beta, sig_c)
    xcR = sp.Rational(repr(xc.real)) + sp.I*sp.Rational(repr(xc.imag))
    epsR = sp.Rational(repr(abs(xc)/(3*abs(sig_c))))
    return xcR, epsR, complex(float(sp.re(xcR)), float(sp.im(xcR))), float(epsR)


def rescaled_rc(num, den, z, bad, xcR, epsR, xc, eps):
    """y_uu = eps^2 r(x_c + eps u) y, exact (symbolic substitution into the same P/Q)."""
    u = sp.Symbol("u")
    sub = {z: xcR + epsR*u}
    return IA.RationalFn(epsR**2*num.subs(sub), den.subs(sub), u, [(complex(b) - xc)/eps for b in bad])


def transport_x(rcu, xc, eps, pts_x, dist_x, stats=None):
    """Transport along an x-polyline in the u-frame. Returns the u-frame matrix D^-1 M_x D, D = diag(1, 1/eps)."""
    pts_u = [(complex(p) - xc)/eps for p in pts_x]
    return IA.transport(rcu, pts_u, dist=(lambda q: dist_x(xc + eps*q)/eps), stats=stats)


# ---------------------------------------------------------------------------------------------- ball tests
def rad_of(t):
    return max(float(t.real.rad()), float(t.imag.rad()))


def ball_test(t, target):
    """[B1]: PASS if the ball contains target with radius <= 1e-10; FAIL if it excludes target; else NOT TESTED."""
    contains = bool(t.real.contains(arb(target)) and t.imag.contains(arb(0)))
    if not contains:
        return "FAIL"
    return "PASS" if rad_of(t) <= VAC else "NOT TESTED"


def ball_str(t):
    return dict(ball=str(t), centre=[float(t.real.mid()), float(t.imag.mid())], radius=rad_of(t),
                sign_real=("-" if float(t.real.mid()) < 0 else "+"))


# ---------------------------------------------------------------------------------------------- the row task
def task_row(row, j):
    t0 = time.time()
    p = ROWS[row]; beta = p["beta"]
    num, den, bad, z = rational_r(row)
    L = lattice(row, j)
    names = list(L)
    sig_c = sum(v[1] for v in L.values())/len(L)
    xcR, epsR, xc, eps = frame(beta, sig_c)
    rc = rescaled_rc(num, den, z, bad, xcR, epsR, xc, eps)
    xs_all = [L[n][0] for n in names]
    def dist(q):
        return min([abs(q - c) for c in xs_all] + [abs(q)])
    out = dict(task=f"{row}_{j}", row=row, j=j, params={k: str(v) for k, v in p.items()},
               lattice={n: dict(x=str(L[n][0]), sigma=str(L[n][1]), kind=L[n][2]) for n in names}, singles={},
               frame=dict(x_c=str(xcR), eps=str(epsR), note="u = (x - x_c)/eps; u-matrices are D^-1 M_x D, D = diag(1, 1/eps)"),
               scope=SCOPE)
    sig = {n: L[n][1] for n in names}
    sep = {n: min(abs(sig[n] - sig[m]) for m in names if m != n) for n in names}
    stats = {}
    # base point and paths
    if p["kind"] == "static":
        c1 = (sig[names[0]] + sig[names[1]])/2
        c2 = (sig[names[1]] + sig[names[2]])/2
        base = c1 + 1j*math.pi + 6
        def path_to(t_c):
            return []
    else:
        maxre = max(s.real for s in sig.values())
        base = complex(maxre + 3, math.pi*(2*j + 1) + math.pi/4)
        def path_to(t_c):
            yc = t_c.imag + math.pi/4
            return [complex(base.real, yc), complex(t_c.real, yc)]
    # singles: T-exact
    Ys = {}
    for n in names:
        c, rho = sig[n], 0.25*sep[n]
        pt = path_to(c)
        entry_dir = (pt[-1] - c) if pt else (base - c)
        if not pt:
            entry_dir = base - c
        xs_loop, circ = loop_element(beta, base, pt, c, rho, entry_dir)
        cnt = enclosed(row, sigma_polyline(beta, circ))
        want = (1, 0) if L[n][2] == "zero" else (0, 1)
        rec = dict(enclosed_zeros_poles=cnt, intended=want)
        if cnt != want:
            rec.update(used=False, why="Q2 count differs from the intended set (or not certified)")
            out["singles"][n] = rec
            continue
        try:
            Y = transport_x(rc, xc, eps, xs_loop, dist, stats)
        except Exception as e:
            rec.update(used=False, why=f"transport: {type(e).__name__}: {e}")
            out["singles"][n] = rec
            continue
        t = IA.tr(Y)
        rec.update(used=True, trace=ball_str(t), T_exact=ball_test(t, 0), det=str(IA.det(Y)))
        out["singles"][n] = rec
        Ys[n] = Y
    # static: pairs (T-limit) and T-L6
    if p["kind"] == "static":
        out["pairs"] = {}
        Yp = {}
        for lab, (a, b) in (("pair_j", (names[0], names[1])), ("pair_j1", (names[1], names[2]))):
            c = (sig[a] + sig[b])/2
            xs_loop, circ = loop_element(beta, base, [], c, 1.5*math.pi, base - c)
            cnt = enclosed(row, sigma_polyline(beta, circ))
            rec = dict(points=[a, b], enclosed_zeros_poles=cnt, intended=(2, 0))
            if cnt != (2, 0):
                rec.update(used=False, why="Q2 count differs from the intended set (or not certified)")
                out["pairs"][lab] = rec
                continue
            try:
                Y = transport_x(rc, xc, eps, xs_loop, dist, stats)
            except Exception as e:
                rec.update(used=False, why=f"transport: {type(e).__name__}: {e}")
                out["pairs"][lab] = rec
                continue
            t = IA.tr(Y)
            win = arb(50)/arb(j)**2
            dev = t - TL_ARB()
            inside = bool(abs(dev) < win)                       # the whole ball within |tr - T| < 50/j^2
            rec.update(used=True, trace=ball_str(t), deviation_from_limit=str(dev), window=str(win),
                       T_limit=("PASS" if inside else "FAIL") if lab == "pair_j" else "n/a (second pair)")
            out["pairs"][lab] = rec
            Yp[lab] = Y
        if len(Yp) == 2:
            ok, det_ = IA.certificate(Yp["pair_j"], Yp["pair_j1"])
            out["T_L6"] = dict(found=bool(ok), g="pair_j", h="pair_j1", **det_)
            out["_YL6"] = (Yp["pair_j"], Yp["pair_j1"]) if ok else None
        else:
            out["T_L6"] = dict(found=False, why="a pair loop was not usable")
    else:
        order = ["Z1_%d" % j, "Z1_%d" % (j + 1), "P+_%d" % j, "P-_%d" % j, "Z2_%d" % j,
                 "P+_%d" % (j + 1), "P-_%d" % (j + 1), "Z2_%d" % (j + 1)]
        prods = []
        for a in range(8):
            for b in range(a + 1, 8):
                na, nb = order[a], order[b]
                if na in Ys and nb in Ys:
                    prods.append((f"{na}*{nb}", IA._matmul(Ys[na], Ys[nb])))
        out["products_available"] = len(prods)
        found = None; tried = 0
        for i in range(len(prods)):
            for k in range(i + 1, len(prods)):
                (gn, G), (hn, H) = prods[i], prods[k]
                tried += 1
                ok, det_ = IA.certificate(G, H)
                if ok:
                    found = dict(found=True, g=gn, h=hn, pairs_tried=tried, **det_)
                    out["_YL6"] = (G, H)
                    break
            if found:
                break
        out["T_L6"] = found or dict(found=False, why="no certified pair in the fixed lexicographic list", pairs_tried=tried)
    out["steps"] = stats.get("steps", 0)
    out["seconds"] = round(time.time() - t0, 1)
    return out


# ---------------------------------------------------------------------------------------------- controls Q3, Q4
def task_Q3(j):
    """G0(b) pullback by exp(2/x^3) (mr_mn_axis.g0, same equation): loop around the root x = (1/(pi i j))^{1/3} of
    exp(2/x^3) = 1; the local exponent difference there is 1/5, so the trace must contain -2 cos(pi/5)."""
    t0 = time.time()
    lam, mu, nu = R_(1, 3), R_(1, 5), R_(1, 7)
    x = sp.Symbol("z")
    phi = sp.exp(2/x**3)
    lp = sp.simplify(sp.diff(sp.log(sp.diff(phi, x)), x))
    rb = sp.together(lp**2/4 - sp.diff(lp, x)/2) + sp.diff(phi, x)**2*AX.riemann_P(lam, mu, nu, phi)
    nB, dB = sp.fraction(sp.together(rb))
    sig0 = 2j*math.pi*j                                   # sigma = 2/x^3 (beta = 1)
    xcR, epsR, xc, eps = frame(1, sig0)
    rB = rescaled_rc(nB, dB, x, [0], xcR, epsR, xc, eps)
    roots = [complex((2/(2j*math.pi*i))**(1/3)) for i in (j - 1, j, j + 1)]
    xr = roots[1]
    rho = 0.25*2*math.pi                                   # in sigma: neighbours at distance 2 pi
    circ = circle_sigma(sig0, rho, 1)
    pts = sigma_polyline(1, circ, spacing=0.05)
    Y = transport_x(rB, xc, eps, pts, lambda q: min([abs(q - r) for r in roots] + [abs(q)]))
    t = IA.tr(Y)
    target = -2*math.cos(math.pi/5)
    e = -2*(arb.pi()/5).cos()
    contains = bool(t.real.contains(e) and t.imag.contains(arb(0)))
    verdict = ("PASS" if rad_of(t) <= VAC else "NOT TESTED") if contains else "FAIL"
    return dict(task=f"Q3_{j}", root=str(xr), trace=ball_str(t), expected=target, Q3=verdict,
                seconds=round(time.time() - t0, 1))


def task_Q4(j):
    """Negative control: r0 = 9 beta^2/x^8 + 2/x^2 (beta = 1/5); solutions exp(+-sigma/2) sigma_x^{-1/2} single-valued,
    so every monodromy is the identity. Same loop geometry as S1 (singles and pairs); traces must contain 2."""
    t0 = time.time()
    beta = R_(1, 5)
    x = sp.Symbol("z")
    r0 = 9*beta**2/x**8 + 2/x**2
    s = 2*beta/x**3
    ysol = sp.exp(s/2)*sp.diff(s, x)**R_(-1, 2)
    check = sp.simplify(sp.diff(ysol, x, 2) - r0*ysol) == 0
    L = lattice("S1", j)
    names = list(L); sig = {n: L[n][1] for n in names}
    xcR, epsR, xc, eps = frame(beta, sum(sig.values())/len(sig))
    rc = rescaled_rc(sp.expand(9*beta**2 + 2*x**6), x**8, x, [0], xcR, epsR, xc, eps)
    c1 = (sig[names[0]] + sig[names[1]])/2
    base = c1 + 1j*math.pi + 6
    res = {}
    Yp = {}
    for lab, c, rho in ((names[0], sig[names[0]], 0.5*math.pi), (names[1], sig[names[1]], 0.5*math.pi),
                        ("pair_j", c1, 1.5*math.pi), ("pair_j1", (sig[names[1]] + sig[names[2]])/2, 1.5*math.pi)):
        xs_loop, _ = loop_element(beta, base, [], c, rho, base - c)
        Y = transport_x(rc, xc, eps, xs_loop, lambda q: abs(q))
        t = IA.tr(Y)
        res[lab] = dict(trace=ball_str(t), Q4=ball_test(t, 2))
        if lab.startswith("pair"):
            Yp[lab] = Y
    ok, det_ = IA.certificate(Yp["pair_j"], Yp["pair_j1"])
    return dict(task=f"Q4_{j}", symbolic_solution_check=bool(check), loops=res,
                L6_certified=bool(ok), Q4=("PASS" if check and not ok and all(v["Q4"] == "PASS" for v in res.values())
                                          else ("FAIL" if (not check or ok or any(v["Q4"] == "FAIL" for v in res.values()))
                                                else "NOT TESTED")),
                seconds=round(time.time() - t0, 1))


# ---------------------------------------------------------------------------------------------- C0
def task_C0():
    """Certified counts of zeros and poles of P (row R1 = p1, (1, 9)) inside the recorded loop h of 2ce8b41 row 7:
    g[0.0634+0.4514j, rad 0.1240], the ia_hub.loop_points 16-gon. The full-precision centre is re-derived with the
    recorded deterministic locator (mr_mn_axis.locate_singular on the recorded r_xi1) and matched to 4 decimals."""
    t0 = time.time()
    rec = json.load(open(os.path.join(HERE, "mr_mn_row_7.json")))["forms"]["r_xi1"]
    r1, xs, Es = exact_r_xi1("R1")
    r_eval = r1.to_expr()
    sing = AX.locate_singular(r_eval, xs)
    cands = [c for c in sing if abs(c - complex(0.0634, 0.4514)) < 1e-3]
    out = dict(task="C0", recorded_h=rec["h"], recorded_base=rec["base"], recorded_located=rec["located"])
    if len(cands) != 1:
        out.update(ok=False, why=f"centre not uniquely re-derived: {cands}")
        return out
    c = cands[0]
    sep = min([abs(c - d) for d in sing if d != c] + [abs(c)])
    rad = 0.3*sep
    out.update(centre=str(c), rad=rad, rad_matches_record=bool(abs(rad - 0.1240) < 5e-5))
    poly = IA.loop_points(complex(rec["base"].strip("()").replace(" ", "")), c, rad)[1:-1]   # the 16-gon itself
    nz, npl = enclosed("R1", poly)
    out.update(zeros_inside=nz, poles_inside=npl)
    L = lattice("R1", 0)
    beta = ROWS["R1"]["beta"]
    labels = {}
    for n, (xv, sv, kind) in L.items():
        labels[n] = dict(x=str(xv), sigma=str(sv), kind=kind, dist_to_centre=abs(xv - c), inside_circle_float=abs(xv - c) < rad)
    out["lattice_cells_0_1"] = labels
    out["seconds"] = round(time.time() - t0, 1)
    return out


# ---------------------------------------------------------------------------------------------- driver
def run_task(name):
    if name.startswith("Q1_"):
        return task_Q1(name[3:])
    if name.startswith("Q3_"):
        return task_Q3(int(name[3:]))
    if name.startswith("Q4_"):
        return task_Q4(int(name[3:]))
    if name == "C0":
        return task_C0()
    row, j = name.split("_")
    out = task_row(row, int(j))
    YL6 = out.pop("_YL6", None)
    if YL6 is not None:
        import lean_export as LE
        G, H = YL6
        os.makedirs(OUTDIR, exist_ok=True)
        BG, BH = LE.box(G), LE.box(H)
        ex = dict(family="mnlat", row=name, which="v1", N=100, g_word=out["T_L6"]["g"], h_word=out["T_L6"]["h"], frame=out["frame"],
                  certificate_ok=True, gate_bit_for_bit=True, export_source="the certifying run itself (no regeneration)",
                  readback=(LE.readback_ok(G, BG) and LE.readback_ok(H, BH)), G=BG, H=BH)
        json.dump(ex, open(os.path.join(OUTDIR, f"lean_{name}.json"), "w"), indent=1)
        out["lean_export"] = dict(file=f"mn_lattice/lean_{name}.json", readback=ex["readback"])
    return out


PHASE1 = ["Q1_S1", "Q1_S2", "Q1_R1", "Q1_R2", "Q3_10", "Q4_10", "S1_10", "S2_10", "R1_10", "R2_10", "C0"]
PHASE2 = ["Q3_100", "Q3_1000", "Q4_100", "Q4_1000"] + [f"{r}_{j}" for j in (100, 1000) for r in ("S1", "S2", "R1", "R2")]


def run_phase(ph):
    import mr_watchdog as W
    os.makedirs(OUTDIR, exist_ok=True)
    tasks = PHASE1 if ph == "1" else PHASE2
    summary = {}
    for t in tasks:
        fn = os.path.join(OUTDIR, f"{t}.json")
        r = W.run_guarded([sys.executable, __file__, "--task", t, fn], mem_limit_mb=2048, time_limit_s=1800,
                          cwd=HERE, log=os.path.join(OUTDIR, f"{t}.log"))
        summary[t] = dict(guard=r)
        print(t, r, flush=True)
    json.dump(summary, open(os.path.join(OUTDIR, f"phase{ph}_guard.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    if sys.argv[1] == "--task":
        t0 = time.time()
        res = run_task(sys.argv[2])
        json.dump(res, open(sys.argv[3], "w"), indent=1, default=str)
        print(json.dumps({k: v for k, v in res.items() if k not in ("lattice", "singles", "lattice_cells_0_1")},
                         default=str)[:3000])
    elif sys.argv[1] == "--phase":
        run_phase(sys.argv[2])
