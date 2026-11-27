"""Control (ii) prerequisite: K_r(x, p_x) = 1/2 [Delta p_r^2 - Pr^2/Delta + r^2] (r = 5 + 4x, p_r = p_x/4, Delta = r^2 - 10 r + 9,
Pr = E (r^2 + 9) - 3 L) is a first integral of the beta = 0 reduced field (mn_s5_gate.mine) on the shell H = -1/2.
Exact symbolic check: the Poisson bracket {K_r, H} with p_y^2 eliminated by the shell, as a rational function, cancels to 0.
E and L are kept SYMBOLIC (so the identity holds for every level, in particular the registered one)."""
import sys, sympy as sp, json, time
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe"); import mn_s5_gate as G
t0 = time.time()
E, L = sp.symbols("E L", positive=True)
X, Y, gxx, gyy, V = G.mine(5, 3, 0, E, L)
PX, PY, W = sp.symbols("PXc PYc W")
H = (gxx * PX**2 + gyy * PY**2) / 2 + V
r = 5 + 4 * X; pr = PX / 4; Dl = r**2 - 10 * r + 9; Pr = E * (r**2 + 9) - 3 * L
K = (Dl * pr**2 - Pr**2 / Dl + r**2) / 2
PB = sp.diff(K, X) * sp.diff(H, PX) - sp.diff(K, PX) * sp.diff(H, X)       # K depends on (x, p_x) only
py2 = (-1 - gxx * PX**2 - 2 * V) / gyy                                       # the shell H = -1/2
PBs = PB.subs(PY**2, W).subs(W, py2)
num = sp.numer(sp.together(sp.expand(PBs)))
res = sp.simplify(sp.factor(num))
print("PB numerator on the shell simplifies to:", res, "  (%.0f s)" % (time.time() - t0))
json.dump(dict(identity_zero=bool(res == 0), seconds=time.time() - t0), open("carter_check.json", "w"))

# must-fire mutations (each must NOT cancel to 0)
K2 = (Dl * pr**2 - Pr**2 / Dl + 2 * r**2) / 2
PB2 = (sp.diff(K2, X) * sp.diff(H, PX) - sp.diff(K2, PX) * sp.diff(H, X)).subs(PY**2, W).subs(W, py2)
m1 = sp.simplify(sp.factor(sp.numer(sp.together(sp.expand(PB2)))))
m2 = sp.simplify(sp.factor(sp.numer(sp.together(sp.expand(PB)))))      # no shell substitution
print("must-fire 1 (mass term doubled) cancels to 0:", m1 == 0, "| must-fire 2 (no shell substitution) cancels to 0:", m2 == 0)
json.dump(dict(identity_zero=bool(res == 0), mustfire_mass_nonzero=bool(m1 != 0), mustfire_noshell_nonzero=bool(m2 != 0), seconds=time.time() - t0), open("carter_check.json", "w"))
