"""Wrapping test (WRAPPING_TEST.md): the REPRODUCTION check of one segment against the original fix-test run.
Usage: wrap_check.py <segment id>      (reads segments.tsv and runs/<id>/; writes runs/<id>/CHECK.txt; prints its 1st line)
IDENTICAL only if ALL of these hold:
  1. every listed original grid save (fix_test/<name>) is byte-identical to this segment's own save of the same name;
  2. every DIAG line of the segment equals the original run's DIAG line(s) of the same step number (all occurrences;
     the trailing ' eratio ...' field is ignored, since the pre-289.75 part of the original was run by the build without it);
  3. every PROJ and CHECKPOINT line of the segment occurs verbatim in the original log;
  4. the segment ended by STOP_AFTER_T, printed an MN-SO line, and printed no THREW / GUARD line;
  5. the dump has one complete STEP record per step the segment took, numbered consecutively.
Otherwise DIFFERS (with the first reason) -- the runner then launches no further segment."""
import re, sys
from pathlib import Path
W = Path(__file__).resolve().parent; FT = W.parent / "fix_test"
sid = sys.argv[1]; d = W / "runs" / sid
row = [l.split("\t") for l in (W / "segments.tsv").read_text().splitlines() if l and not l.startswith("#") and l.split("\t")[0] == sid][0]
orig_out = FT / ("fix_1e-7.out" if row[1] == "1/10000000" else "fix_1e-6.out")
reasons = []
# 1. grid saves
for name in [] if row[5].strip() == "-" else row[5].strip().split(","):
    a, b = FT / name, d / ("st" + name[name.index(".state") + 6:])
    if not b.exists(): reasons.append("missing own save %s" % b.name)
    elif a.read_bytes() != b.read_bytes(): reasons.append("grid save %s differs from the original" % name)
out = (d / "out").read_text().splitlines(); orig = orig_out.read_text().splitlines()
strip = lambda l: re.sub(r" eratio \S+$", "", l)
od = {}
for l in orig:
    if l.startswith("DIAG step "): od.setdefault(int(l.split()[2]), set()).add(strip(l))
ndiag = 0
for l in out:
    if l.startswith("DIAG step "):
        ndiag += 1; k = int(l.split()[2])
        if k not in od: reasons.append("DIAG step %d not in the original log" % k); break
        if od[k] != {strip(l)}: reasons.append("DIAG step %d differs" % k); break
os_ = set(orig)
for l in out:
    if (l.startswith("PROJ ") or l.startswith("CHECKPOINT ")) and l not in os_: reasons.append("line not in the original: " + l[:80]); break
if not any(l.startswith("STOP_AFTER_T ") for l in out): reasons.append("did not end by STOP_AFTER_T")
if not any(l.startswith("MN-SO ") for l in out): reasons.append("no MN-SO line")
if any(l.startswith("THREW") or l.startswith("GUARD") for l in out): reasons.append("THREW or GUARD")
steps = [int(l.split()[1]) for l in (d / "dump").read_text().splitlines() if l.startswith("STEP ")]
ends = (d / "dump").read_text().count("\nEND\n")
if not steps or steps != list(range(steps[0], steps[0] + len(steps))) or ends != len(steps) or ndiag != len(steps):
    reasons.append("dump records not complete/consecutive (%d STEP, %d END, %d DIAG)" % (len(steps), ends, ndiag))
msg = ("IDENTICAL" if not reasons else "DIFFERS: " + reasons[0]) + "\n"
msg += "segment %s: %d steps (%s..%s), DIAG lines %d, original log %s\n" % (sid, len(steps), steps[0] if steps else "-", steps[-1] if steps else "-", ndiag, orig_out.name)
msg += "".join("  reason: %s\n" % r for r in reasons)
(d / "CHECK.txt").write_text(msg); print(msg.splitlines()[0])
