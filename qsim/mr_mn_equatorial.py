"""
MN on the EQUATORIAL solution: certified-monodromy obstruction, as registered in
PREREG_mn_equatorial_certified_monodromy.md (bc4d735). Frozen ia_hub integrator and the A5 search policy.

Route: y = 0, p_y = 0; R = sqrt(x^2 - 1) uniformised by x = (t + 1/t)/2, R = (t^2 - 1)/(2t); coefficients in
Q(t, E1, E2, E3), E_i = exp(g_i(t)); reduced forms built exactly with the derivation D = d/dt + sum g_i' E_i d/dE_i;
essential singularities at t = +-1 declared `bad`.

Since d_y g_ab = 0 at y = 0 (gate Q1, exact), second y-derivatives of any function G(g_ab) at y = 0 are
sum_i dG/dg_i * d_y^2 g_i -- no symbolic differentiation of the (large) inverse metric is needed.

Usage:  python mr_mn_equatorial.py Q1|Q2|Q3|Q4     |     python mr_mn_equatorial.py --one <task> out.json
"""
import json, math, os, sys, time
import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ia_hub as IA
import mr_mn_axis as MA
from flint import acb, ctx

ctx.prec = 192
T_ = sp.Symbol("t")
E_ = sp.symbols("E1 E2 E3")
LEVELS = [(1, 0, 4), (1, 0, 9), (1, 1, 4)]          # (E, L, mu^2) -- registered
BAD = [1, -1]
BAD_SKIP = 0.15
COMP = ("g_tt", "g_tphi", "g_phiphi", "g_xx", "g_yy")


# ----------------------------------------------------------------------------------------------
# uniformisation and the exponential generators
# ----------------------------------------------------------------------------------------------
X_OF_T = (T_**2 + 1)/(2*T_)
R_OF_T = (T_**2 - 1)/(2*T_)


def generators(beta):
    """g_i(t) for E_i = exp(g_i), from the feasibility look: beta/R^3, beta(2 - 2x/R + x/R^3), -3 beta^2/(4 R^6)."""
    if not beta:
        return []
    x, R = X_OF_T, R_OF_T
    return [sp.cancel(beta/R**3), sp.cancel(beta*(2 - 2*x/R + x/R**3)), sp.cancel(-3*beta**2/(4*R**6))]


def to_t(expr, x, y=None):
    """Expression in x (y already 0) with sqrt(x^2-1) -> rational in t (and exp atoms kept)."""
    base = x**2 - 1
    def rep(e):
        b, n = e.args
        if sp.simplify(b - base) == 0 and (2*n).is_Integer:
            return sp.Symbol("R_")**int(2*n)
        raise ValueError(f"unsupported non-integer power {e}")
    e = expr.replace(lambda e: e.is_Pow and not e.args[1].is_Integer, rep)
    return e.subs({sp.Symbol("R_"): R_OF_T, x: X_OF_T})


def exp_to_Es(expr, gens):
    """Every exp(arg) -> prod E_i^{c_i} with arg == sum c_i g_i exactly (c_i rational). Raises if impossible."""
    def rep(e):
        arg = sp.cancel(e.args[0])
        n = len(gens)
        cs = sp.symbols(f"c0:{n}")
        pts = [sp.Rational(3, 2), sp.Rational(5, 2), sp.Rational(7, 3), sp.Rational(11, 4), sp.Rational(13, 5)]
        eqs = [sp.Eq(arg.subs(T_, p), sum(c*g.subs(T_, p) for c, g in zip(cs, gens))) for p in pts[:max(n, 1) + 2]]
        sol = sp.solve(eqs, cs, dict=True)
        if not sol:
            raise ValueError(f"exp argument {arg} is not a combination of the generators")
        sol = sol[0]
        if sp.cancel(arg - sum(sol[c]*g for c, g in zip(cs, gens))) != 0:
            raise ValueError(f"exp argument {arg}: decomposition not exact")
        out = sp.Integer(1)
        for c, Ei in zip(cs, E_):
            v = sol.get(c, 0)
            if not v.is_Integer:
                raise ValueError(f"non-integer exponent {v} for {Ei} (would need a root of E)")
            out *= Ei**int(v)
        return out
    return expr.replace(lambda e: isinstance(e, sp.exp), rep)


