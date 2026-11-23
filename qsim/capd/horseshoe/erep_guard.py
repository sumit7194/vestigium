"""erep_guard.py PID LOG -- the shared-box guard for the registered Z-sym run (E_REP_PREREG.md; the Bridge's slot of
2026-11-18). Every 60 s it measures the run's footprint (compressed pages included), swap, memory pressure and free disk,
and stops the run by VERIFIED PID (owner sumit, cwd = horseshoe/tests, command line identical to the one recorded when
the guard was armed, the binary ./mn_so_erep) when:
  - free disk < 5 GB: at once;
  - the run's own footprint > 300 MB: at once (granted < 250 MB; this is a leak catch);
  - (swap used > 2048 MB AND kern.memorystatus_vm_pressure_level >= 2), or level 4 (critical): only if SUSTAINED, i.e.
    the condition held on every sample for 10 minutes. The Bridge's rule of 2026-11-18 16:47, which replaced
    "swap > 2 GB OR level != 1" after the kernel level stuck at 2 (warning) with ~48% of memory free at launch.
SIGTERM loses at most the work since the last state save (CKPT_SEC 1800). There is NO automatic restart: a stopped run
waits for the Bridge. Logs every stop, every start and end of a sustained condition, and a status line every 10 min.
Exits when the run is gone."""
import os, re, signal, subprocess, sys, time
INFORM = "--inform" in sys.argv; sys.argv = [a for a in sys.argv if a != "--inform"]   # memory policy 2026-11-23 (Sumit): memory INFORMS, never kills
pid, LOG = int(sys.argv[1]), sys.argv[2]
CAP_ARG = int(sys.argv[3]) if len(sys.argv) > 3 else None   # optional own-footprint cap in MB (main_redo: 500, the Bridge 2026-11-19 10:29)
TESTS = "/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests"; SUSTAIN = 600; CAP_MB = 300 if CAP_ARG is None else CAP_ARG
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
def sig(sg, why):
    own, cwd, cmd = ident(pid)
    if (own, cwd, cmd) == (own0, cwd0, cmd0): os.kill(pid, sg); log("VERIFIED PID %d -> %s (%s)" % (pid, sg.name, why)); return True
    log("%s (%s) REFUSED by verification: owner=%s cwd=%s cmd=[%s]" % (sg.name, why, own, cwd, cmd)); return False
if INFORM:
    log("guard armed for PID %d (cmd: %s) in INFORM mode (memory policy 2026-11-23): disk < 5 GB -> stop; footprint > %d MB -> WARN; "
        "squeeze begin/end logged; red (level 4) sustained %d s -> PAUSE (SIGSTOP), resume (SIGCONT) on green; no memory kill" % (pid, cmd0, CAP_MB, SUSTAIN))
    k = 0; peak = 0.0; bad_since = None; red_since = None; paused = False; over = False
    while alive(pid):
        fp = footprint_mb(pid); peak = max(peak, fp)
        sw = float(sh("sysctl -n vm.swapusage | awk '{print $6}'").rstrip("M")); pl = sh("sysctl -n kern.memorystatus_vm_pressure_level")
        dk = int(sh("df -g / | tail -1 | awk '{print $4}'"))
        if k % 10 == 0: log("footprint %.0f MB (peak %.0f), swap used %.0f MB, pressure %s, disk free %d GB%s" % (fp, peak, sw, pl, dk, " PAUSED" if paused else ""))
        if dk < 5:
            if paused: sig(signal.SIGCONT, "resume before the disk stop")
            stop("free disk %d GB < 5 GB" % dk)
        if fp > CAP_MB and not over: over = True; log("WARN: run footprint %.0f MB > %d MB (inform only)" % (fp, CAP_MB))
        if fp <= CAP_MB and over: over = False; log("footprint back to %.0f MB" % fp)
        lv = int(pl) if pl.isdigit() else 4
        bad = (sw > 2048 and lv >= 2) or lv >= 4
        if bad and bad_since is None: bad_since = time.time(); log("squeeze begins: swap %.0f MB, pressure %s (WARN, inform only)" % (sw, pl))
        if not bad and bad_since is not None: log("squeeze ended after %.0f s: swap %.0f MB, pressure %s" % (time.time() - bad_since, sw, pl)); bad_since = None
        red_since = (red_since or time.time()) if lv >= 4 else None
        if red_since and not paused and time.time() - red_since >= SUSTAIN: paused = sig(signal.SIGSTOP, "PAUSE: red sustained %.0f s, swap %.0f MB" % (time.time() - red_since, sw))
        if paused and lv == 1: sig(signal.SIGCONT, "RESUME: pressure green"); paused = False
        k += 1; time.sleep(60)
    log("run PID %d gone; guard exits (peak footprint %.0f MB)" % (pid, peak)); sys.exit(0)
log("guard armed for PID %d (cmd: %s); rule: disk < 5 GB or footprint > %d MB at once; (swap > 2048 MB and level >= 2) or level >= 4 sustained %d s" % (pid, cmd0, CAP_MB, SUSTAIN))
k = 0; peak = 0.0; bad_since = None
while alive(pid):
    fp = footprint_mb(pid); peak = max(peak, fp)
    sw = float(sh("sysctl -n vm.swapusage | awk '{print $6}'").rstrip("M")); pl = sh("sysctl -n kern.memorystatus_vm_pressure_level")
    dk = int(sh("df -g / | tail -1 | awk '{print $4}'"))
    if k % 10 == 0: log("footprint %.0f MB (peak %.0f), swap used %.0f MB, pressure %s, disk free %d GB" % (fp, peak, sw, pl, dk))
    if dk < 5: stop("free disk %d GB < 5 GB" % dk)
    if fp > CAP_MB: stop("run footprint %.0f MB > %d MB" % (fp, CAP_MB))
    lv = int(pl) if pl.isdigit() else 4                        # an unreadable level counts as critical
    bad = (sw > 2048 and lv >= 2) or lv >= 4
    if bad and bad_since is None: bad_since = time.time(); log("squeeze begins: swap %.0f MB, pressure %s (stop if it holds %d s)" % (sw, pl, SUSTAIN))
    if not bad and bad_since is not None: log("squeeze ended after %.0f s: swap %.0f MB, pressure %s" % (time.time() - bad_since, sw, pl)); bad_since = None
    if bad and time.time() - bad_since >= SUSTAIN: stop("sustained %.0f s: swap %.0f MB, pressure %s" % (time.time() - bad_since, sw, pl))
    k += 1; time.sleep(60)
log("run PID %d gone; guard exits (peak footprint %.0f MB)" % (pid, peak))
