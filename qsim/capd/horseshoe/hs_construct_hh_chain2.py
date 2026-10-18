"""Exploration 2 (non-rigorous): Pi4 homoclinic chain with pairwise-disjoint sets (S8). Chain = orbit points x_j,
j1 <= j <= j2, whose sets are disjoint from N0 and from each other; one P step N0 => N_{j1} and N_{j2} => N0."""
import json, itertools, numpy as np, hs_construct as H
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "construct"
e = json.load(open(OUT / "hh_chain_explore.json")); d = json.load(open(OUT / "hh_explore.json"))
s = d["saddles"]["Pi4"]; p = np.array(s["z"]); eu = np.array(s["e_u"]); es = np.array(s["e_s"])
X = [np.array(x) for x in e["X"]]; U = [np.array(u) for u in e["U"]]; S = [np.array(v) for v in e["S"]]; m = e["m"]
res = []
for a0, a, bf0, bf in itertools.product([0.03, 0.02, 0.015, 0.01], [0.01, 0.005, 0.0025], [0.5, 0.25, 0.1], [0.5, 0.25, 0.1]):
    N0 = (p, a0 * eu, bf0 * a0 * es)
    idx = [j for j in range(1, m) if H.disjoint(N0, (X[j], a * U[j], bf * a * S[j]))]
    if not idx: continue
    j1, j2 = idx[0], idx[-1]
    chain = list(range(j1, j2 + 1))
    if chain != idx: continue                               # need a contiguous run of orbit points
    N = {0: N0}; N.update({j: (X[j], a * U[j], bf * a * S[j]) for j in chain})
    if not all(H.disjoint(N[i], N[j]) for i in N for j in N if i < j): continue
    edges = [(0, 0), (0, j1)] + [(j, j + 1) for j in chain[:-1]] + [(j2, 0), (j2, j1)]
    out = {f"{i}>{j}": H.sampled_cover(N[i], N[j], n_edge=12, n_int=8) for i, j in edges}
    nok = sum(1 for v in out.values() if v and v["ok"])
    res.append(dict(a0=a0, a=a, bf0=bf0, bf=bf, chain=chain, n_ok=nok, n=len(edges), detail=out))
    print("a0=%.3f a=%.4f bf0=%.2f bf=%.2f chain x_%d..x_%d: %d/%d ok; failing %s" % (a0, a, bf0, bf, j1, j2, nok,
          len(edges), [k for k, v in out.items() if not (v and v["ok"])]), flush=True)
    if nok == len(edges):
        print("FIRST FULL PASS in registered order:", dict(a0=a0, a=a, bf0=bf0, bf=bf, chain=chain), flush=True); break
json.dump(res, open(OUT / "hh_chain_explore2.json", "w"), indent=1, default=float)