# ----------------------------------------------------------------------------------------------
# exact field Q(t, E1, E2, E3) with the derivation
# ----------------------------------------------------------------------------------------------
class QtE:
    GENS = (T_,) + E_

    def __init__(self, P, Q, ctxd):
        self.c = ctxd
        if Q.is_zero:
            raise ZeroDivisionError
        g = sp.gcd(P, Q)
        P, Q = sp.quo(P, g), sp.quo(Q, g)
        lc = Q.LC()
        self.P, self.Q = (P*(1/lc) if not P.is_zero else P), Q*(1/lc)

    @staticmethod
    def poly(e):
        return sp.Poly(e, *QtE.GENS, domain="QQ")

    @classmethod
    def from_expr(cls, e, ctxd):
        e = sp.together(e)
        n, d = sp.fraction(e)
        return cls(cls.poly(n), cls.poly(d), ctxd)

    def _n(self, P, Q):
        return QtE(P, Q, self.c)

    def _l(self, o):
        return o if isinstance(o, QtE) else self._n(self.poly(sp.Rational(o)), self.poly(1))

    def __add__(self, o):
        o = self._l(o); return self._n(self.P*o.Q + o.P*self.Q, self.Q*o.Q)

    def __sub__(self, o):
        o = self._l(o); return self._n(self.P*o.Q - o.P*self.Q, self.Q*o.Q)

    def __mul__(self, o):
        o = self._l(o); return self._n(self.P*o.P, self.Q*o.Q)

    def __truediv__(self, o):
        o = self._l(o)
        if o.P.is_zero:
            raise ZeroDivisionError
        return self._n(self.P*o.Q, self.Q*o.P)

    __radd__ = __add__
    __rmul__ = __mul__

    def __neg__(self):
        return self._n(-self.P, self.Q)

    def _Db(self, P):
        """b * D(P) as a polynomial, b the common denominator of the g_i'."""
        a, b = self.c["a"], self.c["b"]
        out = b*P.diff(T_)
        for ai, Ei in zip(a, E_):
            out += ai*self.poly(Ei)*P.diff(Ei)
        return out

    def D(self):
        b = self.c["b"]
        return self._n(self._Db(self.P)*self.Q - self.P*self._Db(self.Q), b*self.Q*self.Q)

    def is_zero(self):
        return self.P.is_zero

    def to_expr(self, part=None):
        sub = {Ei: sp.exp(g) for Ei, g in zip(E_, self.c["gens"])}
        if part == "P":
            return self.P.as_expr().subs(sub)
        if part == "Q":
            return self.Q.as_expr().subs(sub)
        return (self.P.as_expr()/self.Q.as_expr()).subs(sub)


def field_ctx(beta):
    gens = generators(beta)
    ders = [sp.cancel(sp.diff(g, T_)) for g in gens]
    b = sp.Integer(1)
    for d in ders:
        b = sp.lcm(b, sp.fraction(d)[1])
    a = [QtE.poly(sp.cancel(d*b)) for d in ders]
    return dict(gens=gens, a=a, b=QtE.poly(b), beta=beta)


# ----------------------------------------------------------------------------------------------
# the equatorial NVE, built in Q(t, E)
# ----------------------------------------------------------------------------------------------
def lower_at_equator(C, x, y, cd):
    """For each lower component: value, first and second y-derivative at y = 0, as QtE."""
    out = {}
    for k in COMP:
        g = C[k]
        vals = []
        for order in (0, 1, 2):
            e = sp.diff(g, y, order).subs(y, 0) if order else g.subs(y, 0)
            e = to_t(e, x)
            if cd["gens"]:
                e = exp_to_Es(e, cd["gens"])
            elif e.has(sp.exp):
                e = e.replace(lambda z: isinstance(z, sp.exp), lambda z: sp.exp(sp.cancel(z.args[0])))
                if e.has(sp.exp):
                    raise ValueError("exp atoms present at beta = 0")
            vals.append(QtE.from_expr(e, cd))
        out[k] = vals
    return out


