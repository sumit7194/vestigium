"""SO continuation criterion (fixed with the Bridge BEFORE the recheck, 2026-11-17): every numeric column except the new
'eratio' column must equal the 2026-10-26 record for every step from 1305 through at least 1322, excluding only the last
2 steps before this run's stop time. Compares DIAG lines and '# step' lines (wall time stripped).
Usage: stepcmp.py <new .out> <record .out>"""
import sys, re
def lines(p):
    d = {}
    for l in open(p):
        m = re.match(r"^(DIAG step|# step) (\d+) ", l)
        if not m: continue
        s = int(m.group(2)); l = re.sub(r" eratio \S+", "", l.rstrip("\n")); l = re.sub(r" wall \d+ s$", "", l)
        d.setdefault((m.group(1), s), l)          # first occurrence (a resumed record never repeats a printed step differently)
    return d
new, rec = lines(sys.argv[1]), lines(sys.argv[2])
steps = sorted({s for _, s in new}); last = steps[-1]; hi = last - 2
keys = [k for k in new if 1305 <= k[1] <= hi]
if hi < 1322: print("DIFFERS: run too short (last step %d, compare up to %d < 1322)" % (last, hi)); sys.exit()
bad = [k for k in sorted(keys, key=lambda k: (k[1], k[0])) if rec.get(k) != new[k]]
print(("IDENTICAL: steps 1305-%d (%d lines; last step %d, last 2 excluded)" % (hi, len(keys), last)) if not bad else
      "DIFFERS at %s: new %s | record %s" % (bad[0], new[bad[0]][:160], (rec.get(bad[0]) or "MISSING")[:160]))
