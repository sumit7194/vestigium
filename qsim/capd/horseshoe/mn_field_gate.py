"""B10 gate (PREREG_chaos_horseshoe_phase2.md, B10): the A-free regularised MN/Kerr reduced Hamiltonian equals the
original one IDENTICALLY, and my metric construction matches the supplied components.

Part 1 (exact, symbolic): in the field Q(x, y, a, b, E2, k, alpha, E, L, p_x, p_y, G2), where a, b are the two
exponential factors of MN_METRIC.md, E2 = e^{2 psi} and G2 = e^{2 gamma} are independent symbols, and A, B, C are the
MN_METRIC polynomials in (x, y, a, b):
  (i)   (x^2-1)(1-y^2) B^2 - 4 C^2 = A Q, remainder exactly 0 (Q returned);
  (ii)  g_phiphi = -f w^2 + rho^2/f equals [E2^-1 k^2 Q + 4k w0 C - E2 w0^2 A]/B;
  (iii) V_orig = [f (L - w E)^2 - rho^2 E^2 / f] / (2 rho^2) equals the B10 form
        V = 1/2 [E2 A L'^2 - 4k C E L' - E2^-1 k^2 E^2 Q] / (rho^2 B), with L' = L + w0 E;
  (iv)  the full H_red, built from the inverse metric, equals 1/2 (g^xx p_x^2 + g^yy p_y^2) + V_B10.
  Here f = E2 A/B, w = 2k E2^-1 C/A - w0, w0 = 4k alpha/(1-alpha^2), rho^2 = k^2 (x^2-1)(1-y^2).
Part 2 (convention check, numeric at 50 digits): at random points (x, y) in the exterior, g_tt, g_tphi, g_phiphi, g_xx
and g_yy from MY construction (with the true a, b, psi, gamma of MN_METRIC.md) equal the supplied component files
(mn_metric_components_{p1,p2,KERR_p1,KERR_p2}.txt, read-only) to <= 1e-40 relative.
Writes mn_field_gate.json next to this file. Exit status 0 iff every check passes."""
import json, random, sys
from pathlib import Path
import sympy as sp

HERE = Path(__file__).resolve().parent
PKG = Path("/Users/sumit/Github/conjecture_machine/data/MN_for_quantum")

x, y, a, b, E2, G2, k, al, E, L, px, py = sp.symbols("x y a b E2 G2 k alpha E L p_x p_y")
A = (x**2 - 1) * (1 + a*b)**2 - (1 - y**2) * (b - a)**2
B = (x + 1 + (x - 1)*a*b)**2 + ((1 + y)*a + (1 - y)*b)**2
C = (x**2 - 1) * (1 + a*b) * (b - a - y*(a + b)) + (1 - y**2) * (b - a) * (1 + a*b + x*(1 - a*b))
w0 = 4*k*al / (1 - al**2)
rho2 = k**2 * (x**2 - 1) * (1 - y**2)
f = E2 * A / B
w = 2*k*C / (E2 * A) - w0


def part1():
    out = {}
    num = sp.expand((x**2 - 1) * (1 - y**2) * B**2 - 4*C**2)
    Qp, r = sp.div(sp.Poly(num, x, y, a, b), sp.Poly(A, x, y, a, b))
    out["identity_remainder_zero"] = r.is_zero
    out["Q_terms"] = len(Qp.terms())
    Q = Qp.as_expr()
    gpp_orig = -f*w**2 + rho2/f
    gpp_reg = (k**2*Q/E2 + 4*k*w0*C - E2*w0**2*A) / B
    out["g_phiphi_identical"] = sp.cancel(sp.together(gpp_orig - gpp_reg)) == 0
    Lp = L + w0*E
    V_orig = (f*(L - w*E)**2 - rho2*E**2/f) / (2*rho2)
    V_reg = sp.Rational(1, 2) * (E2*A*Lp**2 - 4*k*C*E*Lp - k**2*E**2*Q/E2) / (rho2*B)
    out["V_identical"] = sp.cancel(sp.together(V_orig - V_reg)) == 0
    # full H_red from the inverse metric, p_t = -E, p_phi = L
    gtt, gtp, gpp = -f, f*w, gpp_orig
    gxx = k**2 * G2 * (x**2 - y**2) / (f * (x**2 - 1))
    gyy = k**2 * G2 * (x**2 - y**2) / (f * (1 - y**2))
    D = gtt*gpp - gtp**2                                   # = -rho^2
    out["tphi_block_det_is_minus_rho2"] = sp.cancel(sp.together(D + rho2)) == 0
    Ginv_tt, Ginv_tp, Ginv_pp = gpp/D, -gtp/D, gtt/D
    H_orig = sp.Rational(1, 2) * (Ginv_tt*E**2 + 2*Ginv_tp*(-E)*L + Ginv_pp*L**2 + px**2/gxx + py**2/gyy)
    H_reg = sp.Rational(1, 2) * (px**2/gxx + py**2/gyy) + V_reg
    out["H_red_identical"] = sp.cancel(sp.together(H_orig - H_reg)) == 0
    return out, Q


