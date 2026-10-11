"""Exact field gate for the CAPD third replay: the BRIDGE's independently derived p, q (TheBridge export, read-only)
must equal this repo's p, q as rational functions -- checked as an exact polynomial identity
P_bridge * Q_mine - P_mine * Q_bridge == 0 (all coefficients, exact Fractions), for p and for q.
Also: row parameters must match. Usage: replay_gate.py ts   -> writes replay_gate_ts.json"""
import ast, json, sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
QSIM = HERE.parent
sys.path.insert(0, str(QSIM))
BRIDGE = Path("/Users/sumit/Github/TheBridge/falsification/V8_ts2_obstruction_check/export_capd")

def bridge_poly(mons):
    out = {}
    for mon, c in mons:
        assert len(mon) == 1
        out[mon[0]] = out.get(mon[0], Fraction(0)) + Fraction(c)
    return out

def mine_system(family, row):
    import sympy as sp
    if family == "ts2":
        import mr_v2_ts2 as T
        P, (En, L, mu2) = T.ROWS[row]; S, _ = T.system(P, En, L, mu2); params = (En, L, mu2)
    else:
        import mr_ts2_chaos as C
        name, key, p, (En, L, mu2), kind = C.ROWS[row]; S, _ = C.system(key, En, L, mu2); params = (En, L, mu2)
    var = S["var"]; out = {}
    for nm in ("p", "q"):
        for part in ("P", "Q"):
            poly = sp.Poly(sp.expand(S["to_expr"](S[nm], part)), var)
            out[nm + part] = {i: Fraction(int(c.p), int(c.q)) for (i,), c in poly.terms()}
    return out, tuple(Fraction(str(sp.Rational(x))) for x in params), str(var)

def pmul(a, b):
    r = {}
    for i, x in a.items():
        for j, y in b.items(): r[i + j] = r.get(i + j, Fraction(0)) + x * y
    return {k: v for k, v in r.items() if v != 0}

def identical(Pb, Qb, Pm, Qm):
    l, r = pmul(Pb, Qm), pmul(Pm, Qb)
    keys = set(l) | set(r)
    return all(l.get(k, 0) == r.get(k, 0) for k in keys)