def equatorial_nve(G, En, L, mu2):
    """A, B, tdot^2 in Q(t,E) from the y = 0 values (d_y = 0 there by Q1)."""
    tt, tp, pp, xx, yy = (G[k][0] for k in COMP)
    tt2, tp2, pp2, xx2, yy2 = (G[k][2] for k in COMP)
    Dl = tt*pp - tp*tp                                   # g_tt g_pp - g_tp^2
    Nv = pp*(En**2) + tp*(2*En*L) + tt*(L**2)           # numerator of V
    V0 = Nv/Dl
    # dV/dg_i with d_y g = 0:  V = Nv/Dl
    dNv = {"tt": L**2, "tp": 2*En*L, "pp": En**2}
    dDl = {"tt": pp, "tp": -(tp*2), "pp": tt}
    Vyy = sp.Integer(0)
    second = {"tt": tt2, "tp": tp2, "pp": pp2}
    Vyy = None
    for key in ("tt", "tp", "pp"):
        term = (Dl*dNv[key] - Nv*dDl[key])/(Dl*Dl)*second[key]
        Vyy = term if Vyy is None else Vyy + term
    gxx_inv0 = QtE.from_expr(sp.Integer(1), xx.c)/xx
    gxx_inv_yy = -(xx2/(xx*xx))
    A = QtE.from_expr(sp.Integer(1), yy.c)/yy          # g^yy at y = 0
    minus_mu2_V0 = V0*(-1) - mu2
    px2 = minus_mu2_V0/gxx_inv0
    xdot2 = gxx_inv0*minus_mu2_V0
    B = px2*gxx_inv_yy*sp.Rational(1, 2) + Vyy*sp.Rational(1, 2)
    xprime = QtE.from_expr(sp.cancel(sp.diff(X_OF_T, T_)), xx.c)
    tdot2 = xdot2/(xprime*xprime)
    return A, B, tdot2


def form_t(A, B, X, which):
    """One reduced form, built only when needed (xi2 lazily: pipeline fix, 2880887)."""
    q = A*B/X
    if which == "r_xi1":
        p1 = -(A.D()/A - X.D()/(X*2))
        return p1*p1/4 + p1.D()/2 - q
    if B.is_zero():
        return None
    p2 = -(B.D()/B - X.D()/(X*2))
    return p2*p2/4 + p2.D()/2 - q


def reduced_forms_t(A, B, X):
    q = A*B/X
    out = {}
    if not B.is_zero():
        p2 = -(B.D()/B - X.D()/(X*2))
        out["r_xi2"] = p2*p2/4 + p2.D()/2 - q
    p1 = -(A.D()/A - X.D()/(X*2))
    out["r_xi1"] = p1*p1/4 + p1.D()/2 - q
    return out


# ----------------------------------------------------------------------------------------------
# sources
# ----------------------------------------------------------------------------------------------
def source(kind, p=None):
    """-> (C, x, y, beta)."""
    if kind == "mn":
        fname, beta = MA.MN_POINTS[p]
        C, x, y = MA.load(fname)
        return C, x, y, beta
    if kind == "kerr":
        C, x, y = MA.load(MA.KERR_POINTS[p])
        return C, x, y, 0
    if kind == "zv":
        import mr_ts2 as T2
        X, Y = T2.X, T2.Y
        f = ((X - 1)/(X + 1))**2
        e2g = (X**2 - 1)**4/(X**2 - Y**2)**4
        C = {"g_tt": -f, "g_tphi": sp.Integer(0), "g_phiphi": (X**2 - 1)*(1 - Y**2)/f,
             "g_xx": e2g*(X**2 - Y**2)/((X**2 - 1)*f), "g_yy": e2g*(X**2 - Y**2)/((1 - Y**2)*f)}
        return C, X, Y, 0
    raise ValueError(kind)


