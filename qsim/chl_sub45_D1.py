"""Diagnostic D1 (pre-registered 7e955c5): the C1-R published-data interval (HHCWM16 Table 3 + kappa / r7 tails) at the
Stage-2 angles, against my Stage-2 values. Real scalar. Uses chl_c1r_reference's transcribed coefficients unchanged."""
import json, math, os
from mpmath import iv, mp, mpf
import chl_c1r_reference as REF                         # transcription + rounding intervals, unchanged
HERE = os.path.dirname(os.path.abspath(__file__))
PI = iv.pi
mine = json.load(open(os.path.join(HERE, "chl_sub45_eval.json")))["per_angle"]
out = {}
for nm, v in mine.items():
    th = iv.mpf(mpf(v["theta_rad"]))
    eps = PI - th
    S8 = sum(s * eps ** (2 * p + 2) for p, s in enumerate(REF.sig)) / 2
    T = lambda r: (2 * r / PI ** 17) * eps ** 18 / (th * (2 * PI - th)) / 2
    lo_c, lo_t, hi = mpf(S8.a), mpf((S8 + T(REF.kappa)).a), mpf((S8 + T(REF.r7_up)).b)
    a = mpf(v["fine"])
    def pos(L, U):
        return 0.0 if L <= a <= U else float((a - L) / L if a < L else (a - U) / U)
    out[nm] = dict(mine=float(a), conservative=[float(lo_c), float(hi)], tight=[float(lo_t), float(hi)],
                   rel_outside_conservative=pos(lo_c, hi), rel_outside_tight=pos(lo_t, hi),
                   tail_share=float((mpf(T(REF.r7_up).b)) / a))
json.dump(out, open(os.path.join(HERE, "chl_sub45_D1.json"), "w"), indent=1)
for nm in sorted(out, key=lambda k: -mine[k]["theta_rad"]):
    o = out[nm]
    print(f"{nm:>12}: mine {o['mine']:.10f} | tight [{o['tight'][0]:.10f}, {o['tight'][1]:.10f}] | signed rel outside tight {o['rel_outside_tight']:+.2e} | conservative {o['rel_outside_conservative']:+.2e} | tail share {o['tail_share']:.2f}")
