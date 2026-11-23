"""B15d-2 runner (registered: PREREG_chaos_horseshoe_phase2.md, B15d-2): edges first for the twin.

Same binary, sets, caps, depth and precision as b15d_run.py (B15d / B15d-1). Only the existing B13 options are used:
  edge chunk = registered spec + `arange 0 0` (no (a)-piece), no checkpoint line
  (a) chunk  = registered spec (same checkpoint path) + `noedges`
A chunk output is NEVER passed to the classifier alone (an edge chunk prints a=1 ... COVERS=1 vacuously); the classifier
(b15_steps34.classify, unchanged) sees only the MERGED input built by merge().

Order: MC (merge positive control, HH-SECONDARY N0=>N0 vs GB's unchunked line) -> 12 twin edge chunks -> EARLY twin
reading -> twin (a) phase (the two PAUSED unchunked processes resumed with SIGCONT + 10 (a) chunks) -> TWIN reading ->
recipe -> kerr (both unchanged, via b15d_run.run_stage).

  b15d_split.py build     write the chunk specs (no run)
  b15d_split.py test      canned merge cases (no hs_cover run)
  b15d_split.py adopt PID TAG ...   record paused PIDs (verified: owner, cmdline = hs_cover_b15d <twin/TAG.spec>, state T)
  b15d_split.py run       the orchestrator (detached via tools/detach.sh)
  b15d_split.py read      MC + twin table
"""
import json, os, re, signal, sys, time, subprocess
from decimal import Decimal
from pathlib import Path
import b15_steps34 as D
import b15d_run as R

OUT = R.OUT
TWIN_ORDER = [f"{v}_{x}{y}" for v in ("swap", "rot90") for x, y in R.HH2_REQ]
EDGE_FIELDS = ("b", "orient", "fail_b", "certified_fail_b", "orient_certified_fail", "leaves_b")
PAUSED_FILE = OUT / "paused.json"
PAUSED = {}          # pid -> dict(tag, cmd, resumed)
RUNNING_ADOPTED = {} # (stage, tag) -> (pid, cmd): live hs_cover_b15d children of an earlier runner (B15d-3 restart safety)


# ---------------------------------------------------------------------------------------------- specs
def _split(lines, kind, ck=None):
    lines = [l for l in lines if l.strip()]
    i = max(k for k, l in enumerate(lines) if l.startswith("cover "))
    if kind == "e":
        lines = [l for l in lines if not l.startswith("checkpoint ")]
        i = max(k for k, l in enumerate(lines) if l.startswith("cover "))
        return "\n".join(lines[:i] + ["arange 0 0"] + lines[i:]) + "\n"
    if ck is not None:
        lines = [(f"checkpoint {ck}" if l.startswith("checkpoint ") else l) for l in lines]
    return "\n".join(lines[:i] + ["noedges"] + lines[i:]) + "\n"


def build():
    for d in ("mc", "twin_e", "twin_a"): (OUT / d).mkdir(exist_ok=True)
    gb = (OUT / "gb" / "hh2_N0N0.spec").read_text().splitlines()
    (OUT / "ckpt" / "mc").mkdir(parents=True, exist_ok=True)
    (OUT / "mc" / "hh2_N0N0_a.spec").write_text(_split(gb, "a", OUT / "ckpt" / "mc" / "hh2_N0N0_a.ckpt"))
    (OUT / "mc" / "hh2_N0N0_e.spec").write_text(_split(gb, "e"))
    for t in TWIN_ORDER:
        src = (OUT / "twin" / f"{t}.spec").read_text().splitlines()
        (OUT / "twin_e" / f"{t}.spec").write_text(_split(src, "e"))
        (OUT / "twin_a" / f"{t}.spec").write_text(_split(src, "a"))
    for d in ("kerr_e", "kerr_a"): (OUT / d).mkdir(exist_ok=True)
    for t in kerr_order():
        src = (OUT / "kerr" / f"{t}.spec").read_text().splitlines()
        (OUT / "kerr_e" / f"{t}.spec").write_text(_split(src, "e"))
        (OUT / "kerr_a" / f"{t}.spec").write_text(_split(src, "a"))
    print("built: mc 2, twin_e %d, twin_a %d, kerr_e/kerr_a %d" % (len(TWIN_ORDER), len(TWIN_ORDER), len(kerr_order())))


