"""B15b G6 toys (the Bridge's point 5): for EVERY decision type, one synthetic input with a known THIN margin (must be
flagged) and one with a large margin (must NOT be flagged), plus the chord rule (B15b-2) and the replica bookkeeping.
A wrapper that never flags is indistinguishable from a broken one, so this must pass before G6 sees run data."""
import sys, numpy as np
import b15b_g6 as G
ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print("%-58s %s" % (name, "ok" if cond else "FAIL"))

# D1 Newton: residual just under tol vs far under tol
check("D1 thin: residual 0.99e-10 vs tol 1e-10, e_map 1e-12", G.d1_newton([1e-3, 0.99e-10], 1e-10, 1e-12)["iterations"][1]["thin"])
check("D1 thick: residual 1e-14 vs tol 1e-10, e_map 1e-13", not G.d1_newton([1e-3, 1e-14], 1e-10, 1e-13)["iterations"][1]["thin"])
check("D1 tol too tight flagged (tol 1e-10, e_map 2e-11)", G.d1_newton([1e-14], 1e-10, 2e-11)["tol_too_tight"])
# D2 saddle: lam_s just below 1 - 1e-6 vs clearly hyperbolic
Dthin = [[1.0 + 1e-3, 0], [0, 1 - 1.2e-6]]; Dthick = [[62.6, 0], [0, 1 / 62.6]]
check("D2 thin: lam_s = 1 - 1.2e-6 with dD 1e-7", G.d2_saddle(Dthin, [[1e-7] * 2] * 2)["thin"])
check("D2 thick: lam 62.6 / 0.016, dD 1e-10", not G.d2_saddle(Dthick, [[1e-10] * 2] * 2)["thin"])
check("D2 near-complex flagged (disc ~ 0)", G.d2_saddle([[1.0, 1e-4], [-1e-4, 1.0]], [[1e-6] * 2] * 2)["thin"])
# D4 existence: crossing at t ~ 1 - 1e-9 (thin) vs t = 0.5 (thick); near miss just outside
a, b = np.array([0.0, 0.0]), np.array([1.0, 0.0])
r = G.seg_decision(a, b, np.array([1 - 1e-9, -1.0]), np.array([1 - 1e-9, 1.0]), 1e-10, 1e-10)
check("D4 thin: crossing at t = 1 - 1e-9, errors 1e-10", r["strict"] and r["thin"])
r = G.seg_decision(a, b, np.array([0.5, -1.0]), np.array([0.5, 1.0]), 1e-10, 1e-10)
check("D4 thick: crossing at t = 0.5", r["strict"] and not r["thin"])
r = G.seg_decision(a, b, np.array([1 + 1e-9, -1.0]), np.array([1 + 1e-9, 1.0]), 1e-10, 1e-10)
check("D4 near miss: t = 1 + 1e-9 is flagged", (not r["strict"]) and r["near_miss"])
r = G.seg_decision(a, b, np.array([0.5, -1.0]), np.array([0.5, 1.0]), 1e-10, 1e-10)
r2 = G.seg_decision(a, b, np.array([0.0, 1.0]), np.array([1.0, 1.0 + 1e-12]), 1e-10, 1e-10)
check("D4 near-parallel: dt grows like 1/sin(angle)", r2.get("parallel") or r2["dt"] > 1e3 * r["dt"])
# D4 vertex zero-count risk: S passes exactly through a shared vertex of U, just missing both segments by rounding
U = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]]); S = np.array([[1.0 + 1e-13, -1.0], [1.0 + 1e-13, 1.0]])
v = G.vertex_risk(U, S, 0, 1e-12, 1e-12); check("D4 vertex: extended >= strict counted near a vertex", v["extended"] >= 1)
Sfar = np.array([[0.5, -1.0], [0.5, 1.0]]); v2 = G.vertex_risk(U, Sfar, 0, 1e-12, 1e-12)
check("D4 vertex thick: interior crossing, no zero-count risk", (not v2["zero_count_risk"]) and v2["strict"] == 1)
Send = np.array([[2.0 + 1e-13, -1.0], [2.0 + 1e-13, 1.0]]); v3 = G.vertex_risk(U, Send, 0, 1e-12, 1e-12)
check("D4 arc end: a miss just past the end is a zero-count risk", v3["zero_count_risk"])
# D6 angle: 0.01 + 1e-9 vs 0.5
check("D6 thin: angle 0.01 + 1e-9, errors 1e-10 / length 1e-2", G.d6_angle(0.01 + 1e-9, 1e-10, 1e-2, 1e-10, 1e-2)["thin"])
check("D6 thick: angle 0.5", not G.d6_angle(0.5, 1e-10, 1e-2, 1e-10, 1e-2)["thin"])
# D7 red flag: angle ~ 10 theta_floor vs far above
check("D7 thin: angle = 10 floor + 1e-12", G.d7_redflag(1e-3 + 1e-12, 1e-4, 1e-11, 1e-12)["thin"])
check("D7 thick: angle 100x the threshold", not G.d7_redflag(0.1, 1e-4, 1e-11, 1e-12)["thin"])
# D8 with B15b-2
check("D8 chord-only accept -> UNRESOLVED", G.d8_connection([dict(accepted=True, thin=False, on_chord=True)])["outcome"].startswith("UNRESOLVED"))
check("D8 non-chord accept -> CONNECTION", G.d8_connection([dict(accepted=True, thin=False, on_chord=False), dict(accepted=True, thin=False, on_chord=True)])["outcome"] == "CONNECTION")
check("D8 none -> NO CONNECTION", G.d8_connection([dict(accepted=False, thin=False, on_chord=False)])["outcome"] == "NO CONNECTION")
# Replica: chord bookkeeping on a synthetic map with a known drop
calls = []
def P(w, n=1):
    calls.append(tuple(w)); return None if 1.42 < w[0] < 1.48 else (np.array([w[0] * 1.5, w[1]]), 1.0)
def Pinv(w): return np.array([w[0] / 1.5, w[1]])
out, meta, drops = G.arcs_replica(P, Pinv, [0.0, 0.0], [1.0, 0.0], 3.0, forward=True, K=2, eps=0.5, n0=6, dmax=10.0)
check("replica: records drops", len(drops[1]) >= 1)
cm = [G.chord_mask(m, drops) for m in meta]
check("replica: a chord appears only AFTER the drop level", all(not c.any() for c, m in zip(cm, meta) if m["k"] == 0) and any(c.any() for c, m in zip(cm, meta) if m["k"] > 0 and m["sign"] == 1))
print("G6 TOYS", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
