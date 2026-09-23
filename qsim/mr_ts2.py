"""
Stage 2 of the Morales-Ramis tool: Tomimatsu-Sato delta = 2, exactly as registered in
PREREG_ts2_morales_ramis.md (80a631b + 3654441), filed before any computation on the target.

The tool is the Stage-1 code, unchanged. The only new code is here:
  - load_wp(): srepr lower-metric components (T, x, y, phi) -> inverse-metric dict for
    mr_nve.nve_equatorial;
  - zv2_wp(): the q = 0 reduction (ZV delta = 2) written as LOWER components, so control C1
    goes through the same loader and inversion as the target;
  - the registered rows, trust order, and the exact identities for C1 and C2.

Usage:  python mr_ts2.py [i,j,...]      (guarded run of the rows, in registered order)
        python mr_ts2.py --one i out.json
"""
import json, os, sys, time
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mr_kovacic as K, mr_monodromy as MO, mr_nve as N

PKG = "/Users/sumit/Github/conjecture_machine/data/sealed/TS2_for_quantum"
X, Y, SIG = sp.Symbol("x", real=True), sp.Symbol("y", real=True), sp.Symbol("sigma", real=True)


def _read_components(path):
    comps = {}
    for line in open(path):
        if " = " not in line or line.startswith("#"):
            continue
        k, v = line.split(" = ", 1)
        comps[k.strip()] = sp.parse_expr(v.strip())
    return comps


def _inverse(g, sigma):
    """g: lower components g_TT, g_Tphi, g_phiphi, g_xx, g_yy (in X, Y, SIG)."""
    s = {SIG: sigma}
    gTT, gTp, gpp, gxx, gyy = (sp.sympify(g[k]).subs(s) for k in ("g_TT", "g_Tphi", "g_phiphi", "g_xx", "g_yy"))
    det = sp.cancel(gTT*gpp - gTp**2)
    c = lambda e: sp.factor(sp.cancel(e))
    return dict(tt=c(gpp/det), tphi=c(-gTp/det), phiphi=c(gTT/det), xx=c(1/gxx), yy=c(1/gyy))


def load_wp(fname, sigma):
    return _inverse(_read_components(os.path.join(PKG, fname)), sigma)


def zv2_wp(sigma=1):
    """q = 0 of the manifest's formulas (p = 1): f = ((x-1)/(x+1))^2, omega = 0,
    e^{2gamma} = (x^2-1)^4/(x^2-y^2)^4 -- as lower components in the manifest's line element."""
    x, y = X, Y
    f = ((x - 1)/(x + 1))**2
    e2g = (x**2 - 1)**4/(x**2 - y**2)**4
    g = dict(g_TT=-f, g_Tphi=0, g_phiphi=SIG**2*(x**2 - 1)*(1 - y**2)/f,
             g_xx=e2g*SIG**2*(x**2 - y**2)/((x**2 - 1)*f), g_yy=e2g*SIG**2*(x**2 - y**2)/((1 - y**2)*f))
    return _inverse(g, sigma)


R = sp.Rational
TS_P1, TS_P2 = "ts2_metric_components_t1o2.txt", "ts2_metric_components_t1o3.txt"
KERR_P1, KERR_P2 = "ts2_KERR_metric_components_t1o2.txt", "ts2_KERR_metric_components_t1o3.txt"

