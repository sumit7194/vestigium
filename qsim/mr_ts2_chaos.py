"""TS delta=2 obstruction at ansatz's chaos-search levels (PREREG_ts2_chaos_levels.md, 3ee9900 + 74870ec).

Per row: gates (y=0 invariance; v2-vs-Stage-2-loader provenance), route A = 2b' (analyse_v2, both reduced forms),
route B = frozen v2 driver with the A6 policy + v1 replay (N=100; N=140 if tail-limited, pre-registered).
Usage: python mr_ts2_chaos.py RUN        |   python mr_ts2_chaos.py --one i out.json
"""
import json, os, subprocess, sys, time
import sympy as sp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = os.path.dirname(HERE)
R = sp.Rational
# (name, file key, p, (E, L, mu^2), kind)   kind: "target" | "control"
ROWS = [
    ("row1 Dubeibe Fig.1", "TS_P2", R(4, 5), (R(47, 50), R(-39, 5), 1), "target"),
    ("row2 Dubeibe level p=3/5", "TS_P1", R(3, 5), (R(47, 50), R(-52, 5), 1), "target"),
    ("row3 near-sep", "TS_P2", R(4, 5), (R(19, 20), R(-773, 100), 1), "target"),
    ("row4 near-sep", "TS_P2", R(4, 5), (R(97, 100), R(-201, 25), 1), "target"),
    ("row5 near-sep other sense", "TS_P2", R(4, 5), (R(97, 100), R(1051, 100), 1), "target"),
    ("row6 near-sep", "TS_P1", R(3, 5), (R(19, 20), R(-93, 10), 1), "target"),
    ("row7 near-sep", "TS_P1", R(3, 5), (R(97, 100), R(-48, 5), 1), "target"),
    ("row8 near-sep other sense", "TS_P1", R(3, 5), (R(97, 100), R(287, 20), 1), "target"),
    ("ctrl Kerr p=4/5 at row1 level", "KERR_P2", R(4, 5), (R(47, 50), R(-39, 5), 1), "control"),
    ("ctrl Kerr p=3/5 at row2 level", "KERR_P1", R(3, 5), (R(47, 50), R(-52, 5), 1), "control"),
]


def _file(key):
    import mr_ts2 as T2
    return getattr(T2, key)


def system(key, En, L, mu2):
    """As mr_v2_ts2.system, for any WP file (sigma = 1)."""
    import mr_ts2 as T2, mr_mn_equatorial as ME, mr_v2 as V
    C = T2._read_components(os.path.join(T2.PKG, _file(key)))
    C = {k: sp.sympify(v).subs(T2.SIG, 1) for k, v in C.items() if k in ("g_TT", "g_Tphi", "g_phiphi", "g_xx", "g_yy")}
    C = {"g_tt": C["g_TT"], "g_tphi": C["g_Tphi"], "g_phiphi": C["g_phiphi"], "g_xx": C["g_xx"], "g_yy": C["g_yy"]}
    G = ME.lower_at_equator(C, T2.X, T2.Y, ME.field_ctx(0))
    A, B, X = ME.equatorial_nve(G, En, L, mu2)
    p, q = V._pq(A, B, X)
    S = dict(p=p, q=q, gens=ME.QtE.GENS, eregs=lambda b, t: [], var=ME.T_, bad=[], kind="equatorial",
             to_expr=lambda e, part: e.to_expr(part), reduced=lambda: ME.form_t(A, B, X, "r_xi1"),
             skip_near=[], skip=0.0)
    return S, G


def gates(key, En, L, mu2, S, G):
    """Same two gates as mr_v2_ts2.gates, for this row."""
    import mpmath as mp
    import mr_mn_equatorial as ME, mr_ts2 as T2, mr_nve as N, ia_hub as IA
    mp.mp.dps = 60
    inv_ok = all(G[k][1].is_zero() for k in ME.COMP)
    xp, xpp, xppp = [sp.diff(ME.X_OF_T, ME.T_, k) for k in (1, 2, 3)]
    Sch = xppp/xp - R(3, 2)*(xpp/xp)**2
    r_v = S["reduced"]()
    nve = N.nve_equatorial(T2.load_wp(_file(key), 1), T2.X, T2.Y, E=En, L=L, mu=sp.sqrt(mu2))
    fx = sp.lambdify(T2.X, nve["r_xi1"], "mpmath")
    a_ = IA.Compiled(r_v.to_expr(), ME.T_)
    worst = 0.0
    for tv in (R(9, 4), sp.Integer(3), R(7, 4)):
        xv = mp.mpf(ME.X_OF_T.subs(ME.T_, tv))
        ref = mp.mpf((xp**2).subs(ME.T_, tv))*fx(xv) - mp.mpf(Sch.subs(ME.T_, tv))/2
        va = a_(a_._const(tv))
        vam = mp.mpc(va.real.mid().str(60, radius=False), va.imag.mid().str(60, radius=False))
        worst = max(worst, float(abs(vam - ref)/abs(ref)))
    return dict(invariance=inv_ok, provenance_worst_rel=worst, pass_=bool(inv_ok and worst < 1e-25)), nve