# ----------------------------------------------------------------------------------------------
# loop choice (float) and the A5 certificate search, t-plane version
# ----------------------------------------------------------------------------------------------
def locate_singular_t(r_eval, box_=6.0, grid=90):
    import mpmath as mp
    f = sp.lambdify(T_, r_eval, "numpy")
    g = sp.lambdify(T_, 1/r_eval, "mpmath")
    xs = np.linspace(-box_, box_, grid)
    Z = xs[None, :] + 1j*xs[:, None] + 1e-3*(1 + 1j)
    with np.errstate(all="ignore"):
        V = np.abs(f(Z))
    V[~np.isfinite(V)] = 1e300
    cands = [Z[i, j] for i in range(1, grid - 1) for j in range(1, grid - 1)
             if V[i, j] > 10*np.median(V) and V[i, j] == V[i-1:i+2, j-1:j+2].max()]
    found = []
    for c0 in cands:
        try:
            c = complex(mp.findroot(g, mp.mpc(c0), tol=1e-20, maxsteps=60))
        except Exception:
            continue
        if abs(c) <= box_ and all(abs(c - d) > 1e-6 for d in found) and all(abs(c - b) >= BAD_SKIP for b in BAD):
            found.append(c)
    return sorted(found, key=lambda c: (round(c.real, 6), round(c.imag, 6)))


def certificate_search_t(PQ, sing, bad, stats):
    rc = IA.RationalFn(PQ[0], PQ[1], T_, bad)
    pts = list(sing)
    if len(pts) < 2:
        return dict(found=False, why=f"only {len(pts)} located singular points")
    obst = list(sing) + [complex(b) for b in BAD]
    dmin = lambda q: min(abs(q - c) for c in obst)
    sep = {c: min(abs(c - d) for d in obst if d != c) for c in pts}
    rng = np.random.default_rng(7)
    span = max(abs(c) for c in pts) + 1.0
    z0 = max((complex(rng.uniform(-span, span), rng.uniform(-span, span)) for _ in range(4000)), key=dmin)
    pts = sorted(pts, key=lambda c: abs(c - z0))
    gens, cand, tried = [], [], 0
    for c in pts:
        rad = 0.3*sep[c]
        Y = IA.transport(rc, IA.loop_points(z0, c, rad), dist=dmin, stats=stats)
        name = f"g[{c:.4f}, rad {rad:.4f}]"
        new = [(name, Y)] + [(f"{gn}*{name}", IA._matmul(GY, Y)) for gn, GY in gens]
        gens.append((name, Y))
        for nn, NY in new:
            for on, OY in cand:
                for (an, AY), (bn, BY) in (((on, OY), (nn, NY)), ((nn, NY), (on, OY))):
                    if not IA.certainly_not_in_segment(IA.tr(AY)):
                        continue
                    tried += 1
                    ok, det_ = IA.certificate(AY, BY)
                    if ok:
                        return dict(found=True, g=an, h=bn, base=str(z0), **det_, pairs_tried=tried,
                                    n_generators=len(gens))
            cand.append((nn, NY))
    return dict(found=False, why="no certified pair in the registered candidate list", base=str(z0),
                generator_traces={gn: str(IA.tr(GY)) for gn, GY in gens}, pairs_tried=tried, n_generators=len(gens))


# ----------------------------------------------------------------------------------------------
# gates
# ----------------------------------------------------------------------------------------------
def build(kind, p, En, L, mu2):
    """-> (G, (A, B, X), cd, (C, x, y, beta)); forms are built lazily by form_t."""
    C, x, y, beta = source(kind, p)
    cd = field_ctx(beta)
    G = lower_at_equator(C, x, y, cd)
    return G, equatorial_nve(G, En, L, mu2), cd, (C, x, y, beta)


