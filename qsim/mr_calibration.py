"""
Calibration suite for the Morales-Ramis tool, exactly as pre-registered in
PREREG_morales_ramis_tool.md (59c4ae3). Every expected answer comes from a
classical theorem or holds by construction -- none from any fleet output.
"""
import sympy as sp
import mr_kovacic as K

z = sp.Symbol("z")
R_ = sp.Rational


def riemann_P(lam, mu, nu):
    """Reduced form y'' = r y of the Riemann P-equation with exponent differences
    lam, mu, nu at 0, 1, infinity."""
    return ((lam**2 - 1)/(4*z**2) + (mu**2 - 1)/(4*(z - 1)**2)
            - (lam**2 + mu**2 - nu**2 - 1)/(4*z*(z - 1)))


def bessel_reduced(nu):
    """Bessel z^2 y'' + z y' + (z^2 - nu^2) y = 0, reduced by y = u/sqrt z."""
    return -1 + (nu**2 - R_(1, 4))/z**2


CASES = [
    # name, r, expected verdict, expected Kovacic case (None = any), why
    ("y''=y", sp.Integer(1), K.NO_OBSTRUCTION, 1, "e^{+-z}"),
    ("y''=-2/(9z^2)y", -R_(2, 9)/z**2, K.NO_OBSTRUCTION, 1, "z^{1/3}, z^{2/3} algebraic"),
    ("y''=-1/(4z^2)y", -R_(1, 4)/z**2, K.NO_OBSTRUCTION, 1, "sqrt z, sqrt z log z: algebraic y1, additive G0"),
    ("Bessel 1/2", bessel_reduced(R_(1, 2)), K.NO_OBSTRUCTION, 1, "e^{+-iz}"),
    ("P(1/2,1/3,1/3)", riemann_P(R_(1, 2), R_(1, 3), R_(1, 3)), K.NO_OBSTRUCTION, 3, "Schwarz: tetrahedral"),
    ("P(1/2,1/3,1/4)", riemann_P(R_(1, 2), R_(1, 3), R_(1, 4)), K.NO_OBSTRUCTION, 3, "Schwarz: octahedral"),
    ("P(1/2,1/3,1/5)", riemann_P(R_(1, 2), R_(1, 3), R_(1, 5)), K.NO_OBSTRUCTION, 3, "Schwarz: icosahedral"),
    ("P(1/2,1/2,1/7)", riemann_P(R_(1, 2), R_(1, 2), R_(1, 7)), K.NO_OBSTRUCTION, 2, "dihedral"),
    ("Airy", z, K.OBSTRUCTION, 4, "classically non-Liouvillian"),
    ("Bessel 0", bessel_reduced(0), K.OBSTRUCTION, 4, "classically non-Liouvillian"),
    ("Weber z^2+1", z**2 + 1, K.OBSTRUCTION, 1, "Liouvillian but full Borel G0"),
    ("P(1/3,1/5,1/7)", riemann_P(R_(1, 3), R_(1, 5), R_(1, 7)), K.OBSTRUCTION, 4, "not in Schwarz's list"),
    ("sin z", sp.sin(z), K.INCONCLUSIVE, None, "not rational: must be refused"),
]


def run(verbose=True):
    results = []
    for name, r, exp_v, exp_case, why in CASES:
        v, reason, k = K.morales_ramis_verdict(r, z)
        case = k["case"] if k else None
        ok = (v == exp_v) and (exp_case is None or case == exp_case)
        results.append(dict(name=name, verdict=v, case=case, expected=exp_v,
                            expected_case=exp_case, ok=ok, reason=reason))
        if verbose:
            print(f"  {'PASS' if ok else 'FAIL'}  {name:<18} -> {v:<15} case {case}   "
                  f"(expected {exp_v}, case {exp_case}; {why})")
            if not ok:
                print(f"        reason: {reason}")
    return results


if __name__ == "__main__":
    res = run()
    print(f"\n{sum(r['ok'] for r in res)}/{len(res)} calibration entries pass")
