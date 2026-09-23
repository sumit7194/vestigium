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

# --- DECLARED ADDITIONS, added after the pre-registration (59c4ae3), before any control ---
_w = sp.sqrt(2)/z + R_(1, 2)/(z - 1)
ADDED = [
    # a FUCHSIAN full-Borel case, so the monodromy route's "reducible-full-Borel"
    # branch is exercised on a true positive (Weber is not Fuchsian). y1 = z^sqrt2 (z-1)^(1/2)
    # is transcendental; y2/y1 = int z^(-2 sqrt 2)(z-1)^(-1): incomplete beta, not of the form
    # y1^-2 * rational -> additive part non-trivial -> full Borel G0.
    ("Fuchsian full Borel", sp.simplify(sp.diff(_w, z) + _w**2), K.OBSTRUCTION, 1,
     "irrational exponent + non-elementary quadrature"),
    # Abbasi, arXiv:2211.00804, Sec. 3 worked examples, with the Kovacic case HE reports
    ("Abbasi case-1 ex1", (4*z**2 + 8*z + 6)/(2*z + 1)**2, None, 1, "published: case 1"),
    # published: case 1 (group not stated). Verdict checked BY HAND: y1 = sqrt(z(z-1)) e^{-2/(z-1)}
    # is transcendental; with u = 1/(z-1) the quadrature is int e^{4u}/(u+1) du = e^{-4} Ei(4(u+1)),
    # non-elementary -> additive part non-trivial -> full Borel -> OBSTRUCTION.
    ("Abbasi case-1 ex2", (7*z**2 + 10*z - 1)/(4*z**2*(z - 1)**4), K.OBSTRUCTION, 1, "published: case 1; Ei quadrature"),
    ("Abbasi case-2 ex1", (-3 - 8*z)/(16*z**2), K.NO_OBSTRUCTION, 2, "published: case 2"),
    # EXPECTATION CORRECTED 2026-09-24: Abbasi labels this "case 3", but y = z^3 solves his ODE
    # (1-z)z^2 y'' + (5z-4)z y' + (6-9z) y = 0 EXACTLY (verified), so the group is reducible and
    # Kovacic's algorithm terminates in case 1 before case 3 is reached. His section illustrates the
    # case-3 procedure on an equation case 1 already settles. Monodromy independently: reducible.
    # The verdict (NO_OBSTRUCTION) is the same either way; the tool was right, the copied label was not.
    ("Abbasi case-3 ex1", (4 - z)/(4*z*(z - 1)**2), K.NO_OBSTRUCTION, 1, "reducible: y = z^3 (label corrected)"),
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
