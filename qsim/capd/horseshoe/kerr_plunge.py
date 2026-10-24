"""B15b-1 plunge certificate (registered; conventions in B15B_KERR_CONVENTIONS.md; usable because G0b-field and G0c PASSED,
822fe6e). Called by kerr_compiled on a library return of -2 (step-size collapse). Certifies "no return" for that call,
or raises MapCheckFailed. Scope: P with n = 1 and Pinv. The frozen constructor calls P only with n = 1 in B15. A collapse
inside an n > 1 call has a reset start state the certifier does not see, so it is not certified: it raises.

Certificate (all in exact rationals except the second, independent interval certifier):
  constants  exactly from the call's start (x0, 0, px0, py0 = the lifted double the library integrated):
             mu^2 = -2 H(start), Q(start) (Carter, BL form), E, L, a = 80, M = 89, r+ = 128.
  position   r_c = M + k x_c from the collapse state; r1 = M + k (x_c + delta), pushed OUT by delta.
  direction  dr/dt along the integrated flow < 0 at the collapse (sign * k * dH/dp_x, exact at the collapse state).
  (i)        R(r) > 0 on [r+, r1]: (a) sympy Poly.count_roots == 0 on the closed interval and R(r+) > 0 (exact);
             (b) mpmath.iv bisection, every leaf's interval value > 0, leaves no narrower than 2^-40 of the interval.
  (ii)       no section crossing before the horizon: Lambda <= (r1 - r+) / sqrt(min R), with min R from (b);
             |y_c| > Lambda sqrt(Q + a^2 |E^2 - mu^2|) + delta.
  delta      delta = max(delta_floor, 10 x measured) where measured comes from a recompute of the same call at rtol =
             atol = 1e-14 (it must also give -2), and from kerr_state_at at 0.99 and 0.999 x min(t_c, t_c') for both
             tolerances: d = max(|dx|, |dy|) (|dr|/k = |dx|). Growth d(0.999)/d(0.99) > 10 fails. The registered
             floor is max(1e-6, 100 x the G4-measured state error), passed in as delta_floor.
"""
import ctypes
import sympy as sp
import mpmath
import mn_codegen as CG

_x, _y, _px, _py = CG.x, CG.y, CG.PX, CG.PY
PAR = {CG.k: sp.Integer(39), CG.al: sp.Rational(-5, 8), CG.beta: sp.Integer(0), CG.E: sp.Rational(49, 50), CG.L: sp.Rational(445, 2)}
K, M, A, E, L = sp.Integer(39), sp.Integer(89), sp.Integer(80), sp.Rational(49, 50), sp.Rational(445, 2)
RP = M + K                                                     # r+ = M + sqrt(M^2 - a^2) = 128
_H = None


def _ham():
    global _H
    if _H is None:
        H = CG.build()["H"].subs(PAR); H = H.subs({e: 1 for e in H.atoms(sp.exp)})
        _H = (H, sp.diff(H, _px))
    return _H


class NotCertified(Exception):
    pass


def constants(x0, px0, py0):
    """exact mu^2 and Q of the orbit through the doubles (x0, 0, px0, py0)"""
    H, _ = _ham(); pt = {_x: sp.Rational(x0), _y: 0, _px: sp.Rational(px0), _py: sp.Rational(py0)}
    mu2 = -2 * H.xreplace(pt)
    Q = sp.Rational(py0)**2                                    # at y = 0: Q = (1 - y^2) p_y^2 + y^2 [...] = p_y^2
    return mu2, Q


def radial_poly(mu2, Q):
    r = sp.Symbol("r"); Dl = r**2 - 2 * M * r + A**2
    return sp.Poly(sp.expand((E * (r**2 + A**2) - A * L)**2 - Dl * (mu2 * r**2 + (L - A * E)**2 + Q)), r)


def iv_positive(P, lo, hi, depth=40):
    """mpmath.iv bisection: True and the minimum lower bound if every leaf of [lo, hi] has interval value > 0"""
    iv = mpmath.iv; iv.prec = 200
    co = [iv.mpf([sp.Rational(c).p, sp.Rational(c).p]) / iv.mpf([sp.Rational(c).q, sp.Rational(c).q]) for c in P.all_coeffs()]
    def ev(I):
        v = iv.mpf(0)
        for c in co: v = v * I + c
        return v
    lo_i, hi_i = iv.mpf([lo.p, lo.p]) / iv.mpf([lo.q, lo.q]), iv.mpf([hi.p, hi.p]) / iv.mpf([hi.q, hi.q])
    stack = [(iv.mpf([lo_i.a, hi_i.b]), 0)]; minlo = None
    while stack:
        I, d = stack.pop(); v = ev(I)
        if v.a > 0:
            minlo = v.a if minlo is None else min(minlo, v.a); continue
        if d >= depth: return False, None
        m = I.mid; stack += [(iv.mpf([I.a, m.b]), d + 1), (iv.mpf([m.a, I.b]), d + 1)]
    return True, minlo


