"""B15d orchestrator (registered: PREREG_chaos_horseshoe_phase2.md, B15d ed65b68). Builds the exact specs, runs hs_cover
under the slot, classifies with the B15c/B15c-1 classifier, and reads the gates and controls in the registered order:
  gb      gate GB: HH-SECONDARY N0=>N0 (whole COVER line) and R1 generic MM/MN/NM/NN (the GB-1 field rule)
  twin    control 3's rigorous twin: hh2's CERTIFIED sets with U<->S, and with U rotated 90 deg (W2 fallback if singular);
          all 6 required coverings per variant; each variant must be CERTIFIED-FAIL in >= 1 required covering
  recipe  the frame-recipe POSITIVE control on HH-SECONDARY's Pi4 chain -> RECIPE-POSITIVE / RECIPE-NEGATIVE
  kerr    the counted B15d Kerr coverings (only after gb PASS, twin PASS and recipe complete)

Slot: at most N concurrent hs_cover processes, N read from horseshoe_results/kerr/b15d/slots.txt on every loop (2 now;
the Bridge raises it to 4). Each process: nice 10, its own session, one guard (footprint > 1024 MB -> SIGTERM that
process; the box rules -- disk < 5 GB at once, (swap > 2 GB and level >= 2) or level >= 4 sustained 600 s -- stop all).
SIGTERM to this orchestrator stops every child (verified PIDs) and exits; a relaunch resumes from the checkpoints, and
outputs that already end in DONE are not re-run. No wall-time cap (B16).

  b15d_run.py build      write all specs + exact sets (no hs_cover run); prints S8 / chain records
  b15d_run.py run        run the stages in order (detached via tools/detach.sh)
  b15d_run.py read       print the per-covering table and the registered readings
"""
import hashlib, json, os, re, signal, subprocess, sys, threading, time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import b15_steps34 as D
import hs_construct as H

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "horseshoe_results"
OUT = RES / "kerr" / "b15d"
BIN = HERE / "hs_cover_b15d"
BIN_SHA = "fb5fcbfca2d857a2c2f53df1d473b65ee5c6a835c0a062f52887f406dd886ad3"
SIZES = dict(a0=0.03, a=0.01, bf0=0.5, bf=0.5)
GB_FIELDS = ("a", "b", "strong_a", "orient", "fail_a", "fail_b", "return_time", "COVERS")
CAP_MB = 1024


def rot(v):
    return np.array([-v[1], v[0]], float)


# ---------------------------------------------------------------------------------------------- spec building
def _write(stage, tag, text):
    d = OUT / stage; d.mkdir(parents=True, exist_ok=True)
    (d / f"{tag}.spec").write_text(text)


def _with_ck(lines, stage, tag):
    """replace/append the checkpoint line with a fresh, stage-local one"""
    lines = [l for l in lines if not l.startswith("checkpoint ")]
    i = max(k for k, l in enumerate(lines) if l.startswith("cover "))
    ck = OUT / "ckpt" / stage; ck.mkdir(parents=True, exist_ok=True)
    return "\n".join(lines[:i] + [f"checkpoint {ck / (tag + '.ckpt')}"] + lines[i:]) + "\n"


def build_gb():
    rec = {}
    for t in ("MM", "MN", "NM", "NN"):
        src = (RES / f"r1_generic_{t}.spec").read_text().splitlines()
        _write("gb", f"r1_{t}", "\n".join(src) + "\n")
        rec[f"r1_{t}"] = json.loads((RES / f"r1_generic_{t}.json").read_text())["covers"]
    src = (RES / "hh2_N0N0.spec").read_text().splitlines()
    _write("gb", "hh2_N0N0", _with_ck(src, "gb", "hh2_N0N0"))
    rec["hh2_N0N0"] = json.loads((RES / "hh2_N0N0.json").read_text())["covers"]
    (OUT / "gb" / "reference.json").write_text(json.dumps(rec, indent=1))
    return rec


def _hh2_sets():
    ref = json.loads((RES / "hh2_exact_checks.json").read_text())["sets"]
    return {k: tuple([F(x) for x in t] for t in v) for k, v in ref.items()}


HH2_REQ = [("N0", "N0"), ("N0", "N3"), ("N3", "N4"), ("N4", "N5"), ("N5", "N6"), ("N6", "N0")]


