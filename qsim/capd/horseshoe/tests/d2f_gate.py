"""D2f gate: CAPD's full second derivatives of the 8-D MN field (d2f_gate) at 30 random exact points in the MN domain
(on the invariant manifold, p from a plausible range) must contain sympy's EXACT second derivatives (evaluated at
50 digits). The full Hessian is printed symmetric by construction (one coefficient per pair), so symmetry is checked on
the sympy side."""
import sys, random, subprocess, mpmath as mp, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_codegen as CG, mn_codegen8 as C8
mp.mp.dps = 50
F, p8 = C8.build8()
vals = {CG.k: 39, CG.al: sp.Rational(-5, 8), CG.beta: sp.Rational(13394411, 1186380), CG.E: sp.Rational(19, 20), CG.L: 267}
F = [e.subs(vals) for e in F]; Z = C8.STATE
auxf = sp.lambdify([CG.x, CG.y], [e.subs(vals) for e in p8["aux"]], "mpmath")
rnd = random.Random(20261024); pts = []
for _ in range(30):
    x, y = sp.Rational(rnd.randint(19500, 36500), 10000), sp.Rational(rnd.randint(-2000, 2000), 10000)
    a = auxf(mp.mpf(x.p) / x.q, mp.mpf(y.p) / y.q)
    pts.append([x, y, sp.Rational(rnd.randint(-1000, 1000), 10), sp.Rational(rnd.randint(-900, 900), 10)] + [sp.Rational(mp.nstr(v, 45)) for v in a])
inp = "".join(" ".join(mp.nstr(mp.mpf(v.p) / v.q, 45) for v in p) + "\n" for p in pts)
out = subprocess.run(["/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests/d2f_gate"], input=inp, capture_output=True, text=True).stdout.split("\n")
H = [[[sp.diff(F[i], Z[j], Z[k]) for k in range(8)] for j in range(8)] for i in range(8)]
bad = 0; n = 0; asym = 0
for p, line in zip(pts, out):
    v = line.split()[1:]; sub = dict(zip(Z, p)); idx = 0
    for i in range(8):
        for j in range(8):
            for k in range(8):
                lo, hi = mp.mpf(v[2 * idx]), mp.mpf(v[2 * idx + 1]); idx += 1
                ex = mp.mpf(str(sp.N(H[i][j][k].subs(sub), 50))); n += 1
                if not (lo <= ex <= hi): bad += 1
                if j < k and sp.N(H[i][j][k].subs(sub) - H[i][k][j].subs(sub), 40) != 0: asym += 1
print("D2f gate: %d entries checked at %d points, %d not enclosed; sympy asymmetry count %d -> %s" % (n, len(pts), bad, asym, "PASS" if bad == 0 and asym == 0 else "FAIL"))
