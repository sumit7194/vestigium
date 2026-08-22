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
import json
import sys
import time

READER = "/Users/sumit/Github/.claude-coordination/status_read.py"
CONFIRM_S = 70   # must exceed the slowest peer tick, or advance cannot be seen
ME = "quantum"


def load():
    """Load the shared reader, or fail EXPLICITLY.

    Before this, a missing or broken reader produced a raw traceback that
    happened to exit 1. That is fail-closed BY ACCIDENT, not by design -- the
    same "correct by construction rather than earned" distinction that applied
    to my JSON staying valid under load. It matters here because a precondition
    check is consulted by someone deciding whether to do something else, and a
    traceback is not a decision: anyone reading the OUTPUT rather than the exit
    code gets no answer at all, and one `|| true` in a caller turns an accident
    into a launch.

    bridge's prediction is that defects concentrate in things consulted as a
    PRECONDITION rather than read as a RESULT, because nobody is auditing them
    at the moment they are used. This file is one of those, so its failure mode
    is stated rather than inherited.
    """
    try:
        spec = importlib.util.spec_from_file_location("status_read", READER)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    except Exception as e:
        print(f"HOLD: cannot load the shared reader ({type(e).__name__}: {e})")
        print("  No information about peers is available, and NO INFORMATION IS")
        print("  NOT PERMISSION. Refusing to declare the machine clear.")
        sys.exit(1)


def main(need_gb):
    sr = load()
    peers = [p.stem for p in sorted(sr.D.glob("*.status"))] if hasattr(sr.D, "glob") \
        else [n for n in sr.survey()]
    hold, notes = [], []
    for name in peers:
        if name == ME:
            continue
        # ONE implementation of the safety rule, not two. bridge shipped
        # read_status_confirmed() after my fail-open, and two divergent copies of
        # a safety rule is its own hazard: mine would drift, and the drift would
        # be invisible because both would keep returning plausible answers.
        # Verified theirs against my own fail-open fixture before depending on
        # it -- live writer + dead token + 4750 MB job -> busy=True, readable;
        # dead writer, identical file shape -> stays UNKNOWN.
        try:
            s = (sr.read_status_confirmed(name, wait_s=CONFIRM_S)
                 if hasattr(sr, "read_status_confirmed") else sr.read_status(name))
        except Exception as e:
            # read_status documented "never raises" and four of five malformed
            # fixtures raised until bridge tested it. An untested docstring claim
            # is an assertion about the code sitting in the code. Peers change
            # their schemas -- two did today -- so a malformed peer file must
            # cost us a HOLD, never a traceback.
            hold.append(f"{name}: unreadable ({type(e).__name__}) -- no information is not permission")
            continue
        if s.unknown:
            # AN UNKNOWN NEEDS A WAY OUT, NOT JUST A WAY IN. Holding on every
            # UNKNOWN is correct as a default and a deadlock as a policy: a stale
            # token never expires, so a peer whose writer restarted without
            # refreshing its token is invisible-as-busy FOREVER. Two individually
            # correct conservative choices composing into a system that permits
            # nothing -- the third time that shape has appeared today.
            #
            # confirm_writer() is the exit: it samples mtime twice more than a
            # tick apart, because only mtime ADVANCE separates "writer alive with
            # a stale token" from "writer died 30 seconds ago". A single fresh
            # mtime cannot tell those apart, and accepting one would delete the
            # token's only unique capability -- detecting writer death about a
            # timeout earlier than staleness can.
            hold.append(f"{name}: UNKNOWN ({s.why}) -- not idle, just silent")
            continue
        if s.busy:
            try:
                notes.append(f"{name}: BUSY, {s.rss_mb} MB")
            except Exception:
                notes.append(f"{name}: BUSY")
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
