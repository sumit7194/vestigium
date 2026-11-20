"""mel_cert.py -- stage 1 of PREREG.md: Arb (python-flint) enclosures of the Melnikov harmonics L_n of the MN quadrupole
along Kerr's inclined homoclinic orbit at (M, a, r_u, z_m) = (5, 3, 16, 1/2), with gates G1-G5, the Kerr controls and the
sabotage control. Usage: mel_cert.py [--prec 128] [--only gates|L2|controls|all]   -> CHECKS.json (merged) and stdout.
Every number is an Arb ball; acb.integral is rigorous for integrands that return finite balls only where holomorphic
(sqrt with analytic=True; Carlson RF arguments checked to stay in Re > 0; r_h's denominator checked nonzero).
Written by Claude Opus 5.5 (session "Quantum")."""
import argparse, json, sys, time
from pathlib import Path
from flint import acb, arb, arb_mat, ctx
HERE = Path(__file__).resolve().parent
import mel_gen as GEN

M0, A0, RU, ZM = 5, 3, 16, acb(1) / 2
V23 = dict(E="0.935281504567998718539079668064", L="12.9725320356072806906865777805", Q="56.37733827951502222")
NAN = acb("nan")


def ball_ok(v):
    return v.is_finite()


# ------------------------------------------------------------------ G1: the level, by a Krawczyk step
def level():
    a, ru, zm = arb(A0), arb(RU), arb(1) / 2; M = arb(M0)
    def R(r, E, L, Q):
        D = r * r - 2 * M * r + a * a; return (E * (r * r + a * a) - a * L) ** 2 - D * (r * r + (L - a * E) ** 2 + Q)
    def dR(r, E, L, Q):
        D = r * r - 2 * M * r + a * a; dD = 2 * r - 2 * M
        return 2 * (E * (r * r + a * a) - a * L) * (2 * E * r) - dD * (r * r + (L - a * E) ** 2 + Q) - D * 2 * r
    def Fv(v):
        E, L, Q = v
        return [R(ru, E, L, Q), dR(ru, E, L, Q), Q - (Q + a * a * (1 - E * E) + L * L) * zm ** 2 + a * a * (1 - E * E) * zm ** 4]
    def J(v):                                      # analytic Jacobian (rows: equations; cols: E, L, Q)
        E, L, Q = v; r = ru; D = r * r - 2 * M * r + a * a; dD = 2 * r - 2 * M; X = E * (r * r + a * a) - a * L
        return [[2 * X * (r * r + a * a) - D * 2 * (L - a * E) * (-a), 2 * X * (-a) - D * 2 * (L - a * E), -D],
                [2 * (r * r + a * a) * (2 * E * r) + 2 * X * 2 * r - dD * 2 * (L - a * E) * (-a), 2 * (-a) * (2 * E * r) - dD * 2 * (L - a * E), -dD],
                [-a * a * (-2 * E) * zm ** 2 + a * a * (-2 * E) * zm ** 4, -2 * L * zm ** 2, 1 - zm ** 2]]
    x0 = [arb(V23["E"]), arb(V23["L"]), arb(V23["Q"])]
    for _ in range(3):                             # refine the midpoint by Newton (plain arb, midpoints)
        Jm = arb_mat(J(x0)); f = arb_mat([[v] for v in Fv(x0)]); d = Jm.solve(f)
        x0 = [arb((x0[i] - d[i, 0]).mid()) for i in range(3)]
    rad = arb("1e-27")
    X = [x0[i] + arb(0, rad) for i in range(3)]
    Y = arb_mat(J([arb(v.mid()) for v in x0])).inv()
    Ymid = arb_mat([[arb(Y[i, j].mid()) for j in range(3)] for i in range(3)])
    f0 = arb_mat([[v] for v in Fv([arb(v.mid()) for v in x0])])
    JX = arb_mat(J(X)); I = arb_mat([[1 if i == j else 0 for j in range(3)] for i in range(3)])
    dX = arb_mat([[X[i] - arb(x0[i].mid())] for i in range(3)])
    K = [arb(x0[i].mid()) for i in range(3)]
    Kv = arb_mat([[v] for v in K]) - Ymid * f0 + (I - Ymid * JX) * dX
    inside = all(Kv[i, 0].lower() > X[i].lower() and Kv[i, 0].upper() < X[i].upper() for i in range(3))
    E, L, Q = (Kv[i, 0] for i in range(3))
    return dict(E=E, L=L, Q=Q, krawczyk_inside=bool(inside), radius=max(float(Kv[i, 0].rad()) for i in range(3)),
                contains_v23=all(abs(arb(V23[n]) - v) < arb(tol) for n, v, tol in (("E", E, "1e-28"), ("L", L, "1e-27"), ("Q", Q, "1e-17"))),
                R16=R(ru, E, L, Q), dR16=dR(ru, E, L, Q))


