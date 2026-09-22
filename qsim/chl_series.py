"""
Local power series of the CH07 cut-sphere system about x = pi.

Why: the ODE start at x = pi is a boundary layer. With first-order start data
placed at pi - delta, the result carries a delta^2 log(delta) error, and at large
t (replica continuation a = 1/2 - it) the layer narrows until first-order data
selects no beta branch at all while the formulation turns stiff (Jacobian
~ 1/(k^2 bc eps^2)). CHL09 p.8 state the remedy they used: expand in Taylor
series about x = pi and get the coefficients from the equations.

Method. eps = pi - x. Each of the 11 equations (23)-(33) is multiplied through to
clear its sin(eps/2) poles (forms below), all 11 functions are truncated power
series, the six ODE variables have their eps^0 coefficients fixed by the
validated boundary data, and every other coefficient is found by Newton
iteration on the coefficient vector. If a pure power series exists the residual
reaches rounding level and low coefficients are stable under changing N.

Cleared forms (s = sin(eps/2), co = cos(eps/2), K = 8 pi a(1-a)):
 (23)  H_e  - (M/2)(b B2 + c B1 + 2 u B12)                                 = 0
 (24)  X1_e - M (b B12 + u B1)                                             = 0
 (25)  X2_e - M (c B12 + u B2)                                             = 0
 (26)  s c_e - M beta2 u - (1-a) c s tan(eps/2)                            = 0
 (27)  s b_e - M beta1 u - a b s tan(eps/2)                                = 0
 (28)  s u_e - (M/2)(b beta2 + c beta1) + (1/2) u co                       = 0
 (29)  s/K - co H + M (beta1 X2 + beta2 X1) - 2 M s u B12                  = 0
 (30)  s co/K + s^2 H + M co (beta1 X2 + beta2 X1) - M s co (b B2 + c B1)  = 0
 (31)  -M s co (c X1 - b X2) + M co (beta2 B1 - beta1 B2) + (1-2a) s^2 B12 = 0
 (32)  -4a(a-1) - M^2(4 - 8 beta1 beta2 + bc + 3u^2)
         + 4 cos(eps)(a(a-1) + M^2(u^2+1)) + M^2 cos(2eps)(bc - u^2)       = 0
 (33)  (2a-1) u s^2 + M co (beta1 c - b beta2)                             = 0
(x = pi - eps, d/dx = -d/deps; cos x = -cos eps, cos 2x = cos 2eps.)
"""
import math
import numpy as np

PI = np.pi
NAMES = ["H", "X1", "X2", "b", "c", "u", "beta1", "beta2", "B1", "B2", "B12"]
ODE_VARS = ["H", "X1", "X2", "b", "c", "u"]


def _ser(coeffs, N):
    out = np.zeros(N + 1, dtype=complex)
    n = min(len(coeffs), N + 1)
    out[:n] = coeffs[:n]
    return out