# (tag, name, ginv builder, (E, L, mu^2), expected, identity-check name or None)
ROWS = [
    ("C1", "ZV delta=2 via WP loader (1,0,4)", lambda: zv2_wp(1), (1, 0, 4), K.OBSTRUCTION, "C1_vs_stage1_A"),
    ("C2", "Kerr-WP P2 sigma=4/5 B1 (3,0,118)", lambda: load_wp(KERR_P2, R(4, 5)), (3, 0, 118), K.NO_OBSTRUCTION, "C2_vs_stage1_B"),
    ("C2", "Kerr-WP P2 sigma=4/5 B2 (1,2,125/63)", lambda: load_wp(KERR_P2, R(4, 5)), (1, 2, R(125, 63)), K.NO_OBSTRUCTION, "C2_vs_stage1_B"),
    ("C3", "Kerr-WP P1 (1,0,4)", lambda: load_wp(KERR_P1, 1), (1, 0, 4), K.NO_OBSTRUCTION, None),
    ("C3", "Kerr-WP P2 (1,0,4)", lambda: load_wp(KERR_P2, 1), (1, 0, 4), K.NO_OBSTRUCTION, None),
    ("C3", "Kerr-WP P1 (1,0,9)", lambda: load_wp(KERR_P1, 1), (1, 0, 9), K.NO_OBSTRUCTION, None),
    ("C3", "Kerr-WP P2 (1,0,9)", lambda: load_wp(KERR_P2, 1), (1, 0, 9), K.NO_OBSTRUCTION, None),
    ("T1", "TS2 P1 (1,0,4)", lambda: load_wp(TS_P1, 1), (1, 0, 4), None, None),
    ("T1", "TS2 P2 (1,0,4)", lambda: load_wp(TS_P2, 1), (1, 0, 4), None, None),
    ("T2", "TS2 P1 (1,0,9)", lambda: load_wp(TS_P1, 1), (1, 0, 9), None, None),
    ("T2", "TS2 P2 (1,0,9)", lambda: load_wp(TS_P2, 1), (1, 0, 9), None, None),
    # secondary (registered): C3 at L = 1 first, then T3
    ("C3", "Kerr-WP P1 (1,1,4)", lambda: load_wp(KERR_P1, 1), (1, 1, 4), K.NO_OBSTRUCTION, None),
    ("C3", "Kerr-WP P2 (1,1,4)", lambda: load_wp(KERR_P2, 1), (1, 1, 4), K.NO_OBSTRUCTION, None),
    ("T3", "TS2 P1 (1,1,4)", lambda: load_wp(TS_P1, 1), (1, 1, 4), None, None),
    ("T3", "TS2 P2 (1,1,4)", lambda: load_wp(TS_P2, 1), (1, 1, 4), None, None),
]


def _identity(kind, nve, ELm):
    """Exact identities registered for C1 and C2."""
    xs, ys = sp.symbols("x y")
    if kind == "C1_vs_stage1_A":
        ref = N.nve_equatorial(N.zipoy_voorhees(2, xs, ys), xs, ys, E=1, L=0, mu=2)
        return {f: sp.cancel(nve[f] - ref[f].subs(xs, X)) == 0 for f in ("r_xi2", "r_xi1")}
    if kind == "C2_vs_stage1_B":
        E, L, m2 = ELm
        rs, us = sp.symbols("r u")
        s = R(4, 5)
        out = {}
        for sgn in (1, -1):
            ref = N.nve_equatorial(N.kerr(1, R(3, 5), rs, us), rs, us, E=E, L=sgn*L, mu=sp.sqrt(m2))
            out[f"L_sign_{sgn:+d}"] = {f: sp.cancel(nve[f] - s**2*ref[f].subs(rs, s*X + 1)) == 0
                                       for f in ("r_xi2", "r_xi1")}
        return out
    return None


def _describe(rr):
    num, den = sp.fraction(sp.cancel(rr))
    fac = sp.factor_list(den, X)[1]
    return dict(deg_num=int(sp.degree(num, X)), deg_den=int(sp.degree(den, X)),
                den_factors=[(str(g) if sp.degree(g, X) <= 2 else f"<deg {sp.degree(g, X)} factor>", int(e))
                             for g, e in fac])


