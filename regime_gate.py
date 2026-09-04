#!/usr/bin/env python3
"""VALIDITY gate: is the run in a regime where its quantity means anything?

Distinct from preflight.py, which is a READINESS gate -- "not yet" (is the box
free?). This is "not at all" (is the physics window open?). The distinction is
thebridge-a2's, sharpened: order by cost-to-falsify, and a check whose failure
is cheap to discover early must not sit behind a queue. await_box.sh previously
waited hours for memory and then launched, with no validity check anywhere --
so a run doomed by its own parameters would have been discovered only after the
box freed and the multi-hour job started. A control that waits for the box has
been made expensive by SCHEDULING, not by content.

The window, established the hard way in qsim/CORNER_BOUND_FINDINGS.md:

    R << xi << L

Both are needed and they fail independently. corner_angles had R/xi = 0.14
(fine) and xi/L = 0.62 (broken) and was 13.3% below a theorem.

Cost: microseconds. It should always have run first.
"""
import sys

def check(L, m, regions, label="", strict_R=0.25, strict_xi=0.35):
    xi = 1.0/m
    Rmax = max(regions)
    r1, r2 = Rmax/xi, xi/L
    ok1, ok2 = r1 < strict_R, r2 < strict_xi
    print(f"{label}  L={L} m={m:g} xi={xi:.0f} Rmax={Rmax}")
    print(f"    R/xi  = {r1:.3f}  (< {strict_R} needed)   {'ok' if ok1 else 'BROKEN'}")
    print(f"    xi/L  = {r2:.3f}  (< {strict_xi} needed)  {'ok' if ok2 else 'BROKEN'}")
    if not (ok1 and ok2):
        print(f"    -> the log coefficient extracted here is NOT the universal one.")
    return ok1 and ok2

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        L, m = float(sys.argv[1]), float(sys.argv[2])
        regions = [float(x) for x in sys.argv[3:]]
        sys.exit(0 if check(L, m, regions, "proposed run:") else 1)
    # no args: audit the committed studies
    import json, glob
    bad = 0
    for f in sorted(glob.glob("qsim/corner_s*.json")):
        d = json.load(open(f))
        if "L" not in d or not d.get("ls"):
            continue
        bad += not check(d["L"], d["m"], d["ls"], f"{f}: s={d.get('s')}")
    print(f"\n{bad} committed run(s) sit outside the window." if bad else "\nall inside")
    sys.exit(0)
