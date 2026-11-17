"""wrap_run.py -- the wrapping test's runner (WRAPPING_TEST.md). Launch fully detached at nice 10 (children inherit it):
    nice -n 10 tools/detach.sh <W>/run.log <W> <venv python> -u <W>/wrap_run.py
1. K00/K01, the hook controls: mn_so_wrap's kr_ref (t 0 -> 0.9, W0 1e-6) with the dump OFF and ON must be byte-identical
   to the saved so_mn/kr_ref. No segment starts before both are IDENTICAL.
2. The segments of segments.tsv, in file order (A, then B, then C), at most MAXJ at once. Each starts from a copy of an
   original grid save, runs the fix-test configuration (SO_FIXED_REDO=1, SO_DIAG_FROM=285, GUARD_RATIO=0.02, the same
   save grid SAVE_FROM=287.5 SAVE_DT=0.25) with WRAP_DUMP on, and stops after its STOP_AFTER_T; wrap_check.py then
   compares it with the original run. The first non-IDENTICAL result stops all further launches (running ones finish
   and are checked).
3. When every job is IDENTICAL: wrap_adjoint.py for chains A, B and C+A; then the file DONE.
Checkpointing: a segment is the unit (<= ~2.5 h). After an interruption, re-launching skips jobs whose CHECK.txt says
IDENTICAL and reruns any other from its original grid save (its own outputs are rewritten from the start).
Shared-box guards (the Bridge, 2026-11-17), every 60 s:
  - free disk < 5 GB: stop every running job by verified PID, launch nothing, exit;
  - memory pressure not normal (kern.memorystatus_vm_pressure_level != 1) or swap used > 2048 MB: launch nothing while it
    lasts (the G3 worker's own guard stops that worker at once); if it lasts 10 min, stop the running jobs by verified PID
    and exit (rerun later from the segment boundary).
Every stop is by explicit PID, after checking that the process's command line starts with this harness binary."""
import os, subprocess, sys, time
from pathlib import Path
W = Path(__file__).resolve().parent; T = Path("/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests")
FT = W.parent / "fix_test"; CP = W.parent.parent / "mn_smoke"; KR = W.parent / "kr_ref"
PY = "/Users/sumit/Github/quantum/sims/.venv/bin/python"; BIN = str(T / "mn_so_wrap"); MAXJ = 3; RUNS = W / "runs"
def log(s): print(time.strftime("%Y-%m-%d %H:%M:%S ") + s, flush=True)
ROWS = [l.split("\t") for l in (W / "segments.tsv").read_text().splitlines() if l and not l.startswith("#")]
SEG = {r[0]: r for r in ROWS}; QUEUE = ["K00", "K01"] + [r[0] for r in ROWS]
def ok(i): p = RUNS / i / "CHECK.txt"; return p.exists() and p.read_text().splitlines()[0] == "IDENTICAL"
def sh(cmd): return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
def verified_kill(p, i):
    cmd = sh("ps -o command= -p %d" % p.pid)
    if cmd.startswith(BIN + " "): log("VERIFIED PID %d (%s) cmd=[%s] -> SIGTERM" % (p.pid, i, cmd)); p.terminate()
    else: log("REFUSED to stop PID %d (%s): cmd=[%s]" % (p.pid, i, cmd))
