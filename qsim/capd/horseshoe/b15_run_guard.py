"""b15_run_guard.py PID LOG -- shared-box guard for the counted B15 rust run (b15_launch.sh). Every 60 s: whole-tree footprint,
swap, pressure, disk. Stops by signalling the launcher's OWN process group (created by setsid in tools/detach.sh), after
verifying the launcher's owner, cwd and command line are the ones recorded at arming:
  - disk < 5 GB, or the tree's footprint > 2048 MB: at once;
  - (swap > 2048 MB AND level >= 2) or level >= 4, SUSTAINED 600 s (the fleet rule).
No automatic restart (the pcache journal makes a later restart resume exactly)."""
import os, re, signal, subprocess, sys, time
pid, LOG = int(sys.argv[1]), sys.argv[2]; CAP = int(sys.argv[3]) if len(sys.argv) > 3 else 2048; SUSTAIN = 600   # optional cap (MB)
def log(s):
    with open(LOG, "a") as f: f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + s + "\n")
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
def alive(p): return subprocess.run(["ps", "-p", str(p)], capture_output=True).returncode == 0
def ident(p): return sh("ps -o user= -p %d" % p), sh("lsof -a -p %d -d cwd -Fn 2>/dev/null | sed -n 's/^n//p'" % p), sh("ps -o command= -p %d" % p)
def tree(p):
    out, todo = [p], [p]
    while todo:
        q = todo.pop(); kids = [int(x) for x in sh("pgrep -P %d" % q).split()]; out += kids; todo += kids
    return out
def fp(p):
    m = re.search(r"Footprint:\s*([\d.]+)\s*(KB|MB|GB)", sh("footprint -p %d 2>/dev/null | head -3" % p))
    return 0.0 if not m else float(m.group(1)) * {"KB": 1 / 1024, "MB": 1, "GB": 1024}[m.group(2)]
id0 = ident(pid); pg = int(sh("ps -o pgid= -p %d" % pid))
SUFFIX = sys.argv[4] if len(sys.argv) > 4 else "b15_launch.sh"          # the launcher script this guard may stop
if id0[0] != "sumit" or not id0[2].endswith(SUFFIX) or pg != pid:
    log("REFUSED to arm on PID %d: %s pgid %d" % (pid, id0, pg)); sys.exit(1)
def stop(why):
    if ident(pid) == id0: log("VERIFIED launcher PID %d %s -> SIGTERM to its process group %d" % (pid, id0, pg)); os.killpg(pg, signal.SIGTERM)
    else: log("REFUSED: launcher identity changed: %s" % (ident(pid),))
    log("STOP (%s); no automatic restart" % why); sys.exit(0)
log("guard armed for launcher PID %d (%s); disk < 5 GB or tree > %d MB at once; (swap > 2 GB and level >= 2) or level >= 4 sustained %d s" % (pid, id0[2], CAP, SUSTAIN))
k = 0; peak = 0.0; bad = None
while alive(pid):
    f = sum(fp(p) for p in tree(pid)); peak = max(peak, f)
    sw = float(sh("sysctl -n vm.swapusage | awk '{print $6}'").rstrip("M")); pl = sh("sysctl -n kern.memorystatus_vm_pressure_level")
    dk = int(sh("df -g / | tail -1 | awk '{print $4}'")); lv = int(pl) if pl.isdigit() else 4
    if k % 10 == 0: log("footprint %.0f MB (peak %.0f), swap %.0f MB, pressure %s, disk %d GB" % (f, peak, sw, pl, dk))
    if dk < 5: stop("disk %d GB" % dk)
    if f > CAP: stop("tree footprint %.0f MB > %d MB" % (f, CAP))
    b = (sw > 2048 and lv >= 2) or lv >= 4
    if b and bad is None: bad = time.time(); log("squeeze begins: swap %.0f MB, pressure %s" % (sw, pl))
    if not b and bad is not None: log("squeeze ended after %.0f s" % (time.time() - bad)); bad = None
    if b and time.time() - bad >= SUSTAIN: stop("sustained %.0f s: swap %.0f MB, pressure %s" % (time.time() - bad, sw, pl))
    k += 1; time.sleep(60)
log("launcher PID %d gone; guard exits (peak %.0f MB)" % (pid, peak))
