#!/usr/bin/env python3
"""Ask every peer whether it is safe to launch something heavy here.

Uses the bridge's shared reader rather than parsing peer status files myself.
The point of that reader is that it has NO ACCESSOR RETURNING A PAYLOAD WITHOUT
PASSING THE FRESHNESS GATE -- `rss_mb` on a stale file raises instead of
returning a number, and `busy` is True when a peer is UNKNOWN.

That default is my own missing-file finding restated: UNKNOWN IS NOT IDLE. A
peer whose writer died has not told me it is free; it has told me nothing, and
the natural reading of nothing is what caused the problem in the first place.

I verified the reader against fixtures before depending on it, rather than
taking the description -- fresh, busy, stale, dead-token and malformed-JSON,
all five behaving as documented. My first attempt at that test was invalid: I
wrote fixtures to a temp directory the reader never looks at, so every case
came back UNKNOWN and I nearly reported a bug in their fresh-file handling
from a test that had exercised nothing.

Usage:  python3 preflight.py [required_gb]
Exit 0 = clear to launch, 1 = hold.
"""
import importlib.util
import sys

READER = "/Users/sumit/Github/.claude-coordination/status_read.py"
ME = "quantum"


def load():
    spec = importlib.util.spec_from_file_location("status_read", READER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main(need_gb):
    sr = load()
    peers = [p.stem for p in sorted(sr.D.glob("*.status"))] if hasattr(sr.D, "glob") \
        else [n for n in sr.survey()]
    hold, notes = [], []
    for name in peers:
        if name == ME:
            continue
        s = sr.read_status(name)
        if s.unknown:
            hold.append(f"{name}: UNKNOWN ({s.why}) -- not idle, just silent")
        elif s.busy:
            try:
                notes.append(f"{name}: busy, {s.rss_mb} MB")
            except Exception:
                notes.append(f"{name}: busy")
            hold.append(f"{name}: running a job")
        else:
            notes.append(f"{name}: idle")

    mine = sr.read_status(ME)
    avail = None
    if not mine.unknown:
        avail = mine.raw.get("mem_available_gb") if hasattr(mine, "raw") else None

    print("peers:")
    for n in notes:
        print(f"   {n}")
    if avail is not None:
        print(f"available memory: {avail} GB (need {need_gb} GB)")
        if need_gb and avail < need_gb:
            hold.append(f"only {avail} GB available, need {need_gb}")

    if hold:
        print("\nHOLD:")
        for h in hold:
            print(f"   {h}")
        return 1
    print("\nCLEAR to launch.")
    return 0


if __name__ == "__main__":
    need = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    sys.exit(main(need))
