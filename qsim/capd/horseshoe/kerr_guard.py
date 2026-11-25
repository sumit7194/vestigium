"""kerr_guard.py PID [PID ...] -- standalone guard for hs_cover kerr_e processes NOT under the B15d runner (B15e A4,
2026-11-25). It runs b15d_run.guard_loop (tested in tests/disk_policy_test.py) on the given PIDs, so the rules are
Sumit's no-caps rule: memory and footprint INFORM; sustained red pressure PAUSES and green RESUMES; disk < 3 GB PAUSES,
> 4 GB RESUMES, < 2 GB ALERTS. It NEVER kills. Each PID's command line is recorded at arming and every signal is
verified against it. Logs to b15d/run.log (as the runner did). Exits when all its PIDs are gone."""
import sys, threading, time
import b15d_run as R

pids = [int(a) for a in sys.argv[1:]]
for p in pids:
    cmd = R.sh("ps -o command= -p %d" % p); own = R.sh("ps -o user= -p %d" % p)
    if own != "sumit" or not cmd.startswith(str(R.HERE)):
        R.log("kerr_guard REFUSED to arm on PID %d (owner %s, cmd %s)" % (p, own, cmd)); continue
    R.CHILD[p] = ("kerr_guard/" + cmd.rsplit("/", 1)[-1], cmd)
R.log("kerr_guard armed PID %s on %s (no-caps rule: pause/resume/inform only)" % (__import__("os").getpid(), sorted(R.CHILD)))
threading.Thread(target=R.guard_loop, daemon=True).start()
while any(R.sh("ps -o pid= -p %d" % p) for p in list(R.CHILD)):
    for p in list(R.CHILD):
        if not R.sh("ps -o pid= -p %d" % p): R.log("kerr_guard: PID %d (%s) gone" % (p, R.CHILD.pop(p)[0]))
    time.sleep(60)
R.log("kerr_guard: all PIDs gone; exits")
