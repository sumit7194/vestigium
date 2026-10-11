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

if __name__ == "__main__":
    main()
