"""Plan A V1 evaluation, as registered (PREREG_cuspis_sub45_check.md, PLAN A, 2abb00d) plus the re-audit judging rule
committed in f901e46 BEFORE any V1 a(theta) existed.
V1 gates: a(90) vs Stage 1 (0.0118334248474285) <= 1e-9 relative; a(40), a(45) inside the tight D1 interval;
c2 (sigma) is a start-series sanity item (the stepper does not touch it) -- reported from the Stage-2 record.
Re-audit rule (bridge): verdict STANDS at theta if |a_V1 - a_rec|/a_rec < 0.1 x C12 gap:
  40: 6.3e-6, 30: 5.7e-5, 26.565: 1.35e-4, 20: 7.1e-4, 15: 2.5e-3.
Also reported (informational, same as Stage 2): coarse vs fine <= 1e-7, positivity, monotonicity."""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(HERE, "chl_planA_V1_run.json")))
REC = json.load(open(os.path.join(HERE, "chl_sub45_eval.json")))["per_angle"]
D1 = json.load(open(os.path.join(HERE, "chl_sub45_D1.json")))
TH = {"40": 6.3e-6, "30": 5.7e-5, "26.565": 1.35e-4, "20": 7.1e-4, "15": 2.5e-3}
def v1(res, theta):
    k = f"{theta:.12f}"; return V["resolutions"][res]["values"][k]
out = {"per_angle": {}, "missing": {r: len(V["resolutions"][r]["missing"]) for r in V["resolutions"]}}
for nm, rec in REC.items():
    th = rec["theta_rad"]
    f, c = v1("fine", th), v1("coarse", th)
    e = dict(theta_deg=math.degrees(th), a_V1_fine=f, a_V1_coarse=c, a_rec_fine=rec["fine"],
             rel_V1_vs_rec=(f - rec["fine"]) / rec["fine"], coarse_fine_gate=abs(c - f) / abs(f))
    key = {"arctan(1/2)": "26.565"}.get(nm, nm)
    if key in TH:
        e["threshold"] = TH[key]; e["VERDICT_STANDS"] = abs(e["rel_V1_vs_rec"]) < TH[key]
    if nm in D1 or key in D1:
        dd = D1.get(nm) or D1.get(key)
        e["tight_D1"] = dd["tight"]; e["inside_tight_D1"] = dd["tight"][0] <= f <= dd["tight"][1]
    out["per_angle"][nm] = e
a90 = out["per_angle"]["90"]["a_V1_fine"]
out["V1_gate_a90_rel"] = abs(a90 - 0.0118334248474285) / 0.0118334248474285
out["V1_gate_a90_pass"] = out["V1_gate_a90_rel"] <= 1e-9
out["V1_gate_40_45_inside_tight"] = {k: out["per_angle"][k].get("inside_tight_D1") for k in ("40", "45")}
order = sorted(out["per_angle"], key=lambda k: -out["per_angle"][k]["theta_deg"])
out["positive"] = all(out["per_angle"][k]["a_V1_fine"] > 0 for k in order)
out["strictly_increasing_as_theta_decreases"] = all(out["per_angle"][order[i]]["a_V1_fine"] < out["per_angle"][order[i+1]]["a_V1_fine"] for i in range(len(order)-1))
out["all_coarse_fine_1e-7"] = all(out["per_angle"][k]["coarse_fine_gate"] <= 1e-7 for k in order)
out["V1_PASS"] = out["V1_gate_a90_pass"] and all(out["V1_gate_40_45_inside_tight"].values())
out["REAUDIT_all_verdicts_stand"] = all(e["VERDICT_STANDS"] for e in out["per_angle"].values() if "VERDICT_STANDS" in e)
json.dump(out, open(os.path.join(HERE, "chl_planA_V1_eval.json"), "w"), indent=1)
for k in order:
    e = out["per_angle"][k]
    print(f"{k:>12}: a_V1 {e['a_V1_fine']:.12f}  rec {e['a_rec_fine']:.12f}  rel {e['rel_V1_vs_rec']:+.3e}"
          + (f"  thr {e['threshold']:.2e} {'STANDS' if e['VERDICT_STANDS'] else 'EXCEEDS'}" if 'threshold' in e else "")
          + (f"  tightD1 {'in' if e['inside_tight_D1'] else 'OUT'}" if 'inside_tight_D1' in e else "")
          + f"  c/f {e['coarse_fine_gate']:.1e}")
print({k: out[k] for k in ("missing", "V1_gate_a90_rel", "V1_gate_a90_pass", "V1_gate_40_45_inside_tight", "positive",
       "strictly_increasing_as_theta_decreases", "all_coarse_fine_1e-7", "V1_PASS", "REAUDIT_all_verdicts_stand")})
