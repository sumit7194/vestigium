"""S5 field gate (PREREG §2, S5, as carried out after B10): my regularised MN/Kerr reduced Hamiltonian versus the
Bridge's independently derived one (TheBridge/falsification/V13_mn_chaotic_sea/code/v13_field.py, read-only).

Layer 1, EXACT: the polynomial layer. My A, B, C and Q (mn_field_gate) equal the Bridge's _polys(), as polynomials in
(x, y, a, b).
Layer 2, NUMERIC at 60 digits: the full reduced Hamiltonian
H = 1/2 (g^xx p_x^2 + g^yy p_y^2) + V, with V = W/2 in the Bridge's convention, evaluated at random (x, y, p_x, p_y)
in the exterior. My construction (mn_field_gate.part2 formulas: true a, b, psi, gamma) is compared against
v13_field.build + W_reg + ginv_reg, for p1, p2, F5-R and C0 (and their Kerr limits beta = 0) at (E, L) = (19/20, 3).
Pass: all relative differences <= 1e-45.
A mutation control (my V with L -> 1.001 L) must FAIL.
The two transcendental layers are written differently (R = sqrt(x^2+y^2-1) here; x sqrt(1+(y^2-1)/x^2) there), so this
layer is checked numerically rather than as a symbolic identity. That is stated in the prereg."""
import json, random, sys
from pathlib import Path
import sympy as sp, mpmath as mp

HERE = Path(__file__).resolve().parent
import types
sys.modules.setdefault("numba", types.ModuleType("numba"))   # v13_field imports numba but never uses it
sys.path.insert(0, "/Users/sumit/Github/TheBridge/falsification/V13_mn_chaotic_sea/code")
import v13_field as BR                                   # the Bridge's code (read-only import)
import mn_field_gate as Q

POINTS = {"p1": (5, 3, sp.Rational(1, 5)), "p2": (13, 5, sp.Rational(-1, 3)),
          "F5R": (89, 80, sp.Rational(19, 20) * sp.Rational(89, 39)**3), "C0": None}


def mine(M, aa, beta, E, L):
    X, Y = sp.symbols("x y", positive=True)
    chi = sp.Rational(aa, M); kk = sp.sqrt(M**2 - aa**2); alpha = (-1 + sp.sqrt(1 - chi**2)) / chi
    Rr = sp.sqrt(X**2 + Y**2 - 1); u = X*Y/Rr; P = [sp.legendre(l, u) for l in range(4)]
    psi = beta*P[2]/Rr**3
    aexp = -alpha*sp.exp(-2*beta*(-1 + sum((X - Y)*P[l]/Rr**(l + 1) for l in range(3))))
    bexp = alpha*sp.exp(2*beta*(1 + sum((-1)**(3 - l)*(X + Y)*P[l]/Rr**(l + 1) for l in range(3))))
    Gx = 3*beta**2*(P[3]**2 - P[2]**2)/Rr**6 + 2*beta*sum(((X - Y) + (-1)**l*(X + Y))*P[l]/Rr**(l + 1) - 2 for l in range(3)) + 8*beta
    sub = {Q.x: X, Q.y: Y, Q.a: aexp, Q.b: bexp, Q.k: kk, Q.al: alpha}
    A_, B_, C_ = (e.subs(sub) for e in (Q.A, Q.B, Q.C))
    Qp, _ = sp.div(sp.Poly(sp.expand((Q.x**2 - 1)*(1 - Q.y**2)*Q.B**2 - 4*Q.C**2), Q.x, Q.y, Q.a, Q.b),
                   sp.Poly(Q.A, Q.x, Q.y, Q.a, Q.b))
    Q_ = Qp.as_expr().subs(sub)
    w0 = 4*kk*alpha/(1 - alpha**2); rho2 = kk**2*(X**2 - 1)*(1 - Y**2); E2 = sp.exp(2*psi)
    Lp = L + w0*E
    V = sp.Rational(1, 2)*(E2*A_*Lp**2 - 4*kk*C_*E*Lp - kk**2*E**2*Q_/E2)/(rho2*B_)
    # g^xx = f (x^2-1) / (k^2 e^{2gamma} (x^2-y^2)), with e^{2gamma} = (x^2-1)/(x^2-y^2) e^G A /((x^2-1)(1-al^2)^2)
    gxx = E2*(X**2 - 1)*(1 - alpha**2)**2/(kk**2*B_*sp.exp(Gx))
    gyy = E2*(1 - Y**2)*(1 - alpha**2)**2/(kk**2*B_*sp.exp(Gx))
    return X, Y, gxx, gyy, V