def part2(npts=6, seed=20261018):
    import mpmath as mp
    mp.mp.dps = 60
    X, Y = sp.symbols("x y", positive=True)
    res = {}
    rnd = random.Random(seed)
    for tag, fname, (M, aa, beta) in (("p1", "mn_metric_components_p1.txt", (5, 3, sp.Rational(1, 5))),
                                      ("p2", "mn_metric_components_p2.txt", (13, 5, sp.Rational(-1, 3))),
                                      ("KERR_p1", "mn_metric_components_KERR_p1.txt", (5, 3, 0)),
                                      ("KERR_p2", "mn_metric_components_KERR_p2.txt", (13, 5, 0))):
        comps = {}
        for line in (PKG / fname).read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, _, ex = line.partition("=")
                try: comps[key.strip()] = sp.sympify(ex.strip(), locals={"x": X, "y": Y})
                except Exception: pass
        chi = sp.Rational(aa, M); kk = sp.sqrt(M**2 - aa**2); alpha = (-1 + sp.sqrt(1 - chi**2)) / chi
        Rr = sp.sqrt(X**2 + Y**2 - 1); u = X*Y/Rr; P = [sp.legendre(l, u) for l in range(4)]
        psi = beta * P[2] / Rr**3
        aexp = -alpha * sp.exp(-2*beta*(-1 + sum((X - Y) * P[l] / Rr**(l + 1) for l in range(3))))
        bexp = alpha * sp.exp(2*beta*(1 + sum((-1)**(3 - l) * (X + Y) * P[l] / Rr**(l + 1) for l in range(3))))
        g2 = ((X**2 - 1)/(X**2 - Y**2)) * sp.exp(3*beta**2*(P[3]**2 - P[2]**2)/Rr**6 +
              2*beta*sum(((X - Y) + (-1)**l*(X + Y)) * P[l] / Rr**(l + 1) - 2 for l in range(3)) + 8*beta) * \
             A.subs({x: X, y: Y, a: aexp, b: bexp}) / ((X**2 - 1) * (1 - alpha**2)**2)
        sub = {x: X, y: Y, a: aexp, b: bexp, E2: sp.exp(2*psi), G2: g2, k: kk, al: alpha}
        mine = {"g_tt": (-f).subs(sub), "g_tphi": (f*w).subs(sub), "g_phiphi": (-f*w**2 + rho2/f).subs(sub),
                "g_xx": (k**2*G2*(x**2 - y**2)/(f*(x**2 - 1))).subs(sub),
                "g_yy": (k**2*G2*(x**2 - y**2)/(f*(1 - y**2))).subs(sub)}
        worst = {}
        for name, ex in mine.items():
            keys = [c for c in comps if c.replace("_", "").lower() == name.replace("_", "").lower()]
            if not keys: worst[name] = "component not found in file"; continue
            ref = comps[keys[0]]; m = 0
            for _ in range(npts):
                xv = sp.Rational(rnd.randint(1500, 6000), 1000); yv = sp.Rational(rnd.randint(50, 900), 1000)   # y > 0: the files declare y positive
                vm = mp.mpf(sp.N(ex.subs({X: xv, Y: yv}), 60)); vr = mp.mpf(sp.N(ref.subs({X: xv, Y: yv}), 60))
                m = max(m, abs(vm - vr) / max(abs(vr), mp.mpf(10)**-30))
            worst[name] = float(m)
        res[tag] = dict(found=sorted(comps), worst_rel=worst)
    return res


if __name__ == "__main__":
    p1, Q = part1()
    print("part1", p1, flush=True)
    p2 = part2()
    print("part2", json.dumps(p2, indent=1), flush=True)
    ok2 = all(isinstance(v, float) and v <= 1e-40 for r in p2.values() for v in r["worst_rel"].values())
    ok = all(v is True for kk_, v in p1.items() if kk_ != "Q_terms") and p1["Q_terms"] == 46 and ok2
    (HERE / "mn_field_gate.json").write_text(json.dumps(dict(part1=p1, part2=p2, Q=str(Q), GATE=ok), indent=1, default=str))
    print("GATE", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
