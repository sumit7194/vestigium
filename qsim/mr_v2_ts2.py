"""TS delta=2 re-certification by iahub v2 (PREREG_ts2_v2.md, 8d19fbe). Uses the shared equatorial pipeline
(mr_mn_equatorial) on ansatz's rational TS components, the frozen v2 driver, and the v1 replay rule.
Usage: python mr_v2_ts2.py GATES | RUN      |     python mr_v2_ts2.py --one i out.json"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROWS = [(P, lev) for P in ("P1", "P2") for lev in ((1, 0, 4), (1, 0, 9), (1, 1, 4))]


def ts_source(P):
    import mr_ts2 as T2
    fname = T2.TS_P1 if P == "P1" else T2.TS_P2
    C = T2._read_components(os.path.join(T2.PKG, fname))
    C = {k: v.subs(T2.SIG, 1) for k, v in C.items() if k in ("g_TT", "g_Tphi", "g_phiphi", "g_xx", "g_yy")}
    C = {"g_tt": C["g_TT"], "g_tphi": C["g_Tphi"], "g_phiphi": C["g_phiphi"], "g_xx": C["g_xx"], "g_yy": C["g_yy"]}
    return C, T2.X, T2.Y


def system(P, En, L, mu2):
    import mr_mn_equatorial as ME, mr_v2 as V
    C, x, y = ts_source(P)
    cd = ME.field_ctx(0)
    G = ME.lower_at_equator(C, x, y, cd)
    A, B, X = ME.equatorial_nve(G, En, L, mu2)
    p, q = V._pq(A, B, X)
    S = dict(p=p, q=q, gens=ME.QtE.GENS, eregs=lambda b, t: [], var=ME.T_, bad=[], kind="equatorial",
             to_expr=lambda e, part: e.to_expr(part), reduced=lambda: ME.form_t(A, B, X, "r_xi1"),
             skip_near=[], skip=0.0)
    return S, G


def gates():
    """Pre-run gates: (1) exact y=0 invariance; (2) provenance vs the Stage-2 loader's NVE (mr_nve, x variable)."""
    import sympy as sp, mpmath as mp
    import mr_mn_equatorial as ME, mr_ts2 as T2, mr_nve as N, ia_hub as IA
    mp.mp.dps = 60
    out = {}
    for P in ("P1", "P2"):
        S, G = system(P, 1, 0, 4)
        out[f"{P} invariance"] = all(G[k][1].is_zero() for k in ME.COMP)
    xp, xpp, xppp = [sp.diff(ME.X_OF_T, ME.T_, k) for k in (1, 2, 3)]
    Sch = xppp/xp - sp.Rational(3, 2)*(xpp/xp)**2
    worst = 0.0
    for P, (En, L, mu2) in ROWS:
        S, G = system(P, En, L, mu2)
        r_v = S["reduced"]()
        inv = T2.load_wp(T2.TS_P1 if P == "P1" else T2.TS_P2, 1)
        nve = N.nve_equatorial(inv, T2.X, T2.Y, E=En, L=L, mu=sp.sqrt(mu2))
        fx = sp.lambdify(T2.X, nve["r_xi1"], "mpmath")
        a_ = IA.Compiled(r_v.to_expr(), ME.T_)
        for tv in (sp.Rational(9, 4), sp.Integer(3), sp.Rational(7, 4)):
            xv = mp.mpf(ME.X_OF_T.subs(ME.T_, tv))
            ref = mp.mpf((xp**2).subs(ME.T_, tv))*fx(xv) - mp.mpf(Sch.subs(ME.T_, tv))/2
            va = a_(a_._const(tv))
            vam = mp.mpc(va.real.mid().str(60, radius=False), va.imag.mid().str(60, radius=False))
            worst = max(worst, float(abs(vam - ref)/abs(ref)))
        out[f"{P} {(En, L, mu2)} provenance worst rel"] = worst
    out["GATES_PASS"] = all(v for k, v in out.items() if "invariance" in k) and worst < 1e-25
    return out


def run_row(i):
    import mr_v2 as V
    P, (En, L, mu2) = ROWS[i]
    t0 = time.time()
    S, _ = system(P, En, L, mu2)
    sing = V.locate_a6(S)                                   # pre-run amendment: A6 locator
    print(f"[{time.time()-t0:.0f}s] TS {P} eq ({En},{L},{mu2}): {len(sing)} located singular points", flush=True)
    r = V.search(S, sing, log=lambda m: print(f"[{time.time()-t0:.0f}s] {m}", flush=True), skip_failed=True)
    r["located"] = [str(complex(round(c.real, 6), round(c.imag, 6))) for c in sing]
    print(f"[{time.time()-t0:.0f}s] v2 certificate found: {r['found']} {r.get('why', '')}", flush=True)
    if r["found"]:
        # save the v2 certificate BEFORE the (slow) v1 replay, so a later guard kill cannot lose it
        json.dump(dict(r, assessment="v2 certificate found; v1 replay pending"), open(
            os.path.join(HERE, f"{os.path.basename(__file__)[:-3]}_row{i}_v2cert.json"), "w"), indent=1, default=str)
        r["v1_replay"] = V.replay_v1(S, r, sing)
        print(f"[{time.time()-t0:.0f}s] v1 replay: {r['v1_replay']['replayed']}", flush=True)
        r["assessment"] = "CORROBORATED (v2 certificate, v1 replay)" if r["v1_replay"]["replayed"] else \
            "v2 certificate, v1 replay FAILED (not corroboration)"
    else:
        r["assessment"] = "monodromy corroboration still absent at this row"
    r["seconds"] = round(time.time() - t0, 1)
    return r


def run_all():
    import mr_watchdog as W
    res = []
    for i, (P, lev) in enumerate(ROWS):
        outp = os.path.join(HERE, f"mr_v2_ts2_row{i}.json")
        if os.path.exists(outp):
            os.remove(outp)
        g = W.run_guarded([sys.executable, "-u", os.path.abspath(__file__), "--one", str(i), outp], mem_limit_mb=2048,
                          time_limit_s=21600, cwd=HERE, log=os.path.join(HERE, f"mr_v2_ts2_row{i}.log"))
        r = json.load(open(outp)) if (g["status"] == "ok" and os.path.exists(outp)) else \
            dict(assessment=f"no result (guard: {g['status']})")
        r.update(point=P, level=lev, guard=g)
        res.append(r)
        print(f"{i} TS {P} eq {lev} => {r['assessment']} [guard {g['status']}, peak {g['peak_mb']} MB, {g['seconds']} s]",
              flush=True)
        json.dump(res, open(os.path.join(HERE, "mr_v2_ts2.json"), "w"), indent=1, default=str)
        os.system(f"cd {os.path.dirname(HERE)} && git add qsim/mr_v2_ts2.json qsim/mr_v2_ts2_row{i}.json "
                  f"qsim/mr_v2_ts2_row{i}.log qsim/mr_v2_ts2.txt 2>/dev/null; git commit -q -m 'TS v2 re-cert: row {i} "
                  f"raw output\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>' && git push -q origin main")


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--one":
        json.dump(run_row(int(sys.argv[2])), open(sys.argv[3], "w"), indent=1, default=str)
    elif sys.argv[1] == "GATES":
        res = gates(); print(json.dumps(res, indent=1)); json.dump(res, open(os.path.join(HERE, "mr_v2_ts2_gates.json"), "w"), indent=1)
    else:
        run_all()
