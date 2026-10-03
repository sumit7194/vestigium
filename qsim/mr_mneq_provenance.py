"""Rung 5b (iahub v2 draft, §5b): equation provenance for the equatorial MN NVE.
Our exact Q(t,E) pipeline (mr_mn_equatorial: lower_at_equator -> equatorial_nve) vs the bridge's INDEPENDENT
symbolic derivation (TheBridge 92c3ec5, v9_equatorial_provenance.json): p_x, q_x (and A, B, X when present)
of the non-reduced xi1 equation in x, at x = 5/4, 5/3, 2, 13/4, branch R = principal sqrt(x^2-1) <-> t > 1."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp, mpmath as mp
import mr_mn_equatorial as Q, ia_hub as IA
from flint import acb, arb, ctx
ctx.prec = 256
mp.mp.dps = 60
REF = "/Users/sumit/Github/TheBridge/falsification/V9_mn_obstruction_check/results/v9_equatorial_provenance.json"
ref = json.load(open(REF))
out, worst = {}, 0.0
for key, block in ref.items():
    if "|E=" not in key:
        continue
    p, lev = key.split("|")
    En, L, mu2 = (int(v.split("=")[1]) for v in lev.split(","))
    G, (A, B, X), cd, src = Q.build("mn", p, En, L, mu2)
    xprime = Q.QtE.from_expr(sp.cancel(sp.diff(Q.X_OF_T, Q.T_)), A.c)
    Xx = X*xprime*xprime                                       # xdot^2 = tdot^2 * x'(t)^2
    # d/dx = (1/x'(t)) d/dt
    px = -(A.D()/A - Xx.D()/(Xx*2))/xprime
    qx = A*B/Xx
    comp = {"p": IA.Compiled(px.to_expr(), Q.T_), "q": IA.Compiled(qx.to_expr(), Q.T_),
            "A": IA.Compiled(A.to_expr(), Q.T_), "B": IA.Compiled(B.to_expr(), Q.T_), "X": IA.Compiled(Xx.to_expr(), Q.T_)}
    for xs, vals in block.items():
        xv = sp.Rational(xs)
        tv = mp.mpf(xv.p)/xv.q + mp.sqrt((mp.mpf(xv.p)/xv.q)**2 - 1)          # t > 1  <->  R > 0
        tb = acb(arb(mp.nstr(tv, 70, strip_zeros=False)))
        for name, c in comp.items():
            if name not in vals:
                continue
            ours = c(tb)
            ourm = mp.mpc(ours.real.mid().str(60, radius=False), ours.imag.mid().str(60, radius=False))
            theirs = mp.mpf(vals[name])
            rel = float(abs(ourm - theirs)/max(abs(theirs), mp.mpf("1e-300")))
            worst = max(worst, rel)
            out[f"{key} x={xs} {name}"] = dict(ours=mp.nstr(ourm.real, 30), theirs=vals[name][:32], rel=rel,
                                              imag_ours=float(abs(ourm.imag)))
            print(f"{key:<20} x={xs:<5} {name}: rel {rel:.2e}", flush=True)
out["max_rel"] = worst
out["RUNG_5B_PASS"] = worst < 1e-25
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mr_mneq_provenance.json"), "w"), indent=1)
print("max rel", worst, "PASS" if worst < 1e-25 else "FAIL")
