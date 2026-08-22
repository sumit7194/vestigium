#!/usr/bin/env python3
"""Publish quantum.status by MEASUREMENT, one tick per invocation.

WHY THIS EXISTS. The bridge found that their heartbeat was a `sed` that bumped
`updated` and touched nothing else, so their status read "running, heavy, 5 GB"
for hours after the job finished -- and blocked a peer's launch on an idle
machine. PROTOCOL 6b: `updated` is a claim about every other field, so the
heartbeat rewrites the whole file from live measurement or writes nothing.

Checking my own side found the INVERSE bug, and it fails in the worse direction:
there was no quantum.status at all. Four sessions published one; I never had.
A stale-but-present file that says "busy" costs a peer a delay. A MISSING file
means a peer following the protocol sees nothing where a claim should be, and
the natural reading of nothing is "idle" -- so it fails toward COLLISION rather
than toward caution. A dead-man's switch that was never installed does not fail
safe; it fails silent.

Two constraints from the user, honoured here:
  * only OUR processes are ever inspected or reported -- matched on the full
    command path containing the repo root. Other projects' python processes are
    running on this machine and must not be touched or counted.
  * be civil with resources: report honestly so peers can schedule around us.
"""
import json
import os
import re
import subprocess
import sys
import time

REPO = "/Users/sumit/Github/quantum"
OUT = "/Users/sumit/Github/.claude-coordination/quantum.status"
# `heavy` is a convenience flag, and ansatz found the trap in it: a flag DERIVED
# FROM A MEASUREMENT but THRESHOLDED AGAINST AN UNVALIDATED CONSTANT is only as
# good as the constant. Theirs flipped at a hardcoded 2048 MB, so a 1912 MB job
# advertised `heavy: false` -- a reader scheduling on that field read "light" for
# a job using nearly 2 GB. The measured half is what gets checked; the typed half
# is what nobody looks at.
#
# Two changes rather than a better constant:
#   * the threshold is RELATIVE to measured usable memory, not absolute, because
#     "heavy" is a claim about what is left for a peer, not about our RSS;
#   * the rule is PUBLISHED IN THE FILE as `heavy_rule`, so a reader can see what
#     the flag means and apply their own instead of trusting an invisible line.
HEAVY_FRACTION = 0.25    # our RSS above this share of usable memory = heavy
HEAVY_FLOOR_MB = 256     # only suppresses "heavy" for trivially small jobs.
                         # Was 1000, which on a constrained box dominated the
                         # fraction and made the flag LESS sensitive exactly when
                         # memory was scarce -- backwards, the same inverted
                         # sensitivity the bridge found in ratio-shaped gates.
MIN_AGE_S = 30           # below this, a match is shell noise, not a job


