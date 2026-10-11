"""Evaluate Plan A V2 + V3 (PREREG_cuspis_sub45_check.md, PLAN A) from chl_planA_V23_nodes.jsonl, exactly as registered:
V2a: frozen v1 DENSE vs recorded Stage-2 sparse, <= 1e-8 relative at every Stage-2 angle.
V2b: v2 sparse vs v2 dense, <= 1e-10.
V3 : 3a-failed nodes, v2 sparse, sets B and C agree <= 1e-8; smooth decay (record's 'smooth' flag)."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chl_run_controls as R, chl_run_sub45 as S2
L = [json.loads(l) for l in open(os.path.join(HERE, "chl_planA_V23_nodes.jsonl"))]
done = S2.load_done()
def tr(r): return {round(float(k), 12): v[0] for k, v in r["trG"].items()}
def rel(a, b): return abs(a - b) / max(abs(a), abs(b), 1e-300)
idx = {}
for r in L: idx[(r["tag"], round(r["t"], 9), round(r["q"], 9), r["set"], r["stepper"], r["grid"])] = r
out = {"V2a": [], "V2b": [], "V3": []}
orig = {(round(r["t"], 9), round(r["q"], 9)): (r["t"], r["q"]) for r in L if r["tag"] == "V2"}
for t, q in sorted(orig):
    a = idx.get(("V2", t, q, "S2", "v1", "dense")); b = idx.get(("V2", t, q, "S2", "v2", "sparse")); c = idx.get(("V2", t, q, "S2", "v2", "dense"))
    rec = done[R.key(*orig[(t, q)])]
    ra = tr(rec)
    if a and a["ok"]:
        ta = tr(a); m = max(rel(ta[k], ra[k]) for k in ra if k in ta)
        out["V2a"].append(dict(t=t, q=q, max_rel=m, ok=m <= 1e-8))
    else: out["V2a"].append(dict(t=t, q=q, ok=False, error=(a or {}).get("error", "missing")))
    if b and c and b["ok"] and c["ok"]:
        tb, tc = tr(b), tr(c); m = max(rel(tb[k], tc[k]) for k in tb if k in tc)
        out["V2b"].append(dict(t=t, q=q, max_rel=m, ok=m <= 1e-10))
    else: out["V2b"].append(dict(t=t, q=q, ok=False, error=((b or {}).get("error"), (c or {}).get("error"))))
for t, q in ((0.3, 22.8), (0.3, 31.8), (1.37, 23.9), (1.37, 32.9)):
    B = idx.get(("V3", round(t, 9), round(q, 9), "B", "v2", "sparse")); C = idx.get(("V3", round(t, 9), round(q, 9), "C", "v2", "sparse"))
    e = dict(t=t, q=q, B_ok=bool(B and B["ok"]), C_ok=bool(C and C["ok"]))
    if not e["B_ok"]: e["B_error"] = (B or {}).get("error"); e["B_seconds"] = (B or {}).get("seconds")
    if e["B_ok"] and e["C_ok"]:
        tb, tc = tr(B), tr(C); e["max_rel_BC"] = max(rel(tb[k], tc[k]) for k in tb if k in tc)
        e["smooth_B"], e["smooth_C"] = B.get("smooth"), C.get("smooth")
        e["ok"] = e["max_rel_BC"] <= 1e-8 and bool(B.get("smooth")) and bool(C.get("smooth"))
    else: e["ok"] = False
    if e["C_ok"]: e["smooth_C"] = C.get("smooth")
    out["V3"].append(e)
summ = {k: dict(n=len(v), passed=sum(1 for x in v if x["ok"])) for k, v in out.items()}
summ["V2a_worst"] = max((x.get("max_rel", float("inf")) for x in out["V2a"]), default=None)
summ["V2b_worst"] = max((x.get("max_rel", float("inf")) for x in out["V2b"]), default=None)
json.dump(dict(summary=summ, detail=out), open(os.path.join(HERE, "chl_planA_V23_eval.json"), "w"), indent=1, default=str)
print(json.dumps(summ, indent=1)); print(json.dumps(out["V3"], indent=1, default=str)[:3000])