def bridge(M, aa, beta, E, L):
    S = BR.build(M, aa, beta)
    gxx, gyy = BR.ginv_reg(S)
    return gxx, gyy, BR.W_reg(S, E, L) / 2


def main(npts=12, seed=20261018):
    mp.mp.dps = 70
    out = {}
    # layer 1
    Am, Bm, Cm, Qb = BR._polys()
    s = {BR.a_s: Q.a, BR.b_s: Q.b, BR.x: Q.x, BR.y: Q.y}
    _, Qm = Q.part1()
    out["layer1_exact"] = all(sp.expand(e1.subs(s) - e2) == 0 for e1, e2 in ((Am, Q.A), (Bm, Q.B), (Cm, Q.C), (Qb, Qm)))
    E, L = sp.Rational(19, 20), sp.Integer(3)
    pts = dict(POINTS); pts["C0"] = (10, 9, sp.Rational(19, 20) * (sp.Rational(10) / sp.sqrt(19))**3)
    rnd = random.Random(seed); out["layer2"] = {}
    for tag, (M, aa, beta) in list(pts.items()) + [(t + "_KERR", (v[0], v[1], 0)) for t, v in pts.items()]:
        X, Y, gxx, gyy, V = mine(M, aa, beta, E, L)
        bgxx, bgyy, bV = bridge(M, aa, beta, E, L)
        fm = sp.lambdify((X, Y), [gxx, gyy, V], "mpmath")
        fb = sp.lambdify((BR.x, BR.y), [bgxx, bgyy, bV], "mpmath")
        worst = 0.0; worst_mut = 0.0
        for _ in range(npts):
            xv = mp.mpf(rnd.randint(2000, 9000)) / 1000; yv = mp.mpf(rnd.randint(50, 950)) / 1000
            pxv = mp.mpf(rnd.randint(-500, 500)) / 1000; pyv = mp.mpf(rnd.randint(-500, 500)) / 1000
            m = fm(xv, yv); bb = fb(xv, yv)
            Hm = (m[0]*pxv**2 + m[1]*pyv**2)/2 + m[2]; Hb = (bb[0]*pxv**2 + bb[1]*pyv**2)/2 + bb[2]
            worst = max(worst, float(abs(Hm - Hb) / max(abs(Hb), mp.mpf(10)**-30)))
        # mutation control: my V with L -> 1.001 L must disagree
        _, _, _, _, Vmut = mine(M, aa, beta, E, L*sp.Rational(1001, 1000))
        fmut = sp.lambdify((X, Y), Vmut, "mpmath")
        xv, yv = mp.mpf(4), mp.mpf("0.5")
        worst_mut = float(abs(fmut(xv, yv) - fb(xv, yv)[2]) / abs(fb(xv, yv)[2]))
        out["layer2"][tag] = dict(worst_rel_H=worst, mutation_L_1001_rel=worst_mut,
                                  PASS=(worst <= 1e-45 and worst_mut > 1e-6))
        print(tag, out["layer2"][tag], flush=True)
    out["GATE"] = out["layer1_exact"] and all(v["PASS"] for v in out["layer2"].values())
    (HERE / "mn_s5_gate.json").write_text(json.dumps(out, indent=1))
    print("S5 GATE", "PASS" if out["GATE"] else "FAIL")
    return 0 if out["GATE"] else 1


if __name__ == "__main__":
    sys.exit(main())
