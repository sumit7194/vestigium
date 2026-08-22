#!/usr/bin/env python3
"""Does the heartbeat really write NOTHING when a measurement fails?

The claim is the file's entire safety property and it sat untested in the file
that states it -- an assertion about the code, inside the code, which is the
same species as the gate's hardcoded `0.496`.

TWO WAYS THIS TEST CAN LIE, both hit in practice, both reported as INVALID
rather than allowed to bank a pass:

  * PATTERN NOT FOUND     -- the mutation never landed
  * INJECTION BROKE SYNTAX -- the subject died of a SyntaxError and "wrote
    nothing" for a reason that has nothing to do with the claim. My first
    attempt was exactly this and printed "claim holds".

  * AND THE CONTROL, which is bridge's addition and the one I missed: an
    UNMUTATED run that MUST publish. Without it, "wrote nothing" three times
    over is indistinguishable from a harness that never writes at all -- which
    is precisely the state my broken first attempt was in. The control converts
    "the subject did not write" into "the subject did not write AND could have."

Run:  python3 test_heartbeat_failsafe.py   (exit 0 = green)
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "status_heartbeat.py")
OUT = "/Users/sumit/Github/.claude-coordination/quantum.status"
TMP = os.path.join(HERE, ".failsafe_mutant.py")

# (name, anchor, replacement) -- anchors are checked, not assumed
MUTANTS = [
    ("our_processes -> None",
     'def our_processes():\n    """', 'def our_processes():\n    return None\n    """'),
    ("memory_gb -> (None, None)",
     'def memory_gb():\n    """', 'def memory_gb():\n    return None, None\n    """'),
    ("disk_free_gb -> None",
     'def disk_free_gb():\n', 'def disk_free_gb():\n    return None\n'),
    ("vm_stat missing a label",
     'out = subprocess.run(["vm_stat"], capture_output=True, text=True,\n'
     '                             timeout=10).stdout',
     'out = subprocess.run(["vm_stat"], capture_output=True, text=True,\n'
     '                             timeout=10).stdout\n'
     '        out = "\\n".join(l for l in out.splitlines()\n'
     '                        if not l.startswith("Pages inactive:"))'),
]


def loop_running():
    r = subprocess.run(["pgrep", "-f", "vestigium_wr_9f2a4c"],
                       capture_output=True, text=True)
    return [int(x) for x in r.stdout.split() if x.strip().isdigit()]


def snapshot():
    return (open(OUT).read(), os.path.getmtime(OUT)) if os.path.exists(OUT) else ("", 0)


def run(path):
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, cwd=HERE)
    time.sleep(0.25)
    return r


def main():
    src = open(SRC).read()
    results = []

    # THE SUBJECT WRITES TO A FILE A BACKGROUND COPY OF ITSELF ALSO WRITES.
    # With the loop live, a real 60s tick landing between the two snapshots is
    # indistinguishable from the mutant publishing -- which produced a FAIL on
    # `memory_gb` that vanished the moment the loop was stopped. The harness was
    # being corrupted by the very mechanism it tests, and the corruption looks
    # exactly like the defect being hunted.
    #
    # So the loop is stopped for the duration and restarted after. Stopping goes
    # through stop_heartbeat.sh, which kills by PID from the pidfile -- never a
    # name pattern (PROTOCOL 6e).
    was_running = bool(loop_running())
    if was_running:
        subprocess.run([os.path.join(HERE, "stop_heartbeat.sh")],
                       capture_output=True, text=True)
        time.sleep(2)
        if loop_running():
            print("REFUSING TO RUN: could not stop the heartbeat loop. With it live, "
                  "its own ticks are indistinguishable from the mutant publishing.")
            return 2

    for name, old, new in MUTANTS:
        if old not in src:
            results.append((name, "INVALID", "pattern not found -- mutation never landed"))
            continue
        mutated = src.replace(old, new, 1)
        try:
            compile(mutated, TMP, "exec")
        except SyntaxError as e:
            results.append((name, "INVALID", f"injection broke syntax ({e.msg})"))
            continue
        open(TMP, "w").write(mutated)
        before, bmt = snapshot()
        r = run(TMP)
        after, amt = snapshot()
        rewrote = (after != before) or (amt != bmt)
        why = (r.stderr.strip().splitlines() or ["(silent)"])[-1][:58]
        results.append((name, "FAIL" if rewrote else "PASS",
                        "published despite a failed measurement" if rewrote
                        else f"wrote nothing; said: {why}"))

    # THE CONTROL. Unmutated, must publish -- otherwise every PASS above is void.
    before, bmt = snapshot()
    r = run(SRC)
    after, amt = snapshot()
    published = (after != before) or (amt != bmt)
    results.append(("CONTROL: no mutation", "PASS" if published else "FAIL",
                    "published a real tick" if published
                    else "did NOT publish -- every PASS above is meaningless"))

    if os.path.exists(TMP):
        os.remove(TMP)

    if was_running:                                   # leave the box as we found it
        subprocess.Popen(["nohup", os.path.join(HERE, "vestigium_wr_9f2a4c.sh")],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
        time.sleep(3)
        results.append(("heartbeat restarted after test",
                        "PASS" if loop_running() else "FAIL",
                        "loop is running again" if loop_running()
                        else "LOOP LEFT DOWN -- status will go stale"))

    print("=" * 72)
    print("heartbeat fail-safe: does a failed measurement publish anything?")
    print("=" * 72)
    for name, verdict, note in results:
        print(f"  {verdict:8s} {name:26s} {note}")
    bad = [r for r in results if r[1] != "PASS"]
    print("-" * 72)
    if bad:
        print(f"RED -- {len(bad)} not passing (INVALID counts as not passing: a test "
              f"that did not run is not a test that succeeded)")
        return 1
    print("GREEN -- failed measurements publish nothing, and the control proves "
          "the harness can write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