def build_twin():
    base = _hh2_sets(); rec = {}
    variants = {"swap": {k: (c, S, U) for k, (c, U, S) in base.items()}}
    rU = {k: (c, [-U[1], U[0]], S) for k, (c, U, S) in base.items()}
    if any(D.tset(k, *v) is None for k, v in rU.items()):
        variants["rot90"] = {k: (c, [-U[1], U[0]], [-S[1], S[0]]) for k, (c, U, S) in base.items()}; rec["rot90_form"] = "W2 (U and S rotated): U-only frame singular"
    else:
        variants["rot90"] = rU; rec["rot90_form"] = "U only"
    for name, sets in variants.items():
        T = [D.tset(k, *v) for k, v in sets.items()]
        for x, y in HH2_REQ:
            body = D.HH_HEAD + T + D.RIG_BODY + [f"cover {x} {y} 16 16 64"]
            _write("twin", f"{name}_{x}{y}", _with_ck(body, "twin", f"{name}_{x}{y}"))
        rec[name] = dict(s8=D.s8(sets))
    (OUT / "twin" / "build.json").write_text(json.dumps(rec, indent=1, default=str))
    return rec


def recipe_sets(z, eu, es, X, U):
    """B15d §3: N0 in the eigen-frame; chain sets (X_j, a U_j, (b/a) a U_j_perp); B14's chain rule (float), then exact."""
    a0, a, bf0, bf = SIZES["a0"], SIZES["a"], SIZES["bf0"], SIZES["bf"]
    z, eu, es = (np.asarray(v, float) for v in (z, eu, es)); X = [np.asarray(x, float) for x in X]
    U = [np.asarray(u, float) / np.linalg.norm(u) for u in U]; Sp = [rot(u) for u in U]
    m = len(X) - 1
    N0 = (z, a0 * eu, bf0 * a0 * es)
    idx = [j for j in range(1, m) if H.disjoint(N0, (X[j], a * U[j], bf * a * Sp[j]))]
    if not idx:
        return dict(stop="no chain")
    j1, j2 = idx[0], idx[-1]; chain = list(range(j1, j2 + 1))
    if chain != idx:
        return dict(stop="no chain", why="not contiguous", idx=idx)
    N = {0: N0}; N.update({j: (X[j], a * U[j], bf * a * Sp[j]) for j in chain})
    if not all(H.disjoint(N[i], N[j]) for i in N for j in N if i < j):
        return dict(stop="no chain", why="pairwise overlap (float)", idx=idx)
    R = D.R10
    sets = {"N0": ([R(v) for v in z], [R(a0 * v) for v in eu], [R(bf0 * a0 * v) for v in es])}
    for j in chain:
        sets[f"N{j}"] = ([R(v) for v in X[j]], [R(a * v) for v in U[j]], [R(bf * a * v) for v in Sp[j]])
    return dict(stop=None, chain=chain, sets=sets)


def build_recipe(system):
    if system == "hh":
        ex = json.loads((RES / "construct" / "hh_explore.json").read_text())["saddles"]["Pi4"]
        ch = json.loads((RES / "construct" / "hh_chain_explore.json").read_text())
        z, eu, es, X, U = ex["z"], ex["e_u"], ex["e_s"], ch["X"], ch["U"]; stage, head = "recipe", D.HH_HEAD
    else:
        arm = json.loads((RES / "kerr" / "b15c" / "ARM.json").read_text()); s3 = arm["records"][0]["step3"]
        z, eu, es, X, U = arm["saddle"]["z"], arm["saddle"]["e_u"], arm["saddle"]["e_s"], s3["X"], s3["U"]; stage, head = "kerr", D.KERR_HEAD
    r = recipe_sets(z, eu, es, X, U)
    rec = dict(system=system, stop=r["stop"], chain=r.get("chain"))
    if r["stop"] is None:
        s8 = D.s8(r["sets"]); rec["s8"] = s8
        T = [D.tset(k, *v) for k, v in r["sets"].items()]
        if not all(s8.values()):
            rec["stop"] = "S8"
        elif any(t is None for t in T):
            rec["stop"] = "singular frame"
        else:
            ch = r["chain"]; j1, j2 = ch[0], ch[-1]
            req = [("N0", "N0"), ("N0", f"N{j1}")] + [(f"N{j}", f"N{j + 1}") for j in ch[:-1]] + [(f"N{j2}", "N0")]
            opt = [(f"N{j2}", f"N{j1}")]
            for x, y in req + opt:
                _write(stage, f"{x}{y}", _with_ck(head + T + D.RIG_BODY + [f"cover {x} {y} 16 16 64"], stage, f"{x}{y}"))
            rec.update(required=[f"{x}{y}" for x, y in req], optional=[f"{x}{y}" for x, y in opt],
                       sets={k: [[str(x) for x in t] for t in v] for k, v in r["sets"].items()})
    (OUT / stage).mkdir(parents=True, exist_ok=True)
    (OUT / stage / "build.json").write_text(json.dumps(rec, indent=1, default=str))
    return rec


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    print("gb:", list(build_gb()))
    tw = build_twin(); print("twin:", tw["rot90_form"], {k: all(v["s8"].values()) for k, v in tw.items() if k != "rot90_form"})
    for sysn in ("hh", "kerr"):
        r = build_recipe(sysn); print("recipe", sysn, "stop", r["stop"], "chain", r.get("chain"), "required", r.get("required"))


