"""A3 R3a cause checks (a) and (b); predictions in PREDICTIONS.md (35741e6), committed before this ran.
Diagnostics only, in double precision (not rigorous); they do not change A3's verdict.
  (a) linear true widths w1(t), w2(t) along the centre orbit's singular directions, with control a0 against the stored
      hull widths in mn_smoke/b17_cp_1e-7.txt
  (b) the polynomial / error split of every saved state st.t*, projected on u1(t_k), u2(t_k), with control b0
Usage: python checks.py  (writes a.json, b.json and prints the tables)"""
import sys, json, glob, os, re
import numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__)); RUN = os.path.dirname(HERE)
CP = "/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/mn_smoke/b17_cp_1e-7.txt"
W0 = 1e-7

# centre orbit + variational, exactly as tests/b17_checkpoints.py
f = MNN.MNFlow(89, 80, sp.Rational(13394411, 1186380), sp.Rational(19, 20), sp.Integer(267))
x0, px0 = 3.6419361737, 6.0360992808; py0 = f.py_of(x0, px0)
f0 = np.array(f._f(x0, 0.0, px0, py0), float); Hx, Hpx, Hpy = -f0[2], f0[0], f0[1]
D_in = np.array([[1, 0], [0, 0], [0, 1], [-Hx / Hpy, -Hpx / Hpy]])
sv = solve_ivp(f.rhs, (0, 806.5), np.concatenate([[x0, 0, px0, py0], np.eye(4).ravel()]), method="DOP853",
               rtol=1e-13, atol=1e-13, dense_output=True)


def frame(t):
    P = sv.sol(t)[4:].reshape(4, 4); M = P @ D_in
    U, S, Vt = np.linalg.svd(M, full_matrices=False)
    w = [float(np.abs(U[:, k] @ M).sum() * 2 * W0) for k in (0, 1)]
    return U, S, M, w, sv.sol(t)[:4]


# ---------------- (a)
stored = []
L = [l.split() for l in open(CP)]
for k in range(0, len(L), 7):
    if L[k][0] == "t": stored.append((float(L[k][1]), float(L[k + 4][0]), float(L[k + 4][1])))
a0 = []
for t, s1, s2 in stored:
    _, _, _, w, _ = frame(t)
    a0.append(dict(t=t, stored_w1=s1, lin_w1=w[0], r1=w[0] / s1, stored_w2=s2, lin_w2=w[1], r2=w[1] / s2))
a0_ok = all(abs(r["r1"] - 1) <= 0.05 and abs(r["r2"] - 1) <= 0.05 for r in a0)
curve = []
for lo, hi in ((276.0, 300.0), (780.0, 806.0)):
    for t in np.arange(lo, hi + 1e-9, 0.1):
        _, S, _, w, _ = frame(t); curve.append(dict(t=round(float(t), 4), w1=w[0], w2=w[1], s1=float(S[0]), s2=float(S[1])))
near = [c["w2"] for c in curve if abs(c["t"] - 793.2346) <= 0.5]
w2_cp = frame(793.2346306024658)[3][1]
late = [c for c in curve if c["t"] >= 780]
amin = min(late, key=lambda c: c["w2"])
A = dict(a0_ok=a0_ok, a0=a0, w2_at_793=w2_cp, w2_near_793_min=min(near), w2_near_793_max=max(near),
         late_min=amin, curve=curve)
json.dump(A, open(os.path.join(HERE, "a.json"), "w"), indent=1)
print("(a) control a0 (linear / stored hull, must be within 5%%): %s" % ("PASS" if a0_ok else "FAIL"))
for r in a0: print("   t %9.4f  w1 %.4e / %.4e = %.4f   w2 %.4e / %.4e = %.4f" % (r["t"], r["lin_w1"], r["stored_w1"], r["r1"], r["lin_w2"], r["stored_w2"], r["r2"]))
print("(a) w2(793.2346) = %.4e (stored 1.8955e-07); over 793.23 +/- 0.5: min %.4e max %.4e" % (w2_cp, min(near), max(near)))
print("(a) on [780, 806]: min w2 %.4e at t %.1f" % (amin["w2"], amin["t"]))
for c in curve:
    if abs(c["t"] * 2 - round(c["t"] * 2)) < 1e-6 and (c["t"] >= 784 or c["t"] <= 298) and abs(c["t"] - round(c["t"])) < 1e-6:
        print("   t %6.1f  w1 %.3e  w2 %.3e" % (c["t"], c["w1"], c["w2"]))

