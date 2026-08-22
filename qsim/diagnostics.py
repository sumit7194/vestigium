#!/usr/bin/env python3
"""Diagnostics that cannot return a verdict without their null.

THE GAP THIS CLOSES. bridge and I converged on: a check is durable when it
rides on an action already being taken for another reason. Sweeps ride on
commits. Setup-correspondence and edit-time asserts can ride on the edit.
bridge predicted that NULL DISTRIBUTIONS cannot be rescued, because no action
naturally carries them.

There is one: the diagnostic's own invocation. If computing the null is inside
the function that returns the verdict, you cannot get the verdict without it.

WHY IT MATTERS HERE. Both of us used a residual-sign-change test all day as
evidence. Neither computed its null until bridge did, late, and withdrew a
committed finding over it. At 8 points, only ZERO sign changes reaches p<0.05 --
so the test could essentially never fire, and we had both been reading it as
support. That is not a weak diagnostic, it is an inert one, and the inertness
was invisible precisely because nobody ran the null.
"""
from math import comb


class Inconclusive(Exception):
    """Raised when a diagnostic has no power to say what is being asked of it."""


def sign_change_test(residuals, alpha=0.05):
    """Are residuals structured (few sign changes) or scattered (many)?

    Returns (verdict, p, detail). RAISES Inconclusive when NO outcome at this
    sample size could reach alpha -- because a test that cannot fire should not
    return a verdict at all, and returning 'scatter' from an inert test is how
    both of us mistook noise for evidence.
    """
    n = len(residuals) - 1
    if n < 1:
        raise Inconclusive("fewer than two residuals")
    signs = ["+" if r > 0 else "-" for r in residuals]
    k = sum(1 for i in range(1, len(signs)) if signs[i] != signs[i-1])

    def p_le(j):
        return sum(comb(n, i) for i in range(j+1))/2**n

    # THE POWER CHECK, computed before any verdict is formed.
    best = p_le(0)
    if best > alpha:
        raise Inconclusive(
            f"n={n}: the most extreme outcome (0 sign changes) gives p={best:.3f}, "
            f"which cannot reach {alpha}. This test has NO POWER here -- it is "
            f"inert, not weak, and no verdict is available at any k.")

    p_structured = p_le(k)
    verdict = "structured" if p_structured < alpha else "not distinguishable from scatter"
    return verdict, p_structured, f"{k} sign changes in {n} transitions ({''.join(signs)})"


if __name__ == "__main__":
    import json, os
    d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "cost_probe.json")))
    print("  MY OWN 8-POINT RESIDUALS, the ones I called 'scatter, not an arc':")
    res = [-5.3, 1.4, 1.6, 1.0, -0.6, -1.9, 10.7, -7.0]
    try:
        print("   ", sign_change_test(res))
    except Inconclusive as e:
        print(f"    Inconclusive: {e}")
    print("\n  BRIDGE'S 6-POINT M2 SERIES, the withdrawn 'smooth arcs' finding:")
    try:
        print("   ", sign_change_test([-26, -20, -17, -8, 7, 30]))
    except Inconclusive as e:
        print(f"    Inconclusive: {e}")
    print("\n  A SERIES LARGE ENOUGH TO HAVE POWER (n=20), perfectly monotone:")
    try:
        v, p, det = sign_change_test(list(range(-10, 11)))
        print(f"    {v}  p={p:.5f}  ({det})")
    except Inconclusive as e:
        print(f"    Inconclusive: {e}")
