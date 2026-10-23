"""Checks for toys_so (SECOND_ORDER_STEP_DESIGN.md §4/§7) against the CLOSED-FORM flows at 50 digits:
 (1) corner test: the step's [D2Psi(R0)] (i, a, b) contains the exact D2Psi at the 4 corners of R0, where
     Psi(r) = phi_h(x(r)) and x(r) is the set's own parametrisation before the step;
 (2) pointwise containment: for a 21 x 21 grid of r, the exact phi_T(x0(r)) lies in x + C r + 1/2 H(r, r) + B re;
 (3) tightness: the set's width per component against the exact image's spread.
Usage: toys_so.py <output file> <A|B|C|D> <w>"""
import sys, mpmath as mp, itertools
mp.mp.dps = 50
out, toy, wd = sys.argv[1], sys.argv[2], float(sys.argv[3])
w = mp.mpf(wd)                                   # the SAME binary doubles the C++ side uses for the initial set
h11 = mp.mpf(0.6 * wd); h01 = mp.mpf(0.3 * wd)
def flow(x0, y0, t):
    E = mp.e ** (-t)
    if toy == "A": return E * (x0 + 5 * y0 * t) + y0 ** 2 * (E - E ** 2), y0 * E
    if toy == "B": return E * (x0 + 5 * y0 * t + y0 ** 3 * (1 - E ** 2) / 2), y0 * E
    if toy in "CE": return E * x0 + y0 ** 4 * (E - E ** 4) / 3, y0 * E
    return x0 * mp.e ** (-t + y0 * (1 - E)), y0 * E
def x0r(r1, r2):
    if toy in "AB": return 1 + w * r1, w * r2
    if toy == "C": return w * r1 + h11 * r2 ** 2 / 2, w * r2
    if toy == "E": return w * r1, w * r2 + h11 * r1 ** 2 / 2
    return 1 + w * r1 + h01 * r1 * r2, w * r2
L = {l.split()[0]: l.split()[1:] for l in open(out) if l.strip() and not l.startswith("#")}
iv = lambda a: [(mp.mpf(a[2 * k]), mp.mpf(a[2 * k + 1])) for k in range(len(a) // 2)]
ok_all = True
if "CORNER" in L:
    c = L["CORNER"]; t0 = mp.mpf(c[3]); h = mp.mpf(c[c.index("h") + 1])
    X = [mp.mpf((a + b) / 2) for a, b in iv(L["CX"])]
    C = [mp.mpf((a + b) / 2) for a, b in iv(L["CC"])]; H = [mp.mpf((a + b) / 2) for a, b in iv(L["CH"])]
    K = iv(L["CK"])
    import sympy as sp                                     # EXACT second derivatives (symbolic), evaluated at 60 digits
    R1, R2, TT = sp.symbols("r1 r2 t")
    def sflow(x0, y0, t):
        E = sp.exp(-t)
        if toy == "A": return E * (x0 + 5 * y0 * t) + y0 ** 2 * (E - E ** 2), y0 * E
        if toy == "B": return E * (x0 + 5 * y0 * t + y0 ** 3 * (1 - E ** 2) / 2), y0 * E
        if toy in "CE": return E * x0 + y0 ** 4 * (E - E ** 4) / 3, y0 * E
        return x0 * sp.exp(-t + y0 * (1 - E)), y0 * E
    S = lambda v: sp.Float(mp.nstr(v, 60), 60)
    xr = [S(X[j]) + S(C[2 * j]) * R1 + S(C[2 * j + 1]) * R2 + (S(H[4 * j]) * R1 ** 2 + 2 * S(H[4 * j + 1]) * R1 * R2 + S(H[4 * j + 3]) * R2 ** 2) / 2 for j in range(2)]
    Ps = sflow(xr[0], xr[1], TT)
    bad = 0
    for r1, r2 in itertools.product((-1, 1), repeat=2):
        for i in range(2):
            for a in range(2):
                for b in range(2):
                    dexpr = sp.diff(Ps[i], (R1, R2)[a], (R1, R2)[b])
                    d = mp.mpf(str(sp.N(dexpr.subs({R1: r1, R2: r2, TT: S(h)}), 60)))
                    lo, hi = K[4 * i + 2 * a + b]
                    if not (lo <= d <= hi): bad += 1; print("CORNER NOT CONTAINED", (r1, r2), i, a, b, mp.nstr(d, 15), mp.nstr(lo, 15), mp.nstr(hi, 15))
    print("corner test (step %s, h %s): %s" % (c[1], mp.nstr(h, 6), "PASS" if bad == 0 else "FAIL (%d)" % bad)); ok_all &= bad == 0
T = mp.mpf(L["FINAL"][1])
X = iv(L["X"]); C = iv(L["C"]); H = iv(L["H"]); B = iv(L["B"]); RE = iv(L["RE"])
mpi = mp.iv; mpi.dps = 50
I = lambda p: mpi.mpf([p[0], p[1]])
bad = 0; worst = [0, 0]; spread = [[None, None], [None, None]]
for p in range(21):
    for q in range(21):
        r1, r2 = mp.mpf(-1) + mp.mpf(p) / 10, mp.mpf(-1) + mp.mpf(q) / 10
        ex = flow(*x0r(r1, r2), T)
        for i in range(2):
            v = I(X[i]) + I(C[2 * i]) * r1 + I(C[2 * i + 1]) * r2 + (I(H[4 * i]) * r1 ** 2 + 2 * I(H[4 * i + 1]) * r1 * r2 + I(H[4 * i + 3]) * r2 ** 2) / 2 \
                + I(B[2 * i]) * I(RE[0]) + I(B[2 * i + 1]) * I(RE[1])
            if not (v.a <= ex[i] <= v.b): bad += 1
            worst[i] = max(worst[i], float(v.b) - float(v.a))
            lo, hi = spread[i]; spread[i] = [ex[i] if lo is None else min(lo, ex[i]), ex[i] if hi is None else max(hi, ex[i])]
print("pointwise containment at T=%s over 441 r: %s" % (mp.nstr(T, 6), "PASS" if bad == 0 else "FAIL (%d not contained)" % bad)); ok_all &= bad == 0
for i in range(2):
    print("component %d: pointwise set width (max over r) %.3e ; exact image spread %.3e" % (i, worst[i], float(spread[i][1] - spread[i][0])))
print("TOY", toy, "ALL PASS" if ok_all else "SOME FAIL")
