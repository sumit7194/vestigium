"""Rung 5b AXIAL (PREREG_iahub_v2.md §5b): our exact Q(x,E) axial NVE (mr_mn_axis.axial_nve -> QxE, the code v1 and
v2 both use) vs the bridge's INDEPENDENT derivation (TheBridge 35abf26, v9_axial_provenance.json):
p_x, q_x, A, B, X of the non-reduced xi1 equation at x = 5/4, 5/3, 2, 13/4 (branch R = x on the axis)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp, mpmath as mp
import mr_mn_axis as MA, ia_hub as IA
from flint import acb, arb, ctx
ctx.prec = 256; mp.mp.dps = 60
REF = "/Users/sumit/Github/TheBridge/falsification/V9_mn_obstruction_check/results/v9_axial_provenance.json"
ref = json.load(open(REF))
out, worst = {}, 0.0
for key, block in ref.items():
    if "|E=" not in key:
        continue
    p, lev = key.split("|")
    En, L, mu2 = (int(v.split("=")[1]) for v in lev.split(","))
    fname, beta = MA.MN_POINTS[p]
    C, x, y = MA.load(fname)
    A, B, X = MA.axial_nve(C, x, y, En, mu2)
    E = sp.Symbol("E")
    Aq, Bq, Xq = (MA.QxE.from_expr(e, x, E, beta) for e in (A, B, X))
    px = -(Aq.D()/Aq - Xq.D()/(Xq*2)); qx = Aq*Bq/Xq
    comp = {k: IA.Compiled(v.to_expr(), x) for k, v in dict(p=px, q=qx, A=Aq, B=Bq, X=Xq).items()}
    for xs, vals in block.items():
        xv = sp.Rational(xs)
        for name, c in comp.items():
            if name not in vals:
                continue
            ours = c(c._const(xv))
            om = mp.mpc(ours.real.mid().str(60, radius=False), ours.imag.mid().str(60, radius=False))
            th = mp.mpf(vals[name])
            rel = float(abs(om - th)/max(abs(th), mp.mpf("1e-300")))
            worst = max(worst, rel)
            out[f"{key} x={xs} {name}"] = rel
            print(f"{key:<18} x={xs:<5} {name}: rel {rel:.2e}", flush=True)
out["max_rel"] = worst; out["RUNG_5B_AXIAL_PASS"] = worst < 1e-25
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mr_v2_provenance_axial.json"), "w"), indent=1)
print("max rel", worst, "PASS" if worst < 1e-25 else "FAIL")
