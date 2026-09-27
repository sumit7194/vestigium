"""
Interval-arithmetic hub: CERTIFIED analytic continuation and monodromy for y'' = r(z) y
(PREREG_mn_axis_certified_monodromy.md, ed09512 + 248b3bd). Reusable by other fleet items.

Everything is rigorous ball arithmetic (Arb via python-flint 0.9.0):
  - r is given as a SymPy expression in z built from +, *, integer powers, exp and rational numbers
    (non-integer powers are REFUSED: a principal-branch sqrt would silently jump across its cut);
  - Taylor coefficients of r at a point come from truncated power-series ball arithmetic;
  - |r| on a disk is bounded by ONE ball evaluation of r over the enclosing box; a non-finite ball
    means the disk may contain a singularity and the step is halved -- no uncertified step is taken;
  - the Taylor truncation error is bounded by the majorant method (see _step) and added to the balls.

A loop's transported fundamental matrix encloses the TRUE monodromy matrix of that loop, whatever the
loop encloses. The Ziglin-form certificate is then decided on these enclosures with 'certainly' logic.
"""
import cmath
import math
import sympy as sp
from flint import acb, arb, acb_series, ctx


# ----------------------------------------------------------------------------------------------
# SymPy -> ball / ball-series evaluator
# ----------------------------------------------------------------------------------------------
class Compiled:
    def __init__(self, expr, z):
        self.z = z
        repl, red = sp.cse(sp.sympify(expr))
        self.repl, self.out = repl, red[0]

    def _const(self, e):
        if e.is_Integer:
            return acb(int(e))
        if e.is_Rational:
            return acb(int(e.p))/int(e.q)
        if e == sp.I:
            return acb(0, 1)
        if e.is_number:
            re, im = e.as_real_imag()
            if re.is_Rational and im.is_Rational:
                return self._const(re) + acb(0, 1)*self._const(im)
        raise ValueError(f"unsupported constant {e}")

    def _ev(self, e, env):
        if e in env:
            return env[e]
        if e == self.z:
            return env["__z__"]
        if e.is_number:
            return self._const(e)
        if e.is_Add:
            v = self._ev(e.args[0], env)
            for a in e.args[1:]:
                v = v + self._ev(a, env)
            return v
        if e.is_Mul:
            v = self._ev(e.args[0], env)
            for a in e.args[1:]:
                v = v*self._ev(a, env)
            return v
        if e.is_Pow:
            b, n = e.args
            if not n.is_Integer:
                raise ValueError(f"non-integer power {e}: refused (branch cut)")
            return self._ev(b, env)**int(n)
        if isinstance(e, sp.exp):
            return self._ev(e.args[0], env).exp()
        raise ValueError(f"unsupported node {type(e).__name__}: {e}")

    def __call__(self, zval):
        env = {"__z__": zval}
        for s, e in self.repl:
            env[s] = self._ev(e, env)
        return self._ev(self.out, env)


def box(c, rad):
    """Complex box containing the disk |z - c| <= rad."""
    c = complex(c)
    return acb(arb(c.real, rad), arb(c.imag, rad))


def upper(x):
    """Rigorous float upper bound of |x| for an acb/arb."""
    return float(abs(x).upper())


# ----------------------------------------------------------------------------------------------
# one certified Taylor step
# ----------------------------------------------------------------------------------------------
MRHO2_MAX = 4.0     # step policy: reject disks with M rho^2 above this (the tail bound carries exp(M rho^2/N);
                    # near-pole boxes give finite but huge M). Policy only -- every accepted step is rigorous.


def _step(rc, za, zb, N):
    """Transfer matrix T(za -> zb) for (y, y') with rigorous enclosure, or None if the disk
    |z - za| <= rho = 2|zb - za| is not certified analytic.

    Majorant (A2): |r_k| <= rabs_k (exact ball bounds) for k <= N; |r_k| <= M' rho'^-k (Cauchy on rho' = 1.5 rho)
    for k > N. With m_k = |r_k| rho^k <= Mbar = max(max_k<=N m_k, M' (2/3)^(N+1)) the tail recursion below holds with
    M rho^2 replaced by Mbar rho^2. (Stage-1 form, kept for the record:) |r_k| <= M rho^-k (Cauchy, M = sup |r| on the disk). With A_0 = A_1 = 1 (>= |a_0|, |a_1|
    of both basis solutions) and n(n-1) A_n = sum_{k<=n-2} M rho^-k A_{n-2-k}, induction gives |a_n| <= A_n.
    B_n = A_n rho^n, S_n = sum_{j<=n} B_j satisfy S_n <= S_{n-1}(1 + M rho^2/(n(n-1))), so for n > N
    B_n <= S* = S_N exp(M rho^2/N). At |t| = rho/2 (q = 1/2): tail of y <= S* q^(N+1)/(1-q),
    tail of y' <= (S*/rho) q^N ((N+1) - N q)/(1-q)^2."""
    h = abs(complex(zb) - complex(za))
    rho = 2*h
    rhop = 1.5*rho                      # A2: Cauchy bound only for k > N, on the larger disk rho' = 1.5 rho
    Mb = rc(box(za, rhop))
    if not Mb.is_finite():
        return None
    Mp = arb(upper(Mb))
    # Taylor coefficients of r at za
    old = ctx.cap
    ctx.cap = N + 2
    try:
        s = rc(acb_series([acb(complex(za)), 1]))
        rk = list(s.coeffs()) if isinstance(s, acb_series) else [s]
    finally:
        ctx.cap = old
    rk = rk + [acb(0)]*(N + 1 - len(rk))
    rho_a = arb(rho)
    rabs = [arb(upper(c)) for c in rk]                       # rigorous upper bounds |r_k|
    mk = [rabs[k]*rho_a**k for k in range(N + 1)]
    Mbar = Mp*(arb(rho)/arb(rhop))**(N + 1)
    for v in mk:
        if upper(v) > upper(Mbar):
            Mbar = arb(upper(v))
    M = arb(upper(Mbar))
    if upper(M*rho_a**2) > MRHO2_MAX:
        return None
    t = acb(complex(zb)) - acb(complex(za))
    T = []
    for a0, a1 in ((acb(1), acb(0)), (acb(0), acb(1))):
        a = [a0, a1]
        for n in range(2, N + 1):
            acc = acb(0)
            for k in range(0, n - 1):
                acc += rk[k]*a[n - 2 - k]
            a.append(acc/(n*(n - 1)))
        y, yp, tp = acb(0), acb(0), acb(1)
        for n in range(N + 1):
            y += a[n]*tp
            if n + 1 <= N:
                yp += (n + 1)*a[n + 1]*tp
            tp *= t
        T.append((y, yp))
    # majorant tail
    A = [arb(1), arb(1)]
    for n in range(2, N + 1):                                 # A2: exact |r_k| (k <= N-2 here)
        acc = arb(0)
        for k in range(0, n - 1):
            acc += rabs[k]*A[n - 2 - k]
        A.append(acc/(n*(n - 1)))
    S_N = sum(A[j]*rho_a**j for j in range(N + 1))
    Sstar = S_N*(M*rho_a**2/N).exp()
    q = arb(0.5)
    ey = upper(Sstar*q**(N + 1)/(1 - q))
    eyp = upper(Sstar/rho_a*q**N*((N + 1) - N*q)/(1 - q)**2)
    # y'(N-term) above uses coefficients up to a_N; the omitted n = N+1.. terms of y' are covered by eyp
    err = lambda v, e: v + acb(arb(0, e), arb(0, e))
    (y1, y1p), (y2, y2p) = T
    return [[err(y1, ey), err(y2, ey)], [err(y1p, eyp), err(y2p, eyp)]]


