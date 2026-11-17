"""b15b_g3_guard.py PID -- the shared-box guard for ONE MNFlow G3 reference worker (the Bridge, 2026-11-17: one worker,
1 core, nice 15, whole-tree memory watchdog at ~5 GB, stop if memory pressure turns yellow or swap passes 2 GB; disk stop
at 5 GB free). Every 60 s it measures the FOOTPRINT (compressed pages included; RSS hid 3.3 GB as 19 MB on 2026-10-24) of
the worker and all its descendants, and stops the worker by verified PID (b15b_verify_kill.sh, args "grind 0 1") when:
  - the tree's footprint exceeds 5120 MB (the in-progress task is lost and NOT retried by this guard: a gate question), or
  - kern.memorystatus_vm_pressure_level != 1 (yellow or worse), or swap used > 2048 MB, or free disk < 5 GB.
Completed tasks are safe in mnflow_grind0.jsonl (fsync'ed per line); a later restart of the worker skips them.
Logs to b15b_gates/g3_guard.log: every stop, and the footprint every 10 min. Exits when the worker is gone."""
import re, subprocess, sys, time
from pathlib import Path
H = Path(__file__).resolve().parent; G = H.parent / "horseshoe_results" / "kerr" / "b15b_gates"; LOG = G / "g3_guard.log"
pid = int(sys.argv[1]); CAP_MB = 5120
def log(s):
    with open(LOG, "a") as f: f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + s + "\n")
def sh(cmd): return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
def alive(p): return subprocess.run(["ps", "-p", str(p)], capture_output=True).returncode == 0
def tree(p):
    out, todo = [p], [p]
    while todo:
        q = todo.pop(); kids = [int(x) for x in sh("pgrep -P %d" % q).split()]; out += kids; todo += kids
    return out
def footprint_mb(p):
    m = re.search(r"Footprint:\s*([\d.]+)\s*(KB|MB|GB)", sh("footprint -p %d 2>/dev/null | head -3" % p))
    return 0.0 if not m else float(m.group(1)) * {"KB": 1 / 1024, "MB": 1, "GB": 1024}[m.group(2)]
def stop(why):
    rc = subprocess.run([str(H / "b15b_verify_kill.sh"), str(pid), "grind 0 1", str(LOG)]).returncode
    log("STOP (%s): %s; the in-progress task (%s) is lost and not retried by this guard" % (why, "killed" if rc == 0 else "REFUSED by verification", last_task()))
    sys.exit(0)
def last_task():
    lg = G / "mnflow_grind0.jsonl"; return "after %d results" % len(lg.read_text().splitlines()) if lg.exists() else "?"
log("guard armed for worker PID %d (cmd: %s)" % (pid, sh("ps -o command= -p %d" % pid)))
k = 0; peak = 0.0
while alive(pid):
    fp = sum(footprint_mb(p) for p in tree(pid)); peak = max(peak, fp)
    sw = float(sh("sysctl -n vm.swapusage | awk '{print $6}'").rstrip("M")); pl = sh("sysctl -n kern.memorystatus_vm_pressure_level")
    dk = int(sh("df -g / | tail -1 | awk '{print $4}'"))
    if k % 10 == 0: log("footprint %.0f MB (peak %.0f), swap used %.0f MB, pressure %s, disk free %d GB" % (fp, peak, sw, pl, dk))
    if fp > CAP_MB: stop("whole-tree footprint %.0f MB > %d MB" % (fp, CAP_MB))
    if pl != "1": stop("memory pressure level %s (not normal)" % pl)
    if sw > 2048: stop("swap used %.0f MB > 2048 MB" % sw)
    if dk < 5: stop("free disk %d GB < 5 GB" % dk)
    k += 1; time.sleep(60)
log("worker PID %d gone; guard exits (peak footprint %.0f MB)" % (pid, peak))
