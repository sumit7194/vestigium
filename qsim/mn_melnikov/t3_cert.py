"""t3_cert.py -- stage 2 of PREREG.md, Amendment S2-A1 (REGISTERED cabccc9): the two-contour Cauchy bound T3 >= sum_{m>=3} m^2 |L_{2m}|
at each (sigma, tau) point, with the tube-holomorphy certificate, the certified b, the C box rule, the tail bound, the
must-fail controls and the n = 2 / n = 4 consistency gates, and the pass rule (one counted point suffices).
Usage: t3_cert.py --set full|controls|debug [--out T3.json]   (full = the counted launcher: known-value control, must-fail points, 16 grid points)
L2 and L4 enclosures are read from CHECKS.json (stage 1 and mel_cert.py --only L4). Results go to --out (not CHECKS.json, so a
concurrent mel_cert run never races this file). Written by Claude Opus 5.5 (session "Quantum")."""
import argparse, heapq, json, time
from pathlib import Path
from flint import acb, arb, ctx
import mel_cert as MC

HERE = Path(__file__).resolve().parent
LAM, RHO, DEPTH = arb(1), arb("0.5"), 40
SETS = dict(counted=[(s, t) for s in ("0.04", "0.07", "0.10", "0.13") for t in ("0.3", "0.6", "0.9", "1.2")],
            controls=[("0.17", "0.6"), ("0.07", "1.35")], debug=[("0.02", "0.1")])


def iv(lo, hi):                                      # the real ball covering [lo, hi] (lo, hi arb, exact endpoints)
    return (lo + hi) / 2 + arb(0, ((hi - lo) / 2).upper() * (1 + 2.0 ** -60))


def cb(r0, r1, i0, i1): return acb(iv(r0, r1), iv(i0, i1))