def numeric_ref(C, x, y, En, L, mu2, form, tv, dps=60):
    """INDEPENDENT reference: lower components evaluated numerically (mpmath), derivatives by mp.diff;
    mapped to t: r_t = x'(t)^2 r_x - S/2. Shares no code with the chain-rule / Q(t,E) path."""
    import mpmath as mp
    mp.mp.dps = dps
    f = {k: sp.lambdify((x, y), C[k], "mpmath") for k in COMP}
    half = mp.mpf(1)/2

    def V(xv, yv):
        tt, tp, pp = f["g_tt"](xv, yv), f["g_tphi"](xv, yv), f["g_phiphi"](xv, yv)
        return (pp*En**2 + 2*tp*En*L + tt*L**2)/(tt*pp - tp**2)
    gxi = lambda xv, yv: 1/f["g_xx"](xv, yv)
    A = lambda xv: 1/f["g_yy"](xv, 0)
    X = lambda xv: gxi(xv, 0)*(-mu2 - V(xv, 0))

    def B(xv):
        px2 = (-mu2 - V(xv, 0))/gxi(xv, 0)
        return half*px2*mp.diff(lambda yy: gxi(xv, yy), 0, 2) + half*mp.diff(lambda yy: V(xv, yy), 0, 2)
    tv = mp.mpf(sp.Rational(tv).p)/sp.Rational(tv).q
    xv = (tv**2 + 1)/(2*tv)
    F = A if form == "r_xi1" else B
    Fv, Fp, Fpp = F(xv), mp.diff(F, xv, 1), mp.diff(F, xv, 2)
    Xv, Xp, Xpp = X(xv), mp.diff(X, xv, 1), mp.diff(X, xv, 2)
    p_ = -(Fp/Fv - Xp/(2*Xv))
    dp = -((Fpp*Fv - Fp**2)/Fv**2 - (Xpp*Xv - Xp**2)/(2*Xv**2))
    rx = p_**2/4 + dp/2 - A(xv)*B(xv)/Xv
    xp = (1 - 1/tv**2)/2
    xpp, xppp = 1/tv**3, -3/tv**4
    S = xppp/xp - mp.mpf(3)/2*(xpp/xp)**2
    return xp**2*rx - S/2


def check_form(rq, src, En, L, mu2, form, pts=(sp.Rational(9, 4), sp.Integer(3), sp.Rational(7, 4))):
    """Q2 criterion for one form: max relative difference vs numeric_ref at dyadic t > 1."""
    import mpmath as mp
    C, x, y, beta = src
    a_ = IA.Compiled(rq.to_expr(), T_)
    worst = 0.0
    for tv in pts:
        ref = numeric_ref(C, x, y, En, L, mu2, form, tv)
        va = a_(a_._const(tv))
        vam = mp.mpc(va.real.mid().str(60, radius=False), va.imag.mid().str(60, radius=False))
        worst = max(worst, float(abs(vam - ref)/abs(ref)))
    return worst


def q1():
    res = {}
    for p in ("p1", "p2"):
        C, x, y, beta = source("mn", p)
        cd = field_ctx(beta)
        G = lower_at_equator(C, x, y, cd)
        res[p] = {k: bool(G[k][1].is_zero()) for k in COMP}
    res["Q1_PASS"] = all(all(v.values()) for k, v in res.items() if isinstance(v, dict))
    return res


def q2():
    """Pipeline check (fix 2880887): xi1 from Q(t,E) vs the independent numerical-differentiation reference."""
    out = {}
    for kind, p in (("mn", "p1"), ("mn", "p2"), ("kerr", "p1"), ("zv", None)):
        for En, L, mu2 in ((1, 0, 4), (1, 1, 4)):
            G, (A, B, X), cd, src = build(kind, p, En, L, mu2)
            r1 = form_t(A, B, X, "r_xi1")
            out[f"{kind}{p or ''} r_xi1 (E,L,mu2)=({En},{L},{mu2})"] = check_form(r1, src, En, L, mu2, "r_xi1")
            print(out, flush=True)
    out["Q2_PASS"] = all(v < 1e-25 for v in out.values() if isinstance(v, float))
    return out