def launch(i):
    d = RUNS / i; d.mkdir(parents=True, exist_ok=True)
    for f in list(d.glob("st.t*")) + [d / n for n in ("dump", "out", "CHECK.txt", "st")]:   # only this harness's own outputs
        if f.exists(): f.unlink()
    env = dict(os.environ)
    if i.startswith("K0"):
        if i == "K01": env["WRAP_DUMP"] = str(d / "dump")
        argv = [BIN, "1/1000000", str(CP / "b17_cp_1e-6.txt"), str(d / "st"), "0.9"]
    else:
        r = SEG[i]; (d / "st").write_bytes((FT / r[3]).read_bytes())
        env.update(SO_FIXED_REDO="1", SO_DIAG_FROM="285", GUARD_RATIO="0.02", SAVE_FROM="287.5", SAVE_DT="0.25", CKPT_SEC="1e9",
                   WRAP_DUMP=str(d / "dump"), STOP_AFTER_T=r[4])
        argv = [BIN, r[1], str(CP / r[2]), str(d / "st"), "291.9"]
    p = subprocess.Popen(argv, cwd=T, env=env, stdout=open(d / "out", "w"), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    log("launched %s PID %d" % (i, p.pid)); return p
def check(i):
    d = RUNS / i
    if i.startswith("K0"):
        same = (d / "st").exists() and (d / "st").read_bytes() == KR.read_bytes()
        (d / "CHECK.txt").write_text(("IDENTICAL" if same else "DIFFERS: final state is not byte-identical to so_mn/kr_ref") +
                                     "\ncontrol %s: mn_so_wrap kr_ref (t 0 -> 0.9, W0 1e-6), dump %s, vs so_mn/kr_ref\n" % (i, "ON" if i == "K01" else "OFF"))
    else:
        rc = subprocess.run([PY, str(W / "wrap_check.py"), i], capture_output=True, text=True)
        if rc.returncode != 0: (d / "CHECK.txt").write_text("DIFFERS: wrap_check.py failed\n" + rc.stderr)
    r = (d / "CHECK.txt").read_text().splitlines()[0]; log("%s finished: %s" % (i, r)); return r == "IDENTICAL"
hold_since = None
def guards():                                      # 0 ok, 1 hold, 2 stop now
    global hold_since
    dk = int(sh("df -g / | tail -1 | awk '{print $4}'")); sw = float(sh("sysctl -n vm.swapusage | awk '{print $6}'").rstrip("M"))
    pl = sh("sysctl -n kern.memorystatus_vm_pressure_level")
    if dk < 5: log("GUARD: disk free %d GB < 5" % dk); return 2
    if pl != "1" or sw > 2048:
        if hold_since is None: hold_since = time.time(); log("GUARD HOLD: pressure level %s, swap used %.0f MB" % (pl, sw))
        if time.time() - hold_since >= 600: log("GUARD: the memory condition lasted 10 min"); return 2
        return 1
    if hold_since is not None: log("GUARD HOLD cleared")
    hold_since = None; return 0
log("runner start (pid %d, nice %d), queue %s; already IDENTICAL: %s" % (os.getpid(), os.nice(0), " ".join(QUEUE), " ".join(i for i in QUEUE if ok(i)) or "none"))
running, stop, tried = {}, False, set()
while True:
    for i, p in list(running.items()):
        if p.poll() is not None:
            log("%s exited with code %d" % (i, p.returncode)); del running[i]
            if not check(i): stop = True; log("STOP: no further launches (first non-IDENTICAL: %s)" % i)
    g = guards()
    if g == 2:
        for i, p in running.items(): verified_kill(p, i)
        log("runner STOPPED by a guard"); sys.exit(1)
    if g == 0 and not stop:
        for i in QUEUE:
            if len(running) >= MAXJ: break
            if i in running or i in tried or ok(i): continue
            if not i.startswith("K0") and not (ok("K00") and ok("K01")): break   # the controls first
            tried.add(i); running[i] = launch(i)
    if not running:
        if stop: log("runner done (STOPPED at a difference)"); sys.exit(1)
        left = [i for i in QUEUE if not ok(i)]
        if not left:
            ids = lambda c: [r[0] for r in ROWS if r[0].startswith(c)]
            for name, seq in (("A", ids("A")), ("B", ids("B")), ("CA", ids("C") + ids("A"))):
                rc = subprocess.run([PY, str(W / "wrap_adjoint.py"), name] + seq, capture_output=True, text=True)
                log("analysis %s %s" % (name, "written" if rc.returncode == 0 else "FAILED: " + (rc.stdout + rc.stderr).strip()[-300:]))
            (W / "DONE").write_text(time.strftime("%Y-%m-%d %H:%M:%S\n")); log("runner DONE"); sys.exit(0)
        if g == 0: log("runner: nothing launchable but not IDENTICAL: %s" % " ".join(left)); sys.exit(1)
    time.sleep(60)
