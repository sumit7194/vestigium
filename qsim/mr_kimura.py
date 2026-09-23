"""
Kimura's criterion for the Riemann P-equation -- the third route of the
Morales-Ramis tool (PREREG_morales_ramis_tool.md, 59c4ae3). It decides whether
the solutions are LIOUVILLIAN (identity component solvable), so it must agree
with Kovacic on "cases 1-3" vs "case 4". It says nothing about abelian vs not.

Theorem (Kimura, Funkcialaj Ekvacioj 12 (1969/70) 269-281). The table below was
copied from TWO independent restatements that agree row for row, read from the
rendered PDF pages:
  Maciejewski, Przybylska, Yoshida, nlin/0701057, Appendix A, Theorem A.1;
  Acosta-Humanez, Lazaro, Morales-Ruiz, Pantazi, arXiv:1012.4796, Appendix B, Thm B.1.
(My own recollection of it had row 4 without its parity condition; it has one.)

The identity component of the Galois group of the Riemann P equation with
exponent differences lam, mu, nu is solvable iff
  (A) at least one of lam+mu+nu, -lam+mu+nu, lam-mu+nu, lam+mu-nu is an odd integer, or
  (B) lam or -lam, mu or -mu, nu or -nu belong (in arbitrary order) to one of the
      fifteen families below (l, s, q integers; some rows require l+s+q even).

The exponent differences are EXTRACTED FROM r (reduced form y'' = r y), not taken
from how r was built: at an order-2 pole with leading coefficient b the difference
is sqrt(1+4b); at an order-1 pole it is 1; at infinity likewise from r ~ b/z^2
(order 2) or order 3 (difference 1). Applicable only when there are exactly three
singular points, all regular.
"""
import itertools
import sympy as sp

R_ = sp.Rational
HALF = R_(1, 2)
# (entry1, entry2, entry3, parity_required); None = "arbitrary complex number"
TABLE = [
    (HALF, HALF, None, False),
    (HALF, R_(1, 3), R_(1, 3), False),
    (R_(2, 3), R_(1, 3), R_(1, 3), True),
    (HALF, R_(1, 3), R_(1, 4), True),
    (R_(2, 3), R_(1, 4), R_(1, 4), True),
    (HALF, R_(1, 3), R_(1, 5), False),
    (R_(2, 5), R_(1, 3), R_(1, 3), True),
    (R_(2, 3), R_(1, 5), R_(1, 5), True),
    (HALF, R_(2, 5), R_(1, 5), True),
    (R_(3, 5), R_(1, 3), R_(1, 5), True),
    (R_(2, 5), R_(2, 5), R_(2, 5), True),
    (R_(2, 3), R_(1, 3), R_(1, 5), True),
    (R_(4, 5), R_(1, 5), R_(1, 5), True),
    (HALF, R_(2, 5), R_(1, 3), True),
    (R_(3, 5), R_(2, 5), R_(1, 3), True),
]


def _is_integer(v):
    """Exact integer test. First version used nsimplify alone, which can match by
    NUMERICAL COINCIDENCE -- a false-positive route into "Liouvillian". Now: a
    candidate from 50-digit evaluation, accepted only if v - n is also PROVEN zero
    symbolically; numerically zero but unprovable -> Inconclusive, never True."""
    import mr_kovacic as K
    v = sp.sympify(v)
    val = complex(sp.N(v, 50))
    if abs(val.imag) > 1e-40:
        return False
    n = round(val.real)
    if abs(val.real - n) > 1e-40:
        return False
    d = v - n
    if sp.simplify(d) == 0 or sp.simplify(sp.sqrtdenest(d)) == 0:
        return True
    raise K.Inconclusive(f"{v} is numerically the integer {n} but not provably so")


def _odd_integer(v):
    v = sp.simplify(v)
    return _is_integer(v) and int(v) % 2 == 1


def exponent_differences(r, z):
    """-> list of exponent differences at the singular points, or None if the
    equation is not a Riemann P equation (three regular singular points)."""
    import mr_kovacic as K
    R = K.RationalR(r, z)
    if R.zero:
        return None
    diffs = []
    for c, m in R.poles.items():
        if m == 1:
            diffs.append(sp.Integer(1))
        elif m == 2:
            b = R.laurent_at(c, 1)[0]
            diffs.append(sp.sqrt(sp.nsimplify(1 + 4*b)))
        else:
            return None                      # irregular
    oi = R.ord_inf
    if oi == 2:
        diffs.append(sp.sqrt(sp.nsimplify(1 + 4*R.laurent_at_inf(1)[0])))
    elif oi == 3:
        diffs.append(sp.Integer(1))
    elif oi < 2:
        return None                          # irregular at infinity
    # oi >= 4: infinity is an ordinary point
    return diffs if len(diffs) == 3 else None


def kimura_liouvillian(lam, mu, nu):
    """-> (bool, which clause)."""
    for combo in (lam + mu + nu, -lam + mu + nu, lam - mu + nu, lam + mu - nu):
        if _odd_integer(combo):
            return True, f"(A): {sp.simplify(combo)} is an odd integer"
    for signs in itertools.product((1, -1), repeat=3):
        xs = [signs[0]*lam, signs[1]*mu, signs[2]*nu]
        for perm in itertools.permutations(range(3)):
            v = [xs[i] for i in perm]
            for k, (e1, e2, e3, parity) in enumerate(TABLE, start=1):
                ints = []
                ok = True
                for val, e in zip(v, (e1, e2, e3)):
                    if e is None:
                        continue
                    d = sp.simplify(val - e)
                    if not _is_integer(d):
                        ok = False; break
                    ints.append(int(d))
                if ok and (not parity or sum(ints) % 2 == 0):
                    return True, f"(B): family {k}"
    return False, "neither (A) nor any of the fifteen families"


def kimura_verdict(r, z):
    import mr_kovacic as K
    try:
        d = exponent_differences(r, z)
    except K.Inconclusive as e:
        return "INCONCLUSIVE", f"outside scope: {e}", None
    if d is None:
        return "NOT_APPLICABLE", "not a Riemann P equation (three regular singular points)", None
    liou, why = kimura_liouvillian(*d)
    return ("LIOUVILLIAN" if liou else "NOT_LIOUVILLIAN"), why, d
