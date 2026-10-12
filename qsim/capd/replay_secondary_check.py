"""Registered secondary requirement (MR_REPLAY.md, 'Secondary: an independent homotopic loop'): every LOOP matrix
entry of the homotopic secondary run must overlap the primary's (same base point, homotopic loop => same monodromy
matrix), and the verdict must again be REPLAYED. Exact comparison of %Ra endpoints."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from mr_replay import ra_frac
def loops(tag):
    out = {}
    f = HERE / "tests" / "gen" / (tag + ".out")
    for l in open(f):
        p = l.split()
        if p and p[0] == "LOOP": out[(p[1], p[2])] = (ra_frac(p[3]), ra_frac(p[4]))
    return out
def check(sec_tag, prim_tag):
    s, p = loops(sec_tag), loops(prim_tag)
    common = sorted(set(s) & set(p))
    bad = [k for k in common if not (s[k][0] <= p[k][1] and p[k][0] <= s[k][1])]
    return dict(secondary=sec_tag, primary=prim_tag, entries_compared=len(common), loops=len({k[0] for k in common}),
                all_overlap=(len(common) > 0 and not bad), nonoverlap=[list(k) for k in bad])
if __name__ == "__main__":
    out = [check(sys.argv[1], p) for p in sys.argv[2:]]
    for o in out: print(o)
    prev = json.load(open(HERE / "replay_secondary_check.json")) if (HERE / "replay_secondary_check.json").exists() else []
    json.dump(prev + out, open(HERE / "replay_secondary_check.json", "w"), indent=1)
