"""S5 re-run at A-K20's exact (FINAL, TheBridge 0e42f37) parameters: F5-R (89, 80, 13394411/1186380) and
C0 (1, 9/10, (19/20)/(19/100)^(3/2)), both at E = 19/20, L_z = 3M; plus the Kerr limits. Same method as mn_s5_gate."""
import json, random, sys
import sympy as sp, mpmath as mp
import mn_s5_gate as G
mp.mp.dps = 70
E = sp.Rational(19, 20)
pts = {"F5R": (89, 80, sp.Rational(13394411, 1186380)),
       "C0": (1, sp.Rational(9, 10), sp.Rational(19, 20) / (sp.Rational(19, 100))**sp.Rational(3, 2))}
rnd = random.Random(20261020); out = {}
for tag, (M, aa, beta) in list(pts.items()) + [(t + "_KERR", (v[0], v[1], 0)) for t, v in pts.items()]:
    L = 3 * sp.nsimplify(M)
    X, Y, gxx, gyy, V = G.mine(M, aa, beta, E, L)
    bgxx, bgyy, bV = G.bridge(M, aa, beta, E, L)
    fm = sp.lambdify((X, Y), [gxx, gyy, V], "mpmath"); fb = sp.lambdify((G.BR.x, G.BR.y), [bgxx, bgyy, bV], "mpmath")
    worst = 0.0
    for _ in range(12):
        xv = mp.mpf(rnd.randint(1100, 6000)) / 1000 if M == 1 else mp.mpf(rnd.randint(2000, 6000)) / 1000
        yv = mp.mpf(rnd.randint(50, 950)) / 1000
        pxv = mp.mpf(rnd.randint(-5000, 5000)) / 100; pyv = mp.mpf(rnd.randint(-5000, 5000)) / 100
        m = fm(xv, yv); b = fb(xv, yv)
        Hm = (m[0]*pxv**2 + m[1]*pyv**2)/2 + m[2]; Hb = (b[0]*pxv**2 + b[1]*pyv**2)/2 + b[2]
        worst = max(worst, float(abs(Hm - Hb) / max(abs(Hb), mp.mpf(10)**-30)))
    out[tag] = dict(L=str(L), worst_rel_H=worst, PASS=worst <= 1e-45); print(tag, out[tag], flush=True)
out["GATE"] = all(v["PASS"] for v in out.values() if isinstance(v, dict))
json.dump(out, open("mn_s5_gate_ak20.json", "w"), indent=1); print("S5 (A-K20 params)", "PASS" if out["GATE"] else "FAIL")
