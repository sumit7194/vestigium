"""
POST-HOC corroboration: numeric-pole monodromy with the repaired (wide, best-clearance) base-point
search, as registered in PREREG_ts2b_factor_route.md (0855be6). Validation rows first, then the 6 TS
rows. The committed verdict (ce2cab8) changes only if this DISAGREES -> reported as a CONFLICT.

Usage:  python mr_mono_repair.py        |      python mr_mono_repair.py --one i out.json
"""
import json, os, sys, time
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mr_factor_route as F, mr_monodromy as MO, mr_ts2b as B

R = sp.Rational
ROWS = [
    ("VAL", "ZV d=2 A mu=2", lambda: B._nve("zv", 2, 1, 0, 2), "OBSTRUCTION"),
    ("VAL", "C1 ZV d=2 via WP loader", lambda: B._nve("ts2row", 0), "OBSTRUCTION"),
    ("VAL", "Kerr BL B1 (3,0,118)", lambda: B._nve("kerr", 3, 0, 118), "NO_OBSTRUCTION"),
    ("VAL", "C3 Kerr-WP P1 (1,0,4)", lambda: B._nve("ts2row", 3), "NO_OBSTRUCTION"),
    ("VAL", "C3 Kerr-WP P2 (1,0,4)", lambda: B._nve("ts2row", 4), "NO_OBSTRUCTION"),
] + [("TS", B.T2.ROWS[i][1], (lambda i=i: B._nve("ts2row", i)), None) for i in (7, 8, 9, 10, 13, 14)]


def run_row(i):
    tag, name, build, expected = ROWS[i]
    t0 = time.time()
    out = dict(tag=tag, name=name, expected=expected, forms={})
    for form, r, v in build():
        try:
            mv, why, info = MO.monodromy_verdict(r, v, poles=F.numeric_poles(r, v), base_search="wide")
            out["forms"][form] = dict(verdict=mv, why=why, det_err=(info or {}).get("det_err"))
        except Exception as e:
            out["forms"][form] = dict(verdict="FAILED", why=f"{type(e).__name__}: {e}")
        print(f"[{time.time()-t0:.1f}s] {form}: {out['forms'][form]}", flush=True)
    return out


def run_all():
    import mr_watchdog as W
    rows = []
    for i, (tag, name, build, expected) in enumerate(ROWS):
        outp = os.path.join(HERE, f"mr_mono_repair_row_{i}.json")
        g = W.run_guarded([sys.executable, "-u", os.path.abspath(__file__), "--one", str(i), outp],
                          mem_limit_mb=1024, time_limit_s=1800, cwd=HERE,
                          log=os.path.join(HERE, f"mr_mono_repair_row_{i}.log"))
        row = json.load(open(outp)) if g["status"] == "ok" and os.path.exists(outp) else \
            dict(tag=tag, name=name, expected=expected, forms={}, failed=g["status"])
        vs = [f["verdict"] for f in row["forms"].values()]
        if tag == "VAL":
            row["assessment"] = "PASS" if vs and all(v == expected for v in vs) else "FAIL"
        elif "NO_OBSTRUCTION" in vs:
            row["assessment"] = "CONFLICT (monodromy NO_OBSTRUCTION vs route OBSTRUCTION)"
        elif len(vs) == 2 and all(v == "OBSTRUCTION" for v in vs):
            row["assessment"] = "corroborated post hoc (SL2 on both forms)"
        else:
            row["assessment"] = f"still uncorroborated ({vs})"
        row["guard"] = g
        rows.append(row)
        print(f"{i:>2} {tag:<3} {name:<34} => {row['assessment']:<45} "
              f"{[(k, f['verdict'], f.get('det_err')) for k, f in row['forms'].items()]} "
              f"[guard {g['status']}, peak {g['peak_mb']} MB, {g['seconds']} s]", flush=True)
        json.dump(rows, open(os.path.join(HERE, "mr_mono_repair_run.json"), "w"), indent=1, default=str)
        if tag == "VAL" and row["assessment"] != "PASS":
            print("VALIDATION FAILED: the repaired search is not used; TS rows not run", flush=True)
            return rows
    return rows


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--one":
        json.dump(run_row(int(sys.argv[2])), open(sys.argv[3], "w"), indent=1, default=str)
    else:
        run_all()
