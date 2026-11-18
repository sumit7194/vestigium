"""erep_guard.py PID LOG -- the shared-box guard for the registered Z-sym run (E_REP_PREREG.md; the Bridge's slot of
2026-11-18). Every 60 s it measures the run's footprint (compressed pages included), swap, memory pressure and free disk,
and stops the run by VERIFIED PID (owner sumit, cwd = horseshoe/tests, command line identical to the one recorded when
the guard was armed, the binary ./mn_so_erep) when:
  - free disk < 5 GB: at once;
  - the run's own footprint > 300 MB: at once (granted < 250 MB; this is a leak catch);
  - swap used > 2048 MB, or kern.memorystatus_vm_pressure_level != 1: only if SUSTAINED, i.e. the condition held on
    every sample for 10 minutes (the Bridge: the run is ~250 MB, so stopping it on someone else's spike buys nothing).
SIGTERM loses at most the work since the last state save (CKPT_SEC 1800). There is NO automatic restart: a stopped run
waits for the Bridge. Logs every stop, every start and end of a sustained condition, and a status line every 10 min.
Exits when the run is gone."""
import os, re, signal, subprocess, sys, time
pid, LOG = int(sys.argv[1]), sys.argv[2]
TESTS = "/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests"; SUSTAIN = 600; CAP_MB = 300
def log(s):
    with open(LOG, "a") as f: f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + s + "\n")
def sh(cmd): return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
def alive(p): return subprocess.run(["ps", "-p", str(p)], capture_output=True).returncode == 0
def ident(p): return sh("ps -o user= -p %d" % p).strip(), sh("lsof -a -p %d -d cwd -Fn 2>/dev/null | sed -n 's/^n//p'" % p), sh("ps -o command= -p %d" % p)
def footprint_mb(p):
    m = re.search(r"Footprint:\s*([\d.]+)\s*(KB|MB|GB)", sh("footprint -p %d 2>/dev/null | head -3" % p))
    return 0.0 if not m else float(m.group(1)) * {"KB": 1 / 1024, "MB": 1, "GB": 1024}[m.group(2)]
own0, cwd0, cmd0 = ident(pid)
if own0 != "sumit" or cwd0 != TESTS or not cmd0.startswith("./mn_so_erep "):
    log("REFUSED to arm on PID %d: owner=%s cwd=%s cmd=[%s]" % (pid, own0, cwd0, cmd0)); sys.exit(1)
def stop(why):
    own, cwd, cmd = ident(pid)
    if (own, cwd, cmd) == (own0, cwd0, cmd0):
        log("VERIFIED PID %d owner=%s cwd=%s cmd=[%s] -> SIGTERM" % (pid, own, cwd, cmd)); os.kill(pid, signal.SIGTERM)
        log("STOP (%s): killed; no automatic restart (resume from the last state save after the Bridge's OK)" % why)
    else: log("STOP (%s) REFUSED by verification: owner=%s cwd=%s cmd=[%s]" % (why, own, cwd, cmd))
    sys.exit(0)
log("guard armed for PID %d (cmd: %s); sustained window %d s; footprint cap %d MB" % (pid, cmd0, SUSTAIN, CAP_MB))
k = 0; peak = 0.0; bad_since = None
while alive(pid):
    fp = footprint_mb(pid); peak = max(peak, fp)
    sw = float(sh("sysctl -n vm.swapusage | awk '{print $6}'").rstrip("M")); pl = sh("sysctl -n kern.memorystatus_vm_pressure_level")
    dk = int(sh("df -g / | tail -1 | awk '{print $4}'"))
    if k % 10 == 0: log("footprint %.0f MB (peak %.0f), swap used %.0f MB, pressure %s, disk free %d GB" % (fp, peak, sw, pl, dk))
    if dk < 5: stop("free disk %d GB < 5 GB" % dk)
    if fp > CAP_MB: stop("run footprint %.0f MB > %d MB" % (fp, CAP_MB))
    bad = (sw > 2048) or (pl != "1")
    if bad and bad_since is None: bad_since = time.time(); log("squeeze begins: swap %.0f MB, pressure %s (stop if it holds %d s)" % (sw, pl, SUSTAIN))
    if not bad and bad_since is not None: log("squeeze ended after %.0f s: swap %.0f MB, pressure %s" % (time.time() - bad_since, sw, pl)); bad_since = None
    if bad and time.time() - bad_since >= SUSTAIN: stop("sustained %.0f s: swap %.0f MB, pressure %s" % (time.time() - bad_since, sw, pl))
    k += 1; time.sleep(60)
log("run PID %d gone; guard exits (peak footprint %.0f MB)" % (pid, peak))
