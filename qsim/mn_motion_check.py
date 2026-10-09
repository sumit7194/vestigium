"""Footnote for the MN records (bridge request, 2026-10-10): is the real motion along each registered MN particular
solution BOUND or PLUNGE-only? NUMERIC sign scan (mpmath, 30 digits, dense log grid in x > 1), not a proof, and not
used by any verdict (Morales-Ramis needs only the complex phase curve).

  equatorial (y = 0, p_y = 0):  xdot^2 = g^xx (-mu^2 - V0),  V0 = g^TT E^2 - 2 g^Tphi E L + g^phiphi L^2
  axial      (y = 1, L = 0):    xdot^2 = g^xx (-mu^2 + E^2 / f),  g^TT -> -1/f on the axis
Reports the allowed x-intervals (xdot^2 > 0) and the asymptotic mass M from g_tt ~ -(1 - 2M/x) (sigma = 1)."""
import json, os, sys
import numpy as np, sympy as sp, mpmath as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mr_mn_axis as MA
mp.mp.dps = 30


def allowed(W, lo=1.0 + 1e-9, hi=2000.0, n=6000):
    xs = [lo + (hi - lo) * (10 ** (k / n * np.log10(hi - lo + 1)) - 1) / (hi - lo) for k in range(n + 1)]
    xs = sorted(set([mp.mpf(lo)] + [mp.mpf(x) for x in xs if lo < x <= hi]))
    sgn = []
    for x in xs:
        try:
            v = W(x)
            sgn.append(1 if mp.re(v) > 0 else -1)
        except (ZeroDivisionError, ValueError):
            sgn.append(0)
    ints, start = [], None
    for x, s in zip(xs, sgn):
        if s > 0 and start is None:
            start = x
        if s <= 0 and start is not None:
            ints.append((float(start), float(x))); start = None
    if start is not None:
        ints.append((float(start), float("inf")))
    return ints


def classify(ints, hi=2000.0):
    out = []
    for a, b in ints:
        kind = ("ESCAPE" if b == float("inf") else "") + ("FROM-HORIZON" if a < 1.0 + 1e-3 else "")
        out.append(dict(interval=[a, b], kind=kind or "BOUND"))
    return out


def main():
    res = {}
    for p in ("p1", "p2"):
        fname, beta = MA.MN_POINTS[p]
        C, x, y = MA.load(fname)
        gtt, gtp, gpp, gxx = (C[k] for k in ("g_tt", "g_tphi", "g_phiphi", "g_xx"))
        M = sp.limit((gtt.subs(y, 0) + 1) * x / 2, x, sp.oo)
        # equatorial
        e = {k: sp.lambdify(x, v.subs(y, 0), "mpmath") for k, v in (("tt", gtt), ("tp", gtp), ("pp", gpp), ("xx", gxx))}
        for (E, L, mu2) in ((1, 0, 4), (1, 0, 9), (1, 1, 4)):
            def W(xv, E=E, L=L, mu2=mu2):
                a, b, c = e["tt"](xv), e["tp"](xv), e["pp"](xv)
                den = a * c - b * b
                gTT, gTp, gpp_ = c / den, -b / den, a / den
                return (1 / e["xx"](xv)) * (-mu2 - (gTT * E**2 - 2 * gTp * E * L + gpp_ * L**2))
            res[f"{p} equatorial {(E, L, mu2)}"] = dict(E_over_mu=E / mu2**0.5, mass_M=str(M), allowed=classify(allowed(W)))
        # axial (y = 1, L = 0): f = -g_tt
        f1 = sp.lambdify(x, (-gtt).subs(y, 1), "mpmath")
        gxx1 = sp.lambdify(x, gxx.subs(y, 1), "mpmath")
        for (E, mu2) in MA.LEVELS:
            W = lambda xv, E=E, mu2=mu2: (1 / gxx1(xv)) * (-mu2 + E**2 / f1(xv))
            res[f"{p} axial {(E, mu2)}"] = dict(E_over_mu=E / mu2**0.5, mass_M=str(M), allowed=classify(allowed(W)))
        print(p, "done", flush=True)
    json.dump(res, open(os.path.join(HERE, "mn_motion_check.json"), "w"), indent=1)
    for k, v in res.items():
        print(k, "E/mu=%.3f" % v["E_over_mu"], "M=", v["mass_M"], [(round(a["interval"][0], 3), round(a["interval"][1], 3), a["kind"]) for a in v["allowed"]])


if __name__ == "__main__":
    main()
