"""Disk-floor policy tests (the Bridge, 2026-11-25): pause < 3 GB, resume > 4 GB, kill < 1 GB; both directions and the
negative cases, on PLANTED fake-free values (DISK_FAKE_GB_FILE), against real dummy processes (sleep with a disguised
argv[0]). Touches no real job. Usage: python disk_policy_test.py  -> prints PASS/FAIL per check and ALL PASS / FAIL."""
import os, sys, time, signal, subprocess, tempfile, threading, types
HS = "/Users/sumit/Github/quantum/qsim/capd/horseshoe"; TESTS = HS + "/tests"
sys.path.insert(0, HS)
import disk_policy as DP
res = []
def check(name, ok): res.append(ok); print(("PASS " if ok else "FAIL ") + name, flush=True)
def state(pid):
    s = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
    return s[:1] if s else "gone"

# 1. pure function: both directions + negatives
seq = [(7, False, None), (3, False, None), (2, False, "pause"), (2, True, None), (3, True, None), (4, True, None),
       (5, True, "resume"), (0, False, "pause"), (0, True, None), (1, False, "pause")]
check("disk_action table (pause <3, resume >4, NO kill at any level; 3 and 4 hold)", all(DP.disk_action(d, p) == a for d, p, a in seq) and DP.critical(1) and not DP.critical(2))

fake = tempfile.NamedTemporaryFile("w", delete=False, suffix=".gb"); fake.close()
def plant(v): open(fake.name, "w").write(str(v))
os.environ["DISK_FAKE_GB_FILE"] = fake.name
DUMMIES = {}
def dummy(argv0):
    p = subprocess.Popen(["zsh", "-c", 'exec -a "%s" /bin/sleep 900' % argv0], cwd=TESTS, start_new_session=True)
    DUMMIES[p.pid] = p; return p.pid
def end(pid):                                      # kill AND reap, so no zombie keeps a guard waiting
    try: os.kill(pid, signal.SIGKILL)
    except ProcessLookupError: pass
    DUMMIES[pid].wait()

# 2. erep_guard.py (inform mode) on a dummy named like a piece run
plant(7); d = dummy("./mn_so_piece disk_policy_test"); time.sleep(1)
glog = fake.name + ".guard.log"
g = subprocess.Popen([sys.executable, HS + "/erep_guard.py", str(d), glog, "500", "--inform"], cwd=TESTS,
                     env=dict(os.environ, GUARD_TEST_TICK_S="2"), start_new_session=True)
time.sleep(5); plant(3); time.sleep(6); check("erep_guard: 3 GB (negative) -> still running", state(d) in "SR")
plant(2); time.sleep(6); check("erep_guard: 2 GB -> PAUSED (T)", state(d) == "T")
plant(4); time.sleep(6); check("erep_guard: 4 GB (negative) -> still paused", state(d) == "T")
plant(5); time.sleep(6); check("erep_guard: 5 GB -> RESUMED", state(d) in "SR")
plant(0); time.sleep(6); check("erep_guard: 0 GB -> PAUSED, not killed", state(d) == "T")
plant(6); time.sleep(6); check("erep_guard: 6 GB after 0 -> RESUMED", state(d) in "SR")
check("erep_guard: ALERT CRITICAL line logged", "ALERT CRITICAL DISK" in open(glog).read())
end(d); g.wait(timeout=30); print(open(glog).read(), flush=True)

# 3. b15d_run.guard_loop in-process, children = one dummy; time.sleep shortened, logs captured
import b15d_run as R
logs = []; R.log = lambda m: logs.append(m); real_sleep = time.sleep
R.time = types.SimpleNamespace(sleep=lambda s: real_sleep(1), time=time.time)
plant(7); d2 = dummy("disk_policy_test_runner_child"); real_sleep(1)
R.CHILD.clear(); R.CHILD[d2] = ("test/dummy", R.sh("ps -o command= -p %d" % d2)); R.STOPPING.clear()
th = threading.Thread(target=R.guard_loop, daemon=True); th.start()
real_sleep(3); plant(3); real_sleep(3); check("runner guard: 3 GB (negative) -> still running", state(d2) in "SR")
plant(2); real_sleep(3); check("runner guard: 2 GB -> PAUSED (T)", state(d2) == "T")
plant(4); real_sleep(3); check("runner guard: 4 GB (negative) -> still paused", state(d2) == "T")
plant(5); real_sleep(3); check("runner guard: 5 GB -> RESUMED", state(d2) in "SR")
plant(0); real_sleep(3); check("runner guard: 0 GB -> PAUSED, not killed", state(d2) == "T")
plant(6); real_sleep(3); check("runner guard: 6 GB after 0 -> RESUMED", state(d2) in "SR")
check("runner guard: ALERT CRITICAL line logged", any("ALERT CRITICAL DISK" in l for l in logs))
R.STOPPING.set()
print("\n".join("  runner log: " + l for l in logs), flush=True)
end(d2)
print("ALL PASS" if all(res) else "FAIL")