class Point:
    def __init__(self, orb, sig, tau):
        self.o, self.sig, self.tau = orb, arb(sig), arb(tau); self.zm = acb(orb.zm); self.r16 = acb(orb.ru)

    def fin(self, *vals): return all(v.is_finite() for v in vals)

    def pieces(self, lam, chi):                      # (Delta F, psi') at boxes; NaN-propagating
        o = self.o; r = o.rh(lam, analytic=True); dp = o.dpsi(chi, analytic=True)
        if not (r.is_finite() and dp.is_finite()): return MC.NAN, MC.NAN
        z = self.zm * chi.cos()
        return MC.Fval(o, "beta", r, z) - MC.Fval(o, "beta", self.r16, z), dp

    # ---------------- tube certificate, core region: 4-D boxes, adaptive bisection, finite or INVALID-POINT
    def tube_core(self):
        k = self.o.kap; nb = 0; maxd = 0
        stack = [(-LAM + 2 * LAM * i / 8, -LAM + 2 * LAM * (i + 1) / 8, arb(0), self.sig,
                  2 * arb.pi() * j / 16, 2 * arb.pi() * (j + 1) / 16, -self.tau, arb(0), 0) for i in range(8) for j in range(16)]
        while stack:
            u0, u1, s0, s1, c0, c1, t0, t1, d = stack.pop(); nb += 1; maxd = max(maxd, d)
            F, dp = self.pieces(cb(u0, u1, s0, s1), cb(c0, c1, t0, t1))
            if self.fin(F, dp): continue
            if d >= DEPTH: return dict(ok=False, boxes=nb, max_depth=maxd, fail_box=[float(x) for x in (u0, u1, s0, s1, c0, c1, t0, t1)])
            w = [float(k * (u1 - u0)), float(k * (s1 - s0)), float(c1 - c0), float(t1 - t0)]; a = w.index(max(w))
            lo, hi = [(u0, u1), (s0, s1), (c0, c1), (t0, t1)][a]; m = (lo + hi) / 2
            for half in ((lo, m), (m, hi)):
                b = [u0, u1, s0, s1, c0, c1, t0, t1]; b[2 * a], b[2 * a + 1] = half; stack.append((*b, d + 1))
        return dict(ok=True, boxes=nb, max_depth=maxd)

    # ---------------- outer region: d(Lambda) < rho, and the disc x chi-tube boxes (finite; gives Fmax)
    def tube_outer(self):
        o = self.o; A, B, k = o.A, o.B, o.kap
        dL = 2 * A * B / ((A + B) * (k * LAM).sinh() - abs(B - A))
        D0 = (A + B) * (1 - (-2 * k * LAM).exp()) / 2 - abs(B - A) * (-(k * LAM)).exp()
        if not (dL > 0 and dL < RHO and D0 > 0): return dict(ok=False, why="d(Lambda) or D0", dL=str(dL), D0=str(D0))
        g = 10; h = RHO / g; fmax = arb(0); nb = 0; maxd = 0
        for i in range(g):
            for j in range(g):
                r = cb(arb(o.ru) - RHO + 2 * i * h, arb(o.ru) - RHO + 2 * (i + 1) * h, -RHO + 2 * j * h, -RHO + 2 * (j + 1) * h)
                stack = [(2 * arb.pi() * p / 32, 2 * arb.pi() * (p + 1) / 32, -self.tau + self.tau * q / 4, -self.tau + self.tau * (q + 1) / 4, 0)
                         for p in range(32) for q in range(4)]
                while stack:
                    c0, c1, t0, t1, d = stack.pop(); nb += 1; maxd = max(maxd, d)
                    chi = cb(c0, c1, t0, t1); dp = o.dpsi(chi, analytic=True)
                    v = MC.Fval(o, "beta", r, self.zm * chi.cos()) if dp.is_finite() else MC.NAN
                    if v.is_finite(): fmax = max(fmax, abs(v).upper()); continue
                    if d >= DEPTH: return dict(ok=False, why="disc box non-finite", boxes=nb, fail_box=[float(x) for x in (c0, c1, t0, t1)], r_box=str(r))
                    if float(c1 - c0) >= float(t1 - t0):
                        m = (c0 + c1) / 2; stack += [(c0, m, t0, t1, d + 1), (m, c1, t0, t1, d + 1)]
                    else:
                        m = (t0 + t1) / 2; stack += [(c0, c1, t0, m, d + 1), (c0, c1, m, t1, d + 1)]
        return dict(ok=True, dL=dL, D0=D0, Fmax=fmax, boxes=nb, max_depth=maxd)

    # ---------------- b: -Im psi(chi - i tau) = int_0^tau Re psi'(chi - i t) dt >= sum_j h_j min Re psi'(box_j)
    def b_and_psimax(self):
        o = self.o; n = 64; h = self.tau / n; b = arb(0); pm = arb(0)
        for j in range(n):
            mn = None
            for i in range(n):
                dp = o.dpsi(cb(2 * arb.pi() * i / n, 2 * arb.pi() * (i + 1) / n, -(j + 1) * h, -j * h), analytic=True)
                if not dp.is_finite(): return None, None
                lo = dp.real.lower(); mn = lo if mn is None or lo < mn else mn
            b += h * mn
        for i in range(n):                                   # max |psi'| on the contour Im chi = -tau
            dp = o.dpsi(acb(iv(2 * arb.pi() * i / n, 2 * arb.pi() * (i + 1) / n), -self.tau), analytic=True)
            if not dp.is_finite(): return None, None
            pm = max(pm, abs(dp).upper())
        return arb(b.lower()), pm

    # ---------------- C inner: boxes on the shifted contour, refined by the registered rule
    def g(self, lam, chi):                           # G = Delta F(r_h(lam), z(chi)) psi'(chi), plain acb, sqrt analytic always
        o = self.o; r = o.rh(lam, analytic=True); dp = o.dpsi(chi, analytic=True)
        if not (r.is_finite() and dp.is_finite()): return MC.NAN
        z = self.zm * chi.cos()
        return (MC.Fval(o, "beta", r, z) - MC.Fval(o, "beta", self.r16, z)) * dp

    # ---------------- real-analyticity gate (S2-A2 condition 3): G(conj w) overlaps conj(G(w)) at 20 tube points (both
    # factors' arguments), and Im G contains 0 at 5 real points. Catches a complex constant hiding in G.
    def ra_gate(self):
        import random; rnd = random.Random(20261120); ok = True; worst = 0.0
        for _ in range(20):
            lam = acb(arb(repr(rnd.uniform(0, 2))), self.sig * arb(repr(rnd.uniform(0, 1))))
            chi = acb(arb(repr(rnd.uniform(0, 6.28))), -self.tau * arb(repr(rnd.uniform(0, 1))))
            g1, g2 = self.g(lam, chi), self.g(lam.conjugate(), chi.conjugate())     # the gate itself uses conj; the integrand never does
            if not (g1.is_finite() and g2.is_finite()): return dict(ok=False, why="non-finite in tube")
            ok &= g2.overlaps(g1.conjugate()); worst = max(worst, float(abs(g2 - g1.conjugate()).upper()))
        im_ok = True
        for _ in range(5):
            gr = self.g(acb(arb(repr(rnd.uniform(0, 2)))), acb(arb(repr(rnd.uniform(0, 6.28)))))
            im_ok &= gr.imag.contains(0)
        return dict(ok=bool(ok and im_ok), conj_overlap=bool(ok), real_im_contains_0=bool(im_ok), worst_abs_diff=worst)

    # ---------------- C by the L2 route (S2-A2): C <= sqrt(I2h) sqrt(2/alpha), alpha = kappa, with
    # I2h = int_0^inf int_0^pi |G(lam + i sigma, chi - i tau)|^2 cosh(alpha lam) dchi dlam, and |G|^2 = G(lam + i sigma, chi - i tau)
    # G(lam - i sigma, chi + i tau) (G is real-analytic; valid on counted points, whose tube certificate excludes the cut), which
    # is holomorphic, so nested acb.integral encloses it rigorously on [0, LAM_I]; the tail beyond LAM_I by the Cauchy-disc bound.
    def C_L2(self, Fmax, pm, LAM_I=arb(2)):
        o = self.o; A, B, k = o.A, o.B, o.kap; al = acb(k); sg, ta = self.sig, self.tau; cnt = [0]
        def P(lam, chi):
            cnt[0] += 1
            return self.g(lam + acb(0, sg), chi - acb(0, ta)) * self.g(lam - acb(0, sg), chi + acb(0, ta)) * (al * lam).cosh()
        t0 = time.time()
        I = nested(P, LAM_I)
        D0 = (A + B) * (1 - (-2 * k * LAM_I).exp()) / 2 - abs(B - A) * (-(k * LAM_I)).exp()
        dI = 2 * A * B / ((A + B) * (k * LAM_I).sinh() - abs(B - A))
        if not (I.is_finite() and D0 > 0 and dI < RHO): return dict(ok=False, why="L2 integral or tail constants", I=str(I))
        tail = arb.pi() * (pm * Fmax / (RHO - dI)) ** 2 * (2 * A * B / D0) ** 2 * (-(k * LAM_I)).exp() / k
        I2h = arb(I.real.upper()) + arb(tail.upper())
        C = arb(((I2h * 2 / k).sqrt()).upper())
        return dict(ok=True, C=C, I2_core=str(I), I2_tail=str(tail), evals=cnt[0], seconds=round(time.time() - t0, 1), LAM_I=str(LAM_I))