def kerr_order():
    b = json.loads((OUT / "kerr" / "build.json").read_text())
    return list(b["required"]) + list(b["optional"])


# ---------------------------------------------------------------------------------------------- merge
CERT_FP = re.compile(r"\sCERTIFIED(\s|$)")


def _cov(lines):
    c = [l for l in lines if l.startswith("COVER ")]
    return c


def _complete(lines):
    return "DONE" in lines and not any(l.startswith("FATAL") for l in lines)


def _hull(r1, r2):
    if r1 == "none": return r2
    if r2 == "none": return r1
    p = lambda r: r.strip("[]").split(",")
    (a1, b1), (a2, b2) = p(r1), p(r2)
    lo = a1 if Decimal(a1) <= Decimal(a2) else a2
    hi = b1 if Decimal(b1) >= Decimal(b2) else b2
    return f"[{lo},{hi}]"


def _nu(cov_line):
    m = re.search(r"chunk_a=\[(\d+),(\d+)\)", cov_line)
    return (int(m.group(1)), int(m.group(2))) if m else None


def check_e(e_lines):
    """-> (ok, error); validation of an edge chunk"""
    c = _cov(e_lines)
    if len(c) != 1: return False, "edge chunk: %d COVER lines" % len(c)
    f = R.fields(c[0])
    want = dict(a="1", fail_a="0", leaves_a="0", maxdepth_a="0", edges="yes")
    bad = {k: f.get(k) for k, v in want.items() if f.get(k) != v}
    if bad or _nu(c[0]) != (0, 0): return False, "edge chunk shape %s chunk_a %s" % (bad, _nu(c[0]))
    return True, None


def check_a(a_lines, nu=16):
    c = _cov(a_lines)
    if len(c) != 1: return False, "(a) chunk: %d COVER lines" % len(c)
    f = R.fields(c[0])
    want = dict(b="skip", orient="skip", COVERS="chunk-a-only", edges="no")
    bad = {k: f.get(k) for k, v in want.items() if f.get(k) != v}
    if bad or _nu(c[0]) != (0, nu): return False, "(a) chunk shape %s chunk_a %s" % (bad, _nu(c[0]))
    return True, None


def edge_fixed(e_lines):
    """CERTIFIED-FAIL if a complete, valid edge chunk certifies a failure; HARNESS-ERROR if invalid; else None"""
    if not _complete(e_lines) or not _cov(e_lines): return None
    ok, err = check_e(e_lines)
    if not ok: return "HARNESS-ERROR"
    f = R.fields(_cov(e_lines)[0])
    fp = any(l.startswith("FAILPIECE") and CERT_FP.search(l) for l in e_lines)
    return "CERTIFIED-FAIL" if (fp or f.get("orient_certified_fail") == "1") else None


