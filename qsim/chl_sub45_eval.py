"""Stage-2 sub-45 evaluation (PREREG_cuspis_sub45_check.md STAGE 2 ADDENDUM, db54aa0). Gates and controls as registered.
No comparison with cuspis here: values go to the bridge for the sealed comparison."""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "chl_sub45_run.json")))
CT = 3/(32*math.pi**2)
names = {f"{math.radians(v):.12f}": k for k, v in d["angles_deg"].items()}
names[f"{math.atan(0.5):.12f}"] = "arctan(1/2)"
res, ok_all = {}, True
for key, nm in names.items():
    c, f = d["resolutions"]["coarse"]["values"][key], d["resolutions"]["fine"]["values"][key]
    tail = d["resolutions"]["fine"]["t_tail_bound"][key]
    th = float(key)
    gate = abs(c - f)/abs(f)
    bwk = (math.pi**2*CT/3)*math.log(1/math.sin(th/2))
    res[nm] = dict(theta_rad=th, coarse=c, fine=f, rel_gate=gate, gate_pass=gate <= 1e-7, t_tail_bound=tail,
                   a_over_CT=f/CT, bwk16=bwk, bwk_pass=f >= bwk, theta_a=th*f)
order = sorted(res, key=lambda k: res[k]["theta_rad"])
dec = all(res[order[i]]["fine"] > res[order[i+1]]["fine"] for i in range(len(order)-1))
pos = all(res[k]["fine"] > 0 for k in res)
c90 = abs(res["90"]["fine"] - 0.0118334248474285)/0.0118334248474285
anc = res["arctan(1/2)"]["fine"]
out = dict(per_angle=res, missing=[len(d["resolutions"][r]["missing"]) for r in ("coarse", "fine")],
           all_gates=all(v["gate_pass"] for v in res.values()), positive=pos, strictly_decreasing=dec,
           all_bwk16=all(v["bwk_pass"] for v in res.values()),
           consistency_90_rel=c90, consistency_90_pass=c90 <= 1e-9,
           anchor_arctan=dict(value=anc, ge_lower_bound_0p07265=anc >= 0.07265, rel_to_lattice_0p077=abs(anc-0.077)/0.077,
                              within_2p5pct=abs(anc-0.077)/0.077 <= 0.025),
           label="passed under an amendment adopted after a documented control failure (C1-R)")
json.dump(out, open(os.path.join(HERE, "chl_sub45_eval.json"), "w"), indent=1)
for k in order:
    v = res[k]; print(f"{k:>12}: a = {v['fine']:.12f}  coarse {v['coarse']:.12f}  gate {v['rel_gate']:.1e} {'ok' if v['gate_pass'] else 'FAIL'}  a/C_T = {v['a_over_CT']:.8f}  BWK {'ok' if v['bwk_pass'] else 'FAIL'}  theta*a = {v['theta_a']:.6f}")
print({k: out[k] for k in ('missing','all_gates','positive','strictly_decreasing','all_bwk16','consistency_90_rel','consistency_90_pass')}); print(out['anchor_arctan'])
