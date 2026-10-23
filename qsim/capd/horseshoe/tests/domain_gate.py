"""Gate for gen/mn_field8.h mn8_domain: the 160-bit C++ enclosures of (B, g_phiphi) at 40 random exact rational
points in the orbit tube must contain the 60-digit mpmath values of the ORIGINAL (4-D codegen) expressions."""
import sys, random, subprocess, json, mpmath as mp, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_codegen as CG
mp.mp.dps = 60
X = CG.build()
vals = {CG.k: 39, CG.al: sp.Rational(-5, 8), CG.beta: sp.Rational(13394411, 1186380), CG.E: sp.Rational(19, 20), CG.L: 267}
fB = sp.lambdify([CG.x, CG.y], X["B"].subs(vals), "mpmath"); fg = sp.lambdify([CG.x, CG.y], X["gpp"].subs(vals), "mpmath")
rnd = random.Random(20261023)
pts = [(sp.Rational(rnd.randint(17000, 40000), 10000), sp.Rational(rnd.randint(-3000, 3000), 10000)) for _ in range(40)]
out = subprocess.run(["/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests/domain_gate"], input="".join("%s %s\n" % p for p in pts),
                     capture_output=True, text=True).stdout.split("\n")
ok = 0
for (x, y), line in zip(pts, out):
    v = [mp.mpf(t) for t in line.split()]
    ref = [fB(mp.mpf(x.p) / x.q, mp.mpf(y.p) / y.q), fg(mp.mpf(x.p) / x.q, mp.mpf(y.p) / y.q)]
    good = all(v[2 * i] <= ref[i] <= v[2 * i + 1] for i in range(2)); ok += good
    if not good: print("NOT ENCLOSED at", x, y, ref, v)
res = dict(points=len(pts), enclosed=ok, verdict="PASS" if ok == len(pts) else "FAIL")
print(json.dumps(res)); json.dump(res, open("/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/mn_smoke/domain_gate.json", "w"))
