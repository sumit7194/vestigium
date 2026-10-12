"""A6 cross-path table (MR_REPLAY.md): for every TS row with BOTH an original-path and an A5-path result, compare
verdicts and require overlap (exact Fractions) of the w_g, w_h, tr[g,h] enclosures (re and im). FAIL = non-overlap or
opposite certain decisions (A7 clarification); an undecided A5 run after the ladder is 'overlap only (A5 undecided)'."""
import glob, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from mr_replay import ra_frac
KEYS = ["w_g_re", "w_g_im", "w_h_re", "w_h_im", "tr_comm_re", "tr_comm_im"]
def vals(tag):
    out = {}
    f = HERE / "tests" / "gen" / (tag + ".out")
    if not f.exists(): return None
    for l in open(f):
        p = l.split()
        if len(p) == 3 and p[0] in KEYS: out[p[0]] = (ra_frac(p[1]), ra_frac(p[2]))
    return out
def res(path):
    d = json.load(open(path)); return d, vals(d["tag"])
rows = [("ts2", r) for r in range(6)] + [("tschaos", r) for r in range(8)]
table = []
for fam, row in rows:
    orig = HERE / "replay_results" / f"{fam}_{row}_primary_o30_p256.json"
    a5s = [p for lab in ("primary_a5", "xpath_a5", "a5control", "escalated_a5", "escalated2_a5")
           for p in sorted(glob.glob(str(HERE / "replay_results" / f"{fam}_{row}_{lab}_*.json")))]
    if not orig.exists() or not a5s: continue
    do, vo = res(orig)
    for a in a5s:
        da, va = res(a)
        if vo is None or va is None: table.append(dict(row=f"{fam} {row}", a5=da["tag"], status="MISSING OUTPUT")); continue
        ov = {k: (vo[k][0] <= va[k][1] and va[k][0] <= vo[k][1]) for k in KEYS}
        certain_opposite = False
        for c in ("LOX_G", "LOX_H", "COMM_NE_2"):
            if do.get(c) is True and da.get(c) is False and da.get("verdict") == "REPLAYED": certain_opposite = True
        if not all(ov.values()) or certain_opposite: status = "FAIL (investigate)"
        elif do["verdict"] == da["verdict"] == "REPLAYED": status = "AGREE (both REPLAYED, enclosures overlap)"
        elif da["verdict"] == "NOT_REPLAYED": status = "overlap only (A5 undecided)"
        else: status = f"CHECK: orig {do['verdict']} / A5 {da['verdict']}"
        table.append(dict(row=f"{fam} {row}", orig=do["verdict"], a5_run=da["tag"], a5=da["verdict"], overlap=all(ov.values()), status=status))
for t in table: print(t)
json.dump(table, open(HERE / "replay_crosspath.json", "w"), indent=1)
print("ANY FAIL:", any("FAIL" in t["status"] for t in table))
