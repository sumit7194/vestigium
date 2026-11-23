"""erep_cost_watch.py PID RUN_OUT LOG -- the A3 stop conditions not covered by erep_guard.py (E_REP_PREREG.md Amendment A3).
Every 60 s it reads RUN_OUT and stops the run by VERIFIED PID (owner sumit, cwd = horseshoe/tests, command line identical
to the one recorded when armed, binary ./mn_so_erep) when:
  - a HARNESS-ERROR line appears;
  - the first run.out line from this process is not '# RESUMED ... next checkpoint 3' (checked once it exists, or after
    10 min without it);
  - COST-STOP: the mean wall time per step over the latest 200-step window (from the '# step' lines, logged every 20
    steps) exceeds 2 x 63.9 = 127.9 s/step (baseline: main_redo, 154323 s / 2414 steps).
Logs EARLY-COST once >= 20 steps have run since the resume (mean s/step so far, setup included), a status line every
10 min, and every stop. NO automatic restart. Exits when the run is gone."""
import re, signal, subprocess, sys, time
if sys.argv[1] == "--selftest":   # erep_cost_watch.py --selftest RUN_OUT: the 200-step window rates the watch would compute
    st = [(int(m.group(1)), float(m.group(3))) for m in (re.match(r"^# step (\d+) t=(\S+) .* wall (\d+) s$", l) for l in open(sys.argv[2])) if m]
    rates = [(b[1] - a[1]) / (b[0] - a[0]) for a in st for b in st if b[0] - a[0] == 200]
    print("windows %d, s/step min %.1f max %.1f, would COST-STOP: %s" % (len(rates), min(rates), max(rates), max(rates) > 127.8)); sys.exit(0)
INFORM = "--inform" in sys.argv; sys.argv = [a for a in sys.argv if a != "--inform"]   # memory policy 2026-11-23: load-driven slowness informs only
pid, RUN, LOG = int(sys.argv[1]), sys.argv[2], sys.argv[3]
TESTS = "/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests"; BASE = 63.9; LIMIT = 2 * BASE; WIN = 200
def log(s):
    with open(LOG, "a") as f: f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + s + "\n")
def sh(cmd): return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
def alive(p): return subprocess.run(["ps", "-p", str(p)], capture_output=True).returncode == 0
def ident(p): return sh("ps -o user= -p %d" % p).strip(), sh("lsof -a -p %d -d cwd -Fn 2>/dev/null | sed -n 's/^n//p'" % p), sh("ps -o command= -p %d" % p)
own0, cwd0, cmd0 = ident(pid)
if own0 != "sumit" or cwd0 != TESTS or not cmd0.startswith("./mn_so_erep "):
    log("REFUSED to arm on PID %d: owner=%s cwd=%s cmd=[%s]" % (pid, own0, cwd0, cmd0)); sys.exit(1)
def stop(why):
    if ident(pid) == (own0, cwd0, cmd0):
        log("STOP (%s): SIGTERM to verified PID %d" % (why, pid)); subprocess.run(["kill", "-TERM", str(pid)])
    else:
        log("STOP WANTED (%s) but PID %d no longer matches the armed identity; nothing sent" % (why, pid))
    sys.exit(0)
log(("INFORM mode: " if INFORM else "") + "armed for PID %d (cmd: %s); baseline %.1f s/step, COST-STOP above %.1f s/step over a %d-step window" % (pid, cmd0, BASE, LIMIT, WIN))
t_arm = time.time(); warned = None; early_done = False; last_status = 0; resumed_ok = False
step_re = re.compile(r"^# step (\d+) t=(\S+) .* wall (\d+) s$")
while alive(pid):
    try: lines = open(RUN).read().splitlines()
    except OSError: lines = []
    mine = lines   # main_cont/run.out is a fresh file written only by this run (its '# RESUMED' line precedes the '# mn_so:' header)
    if any("HARNESS-ERROR" in l for l in mine): stop("HARNESS-ERROR line")
    res = [l for l in mine if l.startswith("# RESUMED")]
    if res and not resumed_ok:
        if "next checkpoint 3" not in res[0]: stop("wrong RESUMED line: " + res[0])
        resumed_ok = True; log("RESUMED line OK: " + res[0])
    if not resumed_ok and time.time() - t_arm > 600: stop("no RESUMED line after 10 min")
    st = [(int(m.group(1)), float(m.group(2)), float(m.group(3))) for m in (step_re.match(l) for l in mine) if m]
    s0 = int(re.search(r"steps (\d+)", res[0]).group(1)) if res else None
    if st and s0 is not None and not early_done and st[-1][0] - s0 >= 20:
        log("EARLY-COST: %d steps since resume in %.0f s -> %.1f s/step (baseline %.1f)" % (st[-1][0] - s0, st[-1][2], st[-1][2] / (st[-1][0] - s0), BASE)); early_done = True
    if len(st) >= 2:
        last = st[-1]; prev = [x for x in st if x[0] <= last[0] - WIN]
        if prev:
            p = prev[-1]; rate = (last[2] - p[2]) / (last[0] - p[0])
            if rate > LIMIT and not INFORM: stop("COST-STOP: %.1f s/step over steps %d-%d" % (rate, p[0], last[0]))
            if rate > LIMIT and INFORM and p[0] != warned: warned = p[0]; log("COST-WANT (inform only, policy 2026-11-23): %.1f s/step over steps %d-%d" % (rate, p[0], last[0]))
    if time.time() - last_status > 600:
        last_status = time.time(); log("status: last %s" % (("step %d t=%.6f wall %.0f s" % st[-1]) if st else "no step line yet"))
    time.sleep(60)
log("run PID %d gone; cost watch exits" % pid)