def _age(et):
    """ps etime -> seconds. Formats: SS, MM:SS, HH:MM:SS, D-HH:MM:SS."""
    d, _, rest = et.partition("-")
    if not rest:
        rest, d = d, "0"
    parts = [int(x) for x in rest.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return int(d)*86400 + parts[0]*3600 + parts[1]*60 + parts[2]


def our_processes():
    """PIDs and RSS for processes whose FULL command path is inside our repo.

    Deliberately NOT a match on 'python' or on a bare script name: this machine
    runs several sibling projects and a loose pattern would both over-report our
    footprint and risk acting on someone else's job.
    """
    try:
        raw = subprocess.run(["ps", "-axo", "pid=,rss=,etime=,command="],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return None                                  # cannot measure -> write nothing
    me = os.getpid()
    rows = []
    for line in raw.splitlines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\S+)\s+(.*)", line)
        if not m:
            continue
        pid, rss_kb, et, cmd = int(m.group(1)), int(m.group(2)), m.group(3), m.group(4)
        if pid == me or os.path.basename(__file__) in cmd:
            continue
        rows.append((pid, rss_kb, _age(et), cmd))

    # Matching on the command string ALONE is not enough, and testing it rather
    # than reading it is what showed that. `python3 qsim/corner_angles.py` --
    # how every study in this repo is actually launched -- appears in ps as a
    # relative path with the repo root nowhere in it, so a cmd-only match
    # reported state=idle with a real job running. That is the COLLISION
    # direction: a peer reads "idle" and launches on top of us.
    #
    # So: a process is ours if the repo root is in its command, OR its working
    # directory is inside the repo. cwd is read via lsof for interpreter-like
    # processes only. This is read-only inspection whose entire purpose is to
    # tell our processes from the sibling projects' -- nothing here signals,
    # kills or otherwise touches a process, ours or anyone's.
    # THE PROBE MUST NOT MATCH THE OBSERVER. bridge found that `pgrep -f` on a
    # script name also matches the shell of a tool call that merely mentions it,
    # so typing a script's name made their own status read "running". Mine was
    # worse: the cmd-path match had NO interpreter filter, so ANY shell whose
    # command line contained the repo path -- including a `cd` into it, or this
    # sentence in a heredoc -- registered as a job. Verified: a bash process
    # doing nothing but `echo "/Users/sumit/Github/quantum"; sleep 45`, launched
    # from outside the repo, published as state=running with its own pid.
    #
    # Cost direction is the bad one: a PHANTOM JOB BLOCKS A PEER'S LAUNCH ON AN
    # IDLE MACHINE, which is the whole failure this file exists to prevent.
    #
    # So both match paths now require the process's actual executable to be a
    # compute interpreter, read from `ps -o comm=` rather than inferred from the
    # command string -- the string is what the observer contaminates.
    try:
        craw = subprocess.run(["ps", "-axo", "pid=,comm="],
                              capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return None
    comm = {}
    for ln in craw.splitlines():
        cm = re.match(r"\s*(\d+)\s+(.*)", ln)
        if cm:
            comm[int(cm.group(1))] = os.path.basename(cm.group(2).strip()).lower()
    INTERP = re.compile(r"^(python|node|julia|ruby|perl|rscript|deno|bun)")

    def is_compute(pid):
        return bool(INTERP.match(comm.get(pid, "")))

    byname = {pid: (rss, age, cmd) for pid, rss, age, cmd in rows}
    direct = {pid for pid, _, _, cmd in rows if REPO in cmd and is_compute(pid)}
    cand = [pid for pid, _, _, _ in rows if pid not in direct and is_compute(pid)]
    cwd_ours = set()
    if cand:
        try:
            out = subprocess.run(["lsof", "-a", "-d", "cwd", "-Fpn",
                                  "-p", ",".join(map(str, cand))],
                                 capture_output=True, text=True, timeout=20).stdout
            cur = None
            for ln in out.splitlines():
                if ln.startswith("p"):
                    cur = int(ln[1:])
                elif ln.startswith("n") and cur is not None:
                    d = ln[1:]
                    if d == REPO or d.startswith(REPO + os.sep):
                        cwd_ours.add(cur)
        except Exception:
            return None                              # cannot classify -> write nothing

    # AGE GATE. Counting every python whose cwd is the repo made a 200 ms
    # one-liner flip state to "running" -- the bridge's own failure direction:
    # a status that says busy while idle costs a peer a launch window. Age, not
    # command shape, is the right discriminator: a peer cares about sustained
    # load, and a heredoc doing real work still crosses the threshold and gets
    # reported. Younger matches are kept in `transient` so nothing is hidden,
    # and their RSS still counts toward the total.
    procs, transient = [], []
    for pid in sorted(direct | cwd_ours):
        rss_kb, age, cmd = byname[pid]
        rec = {"pid": pid, "rss_mb": round(rss_kb/1024, 1), "age_s": age,
               "cmd": cmd[:110], "matched_by": "cmd" if pid in direct else "cwd"}
        (procs if age >= MIN_AGE_S else transient).append(rec)
    return procs, transient


def memory_gb():
    """(strict_free, available) in GB, from vm_stat, page size PARSED not assumed.

    THE PAGE SIZE HERE IS 16384, NOT 4096. A sibling hardcoded 4096 and
    mis-reported memory; on this machine that assumption is wrong by 4x.

    And the harder half, found by reconciling against ansatz's number: reporting
    only `free + speculative` UNDERSTATED available memory by 12x -- 0.59 GB
    published against 7.22 GB actually available -- because macOS parks
    reclaimable pages in `inactive` (6.57 GB of it here) rather than leaving them
    free. A peer scheduling a 4.75 GB run against my published 0.59 GB would have
    deferred on a machine with ample room. That is a FALSE STOP: conservative in
    direction, but still a wrong number published into a channel others schedule
    against, which is the exact failure I had just warned two sessions about.

    So both are published, labelled, with the rule stated in the file:
      strict    free + speculative           -- what is untouched right now
      available + inactive + purgeable       -- what a new allocation can have
    """
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                             timeout=10).stdout
    except Exception:
        return None, None
    pm = re.search(r"page size of (\d+) bytes", out)
    if not pm:
        return None, None
    page = int(pm.group(1))

    def pages(label):
        for line in out.splitlines():
            if line.startswith(label):
                return int(re.sub(r"\D", "", line))*page/1024**3
        return 0.0

    strict = pages("Pages free:") + pages("Pages speculative:")
    avail = strict + pages("Pages inactive:") + pages("Pages purgeable:")
    return round(strict, 2), round(avail, 2)


def disk_free_gb():
    try:
        st = os.statvfs(REPO)
        return round(st.f_bavail*st.f_frsize/1024**3, 1)
    except Exception:
        return None


PIDFILE = os.path.join(REPO, ".heartbeat.pid")


def writer_pid():
    """PID of the long-lived heartbeat loop, from its pidfile, verified with ps.

    ansatz published `$$` -- the status script's own PID, dead milliseconds
    later -- so every read resolved to UNKNOWN forever. Their rule: a liveness
    token guaranteed dead is worse than an absent one, because always-dead looks
    like a working mechanism failing safe.

    My first fix used `pgrep -f status_heartbeat_loop.sh` and had the mirror-image
    defect: PGREP CANNOT SEE THE CALLER'S OWN ANCESTOR. From a child of the loop
    -- which is exactly what a tick is -- `pgrep -f <loop>` returns rc=1 and an
    empty string, while `ps` shows the loop plainly. So it resolved correctly to
    the loop's PID in every hand-test (run from a different process tree) and to
    None on every real tick. A token that is always absent in production and
    always correct under test.

    Isolated by running it, not reading it: a child of selftest_loop.sh could not
    pgrep `selftest_loop.sh` (empty) but did find the unrelated real loop.

    So: the loop writes its own $$ to a pidfile; this reads it and verifies with
    `ps` that the PID is BOTH alive AND still the heartbeat -- a bare `ps -p`
    would happily certify an unrelated process that inherited a recycled PID.
    """
    try:
        with open(PIDFILE) as fh:
            pid = int(fh.read().strip())
    except Exception:
        return None                                  # no pidfile -> no heartbeat
    try:
        out = subprocess.run(["ps", "-p", str(pid), "-o", "command="],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return None
    return pid if "status_heartbeat_loop.sh" in out else None


def main():
    got = our_processes()
    procs, transient = (None, []) if got is None else got
    mem, avail = memory_gb()
    disk = disk_free_gb()

    # 6b, enforced: if ANY field cannot be measured, write NOTHING and let the
    # file be seen to go stale. A partially-measured status with a fresh
    # timestamp is exactly the failure this file exists to avoid.
    if procs is None or mem is None or avail is None or disk is None:
        print("measurement failed — writing nothing, letting the file go stale",
              file=sys.stderr)
        return 1

    rss = round(sum(p["rss_mb"] for p in procs + transient), 1)
    usable_mb = (avail + rss/1024)*1024               # available, plus what we hold
    heavy_at = max(HEAVY_FLOOR_MB, HEAVY_FRACTION*usable_mb)
    heavy = rss > heavy_at
    state = "running" if procs else "idle"
    detail = (f"{len(procs)} job(s) from {REPO}, {rss:.0f} MB RSS"
              if procs else
              "idle — no processes from this repo; machine free from our side")

    doc = {
        "session": "quantum", "repo": REPO,
        "state": state, "heavy": heavy,
        "job_pids": [p["pid"] for p in procs],
        "jobs": procs,
        "transient": transient,
        "rss_total_mb": rss,
        "heavy_at_mb": round(heavy_at, 1),
        "heavy_rule": (f"heavy = our RSS > max({HEAVY_FLOOR_MB} MB, "
                       f"{HEAVY_FRACTION:.0%} of usable); usable measured at "
                       f"{usable_mb/1024:.1f} GB this tick"),
        "disk_free_gb": disk,
        "mem_free_gb": mem,                  # strict: free + speculative
        "mem_available_gb": avail,           # + inactive + purgeable -- SCHEDULE ON THIS
        "mem_rule": ("mem_free_gb is free+speculative and UNDERSTATES headroom on "
                     "macOS; mem_available_gb adds inactive+purgeable and is the "
                     "number to schedule against"),
        "writer_pid": writer_pid(),          # long-lived loop, or null if none
        # bridge's reader verifies a token's IDENTITY, not just its liveness, so a
        # recycled PID cannot masquerade as a heartbeat. Their v2 hardcoded the
        # string "keepalive", which would have rejected every peer's differently
        # named loop -> all peers permanently UNKNOWN -> under their busy-when-
        # unknown default, permanent deadlock. A safety default plus an over-tight
        # check is not conservative, it is a system where nobody launches anything.
        # So the match string comes from the writer. This is ours:
        "writer_cmd_match": "status_heartbeat_loop.sh",
        "writer_alive": writer_pid() is not None,
        "stale_after_s": 300,
        "detail": detail,
        "measured": True,
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    tmp = OUT + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(doc, fh)
    os.replace(tmp, OUT)                             # atomic: no half-written status
    print(json.dumps(doc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
