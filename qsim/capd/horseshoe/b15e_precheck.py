"""B15e pre-check (NOT COUNTED; rule fixed in B15E_DRAFT.md §3 before this runs): the stab variant's 6 edge chunks on HH.

stab frame per hh2 set (c, U, S): u = |U| * S/|S|, s = |S| * rot+90(S/|S|), components at 1e-10 (D.R10); centre unchanged.
Edge chunk = the registered-form spec + `arange 0 0`, no checkpoint (as B15d-2). Same binary, caps, depth, precision.
1 slot (the 4th; B15d's runner keeps 3), nice 10, the B15d guard (1 GB per process + box rules).

  b15e_precheck.py build   write the specs + build.json (S8 and singular-frame gates)
  b15e_precheck.py run     run the 6 edge chunks one at a time (detached via tools/detach.sh)
  b15e_precheck.py read    per covering: edge_fixed class (b15d_split.edge_fixed), check_e, COVER line
"""
import json, math, signal, sys, threading
import b15_steps34 as D
import b15d_run as R
import b15d_split as S

OUT = R.OUT.parent / "b15e" / "precheck"
R.OUT = OUT; S.OUT = OUT; R.LOG = OUT / "run.log"     # this process only: own log, own slot file, own outputs
STAGE = "stab_e"
SLOTS = 1
S.CHUNK_STAGES = S.CHUNK_STAGES + (STAGE,)            # an edge chunk is never classified alone (B15d-2)


def stab_sets():
    out = {}
    for k, (c, U, Sv) in R._hh2_sets().items():
        u, s = [float(x) for x in U], [float(x) for x in Sv]
        nu, ns = math.hypot(*u), math.hypot(*s)
        sh = (s[0] / ns, s[1] / ns)
        out[k] = (c, [D.R10(nu * sh[0]), D.R10(nu * sh[1])], [D.R10(-ns * sh[1]), D.R10(ns * sh[0])])
    return out


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    sets = stab_sets(); s8 = D.s8(sets); T = [D.tset(k, *v) for k, v in sets.items()]
    rec = dict(variant="stab", s8=s8, stop=None)
    if not all(s8.values()): rec["stop"] = "stab: S8"
    elif any(t is None for t in T): rec["stop"] = "stab: singular"
    else:
        for x, y in R.HH2_REQ:
            body = D.HH_HEAD + T + D.RIG_BODY + ["arange 0 0", f"cover {x} {y} 16 16 64"]
            R._write(STAGE, f"stab_{x}{y}", "\n".join(body) + "\n")
        rec["sets"] = {k: [[str(x) for x in t] for t in v] for k, v in sets.items()}
    (OUT / "build.json").write_text(json.dumps(rec, indent=1, default=str))
    print(json.dumps({k: rec[k] for k in ("stop", "s8")}, indent=1))


def table():
    rows = {}
    for x, y in R.HH2_REQ:
        e = S._read(OUT / STAGE / f"stab_{x}{y}.out")
        rows[f"{x}{y}"] = dict(edge_fixed=S.edge_fixed(e), check_e=list(S.check_e(e)) if S._complete(e) else "incomplete",
                               cover=(S._cov(e) or [None])[0])
    ef = [r["edge_fixed"] for r in rows.values()]
    rule = ("ENTERS B15e" if "CERTIFIED-FAIL" in ef and "HARNESS-ERROR" not in ef else
            "does NOT enter (no decidable second variant)" if all(r["check_e"] != "incomplete" for r in rows.values()) else "pending")
    return dict(rows=rows, rule=rule)


def run():
    signal.signal(signal.SIGTERM, S._on_term)
    R.slots = lambda: SLOTS
    R.stop_all = S.stop_all
    if D.file_sha(R.BIN) != R.BIN_SHA: R.log("HARNESS-ERROR: binary sha mismatch"); sys.exit(1)
    threading.Thread(target=R.guard_loop, daemon=True).start()
    R.log("B15e pre-check start (NOT COUNTED; rule in B15E_DRAFT.md §3)")
    if not S.run_jobs([(STAGE, f"stab_{x}{y}") for x, y in R.HH2_REQ]): return
    R.log("PRECHECK: %s" % json.dumps(table())); R.log("DONE")


if __name__ == "__main__":
    {"build": build, "run": run, "read": lambda: print(json.dumps(table(), indent=1))}[sys.argv[1]]()