def nested(P, LAM_I):
    """the nested acb.integral used for I2h (and, identically, for the known-value control). The integrand P branch-checks on
    every call whatever analytic flag acb.integral passes (S2-A2 condition 2): r_h and psi' with analytic=True, every sqrt in
    mel_gen.py is sqrt(analytic=True), and divisions by balls containing 0 are non-finite."""
    def inner(lam, an):
        return acb.integral(lambda chi, a2: P(lam, chi), 0, arb.pi(), rel_tol=arb(2) ** -8, abs_tol=arb(2) ** -16)
    return acb.integral(inner, 0, LAM_I, rel_tol=arb(2) ** -8, abs_tol=arb(2) ** -16)


def known_value_control():
    """S2-A2 condition 4: P = 1/((lam - 1 - 0.02i)(chi - 1.5 + 0.02i)) on [0, 2] x [0, pi], poles 0.02 off both segments.
    Exact: [Log(1 - 0.02i) - Log(-1 - 0.02i)] [Log(pi - 1.5 + 0.02i) - Log(-1.5 + 0.02i)] (neither segment's image crosses the
    principal cut: Im is the constant -0.02, resp. +0.02). The enclosure must contain the exact value."""
    a = acb(1, arb("0.02")); c = acb(arb("1.5"), arb("-0.02"))
    def P(lam, chi):
        d1, d2 = lam - acb(1, arb("0.02")) * 1, chi - c
        if d1.contains(0) or d2.contains(0): return MC.NAN
        return 1 / (d1 * d2)
    t0 = time.time(); I = nested(P, arb(2))
    exact = ((2 - a).log() - (-a).log()) * ((arb.pi() - c).log() - (-c).log())
    return dict(ok=bool(I.is_finite() and I.overlaps(exact) and I.real.contains(exact.real) and I.imag.contains(exact.imag)),
                value=str(I), exact=str(exact), seconds=round(time.time() - t0, 1))


def T3_of(C, q):
    return C * (q * (1 + q) / (1 - q) ** 3 - q - 4 * q * q)


