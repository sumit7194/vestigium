"""Real equatorial motion of TS delta=2 (ansatz's WP components, sigma=1) at a level (E, L, mu^2).

On y = 0, p_y = 0:  xdot^2 = g^xx * F(x),  F(x) = -mu^2 - (g^TT E^2 - 2 g^Tphi E L + g^phiphi L^2)  (p_T = -E, p_phi = L).
Motion is allowed where g^xx F >= 0. This reports the allowed real x-intervals outside the ring (x > x_ring > 1) and
classifies each as BOUND (two turning points), PLUNGE (reaches the ring), ESCAPE (to infinity), or none.
Exact rational inputs; the root finding is numeric (mpmath, 50 digits) on the exact numerator of F.

Usage: python ts_bound_orbits.py P1|P2 E L mu2        (rationals as a/b)
"""
import os, sys
import sympy as sp
import mpmath as mp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
mp.mp.dps = 50


def ring(p):
    X = sp.Symbol("x")
    return max(float(sp.N(r, 30)) for r in sp.Poly(p**2*X**4 + 2*p*X**3 - 2*p*X - 1, X).real_roots())


def analyse(P, E, L, mu2):
    import mr_ts2 as T2
    p = sp.Rational(3, 5) if P == "P1" else sp.Rational(4, 5)
    inv = T2.load_wp(T2.TS_P1 if P == "P1" else T2.TS_P2, 1)
    x, y = T2.X, T2.Y
    at0 = {k: sp.factor(sp.together(v.subs(y, 0))) for k, v in inv.items()}
    gTT, gTp, gpp, gxx = (at0[k] for k in ("tt", "tphi", "phiphi", "xx"))
    F = sp.together(-mu2 - (gTT*E**2 - 2*gTp*E*L + gpp*L**2))
    W = sp.together(gxx*F)                                    # xdot^2 as a rational function of x
    num, den = sp.fraction(sp.factor(W))
    xr = ring(p)
    crit = set()                                              # exact real-root isolation, factor by factor over Q
    for f in (num, den):
        for fac, _ in sp.factor_list(sp.Poly(f, x))[1]:
            for r in sp.Poly(fac, x).real_roots():
                v = float(sp.N(r, 30))
                if v > float(xr) + 1e-12:
                    crit.add(v)
    crit = sorted(crit)
    Wf = sp.lambdify(x, W, "mpmath")
    pts = [float(xr)] + crit + [float("inf")]
    allowed = []
    for a, b in zip(pts[:-1], pts[1:]):
        mid = (a + b)/2 if b != float("inf") else max(2*a, a + 10)
        if Wf(mp.mpf(mid)) > 0:
            kind = ("PLUNGE" if a == float(xr) else "") + ("ESCAPE" if b == float("inf") else "")
            allowed.append(dict(interval=(a, b), kind=kind or "BOUND"))
    return dict(P=P, p=str(p), E=str(E), L=str(L), mu2=str(mu2), E_over_mu=float(E/sp.sqrt(mu2)),
                ring=float(xr), turning_points=crit, allowed=allowed)


if __name__ == "__main__":
    P = sys.argv[1]; E, L, mu2 = (sp.Rational(a) for a in sys.argv[2:5])
    import json; print(json.dumps(analyse(P, E, L, mu2), indent=1))
