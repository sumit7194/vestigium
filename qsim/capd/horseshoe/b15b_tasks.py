"""B15b: the MNFlow reference evaluations the registered gates need, as one task list (tasks.json), in priority order.
  G1   12 points (kerr_p_gate.py's rule, seed 20261024): P(w, 1, jac, tmax 2000), Pinv(w, tmax 2000)   [rtol = atol 1e-12]
  G4   the registered G4 points from orbits.json (rule below): P(w, 1, jac, tmax 1e6) for forward-orbit points,
       Pinv(w, tmax 1e6) for mirror points   [1e-12]
  G4c  MNFlow self-convergence at the 3 G4 forward points with the largest T: P(w, 1, jac, tmax 1e6) at 1e-11 and 1e-13
  G3   the 200 G2 points (kerr_rs_cross.py's rule, seed 20261024): P(w, 1, jac, tmax 2000)   [1e-12] (det DP for G3)
G4 point rule (registered): on each of the 8 orbits, the first iterate past x = 2, 5, 10, 20, 50, 100, plus the iterate
with the largest T, plus the 2 iterates closest to z* after the first iterate past x = 5 (ties by index); duplicates
within an orbit are taken once; iterate 0 (the seed) is never a G4 point. Forward orbits are compared through P and
mirror orbits through Pinv.
"T" of a G4 point is the return time of the COMPARED return, the next iterate's recorded T (for mirror points, that is
the forward time of the same leg). orbits.json records each iterate's ARRIVAL time. The registration's "largest T"
(point rule and G4c) is meant to exercise the longest compared returns, so it is read as the next T. This
interpretation is fixed here before any G4 output exists; the arrival-time reading was in a draft of this script
that never ran a gate."""
import json, random, numpy as np
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "kerr" / "b15b_gates"
ORB = json.loads((OUT / "orbits.json").read_text())
Z = np.array(ORB["z"])
tasks = []


def near_saddle_pts(rnd, n):
    return [Z + 10 ** rnd.uniform(-6, -3) * np.array([np.cos(a), np.sin(a)]) for a in (rnd.uniform(0, 2 * np.pi) for _ in range(n))]


for i, w in enumerate(near_saddle_pts(random.Random(20261024), 12)):
    tasks.append(dict(id="G1_%02d_P" % i, gate="G1", call="P", jac=True, w=w.tolist(), tmax=2000.0, tol=1e-12))
    tasks.append(dict(id="G1_%02d_Pinv" % i, gate="G1", call="Pinv", jac=False, w=w.tolist(), tmax=2000.0, tol=1e-12))
g4 = []
for oi, orb in enumerate(ORB["orbits"]):
    its = orb["iterates"][1:]; pick = []
    for th in (2, 5, 10, 20, 50, 100):
        c = [it for it in its if it["w"][0] > th]
        if c: pick.append(c[0]["k"])
    allits = orb["iterates"]
    Tn = {it["k"]: allits[it["k"] + 1]["T"] for it in its if it["k"] + 1 < len(allits) and allits[it["k"] + 1]["T"] is not None}
    if Tn: pick.append(max(Tn, key=lambda k: (Tn[k], -k)))
    p5 = [it for it in its if it["w"][0] > 5]
    if p5:
        after = [it for it in its if it["k"] > p5[0]["k"]]
        after.sort(key=lambda it: (np.linalg.norm(np.array(it["w"]) - Z), it["k"]))
        pick += [it["k"] for it in after[:2]]
    for k in sorted(set(pick)):
        it = orb["iterates"][k]; call = orb["kind"]
        g4.append(dict(id="G4_o%d_k%03d_%s" % (oi, k, call), gate="G4", call=call, jac=(call == "P"), w=it["w"], tmax=1e6, tol=1e-12,
                       orbit=oi, k=k, T=Tn.get(k)))
tasks += g4
for t in sorted([t for t in g4 if t["call"] == "P" and t["T"] is not None], key=lambda t: -t["T"])[:3]:
    for tol in (1e-11, 1e-13):
        tasks.append(dict(t, id=t["id"] + "_tol%g" % tol, gate="G4c", tol=tol))
for i, w in enumerate(near_saddle_pts(random.Random(20261024), 200)):
    tasks.append(dict(id="G3_%03d_P" % i, gate="G3", call="P", jac=True, w=w.tolist(), tmax=2000.0, tol=1e-12))
(OUT / "tasks.json").write_text(json.dumps(tasks, indent=1))
print("tasks:", {g: sum(1 for t in tasks if t["gate"] == g) for g in ("G1", "G4", "G4c", "G3")}, "G4 points:", len(g4))
