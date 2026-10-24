"""B15b G4 point rule (registered), step 1: the 8 orbits, computed with kerr_rs.
  forward:  seeds z* + sgn s e_u, s in {1e-4, 1e-3}, sgn in {+1, -1}, iterated with P (tmax 1e6);
  mirror:   seeds z* + sgn s e_s, the same s and sgn, iterated with Pinv (tmax 1e6).
z* = (1.8411884397812655, 0) (the registered seed); e_u and e_s from hs_construct.saddle_info at kerr_rs's DP(z*).
Each orbit stops when it comes back within 0.01 of z* after first leaving that ball, after 200 returns, at a
no-return (None, a certified plunge included) or at a MapCheckFailed (recorded; the gates treat it as a FAIL).
Each iterate records w and the return time T of the step that produced it (for Pinv: the forward return time
P(w_{k+1}) -> w_k, by kerr_rs). Writes horseshoe_results/kerr/b15b_gates/orbits.json; nothing here is a gate verdict."""
import json, time, numpy as np
from pathlib import Path
import kerr_compiled as K
import hs_construct as HC

OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "kerr" / "b15b_gates"; OUT.mkdir(parents=True, exist_ok=True)
TMAX = 1e6
Z = np.array([1.8411884397812655, 0.0])
f = K.CompiledFlow(K.RUST)
_, _, D = f.P(Z, 1, jac=True)
si = HC.saddle_info(D)
eu, es = np.asarray(si["e_u"], float), np.asarray(si["e_s"], float)
orbits = []
t0 = time.time()
for kind, e in (("P", eu), ("Pinv", es)):
    for s in (1e-4, 1e-3):
        for sgn in (1, -1):
            w = Z + sgn * s * e; its = [dict(k=0, w=w.tolist(), T=None)]; left = False; stop = "200 returns"
            for k in range(1, 201):
                try:
                    if kind == "P":
                        r = f.P(w, 1, tmax=TMAX); w2, T = (r[0], r[1]) if r is not None else (None, None)
                    else:
                        w2 = f.Pinv(w, tmax=TMAX); T = None
                        if w2 is not None:
                            rr = f.P(w2, 1, tmax=TMAX); T = rr[1] if rr is not None else None
                except K.MapCheckFailed as ex:
                    stop = "MapCheckFailed: %s" % ex; break
                if w2 is None:
                    stop = "no return" + (" (plunge-certified)" if f.plunges and tuple(f.plunges[-1]["start"][:2]) == (float(w[0]), float(w[1])) else ""); break
                w = np.asarray(w2, float); its.append(dict(k=k, w=w.tolist(), T=T))
                d = np.linalg.norm(w - Z)
                if d > 0.01: left = True
                elif left: stop = "back within 0.01 of z*"; break
            orbits.append(dict(kind=kind, s=s, sgn=sgn, iterates=its, stop=stop))
            xs = [it["w"][0] for it in its]
            print("%-4s s=%g sgn=%+d: %3d iterates, x in [%.4f, %.4f], stop: %s" % (kind, s, sgn, len(its) - 1, min(xs), max(xs), stop), flush=True)
(OUT / "orbits.json").write_text(json.dumps(dict(z=Z.tolist(), e_u=eu.tolist(), e_s=es.tolist(), lam_u=float(si["lam_u"]), tmax=TMAX,
                                                 orbits=orbits, plunges=f.plunges, seconds=time.time() - t0), indent=1, default=float))
print("wrote orbits.json, %.0f s" % (time.time() - t0))
