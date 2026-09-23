"""
Stage 2b: a ROOT-FREE, factor-by-factor Kovacic route (PREREG_ts2b_factor_route.md, 737982c + fca18ea).

For reduced y'' = r y, r = s/t in Q(x): factor t over Q and never compute a root. All local
data at the roots of an irreducible factor g live in Q(c) = Q[a]/(g), where an element vanishes
at one root iff it vanishes at every conjugate -- so every statement below holds for all
conjugate singular points at once.

    OBSTRUCTION   iff  a logarithmic point exists (excludes Kovacic cases 2 and 3)
                  AND  no count combination gives d in Z>=0 (Kovacic's case-1 necessary condition)
    INCONCLUSIVE  otherwise.  This route never outputs NO_OBSTRUCTION.

Scope: finite poles of order 1 or 2, ord_inf >= 2, and on every order-2 factor a RATIONAL local
coefficient b (so all conjugate roots share the same exponents). Anything else is INCONCLUSIVE.
"""
import sympy as sp
from sympy import QQ

OBSTRUCTION, INCONCLUSIVE = "OBSTRUCTION", "INCONCLUSIVE"
A = sp.Symbol("a_root")


class NumberField:
    """Q[a]/(g) for an irreducible g over Q; elements are Polys in A, reduced."""

    def __init__(self, g_expr, x):
        self.g = sp.Poly(sp.sympify(g_expr).subs(x, A), A, domain=QQ).monic()

    def elt(self, p_expr, x):
        return sp.Poly(sp.sympify(p_expr).subs(x, A), A, domain=QQ).rem(self.g)

    def const(self, q):
        return sp.Poly(q, A, domain=QQ)

    def mul(self, p, q):
        return (p*q).rem(self.g)

    def inv(self, p):
        if p.is_zero:
            raise ZeroDivisionError("inverse of 0 in Q(c)")
        return sp.Poly(sp.invert(p.as_expr(), self.g.as_expr(), A), A, domain=QQ).rem(self.g)

    @staticmethod
    def as_rational(p):
        if p.is_zero:
            return sp.Integer(0)
        return sp.Rational(p.LC()) if p.degree() <= 0 else None


def _taylor_at_root(P, K, x, n):
    """Coefficients P_k = P^(k)(c)/k! in Q(c), k = 0..n-1, for a polynomial P in x."""
    out, D = [], sp.Poly(P, x, domain=QQ)
    for k in range(n):
        out.append(K.elt(D.as_expr(), x) if not D.is_zero else K.const(0))
        D = D.diff(x)*sp.Rational(1, k + 1)
    return out


def laurent_at_factor(s, t, g, m, x, n):
    """f_0..f_{n-1} in Q(c) with r = (x-c)^{-m} sum f_k (x-c)^k at a root c of g (g^m || t)."""
    K = NumberField(g, x)
    ts = _taylor_at_root(t, K, x, n + m)
    if any(not tk.is_zero for tk in ts[:m]):
        raise ValueError("multiplicity bookkeeping failed")
    tt = ts[m:]
    ss = _taylor_at_root(s, K, x, n)
    inv0 = K.inv(tt[0])
    f = []
    for k in range(n):
        acc = ss[k]
        for j in range(1, k + 1):
            acc = acc - K.mul(tt[j], f[k - j])
        f.append(K.mul(acc, inv0))
    return K, f


