"""B15b gates G1, G3 and G4 (registered), from the MNFlow reference results (mnflow_w*.jsonl, b15b_mnflow_worker.py) and
fresh compiled evaluations (kerr_rs and kerr_p) of the same tasks.
  G1  per G1 point, both libraries: py, P (x, px, T), DP, Pinv vs MNFlow: max relative difference |a - b| / max(1, |b|)
      <= 1e-10; a return mismatch is a FAIL (B15b-1 P4 agreement table: MNFlow None via 'status -1' with a compiled
      'plunge-certified', or via 'tmax' with a compiled no-return within tmax, agree; any other None pairing is a FAIL).
  G3  |det DP - 1| <= 1e-8 at every G1, G3 (= the G2 points) and G4 P point, for both libraries and MNFlow.
  G4  per G4 point: P (x, px, T, DP) or Pinv (x, px) vs MNFlow, <= 1e-10, unscaled; None pairing as G1.
      Reference acceptance (G4c): at the 3 longest-T points, MNFlow's 1e-12 value within 1e-11 relative of its 1e-13
      value (every compared quantity). A point whose reference fails this cannot gate: it is reported as
      REFERENCE-UNCONVERGED, and G4 cannot PASS with such a point (it is open, not passed).
      G0b-drift (diagnostic, no bar): relative change of H and Carter's Q over the compared return, per map.
      E3: the compiled per-call stats are recorded.
On any FAIL the registered path is a self-convergence study (rtol = atol 1e-11 .. 1e-14), not a scaled criterion.
Usage: b15b_gates_eval.py [--partial]  (--partial: evaluate what has finished; no verdict for incomplete gates)
Writes horseshoe_results/kerr/b15b_gates/G1_G3_G4.json."""
import glob, json, sys, numpy as np, sympy as sp
from pathlib import Path
import kerr_compiled as K, mn_codegen as CG, mn_numerics as MNN

OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "kerr" / "b15b_gates"
PARTIAL = "--partial" in sys.argv
tasks = json.loads((OUT / "tasks.json").read_text())
ref = {}
for p in glob.glob(str(OUT / "mnflow_*.jsonl")):
    for line in Path(p).read_text().splitlines():
        try: r = json.loads(line); ref[r["id"]] = r
        except Exception: pass
kerr = MNN.MNFlow(89, 80, 0, sp.Rational(49, 50), sp.Rational(445, 2))       # for py_of only (cheap)
libs = {"rust": K.CompiledFlow(K.RUST), "c++": K.CompiledFlow(K.CPP)}
rel = lambda a, b: abs(a - b) / max(1.0, abs(b))
PAR = {CG.k: 39, CG.al: sp.Rational(-5, 8), CG.beta: 0, CG.E: sp.Rational(49, 50), CG.L: sp.Rational(445, 2)}
_H = CG.build()["H"].subs(PAR); _H = _H.subs({e: 1 for e in _H.atoms(sp.exp)})
Hf = sp.lambdify((CG.x, CG.y, CG.PX, CG.PY), _H, "math")
def carter(s):
    x, y, px, py = s; mu2 = -2 * Hf(*s)
    return (1 - y * y) * py * py + y * y * (6400 * (mu2 - 0.98**2) + 222.5**2 / (1 - y * y))


def compiled(f, t):
    w = np.array(t["w"]); f.plunges.clear()
    try:
        if t["call"] == "P":
            r = f.P(w, 1, jac=t["jac"], tmax=t["tmax"], rtol=t["tol"], atol=t["tol"])
            v = None if r is None else [r[0][0], r[0][1], r[1]] + (list(np.asarray(r[2]).ravel()) if t["jac"] else [])
        else:
            r = f.Pinv(w, tmax=t["tmax"], rtol=t["tol"], atol=t["tol"]); v = None if r is None else [r[0], r[1]]
        why = None if v is not None else ("plunge-certified" if f.plunges else "tmax")
        return dict(value=v, why=why, stats=f.stats())
    except K.MapCheckFailed as e:
        return dict(value=None, why="MapCheckFailed: %s" % e, stats=f.stats())


def none_pair_ok(rv, cv):
    if rv["value"] is not None and cv["value"] is not None: return True
    if rv["value"] is None and cv["value"] is None:
        return (rv["route"] == "status -1" and cv["why"] == "plunge-certified") or (rv["route"] == "tmax" and cv["why"] == "tmax")
    return False


