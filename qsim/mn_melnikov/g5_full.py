"""g5_full.py -- gate G5 exactly as registered (PREREG.md): "acb.elliptic_f(phi|m) agrees with mpmath ellipf at 10 points, real
and complex phi, as used in stage 2". mel_cert.py's G5 tested psi at 8 REAL points only; this closes the gap (post-run addendum,
labelled in RESULT.md). Two parts, both must pass:
  (a) literal: acb.elliptic_f(phi, m) vs mpmath.ellipf(phi, m) at 10 phi (5 real, 5 complex), m = the orbit's m;
  (b) as used: Orbit.psi(chi, analytic=True) (the Carlson RF forms) vs (pi/2)(1 - ellipf(pi/2 - chi | m)/K) at the same 10 chi.
Agreement: |Arb midpoint - mpmath| < 1e-25 (mpmath at 40 digits), and the Arb value finite. Writes CHECKS.json["G5_full"].
Written by Claude Opus 5.5 (session "Quantum")."""
import json
from pathlib import Path
import mpmath as mp
from flint import acb, arb, ctx
import mel_cert as MC

HERE = Path(__file__).resolve().parent
PTS = [0.05, 0.4, 0.785, 0.786, 1.4,                                  # real, both RF branches and the pi/4 seam
       (0.1, 0.05), (0.5, -0.1), (0.78, 0.12), (0.9, 0.15), (1.45, -0.15)]   # complex, |Im| <= 0.15


def cplx(p): return (complex(*p) if isinstance(p, tuple) else complex(p, 0))


def tomp(z): return mp.mpc(mp.mpf(z.real.mid().str(45, radius=False)), mp.mpf(z.imag.mid().str(45, radius=False)))


def main():
    ctx.prec = 128; mp.mp.dps = 40
    orb = MC.Orbit(MC.level()); m_a = acb(orb.m); mf = mp.mpf(orb.m.mid().str(45, radius=False)); Kf = mp.ellipk(mf)
    rows = []; ok = True
    for p in PTS:
        c = cplx(p); ca = acb(arb(repr(c.real)), arb(repr(c.imag))); cm = mp.mpc(repr(c.real), repr(c.imag))
        fa = acb.elliptic_f(ca, m_a); fr = mp.ellipf(cm, mf)
        da = float(abs(tomp(fa) - fr)) if fa.is_finite() else float("inf")
        ps = orb.psi(ca, analytic=True); pr = mp.pi / 2 * (1 - mp.ellipf(mp.pi / 2 - cm, mf) / Kf)
        dp = float(abs(tomp(ps) - pr)) if ps.is_finite() else float("inf")
        good = da < 1e-25 and dp < 1e-25; ok &= good
        rows.append(dict(chi=[c.real, c.imag], elliptic_f_diff=da, psi_diff=dp, ok=good))
        print(rows[-1], flush=True)
    res = dict(points=rows, worst_elliptic_f=max(r["elliptic_f_diff"] for r in rows), worst_psi=max(r["psi_diff"] for r in rows), PASS=bool(ok))
    ck = json.loads((HERE / "CHECKS.json").read_text()); ck["G5_full"] = res
    (HERE / "CHECKS.json").write_text(json.dumps(ck, indent=1)); print("G5_full PASS" if ok else "G5_full FAIL", res["worst_elliptic_f"], res["worst_psi"])


if __name__ == "__main__":
    main()
