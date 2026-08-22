#!/usr/bin/env python3
"""Which generalized hexagons H(p,q,r) on the triangular lattice have six
exactly-120-degree corners?

    H(p,q,r) = { (n1,n2) : |n1| <= p, |n2| <= q, |n1+n2| <= r }

WHY THIS FILE EXISTS. I sent tabula an "elongated hexagon" gate for isolating
their corner extraction, and asserted the admissible range from reasoning about
which constraints are active. I never drew the hulls. They verified it instead
of taking it and found my lower bound excluded the regular hexagon -- my own
reference shape. Their patch (max(p,q) <= r) was still not tight: it throws away
valid shapes BELOW max(p,q), which neither of us had tested because I had said
the interesting boundary was the other one.

So this is committed rather than run in a shell, which is the whole point: the
first version of this result was a heredoc number, and heredoc numbers are how
this repo already published a claim its code could not reproduce.

RESULT, exhaustive over p,q in 2..12 and r in 0..25 (3146 cases, 0 mismatches):

    H(p,q,r) has six exactly-120-deg corners  <=>  |p-q| < r < p+q

which is the TRIANGLE INEQUALITY on (p,q,r), both bounds strict. It had to be
symmetric in the three parameters -- the three constraint families are related
by the lattice's 3-fold symmetry -- and my `max(p,q)` broke that symmetry, which
was the tell I missed. Outside the range one constraint goes slack and the shape
drops to a 4-corner 120/60/120/60 rhombus: at r = p+q the |n1+n2| constraint,
at r = |p-q| the |n2| constraint. Same failure, two ends.

The regular hexagon is (R,R,R) -- an equilateral triangle, deep in the interior.
"""
import numpy as np
from scipy.spatial import ConvexHull


def corner_angles(p, q, r):
    """Interior angles at the true corners of H(p,q,r); collinear points dropped."""
    pts = [(a + 0.5*b, b*np.sqrt(3)/2)
           for a in range(-p, p+1) for b in range(-q, q+1) if abs(a + b) <= r]
    P = np.array(pts)
    if len(P) < 3 or np.linalg.matrix_rank(P - P[0]) < 2:
        return None                                   # degenerate: a segment or point
    V = P[ConvexHull(P).vertices]
    out, n = [], len(V)
    for i in range(n):
        a, b, c = V[i-1], V[i], V[(i+1) % n]
        v1, v2 = a - b, c - b
        t = np.degrees(np.arccos(np.clip(
            v1 @ v2 / np.linalg.norm(v1) / np.linalg.norm(v2), -1, 1)))
        if abs(t - 180) > 1e-6:                       # a collinear point is not a corner
            out.append(round(float(t), 1))
    return out


def is_hex120(p, q, r):
    a = corner_angles(p, q, r)
    return a is not None and a == [120.0]*6


def triangle_rule(p, q, r):
    return abs(p - q) < r < p + q


if __name__ == "__main__":
    RULES = {
        "mine, as sent to tabula": lambda p, q, r: max(p, q) < r < p + q,
        "tabula's patch":          lambda p, q, r: max(p, q) <= r < p + q,
        "triangle inequality":     triangle_rule,
    }
    cases = [(p, q, r) for p in range(2, 13) for q in range(2, 13) for r in range(26)]
    print(f"exhaustive scan: {len(cases)} cases, p,q in 2..12, r in 0..25\n")
    for name, rule in RULES.items():
        bad = [c for c in cases if is_hex120(*c) != rule(*c)]
        print(f"  {name:24s} mismatches: {len(bad):4d}"
              + (f"   e.g. {bad[:3]}" if bad else "   <-- exact"))

    print("\nthe two boundaries, p=5 q=7  ->  |p-q|=2, p+q=12:")
    for r in (1, 2, 3, 11, 12, 13):
        a = corner_angles(5, 7, r)
        tag = "six 120s" if a == [120.0]*6 else f"{len(a)} corners {sorted(set(a))}"
        edge = "  <-- |p-q|" if r == 2 else ("  <-- p+q" if r == 12 else "")
        print(f"   H(5,7,{r:2d}): {tag}{edge}")

    print("\nshapes MY rule wrongly excluded (all six exact 120s):")
    for c in [(6, 6, 6), (6, 6, 3), (5, 7, 3)]:
        print(f"   H{c}: six 120s = {is_hex120(*c)}")

    assert all(is_hex120(*c) == triangle_rule(*c) for c in cases)
    print("\nOK  |p-q| < r < p+q  is exact over the scanned range.")
