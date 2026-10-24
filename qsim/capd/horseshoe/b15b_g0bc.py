"""B15b gates G0b-field and G0c (registered; conventions in B15B_KERR_CONVENTIONS.md, committed before this first ran).
Exact rational arithmetic on the SOURCE expressions (mn_codegen.build) at beta = 0 and the exact B15 parameters:
  G0b-field: {Q, H} = 0 exactly at 20 random rational phase-space points (Carter's Q, textbook BL form, mu^2 = -2H);
             plus a sympy cancel() of the full bracket, reported.
  G0c:       (Sigma k dH/dp_x)^2 = R(M + k x) exactly at the same 20 points (fixes the sign of a, E/L and the time).
Points: numerators and denominators >= 64 bits, x in (1, 21), |y| < 1, p_x and p_y in (-100, 100); seed 20261024.
Mutation controls (must FAIL, else the gate is not discriminating): G0c with a -> -a; G0b-field with L -> 1.001 L in Q.
Writes horseshoe_results/kerr/b15b_gates/G0bc.json. Exit 0 iff both gates pass and both controls fail."""
import json, random, sys, time
from pathlib import Path
import sympy as sp
import mn_codegen as CG

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "horseshoe_results" / "kerr" / "b15b_gates"; OUT.mkdir(parents=True, exist_ok=True)
SEED = 20261024
x, y, px, py = CG.x, CG.y, CG.PX, CG.PY
PAR = {CG.k: sp.Integer(39), CG.al: sp.Rational(-5, 8), CG.beta: sp.Integer(0), CG.E: sp.Rational(49, 50), CG.L: sp.Rational(445, 2)}
k, al, Ev, Lv = 39, sp.Rational(-5, 8), sp.Rational(49, 50), sp.Rational(445, 2)
M = sp.Rational(k) * (1 + al**2) / (1 - al**2); a = -2 * k * al / (1 - al**2)
assert (M, a) == (89, 80) and M**2 - a**2 == k**2

t0 = time.time()
H = CG.build()["H"].subs(PAR)
assert not H.has(sp.exp) or all(e.args[0] == 0 for e in H.atoms(sp.exp)), "exp terms survive at beta = 0"
H = H.subs({e: 1 for e in H.atoms(sp.exp)})
assert not any(s.is_Pow and s.exp.is_Rational and s.exp.q != 1 for s in H.atoms(sp.Pow)), "non-rational power at beta = 0"
mu2 = -2 * H


def carter(Lq, aq):
    return (1 - y**2) * py**2 + y**2 * (aq**2 * (mu2 - Ev**2) + Lq**2 / (1 - y**2))


def bracket(F):
    return sp.diff(F, x) * sp.diff(H, px) - sp.diff(F, px) * sp.diff(H, x) + sp.diff(F, y) * sp.diff(H, py) - sp.diff(F, py) * sp.diff(H, y)


def g0c_expr(aq, Q):
    r = M + k * x; Sig = r**2 + aq**2 * y**2; Dl = r**2 - 2 * M * r + aq**2
    R = (Ev * (r**2 + aq**2) - aq * Lv)**2 - Dl * (mu2 * r**2 + (Lv - aq * Ev)**2 + Q)
    return (Sig * k * sp.diff(H, px))**2 - R


rnd = random.Random(SEED)
def rat(lo, hi):
    den = rnd.randrange(2**63, 2**64); return sp.Rational(rnd.randrange(int(lo * den) + 1, int(hi * den)), den)
pts = [{x: rat(1, 21), y: rat(-1, 1), px: rat(-100, 100), py: rat(-100, 100)} for _ in range(20)]

Q = carter(Lv, a)
exprs = {"G0b_field": bracket(Q), "G0c": g0c_expr(a, Q),
         "CTRL_G0c_a_flipped": g0c_expr(-a, carter(Lv, -a)), "CTRL_G0b_L_mutated": bracket(carter(Lv * sp.Rational(1001, 1000), a))}
res = {}
for name, e in exprs.items():
    vals = [e.xreplace(p) for p in pts]
    assert all(v.is_Rational for v in vals), name + ": a value is not an exact rational"
    nz = sum(1 for v in vals if v != 0)
    res[name] = dict(nonzero=nz, max_abs=str(max(abs(v) for v in vals)) if nz else "0")
    print("%-20s nonzero at %2d / 20 points  (max |value| %s)" % (name, nz, "%.3e" % float(max(abs(v) for v in vals)) if nz else "0"), flush=True)
t1 = time.time()
try:
    canc = sp.cancel(sp.together(exprs["G0b_field"])); res["G0b_field_cancel"] = "0" if canc == 0 else "nonzero: " + str(canc)[:200]
except Exception as ex:
    res["G0b_field_cancel"] = "not completed: %r" % (ex,)
print("G0b-field symbolic cancel:", res["G0b_field_cancel"], "(%.0f s)" % (time.time() - t1))
ok = res["G0b_field"]["nonzero"] == 0 and res["G0c"]["nonzero"] == 0
ctrl = res["CTRL_G0c_a_flipped"]["nonzero"] == 20 and res["CTRL_G0b_L_mutated"]["nonzero"] == 20
res.update(seed=SEED, points=[{str(s): str(v) for s, v in p.items()} for p in pts], M=str(M), a=str(a),
           verdict=dict(G0b_field="PASS" if res["G0b_field"]["nonzero"] == 0 else "FAIL", G0c="PASS" if res["G0c"]["nonzero"] == 0 else "FAIL",
                        controls="DISCRIMINATING" if ctrl else "NOT DISCRIMINATING"), seconds=time.time() - t0)
(OUT / "G0bc.json").write_text(json.dumps(res, indent=1))
print("G0b-field %s, G0c %s, controls %s" % (res["verdict"]["G0b_field"], res["verdict"]["G0c"], res["verdict"]["controls"]))
sys.exit(0 if ok and ctrl else 1)