def raw_reduced(A, B, X, x):
    p2 = -(sp.diff(B, x)/B - sp.diff(X, x)/(2*X))
    p1 = -(sp.diff(A, x)/A - sp.diff(X, x)/(2*X))
    q = A*B/X
    return {"r_xi2": p2**2/4 + sp.diff(p2, x)/2 - q, "r_xi1": p1**2/4 + sp.diff(p1, x)/2 - q}


def raw_inverse(C, y):
    gtt, gtp, gpp, gxx, gyy = (C[k] for k in COMP)
    Dl = gtt*gpp - gtp**2
    return dict(tt=gpp/Dl, tphi=-gtp/Dl, phiphi=gtt/Dl, xx=1/gxx, yy=1/gyy)


def raw_equatorial(inv, x, y, En, L, mu2):
    """Raw (unsimplified) equatorial A, B, xdot^2 in x, for the Q2 cross-check only."""
    V = inv["tt"]*En**2 - 2*inv["tphi"]*En*L + inv["phiphi"]*L**2
    V0 = V.subs(y, 0)
    gxx0 = inv["xx"].subs(y, 0)
    px2 = (-mu2 - V0)/gxx0
    xdot2 = gxx0*(-mu2 - V0)
    A = inv["yy"].subs(y, 0)
    px = sp.Symbol("p_x")
    H = sp.Rational(1, 2)*(V + inv["xx"]*px**2)
    B = sp.diff(H, y, 2).subs(y, 0).subs(px**2, px2)
    return A, B, xdot2


def rows():
    r = []
    for En, L, mu2 in ((1, 0, 4), (1, 0, 9)):
        r.append(("Q3", f"ZV d=2 equatorial ({En},{L},{mu2}) [must FIND]", ("zv", None, En, L, mu2), True))
    for p in ("p1", "p2"):
        for En, L, mu2 in LEVELS:
            r.append(("Q3", f"Kerr {p} equatorial ({En},{L},{mu2}) [must NOT find]", ("kerr", p, En, L, mu2), False))
    for p in ("p1", "p2"):
        for En, L, mu2 in LEVELS:
            r.append(("Q4", f"MN {p} equatorial ({En},{L},{mu2})", ("mn", p, En, L, mu2), None))
    return r


def run_row(spec, outp=None):
    kind, p, En, L, mu2 = spec
    t0 = time.time()
    stats = {}
    G, (A, B, X), cd, src = build(kind, p, En, L, mu2)
    out = dict(spec=str(spec), forms={}, terms={})
    bad = BAD if cd["gens"] else []
    save = (lambda: json.dump(out, open(outp, "w"), indent=1, default=str)) if outp else (lambda: None)
    print(f"[{time.time()-t0:.1f}s] y = 0 data and A, B, tdot^2 built", flush=True)
    for k in ("r_xi1", "r_xi2"):
        if any(f.get("found") for f in out["forms"].values()):
            out["forms"][k] = dict(found=None, why="not run: certificate already found on the other form")
            continue
        out["forms"][k] = dict(found=None, why="building (a kill here leaves this form INCONCLUSIVE)")
        save()
        rq = form_t(A, B, X, k)
        if rq is None:
            out["forms"][k] = dict(found=None, why="degenerate: B == 0 exactly")
            continue
        out["terms"][k] = [len(rq.P.terms()), len(rq.Q.terms())]
        print(f"[{time.time()-t0:.1f}s] {k} built in Q(t,E): {out['terms'][k]}", flush=True)
        if k == "r_xi2":                                       # inline pipeline check (fix 2880887)
            err = check_form(rq, src, En, L, mu2, k)
            out["xi2_inline_check_relerr"] = err
            print(f"[{time.time()-t0:.1f}s] xi2 inline check rel err {err:.2e}", flush=True)
            if not err < 1e-25:
                out["forms"][k] = dict(found=None, why=f"xi2 pipeline check FAILED ({err:.2e}): not searched")
                save()
                continue
        sing = locate_singular_t(rq.to_expr())
        print(f"[{time.time()-t0:.1f}s] {k}: {len(sing)} located singular points", flush=True)
        try:
            res = certificate_search_t((rq.to_expr("P"), rq.to_expr("Q")), sing, bad, stats)
        except Exception as e:
            res = dict(found=False, why=f"{type(e).__name__}: {e}")
        res["located"] = [str(complex(round(c.real, 5), round(c.imag, 5))) for c in sing]
        out["forms"][k] = res
        save()
        print(f"[{time.time()-t0:.1f}s] {k}: certificate found = {res['found']}  {res.get('why', '')}", flush=True)
    out["steps"] = stats.get("steps", 0)
    out["seconds"] = round(time.time() - t0, 1)
    save()
    return out