def run_row(i):
    tag, name, build, ELm, expected, ident = ROWS[i]
    t0 = time.time()
    E, L, m2 = ELm
    ginv = build()
    print(f"[{time.time()-t0:.1f}s] loaded", flush=True)
    nve = N.nve_equatorial(ginv, X, Y, E=E, L=L, mu=sp.sqrt(m2))
    print(f"[{time.time()-t0:.1f}s] NVE built", flush=True)
    row = dict(control=tag, name=name, ELmu2=[str(v) for v in ELm], expected=expected, forms={})
    if ident:
        row["identity"] = _identity(ident, nve, ELm)
        print(f"[{time.time()-t0:.1f}s] identity {row['identity']}", flush=True)
    for form in ("r_xi2", "r_xi1"):
        rr = nve[form]
        if rr is None:
            row["forms"][form] = dict(verdict=K.NO_OBSTRUCTION, case="analytic",
                                      reason="DEGENERATE NVE, B == 0 (analytic, not Kovacic)", monodromy="NOT_APPLICABLE")
            continue
        d = _describe(rr)
        print(f"[{time.time()-t0:.1f}s] {form}: {d}", flush=True)
        v, reason, k = K.morales_ramis_verdict(rr, X)
        print(f"[{time.time()-t0:.1f}s] {form}: Kovacic -> {v} ({reason})", flush=True)
        mv, mwhy, minfo = MO.monodromy_verdict(rr, X)
        print(f"[{time.time()-t0:.1f}s] {form}: monodromy -> {mv} ({mwhy})", flush=True)
        row["forms"][form] = dict(verdict=v, case=(k["case"] if k else None), reason=reason, structure=d,
                                  monodromy=mv, monodromy_why=mwhy, monodromy_det_err=(minfo or {}).get("det_err"))
    row["seconds"] = round(time.time() - t0, 1)
    return row


def _identity_ok(row):
    idn = row.get("identity")
    if idn is None:
        return True
    if "r_xi2" in idn:
        return all(idn.values())
    return any(all(v.values()) for v in idn.values())


def run_guarded_all(mem_limit_mb=1024, time_limit_s=1800, only=None):
    import mr_watchdog as W
    rows = []
    for i, (tag, name, build, ELm, expected, ident) in enumerate(ROWS):
        if only is not None and i not in only:
            continue
        outp = os.path.join(HERE, f"mr_ts2_row_{i}.json")
        if os.path.exists(outp):
            os.remove(outp)
        g = W.run_guarded([sys.executable, "-u", os.path.abspath(__file__), "--one", str(i), outp],
                          mem_limit_mb=mem_limit_mb, time_limit_s=time_limit_s, cwd=HERE,
                          log=os.path.join(HERE, f"mr_ts2_row_{i}.log"))
        if g["status"] == "ok" and os.path.exists(outp):
            row = json.load(open(outp))
        else:
            row = dict(control=tag, name=name, ELmu2=[str(v) for v in ELm], expected=expected,
                       forms={f: dict(verdict=K.INCONCLUSIVE, case=None, reason=f"resource limit: {g['status']}",
                                      monodromy="NOT_RUN") for f in ("r_xi2", "r_xi1")})
        row["guard"] = g
        vs = {f["verdict"] for f in row["forms"].values()}
        mono = [f["monodromy"] for f in row["forms"].values() if f["monodromy"] in (K.OBSTRUCTION, K.NO_OBSTRUCTION)]
        row["forms_agree"] = len(vs) == 1
        row["verdict"] = row["forms"]["r_xi2"]["verdict"] if row["forms_agree"] else "FAIL (forms disagree)"
        row["monodromy_agree"] = all(m == row["forms"]["r_xi2"]["verdict"] for m in mono)
        row["single_route"] = len(mono) == 0
        if not row["monodromy_agree"]:
            row["verdict"] = "FAIL (routes disagree)"
        row["identity_ok"] = _identity_ok(row)
        row["ok"] = (row["verdict"] == expected and row["identity_ok"]) if expected else None
        rows.append(row)
        print(f"{i:>2} {tag:<3} {name:<38} -> {row['verdict']:<22} cases "
              f"{[f.get('case') for f in row['forms'].values()]} monodromy "
              f"{[f['monodromy'] for f in row['forms'].values()]}"
              + (f" identity {row.get('identity')}" if ident else "")
              + (f" expected {expected}: {'PASS' if row['ok'] else 'FAIL'}" if expected else "  [TARGET]")
              + f"   [guard {g['status']}, peak {g['peak_mb']} MB, {g['seconds']} s]", flush=True)
        json.dump(rows, open(os.path.join(HERE, "mr_ts2_run.json"), "w"), indent=1, default=str)
    return rows


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--one":
        json.dump(run_row(int(sys.argv[2])), open(sys.argv[3], "w"), indent=1, default=str)
    else:
        only = set(int(a) for a in sys.argv[1].split(",")) if len(sys.argv) > 1 else None
        run_guarded_all(only=only)
