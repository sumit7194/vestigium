"""Exploration (non-rigorous, construction only): HH saddles Pi4, Pi5, Pi6 and their manifold crossings."""
import json, time, numpy as np, hs_construct as H
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "construct"
t0 = time.time()
sad = {}
for name, seed in (("Pi4", (-0.25, 0.0)), ("Pi5", (0.37, 0.30)), ("Pi6", (0.37, -0.30))):
    z, D = H.find_periodic(seed, 1, iters=30); si = H.saddle_info(D)
    sad[name] = dict(z=z, **si); print(name, z, si["lam_u"], flush=True)
arcs = {}
for name, s in sad.items():
    arcs[(name, "u")] = H.manifold_arcs(s["z"], s["e_u"], s["lam_u"], forward=True, K=5, eps=1e-4)
    arcs[(name, "s")] = H.manifold_arcs(s["z"], s["e_s"], 1 / s["lam_s"], forward=False, K=5, eps=1e-4)
    print(name, "arcs:", sum(len(a) for _, a in arcs[(name, "u")]), sum(len(a) for _, a in arcs[(name, "s")]),
          "pts, %.0fs" % (time.time() - t0), flush=True)
np.savez(OUT / "hh_arcs.npz", **{f"{k[0]}_{k[1]}_{kk}": a for k, v in arcs.items() for kk, a in v})
print("arcs saved %.0fs" % (time.time() - t0), flush=True)
res = {}
zs = [s["z"] for s in sad.values()]
for p in sad:
    for q in sad:
        cr = H.crossings(arcs[(p, "u")], arcs[(q, "s")], min_angle=1e-2, skip_near=zs)
        res[f"{p}->{q}"] = [dict(point=list(map(float, c[0])), angle=float(c[1]), k_u=int(c[2]), k_s=int(c[3])) for c in cr]
        print(p, "->", q, len(cr), "transverse crossings; smallest k_u+k_s:",
              sorted((abs(c[2]) + abs(c[3]), round(c[1], 3)) for c in cr)[:3], flush=True)
json.dump(dict(saddles={k: dict(z=list(map(float, v["z"])), lam_u=float(v["lam_u"]), lam_s=float(v["lam_s"]),
                                e_u=list(map(float, v["e_u"])), e_s=list(map(float, v["e_s"]))) for k, v in sad.items()},
               crossings=res,
               arcs={f"{k[0]}_{k[1]}": [[int(kk), a.tolist()] for kk, a in v] for k, v in arcs.items()},
               seconds=time.time() - t0), open(OUT / "hh_explore.json", "w"))
print("done %.0fs" % (time.time() - t0))
