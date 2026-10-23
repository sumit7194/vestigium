"""Lift containment test (SECOND_ORDER_STEP_DESIGN.md §2a): for 1000 random r in R0 = [-1,1]^2 plus the 4 corners,
the 50-digit lift L(r) from the ORIGINAL formulas (mn_codegen.build: g^xx, g^yy, V at y = 0; the exponential aux
formulas of mn_codegen8) must lie in x0 + C0 r + 1/2 H0(r, r) + E3 componentwise (mn_lift_so output).
Usage: mn_lift_so.py <mn_lift_so output> <h p/q>"""
import sys, random, mpmath as mp, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_codegen as CG, mn_codegen8 as C8
mp.mp.dps = 50
out, hq = sys.argv[1], sp.Rational(sys.argv[2])
vals = {CG.k: 39, CG.al: sp.Rational(-5, 8), CG.beta: sp.Rational(13394411, 1186380), CG.E: sp.Rational(19, 20), CG.L: 267}
X = CG.build(); p8 = C8.pieces()
gxx = sp.lambdify(CG.x, X["gxx"].subs(vals).subs(CG.y, 0), "mpmath"); gyy = sp.lambdify(CG.x, X["gyy"].subs(vals).subs(CG.y, 0), "mpmath")
V = sp.lambdify(CG.x, X["V"].subs(vals).subs(CG.y, 0), "mpmath")
aux = [sp.lambdify(CG.x, e.subs(vals).subs(CG.y, 0), "mpmath") for e in p8["aux"]]
cx, cp, h = sp.Rational(36419361737, 10**10), sp.Rational(60360992808, 10**10), hq
def L(r1, r2):
    x = mp.mpf(cx.p) / cx.q + r1 * mp.mpf(h.p) / h.q; px = mp.mpf(cp.p) / cp.q + r2 * mp.mpf(h.p) / h.q
    py = mp.sqrt((-1 - gxx(x) * px ** 2 - 2 * V(x)) / gyy(x))
    return [x, mp.mpf(0), px, py] + [f(x) for f in aux]
Ls = {l.split()[0]: l.split()[1:] for l in open(out) if l.strip() and not l.startswith("#")}
iv = lambda a: [mp.iv.mpf([a[2 * k], a[2 * k + 1]]) for k in range(len(a) // 2)]
mp.iv.dps = 50
X0, C0, H0, E3 = iv(Ls["X"]), iv(Ls["C"]), iv(Ls["H"]), iv(Ls["E3"])
rnd = random.Random(20261024)
pts = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(1000)] + [(-1, -1), (-1, 1), (1, -1), (1, 1)]
bad = 0; maxrel = 0
for r1, r2 in pts:
    r1, r2 = mp.mpf(r1), mp.mpf(r2); ex = L(r1, r2)
    for i in range(8):
        v = X0[i] + C0[2 * i] * r1 + C0[2 * i + 1] * r2 + (H0[4 * i] * r1 ** 2 + 2 * H0[4 * i + 1] * r1 * r2 + H0[4 * i + 3] * r2 ** 2) / 2 + E3[i]
        if not (v.a <= ex[i] <= v.b): bad += 1; print("NOT CONTAINED", i, mp.nstr(ex[i], 25), v) if bad < 5 else None
print("lift containment (h = %s): %d point-components checked, %d not contained -> %s" % (hq, 8 * len(pts), bad, "PASS" if bad == 0 else "FAIL"))
print("widths: E3 %s" % " ".join(mp.nstr(float(e.b) - float(e.a), 3) for e in E3))
