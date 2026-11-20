"""b15_g6_summary.py G6JSON OUT -- stream b15_g6.json (indent=1, ~1 GB) one record at a time: per-crossing and per-near-miss tallies, the accept rows. Read-only; written after the run by Claude Opus 5.5 (session "Quantum"), 2026-11-20."""
import json, sys, collections
P = sys.argv[1]
sec = None; buf = []; out = collections.Counter(); acc = []; nm_exist = []; nm_flag = []
with open(P) as f:
    for line in f:
        if line.startswith('  "crossings": ['): sec = "c"; continue
        if line.startswith('  "near_misses": ['): sec = "n"; continue
        if sec and line.startswith("  ]"): sec = None; continue
        if not sec: continue
        if line.startswith("   {"): buf = [line]; continue
        buf.append(line)
        if line.startswith("   }"):
            r = json.loads("".join(buf).rstrip().rstrip(","))
            if sec == "c":
                out["crossings"] += 1
                rec = r.get("recompute_1e-14")
                th0 = rec is not None
                out["c_thin_run"] += th0
                th14 = bool(rec.get("thin", True)) if rec else False
                out["c_thin_1e14"] += th14
                a = rec.get("accepted", r["D6"]["accepted"]) if rec else r["D6"]["accepted"]
                if r["D6"]["accepted"] or a:
                    acc.append(dict(n=r["n"], angle=r["angle"], run_acc=r["D6"]["accepted"], acc14=a, thin_run=th0, thin14=th14,
                                    chord=r["on_chord"], measured=r["measured"], dmargin=r["D6"].get("margin"),
                                    ang14=(rec or {}).get("angle")))
                out["c_red"] += bool(r["D7"]["red"])
                out["c_unmeasured"] += (not r["measured"])
            else:
                out["near"] += 1; out["near_could_flag"] += r["could_flag"]; out["near_could_accept"] += r["could_accept"]
                rec = r.get("recompute_1e-14")
                if rec:
                    out["near_rec"] += 1; out["near_thin14"] += bool(rec.get("thin", True))
                    if rec.get("exists"): nm_exist.append(dict(u=r["u"], s=r["s"], ang14=rec.get("angle"), acc=rec.get("accepted"), thin=rec.get("thin"), red=rec.get("red_flag")))
print(json.dumps(dict(counts=out), indent=1))
A = acc; print("accept rows", len(A))
print("run_acc", sum(x["run_acc"] for x in A), "acc14", sum(bool(x["acc14"]) for x in A))
print("robust accepts (accepted at the decision used, not thin at 1e-14, not chord):",
      sum(1 for x in A if x["acc14"] and not x["thin14"] and not x["chord"]))
print("accepts never flagged thin in the run:", sum(1 for x in A if x["run_acc"] and not x["thin_run"]))
print("accepts thin in run, resolved at 1e-14:", sum(1 for x in A if x["thin_run"] and not x["thin14"]))
print("accept angle range:", min(x["angle"] for x in A), max(x["angle"] for x in A))
rob = [x for x in A if x["acc14"] and not x["thin14"] and not x["chord"]]
print("robust sample:", rob[:5])
print("near-miss EXISTS at 1e-14:", len(nm_exist), "accepted", sum(bool(x["acc"]) for x in nm_exist), "red", sum(bool(x["red"]) for x in nm_exist),
      "robust-accepted", sum(1 for x in nm_exist if x["acc"] and not x["thin"]))
json.dump(dict(counts=out, accepts=A, near_exist=nm_exist), open(sys.argv[2], "w"), indent=1)