def merge(a_lines, e_lines, nu=16):
    """-> (merged classifier input lines | None, error | None). None, None = not complete yet (UNDECIDED)."""
    a_lines = [l.rstrip("\n") for l in a_lines]; e_lines = [l.rstrip("\n") for l in e_lines]
    fps = [l for l in a_lines + e_lines if l.startswith("FAILPIECE")]
    if not (_complete(a_lines) and _complete(e_lines) and _cov(a_lines) and _cov(e_lines)):
        return fps, None                                    # no merged COVER line -> classify() gives UNDECIDED
    ok, err = check_a(a_lines, nu)
    if not ok: return None, err
    ok, err = check_e(e_lines)
    if not ok: return None, err
    ca, ce = _cov(a_lines)[0], _cov(e_lines)[0]
    if ca.split()[1:3] != ce.split()[1:3]: return None, "source/target differ: %s vs %s" % (ca.split()[1:3], ce.split()[1:3])
    fa, fe = R.fields(ca), R.fields(ce)
    covers = "1" if (fa["a"] == "1" and fe["b"] == "1") else "0"
    line = ("COVER %s %s a=%s b=%s strong_a=%s orient=%s fail_a=%s fail_b=%s certified_fail_b=%s orient_certified_fail=%s"
            " leaves_a=%s leaves_b=%s maxdepth_a=%s replay_steps=%d return_time=%s COVERS=%s"
            " chunk_a=[0,%d) edges=merged reloaded_pieces=%s") % (
        *ca.split()[1:3], fa["a"], fe["b"], fa["strong_a"], fe["orient"], fa["fail_a"], fe["fail_b"],
        fe["certified_fail_b"], fe["orient_certified_fail"], fa["leaves_a"], fe["leaves_b"], fa["maxdepth_a"],
        int(fa["replay_steps"]) + int(fe["replay_steps"]), _hull(fa["return_time"], fe["return_time"]), covers,
        nu, fa["reloaded_pieces"])
    return fps + [line, "DONE"], None


def merged_class(a_lines, e_lines, nu=16):
    m, err = merge(a_lines, e_lines, nu)
    if err: return "HARNESS-ERROR", err
    c = D.classify(m)
    ef = edge_fixed([l.rstrip("\n") for l in e_lines])
    if ef == "HARNESS-ERROR": return "HARNESS-ERROR", "edge chunk invalid"
    if ef == "CERTIFIED-FAIL" and any(l.startswith("COVER ") for l in m) and c != "CERTIFIED-FAIL":
        return "HARNESS-ERROR", "edge-fixed CERTIFIED-FAIL but merged %s" % c
    return c, None


# ---------------------------------------------------------------------------------------------- canned cases
def _E(b="1", orient="LR", fb="0", cfb="0", ocf="0", lb="128", rt="[7.0e+00,7.5e+00]", extra=(), done=True, la="0", ch="[0,0)"):
    l = ["PREC 128", *extra,
         f"COVER N0 N0 a=1 b={b} strong_a=1 orient={orient} fail_a=0 fail_b={fb} certified_fail_b={cfb} "
         f"orient_certified_fail={ocf} leaves_a={la} leaves_b={lb} maxdepth_a=0 replay_steps=100 return_time={rt} "
         f"COVERS={'1' if b == '1' else '0'} chunk_a={ch} edges=yes reloaded_pieces=0"]
    return l + (["DONE"] if done else [])


def _A(a="1", fa="0", la="337", rt="[6.8e+00,7.4e+00]", extra=(), done=True, ch="[0,16)", src="N0 N0"):
    l = ["PREC 128", *extra,
         f"COVER {src} a={a} b=skip strong_a=0 orient=skip fail_a={fa} fail_b=0 certified_fail_b=0 "
         f"orient_certified_fail=0 leaves_a={la} leaves_b=0 maxdepth_a=2 replay_steps=1000 return_time={rt} "
         f"COVERS=chunk-a-only chunk_a={ch} edges=no reloaded_pieces=0"]
    return l + (["DONE"] if done else [])


CFP = "FAILPIECE N0>N0 b edge=L s=[0,1] CERTIFIED u=[2,3] w1=[0,1]"
UFP = "FAILPIECE N0>N0 a depth=16(depth cap) u=[0,1] s=[0,1] u=[0,1] s=[0,1]"