class Orbit:
    def __init__(self, lv):
        a, ru, zm, M = arb(A0), arb(RU), arb(1) / 2, arb(M0)
        E, L, Q = lv["E"], lv["L"], lv["Q"]; self.E, self.L, self.Q = E, L, Q
        c4, c3, c2, c1, c0 = E * E - 1, 2 * M, a * a * (E * E - 1) - L * L - Q, 2 * M * ((a * E - L) ** 2 + Q), -a * a * Q
        # deflate by (r - 16)^2: synthetic division twice
        cc = [c4, c3, c2, c1, c0]
        for _ in range(2):
            out = [cc[0]]
            for v in cc[1:-1]: out.append(v + out[-1] * ru)
            self_rem = cc[-1] + out[-1] * ru; cc = out
        q2, q1, q0 = cc; disc = q1 * q1 - 4 * q2 * q0
        r1, r2 = (-q1 + disc.sqrt()) / (2 * q2), (-q1 - disc.sqrt()) / (2 * q2)
        self.rt, self.r4 = (r1, r2) if r1 > r2 else (r2, r1)
        self.A, self.B = self.rt - ru, ru - self.r4
        self.kap = ((1 - E * E) * self.A * self.B).sqrt()
        self.zp2 = Q / (a * a * (1 - E * E) * zm * zm); self.m = zm * zm / self.zp2
        self.K = acb(self.m).elliptic_k().real
        self.Ups = arb.pi() * a * (1 - E * E).sqrt() * self.zp2.sqrt() / (2 * self.K)
        self.a, self.ru, self.zm, self.M = a, ru, zm, M
        self.Rcoef = (c4, c3, c2, c1, c0)

    def R(self, r):
        c4, c3, c2, c1, c0 = (acb(c) for c in self.Rcoef); return (((c4 * r + c3) * r + c2) * r + c1) * r + c0

    def Z(self, z):
        a, E, L, Q = (acb(v) for v in (self.a, self.E, self.L, self.Q))
        return Q - (Q + a * a * (1 - E * E) + L * L) * z * z + a * a * (1 - E * E) * z ** 4

    def rh(self, lam, analytic=False):
        A, B, k = acb(self.A), acb(self.B), acb(self.kap)
        den = (B - A) + (A + B) * (k * lam).cosh()
        if analytic and den.contains(0): return NAN
        return acb(self.ru) + 2 * A * B / den

    def psi(self, chi, analytic=False):
        """psi(chi) = (pi/2) (1 - F(pi/2 - chi | m)/K): RF forms chosen so their arguments stay near the positive reals"""
        m = acb(self.m); K = acb(self.K); s, c = chi.sin(), chi.cos()
        if (chi.real.mid() < arb.pi() / 4):            # F(chi | -m/(1-m)) / sqrt(1-m) form
            x1, y1 = c * c, 1 + m / (1 - m) * s * s
            if analytic and (x1.real.lower() <= 0 or y1.real.lower() <= 0): return NAN
            Finc = s * acb.elliptic_rf(x1, y1, acb(1)) / (1 - m).sqrt()
            return arb.pi() / (2 * K) * Finc
        x1, y1 = s * s, 1 - m * c * c
        if analytic and (x1.real.lower() <= 0 or y1.real.lower() <= 0): return NAN
        return arb.pi() / 2 * (1 - c * acb.elliptic_rf(x1, y1, acb(1)) / K)

    def dpsi(self, chi, analytic=False):
        m = acb(self.m); w = 1 - m * chi.cos() ** 2
        if analytic and w.real.lower() <= 0: return NAN
        return arb.pi() / (2 * acb(self.K)) / w.sqrt(analytic=True)

    def mom(self, r, z):
        k = acb(4); a = acb(self.a); D = r * r - 2 * acb(self.M) * r + a * a
        return k * k * self.R(r) / D ** 2, self.Z(z) / (1 - z * z) ** 2


def Fval(orb, kind, r, z):
    x = (r - orb.M) / 4; PX2, PY2 = orb.mom(r, z); E, L = acb(orb.E), acb(orb.L)
    f = dict(beta=GEN.Hb, M=GEN.HM, a=GEN.Ha)[kind] if kind != "sabotage" else None
    sig = r * r + acb(orb.a) ** 2 * z * z
    if kind == "sabotage":                          # V23's sabotage: G1^{tt} = x y, so (1/2) G1^{ab} p p = (1/2) x y E^2
        return sig * x * z * E * E / 2
    return sig * f(x, z, PX2, PY2, E, L)