def trig_series(N):
    """Taylor coefficients in eps of the trig factors, to order N."""
    k = np.arange(N + 1)
    fact = np.array([math.factorial(int(i)) for i in k], dtype=float)
    def from_pattern(f):
        return np.array([f(int(i)) for i in k], dtype=complex)
    s = from_pattern(lambda n: 0 if n % 2 == 0 else (-1)**((n - 1)//2) * 0.5**n / math.factorial(n))
    co = from_pattern(lambda n: 0 if n % 2 else (-1)**(n//2) * 0.5**n / math.factorial(n))
    c1 = from_pattern(lambda n: 0 if n % 2 else (-1)**(n//2) / math.factorial(n))
    c2 = from_pattern(lambda n: 0 if n % 2 else (-1)**(n//2) * 2.0**n / math.factorial(n))
    tan = div(s, co)
    return dict(s=s, co=co, cos1=c1, cos2=c2, tan=tan)


def mul(p, q):
    return np.convolve(p, q)[:len(p)]


def div(p, q):
    """p/q as truncated series; q[0] != 0."""
    N = len(p) - 1
    r = np.zeros(N + 1, dtype=complex)
    for n in range(N + 1):
        r[n] = (p[n] - np.dot(r[:n], q[n:0:-1])) / q[0]
    return r


def deriv(p):
    """d/deps, same length, top coefficient lost (set 0)."""
    N = len(p) - 1
    d = np.zeros(N + 1, dtype=complex)
    d[:N] = p[1:] * np.arange(1, N + 1)
    return d


def residuals(F, a, M, T):
    """The 11 cleared equations as series; F maps name -> coefficient array."""
    H, X1, X2, b, c, u = (F[n] for n in ODE_VARS)
    b1, b2, B1, B2, B12 = F["beta1"], F["beta2"], F["B1"], F["B2"], F["B12"]
    s, co, tan = T["s"], T["co"], T["tan"]
    one = np.zeros_like(H); one[0] = 1
    K = 8*PI*a*(1 - a)
    bx = mul(b1, X2) + mul(b2, X1)
    st = mul(s, tan)
    R = [
        deriv(H) - (M/2)*(mul(b, B2) + mul(c, B1) + 2*mul(u, B12)),
        deriv(X1) - M*(mul(b, B12) + mul(u, B1)),
        deriv(X2) - M*(mul(c, B12) + mul(u, B2)),
        mul(s, deriv(c)) - M*mul(b2, u) - (1 - a)*mul(c, st),
        mul(s, deriv(b)) - M*mul(b1, u) - a*mul(b, st),
        mul(s, deriv(u)) - (M/2)*(mul(b, b2) + mul(c, b1)) + 0.5*mul(u, co),
        s/K - mul(co, H) + M*bx - 2*M*mul(s, mul(u, B12)),
        mul(s, co)/K + mul(mul(s, s), H) + M*mul(co, bx) - M*mul(mul(s, co), mul(b, B2) + mul(c, B1)),
        -M*mul(mul(s, co), mul(c, X1) - mul(b, X2)) + M*mul(co, mul(b2, B1) - mul(b1, B2))
            + (1 - 2*a)*mul(mul(s, s), B12),
        (-4*a*(a - 1) - 4*M*M)*one + 8*M*M*mul(b1, b2) - M*M*mul(b, c) - 3*M*M*mul(u, u)
            + 4*mul(T["cos1"], a*(a - 1)*one + M*M*(mul(u, u) + one))
            + M*M*mul(T["cos2"], mul(b, c) - mul(u, u)),
        (2*a - 1)*mul(u, mul(s, s)) + M*mul(co, mul(b1, c) - mul(b, b2)),
    ]
    return R


def solve_series(a, M, start, N=24, iters=40, tol=1e-13, guess=None, verbose=False,
                 strict=True, want_jacobian=False):
    """Newton on the coefficient vector. `start` = chl_corner.start_data(a, M).

    Residual orders 0..N-1 are enforced (the derivative loses the top order).
    `guess`: a converged series at NEIGHBOURING parameters, used as the initial
    iterate (continuation). Without it the first-order local solution is used,
    which is adequate at small t but diverges once k is small (t >~ 2).
    The Jacobian is formed with per-column relative steps and column scaling,
    because the unknowns span e^{-pi M} (b, c, u) to e^{+pi M} (B1, B2).
    Raises if Newton does not reach `tol`: an unconverged series must never
    silently become start data.
    """
    T = trig_series(N)
    fixed0 = dict(H=0.0, X1=start["X1"], X2=start["X2"], b=start["b"], c=start["c"], u=0.0)
    F = {n: np.zeros(N + 1, dtype=complex) for n in NAMES}
    if guess is not None:
        for n in NAMES:
            m = min(N + 1, len(guess[n]))
            F[n][:m] = guess[n][:m]
    else:
        F["H"][1], F["u"][1] = start["H1"], start["u1"]
        F["beta1"][1], F["beta2"][1] = start["k"]*start["b"], start["k"]*start["c"]
        F["B1"][0], F["B2"][0] = start["B1"], start["B2"]
    for n, v in fixed0.items():
        F[n][0] = v
    idx = [(n, j) for n in NAMES for j in range(N + 1) if not (n in fixed0 and j == 0)]
    def pack(F):
        return np.array([F[n][j] for n, j in idx])
    def unpack(z):
        G = {n: F[n].copy() for n in NAMES}
        for (n, j), v in zip(idx, z):
            G[n][j] = v
        return G
    # characteristic size of each function, for relative steps and column scaling
    # Physical scales from the start data, never from the (possibly zero) guess:
    # a zero initial iterate (B12 at first order) would otherwise get a 1e-307
    # finite-difference step. b, c, u ~ e^{-pi M}; B1, B2 ~ e^{+pi M}.
    phys = dict(H=abs(start["H1"]), X1=abs(start["X1"]), X2=abs(start["X2"]),
                b=abs(start["b"]), c=abs(start["c"]), u=abs(start["u1"]),
                beta1=abs(start["k"])*max(abs(start["b"]), abs(start["c"])),
                B1=abs(start["B1"]), B2=abs(start["B2"]))
    phys["beta2"] = phys["beta1"]
    phys["B12"] = min(phys["B1"], phys["B2"])
    size = {n: max(np.max(np.abs(F[n])), phys[n]) for n in NAMES}
    colscale = np.array([size[n] for n, j in idx])
    def resvec(z):
        return np.concatenate([r[:N] for r in residuals(unpack(z), a, M, T)])
    # Tolerance is RELATIVE to the equations' own scale: with B ~ e^{pi M} the
    # rounding floor of an absolute residual rises exponentially in M, and an
    # absolute 1e-13 is unreachable at M >= 4 though the series is converged.
    def eqscale(z):
        G = unpack(z)
        mags = [np.max(np.abs(G[n])) for n in NAMES]
        return max(1.0, max(abs(M)*mags[3]*mags[9], abs(M)*mags[4]*mags[8]))
    z = pack(F)
    hist = []
    for it in range(iters):
        r = resvec(z)
        nr = np.max(np.abs(r))/eqscale(z)
        hist.append(nr)
        if verbose:
            print(f"   newton {it}: max|res| = {nr:.3e}")
        if nr < tol:
            break
        # Every residual is AT MOST QUADRATIC in the unknowns (products of two
        # series), so a CENTRAL difference is exact up to rounding for any step:
        # the O(h^2) truncation term vanishes identically. A large step then
        # also suppresses rounding. (Forward differences carried O(h) ~ 1e-7
        # error, which the ~1/(k^2 bc) conditioning at large t turned into a
        # Newton stall at t ~ 2.2.)
        J = np.empty((len(r), len(z)), dtype=complex)
        for j in range(len(z)):
            h = 1e-2*colscale[j]
            zp = z.copy(); zp[j] += h
            zm = z.copy(); zm[j] -= h
            J[:, j] = (resvec(zp) - resvec(zm))/(2*h)
        dzs, *_ = np.linalg.lstsq(J*colscale, -r, rcond=None)
        # damped: backtrack until the residual actually falls (undamped steps
        # overshot to 2e3 from 3e-2 at t = 2.2 before crawling back)
        lam = 1.0
        while True:
            zt = z + lam*dzs*colscale
            if np.max(np.abs(resvec(zt)))/eqscale(zt) < nr or lam < 1e-4:
                break
            lam *= 0.5
        z = zt
    if hist[-1] >= tol and strict:
        raise RuntimeError(f"series Newton did not converge at a={a}, M={M}: "
                           f"residual {hist[-1]:.2e} after {len(hist)} iterations")
    info = dict(residual=hist[-1], history=hist, n_unknowns=len(z), n_eqs=len(r),
                converged=hist[-1] < tol)
    if want_jacobian:
        # at the returned iterate, central differences (exact for quadratic eqs)
        J = np.empty((len(r), len(z)), dtype=complex)
        for j in range(len(z)):
            h = 1e-2*colscale[j]
            zp = z.copy(); zp[j] += h
            zm = z.copy(); zm[j] -= h
            J[:, j] = (resvec(zp) - resvec(zm))/(2*h)
        info.update(J=J, colscale=colscale, idx=idx)
    return unpack(z), info


def continue_in_t(t_target, M, N=32, dt=0.05, dt_min=1e-3, start_fn=None, keep=None,
                  strict=True):
    """Series at a = 1/2 - i t, for every t in `keep` up to t_target, by
    continuation from t = 0 with a SECANT predictor (linear extrapolation from
    the last two converged series) and adaptive steps. Returns {t: series}.
    A step that fails is halved, down to dt_min, and then the whole call raises:
    a gap in the continuation must never be bridged silently."""
    import chl_corner as cc
    start_fn = start_fn or cc.start_data
    keep = sorted(set([float(t_target)] + list(keep or [])))
    out = {}
    t, h = 0.0, dt
    G_prev, t_prev = None, None
    a = 0.5 + 0j
    G, _ = solve_series(a, M, start_fn(a, M), N=N, strict=strict)
    if 0.0 in keep:
        out[0.0] = G
    pending = [k for k in keep if k > 0]
    while pending:
        nxt = min(t + h, pending[0])
        if G_prev is None:
            guess = G
        else:
            w = (nxt - t)/(t - t_prev)
            guess = {n: G[n] + w*(G[n] - G_prev[n]) for n in NAMES}
        a = 0.5 - 1j*nxt
        try:
            Gn, inf = solve_series(a, M, start_fn(a, M), N=N, guess=guess, strict=strict)
            if not strict and inf["residual"] > 1e-6:
                raise RuntimeError("guess too poor even for refinement")
        except RuntimeError:
            h *= 0.5
            if h < dt_min:
                raise RuntimeError(f"continuation stalled at t = {t:.4f} (M = {M}): "
                                   f"step fell below {dt_min}")
            continue
        G_prev, t_prev, G, t = G, t, Gn, nxt
        if abs(t - pending[0]) < 1e-12:
            out[pending.pop(0)] = G
        h = min(dt, 1.5*h)
    return out


def evaluate(G, eps, upto=None):
    """Sum each series at eps using coefficients up to order `upto`."""
    out = {}
    for n, cf in G.items():
        m = len(cf) if upto is None else upto + 1
        out[n] = np.polyval(cf[:m][::-1], eps)
    return out
