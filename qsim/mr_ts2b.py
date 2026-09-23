"""
Stage 2b runner, exactly as registered in PREREG_ts2b_factor_route.md (737982c + fca18ea):
validation (V-neg, V-pos, V-info, V-mono) first, then the 8 TS target rows. Guarded, sequential.

Usage:  python mr_ts2b.py [i,j,...]      |      python mr_ts2b.py --one i out.json
"""
import json, os, sys, time
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mr_factor_route as F, mr_monodromy as MO, mr_nve as N, mr_ts2 as T2, mr_calibration as C

OBS, INC, NOB = F.OBSTRUCTION, F.INCONCLUSIVE, "NO_OBSTRUCTION"
R = sp.Rational
xs, ys, rs, us = sp.symbols("x y r u")


def _calib(expected_set):
    return [(name, r, C.z) for name, r, exp, case, why in C.CASES + C.ADDED if exp in expected_set]


def _poisons():
    x = sp.Symbol("x")
    return [(f"r = y1''/y1, y1 = {y1}", sp.cancel(sp.diff(y1, x, 2)/y1), x) for y1 in (sp.sqrt(x**2 - 2), sp.sqrt(x**3 - 2))]


def _nve(kind, *a):
    if kind == "zv":
        d, E, L, mu = a
        n = N.nve_equatorial(N.zipoy_voorhees(d, xs, ys), xs, ys, E=E, L=L, mu=mu); v = xs
    elif kind == "kerr":
        E, L, m2 = a
        n = N.nve_equatorial(N.kerr(1, R(3, 5), rs, us), rs, us, E=E, L=L, mu=sp.sqrt(m2)); v = rs
    elif kind == "ts2row":
        i, = a
        tag, name, build, ELm, expected, ident = T2.ROWS[i]
        n = N.nve_equatorial(build(), T2.X, T2.Y, E=ELm[0], L=ELm[1], mu=sp.sqrt(ELm[2])); v = T2.X
    return [(f, n[f], v) for f in ("r_xi2", "r_xi1") if n[f] is not None]


# (group, name, builder -> list of (label, r, var), expectation, run monodromy?)
#   expectation: "not_OBS" (V-neg), "OBS" (V-pos), None (V-info / target)
ROWS = [
    ("V-neg", "Stage-1 calibration, expected NO_OBSTRUCTION or INCONCLUSIVE", lambda: _calib({"NO_OBSTRUCTION", "INCONCLUSIVE"}), "not_OBS", False),
    ("V-neg", "algebraic-factor Liouvillian poisons", _poisons, "not_OBS", False),
    ("V-info", "Stage-1 calibration, expected OBSTRUCTION or None", lambda: _calib({"OBSTRUCTION", None}), None, False),
    ("V-info", "P(0,0,1/3) (Kimura: non-Liouvillian)", lambda: [("P(0,0,1/3)", C.riemann_P(0, 0, R(1, 3)), C.z)], None, False),
    ("V-pos", "Stage-1 A: ZV d=2 mu=2", lambda: _nve("zv", 2, 1, 0, 2), "OBS", True),
    ("V-pos", "Stage-1 A: ZV d=2 mu=3", lambda: _nve("zv", 2, 1, 0, 3), "OBS", True),
    ("V-pos", "Stage-2 C1: ZV d=2 via WP loader", lambda: _nve("ts2row", 0), "OBS", True),
    ("V-neg", "Stage-1 B1: Kerr BL (3,0,118)", lambda: _nve("kerr", 3, 0, 118), "not_OBS", True),
    ("V-neg", "Stage-1 B2: Kerr BL (1,2,125/63)", lambda: _nve("kerr", 1, 2, R(125, 63)), "not_OBS", True),
    ("V-neg", "Stage-1 A'': ZV d=1 L=1 mu=2", lambda: _nve("zv", 1, 1, 1, 2), "not_OBS", True),
    ("V-neg", "Stage-1 A'': ZV d=1 L=1 mu=3", lambda: _nve("zv", 1, 1, 1, 3), "not_OBS", True),
] + [("V-neg", f"Stage-2 {T2.ROWS[i][0]}: {T2.ROWS[i][1]}", (lambda i=i: _nve("ts2row", i)), "not_OBS", True)
     for i in (1, 2, 3, 4, 5, 6, 11, 12)] \
  + [("TARGET", f"{T2.ROWS[i][0]}: {T2.ROWS[i][1]}", (lambda i=i: _nve("ts2row", i)), None, True)
     for i in (7, 8, 9, 10, 13, 14)]
N_VALIDATION = len([r for r in ROWS if r[0] != "TARGET"])