def v_n(orb, kind, n, r, analytic=False):
    """v_n(r) = (2/pi) int_0^{pi/2} F(r, z) cos(n psi) psi' dchi (even n); odd n: (1/2pi) int over [0, 2pi] via symmetry
    v_n = (2/pi) int_0^{pi/2} [F(r, z) - F(r, -z)]/2 ... handled by the caller as the full-period integral."""
    def f(chi, an):
        p = orb.psi(chi, an); dp = orb.dpsi(chi, an)
        if not (p.is_finite() and dp.is_finite()): return NAN
        val = Fval(orb, kind, r, orb.zm * chi.cos()) * (n * p).cos() * dp
        return val
    q = acb.integral(f, 0, arb.pi() / 4) + acb.integral(f, arb.pi() / 4, arb.pi() / 2)
    return 2 / arb.pi() * q


def v_n_full(orb, kind, n, r, analytic=False):
    """the full-period form (1/2pi) int_0^{2pi} F e^{-i n psi} psi' dchi, for ODD n (parity gate G4 and the sabotage):
    with psi(pi - chi) = pi - psi(chi) and z(pi - chi) = -z(chi), on [0, pi]: (1/pi) int_0^pi F cos(n psi) psi' dchi; and
    [0, pi] = [0, pi/2] + [pi/2, pi] with chi -> pi - chi: (1/pi) int_0^{pi/2} [F(z) + (-1)^n F(-z)] cos(n psi) psi'."""
    def f(chi, an):
        p = orb.psi(chi, an); dp = orb.dpsi(chi, an)
        if not (p.is_finite() and dp.is_finite()): return NAN
        z = orb.zm * chi.cos()
        return (Fval(orb, kind, r, z) + (-1) ** n * Fval(orb, kind, r, -z)) * (n * p).cos() * dp
    q = acb.integral(f, 0, arb.pi() / 4) + acb.integral(f, arb.pi() / 4, arb.pi() / 2)
    return q / arb.pi()


def L_n(orb, kind, n, Tfac=75, odd=False, verbose=False):
    vfun = v_n_full if odd else v_n
    vu = vfun(orb, kind, n, acb(orb.ru))
    Ups = acb(orb.Ups); T = arb(Tfac) / orb.kap; cnt = [0]
    def g(lam, an):
        r = orb.rh(lam, an)
        if not r.is_finite(): return NAN
        cnt[0] += 1
        return (vfun(orb, kind, n, r, an) - vu) * (n * Ups * lam).cos()
    I = acb.integral(g, 0, T, rel_tol=arb(2) ** -60, abs_tol=arb(2) ** -80)   # tolerances set the width only, never the rigour
    # tail: |v(r) - v(16)| <= S |r - 16| for r in [16, 16 + d], S <= max_{|r'-16| = rho} |v(r')| / (rho - d) (Cauchy)
    A, B, k = orb.A, orb.B, orb.kap
    d = 8 * A * B * (-(k * T)).exp() / (A + B)
    rho, Vmax = tail_vmax(orb, kind, n, vfun)
    S = arb(Vmax) / (rho - d)
    tail = S * 8 * A * B * (-(k * T)).exp() / ((A + B) * k)
    tot = 2 * (I + acb(arb(0, tail.upper())))
    return tot, dict(I=I, tail=tail, T=T, evals=cnt[0])


