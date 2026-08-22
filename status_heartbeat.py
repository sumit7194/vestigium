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
HEAVY_MB = 1500          # above this total RSS, warn peers off a big launch
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
    byname = {pid: (rss, age, cmd) for pid, rss, age, cmd in rows}
    direct = {pid for pid, _, _, cmd in rows if REPO in cmd}
    cand = [pid for pid, _, _, cmd in rows
            if pid not in direct
            and re.search(r"(python|node|julia|ruby|perl|Rscript)", cmd, re.I)]
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


def mem_free_gb():
    """Free memory from vm_stat, with the page size PARSED, not assumed.

    A sibling hardcoded 4096 and mis-reported memory on a machine that does not
    use a 4 KiB page. Also avoids `memory_pressure`, whose 'free' is
    reclaimable-inclusive and reads far rosier than it is.
    """
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                             timeout=10).stdout
    except Exception:
        return None
    pm = re.search(r"page size of (\d+) bytes", out)
    if not pm:
        return None
    page = int(pm.group(1))
    free = spec = 0
    for line in out.splitlines():
        if line.startswith("Pages free:"):
            free = int(re.sub(r"\D", "", line))
        elif line.startswith("Pages speculative:"):
            spec = int(re.sub(r"\D", "", line))
    return round((free + spec)*page/1024**3, 1)


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
    mem = mem_free_gb()
    disk = disk_free_gb()

    # 6b, enforced: if ANY field cannot be measured, write NOTHING and let the
    # file be seen to go stale. A partially-measured status with a fresh
    # timestamp is exactly the failure this file exists to avoid.
    if procs is None or mem is None or disk is None:
        print("measurement failed — writing nothing, letting the file go stale",
              file=sys.stderr)
        return 1

    rss = round(sum(p["rss_mb"] for p in procs + transient), 1)
    heavy = rss > HEAVY_MB
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
        "disk_free_gb": disk, "mem_free_gb": mem,
        "writer_pid": writer_pid(),          # long-lived loop, or null if none
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