def canned():
    cases = [
        ("edge alone COVERS=1 + a=0", _A(a="0", fa="3", extra=[UFP]), _E(), "UNDECIDED", None),
        ("both pass", _A(), _E(), "CERTIFIED", None),
        ("certified edge FAILPIECE", _A(), _E(b="0", orient="none", fb="1", cfb="1", extra=[CFP]), "CERTIFIED-FAIL", "CERTIFIED-FAIL"),
        ("certified edge + failing (a)", _A(a="0", fa="5", extra=[UFP]), _E(b="0", orient="none", fb="1", cfb="1", extra=[CFP]), "CERTIFIED-FAIL", "CERTIFIED-FAIL"),
        ("orient_certified_fail", _A(), _E(b="0", orient="none", ocf="1"), "CERTIFIED-FAIL", "CERTIFIED-FAIL"),
        ("mismatched source/target", _A(src="N0 N3"), _E(), "HARNESS-ERROR", None),
        ("(a) chunk not [0,16)", _A(ch="[0,8)"), _E(), "HARNESS-ERROR", None),
        ("edge chunk leaves_a>0", _A(), _E(la="5"), "HARNESS-ERROR", "HARNESS-ERROR"),
        ("(a) unfinished, edge certified", _A(done=False), _E(b="0", orient="none", fb="1", cfb="1", extra=[CFP]), "UNDECIDED", "CERTIFIED-FAIL"),
        ("(a) missing", [], _E(), "UNDECIDED", None),
        ("uncertified edge fail", _A(), _E(b="0", orient="none", fb="2"), "UNDECIDED", None),
    ]
    res = []; ok = True
    for name, a, e, want, want_ef in cases:
        got, err = merged_class(a, e); ef = edge_fixed(e)
        good = got == want and ef == want_ef; ok &= good
        res.append(dict(case=name, got=got, want=want, edge_fixed=ef, want_edge_fixed=want_ef, err=err, ok=good))
    h = [_hull("none", "[1e+00,2e+00]") == "[1e+00,2e+00]", _hull("[1.5e+00,2e+00]", "[1e+00,1.8e+00]") == "[1e+00,2e+00]",
         _hull("none", "none") == "none", _hull("[-2.0e+00,1e+00]", "[-1.0e+00,3e+00]") == "[-2.0e+00,3e+00]"]
    res.append(dict(case="hull", ok=all(h))); ok &= all(h)
    m, _ = merge(_A(), _E())
    full = [l for l in m if l.startswith("COVER ")][0]
    want_line = ("COVER N0 N0 a=1 b=1 strong_a=0 orient=LR fail_a=0 fail_b=0 certified_fail_b=0 orient_certified_fail=0 "
                 "leaves_a=337 leaves_b=128 maxdepth_a=2 replay_steps=1100 return_time=[6.8e+00,7.5e+00] COVERS=1")
    lf = full.split(" chunk_a=")[0] == want_line; ok &= lf
    res.append(dict(case="merged line format", ok=lf, got=full))
    return ok, res


# ---------------------------------------------------------------------------------------------- adopt / run
def _read(p):
    return p.read_text().splitlines() if p.exists() else []


def adopt(args):
    rec = json.loads(PAUSED_FILE.read_text()) if PAUSED_FILE.exists() else {}
    for pid, tag in zip(args[0::2], args[1::2]):
        pid = int(pid); cmd = R.sh("ps -o command= -p %d" % pid); own = R.sh("ps -o user= -p %d" % pid)
        st = R.sh("ps -o stat= -p %d" % pid)
        want = "%s %s" % (R.BIN, OUT / "twin" / f"{tag}.spec")
        if own != "sumit" or cmd != want or not st.startswith("T"):
            print("REFUSED", pid, tag, own, st, cmd); sys.exit(1)
        rec[str(pid)] = dict(tag=tag, cmd=cmd, resumed=False)
    PAUSED_FILE.write_text(json.dumps(rec, indent=1)); print(json.dumps(rec, indent=1))


def _alive(pid, cmd):
    return R.sh("ps -o command= -p %d" % pid) == cmd


def stop_all(why):
    R.STOPPING.set()
    for pid in list(R.CHILD):
        R.verified_term(pid, why)
        if pid in PAUSED and _alive(pid, PAUSED[pid]["cmd"]):
            os.kill(pid, signal.SIGCONT); R.log("SIGCONT PID %d after SIGTERM (paused process must run to end)" % pid)


