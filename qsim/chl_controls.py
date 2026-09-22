"""
Known-answer controls for the CHL sub-45-degree corner-function CHECK.

Pre-registered in PREREG_cuspis_sub45_check.md. This file is the INSTRUMENT
VALIDATION only -- it holds no solver. That separation is deliberate: a control
living in the same file as the thing it checks drifts with it, and the point of
these four is to be the part that does not move.

WHY THIS FILE EXISTS AT ALL, stated so it is not mistaken for boilerplate.
The region under audit (theta < 45 deg) has NO published value. Nothing there
can be checked directly. So the entire warrant for any sub-45 number is that the
same solver, unmodified, reproduces the values that ARE published. If control 1
fails, nothing below 45 deg is reportable -- and the registered response is to
say the instrument failed, not to widen the tolerance.

THE RULE THIS FILE IS BUILT AROUND (learned 2026-09-22, the hard way):
A CONTROL THAT HAS NEVER BEEN SHOWN TO FAIL IS DECORATION.
The contamination detector withdrawn that morning reported "zero sub-45 tables"
about a tree holding 145 of them. It was never mutation-tested, so "zero" and
"blind" were the same output. Therefore EVERY control here carries a poison():
a deliberate corruption that it MUST reject. run_controls() refuses to report a
pass until each control has first been made to fail on its own poison. A green
line printed by this file means "this check rejected a wrong answer thirty
milliseconds ago", not "this check did not complain".

Conventions are fixed in the pre-registration and re-stated in CONVENTIONS below
rather than referenced, because a convention that lives only in a prose file
tends to be reconciled after the fact.
"""

import math

PI = math.pi

# --- conventions, frozen before any number exists ---------------------------
CONVENTIONS = {
    "normalisation": "S contains -a(theta)*log(R/delta); sign such that a > 0",
    "angle":         "theta is the OPENING angle: theta->pi smooth, theta->0 sharp",
    "renyi_index":   "n = 1 (von Neumann) ONLY; n=2 is excluded as contaminated",
    "C_T":           "real free scalar C_T = 3/(32 pi^2), the convention in which "
                     "the BWK16 prefactor is exactly 1/32",
}

# C_T for a single real free massless scalar in d = 3.
C_T_SCALAR = 3.0 / (32.0 * PI ** 2)


def bwk16_bound(theta, c_t=C_T_SCALAR):
    """Lower bound a(theta) >= (pi^2 C_T/3) log[1/sin(theta/2)].

    From SSA + Lorentz invariance [CHL09] with sigma = pi^2 C_T/24 [FLP16].
    For a real scalar the prefactor is exactly 1/32 -- no fitted parameter and
    no threshold, which is why this is a live constraint and not a formality.
    Below 45 degrees the bound is STRONG, so it does real work in the very
    region where nothing else can check the answer.
    """
    if not 0.0 < theta < 2.0 * PI:
        raise ValueError(f"theta out of range: {theta}")
    return (PI ** 2 * c_t / 3.0) * math.log(1.0 / math.sin(theta / 2.0))


def smooth_limit_sigma(c_t=C_T_SCALAR):
    """sigma in a(theta) -> sigma (pi-theta)^2 as theta -> pi. [FLP16]"""
    return PI ** 2 * c_t / 24.0


def smooth_limit(theta, c_t=C_T_SCALAR):
    return smooth_limit_sigma(c_t) * (PI - theta) ** 2


def bound_reduces_to_smooth_limit(theta=math.radians(179.9), c_t=C_T_SCALAR):
    """Self-consistency of the two imported constants against each other.

    As theta -> pi the bound must reduce to sigma(pi-theta)^2. If it does not,
    the two constants are in different normalisations and every comparison
    downstream is bookkeeping. Returns the ratio, which must be 1.
    """
    return bwk16_bound(theta, c_t) / smooth_limit(theta, c_t)


# =============================================================================
# The control framework. Every control must reject before it may accept.
# =============================================================================

class ControlFailed(Exception):
    """Raised when a control rejects a value. Never caught to widen a tolerance."""


class Control:
    """A known-answer check, plus the corruption it must be able to reject.

    `check(value)` raises ControlFailed on a bad value and returns a detail
    string on a good one. `poison(value)` returns a value that check() MUST
    reject -- the corruption is chosen to be SMALL and PLAUSIBLE, not absurd,
    because a control that only rejects nonsense is barely a control. A sign
    flip or a factor of ten proves nothing; the poisons here sit just outside
    the tolerance, which is the regime a real bug lives in.
    """

    def __init__(self, name, why, check, poison):
        self.name, self.why, self.check, self.poison = name, why, check, poison

    def validate(self, value):
        """Run the control AND prove it can fire. Returns (detail, poison_detail).

        Order matters and is the whole point: the poison is rejected FIRST. If
        the control accepts its own poison it is reported as broken, and the
        real value is not consulted at all -- an instrument that cannot say no
        has no opinion worth hearing when it says yes.
        """
        bad = self.poison(value)
        try:
            self.check(bad)
        except ControlFailed as exc:
            poison_detail = f"rejected poison {bad!r}: {exc}"
        else:
            raise AssertionError(
                f"CONTROL IS DECORATION: '{self.name}' ACCEPTED its own poison "
                f"{bad!r}. It cannot distinguish a right answer from a wrong one, "
                f"so its verdict on the real value is worthless. Fix the control "
                f"before trusting anything it has ever passed."
            )
        return self.check(value), poison_detail


def relative(a, b):
    """Relative difference, symmetric-safe against a zero reference."""
    denom = max(abs(a), abs(b))
    return abs(a - b) / denom if denom else 0.0


def make_bound_control(theta, c_t=C_T_SCALAR):
    """Control 3: a(theta) must clear the BWK16 bound at every angle computed."""
    bound = bwk16_bound(theta, c_t)

    def check(value):
        if value < bound:
            raise ControlFailed(
                f"a({math.degrees(theta):.3f} deg) = {value:.8g} is BELOW the "
                f"BWK16 bound {bound:.8g} (ratio {value/bound:.6f})")
        return f"a = {value:.8g} >= bound {bound:.8g} (ratio {value/bound:.6f})"

    # Poison: nudge to just under the bound. Not a sign flip -- a violation of
    # 0.1% is exactly what a subtly wrong normalisation produces.
    return Control(
        name=f"BWK16 bound at {math.degrees(theta):.3f} deg",
        why="strong below 45 deg, where nothing published can check the answer",
        check=check,
        poison=lambda v: bound * 0.999,
    )


def make_known_value_control(theta, published, rtol, source):
    """Control 1: reproduce a published value. The warrant for everything else."""

    def check(value):
        rel = relative(value, published)
        if rel > rtol:
            raise ControlFailed(
                f"a({math.degrees(theta):.3f} deg) = {value:.8g} vs published "
                f"{published:.8g} [{source}]: relative difference {rel:.3e} "
                f"exceeds {rtol:.1e}")
        return (f"a = {value:.8g} vs published {published:.8g} [{source}], "
                f"rel {rel:.3e} <= {rtol:.1e}")

    # Poison: exceed the tolerance by 10%. Deliberately just outside, so the
    # control is shown to discriminate at its own boundary rather than far away.
    return Control(
        name=f"known value at {math.degrees(theta):.3f} deg",
        why="the whole basis for trusting output where no published value exists",
        check=check,
        poison=lambda v: published * (1.0 + 1.1 * rtol),
    )