def run_gate(gate, only=None):
    import mr_watchdog as W
    py = sys.executable
    if gate in ("Q1", "Q2"):
        outp = os.path.join(HERE, f"mr_mneq_{gate}.json")
        g = W.run_guarded([py, "-u", os.path.abspath(__file__), "--one", gate, outp], mem_limit_mb=2048,
                          time_limit_s=3600, cwd=HERE, log=os.path.join(HERE, f"mr_mneq_{gate}.log"))
        res = json.load(open(outp)) if g["status"] == "ok" and os.path.exists(outp) else dict(failed=g["status"])
        res["guard"] = g
        print(json.dumps(res, indent=1, default=str), flush=True)
        return res
    allr = rows()
    results = []
    for i, (tag, name, spec, expect) in enumerate(allr):
        if tag != gate or (only is not None and i not in only):
            continue
        outp = os.path.join(HERE, f"mr_mneq_row_{i}.json")
        if os.path.exists(outp):
            os.remove(outp)
        g = W.run_guarded([py, "-u", os.path.abspath(__file__), "--one", f"row{i}", outp], mem_limit_mb=2048,
                          time_limit_s=10800, cwd=HERE, log=os.path.join(HERE, f"mr_mneq_row_{i}.log"))
        if os.path.exists(outp):
            res = json.load(open(outp))
            if g["status"] != "ok":
                res["killed"] = g["status"]
                for f in res.get("forms", {}).values():
                    if f.get("found") is None and "not run" not in f.get("why", ""):
                        f["why"] = f"INCONCLUSIVE (resource: {g['status']}) -- " + f.get("why", "")
        else:
            res = dict(forms={}, failed=g["status"])
        found = any(f.get("found") for f in res.get("forms", {}).values())
        if expect is True:
            verdict = "PASS" if found else "FAIL (certificate not found)"
        elif expect is False:
            verdict = ("FAIL (certificate FOUND on an integrable control)" if found
                       else ("PASS" if res.get("forms") else "FAIL (did not run)"))
        else:
            verdict = "OBSTRUCTION (certificate)" if found else "INCONCLUSIVE"
        res.update(tag=tag, name=name, assessment=verdict, guard=g)
        results.append(res)
        print(f"{i:>2} {tag} {name:<48} => {verdict:<28} {({k: v.get('found') for k, v in res.get('forms', {}).items()})}"
              f" [guard {g['status']}, peak {g['peak_mb']} MB, {g['seconds']} s]", flush=True)
        json.dump(results, open(os.path.join(HERE, f"mr_mneq_{gate}_run.json"), "w"), indent=1, default=str)
        if expect is not None and verdict != "PASS":
            print("CONTROL MISBEHAVED: stopping, per the registration", flush=True)
            break
    return results


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--one":
        task, outp = sys.argv[2], sys.argv[3]
        if task == "Q1":
            res = q1()
        elif task == "Q2":
            res = q2()
        else:
            res = run_row(rows()[int(task[3:])][2], outp)
        json.dump(res, open(outp, "w"), indent=1, default=str)
    else:
        only = set(int(a) for a in sys.argv[2].split(",")) if len(sys.argv) > 2 else None   # row filter (re-run)
        run_gate(sys.argv[1], only)