report = dict(G1=[], G3=[], G4=[], G4c=[]); verdict = {}
for gate in ("G1", "G4", "G3"):
    ts = [t for t in tasks if t["gate"] == gate]; missing = [t["id"] for t in ts if t["id"] not in ref]
    for t in ts:
        if t["id"] not in ref: continue
        rv = ref[t["id"]]; row = dict(id=t["id"], ref_route=rv["route"], ref_seconds=rv["seconds"], ref_ok=rv["ok"])
        if not rv["ok"]: row["error"] = rv["error"]
        for name, f in libs.items():
            cv = compiled(f, t); row[name] = dict(why=cv["why"], stats=cv["stats"])
            if not none_pair_ok(rv, cv): row[name]["mismatch"] = True; continue
            if cv["value"] is None: continue
            a, b = np.array(cv["value"]), np.array(rv["value"])
            if gate != "G3": row[name]["maxrel"] = max(rel(x, y) for x, y in zip(a, b))
            if gate == "G1" and t["call"] == "P":
                row[name]["py_rel"] = rel(f.lib.kerr_py(*t["w"]), kerr.py_of(*t["w"])); row[name]["maxrel"] = max(row[name]["maxrel"], row[name]["py_rel"])
            if t["call"] == "P" and t["jac"]:
                row[name]["det_err"] = abs(a[3] * a[6] - a[4] * a[5] - 1)
            if gate == "G4":
                w = t["w"]                                    # the lift, for the drift diagnostic
                s0 = [w[0], 0.0, w[1], f.lib.kerr_py(w[0], w[1])]
                s1 = [a[0], 0.0, a[1], f.lib.kerr_py(a[0], a[1])]
                row[name]["drift_H"] = abs(Hf(*s1) - Hf(*s0)); row[name]["drift_Q_rel"] = abs(carter(s1) - carter(s0)) / abs(carter(s0))
        if rv["value"] is not None and t["call"] == "P" and t["jac"]:
            b = rv["value"]; row["ref_det_err"] = abs(b[3] * b[6] - b[4] * b[5] - 1)
        report[gate].append(row)
    if missing and not PARTIAL:
        sys.exit("incomplete: %d %s tasks have no reference result yet (use --partial)" % (len(missing), gate))
    if missing: verdict[gate] = "INCOMPLETE (%d / %d)" % (len(ts) - len(missing), len(ts)); continue
    rows = report[gate]
    mism = sum(1 for r in rows for n in libs if r[n].get("mismatch")) + sum(1 for r in rows if not r["ref_ok"])
    if gate != "G3":
        worst = max([r[n].get("maxrel", 0) for r in rows for n in libs] or [0])
        verdict[gate] = "%s (worst %.3e, mismatches %d)" % ("PASS" if mism == 0 and worst <= 1e-10 else "FAIL", worst, mism)
# G4c reference acceptance
unconv = []
for t in [t for t in tasks if t["gate"] == "G4c"]:
    base = t["id"].rsplit("_tol", 1)[0]
    if t["id"] in ref and base in ref and ref[t["id"]]["value"] is not None and ref[base]["value"] is not None:
        d = max(rel(x, y) for x, y in zip(ref[base]["value"], ref[t["id"]]["value"]))
        report["G4c"].append(dict(id=t["id"], maxrel_vs_1e12=d))
        if t["id"].endswith("1e-13") and d > 1e-11: unconv.append(base)
    elif not PARTIAL:
        sys.exit("incomplete: G4c %s" % t["id"])
if "G4" in verdict and verdict["G4"].startswith("PASS") and unconv:
    verdict["G4"] = "OPEN: REFERENCE-UNCONVERGED at %s" % unconv
# G3 over all P-jac rows
dets = [r[n]["det_err"] for g in ("G1", "G3", "G4") for r in report[g] for n in libs if "det_err" in r[n]] + \
       [r["ref_det_err"] for g in ("G1", "G3", "G4") for r in report[g] if "ref_det_err" in r]
g3_incomplete = any(v.startswith("INCOMPLETE") for v in verdict.values())
verdict["G3"] = ("INCOMPLETE; " if g3_incomplete else "") + "%s (worst |det - 1| %.3e over %d)" % ("PASS" if dets and max(dets) <= 1e-8 else "FAIL", max(dets) if dets else float("nan"), len(dets))
report["verdict"] = verdict
(OUT / ("G1_G3_G4%s.json" % ("_partial" if PARTIAL else ""))).write_text(json.dumps(report, indent=1, default=float))
for k, v in verdict.items(): print(k, v)