# ---------------------------------------------------------------------------------------------- running
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()


def footprint_mb(p):
    m = re.search(r"Footprint:\s*([\d.]+)\s*(KB|MB|GB)", sh("footprint -p %d 2>/dev/null | head -3" % p))
    return 0.0 if not m else float(m.group(1)) * {"KB": 1 / 1024, "MB": 1, "GB": 1024}[m.group(2)]


LOG = OUT / "run.log"
CHILD = {}            # pid -> (tag, cmdline)
STOPPING = threading.Event()


def log(s):
    with open(LOG, "a") as f: f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + s + "\n")


def verified_term(pid, why):
    tag, cmd0 = CHILD.get(pid, (None, None))
    cmd = sh("ps -o command= -p %d" % pid); own = sh("ps -o user= -p %d" % pid)
    if own == "sumit" and cmd == cmd0:
        log("SIGTERM verified PID %d (%s): %s" % (pid, tag, why)); os.kill(pid, signal.SIGTERM)
    else:
        log("SIGTERM REFUSED for PID %d (%s): identity changed (%s / %s)" % (pid, tag, own, cmd))


def guard_loop():
    bad_since = None
    while not STOPPING.is_set():
        for pid in list(CHILD):
            if footprint_mb(pid) > CAP_MB: verified_term(pid, "footprint > %d MB" % CAP_MB)
        dk = int(sh("df -g / | tail -1 | awk '{print $4}'") or 99)
        sw = float((sh("sysctl -n vm.swapusage | awk '{print $6}'") or "0M").rstrip("M")); pl = int(sh("sysctl -n kern.memorystatus_vm_pressure_level") or 1)
        if dk < 5:
            log("BOX STOP: disk %d GB < 5" % dk); stop_all("disk")
        bad = (sw > 2048 and pl >= 2) or pl >= 4
        bad_since = (bad_since or time.time()) if bad else None
        if bad_since and time.time() - bad_since > 600:
            log("BOX STOP: swap %.0f MB level %d sustained 600 s" % (sw, pl)); stop_all("memory")
        time.sleep(60)


def stop_all(why):
    STOPPING.set()
    for pid in list(CHILD): verified_term(pid, why)


def _on_term(signum, frame):
    log("orchestrator SIGTERM: stopping all children (checkpointed; relaunch resumes)"); stop_all("orchestrator SIGTERM")


def slots():
    try: return max(1, min(4, int((OUT / "slots.txt").read_text().strip())))
    except Exception: return 2


def done_ok(stage, tag):
    o = OUT / stage / f"{tag}.out"
    return o.exists() and "DONE" in o.read_text().splitlines()


def run_stage(stage, tags):
    todo = [t for t in tags if not done_ok(stage, t)]
    running = {}
    while (todo or running) and not STOPPING.is_set():
        for pid, (t, p) in list(running.items()):
            if p.poll() is not None:
                del running[pid]; CHILD.pop(pid, None)
                log("%s/%s exit %s; class %s" % (stage, t, p.returncode, D.classify((OUT / stage / f"{t}.out").read_text().splitlines())))
        while todo and len(running) < slots() and not STOPPING.is_set():
            t = todo.pop(0); spec = OUT / stage / f"{t}.spec"
            fo = open(OUT / stage / f"{t}.out", "w")
            p = subprocess.Popen(["nice", "-n", "10", str(BIN), str(spec)], stdout=fo, stderr=subprocess.STDOUT,
                                 cwd=str(HERE), start_new_session=True)
            time.sleep(0.5); CHILD[p.pid] = (f"{stage}/{t}", sh("ps -o command= -p %d" % p.pid)); running[p.pid] = (t, p)
            log("start %s/%s PID %d (spec sha256 %s)" % (stage, t, p.pid, D.file_sha(spec)[:16]))
        time.sleep(10)
    return not STOPPING.is_set()


