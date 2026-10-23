"""Checks for toy_sec (so_section.h) against the closed-form Poincare map P(x0, y0) = (x0 - y0 + 1) e^{y0 - 1} on y = 1:
pointwise containment of P(x0(r), y0(r)) in x + C r + 1/2 H(r, r) + box for a 21 x 21 grid of r, plus the y component
(= 1 exactly on the section). Usage: toy_sec.py <output> <w>"""
import sys, mpmath as mp
mp.mp.dps = 60; mp.iv.dps = 60
out, wd = sys.argv[1], float(sys.argv[2]); w = mp.mpf(wd)
L = {l.split()[0]: l.split()[1:] for l in open(out) if l.strip() and not l.startswith("#")}
hs = float(L["HS"][0]); h01 = mp.mpf(0.3 * wd * hs); h10 = mp.mpf(0.6 * wd * hs)
iv = lambda a: [mp.iv.mpf([a[2 * k], a[2 * k + 1]]) for k in range(len(a) // 2)]
X, C, H, B = iv(L["X"]), iv(L["C"]), iv(L["H"]), iv(L["BOX"])
bad = 0; worst = 0
for p in range(21):
    for q in range(21):
        r1, r2 = mp.mpf(-1) + mp.mpf(p) / 10, mp.mpf(-1) + mp.mpf(q) / 10
        x0 = 1 + w * r1 + h01 * r1 * r2; y0 = w * r2 + h10 * r1 ** 2 / 2
        ex = [(x0 - y0 + 1) * mp.e ** (y0 - 1), mp.mpf(1)]
        for i in range(2):
            v = X[i] + C[2 * i] * r1 + C[2 * i + 1] * r2 + (H[4 * i] * r1 ** 2 + 2 * H[4 * i + 1] * r1 * r2 + H[4 * i + 3] * r2 ** 2) / 2 + B[i]
            if not (v.a <= ex[i] <= v.b): bad += 1
            if i == 0: worst = max(worst, float(v.b) - float(v.a))
import sympy as sp, itertools
R1, R2 = sp.symbols("r1 r2"); S_ = lambda v: sp.Float(mp.nstr(v, 60), 60)
X0 = 1 + S_(w) * R1 + S_(h01) * R1 * R2; Y0 = S_(w) * R2 + S_(h10) * R1 ** 2 / 2
Psi = [(X0 - Y0 + 1) * sp.exp(Y0 - 1), sp.Integer(1)]
K = iv(L["D2PSI"]); cbad = 0
for r1, r2 in itertools.product((-1, 1), repeat=2):
    for i in range(2):
        for a in range(2):
            for b in range(2):
                d = mp.mpf(str(sp.N(sp.diff(Psi[i], (R1, R2)[a], (R1, R2)[b]).subs({R1: r1, R2: r2}), 60)))
                k = K[4 * i + 2 * a + b]
                if not (k.a <= d <= k.b): cbad += 1
print("corner test of [D2Psi(R0)]: %s" % ("PASS" if cbad == 0 else "FAIL (%d)" % cbad))
print("section image containment over 441 r: %s ; max width (x) %.3e" % ("PASS" if bad == 0 else "FAIL (%d not contained)" % bad, worst))
