"""Optional SECOND exact gate (bridge 'factored' export): p, q rebuilt from the bridge's factors
    p = -(A_t/A - X_t/(2X)) - x2/x1,  q = x1^2 A B / X,  x1 = (1 - 1/t^2)/2, x2 = 1/t^3
must equal this repo's expanded p, q. Checked EXACTLY (Fractions) at 20 random rational points in (t, E1, E2, E3)
treated as independent variables (Schwartz-Zippel: a nonzero rational function vanishes at a random point of a
large grid with negligible probability), and the exps must equal my basis exactly. Usage: replay_gate_factored.py 0 1 .. 5"""
import ast, json, random, sys
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent))
BR = Path("/Users/sumit/Github/TheBridge/falsification/V9_mn_obstruction_check/export_capd")

def ev(m, t, E):
    tot = Fraction(0)
    for mon, c in m:
        v = Fraction(c) * t ** mon[0]
        for k, j in enumerate(mon[1:]): v *= E[k] ** j
        tot += v
    return tot

def main(rows):
    import mr_v2 as V, mr_v2_mneq as M, mr_mn_equatorial as ME, sympy as sp
    out = []
    R = random.Random(20261012)
    for row in rows:
        b = json.load(open(BR / f"mneq_factored_row_{row}.json"))
        fac = {k: {s: (ast.literal_eval(v[s]) if isinstance(v[s], str) else v[s]) for s in ("num", "den")} for k, v in b["factors"].items()}
        p_, (En, L, mu2) = M.ROWS[row]
        S = V.system_equatorial("mn", p_, En, L, mu2)
        G, (A, B, X), cd, src = ME.build("mn", p_, En, L, mu2)
        t_ = ME.T_
        ok_e = len(b["exps"]) == len(cd["gens"]) and all(
            sp.cancel(sum(sp.Rational(str(Fraction(c))) * t_**i for i, c in enumerate(e["num"])) /
                      sum(sp.Rational(str(Fraction(c))) * t_**i for i, c in enumerate(e["den"])) - g) == 0
            for e, g in zip(b["exps"], cd["gens"]))
        mine = {nm + part: [(tuple(int(x) for x in mon), Fraction(int(c.p), int(c.q))) for mon, c in getattr(S[nm], part).terms()]
                for nm in ("p", "q") for part in ("P", "Q")}
        K = len(b["exps"]); ok = True; npts = 0
        while npts < 20:
            t = Fraction(R.randint(-10**6, 10**6), R.randint(1, 10**6)); E = [Fraction(R.randint(-10**6, 10**6), R.randint(1, 10**6)) for _ in range(K)]
            f = {k: (ev(v["num"], t, E), ev(v["den"], t, E)) for k, v in fac.items()}
            if any(d == 0 for _, d in f.values()) or f["A"][0] == 0 or f["X"][0] == 0 or t == 0: continue
            A_, B_, X_, At, Xt = (f[k][0] / f[k][1] for k in ("A", "B", "X", "A_t", "X_t"))
            x1 = (1 - 1 / t**2) / 2; x2 = 1 / t**3
            pf = -(At / A_ - Xt / (2 * X_)) - x2 / x1; qf = x1**2 * A_ * B_ / X_
            Pm, Qm, Pq, Qq = (ev(mine[k], t, E) for k in ("pP", "pQ", "qP", "qQ"))
            if Qm == 0 or Qq == 0: continue
            ok &= (pf == Pm / Qm) and (qf == Pq / Qq); npts += 1
        r = dict(row=row, exps_identical=bool(ok_e), p_q_equal_at_20_random_rational_points=bool(ok), GATE=bool(ok and ok_e))
        print(r, flush=True); out.append(r)
    import subprocess
    commit = subprocess.run(["git", "-C", str(BR), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    json.dump(dict(bridge_commit=commit, rows=out, all_pass=all(r["GATE"] for r in out)), open(HERE / "replay_gate_factored.json", "w"), indent=1)
    print("ALL PASS" if all(r["GATE"] for r in out) else "GATE FAILURES")

if __name__ == "__main__":
    main([int(x) for x in sys.argv[1:]])
