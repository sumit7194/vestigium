"""R3 Kerr negative control, branch K-1 (prereg §6.3, B14 step 1): the FROZEN constructor's saddle finder on Kerr
(F5-R's Kerr limit: M = 89, a = 80, q = 0; E = 19/20, L_z = 267), seeded at A-K20's F5-R UPO section points.
Records, per seed, whether Newton converges, and the multipliers. Non-rigorous (construction stage)."""
import json, time, numpy as np, sympy as sp
from pathlib import Path
import mn_numerics as MNN
OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "kerr"
seeds = {"2": [(3.6419361737, 6.0360992808)], "4": [(3.6419361737, -6.0360992808)], "8": [(3.6027445056, 0.0)],
         "3": [(2.8351345960, 42.7008610620), (2.6086564716, -44.4884516459), (2.0104594390, 23.8102634036)],
         "6": [(2.8351345960, -42.7008610621), (2.0104594390, -23.8102634043), (2.6086564716, 44.4884516462)],
         "7": [(3.3482091281, 0.0), (2.8958122167, -62.6170252389), (2.8958122167, 62.6170252388)]}
period = {"2": 1, "4": 1, "8": 1, "3": 3, "6": 3, "7": 3}
t0 = time.time()
kerr = MNN.MNFlow(89, 80, 0, sp.Rational(19, 20), sp.Integer(267))
H = MNN.plug_into_constructor(kerr)
res = []
for upo, pts in seeds.items():
    for w in pts:
        lift = kerr.py_of(*w)
        rec = dict(mn_upo=upo, seed=w, period=period[upo], kerr_py_lift=(None if not np.isfinite(lift) else float(lift)))
        if np.isfinite(lift):
            r = H.find_periodic(w, period[upo], iters=25)
            if r is None:
                rec["newton"] = "no convergence"
            else:
                z, D = r; ev = np.linalg.eigvals(D); si = H.saddle_info(D)
                rec.update(newton="converged", z=z.tolist(), eigvals=[complex(e).__repr__() for e in ev],
                           saddle=bool(si), lam_u=(float(si["lam_u"]) if si else None))
        else:
            rec["newton"] = "seed not in the Kerr allowed region at this level"
        res.append(rec); print(rec, "%.0fs" % (time.time() - t0), flush=True)
json.dump(dict(system="Kerr (89,80,q=0)", E="19/20", L="267", results=res), open(OUT / "r3_k1_saddles.json", "w"), indent=1)
print("K-1 saddles found:", sum(1 for r in res if r.get("saddle")))
