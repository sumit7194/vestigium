"""Companion to a2_cond_shift.py: the same lambda^+-1 shift from each zero's NEAREST S1 SAMPLE s_u (the other s_u S1 recorded).
Both variants are reported; neither is selected. 2026-11-27, Claude Opus 5.5 (Quantum)."""
import json, os, time
import s1
HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
for beta in (0.01,):
    f = s1.flow(beta); fp, fperr, lam, vu, vs, J, T = s1.fixed_point(f)
    R = json.load(open(os.path.join(HERE, "s1_beta_%g.json" % beta))); rows = []
    for c in R["cond"]:
        s0 = c["nearest_sample"]["s_u"]; row = dict(psi=c["psi"], s_u=s0)
        for nm, s in (("down", s0 / lam), ("base", s0), ("up", s0 * lam)):
            r = s1.cond_df(f, fp, vu, vs, s); row[nm] = dict(s_u=s, n=r.get("n"), cond=r.get("cond"))
        cb = row["base"]["cond"]; row["max_rel_change"] = max(abs(row[k]["cond"] - cb) / cb for k in ("down", "up")); rows.append(row)
        print(beta, "psi %.3f n %s cond %.3e/%.3e/%.3e max rel %.3f" % (c["psi"], [row[k]["n"] for k in ("down", "base", "up")], row["down"]["cond"], cb, row["up"]["cond"], row["max_rel_change"]), flush=True)
    out[str(beta)] = dict(rows=rows, all_under_10pct=all(r["max_rel_change"] < 0.10 for r in rows))
json.dump(out, open(os.path.join(HERE, "a2_cond_shift_nearest.json"), "w"), indent=1); print({b: out[b]["all_under_10pct"] for b in out})