def classes(stage):
    return {f.stem: D.classify(f.read_text().splitlines()) for f in sorted((OUT / stage).glob("*.out"))}


def cover_line(stage, tag):
    c = [l for l in (OUT / stage / f"{tag}.out").read_text().splitlines() if l.startswith("COVER ")]
    return c[0] if c else None


def fields(line):
    return dict(re.findall(r"(\S+?)=(\S+)", line or ""))


def read_gb():
    ref = json.loads((OUT / "gb" / "reference.json").read_text()); res = {}
    l = cover_line("gb", "hh2_N0N0"); res["hh2_N0N0"] = dict(match=(l is not None and l == ref["hh2_N0N0"][0]), got=l, want=ref["hh2_N0N0"][0])
    for t in ("MM", "MN", "NM", "NN"):
        g, w = fields(cover_line("gb", f"r1_{t}")), fields(ref[f"r1_{t}"][0])
        res[f"r1_{t}"] = dict(match=all(g.get(k) == w.get(k) for k in GB_FIELDS), diff={k: (g.get(k), w.get(k)) for k in GB_FIELDS if g.get(k) != w.get(k)})
    res["PASS"] = all(v["match"] for k, v in res.items() if isinstance(v, dict))
    return res


def read_twin():
    c = classes("twin"); out = {}
    for v in ("swap", "rot90"):
        req = [c.get(f"{v}_{x}{y}") for x, y in HH2_REQ]
        out[v] = dict(classes=req, PASS=("CERTIFIED-FAIL" in req and "HARNESS-ERROR" not in req),
                      decided=all(r is not None for r in req))
    out["PASS"] = out["swap"]["PASS"] and out["rot90"]["PASS"]
    return out


def read_recipe(stage):
    b = json.loads((OUT / stage / "build.json").read_text())
    if b["stop"]:
        return dict(stop=b["stop"], reading=("RECIPE-NEGATIVE" if stage == "recipe" else "NOT TESTED (%s)" % b["stop"]))
    c = classes(stage); req = [c.get(t) for t in b["required"]]
    r = dict(chain=b["chain"], required={t: c.get(t) for t in b["required"]}, optional={t: c.get(t) for t in b["optional"]})
    if stage == "recipe":
        r["reading"] = "RECIPE-POSITIVE" if all(x == "CERTIFIED" for x in req) else "RECIPE-NEGATIVE"
    else:
        r["chain_class"] = D.chain_class(req)
    return r


def run():
    signal.signal(signal.SIGTERM, _on_term)
    if D.file_sha(BIN) != BIN_SHA: log("HARNESS-ERROR: binary sha mismatch"); sys.exit(1)
    threading.Thread(target=guard_loop, daemon=True).start()
    log("orchestrator start PID %d; binary %s; slots %d" % (os.getpid(), BIN_SHA[:16], slots()))
    tags = lambda st: [f.stem for f in sorted((OUT / st).glob("*.spec"))]
    if not run_stage("gb", tags("gb")): return
    g = read_gb(); log("GB: %s" % json.dumps(g)[:2000])
    if not g["PASS"]: log("GB FAILED: B15d holds; to the Bridge"); return
    if not run_stage("twin", tags("twin")) or not run_stage("recipe", tags("recipe")): return
    tw = read_twin(); rc = read_recipe("recipe"); log("TWIN: %s" % json.dumps(tw)); log("RECIPE: %s" % json.dumps(rc))
    if not tw["PASS"]: log("TWIN not PASS (control 3 not decided or failed): B15d holds; to the Bridge"); return
    if not run_stage("kerr", tags("kerr")): return
    log("KERR: %s" % json.dumps(read_recipe("kerr"))); log("DONE")


def read():
    print("GB", json.dumps(read_gb(), indent=1)[:3000])
    for st in ("twin",): print("TWIN", json.dumps(read_twin(), indent=1))
    for st in ("recipe", "kerr"):
        try: print(st.upper(), json.dumps(read_recipe(st), indent=1))
        except FileNotFoundError: print(st, "not built")


if __name__ == "__main__":
    {"build": build, "run": run, "read": read}[sys.argv[1]]()