def certify(flow, kind, w, collapse, sign, delta_floor):
    """kind 'P' (n = 1) or 'Pinv'; collapse = (x, y, px, py, t) from kerr_collapse; sign +1 forward, -1 reversed.
    Returns the certificate record, or raises NotCertified"""
    x0, px0 = float(w[0]), float(w[1]); py0 = flow.lib.kerr_py(x0, px0)
    xc, yc, pxc, pyc, tc = collapse
    rec = dict(kind=kind, start=(x0, px0, py0), collapse=tuple(collapse))
    # delta measured at the plunge: the same call at 1e-14, then states at two common times for both tolerances
    tol = flow.tol; out = (ctypes.c_double * 7)(); c2 = (ctypes.c_double * 5)()
    flow._tol(1e-14, 1e-14)
    try:
        r2 = flow.lib.kerr_P(x0, px0, 1, 0, 1e300, out) if kind == "P" else flow.lib.kerr_Pinv(x0, px0, 1e300, out)
        if r2 != -2: raise NotCertified("1e-14 recompute gave %d, not a collapse" % r2)
        flow.lib.kerr_collapse(c2); tmin = min(tc, c2[4])
        st = {}
        for tl in ((1e-14, 1e-14), tol):
            flow._tol(*tl)
            for f in (0.99, 0.999):
                o = (ctypes.c_double * 4)()
                if flow.lib.kerr_state_at(x0, px0, f * tmin, float(sign), o) != 1: raise NotCertified("kerr_state_at failed at %g t_min" % f)
                st[(tl, f)] = list(o)
    finally:
        flow._tol(*tol)
    d = {f: max(abs(st[(tol, f)][0] - st[((1e-14, 1e-14), f)][0]), abs(st[(tol, f)][1] - st[((1e-14, 1e-14), f)][1])) for f in (0.99, 0.999)}
    rec.update(d099=d[0.99], d0999=d[0.999], t_c=tc, t_c_1e14=c2[4])
    if d[0.999] > 10 * max(d[0.99], 1e-300): raise NotCertified("state difference grows > 10x between 0.99 and 0.999 t_min: %r" % d)
    delta = max(delta_floor, 10 * max(d.values())); rec["delta"] = delta
    # direction: inward along the integrated flow at the collapse (exact)
    _, dHdpx = _ham()
    xdot = dHdpx.xreplace({_x: sp.Rational(xc), _y: sp.Rational(yc), _px: sp.Rational(pxc), _py: sp.Rational(pyc)})
    if not (sign * xdot < 0): raise NotCertified("not moving inward at the collapse")
    mu2, Q = constants(x0, px0, py0); P = radial_poly(mu2, Q)
    r1 = M + K * (sp.Rational(xc) + sp.Rational(delta))
    rec.update(mu2=str(mu2), Q=str(Q), r1=float(r1))
    # (i) R > 0 on [r+, r1], twice
    if not (P.count_roots(RP, r1) == 0 and P.eval(RP) > 0): raise NotCertified("(i a) Sturm: R has a root in [r+, r1] or R(r+) <= 0")
    ok, minR = iv_positive(P, RP, r1)
    if not ok: raise NotCertified("(i b) interval: R not certified > 0 on [r+, r1]")
    # (ii) no section crossing before the horizon (Mino time)
    lam = (mpmath.mpf(float(r1 - RP)) * (1 + 1e-12)) / mpmath.sqrt(minR)
    vy = mpmath.sqrt(mpmath.mpf(float(Q + A**2 * abs(E**2 - mu2))) * (1 + 1e-12))
    rec.update(minR_lo=float(minR), Lambda_bound=float(lam), ydot_bound=float(vy), slack_y=float(abs(yc) - (lam * vy + delta)))
    if not (abs(yc) > lam * vy + delta): raise NotCertified("(ii) |y_c| not above the section-crossing bound")
    return rec
