# symbolic-algebra check: on the manifold, 8-D field components 0-3 equal the 4-D field, 4-7 equal d/dt of a(x,y) etc.
import sys, random, mpmath as mp, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_codegen as CG, mn_codegen8 as C8
mp.mp.dps = 50
F8, p = C8.build8(); F4 = CG.build()["field"]
vals = {CG.k: 39, CG.al: sp.Rational(-5, 8), CG.beta: sp.Rational(13394411, 1186380), CG.E: sp.Rational(19, 20), CG.L: 267}
Z4 = [CG.x, CG.y, CG.PX, CG.PY]
f4 = sp.lambdify(Z4, [sp.sympify(e).subs(vals) for e in F4], "mpmath")
f8 = sp.lambdify(C8.STATE, [e.subs(vals) for e in F8], "mpmath")
aux = sp.lambdify([CG.x, CG.y], [e.subs(vals) for e in p["aux"]], "mpmath")
# d/dt aux along the 4-D flow = grad(aux) . (xdot, ydot)
gaux = sp.lambdify([CG.x, CG.y], [[sp.diff(e.subs(vals), v) for v in (CG.x, CG.y)] for e in p["aux"]], "mpmath")
rnd = random.Random(7); worst = 0
for _ in range(8):
    X, Y = mp.mpf(rnd.uniform(1.5, 4)), mp.mpf(rnd.uniform(-0.3, 0.3)); PXv, PYv = mp.mpf(rnd.uniform(-50, 50)), mp.mpf(rnd.uniform(-50, 50))
    s4 = f4(X, Y, PXv, PYv); A_ = aux(X, Y); s8 = f8(X, Y, PXv, PYv, *A_); G_ = gaux(X, Y)
    ref = list(s4) + [G_[i][0]*s4[0] + G_[i][1]*s4[1] for i in range(4)]
    rel = max(abs(s8[i] - ref[i])/max(abs(ref[i]), mp.mpf(1e-30)) for i in range(8)); worst = max(worst, rel)
print("max relative deviation 8-D vs (4-D field, chain rule), 8 points, 50 digits:", mp.nstr(worst, 3))