def _on_term(signum, frame):
    R.log("split orchestrator SIGTERM: stopping all children (checkpointed; relaunch resumes)"); stop_all("orchestrator SIGTERM")


CHUNK_STAGES = ("mc", "twin_e", "twin_a", "kerr_e", "kerr_a")


def scan_running():
    """adopt live hs_cover_b15d processes of mine on a spec under OUT that are not in paused.json"""
    paused_pids = {int(k) for k in (json.loads(PAUSED_FILE.read_text()) if PAUSED_FILE.exists() else {})}
    for l in R.sh("ps -axo pid=,user=,command=").splitlines():
        f = l.split(None, 2)
        if len(f) < 3 or f[1] != "sumit" or not f[2].startswith(str(R.BIN) + " " + str(OUT) + "/"): continue
        pid = int(f[0])
        if pid in paused_pids: continue
        spec = Path(f[2].split(" ", 1)[1]); st, t = spec.parent.name, spec.stem
        RUNNING_ADOPTED[(st, t)] = (pid, f[2]); R.CHILD[pid] = (f"{st}/{t}", f[2])
        R.log("adopted running PID %d (%s/%s, state %s)" % (pid, st, t, R.sh("ps -o stat= -p %d" % pid)))


LEVEL_LINE = {"mn": "param level -1/2", "hh": "param level 1/6"}


def spec_gate(spec):
    """B15e A1: a hamiltonian spec must carry exactly one registered `param level` line (hs_cover's S9 reads SYS.level,
    which only that line sets; the mn lift hard-codes H = -1/2). Returns (ok, reason)."""
    lines = [l.strip() for l in open(spec).read().splitlines()]
    sysl = [l.split()[1] for l in lines if l.startswith("system ")]
    if len(sysl) != 1: return False, "spec has %d system lines" % len(sysl)
    want = LEVEL_LINE.get(sysl[0])
    if want is None: return True, "no level needed (system %s)" % sysl[0]
    lv = [l for l in lines if l.startswith("param level")]
    if lv != [want]: return False, "system %s needs exactly one '%s', found %s" % (sysl[0], want, lv)
    return True, want


def run_jobs(jobs, adopted=(), on_tick=None):
    """jobs: [(stage_dir, tag)]; adopted: paused PIDs already resumed (count toward slots). Chunk outputs get no class;
    unchunked stages (recipe) log the B15c classifier's class as b15d_run.run_stage did."""
    todo = [j for j in jobs if not R.done_ok(*j)]
    running = {pid: (("twin", PAUSED[pid]["tag"]), None) for pid in adopted}
    CMDS = {pid: PAUSED[pid]["cmd"] for pid in adopted}
    for j in list(todo):
        if j in RUNNING_ADOPTED:
            pid, cmd = RUNNING_ADOPTED.pop(j); todo.remove(j)
            if _alive(pid, cmd): running[pid] = (j, None); CMDS[pid] = cmd
    # B15e A3-fix: tick at least once, so a relaunch with nothing left in `jobs` and no paused PID still reaches on_tick
    # (which re-queues the adopted kerr_e chunks); before this, such a relaunch fell straight through to "stage 0"
    first = on_tick is not None
    while (todo or running or first) and not R.STOPPING.is_set():
        first = False
        for pid, (j, p) in list(running.items()):
            ended = (p.poll() is not None) if p is not None else not _alive(pid, CMDS[pid])
            if ended:
                del running[pid]; R.CHILD.pop(pid, None)
                rc = p.returncode if p else "n/a"
                if j[0] in CHUNK_STAGES or (j[0] == "twin" and p is None):
                    R.log("%s/%s exit %s (chunk/adopted; classified only by the B15d-2/-3 reading)" % (j[0], j[1], rc))
                else:
                    R.log("%s/%s exit %s; class %s" % (j[0], j[1], rc, D.classify(_read(OUT / j[0] / f"{j[1]}.out"))))
        while todo and len(running) < R.slots() and not R.STOPPING.is_set():
            st, t = todo.pop(0); spec = OUT / st / f"{t}.spec"
            g_ok, g_why = spec_gate(spec)
            if not g_ok:
                R.log("REFUSED %s/%s: %s (B15e A1 gate); not launched" % (st, t, g_why)); continue
            fo = open(OUT / st / f"{t}.out", "w")
            # B15e A1-flush: line-buffered stdout (/usr/bin/stdbuf execs the same binary), so a stopped process
            # leaves every finished piece's line on disk; the binary and its sha are unchanged
            p = subprocess.Popen(["nice", "-n", "10", "/usr/bin/stdbuf", "-oL", str(R.BIN), str(spec)], stdout=fo, stderr=subprocess.STDOUT,
                                 cwd=str(R.HERE), start_new_session=True)
            time.sleep(0.5); R.CHILD[p.pid] = (f"{st}/{t}", R.sh("ps -o command= -p %d" % p.pid)); running[p.pid] = ((st, t), p)
            R.log("start %s/%s PID %d (spec sha256 %s)" % (st, t, p.pid, D.file_sha(spec)[:16]))
        if on_tick:
            for j in (on_tick() or []):
                if R.done_ok(*j): continue
                if j in RUNNING_ADOPTED:
                    pid, cmd = RUNNING_ADOPTED.pop(j)
                    if _alive(pid, cmd): running[pid] = (j, None); CMDS[pid] = cmd; continue
                todo.append(j)
        time.sleep(10)
    return not R.STOPPING.is_set()


