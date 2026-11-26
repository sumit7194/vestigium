"""b15e_read.py -- the B15e readings, from the registered code (B15e A7). It replaces only the retired runner's LOGGING
of the readings. Every table comes from b15d_split / b15d_run / b15_steps34 unchanged, and the closing block below is
b15d_split.run()'s closing block verbatim (only `ST["kerr"]` is recomputed: the runner set it when it logged
"B15e twin PASS (one variant, ...)", i.e. from twin_table()["swap"]["PASS"]). Written by Claude Opus 5.5 (Quantum-personal).

  python b15e_read.py golden   reproduce the last recorded TWIN-EARLY and RECIPE lines byte for byte (writes nothing)
  python b15e_read.py early    log "KERR-EARLY: ..." once, when all 8 kerr_e outputs hold DONE (golden first)
  python b15e_read.py final    log TWIN / hold / TWIN-1V / KERR (final or WITHHELD) / DONE, only when every twin_a and
                               kerr_a chunk holds DONE (golden first)
Run with sims/.venv python from this folder. It never starts, signals or stops a process.
"""
import json, sys
import b15d_split as S
import b15d_run as R
from b15d_split import twin_table, kerr_table, kerr_order, TWIN_ORDER


def golden():
    log = R.LOG.read_text().splitlines(); ok = True
    for tag, f in (("TWIN-EARLY", lambda: json.dumps(twin_table())), ("RECIPE", lambda: json.dumps(R.read_recipe("recipe")))):
        ls = [l for l in log if l[20:].startswith(tag + ": ")]
        if not ls: print(f"golden {tag}: no recorded line"); ok = False; continue
        same = ls[-1].split(tag + ": ", 1)[1] == f()
        print(f"golden {tag} (recorded {ls[-1][:19]}): {'BYTE-IDENTICAL' if same else 'DIFFERS'}"); ok = ok and same
    return ok


def logged(prefix):
    return any(l[20:].startswith(prefix) for l in R.LOG.read_text().splitlines())


def main():
    cmd = sys.argv[1] if len(sys.argv) == 2 else ""
    if cmd not in ("golden", "early", "final"): sys.exit(__doc__)
    if not golden(): sys.exit("REFUSED: golden failed; nothing logged; to the Bridge")
    if cmd == "golden": return
    kejobs = [("kerr_e", t) for t in kerr_order()]
    if cmd == "early":
        if not all(R.done_ok(*j) for j in kejobs): sys.exit("not yet: kerr_e without DONE: %s" % [t for s, t in kejobs if not R.done_ok(s, t)])
        if logged("KERR-EARLY: "): sys.exit("KERR-EARLY already logged; not logged twice")
        R.log("KERR-EARLY: %s" % json.dumps(kerr_table())); print("logged KERR-EARLY"); return
    tjobs = [("twin_a", t) for t in TWIN_ORDER]; kajobs = [("kerr_a", t) for t in kerr_order()]
    missing = [f"{s}/{t}" for s, t in tjobs + kajobs + kejobs if not R.done_ok(s, t)]
    if missing: sys.exit("not yet: no DONE in %s" % missing)
    if logged("KERR (B15e, final)") or logged("KERR WITHHELD"): sys.exit("a KERR reading is already logged; not logged twice")
    ST = dict(kerr=twin_table()["swap"]["PASS"])
    # ---- b15d_split.run() closing block, verbatim ----
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


if __name__ == "__main__":
    main()