def _mono(r, v, numeric):
    try:
        if numeric:
            mv, why, info = MO.monodromy_verdict(r, v, poles=F.numeric_poles(r, v))
        else:
            mv, why, info = MO.monodromy_verdict(r, v)
        return dict(verdict=mv, why=why, det_err=(info or {}).get("det_err"))
    except Exception as e:                       # numerical failure -> uncorroborated, never a verdict
        return dict(verdict="FAILED", why=f"{type(e).__name__}: {e}")


def run_row(i):
    group, name, build, expect, mono = ROWS[i]
    t0 = time.time()
    items = build()
    out = dict(group=group, name=name, expect=expect, items=[])
    for label, r, v in items:
        a = F.analyse(r, v)
        it = dict(label=label, route=a["verdict"], reason=a["reason"],
                  factors=a.get("factors"), inf=a.get("inf"), ord_inf=a.get("ord_inf"),
                  case1_candidates=a.get("case1_candidates"), log_point=a.get("log_point"))
        print(f"[{time.time()-t0:.1f}s] {label}: route {a['verdict']} -- {a['reason']}", flush=True)
        if mono:
            it["mono_numeric"] = _mono(r, v, True)
            print(f"[{time.time()-t0:.1f}s] {label}: numeric-pole monodromy {it['mono_numeric']['verdict']} ({it['mono_numeric']['why']})", flush=True)
            if group != "TARGET":
                it["mono_default"] = _mono(r, v, False)
                print(f"[{time.time()-t0:.1f}s] {label}: default monodromy {it['mono_default']['verdict']}", flush=True)
        out["items"].append(it)
    out["seconds"] = round(time.time() - t0, 1)
    return out


def assess(row):
    its = row["items"]
    routes = [it["route"] for it in its]
    if row["group"] == "TARGET":
        mn = [it["mono_numeric"]["verdict"] for it in its]
        if "NO_OBSTRUCTION" in mn and OBS in routes:
            return "FAIL (route OBSTRUCTION vs monodromy NO_OBSTRUCTION)"
        if len(its) == 2 and all(r == OBS for r in routes):
            return "OBSTRUCTION" if all(m == OBS for m in mn) else "OBSTRUCTION (route), monodromy uncorroborated " + str(mn)
        if OBS in routes:
            return f"OBSTRUCTION on one form only ({[it['label'] for it in its if it['route'] == OBS]}): single-form proof"
        return "INCONCLUSIVE"
    ok = True
    if row["expect"] == "not_OBS":
        ok = OBS not in routes
    elif row["expect"] == "OBS":
        ok = all(r == OBS for r in routes)
    mono_ok = all(it["mono_numeric"]["verdict"] == it["mono_default"]["verdict"] for it in its if "mono_default" in it)
    return ("PASS" if ok and mono_ok else "FAIL") + ("" if mono_ok else " (V-mono disagreement)") if row["expect"] else "INFO"


def run_guarded_all(only=None, mem_limit_mb=1024, time_limit_s=1800):
    import mr_watchdog as W
    rows = []
    for i, (group, name, build, expect, mono) in enumerate(ROWS):
        if only is not None and i not in only:
            continue
        outp = os.path.join(HERE, f"mr_ts2b_row_{i}.json")
        if os.path.exists(outp):
            os.remove(outp)
        g = W.run_guarded([sys.executable, "-u", os.path.abspath(__file__), "--one", str(i), outp],
                          mem_limit_mb=mem_limit_mb, time_limit_s=time_limit_s, cwd=HERE,
                          log=os.path.join(HERE, f"mr_ts2b_row_{i}.log"))
        if g["status"] == "ok" and os.path.exists(outp):
            row = json.load(open(outp))
            row["assessment"] = assess(row)
        else:
            row = dict(group=group, name=name, expect=expect, items=[],
                       assessment=("FAIL" if expect else "INCONCLUSIVE") + f" (resource limit: {g['status']})")
        row["guard"] = g
        rows.append(row)
        summ = "; ".join(f"{it['label']}: {it['route']}" + (f"/mono {it['mono_numeric']['verdict']}" if "mono_numeric" in it else "")
                         for it in row["items"])
        print(f"{i:>2} {group:<7} {name:<52} => {row['assessment']}   [{summ[:300]}]   "
              f"[guard {g['status']}, peak {g['peak_mb']} MB, {g['seconds']} s]", flush=True)
        json.dump(rows, open(os.path.join(HERE, "mr_ts2b_run.json"), "w"), indent=1, default=str)
    return rows


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--one":
        json.dump(run_row(int(sys.argv[2])), open(sys.argv[3], "w"), indent=1, default=str)
    else:
        only = set(int(a) for a in sys.argv[1].split(",")) if len(sys.argv) > 1 else None
        run_guarded_all(only=only)
