"""Regenerates the saved artifact for PREREG A2 (line ~123): 'cond(DF) is independent of n; shifting s_u by lambda^+-1
changes n by 1 and cond by < 10% at all four zeros'. Float only (S1 machinery, s1.cond_df). Written 2026-11-27 by
Claude Opus 5.5 (Quantum) for the A13 audit triage; the original measurement was printed in-session but not saved."""
import json, os, sys, time
import numpy as np
import s1
HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
for beta in (0.01, 0.03):
    t0 = time.time(); f = s1.flow(beta); fp, fperr, lam, vu, vs, J, T = s1.fixed_point(f)
    R = json.load(open(os.path.join(HERE, "s1_beta_%g.json" % beta))); rows = []
    for c in R["cond"]:
        row = dict(psi=c["psi"], s_u=c["s_u"])
        for nm, s in (("down", c["s_u"] / lam), ("base", c["s_u"]), ("up", c["s_u"] * lam)):
            r = s1.cond_df(f, fp, vu, vs, s); row[nm] = dict(s_u=s, n=r.get("n"), cond=r.get("cond"), ok=r["ok"])
        cb = row["base"]["cond"]; row["max_rel_change"] = max(abs(row[k]["cond"] - cb) / cb for k in ("down", "up"))
        row["n_steps"] = (row["down"]["n"] - row["base"]["n"], row["up"]["n"] - row["base"]["n"])
        rows.append(row); print(beta, "psi %.3f n %s cond %.3e/%.3e/%.3e  max rel %.3f" % (c["psi"], [row[k]["n"] for k in ("down", "base", "up")],
              row["down"]["cond"], cb, row["up"]["cond"], row["max_rel_change"]), flush=True)
    out[str(beta)] = dict(lam_u=lam, rows=rows, all_under_10pct=all(r["max_rel_change"] < 0.10 for r in rows), seconds=time.time() - t0)
json.dump(out, open(os.path.join(HERE, "a2_cond_shift.json"), "w"), indent=1)
print({b: out[b]["all_under_10pct"] for b in out})