def run_point(orb, sig, tau, _unused, L2, L4):
    t0 = time.time(); P = Point(orb, sig, tau); out = dict(sigma=sig, tau=tau)
    tc = P.tube_core(); out["tube_core"] = tc
    if not tc["ok"]: out["status"] = "INVALID-POINT"; out["seconds"] = round(time.time() - t0, 1); return out
    to = P.tube_outer(); out["tube_outer"] = {k: (str(v) if isinstance(v, arb) else v) for k, v in to.items()}
    if not to["ok"]: out["status"] = "INVALID-POINT"; out["seconds"] = round(time.time() - t0, 1); return out
    b, pm = P.b_and_psimax()
    if b is None or not b > 0: out["status"] = "INVALID-POINT"; out["why"] = "b"; out["seconds"] = round(time.time() - t0, 1); return out
    ra = P.ra_gate(); out["ra_gate"] = ra
    if not ra["ok"]: out["status"] = "RA-GATE-FAIL"; out["seconds"] = round(time.time() - t0, 1); return out
    cl = P.C_L2(to["Fmax"], pm); out["C_L2"] = {k: (str(v) if isinstance(v, arb) else v) for k, v in cl.items()}
    if not cl["ok"]: out["status"] = "INVALID-POINT"; out["seconds"] = round(time.time() - t0, 1); return out
    C = cl["C"]
    e1 = (-(orb.Ups * P.sig + b)).exp(); q = arb((e1 * e1).upper())
    T3 = arb(T3_of(C, q).upper())
    B2, B4 = C * q, C * q * q                                  # C e^{-2(Ups sigma + b)}, C e^{-4(...)}
    out.update(b=str(b), psimax=str(pm), C=str(C), q=str(q), T3=str(T3), B2=str(B2), B4=str(B4), status="COUNTED")
    out["gate_n2"] = bool(B2 >= abs(L2).upper()) if L2 is not None else None
    out["gate_n4"] = bool(B4 >= abs(L4).upper()) if L4 is not None else None
    if L2 is not None and L4 is not None:
        marg = abs(L2).lower() - 4 * abs(L4).upper() - T3
        out["margin_lower"] = str(arb(marg.lower())); out["closes"] = bool(marg.lower() > 0)
    out["seconds"] = round(time.time() - t0, 1)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--set", default="debug")
    ap.add_argument("--out", default="T3.json"); a = ap.parse_args(); ctx.prec = 128
    ck = json.loads((HERE / "CHECKS.json").read_text())
    L2 = arb(ck["L2_beta"]["value"]) if "L2_beta" in ck else None
    L4 = arb(ck["L4_beta"]["value"]) if "L4_beta" in ck else None
    orb = MC.Orbit(MC.level()); res = dict(set=a.set, L2=str(L2), L4=str(L4), points=[])
    outp = HERE / a.out
    if a.set == "full":                              # the counted launcher: known-value control, must-fail points, then the grid
        res["known_value_control"] = kv = known_value_control(); print("KNOWN-VALUE CONTROL", kv, flush=True)
        outp.write_text(json.dumps(res, indent=1, default=str))
        pts = [(s, t, "control") for s, t in SETS["controls"]] + [(s, t, "counted") for s, t in SETS["counted"]]
    else:
        pts = [(s, t, a.set) for s, t in SETS[a.set]]
    for s, t, role in pts:
        r = run_point(orb, s, t, 0, L2, L4); r["role"] = role; res["points"].append(r)
        print({k: v for k, v in r.items() if k not in ("tube_core", "tube_outer", "C_L2")}, flush=True)
        print("   tube_core", r.get("tube_core"), "\n   tube_outer", r.get("tube_outer"), "\n   C_L2", r.get("C_L2"), flush=True)
        outp.write_text(json.dumps(res, indent=1, default=str))
    ctl = [p for p in res["points"] if p["role"] == "control"]
    cnt = [p for p in res["points"] if p["role"] == "counted" and p["status"] == "COUNTED"]
    if ctl: res["controls_pass"] = all(p["status"] == "INVALID-POINT" for p in ctl)
    if a.set == "full":
        ra_fail = any(p["status"] == "RA-GATE-FAIL" for p in res["points"] if p["role"] == "counted")
        gates = all(p["gate_n2"] and p["gate_n4"] for p in cnt) if cnt else None
        res["gates_n2_n4"] = gates
        bad = (not res["known_value_control"]["ok"]) or (not res["controls_pass"]) or ra_fail or gates is False or L4 is None
        res["verdict"] = ("INVALID" if bad else "CERTIFIED-NONDEGENERATE" if any(p.get("closes") for p in cnt) else "OPEN")
        res["counted_points_closing"] = [(p["sigma"], p["tau"]) for p in cnt if p.get("closes")]
    outp.write_text(json.dumps(res, indent=1, default=str)); print("SUMMARY", {k: v for k, v in res.items() if k != "points"})


if __name__ == "__main__":
    main()
