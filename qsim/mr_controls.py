"""
Stage-1 Hamiltonian controls for the Morales-Ramis tool -- exactly as fixed in
PREREG_morales_ramis_tool.md amendment 1 (8d7254a), filed before any control ran.

  A   Zipoy-Voorhees delta = 2, y = 0, p_y = 0, L = 0, E = 1, mu = 2 and 3   -> OBSTRUCTION
  A'  the same at delta = 1 (Schwarzschild)                                  -> NO_OBSTRUCTION
  B1  Kerr M = 1, a = 3/5, equatorial, L = 0, E = 3, mu^2 = 118              -> NO_OBSTRUCTION
  B2  Kerr, equatorial, L = 2, E = 1, mu^2 = 125/63                          -> NO_OBSTRUCTION

Every control runs on BOTH NVE forms (xi2 = dp_y, xi1 = dy), which must agree,
and through the monodromy route wherever the NVE is Fuchsian, which must agree.
Trust order is applied mechanically: A counts only if A' passed; B counts only
if the tool has already said OBSTRUCTION on A.
"""
import json, os, sys, time
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mr_kovacic as K, mr_monodromy as MO, mr_nve as N

x, y, r_, u = sp.symbols("x y r u")

CONTROLS = [
    ("A",  "ZV delta=2, mu=2", lambda: N.nve_equatorial(N.zipoy_voorhees(2, x, y), x, y, E=1, L=0, mu=2), x, K.OBSTRUCTION),
    ("A",  "ZV delta=2, mu=3", lambda: N.nve_equatorial(N.zipoy_voorhees(2, x, y), x, y, E=1, L=0, mu=3), x, K.OBSTRUCTION),
    ("A'", "ZV delta=1, mu=2", lambda: N.nve_equatorial(N.zipoy_voorhees(1, x, y), x, y, E=1, L=0, mu=2), x, K.NO_OBSTRUCTION),
    ("A'", "ZV delta=1, mu=3", lambda: N.nve_equatorial(N.zipoy_voorhees(1, x, y), x, y, E=1, L=0, mu=3), x, K.NO_OBSTRUCTION),
    # AMENDMENT 3 (filed after A's result, before any A'/A''/B result): the registered A' is
    # DEGENERATE (B == 0), so a NON-degenerate Schwarzschild poison is added -- L = 1.
    ("A''", "ZV delta=1, L=1, mu=2", lambda: N.nve_equatorial(N.zipoy_voorhees(1, x, y), x, y, E=1, L=1, mu=2), x, K.NO_OBSTRUCTION),
    ("A''", "ZV delta=1, L=1, mu=3", lambda: N.nve_equatorial(N.zipoy_voorhees(1, x, y), x, y, E=1, L=1, mu=3), x, K.NO_OBSTRUCTION),
    ("B1", "Kerr a=3/5 L=0 E=3 mu^2=118",
     lambda: N.nve_equatorial(N.kerr(1, sp.Rational(3, 5), r_, u), r_, u, E=3, L=0, mu=sp.sqrt(118)), r_, K.NO_OBSTRUCTION),
    ("B2", "Kerr a=3/5 L=2 E=1 mu^2=125/63",
     lambda: N.nve_equatorial(N.kerr(1, sp.Rational(3, 5), r_, u), r_, u, E=1, L=2, mu=sp.sqrt(sp.Rational(125, 63))), r_, K.NO_OBSTRUCTION),
]


def run():
    out = []
    for tag, name, build, var, expected in CONTROLS:
        t0 = time.time()
        nve = build()
        row = dict(control=tag, name=name, expected=expected, forms={})
        for form in ("r_xi2", "r_xi1"):
            rr = nve[form]
            if rr is None:                      # degenerate xi2 elimination (B == 0)
                row["forms"][form] = dict(
                    verdict=K.NO_OBSTRUCTION, case="analytic",
                    reason="DEGENERATE NVE, B == 0: decoupled, G0 in the additive group "
                           "(analytic argument, NOT a Kovacic verdict)",
                    poles={}, ord_inf=None, monodromy="NOT_APPLICABLE", monodromy_why="degenerate",
                    monodromy_det_err=None)
                continue
            R = K.RationalR(rr, var)
            v, reason, k = K.morales_ramis_verdict(rr, var)
            mv, mwhy, minfo = MO.monodromy_verdict(rr, var)
            row["forms"][form] = dict(
                verdict=v, case=(k["case"] if k else None), reason=reason,
                poles={str(c): m for c, m in R.poles.items()}, ord_inf=str(R.ord_inf),
                monodromy=mv, monodromy_why=mwhy,
                monodromy_det_err=(minfo or {}).get("det_err"))
        vs = {f["verdict"] for f in row["forms"].values()}
        forms_agree = len(vs) == 1
        mono = [f["monodromy"] for f in row["forms"].values() if f["monodromy"] not in ("NOT_APPLICABLE",)]
        mono_agree = all(m == row["forms"]["r_xi2"]["verdict"] for m in mono)
        row.update(forms_agree=forms_agree, monodromy_agree=mono_agree,
                   verdict=row["forms"]["r_xi2"]["verdict"],
                   ok=forms_agree and mono_agree and row["forms"]["r_xi2"]["verdict"] == expected,
                   seconds=round(time.time() - t0, 1))
        out.append(row)
        print(f"{tag:<3} {name:<30} -> {row['verdict']:<15} (xi2 case {row['forms']['r_xi2']['case']}, "
              f"xi1 case {row['forms']['r_xi1']['case']}; forms agree {forms_agree}; monodromy "
              f"{[f['monodromy'] for f in row['forms'].values()]}) expected {expected}: "
              f"{'PASS' if row['ok'] else 'FAIL'}  ({row['seconds']}s)", flush=True)
    # trust order, mechanically
    ok = lambda t: all(rw["ok"] for rw in out if rw["control"] == t)
    A_ok, Ap_ok = ok("A"), ok("A'") and ok("A''")
    B_ok = ok("B1") and ok("B2")
    verdict = dict(
        A_prime=Ap_ok,
        A=(A_ok and Ap_ok),             # A counts only if A' passed
        B=(B_ok and A_ok),              # B counts only after an OBSTRUCTION was seen on A
        no_inconclusive=all(rw["verdict"] != K.INCONCLUSIVE for rw in out))
    verdict["STAGE1_CONTROLS_PASS"] = all(verdict.values())
    print("\nTRUST-ORDERED:", verdict)
    json.dump(dict(rows=out, verdict=verdict), open(os.path.join(HERE, "mr_controls_run.json"), "w"),
              indent=1, default=str)
    return out, verdict


if __name__ == "__main__":
    run()