def main():
    res = []
    for f in sorted(BRIDGE.glob("ts2_row_*.json")):
        b = json.load(open(f))
        tag = b["row"]
        fam, row = ("ts2", int(tag)) if not tag.startswith("C") else ("tschaos", int(tag[1:]) - 1)
        mine, params, var = mine_system(fam, row)
        bp = ast.literal_eval(b["p"]) if isinstance(b["p"], str) else b["p"]
        bq = ast.literal_eval(b["q"]) if isinstance(b["q"], str) else b["q"]
        bpar = tuple(Fraction(b["row_params"][k]) for k in ("E", "L", "mu2"))
        ok_p = identical(bridge_poly(bp["num"]), bridge_poly(bp["den"]), mine["pP"], mine["pQ"])
        ok_q = identical(bridge_poly(bq["num"]), bridge_poly(bq["den"]), mine["qP"], mine["qQ"])
        r = dict(bridge_file=f.name, mine=f"{fam} row {row}", params_match=(bpar == params), var_match=(b["var"] == var),
                 p_identical=ok_p, q_identical=ok_q, exps_empty=(b["exps"] == []))
        r["GATE"] = all([r["params_match"], r["var_match"], ok_p, ok_q, r["exps_empty"]])
        print(r, flush=True); res.append(r)
    import subprocess
    commit = subprocess.run(["git", "-C", str(BRIDGE), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = dict(bridge_commit=commit, rows=res, all_pass=all(r["GATE"] for r in res))
    json.dump(out, open(HERE / "replay_gate_ts.json", "w"), indent=1)
    print("ALL PASS" if out["all_pass"] else "GATE FAILURES")

BRIDGE_MN = Path("/Users/sumit/Github/TheBridge/falsification/V9_mn_obstruction_check/export_capd")

def mn_eq(rows):
    """MN equatorial: polynomials in (t, E1, E2, E3) with E_k independent symbols; exps must equal my w_k exactly."""
    import ast, subprocess, sympy as sp
    import mr_v2 as V, mr_v2_mneq as M, mr_mn_equatorial as ME
    res = []
    for row in rows:
        f = BRIDGE_MN / f"mneq_row_{row}.json"
        if not f.exists(): print("missing", f); continue
        b = json.load(open(f))
        p_, (En, L, mu2) = M.ROWS[row]
        G, (A, B, X), cd, src = ME.build("mn", p_, En, L, mu2)
        S = V.system_equatorial("mn", p_, En, L, mu2)
        mine = {}
        for nm in ("p", "q"):
            for part in ("P", "Q"):
                poly = getattr(S[nm], part)
                mine[nm + part] = {tuple(int(x) for x in mon): Fraction(int(c.p), int(c.q)) for mon, c in poly.terms()}
        def bpoly(m):
            m = ast.literal_eval(m) if isinstance(m, str) else m
            out = {}
            for mon, c in m: out[tuple(mon)] = out.get(tuple(mon), Fraction(0)) + Fraction(c)
            return out
        bp = ast.literal_eval(b["p"]) if isinstance(b["p"], str) else b["p"]
        bq = ast.literal_eval(b["q"]) if isinstance(b["q"], str) else b["q"]
        ok_p = identical(bpoly(bp["num"]), bpoly(bp["den"]), mine["pP"], mine["pQ"])
        ok_q = identical(bpoly(bq["num"]), bpoly(bq["den"]), mine["qP"], mine["qQ"])
        t = ME.T_
        ok_e = len(b["exps"]) == len(cd["gens"])
        for e, g in zip(b["exps"], cd["gens"]):
            numS = sum(sp.Rational(str(Fraction(c))) * t**i for i, c in enumerate(e["num"]))
            denS = sum(sp.Rational(str(Fraction(c))) * t**i for i, c in enumerate(e["den"]))
            ok_e &= sp.cancel(numS / denS - g) == 0
        bpar = tuple(Fraction(str(b["row_params"][k])) for k in ("E", "L", "mu2"))
        mpar = tuple(Fraction(str(sp.Rational(x))) for x in (En, L, mu2))
        r = dict(bridge_file=f.name, mine=f"mneq row {row}", params_match=(bpar == mpar), var_match=(b["var"] == "t"),
                 p_identical=ok_p, q_identical=ok_q, exps_identical=bool(ok_e),
                 n_terms=dict(p_num=len(bpoly(bp["num"])), p_den=len(bpoly(bp["den"])), q_num=len(bpoly(bq["num"])), q_den=len(bpoly(bq["den"]))))
        r["GATE"] = all([r["params_match"], r["var_match"], ok_p, ok_q, r["exps_identical"]])
        print(r, flush=True); res.append(r)
    commit = subprocess.run(["git", "-C", str(BRIDGE_MN), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = dict(bridge_commit=commit, rows=res, all_pass=bool(res) and all(r["GATE"] for r in res))
    json.dump(out, open(HERE / ("replay_gate_mneq_%s.json" % "_".join(map(str, rows))), "w"), indent=1)
    print("ALL PASS" if out["all_pass"] else "GATE FAILURES")

def mn_axial(rows):
    """MN axial (VREPRO rows 0-3 = bridge V9 rows 6-9): polynomials in (x, E1) with E1 = exp(2 beta/x^3) as an
    independent symbol; the bridge's single exp must equal 2 beta/x^3 exactly."""
    import ast, subprocess, sympy as sp
    import mr_v2 as V, mr_v2_ladder as LD, mr_mn_axis as MA
    MAP = {0: ("p1", 4), 1: ("p1", 9), 2: ("p2", 4), 3: ("p2", 9)}
    res = []
    for row in rows:
        pt, mu2 = MAP[row]
        f = BRIDGE_MN / f"mnaxial_{pt}_E1_mu2{mu2}.json"
        if not f.exists(): print("missing", f); continue
        b = json.load(open(f))
        name, build, expect = LD.rows("VREPRO")[row]
        assert name == f"MN {pt} axial (1,{mu2})", name
        S = build()
        mine = {}
        for nm in ("p", "q"):
            for part in ("P", "Q"):
                poly = getattr(S[nm], part)
                mine[nm + part] = {tuple(int(x) for x in mon): Fraction(int(c.p), int(c.q)) for mon, c in poly.terms()}
        def bpoly(m):
            m = ast.literal_eval(m) if isinstance(m, str) else m
            out = {}
            for mon, c in m: out[tuple(mon)] = out.get(tuple(mon), Fraction(0)) + Fraction(c)
            return out
        bp = ast.literal_eval(b["p"]) if isinstance(b["p"], str) else b["p"]
        bq = ast.literal_eval(b["q"]) if isinstance(b["q"], str) else b["q"]
        ok_p = identical(bpoly(bp["num"]), bpoly(bp["den"]), mine["pP"], mine["pQ"])
        ok_q = identical(bpoly(bq["num"]), bpoly(bq["den"]), mine["qP"], mine["qQ"])
        beta = MA.MN_POINTS[pt][1]; x = sp.Symbol("x")
        ok_e = len(b["exps"]) == 1
        if ok_e:
            e = b["exps"][0]
            numS = sum(sp.Rational(str(Fraction(c))) * x**i for i, c in enumerate(e["num"]))
            denS = sum(sp.Rational(str(Fraction(c))) * x**i for i, c in enumerate(e["den"]))
            ok_e = sp.cancel(numS / denS - 2 * beta / x**3) == 0
        r = dict(bridge_file=f.name, mine=f"mnaxv2 (VREPRO) row {row} = {name}", var_match=(b["var"] == "x"),
                 my_var=str(S["var"]), p_identical=ok_p, q_identical=ok_q, exp_identical=bool(ok_e))
        r["GATE"] = all([r["var_match"], str(S["var"]) == "x", ok_p, ok_q, r["exp_identical"]])
        print(r, flush=True); res.append(r)
    commit = subprocess.run(["git", "-C", str(BRIDGE_MN), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = dict(bridge_commit=commit, rows=res, all_pass=bool(res) and all(r["GATE"] for r in res))
    json.dump(out, open(HERE / "replay_gate_mnaxial.json", "w"), indent=1)
    print("ALL PASS" if out["all_pass"] else "GATE FAILURES")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mnaxial":
        mn_axial([int(x) for x in sys.argv[2:]])
    elif len(sys.argv) > 1 and sys.argv[1] == "mneq":
        mn_eq([int(x) for x in sys.argv[2:]])
    else:
        main()
