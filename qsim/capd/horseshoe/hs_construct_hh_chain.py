"""Exploration (non-rigorous): the Pi4 homoclinic chain, frames from manifold tangents, sampled covering checks."""
import json, sys, time, itertools, numpy as np, hs_construct as H
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "construct"
d = json.load(open(OUT / "hh_explore.json"))
s = d["saddles"]["Pi4"]; p = np.array(s["z"]); eu = np.array(s["e_u"]); es = np.array(s["e_s"]); lam = s["lam_u"]
c = sorted(d["crossings"]["Pi4->Pi4"], key=lambda c: (abs(c["k_u"]) + abs(c["k_s"]), -c["angle"]))[0]
ku, ks = abs(c["k_u"]), abs(c["k_s"]); su, ss = (np.sign(c["k_u"]) or 1), (np.sign(c["k_s"]) or 1)
r = H.refine_connection(p, su * eu, p, ss * es, ku, ks, np.array(c["point"]))
t, tau = r["t"], r["tau"]; m = ku + ks
X = [H.tangent_fwd(p, su * eu, t, j)[0] for j in range(m + 1)]
Uu = [H.tangent_fwd(p, su * eu, t, j)[1] for j in range(m + 1)]
Su = [H.tangent_back(p, ss * es, tau, m - j)[1] for j in range(m + 1)]
print("homoclinic t=%.3e tau=%.3e  m=%d steps; x_m - (p+tau es) = %.1e" % (t, tau, m, np.linalg.norm(X[m] - (p + tau * ss * es))), flush=True)
for j in range(m + 1):
    ang = abs(Uu[j][0] * Su[j][1] - Uu[j][1] * Su[j][0]); print("  x_%d = %s  |x-p| = %.3e  sin(angle u,s) = %.3f" % (j, np.round(X[j], 5), np.linalg.norm(X[j] - p), ang))
res = []
for a0, a, bfac in itertools.product([2e-3, 1e-3, 5e-4], [4e-3, 2e-3, 1e-3], [0.25, 0.1]):
    N = {0: (p, a0 * eu, bfac * a0 * es)}
    for j in range(1, m):
        N[j] = (X[j], a * Uu[j], bfac * a * Su[j])
    edges = [(0, 0), (0, 1)] + [(j, j + 1) for j in range(1, m - 1)] + [(m - 1, 0), (m - 1, 1)]
    out = {f"{i}>{j}": H.sampled_cover(N[i], N[j], n_edge=12, n_int=8) for i, j in edges}
    nok = sum(1 for v in out.values() if v and v["ok"])
    res.append(dict(a0=a0, a=a, bfac=bfac, n_ok=nok, n=len(edges), detail=out))
    print("a0=%.0e a=%.0e bfac=%.2f: %d/%d sampled coverings ok; failing: %s" % (a0, a, bfac, nok, len(edges),
          [k for k, v in out.items() if not (v and v["ok"])]), flush=True)
json.dump(dict(t=t, tau=tau, m=m, X=[x.tolist() for x in X], U=[u.tolist() for u in Uu], S=[v.tolist() for v in Su], scan=res),
          open(OUT / "hh_chain_explore.json", "w"), indent=1, default=float)
