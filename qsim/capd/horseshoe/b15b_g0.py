"""B15b gate G0 (registered): field accuracy in double along the real excursion.
States: 100 = 25 per forward orbit of orbits.json (all 4 forward W^u orbits of the G4 rule; the registration says
"two orbits"; using all four covers both s and both branches and is fixed here, before this first ran), at equal
(x, y)-arc length along each orbit's continuous trajectory (every return leg, and a plunge leg up to 0.999 t_c), keeping
x - 1 >= 0.05. Trajectory states come from kerr_rs's kerr_state_at.
Compared at each state (the same double inputs): the generated double field of kerr_rs (kerr_field), of kerr_p
(kerr_field) and MNFlow's lambdified field, against 50-digit mpmath evaluation of the same sympy field expressions.
Criterion: |df_i| <= 1e-12 ||f_ref||_inf, every component at every state, for all three. Componentwise relative
errors are reported too (no criterion). Writes horseshoe_results/kerr/b15b_gates/G0.json; exit 0 iff PASS."""
import ctypes, json, sys, time, numpy as np, sympy as sp, mpmath as mp
from pathlib import Path
import kerr_compiled as K, mn_numerics as MNN, mn_codegen as CG

OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "kerr" / "b15b_gates"
ORB = json.loads((OUT / "orbits.json").read_text())
fr, fc = K.CompiledFlow(K.RUST), K.CompiledFlow(K.CPP)
for g in (fr, fc): g.lib.kerr_field.argtypes = [ctypes.POINTER(ctypes.c_double)] * 2
kerr = MNN.MNFlow(89, 80, 0, sp.Rational(49, 50), sp.Rational(445, 2))
PAR = {CG.k: 39, CG.al: sp.Rational(-5, 8), CG.beta: 0, CG.E: sp.Rational(49, 50), CG.L: sp.Rational(445, 2)}
field_mp = sp.lambdify((CG.x, CG.y, CG.PX, CG.PY), [e.subs(PAR) for e in CG.build()["field"]], "mpmath")
mp.mp.dps = 50


def state_at(w, t):
    o = (ctypes.c_double * 4)(); r = fr.lib.kerr_state_at(float(w[0]), float(w[1]), float(t), 1.0, o)
    if r != 1: raise RuntimeError("kerr_state_at %d" % r)
    return np.array(o[:])


t0 = time.time(); states = []
for orb in [o for o in ORB["orbits"] if o["kind"] == "P"]:
    its = orb["iterates"]; legs = [(its[i]["w"], its[i + 1]["T"]) for i in range(len(its) - 1)]
    pl = [p for p in ORB["plunges"] if p["kind"] == "P" and tuple(p["start"][:2]) == tuple(its[-1]["w"])]
    if pl: legs.append((its[-1]["w"], 0.999 * pl[0]["t_c"]))
    grid = []                                                  # (leg, t, state)
    for li, (w, T) in enumerate(legs):
        for t in np.linspace(T / 400, T, 400): grid.append((li, t, state_at(w, t)))
    xy = np.array([g[2][:2] for g in grid]); arc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))])
    for target in np.linspace(0, arc[-1], 25, endpoint=False) + arc[-1] / 50:
        j = int(np.searchsorted(arc, target)); j = min(max(j, 1), len(grid) - 1)
        li, ta, _ = grid[j - 1]; lb, tb, _ = grid[j]
        t = ta + (tb - ta) * (target - arc[j - 1]) / (arc[j] - arc[j - 1]) if li == lb else tb
        s = state_at(legs[lb][0], t)
        if s[0] - 1 >= 0.05: states.append(s)
print("G0: %d states, x in [%.4f, %.4f]" % (len(states), min(s[0] for s in states), max(s[0] for s in states)), flush=True)
worst = {"rust": 0.0, "c++": 0.0, "MNFlow": 0.0}; rows = []
for s in states:
    ref = np.array([float(v) for v in field_mp(*[mp.mpf(float(v)) for v in s])]); nrm = np.max(np.abs(ref))
    refm = field_mp(*[mp.mpf(float(v)) for v in s])
    got = {}
    for name, g in (("rust", fr), ("c++", fc)):
        i4, o4 = (ctypes.c_double * 4)(*s), (ctypes.c_double * 4)(); g.lib.kerr_field(i4, o4); got[name] = list(o4)
    got["MNFlow"] = [float(v) for v in kerr._f(*s)]
    row = dict(state=s.tolist(), norm=nrm)
    for name, v in got.items():
        d = [float(abs(mp.mpf(v[i]) - refm[i])) for i in range(4)]
        row[name] = dict(abs_over_norm=max(d) / nrm, comp_rel=[di / max(abs(float(refm[i])), 1e-300) for i, di in enumerate(d)])
        worst[name] = max(worst[name], max(d) / nrm)
    rows.append(row)
ok = all(v <= 1e-12 for v in worst.values())
for n, v in worst.items(): print("G0 %-7s worst |df|/||f|| = %.3e" % (n, v))
print("G0 %s (%.0f s)" % ("PASS" if ok else "FAIL", time.time() - t0))
(OUT / "G0.json").write_text(json.dumps(dict(worst=worst, verdict="PASS" if ok else "FAIL", n=len(states), rows=rows), indent=1, default=float))
sys.exit(0 if ok else 1)
