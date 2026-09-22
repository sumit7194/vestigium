"""
Free-scalar corner function a(theta), from the published Casini-Huerta equations.

The fresh solver for the CHL sub-45 CHECK (PREREG_cuspis_sub45_check.md). Sources:
CH07 = hep-th/0606256 eqs (23)-(40), read from the RENDERED pages (text extraction
dropped parentheses in (32) -- see chl_boundary.py); CHL09 = arXiv:0811.1968
eq (61). No import from corner_function/, and nothing of cuspis's read out of git
history. Boundary data at x = pi were validated independently of every published
s-value in chl_boundary.py before this file existed.

THE SYSTEM. For twist a and mass M on the cut sphere, integrate in x from pi down:
  state (H, X1, X2, b, c, u) by (23)-(28), with (beta1, beta2, B1, B2, B12) solved
  at each x from the algebraic set (29)-(33). The trace is
      tr G(x, M, a) = 8 pi a (1-a) I(x),     I(x) = int_x^pi H(y) dy.
REAL scalar, von Neumann (n = 1 ONLY -- n = 2 is excluded as contaminated):
      s(x) = int_0^inf dt sech^2(pi t) int_{1/2}^inf dM M sqrt(M^2 - 1/4) tr G(x,M,1/2-it)
(half of CHL09 (61); derived independently from CH07 (40) by the continuation
 lim (1/(n-1)) sum g(k/n) = pi int sech^2(pi t) g(1/2 - it) dt, checked exactly on
 g = a(1-a) and a^2(1-a)^2).

THE SINGULAR START. At x = pi, beta = 0 exactly and several algebraic solves are
0/0. Leading behaviour, all derived (chl_boundary.py): beta ~ k eps (b, c),
u ~ M k b c eps, H ~ (M/2)(b B2 + c B1) eps, with k and B1, B2 closed-form from
(32), (80), (81) at pi. Integration starts at x = pi - delta from that data; the
delta-dependence is MEASURED, not assumed small.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import gamma, psi

PI = np.pi


def _pairgamma(z0, mu):
    """Gamma(z0 + i mu/2) Gamma(z0 - i mu/2): |Gamma|^2 for real z0, continued analytically."""
    return gamma(z0 + 0.5j*mu) * gamma(z0 - 0.5j*mu)


def _impsi(z0, mu):
    """Im psi(z0 + i mu/2) for real z0, continued analytically."""
    return (psi(z0 + 0.5j*mu) - psi(z0 - 0.5j*mu)) / 2j


def X1_pi_typeset(a, M):
    """Eq (35) exactly as typeset (validated in chl_boundary.py for real a).
    Kept for cross-checking only: it has a removable 0*inf at mu = 2t when
    a = 1/2 - it, where cos(2 pi a) + cosh(pi mu) -> 0 and Gamma(1/2-a-i mu/2) -> Gamma(0)."""
    mu = np.sqrt(4*M*M - 1)
    num = gamma(-a) * (np.cosh(PI*mu/2)*_impsi(0.5 + a, mu) - PI/2*np.sinh(PI*mu/2))
    den = 2**(2*a) * mu * (np.cos(2*a*PI) + np.cosh(PI*mu)) * gamma(1 + a) * _pairgamma(0.5 - a, mu)
    return num / den


def X1_pi(a, M):
    """Eq (35) with the 0*inf removed EXACTLY, not numerically.
    With z, z' = 1/2 - a -+ i mu/2:  cos(2 pi a) + cosh(pi mu) = 2 sin(pi z) sin(pi z'),
    and reflection Gamma(z) sin(pi z) = pi / Gamma(1-z) makes the denominator
      (cos 2 pi a + cosh pi mu) Gamma(z) Gamma(z') = 2 pi^2 / [Gamma(1/2+a+i mu/2) Gamma(1/2+a-i mu/2)].
    """
    mu = np.sqrt(4*M*M - 1)
    num = gamma(-a) * (np.cosh(PI*mu/2)*_impsi(0.5 + a, mu) - PI/2*np.sinh(PI*mu/2))
    return num * _pairgamma(0.5 + a, mu) / (2**(2*a + 1) * PI**2 * mu * gamma(1 + a))


def b_pi(a, M):
    mu = np.sqrt(4*M*M - 1)
    return 2**(1 - 2*a) * a*(1 - a) * _pairgamma(0.5 + a, mu) / (M * gamma(1 + a)**2)


def start_data(a, M, k_sign=-1.0):
    """Everything at x = pi, plus the first-order slopes. Complex a allowed."""
    X1, X2 = X1_pi(a, M), X1_pi(1 - a, M)
    b, c = b_pi(a, M), b_pi(1 - a, M)
    k = k_sign * np.sqrt((a*(a - 1) + M*M*(1 + b*c)) / (4*M*M*b*c))
    # (81) at pi:  c X1 - b X2 = 2k (c B1 - b B2)
    # (80) at pi:  1/(8 pi a(1-a)) = M (b B2 + c B1) - 2 M k (b X2 + c X1)
    lhs = np.array([[2*k*c, -2*k*b], [M*c, M*b]], dtype=complex)
    rhs = np.array([c*X1 - b*X2, 1/(8*PI*a*(1 - a)) + 2*M*k*(b*X2 + c*X1)], dtype=complex)
    B1, B2 = np.linalg.solve(lhs, rhs)
    return dict(X1=X1, X2=X2, b=b, c=c, k=k, B1=B1, B2=B2,
                H1=0.5*M*(b*B2 + c*B1), u1=M*k*b*c)


class CutSphere:
    """ODE right-hand side with the algebraic solve. PURE: no state mutates per call.

    The beta branch was first chosen as "the root nearest the previous one", stored
    as a side effect. That made the RHS impure -- every Jacobian probe and trial
    stage rewrote the branch -- and near x = pi the two roots are only ~2|k| c eps
    apart, so a probe could flip them. Now the branch is fixed ONCE from the start
    data: beta2 = (-Q + sigma sqrt(D)) / (2b), with sqrt's cut rotated to lie
    opposite arg(D_start) so a path along which arg(D) stays near its start value
    never crosses it. If arg(D) drifts by more than pi/2 the call RAISES rather
    than silently changing branch.
    """

    def __init__(self, a, M, beta2_start, x_start, state_start):
        self.a, self.M = a, M
        self.sigma, self.phi0 = 1.0, 0.0
        D0, Q0 = self._disc(x_start, *state_start)
        self.phi0 = np.angle(D0)
        r = self._sqrt(D0)
        b0 = state_start[3]
        cand = {+1.0: (-Q0 + r)/(2*b0), -1.0: (-Q0 - r)/(2*b0)}
        self.sigma = min(cand, key=lambda sg: abs(cand[sg] - beta2_start))
        if abs(cand[self.sigma] - beta2_start) > 1e-2*abs(beta2_start):
            raise RuntimeError("start data does not select a beta branch cleanly")

    def _sqrt(self, D):
        rot = np.exp(-1j*self.phi0)
        w = D*rot
        if np.real(w) < 0 and abs(np.angle(w)) > PI/2:
            raise RuntimeError(f"arg(D) drifted by {np.angle(w):.3f} from its start value: "
                               "branch continuity not guaranteed")
        return np.sqrt(w + 0j)*np.exp(0.5j*self.phi0)

    def _disc(self, x, H, X1, X2, b, c, u):
        a, M = self.a, self.M
        sx, cx = np.sin(x/2), np.cos(x/2)
        P8 = (4*a*(a - 1) + M*M*(4 + b*c + 3*u*u)
              + 4*np.cos(x)*(a*(a - 1) + M*M*(u*u + 1)) - M*M*np.cos(2*x)*(b*c - u*u))
        Q = -(2*a - 1)*u*cx*cx/(M*sx)                        # beta1 c - b beta2   (33)
        return Q*Q + 4*b*c*P8/(8*M*M), Q                     # beta1 beta2 = P8/8M^2 (32)

    def algebraic(self, x, H, X1, X2, b, c, u):
        a, M = self.a, self.M
        sx, cx = np.sin(x/2), np.cos(x/2)
        tx = sx/cx
        D, Q = self._disc(x, H, X1, X2, b, c, u)
        beta2 = (-Q + self.sigma*self._sqrt(D))/(2*b)
        beta1 = (Q + b*beta2)/c
        bx = beta1*X2 + beta2*X1
        B12 = (cx/(8*PI*a*(1 - a)) - sx*H + M*bx) / (2*M*cx*u)          # (29)
        R1 = (sx/(8*PI*a*(1 - a)) + cx*H + M*tx*bx) / (M*sx)             # (30): bB2 + cB1
        R2 = (M*sx*(c*X1 - b*X2) - (1 - 2*a)*cx*B12) / (M*tx)            # (31): beta2 B1 - beta1 B2
        B1, B2 = np.linalg.solve(np.array([[c, b], [beta2, -beta1]]), np.array([R1, R2]))
        return beta1, beta2, B1, B2, B12

    def __call__(self, x, y):
        a, M = self.a, self.M
        H, X1, X2, b, c, u, I = y
        beta1, beta2, B1, B2, B12 = self.algebraic(x, H, X1, X2, b, c, u)
        sx, cx = np.sin(x/2), np.cos(x/2)
        cscx = 1/np.sin(x)
        return [-(M/2)*(b*B2 + c*B1 + 2*u*B12),
                -M*(b*B12 + u*B1),
                -M*(c*B12 + u*B2),
                -2*M*beta1*u*cscx*sx - b*a*cscx*(1 + np.cos(x)),
                -2*M*beta2*u*cscx*sx - c*(1 - a)*cscx*(1 + np.cos(x)),
                -(M/2)/cx*(b*beta2 + c*beta1) + 0.5*u*sx/cx,
                -H]


def trace_G(a, M, xs, delta=1e-3, rtol=1e-11, atol=1e-14):
    """tr G(x, M, a) at the angles xs (descending order not required). Raises on failure."""
    d = start_data(a, M)
    eps = delta
    y0 = np.array([d["H1"]*eps, d["X1"], d["X2"], d["b"], d["c"], d["u1"]*eps,
                   0.5*d["H1"]*eps*eps], dtype=complex)
    rhs = CutSphere(a, M, beta2_start=d["k"]*d["c"]*eps, x_start=PI - delta,
                    state_start=tuple(y0[:6]))
    xs = np.atleast_1d(xs)
    sol = solve_ivp(rhs, [PI - delta, float(np.min(xs))], y0, method="DOP853",
                    rtol=rtol, atol=atol, dense_output=True)
    if not sol.success:
        raise RuntimeError(f"cut-sphere integration failed at a={a}, M={M}: {sol.message}")
    I = np.array([sol.sol(x)[6] for x in xs])
    return 8*PI*a*(1 - a)*I


# =============================================================================
# The start offset: MEASURED to go as delta^2 log(delta), so extrapolate in that
# basis. (A pure power series in delta fits 100x worse -- the local expansion at
# x = pi has a logarithmic resonance, which is why the naive rate was 1.85.)
# =============================================================================
DELTAS = np.array([4e-3, 2.83e-3, 2e-3, 1.41e-3, 1e-3])


def trace_G_extrap(a, M, xs, deltas=DELTAS):
    """tr G extrapolated to delta -> 0 in the basis {1, d^2 log d, d^2}.
    Returns (value, spread) where spread = |two-term fit - three-term fit|, a
    per-point honesty measure of the extrapolation itself."""
    G = np.array([trace_G(a, M, xs, delta=d) for d in deltas])      # (nd, nx)
    A2 = np.column_stack([np.ones_like(deltas), deltas**2*np.log(deltas), deltas**2])
    A3 = np.column_stack([A2, deltas**3])
    g2 = np.linalg.lstsq(A2, G, rcond=None)[0][0]
    g3 = np.linalg.lstsq(A3, G, rcond=None)[0][0]
    return g2, np.abs(g2 - g3)


def s_real_scalar(xs, nt=24, tmax=5.0, nq=32, qmax=8.0, verbose=False):
    """Von Neumann corner coefficient s(x) for a REAL free scalar.

    s(x) = int_0^tmax dt sech^2(pi t) int_0^qmax dq q^2 Re trG(x, sqrt(1/4+q^2), 1/2 - it)
    (M = sqrt(1/4 + q^2) turns M sqrt(M^2-1/4) dM into q^2 dq and keeps every node
     off q = 0, where the x = pi boundary formulas are 0/0.)
    Returns (s, diag) with the worst extrapolation spread seen, weighted.
    """
    xs = np.atleast_1d(np.asarray(xs, dtype=float))
    tn, tw = np.polynomial.legendre.leggauss(nt)
    tn, tw = 0.5*tmax*(tn + 1), 0.5*tmax*tw
    qn, qw = np.polynomial.legendre.leggauss(nq)
    qn, qw = 0.5*qmax*(qn + 1), 0.5*qmax*qw
    total = np.zeros(len(xs))
    err = np.zeros(len(xs))
    imag_max = 0.0
    for t, wt in zip(tn, tw):
        a = 0.5 - 1j*t
        wtt = wt / np.cosh(PI*t)**2
        for q, wq in zip(qn, qw):
            M = np.sqrt(0.25 + q*q)
            g, sp = trace_G_extrap(a, M, xs)
            imag_max = max(imag_max, float(np.max(np.abs(g.imag)/(np.abs(g.real) + 1e-300))))
            total += wtt*wq*q*q*g.real
            err += wtt*wq*q*q*sp
        if verbose:
            print(f"   t={t:.3f} done", flush=True)
    return total, dict(extrap_spread=err, imag_over_real_max=imag_max)


# =============================================================================
# Series-started integration (replaces the delta-extrapolated start)
# =============================================================================
def trace_G_from_series(a, M, G, xs, eps0=0.3, upto=None, rtol=1e-12, max_calls=100000,
                        method="DOP853"):
    """tr G(x) at angles xs, starting the ODE at x = pi - eps0 from the local
    power series G (chl_series). The series carries the solution through the
    boundary layer at x = pi exactly, so there is no delta to extrapolate."""
    import chl_series as cs
    upto = (len(G["H"]) - 3) if upto is None else upto
    st = cs.evaluate(G, eps0, upto)
    y0 = np.array([st[k] for k in ["H", "X1", "X2", "b", "c", "u"]] + [0], dtype=complex)
    cf = G["H"][:upto + 1]
    y0[6] = sum(cf[n]*eps0**(n + 1)/(n + 1) for n in range(len(cf)))   # int_0^eps0 H
    rhs = CutSphere(a, M, beta2_start=st["beta2"], x_start=PI - eps0, state_start=tuple(y0[:6]))
    calls = [0]
    def f(x, y):
        calls[0] += 1
        if calls[0] > max_calls:
            raise RuntimeError(f"rhs budget {max_calls} exceeded at a={a}, M={M}, x={x:.5f}")
        return rhs(x, y)
    xs = np.atleast_1d(xs)
    if method == "DOP853":
        sol = solve_ivp(f, [PI - eps0, float(np.min(xs))], y0, method="DOP853",
                        rtol=rtol, atol=1e-30, dense_output=True)
        if not sol.success:
            raise RuntimeError(f"integration failed at a={a}, M={M}: {sol.message}")
        I = np.array([sol.sol(x)[6] for x in xs])
    else:
        # Implicit, for the e^{pi M} stiffness from (29)'s 1/u. scipy's Radau is
        # real-only, so the state is split into real and imaginary parts.
        sc = np.maximum(np.abs(y0), 1e-300)
        def fr(x, yr):
            z = (yr[:7] + 1j*yr[7:])*sc
            r = np.asarray(f(x, z), dtype=complex)/sc
            return np.concatenate([r.real, r.imag])
        z0 = y0/sc
        sol = solve_ivp(fr, [PI - eps0, float(np.min(xs))], np.concatenate([z0.real, z0.imag]),
                        method=method, rtol=rtol, atol=1e-14, dense_output=True)
        if not sol.success:
            raise RuntimeError(f"{method} integration failed at a={a}, M={M}: {sol.message}")
        I = np.array([(sol.sol(x)[6] + 1j*sol.sol(x)[13])*sc[6] for x in xs])
    return 8*PI*a*(1 - a)*I, calls[0]