def sqrt_rational(u):
    """sqrt(u) for rational u as (coef, m): coef*sqrt(m), m a squarefree integer (sign kept)."""
    u = sp.Rational(u)
    if u == 0:
        return sp.Integer(0), 1
    n = u.p*u.q
    sgn = -1 if n < 0 else 1
    sq, free = 1, 1
    for pr, e in sp.factorint(abs(n)).items():
        sq *= pr**(e//2)
        if e % 2:
            free *= pr
    return sp.Rational(sq, u.q), sgn*free


def _frobenius_log_field(K, f, b, N):
    """Integer exponent difference N >= 0 at an order-2 point with Laurent data f (in Q(c)).
    True iff the smaller-exponent Frobenius series is inconsistent at k = N (a logarithm)."""
    if N == 0:
        return True
    a2 = sp.Rational(1, 2) - sp.Rational(N, 2)
    coeffs = [K.const(1)]
    for k in range(1, N + 1):
        rhs = K.const(0)
        for j in range(1, k + 1):
            rhs = rhs + K.mul(f[j], coeffs[k - j])
        rhs = rhs.rem(K.g)
        lhs = (a2 + k)*(a2 + k - 1) - b
        if k < N:
            coeffs.append(K.mul(rhs, K.const(1/lhs)))
        else:
            return not rhs.is_zero
    return False


def _local(s, t, g, m, x):
    """Local data at the roots of the factor g (multiplicity m in t)."""
    dg = int(sp.degree(g, x))
    info = dict(factor=(str(g) if dg <= 2 else f"<deg {dg}>"), deg=dg, mult=int(m))
    if m == 1:
        info.update(b=None, alpha="1 (simple pole)", log=True)
        return info
    K, f = laurent_at_factor(s, t, g, 2, x, 1)
    b = NumberField.as_rational(f[0])
    if b is None:
        info.update(b="IRRATIONAL (varies over conjugates)", out_of_scope=True, log=None)
        return info
    coef, msq = sqrt_rational(1 + 4*b)
    info.update(b=str(b), sqrt_1p4b=(str(coef), msq))
    if msq == 1 and coef.is_integer and coef >= 0:
        N = int(coef)
        K, f = laurent_at_factor(s, t, g, 2, x, N + 1)
        info.update(N=N, log=_frobenius_log_field(K, f, b, N))
    else:
        info.update(N=None, log=False)
    return info


def _add(a, b):
    c = dict(a)
    for k, v in b.items():
        c[k] = c.get(k, 0) + v
    return {k: v for k, v in c.items() if v != 0 or k == 1}


def analyse(r, x):
    r = sp.cancel(sp.together(sp.sympify(r)))
    if r.free_symbols - {x}:
        return dict(verdict=INCONCLUSIVE, reason=f"free parameters {r.free_symbols - {x}}")
    if not r.is_rational_function(x):
        return dict(verdict=INCONCLUSIVE, reason="r is not rational (out of scope)")
    s, t = sp.fraction(r)
    try:
        sP, tP = sp.Poly(s, x, domain=QQ), sp.Poly(t, x, domain=QQ)
    except (sp.polys.polyerrors.PolynomialError, sp.polys.polyerrors.CoercionFailed):
        return dict(verdict=INCONCLUSIVE, reason="coefficients not in Q (out of scope)")
    if sP.is_zero:
        return dict(verdict=INCONCLUSIVE, reason="r = 0 (out of scope)")
    lc = tP.LC()
    sP, tP = sP*(1/lc), tP*(1/lc)
    ord_inf = tP.degree() - sP.degree()
    out = dict(ord_inf=int(ord_inf), deg_s=int(sP.degree()), deg_t=int(tP.degree()), factors=[])
    facs = [(sp.Poly(g, x, domain=QQ).monic(), m) for g, m in sp.factor_list(tP)[1]]
    if any(m > 2 for _, m in facs) or ord_inf < 2:
        out.update(verdict=INCONCLUSIVE, reason="out of scope: a pole of order > 2 or ord_inf < 2 (not Fuchsian)")
        return out
    S, T = sP.as_expr(), tP.as_expr()
    for g, m in facs:
        out["factors"].append(_local(S, T, g.as_expr(), m, x))
    # infinity
    if ord_inf > 2:
        inf_choices = [{1: sp.Integer(0)}, {1: sp.Integer(1)}]
        out["inf"] = dict(alpha="0 or 1", log=(ord_inf == 3))
    else:
        binf = sp.Rational(sP.LC())/sp.Rational(tP.LC())
        coef, msq = sqrt_rational(1 + 4*binf)
        inf_choices = [_add({1: sp.Rational(1, 2)}, {msq: sg*coef/2}) for sg in (1, -1)]
        # log at infinity: w = 1/x, reduced rt(w) = r(1/w)/w^4 has a double pole at w = 0
        w = sp.Symbol("w_inf")
        rt = sp.cancel(sp.together(r.subs(x, 1/w)/w**4))
        sw, tw = sp.fraction(rt)
        loc = _local(sp.expand(sw), sp.expand(tw), w, 2, w)
        out["inf"] = dict(b=str(binf), sqrt_1p4b=(str(coef), msq), log=loc.get("log"), N=loc.get("N"))
    if any(fi.get("out_of_scope") for fi in out["factors"]):
        out.update(verdict=INCONCLUSIVE, reason="out of scope: irrational local coefficient b on a factor")
        return out
    # case-1 necessary condition over all count combinations
    per_factor = []
    for fi, (g, m) in zip(out["factors"], facs):
        n = g.degree()
        if m == 1:
            per_factor.append([{1: sp.Integer(n)}])
            continue
        coef, msq = sp.Rational(fi["sqrt_1p4b"][0]), fi["sqrt_1p4b"][1]
        per_factor.append([_add({1: sp.Rational(n, 2)}, {msq: sp.Rational(2*k - n, 2)*coef}) for k in range(n + 1)])
    sums = {frozenset({1: sp.Integer(0)}.items())}
    for opts in per_factor:
        sums = {frozenset(_add(dict(sm), o).items()) for sm in sums for o in opts}
    cands = []
    for ai in inf_choices:
        for sm in sums:
            d = _add(ai, {k: -v for k, v in dict(sm).items()})
            if all(v == 0 for k, v in d.items() if k != 1):
                d1 = sp.Rational(d.get(1, 0))
                if d1.is_integer and d1 >= 0:
                    cands.append(int(d1))
    has_log = any(fi.get("log") for fi in out["factors"]) or bool(out["inf"].get("log"))
    out.update(log_point=has_log, case1_candidates=sorted(set(cands)), n_distinct_sums=len(sums))
    if not has_log:
        out.update(verdict=INCONCLUSIVE, reason="no logarithmic point: cases 2 and 3 are not excluded by this route")
    elif cands:
        out.update(verdict=INCONCLUSIVE, reason=f"case-1 candidate degree(s) d = {sorted(set(cands))[:8]} survive")
    else:
        where = [fi["factor"] for fi in out["factors"] if fi.get("log")] + (["infinity"] if out["inf"].get("log") else [])
        out.update(verdict=OBSTRUCTION, reason=f"log point(s) at roots of {where} exclude cases 2, 3; no d in Z>=0 "
                                              "over every count combination excludes case 1: G = SL(2)")
    return out


def numeric_poles(r, x, dps=30):
    """High-precision numeric finite poles, per irreducible factor (for the monodromy route)."""
    t = sp.fraction(sp.cancel(sp.together(r)))[1]
    cs = []
    for g, m in sp.factor_list(sp.Poly(t, x, domain=QQ))[1]:
        cs += [complex(c) for c in sp.Poly(g, x).nroots(n=dps, maxsteps=200)]
    return cs


# ----------------------------------------------------------------------------
# 2b' (AMENDMENT, post-failure; PREREG_ts2b_factor_route.md dc4f53e + 0dacd90)
# ----------------------------------------------------------------------------
# Lemma: with a log point, case 1 has at most ONE rational Riccati solution, and it lies in Q(x).
# Hence at every factor with RATIONAL exponents the same alpha is taken at all conjugate roots,
# theta = sum alpha_j g_j'/g_j is in Q(x), and P is a monic polynomial over Q: search it exactly.
def analyse_v2(r, x):
    import itertools
    import mr_kovacic as K
    base = analyse(r, x)
    base["route"] = "2b'"
    if "log_point" not in base:                       # out of scope in 2b's checks
        return base
    if not base["log_point"]:
        base.update(verdict=INCONCLUSIVE, reason="no logarithmic point: the uniqueness lemma does not apply")
        return base
    r = sp.cancel(sp.together(sp.sympify(r)))
    s, t = sp.fraction(r)
    tP = sp.Poly(t, x, domain=QQ)
    tP = tP*(1/tP.LC())
    facs = [(sp.Poly(g, x, domain=QQ).monic(), m) for g, m in sp.factor_list(tP)[1]]
    opts, irr_even, impossible = [], [], []
    for fi, (g, m) in zip(base["factors"], facs):
        n = g.degree()
        if m == 1:
            opts.append((g, [sp.Integer(1)]))
            continue
        coef, msq = sp.Rational(fi["sqrt_1p4b"][0]), fi["sqrt_1p4b"][1]
        if msq == 1:
            al = sorted({sp.Rational(1, 2) + coef/2, sp.Rational(1, 2) - coef/2})
            opts.append((g, al))
        elif n % 2 == 1:
            impossible.append(fi["factor"])            # Tr(alpha) in Q forces sum eps = 0: impossible, n odd
        else:
            irr_even.append((fi["factor"], n))
    if impossible:
        base.update(verdict=OBSTRUCTION, case1_tested=[],
                    reason=f"log point excludes cases 2, 3; irrational exponents at odd-degree factor(s) {impossible} "
                           "make case 1 impossible (trace argument): G = SL(2)")
        return base
    inf = base["inf"]
    if base["ord_inf"] > 2:
        inf_alphas = [sp.Integer(0), sp.Integer(1)]
    else:
        c, m = sp.Rational(inf["sqrt_1p4b"][0]), inf["sqrt_1p4b"][1]
        inf_alphas = sorted({sp.Rational(1, 2) + c/2, sp.Rational(1, 2) - c/2}) if m == 1 else []   # irrational: no integer d
    shift = sum(sp.Rational(n, 2) for _, n in irr_even)
    tested, blocked = [], []
    for choice in itertools.product(*[al for _, al in opts]):
        S = sum(ch*g.degree() for ch, (g, _) in zip(choice, opts)) + shift
        for ainf in inf_alphas:
            d = ainf - S
            if not (d.is_integer and d >= 0):
                continue
            d = int(d)
            if irr_even:
                blocked.append(dict(d=d, why=f"needs a non-symmetric pattern at {irr_even}"))
                continue
            theta = sum(ch*sp.diff(g.as_expr(), x)/g.as_expr() for ch, (g, _) in zip(choice, opts))
            T2 = sp.cancel(sp.together(2*theta))
            Q0 = sp.cancel(sp.together(sp.diff(theta, x) + theta**2 - r))
            eq = lambda P, T2=T2, Q0=Q0: sp.diff(P, x, 2) + T2*sp.diff(P, x) + Q0*P
            try:
                P = K._monic_poly_solution(eq, d, x)
            except K.Inconclusive as e:
                blocked.append(dict(d=d, why=str(e)))
                continue
            tested.append(dict(alphas=[str(a) for a in choice], alpha_inf=str(ainf), d=d,
                               P=(str(P) if P is not None else None)))
    base["case1_tested"] = tested
    base["case1_blocked"] = blocked
    found = [tt for tt in tested if tt["P"] is not None]
    if found:
        base.update(verdict=INCONCLUSIVE, reason=f"case 1 HOLDS: P of degree {found[0]['d']} found ({found[0]['P'][:80]}); "
                                                  "the Borel part is not graded by this route")
    elif blocked:
        base.update(verdict=INCONCLUSIVE, reason=f"case-1 candidate(s) not searchable: {blocked[:3]}")
    else:
        base.update(verdict=OBSTRUCTION,
                    reason=f"log point excludes cases 2, 3; all {len(tested)} symmetric case-1 candidates (d in Z>=0) "
                           "have NO monic P over Q (uniqueness lemma): case 1 impossible, G = SL(2)")
    return base