def route_a(nve):
    import mr_factor_route as F, mr_ts2 as T2
    out = {}
    for form in ("r_xi2", "r_xi1"):
        if nve.get(form) is None:
            continue
        a = F.analyse_v2(nve[form], T2.X)
        out[form] = dict(verdict=a["verdict"], reason=a["reason"], log_point=a.get("log_point"),
                         case1_candidates=a.get("case1_candidates"))
    return out


def route_b(S, log):
    import mr_v2 as V
    t0 = time.time()
    sing = V.locate_a6(S)
    log(f"[{time.time()-t0:.0f}s] {len(sing)} located singular points")
    r = V.search(S, sing, log=lambda m: log(f"[{time.time()-t0:.0f}s] {m}"), skip_failed=True)
    r["located"] = [str(complex(round(c.real, 6), round(c.imag, 6))) for c in sing]
    log(f"[{time.time()-t0:.0f}s] v2 certificate found: {r['found']} {r.get('why', '')}")
    if r["found"]:
        runs = {}
        for N in (100, 140):
            rr = V.replay_v1(S, r, sing, procs=3, N=N)
            runs[str(N)] = rr
            log(f"[{time.time()-t0:.0f}s] v1 replay N={N}: {rr['replayed']}")
            if rr["replayed"]:
                break
        r["v1_replay_by_N"] = runs
        r["v1_replay"] = runs[max(runs, key=int)]
    r["seconds"] = round(time.time() - t0, 1)
    return r


def run_row(i):
    name, key, p, (En, L, mu2), kind = ROWS[i]
    log = lambda m: print(m, flush=True)
    t0 = time.time()
    S, G = system(key, En, L, mu2)
    g, nve = gates(key, En, L, mu2, S, G)
    log(f"gates: {g}")
    out = dict(name=name, file=_file(key), p=str(p), level=[str(En), str(L), str(mu2)], kind=kind, gates=g)
    if not g["pass_"]:
        out["assessment"] = "STOPPED (gate failed)"
        return out
    out["route_a"] = route_a(nve)
    log(f"route A (2b'): { {k: v['verdict'] for k, v in out['route_a'].items()} }")
    out["route_b"] = route_b(S, log)
    a_obs = any(v["verdict"] == "OBSTRUCTION" for v in out["route_a"].values())
    b_obs = bool(out["route_b"]["found"] and out["route_b"].get("v1_replay", {}).get("replayed"))
    if kind == "control":
        bad = a_obs or out["route_b"]["found"]
        out["assessment"] = "CONTROL FAILED (obstruction on Kerr)" if bad else "CONTROL PASS (no obstruction)"
    else:
        out["assessment"] = ("OBSTRUCTION (two routes)" if a_obs and b_obs else
                             "OBSTRUCTION (single route: A, 2b')" if a_obs else
                             "OBSTRUCTION (single route: B, monodromy)" if b_obs else "INCONCLUSIVE")
    out["seconds"] = round(time.time() - t0, 1)
    return out


def run_all():
    import mr_watchdog as W
    res = []
    for i, (name, *_ ) in enumerate(ROWS):
        outp = os.path.join(HERE, f"mr_ts2_chaos_row{i}.json")
        if os.path.exists(outp):
            os.remove(outp)
        g = W.run_guarded([sys.executable, "-u", os.path.abspath(__file__), "--one", str(i), outp], mem_limit_mb=2048,
                          time_limit_s=3600, cwd=HERE, log=os.path.join(HERE, f"mr_ts2_chaos_row{i}.log"))
        r = json.load(open(outp)) if (g["status"] == "ok" and os.path.exists(outp)) else \
            dict(name=name, assessment=f"no result (guard: {g['status']})")
        r["guard"] = g
        res.append(r)
        print(f"{i} {name:<32} => {r['assessment']} [guard {g['status']}, peak {g['peak_mb']} MB, {g['seconds']} s]",
              flush=True)
        json.dump(res, open(os.path.join(HERE, "mr_ts2_chaos.json"), "w"), indent=1, default=str)
        paths = [os.path.relpath(p_, REPO) for p_ in (outp, os.path.join(HERE, f"mr_ts2_chaos_row{i}.log"),
                 os.path.join(HERE, "mr_ts2_chaos.json"), os.path.join(HERE, "mr_ts2_chaos.txt")) if os.path.exists(p_)]
        subprocess.run(["git", "add", *paths], cwd=REPO)
        if subprocess.run(["git", "commit", "-q", "-m", f"TS chaos-levels: row {i} raw output\n\n"
                           "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], cwd=REPO).returncode == 0:
            subprocess.run(["git", "push", "-q", "origin", "main"], cwd=REPO)
        if r.get("kind") == "control" and r["assessment"].startswith("CONTROL FAILED"):
            print("STOP: a control obstructed (registered stop rule)", flush=True)
            break


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--one":
        json.dump(run_row(int(sys.argv[2])), open(sys.argv[3], "w"), indent=1, default=str)
    else:
        run_all()