def read_mc():
    a, e = _read(OUT / "mc" / "hh2_N0N0_a.out"), _read(OUT / "mc" / "hh2_N0N0_e.out")
    ref = [l for l in _read(OUT / "gb" / "hh2_N0N0.out") if l.startswith("COVER ")][0]
    m, err = merge(a, e)
    got = [l for l in (m or []) if l.startswith("COVER ")]
    got = got[0] if got else None
    cls, cerr = merged_class(a, e)
    same = got is not None and got.split(" chunk_a=")[0] == ref.split(" chunk_a=")[0]
    return dict(PASS=bool(same and cls == "CERTIFIED" and D.classify(_read(OUT / "gb" / "hh2_N0N0.out")) == "CERTIFIED"),
                merged=got, gb=ref, merged_class=cls, err=err or cerr)


def twin_table():
    rows = {}
    adopted_tags = {v["tag"] for v in (json.loads(PAUSED_FILE.read_text()).values() if PAUSED_FILE.exists() else [])}
    for t in TWIN_ORDER:
        e = _read(OUT / "twin_e" / f"{t}.out"); ef = edge_fixed(e)
        if t in adopted_tags and not (OUT / "twin_a" / f"{t}.out").exists():   # a vanished paused PID runs as an (a) chunk
            full = _read(OUT / "twin" / f"{t}.out")
            done = _complete(full) and _cov(full)
            cls = D.classify(full) if done else None
            if done and _complete(e) and _cov(e):
                ff, fe = R.fields(_cov(full)[0]), R.fields(_cov(e)[0])
                diff = {k: (ff.get(k), fe.get(k)) for k in EDGE_FIELDS if ff.get(k) != fe.get(k)}
                if diff: cls = "HARNESS-ERROR"
            else:
                diff = None
            rows[t] = dict(source="unchunked (adopted)", edge_fixed=ef, final=cls, edge_check=diff)
        else:
            a = _read(OUT / "twin_a" / f"{t}.out")
            done = _complete(a) and _complete(e) and _cov(a) and _cov(e)
            cls, err = merged_class(a, e) if done else (None, None)
            rows[t] = dict(source="merged", edge_fixed=ef, final=cls, err=err)
        r = rows[t]; r["reading"] = r["final"] or r["edge_fixed"] or "pending"
    out = dict(rows=rows)
    for v in ("swap", "rot90"):
        req = [rows[f"{v}_{x}{y}"]["reading"] for x, y in R.HH2_REQ]
        out[v] = dict(classes=req, PASS=("CERTIFIED-FAIL" in req and "HARNESS-ERROR" not in req),
                      complete=all(rows[f"{v}_{x}{y}"]["final"] for x, y in R.HH2_REQ))
    out["PASS"] = out["swap"]["PASS"] and out["rot90"]["PASS"]
    return out


