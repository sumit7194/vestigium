"""Amendment C1-R (PREREG_cuspis_sub45_check.md, 9f142e6 + f8c94b3): the replacement reference for control 1.

Builds the a(pi/2) reference interval from HHCWM16 Table 3 (boson, alpha = 1), transcribed by hand from the paper.
Interval arithmetic (mpmath iv). Each tabulated coefficient carries +-1/2 unit in its last printed digit.
It does NOT compare against this repo's solver value: that comparison waits for the bridge's transcription check.

  a(theta) = sum_{p>=0} sigma^(p) (theta - pi)^(2p+2)        [HHCWM16 eqs. (22)-(23)]
  tail_{p>=8} <= T(r) = (2 r / pi^17) eps^18 / [theta (2 pi - theta)],   r = sup_{p>=8} sigma^(p) pi^(2p+3)/2
"""
import json, os
from mpmath import iv, mp, mpf

iv.dps = 40
mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))

PI = iv.pi
# transcribed: (mantissa string, decimal exponent of the column scale)
TABLE = [("5.34655497", -5), ("5.40160621", -6), ("5.45758486", -7),
         ("5.51156763", -8), ("5.57181927", -9), ("5.63580458", -10)]


def rounded(mant, e):
    """Interval [v - 1/2 ulp, v + 1/2 ulp] for a tabulated value whose last digit was rounded."""
    digits_after_point = len(mant.split(".")[1])
    half_ulp = mpf(5) * mpf(10) ** (-(digits_after_point + 1))
    v = mpf(mant)
    return iv.mpf([v - half_ulp, v + half_ulp]) * iv.mpf(10) ** e


sig = [iv.mpf(1) / 128, (20 + 3 * PI ** 2) / (9216 * PI ** 2)] + [rounded(m, e) for m, e in TABLE]
theta = PI / 2
eps = PI - theta                      # = pi/2
S8 = sum(s * eps ** (2 * p + 2) for p, s in enumerate(sig))


def T(r):
    return (2 * r / PI ** 17) * eps ** 18 / (theta * (2 * PI - theta))


r7 = sig[7] * PI ** 17 / 2
r7_up = iv.mpf(r7.b)                                  # top of sigma^(7)'s rounding interval
kappa = iv.mpf([mpf("0.07935"), mpf("0.07945")])      # CHL09 Table 1 c_-1^(0) = 7.94e-2, +-1/2 unit
T_r7, T_k = T(r7_up), T(kappa)


def ends(scale):
    S = S8 * scale
    return dict(
        conservative=[mp.nstr(mpf(S.a), 15), mp.nstr(mpf((S + T_r7 * scale).b), 15)],
        tight=[mp.nstr(mpf((S + T_k * scale).a), 15), mp.nstr(mpf((S + T_r7 * scale).b), 15)],
        S8=[mp.nstr(mpf(S.a), 15), mp.nstr(mpf(S.b), 15)],
        tail_r7=mp.nstr(mpf((T_r7 * scale).b), 6), tail_kappa=[mp.nstr(mpf((T_k * scale).a), 6), mp.nstr(mpf((T_k * scale).b), 6)])


out = dict(
    source="HHCWM16 Table 3 (boson, alpha=1), transcribed from arXiv:1606.03096 HTML; kappa from CHL09 Table 1",
    r_p=[mp.nstr(mpf((s * PI ** (2 * p + 3) / 2).mid), 8) for p, s in enumerate(sig)],
    r7_upper=mp.nstr(mpf(r7_up.b), 10),
    complex_boson=ends(iv.mpf(1)), real_scalar=ends(iv.mpf(1) / 2),
    labels=["L (S8) assumes non-negative omitted coefficients (observed, not proven at n=1)",
            "U uses r7: assumes r_p non-increasing for p >= 8 (observed p=1..7, not proven)",
            "control-1 verdict uses the CONSERVATIVE interval"])
json.dump(out, open(os.path.join(HERE, "chl_c1r_reference.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
