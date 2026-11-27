"""
mn_indep.py -- independent implementation of the reduced Manko-Novikov (MN)
geodesic Hamiltonian, mpmath only (no CAS).

Source: J. R. Gair, C. Li, I. Mandel, "Observable properties of orbits in exact
bumpy spacetimes", Phys. Rev. D 77, 024035 (2008), arXiv:0708.0628v2, Sec. II:
  line element               eq. (2)
  metric functions           eqs. (3a)-(3l)
  multipole moments          eq. (4)
  (alpha, k, beta) from (M, chi, q)   eq. (5)
  rho, z                     eq. (6)

Physical setting: G = c = 1, signature (-,+,+,+), M = 5, a = J/M = 3
(chi = 3/5), so alpha = -1/3, k = 4. Coordinates (t, x, y, phi).

Only ONE deviation from the literal typeset text (a typo; see the report):
in eq. (3h) the "-2" is applied ONCE to the l-sum, i.e.
   beta * [ sum_{l=0}^{2} (x - y + (-1)^(2-l) (x+y)) P_l / R^(l+1)  -  2 ],
not "-2" inside every summand.  Only this reading gives gamma = 0 on the
symmetry axis (y = +-1) and at spatial infinity (elementary flatness /
asymptotic flatness); the literal reading gives gamma -> -4 beta there.

H = 1/2 g^{mu nu} p_mu p_nu with p_t = -E, p_phi = +L, (px, py) conjugate to
(x, y).  The t-phi block is inverted numerically as an exact 2x2 inverse;
g^{xx} = 1/g_xx, g^{yy} = 1/g_yy.

Derivatives: mpmath.diff (default 'step' method: central finite differences
evaluated at automatically raised working precision), at the caller's
working precision (mp.dps >= 50 enforced at import; default here 60).
"""
from mpmath import mp, mpf, sqrt, exp, log, legendre, diff

if mp.dps < 60:
    mp.dps = 60

M_MASS = 5      # mass M
A_SPIN = 3      # Kerr spin a = J/M  (rotation in the +phi sense)


def _params():
    """Paper eq. (5), evaluated at the CURRENT working precision."""
    M = mpf(M_MASS)
    chi = mpf(A_SPIN) / M                       # chi = S1/M^2 = a/M
    alpha = (-1 + sqrt(1 - chi**2)) / chi       # eq. (5): -1/3
    k = M * (1 - alpha**2) / (1 + alpha**2)     # eq. (5): 4
    return M, chi, alpha, k


def metric_functions(x, y, beta):
    """f, omega, e^{2 gamma} of eqs. (3a)-(3l), plus intermediates."""
    _, _, alpha, k = _params()
    R = sqrt(x**2 + y**2 - 1)                              # (3k)
    u = x * y / R                                           # argument of (3l)
    P = [legendre(n, u) for n in range(4)]                  # (3l)
    psi = beta * R**(-3) * P[2]                             # (3g)
    s_g = sum((x - y + (-1)**(2 - l) * (x + y)) / R**(l + 1) * P[l]
              for l in range(3))
    gammap = (log((x**2 - 1) / (x**2 - y**2)) / 2
              + 9 * beta**2 / (6 * R**6) * (P[3] * P[3] - P[2] * P[2])
              + beta * (s_g - 2))                           # (3h), -2 once
    s_a = sum((x - y) * P[l] / R**(l + 1) for l in range(3))
    a = -alpha * exp(-2 * beta * (-1 + s_a))                # (3i)
    s_b = sum((-1)**(3 - l) * (x + y) * P[l] / R**(l + 1) for l in range(3))
    b = alpha * exp(2 * beta * (1 + s_b))                   # (3j)
    A = (x**2 - 1) * (1 + a * b)**2 - (1 - y**2) * (b - a)**2          # (3d)
    B = (x + 1 + (x - 1) * a * b)**2 + ((1 + y) * a + (1 - y) * b)**2  # (3e)
    C = ((x**2 - 1) * (1 + a * b) * (b - a - y * (a + b))
         + (1 - y**2) * (b - a) * (1 + a * b + x * (1 - a * b)))       # (3f)
    f = exp(2 * psi) * A / B                                           # (3a)
    omega = 2 * k * exp(-2 * psi) * C / A - 4 * k * alpha / (1 - alpha**2)  # (3b)
    e2gamma = exp(2 * gammap) * A / (x**2 - 1) / (1 - alpha**2)**2     # (3c)
    return dict(f=f, omega=omega, e2gamma=e2gamma, gammap=gammap, psi=psi,
                a=a, b=b, A=A, B=B, C=C, R=R, k=k, alpha=alpha)


def metric(x, y, beta):
    """Covariant components from eq. (2): returns (g_tt, g_tphi, g_phiphi, g_xx, g_yy)."""
    m = metric_functions(x, y, beta)
    f, w, e2g, k = m['f'], m['omega'], m['e2gamma'], m['k']
    g_tt = -f
    g_tp = f * w
    g_pp = -f * w**2 + k**2 / f * (x**2 - 1) * (1 - y**2)
    g_xx = k**2 / f * e2g * (x**2 - y**2) / (x**2 - 1)
    g_yy = k**2 / f * e2g * (x**2 - y**2) / (1 - y**2)
    return g_tt, g_tp, g_pp, g_xx, g_yy


def _H(x, y, px, py, beta, E, L):
    g_tt, g_tp, g_pp, g_xx, g_yy = metric(x, y, beta)
    D = g_tt * g_pp - g_tp * g_tp          # exact 2x2 inverse of the t-phi block
    Gtt = g_pp / D
    Gtp = -g_tp / D
    Gpp = g_tt / D
    pt, pp = -E, L
    return (Gtt * pt * pt + 2 * Gtp * pt * pp + Gpp * pp * pp
            + px * px / g_xx + py * py / g_yy) / 2


def _cv(*v):
    return [mpf(t) for t in v]


def H(x, y, px, py, beta, E, L):
    """1/2 g^{mu nu} p_mu p_nu, p_t = -E, p_phi = +L."""
    x, y, px, py, beta, E, L = _cv(x, y, px, py, beta, E, L)
    return _H(x, y, px, py, beta, E, L)


def field(x, y, px, py, beta, E, L):
    """(dH/dpx, dH/dpy, -dH/dx, -dH/dy).  Momentum derivatives are taken with
    mpmath.diff too (method stated in module docstring)."""
    x, y, px, py, beta, E, L = _cv(x, y, px, py, beta, E, L)
    dpx = diff(lambda s: _H(x, y, s, py, beta, E, L), px)
    dpy = diff(lambda s: _H(x, y, px, s, beta, E, L), py)
    dx = diff(lambda s: _H(s, y, px, py, beta, E, L), x)
    dy = diff(lambda s: _H(x, s, px, py, beta, E, L), y)
    return (dpx, dpy, -dx, -dy)


def dH_dbeta(x, y, px, py, E, L):
    """dH/dbeta at beta = 0 (mpmath.diff)."""
    x, y, px, py, E, L = _cv(x, y, px, py, E, L)
    return diff(lambda b: _H(x, y, px, py, b, E, L), mpf(0))