def _matmul(P, Q):
    return [[P[0][0]*Q[0][0] + P[0][1]*Q[1][0], P[0][0]*Q[0][1] + P[0][1]*Q[1][1]],
            [P[1][0]*Q[0][0] + P[1][1]*Q[1][0], P[1][0]*Q[0][1] + P[1][1]*Q[1][1]]]


def transport(rc, pts, N=100, hmax=0.25, dist=None, min_h=1e-6, stats=None):
    """Certified transfer matrix along the polyline pts (complex). dist(z) (optional) is a float
    estimate of the distance to the nearest singularity, used only to pick step sizes."""
    Y = [[acb(1), acb(0)], [acb(0), acb(1)]]
    nsteps = 0
    for p, q in zip(pts[:-1], pts[1:]):
        z = complex(p)
        q = complex(q)
        while abs(q - z) > 0:
            h = min(abs(q - z), hmax)
            if dist is not None:
                h = min(h, 0.2*dist(z))
            while True:
                zb = q if h >= abs(q - z) else z + h*(q - z)/abs(q - z)
                T = _step(rc, z, zb, N)
                if T is not None:
                    break
                h /= 2
                if h < min_h:
                    raise RuntimeError(f"step size underflow near {z}: cannot certify analyticity")
            Y = _matmul(T, Y)
            z = zb
            nsteps += 1
    if stats is not None:
        stats["steps"] = stats.get("steps", 0) + nsteps
    return Y


def loop_points(z0, c, rad, ngon=16):
    """Closed polyline: z0 -> circle(c, rad) entry point -> ngon around c (counter-clockwise) -> z0."""
    z0, c = complex(z0), complex(c)
    ph = cmath.phase(z0 - c)
    circ = [c + rad*cmath.exp(1j*(ph + 2*math.pi*k/ngon)) for k in range(ngon + 1)]
    return [z0] + circ + [z0]


# ----------------------------------------------------------------------------------------------
# SL(2) ball helpers and the Ziglin-form certificate
# ----------------------------------------------------------------------------------------------
def det(Y):
    return Y[0][0]*Y[1][1] - Y[0][1]*Y[1][0]


def inv(Y):
    d = det(Y)
    return [[Y[1][1]/d, -Y[0][1]/d], [-Y[1][0]/d, Y[0][0]/d]]


def tr(Y):
    return Y[0][0] + Y[1][1]


def certainly_not_in_segment(t, lo=-2, hi=2):
    """True only if the ball t certainly avoids the real segment [lo, hi]."""
    return bool(t.imag > 0 or t.imag < 0 or t.real > hi or t.real < lo)


def certainly_ne(t, v):
    d = t - v
    return bool(d.real > 0 or d.real < 0 or d.imag > 0 or d.imag < 0)


def certificate(g, h):
    """(i) tr g not in [-2,2], (ii) tr h not in [-2,2], (iii) tr[g,h] != 2 -- all CERTIFIED.
    Returns (bool, details)."""
    tg, th = tr(g), tr(h)
    c = tr(_matmul(_matmul(g, h), _matmul(inv(g), inv(h))))
    ok = certainly_not_in_segment(tg) and certainly_not_in_segment(th) and certainly_ne(c, 2)
    return ok, dict(tr_g=str(tg), tr_h=str(th), tr_comm=str(c))


def radius_digits(x):
    """Approximate number of correct decimal digits of a ball (relative)."""
    m = max(upper(x), 1e-300)
    r = float(abs(x.real).rad() + abs(x.imag).rad()) if hasattr(x, "imag") else float(x.rad())
    return -math.log10(max(r, 1e-300)/m) if r > 0 else 99.0
