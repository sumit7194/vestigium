"""B15e A1 (PREREG, 852b9f9): spec slip -- the Kerr specs lacked `param level`, so S9 failed on every piece.

  b15e_a1.py fix          insert `param level -1/2` after `param L 445/2` in kerr/, kerr_e/, kerr_a/ (*.spec);
                          old/new sha256 -> kerr/a1_specs.json. Refuses to touch a file that already has a level line.
  b15e_a1.py kat          known-answer test of the runner gate (NOT COUNTED): a copy of the fixed kerr_e/N0N0.spec
                          WITHOUT `param level` goes through b15d_split.run_jobs with process launch disabled; it must be
                          REFUSED and never launched, and the fixed spec must pass the gate. Result -> run.log.
  b15e_a1.py smoke-build  S+ / S- specs (stage 1, or stage 2 with `2`) in kerr/b15e/a1_smoke/
  b15e_a1.py smoke-read   the registered PASS / INCONCLUSIVE / FAIL reading for a stage
"""
import json, subprocess, sys
import b15_steps34 as D
import b15d_run as R
import b15d_split as S

B = R.OUT                                       # horseshoe_results/kerr/b15d
SMOKE = B.parent / "b15e" / "a1_smoke"
LEVEL = "param level -1/2"
WRONG = "param level -499/1000"                 # -1/2 + 1/1000 (must-fail twin)


def fix():
    rec = {}
    for d in ("kerr", "kerr_e", "kerr_a"):
        for f in sorted((B / d).glob("*.spec")):
            lines = f.read_text().splitlines()
            if any(l.startswith("param level") for l in lines): raise SystemExit(f"{f}: already has a level line")
            idx = [k for k, l in enumerate(lines) if l.strip() == "param L 445/2"]
            if len(idx) != 1 or lines[0].strip() != "system mn": raise SystemExit(f"{f}: unexpected header")
            old = D.file_sha(f)
            f.write_text("\n".join(lines[:idx[0] + 1] + [LEVEL] + lines[idx[0] + 1:]) + "\n")
            rec[f"{d}/{f.name}"] = dict(old=old, new=D.file_sha(f))
    (B / "kerr" / "a1_specs.json").write_text(json.dumps(rec, indent=1))
    print("fixed %d specs" % len(rec))


def kat():
    d = B.parent / "b15e" / "a1_kat"; (d / "kat_e").mkdir(parents=True, exist_ok=True)
    src = (B / "kerr_e" / "N0N0.spec").read_text().splitlines()
    assert src.count(LEVEL) == 1, "kerr_e/N0N0.spec is not fixed"
    (d / "kat_e" / "nolevel.spec").write_text("\n".join(l for l in src if l != LEVEL) + "\n")
    fixed_ok = S.spec_gate(B / "kerr_e" / "N0N0.spec")
    logged = []
    real_log, real_out, real_popen = R.log, S.OUT, subprocess.Popen
    launched = []
    try:
        R.log = lambda m: logged.append(m)
        S.OUT = d
        subprocess.Popen = lambda *a, **k: launched.append(a) or (_ for _ in ()).throw(RuntimeError("launch attempted"))
        S.run_jobs([("kat_e", "nolevel")])
    finally:
        R.log, S.OUT, subprocess.Popen = real_log, real_out, real_popen
    refused = any(m.startswith("REFUSED kat_e/nolevel") for m in logged)
    ok = fixed_ok[0] and refused and not launched
    res = dict(PASS=ok, fixed_spec_gate=fixed_ok, refused=refused, launched=len(launched), runner_lines=logged)
    (d / "kat.json").write_text(json.dumps(res, indent=1))
    R.log("B15e A1 gate known-answer test (NOT COUNTED): %s" % json.dumps(res))
    print(json.dumps(res, indent=1))


def smoke_build(stage="1"):
    SMOKE.mkdir(parents=True, exist_ok=True)
    src = [l for l in (B / "kerr_e" / "N0N0.spec").read_text().splitlines() if l.strip()]
    assert src.count(LEVEL) == 1
    head = [l for l in src if not l.startswith(("caps ", "depth ", "arange ", "noedges", "checkpoint ", "cover "))]
    tail = (["caps 65536 4096", "depth 0 0", "cover N0 N0 1 1 1"] if stage == "1" else
            ["caps 65536 4096", "depth 0 0", "arange 0 1", "noedges", "cover N0 N0 16 16 64"])
    for v, lv in (("plus", LEVEL), ("minus", WRONG)):
        body = [lv if l == LEVEL else l for l in head] + tail
        (SMOKE / f"s{stage}_{v}.spec").write_text("\n".join(body) + "\n")
    print("built", sorted(p.name for p in SMOKE.glob(f"s{stage}_*.spec")))


def _pieces(lines):
    """FAILPIECE lines -> {piece id: reason}; piece id = everything before the reason"""
    out = {}
    for l in lines:
        if not l.startswith("FAILPIECE "): continue
        if " b edge=" in l:
            pid, rest = l.split(" s=", 1); s_iv, why = rest.split("] ", 1); pid = pid + " s=" + s_iv + "]"
        else:
            pre, rest = l.split(" s=", 1); s_iv, why = rest.split("] ", 1)
            pid = pre.split(" depth=")[0] + " u=" + pre.split(" u=")[1] + " s=" + s_iv + "]"
        out[pid] = why.strip()
    return out


def smoke_read(stage="1"):
    rd = lambda v: (SMOKE / f"s{stage}_{v}.out").read_text().splitlines() if (SMOKE / f"s{stage}_{v}.out").exists() else []
    p, m = rd("plus"), rd("minus")
    done = all(any(l.startswith("COVER ") for l in x) and "DONE" in x for x in (p, m))
    fp, fm = _pieces(p), _pieces(m)
    P = [k for k, w in fm.items() if w.startswith("S9: return enclosure misses the energy level (BUG)")]
    plus_s9 = [k for k, w in fp.items() if "S9" in w] + [l for l in p if "(BUG)" in l and not l.startswith("FAILPIECE")]
    good = [k for k in P if k not in fp or fp[k].startswith("u=")]
    if not done: reading = "pending"
    elif plus_s9: reading = "FAIL (S+ has S9/BUG)"
    elif not P: reading = "INCONCLUSIVE (S- reached no S9)"
    elif good: reading = "PASS"
    else: reading = "INCONCLUSIVE (no P piece completed S9 in S+)"
    res = dict(stage=stage, reading=reading, P=P, plus=fp, minus=fm, plus_ok_in_P=good,
               cover_plus=[l for l in p if l.startswith("COVER ")], cover_minus=[l for l in m if l.startswith("COVER ")])
    print(json.dumps(res, indent=1)); return res


if __name__ == "__main__":
    a = sys.argv[1:]
    {"fix": fix, "kat": kat, "smoke-build": lambda: smoke_build(*a[1:]), "smoke-read": lambda: smoke_read(*a[1:])}[a[0]]()