# ---------------- (b)
def fx(s): return float.fromhex(s)


def load_state(fn):
    tok = open(fn).read().split(); p = 0
    def iv():
        nonlocal p; lo, hi = fx(tok[p]), fx(tok[p + 1]); p += 2; return lo, hi
    steps, nextcp = tok[0], tok[1]; p = 2
    t = iv(); iv()
    x = np.array([np.mean(iv()) for _ in range(8)])
    C = np.array([[np.mean(iv()) for a in range(2)] for i in range(8)])
    H = np.array([[[np.mean(iv()) for b in range(2)] for a in range(2)] for i in range(8)])
    for _ in range(64): iv()
    for _ in range(8): iv()
    assert tok[p] == "EREP"; N = int(tok[p + 2]); p += 3
    G = np.empty((N, 8)); Gr = np.empty((N, 8))
    for j in range(N):
        for i in range(8):
            lo, hi = iv(); G[j, i] = (lo + hi) / 2; Gr[j, i] = (hi - lo) / 2
    assert tok[p] == "END"
    return dict(t=float(np.mean(t)), x=x, C=C, H=H, G=G, Gr=Gr)


rg = np.linspace(-1, 1, 401); R1, R2 = np.meshgrid(rg, rg)
rows = []
for fn in sorted(glob.glob(os.path.join(RUN, "st.t*")), key=lambda s: float(s.split(".t")[-1])):
    S_ = load_state(fn); t = S_["t"]; U, Sg, M, w, zc = frame(t)
    row = dict(file=os.path.basename(fn), t=t, N=len(S_["G"]), centre_err=float(np.abs(S_["x"][:4] - zc).max()))
    for k, nm in ((0, "u1"), (1, "u2")):
        u = np.concatenate([U[:, k], np.zeros(4)])
        l = u @ S_["C"]; Mq = np.einsum("i,iab->ab", u, S_["H"])
        v = l[0] * R1 + l[1] * R2 + (Mq[0, 0] * R1 ** 2 + 2 * Mq[0, 1] * R1 * R2 + Mq[1, 1] * R2 ** 2) / 2
        Wp = float(v.max() - v.min())
        WE = float(2 * (np.abs(S_["G"] @ u) + S_["Gr"] @ np.abs(u)).sum())
        row[nm] = dict(w_true=w[k], W_poly=Wp, W_E=WE, poly_over_true=Wp / w[k], ratio=(Wp + WE) / w[k],
                       excess=Wp + WE - w[k])
    rows.append(row)
b0_ok = all(r["centre_err"] <= 1e-6 and 0.8 <= r[nm]["poly_over_true"] <= 1.25 for r in rows for nm in ("u1", "u2"))
lw = [np.log(r["u2"]["W_E"]) for r in rows]
tot = lw[-1] - lw[0]; inc = [lw[k + 1] - lw[k] for k in range(len(lw) - 1)]
last = rows[-1]["u2"]
B = dict(b0_ok=b0_ok, rows=rows, logWE_total=tot, max_interval_share=max(inc) / tot if tot > 0 else None,
         last_interval_share=inc[-1] / tot if tot > 0 else None, last_jump=float(np.exp(inc[-1])),
         E_share_of_excess_at_last=last["W_E"] / last["excess"] if last["excess"] > 0 else None)
json.dump(B, open(os.path.join(HERE, "b.json"), "w"), indent=1)
print("(b) control b0 (centre within 1e-6, W_poly/w_true in [0.8, 1.25]): %s" % ("PASS" if b0_ok else "FAIL"))
print("   %-14s %9s %6s %9s | %10s %10s %10s %7s %7s" % ("file", "t", "N", "c_err", "w2_true", "W2_poly", "W2_E", "p/true", "ratio"))
for r in rows:
    q = r["u2"]; print("   %-14s %9.3f %6d %9.1e | %10.3e %10.3e %10.3e %7.3f %7.2f" % (r["file"], r["t"], r["N"], r["centre_err"], q["w_true"], q["W_poly"], q["W_E"], q["poly_over_true"], q["ratio"]))
print("(b) log W2_E growth 292 -> 792: %.3f; largest single-interval share %.2f; last interval (772 -> 792) share %.2f, jump x%.2f" %
      (tot, B["max_interval_share"], B["last_interval_share"], B["last_jump"]))
print("(b) at the last state: W2_E / excess = %.2f" % B["E_share_of_excess_at_last"])
