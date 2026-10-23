"""B17 harness validation (ii): CONTAINMENT. At every checkpoint, the projections (on u1, u2, n_H) of the 8 reference
points of the W0 box (4 corners + 4 edge midpoints; CAPD 128-bit point runs = b17_check with W0 = 0 and CENTRE_OFFSET)
must lie inside the W0 set's projected intervals from the b17_check run (PROJ: absolute at time checkpoints; PROJREL:
relative to the same centre-crossing state at section checkpoints). Measurement validation only (no tightness).
Usage: b17_containment.py set_run.out ref_run1.out [ref_run2.out ...]"""
import sys, re, mpmath as mp
mp.mp.dps = 40
pat = re.compile(r"^(PROJ|PROJREL) (\S+) t=(\S+) (\S+) \[(\S+), (\S+)\]")
def load(fn):
    out = {}
    for l in open(fn):
        m = pat.match(l)
        if m: out[(m.group(2), m.group(3), m.group(4))] = (mp.mpf(m.group(5)), mp.mpf(m.group(6)))
    return out
S = load(sys.argv[1]); refs = [load(f) for f in sys.argv[2:]]
bad = 0; n = 0
for key, (lo, hi) in sorted(S.items(), key=lambda kv: float(kv[0][1])):
    for r, fn in zip(refs, sys.argv[2:]):
        if key not in r: continue
        a, b = r[key]; n += 1
        if not (lo <= a and b <= hi):
            bad += 1; print("NOT CONTAINED", key, fn, "point", mp.nstr(a, 20), "set", mp.nstr(lo, 20), mp.nstr(hi, 20))
missing = [fn for r, fn in zip(refs, sys.argv[2:]) if len(r) < len(S)]
print("containment: %d point-projections checked, %d not contained; reference runs with missing checkpoints: %s" % (n, bad, missing or "none"))
print("CONTAINMENT", "PASS" if bad == 0 and n > 0 else "FAIL")