def kerr_table():
    b = json.loads((OUT / "kerr" / "build.json").read_text()); rows = {}
    for t in kerr_order():
        e, a = _read(OUT / "kerr_e" / f"{t}.out"), _read(OUT / "kerr_a" / f"{t}.out")
        ef = edge_fixed(e)
        done = _complete(a) and _complete(e) and _cov(a) and _cov(e)
        cls, err = merged_class(a, e) if done else (None, None)
        rows[t] = dict(edge_fixed=ef, final=cls, err=err, reading=cls or ef or "pending")
    req = [rows[t]["reading"] for t in b["required"]]
    complete = all(rows[t]["final"] for t in b["required"])
    early = ("HARNESS-ERROR" if "HARNESS-ERROR" in req else
             "CERTIFIED-FAIL (edge-fixed; final unless a HARNESS-ERROR appears)" if "CERTIFIED-FAIL" in req else "pending")
    out = dict(chain=b["chain"], rows=rows, complete=complete, early_chain=early)
    if complete: out["chain_class"] = D.chain_class([rows[t]["final"] for t in b["required"]])
    return out


def run():
    signal.signal(signal.SIGTERM, _on_term)
    R.stop_all = stop_all                                   # the guard's box stop must also SIGCONT paused processes
    if D.file_sha(R.BIN) != R.BIN_SHA: R.log("HARNESS-ERROR: binary sha mismatch"); sys.exit(1)
    ok, res = canned()
    R.log("B15d-2 canned merge cases: %s" % ("PASS" if ok else "FAIL " + json.dumps(res)))
    if not ok: return
    rec = json.loads(PAUSED_FILE.read_text()) if PAUSED_FILE.exists() else {}
    for k, v in rec.items():
        pid = int(k)
        if _alive(pid, v["cmd"]):
            PAUSED[pid] = v; R.CHILD[pid] = ("twin/" + v["tag"], v["cmd"])
            R.log("adopted PID %d (twin/%s, state %s)" % (pid, v["tag"], R.sh("ps -o stat= -p %d" % pid)))
        else:
            R.log("paused PID %d (twin/%s) is gone: its covering runs as an (a) chunk from its checkpoint instead" % (pid, v["tag"]))
    scan_running()
    import threading
    threading.Thread(target=R.guard_loop, daemon=True).start()
    R.log("B15d-2 split orchestrator start PID %d; slots %d" % (os.getpid(), R.slots()))
    if not run_jobs([("mc", "hh2_N0N0_a"), ("mc", "hh2_N0N0_e")]): return
    mc = read_mc(); R.log("MC: %s" % json.dumps(mc))
    if not mc["PASS"]: R.log("MC FAILED: split not used; B15d holds; to the Bridge"); return
    if not run_jobs([("twin_e", t) for t in TWIN_ORDER]): return
    R.log("TWIN-EARLY: %s" % json.dumps(twin_table()))
    for pid, v in PAUSED.items():
        if _alive(pid, v["cmd"]):
            os.kill(pid, signal.SIGCONT); R.log("SIGCONT verified PID %d (twin/%s): resumed" % (pid, v["tag"]))
    adopted_tags = {v["tag"] for v in PAUSED.values()}
    gone = {v["tag"] for v in rec.values()} - adopted_tags  # paused PIDs that vanished: plain (a) chunks
    # B15e (on top of B15d-4): recipe -> RECIPE -> [twin PASS (B15e) = swap PASS] -> kerr_e -> KERR-EARLY ->
    # twin (a) interleaved with kerr (a) -> TWIN (B15d) + hold -> TWIN-1V (B15e) -> KERR (final only if every twin merge is
    # complete with no HARNESS-ERROR)
    tags = lambda st: [f.stem for f in sorted((OUT / st).glob("*.spec"))]
    rjobs = [("recipe", t) for t in tags("recipe")]
    tjobs = [("twin_a", t) for t in TWIN_ORDER if t not in adopted_tags or t in gone]
    kejobs = [("kerr_e", t) for t in kerr_order()]; kajobs = [("kerr_a", t) for t in kerr_order()]
    ST = dict(stage=0, kerr=False)
    def tick():
        if ST["stage"] == 0 and all(R.done_ok(*j) for j in rjobs):
            ST["stage"] = 1; R.log("RECIPE: %s" % json.dumps(R.read_recipe("recipe")))
            sw = twin_table()["swap"]
            if sw["PASS"]:
                ST["kerr"] = True; R.log("B15e twin PASS (one variant, swap: %s): Kerr edge chunks start" % sw["classes"]); return kejobs
            ST["stage"] = 2; R.log("B15e twin NOT PASS (swap: %s): no Kerr covering runs; twin (a) chunks for the record" % sw["classes"]); return tjobs
        if ST["stage"] == 1 and all(R.done_ok(*j) for j in kejobs):
            ST["stage"] = 2; R.log("KERR-EARLY: %s" % json.dumps(kerr_table()))
            out = []
            for n in range(max(len(tjobs), len(kajobs))):
                out += tjobs[n:n + 1] + kajobs[n:n + 1]
            return out
        return None
    R.log("B15e queue: recipe %s; then (if swap PASS) kerr_e %s; then twin (a) %s interleaved with kerr (a)" %
          ([t for _, t in rjobs], [t for _, t in kejobs], [t for _, t in tjobs]))
    if not run_jobs(rjobs, adopted=[p for p in PAUSED if _alive(p, PAUSED[p]["cmd"])], on_tick=tick): return
    if ST["stage"] < 2:
        R.log("B15e queue ended at stage %d (a recipe or Kerr edge covering has no DONE): HARNESS; held; to the Bridge" % ST["stage"]); return
    tw = twin_table(); R.log("TWIN: %s" % json.dumps(tw))
    if not tw["PASS"]: R.log("TWIN not PASS (control 3 not decided or failed): B15d holds; to the Bridge")
    rows = tw["rows"]; harness = [t for t, r in rows.items() if r["reading"] == "HARNESS-ERROR"]
    complete = all(r["final"] for r in rows.values())
    R.log("TWIN-1V (B15e, one variant): %s" % json.dumps(dict(swap=tw["swap"], all_twin_complete=complete, harness=harness)))
    if not ST["kerr"]: R.log("DONE (B15e: no Kerr covering ran)"); return
    kt = kerr_table()
    if complete and not harness and tw["swap"]["PASS"]:
        R.log("KERR (B15e, final): %s" % json.dumps(kt))
    else:
        R.log("KERR WITHHELD (B15e: twin merges incomplete or HARNESS-ERROR %s): %s; to the Bridge" % (harness, json.dumps(kt)))
    R.log("DONE")


def read():
    try: print("MC", json.dumps(read_mc(), indent=1))
    except (IndexError, FileNotFoundError): print("MC not run")
    print("TWIN", json.dumps(twin_table(), indent=1))
    try: print("KERR", json.dumps(kerr_table(), indent=1))
    except FileNotFoundError: print("KERR not run")


if __name__ == "__main__":
    if sys.argv[1] == "test":
        ok, res = canned(); print(json.dumps(res, indent=1)); print("CANNED", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
    if sys.argv[1] == "adopt": adopt(sys.argv[2:]); sys.exit(0)
    {"build": build, "run": run, "read": read}[sys.argv[1]]()
