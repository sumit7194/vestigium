"""b15b_g3_guard.py PID -- the shared-box guard for ONE MNFlow G3 reference worker (the Bridge, 2026-11-17: one worker,
1 core, nice 15, whole-tree memory watchdog at ~5 GB, stop if memory pressure turns yellow or swap passes 2 GB; disk stop
at 5 GB free). REVISED 2026-11-18 (the Bridge): the pressure rule is now the Z-sym guard's sustained rule, and the
footprint cap is 1024 MB as a leak catch (the worker runs flat at ~89 MB since the t_eval=[] fix). Every 60 s it measures the FOOTPRINT (compressed pages included; RSS hid 3.3 GB as 19 MB on 2026-10-24) of
the worker and all its descendants, and stops the worker by verified PID (b15b_verify_kill.sh, args "grind 0 1") when:
  - the tree's footprint exceeds 5120 MB (the in-progress task is lost and NOT retried by this guard: a gate question), or
  - kern.memorystatus_vm_pressure_level != 1 (yellow or worse), or swap used > 2048 MB, or free disk < 5 GB.
Completed tasks are safe in mnflow_grind0.jsonl (fsync'ed per line); a later restart of the worker skips them.
Logs to b15b_gates/g3_guard.log: every stop, and the footprint every 10 min. Exits when the worker is gone."""
import re, subprocess, sys, time
from pathlib import Path
H = Path(__file__).resolve().parent; G = H.parent / "horseshoe_results" / "kerr" / "b15b_gates"; LOG = G / "g3_guard.log"
pid = int(sys.argv[1]); CAP_MB = 1024; SUSTAIN = 600
VERIFY = sys.argv[2] if len(sys.argv) > 2 else "grind 0 1"   # the worker args b15b_verify_kill.sh must see (claim workers: "claim <k>")
def log(s):
    with open(LOG, "a") as f: f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + ("[%d] " % pid if len(sys.argv) > 2 else "") + s + "\n")
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
    rc = subprocess.run([str(H / "b15b_verify_kill.sh"), str(pid), VERIFY, str(LOG)]).returncode
    log("STOP (%s): %s; the in-progress task (%s) is lost and not retried by this guard" % (why, "killed" if rc == 0 else "REFUSED by verification", last_task()))
    sys.exit(0)
def last_task():
    lg = G / "mnflow_grind0.jsonl"; return "after %d results" % len(lg.read_text().splitlines()) if lg.exists() else "?"
log("guard armed for worker PID %d (cmd: %s); rule (the Bridge, 2026-11-18 ~20:15, as the Z-sym guard): disk < 5 GB or tree footprint > %d MB at once; (swap > 2048 MB and level >= 2) or level >= 4 sustained %d s" % (pid, sh("ps -o command= -p %d" % pid), CAP_MB, SUSTAIN))
k = 0; peak = 0.0; bad_since = None
while alive(pid):
    fp = sum(footprint_mb(p) for p in tree(pid)); peak = max(peak, fp)
    sw = float(sh("sysctl -n vm.swapusage | awk '{print $6}'").rstrip("M")); pl = sh("sysctl -n kern.memorystatus_vm_pressure_level")
    dk = int(sh("df -g / | tail -1 | awk '{print $4}'"))
    if k % 10 == 0: log("footprint %.0f MB (peak %.0f), swap used %.0f MB, pressure %s, disk free %d GB" % (fp, peak, sw, pl, dk))
    if fp > CAP_MB: stop("whole-tree footprint %.0f MB > %d MB (leak catch)" % (fp, CAP_MB))
    if dk < 5: stop("free disk %d GB < 5 GB" % dk)
    lv = int(pl) if pl.isdigit() else 4                        # an unreadable level counts as critical
    bad = (sw > 2048 and lv >= 2) or lv >= 4
    if bad and bad_since is None: bad_since = time.time(); log("squeeze begins: swap %.0f MB, pressure %s (stop if it holds %d s)" % (sw, pl, SUSTAIN))
    if not bad and bad_since is not None: log("squeeze ended after %.0f s: swap %.0f MB, pressure %s" % (time.time() - bad_since, sw, pl)); bad_since = None
    if bad and time.time() - bad_since >= SUSTAIN: stop("sustained %.0f s: swap %.0f MB, pressure %s" % (time.time() - bad_since, sw, pl))
    k += 1; time.sleep(60)
log("worker PID %d gone; guard exits (peak footprint %.0f MB)" % (pid, peak))