def tail_vmax(orb, kind, n, vfun, rho=arb("0.5"), g=10):
    """max |v_n| over the closed disc |r - 16| <= rho, from a g x g grid of small complex boxes covering the square
    [16 - rho, 16 + rho] + i[-rho, rho]; every box must give a FINITE enclosure (which also certifies v_n holomorphic on
    the disc: F is a composition of holomorphic operations with checked denominators and sqrt branch cuts). A non-finite
    box makes the bound infinite (never skipped)."""
    h = rho / g; vm = arb(0)
    for i in range(g):
        for j in range(g):
            c = acb(arb(RU) - rho + (2 * i + 1) * h, -rho + (2 * j + 1) * h)
            box = c + acb(arb(0, h * arb("1.0001")), arb(0, h * arb("1.0001")))
            v = vfun(orb, kind, n, box)
            if not v.is_finite(): return rho, arb("inf")
            vm = max(vm, abs(v).upper())
    return rho, vm


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--prec", type=int, default=128); ap.add_argument("--only", default="all")
    a = ap.parse_args(); ctx.prec = a.prec
    out_path = HERE / "CHECKS.json"; res = json.loads(out_path.read_text()) if out_path.exists() else {}
    t0 = time.time(); s = lambda v: str(v)
    lv = level(); orb = Orbit(lv)
    res["G1"] = dict(E=s(lv["E"]), L=s(lv["L"]), Q=s(lv["Q"]), krawczyk_inside=lv["krawczyk_inside"], radius=lv["radius"],
                     contains_v23=lv["contains_v23"], R16_contains_0=lv["R16"].contains(0), dR16_contains_0=lv["dR16"].contains(0),
                     rt=s(orb.rt), r4=s(orb.r4), kappa=s(orb.kap), Upsilon=s(orb.Ups), m=s(orb.m), sign=GEN.SIGN)
    res["G1"]["PASS"] = bool(lv["krawczyk_inside"] and lv["contains_v23"] and res["G1"]["R16_contains_0"] and res["G1"]["dR16_contains_0"] and lv["radius"] < 1e-25)
    print("G1", res["G1"]["PASS"], "E", lv["E"], "kappa", orb.kap, "Ups", orb.Ups, flush=True)
    # G2: orbit equation and the mass shell
    import random; random.seed(2026)
    g2o, g2s = True, True; worst = 0.0
    for j in range(20):
        lam = acb(arb(random.uniform(-3, 3)) / orb.kap); r = orb.rh(lam)
        A, B, k = acb(orb.A), acb(orb.B), acb(orb.kap)
        den = (B - A) + (A + B) * (k * lam).cosh(); drh = -2 * A * B * (A + B) * k * (k * lam).sinh() / den ** 2
        g2o &= (drh ** 2 - orb.R(r)).contains(0)
        z = acb(arb(random.uniform(-0.5, 0.5))); PX2, PY2 = orb.mom(r, z)
        h0 = GEN.H0((r - orb.M) / 4, z, PX2, PY2, acb(orb.E), acb(orb.L)); g2s &= (h0 + acb(1) / 2).contains(0)
        worst = max(worst, float(abs(h0 + acb(1) / 2).upper()))
    res["G2"] = dict(orbit_eq=bool(g2o), mass_shell=bool(g2s), worst_shell=worst, PASS=bool(g2o and g2s), sign=GEN.SIGN)
    print("G2", res["G2"], flush=True)
    # G5: psi against mpmath (both RF forms), and continuity at pi/4
    import mpmath as mp
    mp.mp.dps = 40; mf = mp.mpf(orb.m.mid().str(45, radius=False)); Kf = mp.ellipk(mf); g5 = True; wst = 0.0
    for c in [0.05, 0.3, 0.7, 0.785, 0.786, 1.0, 1.3, 1.5]:
        ref = mp.pi / 2 * (1 - mp.ellipf(mp.pi / 2 - c, mf) / Kf)
        got = orb.psi(acb(arb(c))); d = float(abs(mp.mpf(got.real.mid().str(45, radius=False)) - ref)); wst = max(wst, d); g5 &= d < 1e-25
    res["G5"] = dict(psi_vs_mpmath_worst=wst, PASS=bool(g5)); print("G5", res["G5"], flush=True)
    # G3: F against V23's float code (comparison only)
    try:
        sys.path.insert(0, "/Users/sumit/Github/TheBridge/falsification/V23_mn_melnikov_check/code")
        import numpy as np, v23
        G0, G1 = v23.pieces(5.0, 3.0, "beta"); lev = v23.Level(5, 3, 16, mp.mpf(1) / 2, (mp.mpf("0.94"), mp.mpf("13"), mp.mpf("56")))
        g3 = True; wr = 0.0
        for j in range(10):
            rr, zz = random.uniform(16.5, 45), random.uniform(-0.45, 0.45)
            fv, _ = v23.F_vals(lev, G0, G1, np.array([rr]), np.array([zz]))
            mine = Fval(orb, "beta", acb(arb(rr)), acb(arb(zz)))
            rel = abs(float(mine.real.mid()) - float(fv[0])) / max(1e-300, abs(float(fv[0]))); wr = max(wr, rel); g3 &= rel < 1e-12
        res["G3"] = dict(worst_rel=wr, PASS=bool(g3))
    except Exception as e:
        res["G3"] = dict(error=repr(e), PASS=False)
    print("G3", res["G3"], flush=True)
    out_path.write_text(json.dumps(res, indent=1, default=str))
    if a.only == "gates": return
    gates_ok = all(res[g]["PASS"] for g in ("G1", "G2", "G3", "G5"))
    jobs = []
    if a.only in ("all", "L2"): jobs += [("L2_beta", "beta", 2, False), ("L1_beta", "beta", 1, True)]
    if a.only in ("all", "controls"): jobs += [("L2_M", "M", 2, False), ("L2_a", "a", 2, False), ("L1_sabotage", "sabotage", 1, True)]
    if a.only == "L4": jobs += [("L4_beta", "beta", 4, False)]
    for name, kind, n, odd in jobs:
        t1 = time.time(); v, meta = L_n(orb, kind, n, odd=odd)
        res[name] = dict(value=s(v), mid=float(v.real.mid()), rad=float(v.real.rad()), excludes_0=not v.real.contains(0),
                         tail=s(meta["tail"]), evals=meta["evals"], seconds=round(time.time() - t1, 1), prec=a.prec, gates_ok=gates_ok)
        print(name, res[name], flush=True); out_path.write_text(json.dumps(res, indent=1, default=str))
    print("total %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
