"""TS v2 re-cert: equation provenance vs the bridge's INDEPENDENT V8 derivation (TheBridge ed433e7,
v8_ts_provenance.json): p_x, q_x, A, B, X of the non-reduced xi1 equation at x = 5/4, 5/3, 2, 13/4 (R principal)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp, mpmath as mp
import mr_mn_equatorial as ME, ia_hub as IA, mr_v2_ts2 as TS
from flint import acb, arb, ctx
ctx.prec = 256; mp.mp.dps = 60
REF = "/Users/sumit/Github/TheBridge/falsification/V8_ts2_obstruction_check/results/v8_ts_provenance.json"
ref = json.load(open(REF))
out, worst = {}, 0.0
for key, block in ref.items():
    if "|E=" not in key:
        continue
    P, lev = key.split("|")
    En, L, mu2 = (int(v.split("=")[1]) for v in lev.split(","))
    C, x, y = TS.ts_source(P)
    cd = ME.field_ctx(0)
    G = ME.lower_at_equator(C, x, y, cd)
    A, B, X = ME.equatorial_nve(G, En, L, mu2)
    xprime = ME.QtE.from_expr(sp.cancel(sp.diff(ME.X_OF_T, ME.T_)), A.c)
    Xx = X*xprime*xprime
    px = -(A.D()/A - Xx.D()/(Xx*2))/xprime
    qx = A*B/Xx
    comp = {k: IA.Compiled(v.to_expr(), ME.T_) for k, v in dict(p=px, q=qx, A=A, B=B, X=Xx).items()}
    for xs, vals in block.items():
        xv = sp.Rational(xs)
        tv = mp.mpf(xv.p)/xv.q + mp.sqrt((mp.mpf(xv.p)/xv.q)**2 - 1)
        tb = acb(arb(mp.nstr(tv, 70, strip_zeros=False)))
        for name, c in comp.items():
            if name not in vals:
                continue
            ours = c(tb)
            om = mp.mpc(ours.real.mid().str(60, radius=False), ours.imag.mid().str(60, radius=False))
            th = mp.mpf(vals[name])
            rel = float(abs(om - th)/max(abs(th), mp.mpf("1e-300")))
            worst = max(worst, rel)
            out[f"{key} x={xs} {name}"] = rel
            print(f"{key:<18} x={xs:<5} {name}: rel {rel:.2e}", flush=True)
out["max_rel"] = worst; out["TS_PROVENANCE_PASS"] = worst < 1e-25
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mr_v2_ts2_provenance.json"), "w"), indent=1)
print("max rel", worst, "PASS" if worst < 1e-25 else "FAIL")
