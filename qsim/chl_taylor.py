"""
High-order Taylor stepping of the CH07 cut-sphere DAE at REGULAR points.

Why a Taylor method. The explicit and implicit integrators both hit walls that
are properties of the FORMULATION, not the solution: stiffness ~ e^{pi M} from
the 1/u in (29), and precision loss because b, c, u ~ e^{-pi M} while
B1, B2 ~ e^{+pi M}. A Taylor method's step is limited by the radius of
convergence of the TRUE solution -- its complex singularities, which do not grow
with M -- not by stiffness. Extra precision is then just more digits, which is
the whole cost. The same code runs in double (cmath) and in mpmath: arithmetic
is passed in as a backend.

Recursion at an expansion point x0, with delta = x - x0. ODE variables
Y = (H, X1, X2, b, c, u, I) and algebraic Z = (beta1, beta2, B1, B2, B12).
Given Y through order n and Z through order n-1:
  Z_n  : the algebraic equations (29)-(33) at order n are LINEAR in Z_n with a
         FIXED matrix A0 = d(eqs)/dZ at order 0 (the only quadratic term,
         beta1 beta2, contributes beta1_0 beta2_n + beta1_n beta2_0). One solve.
  Y_{n+1} = [RHS of (23)-(28)]_n / (n+1),   I' = -H.
At each new x0, Z_0 is found by Newton from the previous series evaluated there,
which preserves the beta branch by continuity.
"""
import cmath
import math

PI = math.pi
Y_NAMES = ["H", "X1", "X2", "b", "c", "u", "I"]
Z_NAMES = ["beta1", "beta2", "B1", "B2", "B12"]


class Backend:
    def __init__(self, kind="double", dps=30):
        self.kind = kind
        if kind == "double":
            self.sin, self.cos = cmath.sin, cmath.cos
            self.c = complex
            self.pi = math.pi
            self.abs = abs
        else:
            import mpmath
            self.mp = mpmath.mp
            self.mp.dps = dps
            self.sin, self.cos = mpmath.sin, mpmath.cos
            self.c = mpmath.mpc
            self.pi = mpmath.pi
            self.abs = abs

    def solve(self, A, b):
        """Gaussian elimination with partial pivoting on small dense systems."""
        n = len(b)
        A = [row[:] for row in A]; b = b[:]
        for k in range(n):
            p = max(range(k, n), key=lambda i: abs(A[i][k]))
            A[k], A[p] = A[p], A[k]; b[k], b[p] = b[p], b[k]
            if A[k][k] == 0:
                raise ZeroDivisionError("singular algebraic Jacobian")
            for i in range(k + 1, n):
                f = A[i][k]/A[k][k]
                for j in range(k, n):
                    A[i][j] -= f*A[k][j]
                b[i] -= f*b[k]
        x = [0]*n
        for i in range(n - 1, -1, -1):
            x[i] = (b[i] - sum(A[i][j]*x[j] for j in range(i + 1, n)))/A[i][i]
        return x


def _conv(p, q, n):
    return sum(p[j]*q[n - j] for j in range(n + 1))


def _series_div(p, q, N):
    r = [0]*(N + 1)
    for n in range(N + 1):
        r[n] = (p[n] - sum(r[j]*q[n - j] for j in range(n)))/q[0]
    return r


def trig_at(x0, N, B):
    """Taylor coefficients in delta of every trig factor, at x0."""
    zero = B.c(0)
    def sc_series(scale):          # sin(scale*delta), cos(scale*delta)
        s = [zero]*(N + 1); c = [zero]*(N + 1)
        f = B.c(1)
        for n in range(N + 1):
            if n > 0:
                f = f*scale/n
            if n % 2 == 0:
                c[n] = f*(-1)**(n//2)
            else:
                s[n] = f*(-1)**((n - 1)//2)
        return s, c
    s_h, c_h = sc_series(B.c(0.5))
    s_1, c_1 = sc_series(B.c(1))
    s_2, c_2 = sc_series(B.c(2))
    A, Bc = B.sin(x0/2), B.cos(x0/2)
    SX = [A*c_h[n] + Bc*s_h[n] for n in range(N + 1)]            # sin((x0+d)/2)
    CX = [Bc*c_h[n] - A*s_h[n] for n in range(N + 1)]            # cos((x0+d)/2)
    S1, C1 = B.sin(x0), B.cos(x0)
    SINX = [S1*c_1[n] + C1*s_1[n] for n in range(N + 1)]
    COSX = [C1*c_1[n] - S1*s_1[n] for n in range(N + 1)]
    S2, C2 = B.sin(2*x0), B.cos(2*x0)
    COS2X = [C2*c_2[n] - S2*s_2[n] for n in range(N + 1)]
    one = [B.c(1)] + [zero]*N
    TX = _series_div(SX, CX, N)
    SECX = _series_div(one, CX, N)
    CSC_SX = _series_div(SX, SINX, N)                           # csc(x) sin(x/2)
    ONEPC = [one[n] + COSX[n] for n in range(N + 1)]
    CSC_1PC = _series_div(ONEPC, SINX, N)                       # csc(x)(1+cos x)
    return dict(SX=SX, CX=CX, TX=TX, SECX=SECX, COSX=COSX, COS2X=COS2X,
                CSC_SX=CSC_SX, CSC_1PC=CSC_1PC)


def alg_residual_n(Y, Z, T, n, a, M, K):
    """Order-n coefficient of the five algebraic equations (29)-(33)."""
    cv = _conv
    b1, b2, B1, B2, B12 = (Z[k] for k in Z_NAMES)
    H, X1, X2, b, c, u = (Y[k] for k in Y_NAMES[:6])
    def prod(p, q):
        return [cv(p, q, m) for m in range(n + 1)]
    bx = [cv(b1, X2, m) + cv(b2, X1, m) for m in range(n + 1)]
    uB12 = prod(u, B12)
    bBcB = [cv(b, B2, m) + cv(c, B1, m) for m in range(n + 1)]
    SX, CX, TX = T["SX"], T["CX"], T["TX"]
    e1 = CX[n]/K - cv(SX, H, n) + M*bx[n] - 2*M*cv(CX, uB12, n)
    e2 = SX[n]/K + cv(CX, H, n) + M*cv(TX, bx, n) - M*cv(SX, bBcB, n)
    cXbX = [cv(c, X1, m) - cv(b, X2, m) for m in range(n + 1)]
    bB = [cv(b2, B1, m) - cv(b1, B2, m) for m in range(n + 1)]
    e3 = -M*cv(SX, cXbX, n) + M*cv(TX, bB, n) + (1 - 2*a)*cv(CX, B12, n)
    one_n = 1 if n == 0 else 0
    bb = cv(b1, b2, n); bc = cv(b, c, n); uu = cv(u, u, n)
    inner = [a*(a - 1)*(1 if m == 0 else 0) + M*M*(cv(u, u, m) + (1 if m == 0 else 0)) for m in range(n + 1)]
    bcuu = [cv(b, c, m) - cv(u, u, m) for m in range(n + 1)]
    e4 = (-4*a*(a - 1)*one_n - M*M*(4*one_n - 8*bb + bc + 3*uu)
          - 4*cv(T["COSX"], inner, n) + M*M*cv(T["COS2X"], bcuu, n))
    bcb = [cv(b1, c, m) - cv(b, b2, m) for m in range(n + 1)]
    e5 = (2*a - 1)*cv(CX, u, n) + M*cv(TX, bcb, n)
    return [e1, e2, e3, e4, e5]


def ode_rhs_n(Y, Z, T, n, a, M):
    """Order-n coefficient of the right-hand sides of (23)-(28) and I' = -H."""
    cv = _conv
    b1, b2, B1, B2, B12 = (Z[k] for k in Z_NAMES)
    H, X1, X2, b, c, u = (Y[k] for k in Y_NAMES[:6])
    def pr(p, q):
        return [cv(p, q, m) for m in range(n + 1)]
    b2u, b1u = pr(b2, u), pr(b1, u)
    bb2cb1 = [cv(b, b2, m) + cv(c, b1, m) for m in range(n + 1)]
    return [
        -(M/2)*(cv(b, B2, n) + cv(c, B1, n) + 2*cv(u, B12, n)),
        -M*(cv(b, B12, n) + cv(u, B1, n)),
        -M*(cv(c, B12, n) + cv(u, B2, n)),
        -2*M*cv(T["CSC_SX"], b1u, n) - a*cv(T["CSC_1PC"], b, n),
        -2*M*cv(T["CSC_SX"], b2u, n) - (1 - a)*cv(T["CSC_1PC"], c, n),
        -(M/2)*cv(T["SECX"], bb2cb1, n) + 0.5*cv(T["TX"], u, n),
        -H[n],
    ]


def _alg_jacobian(Y, z, T0, a, M, K, B):
    """d(eqs)/dZ at order 0. The equations are at most quadratic in Z, so the
    central difference is exact up to rounding for any step."""
    scale = max(B.abs(v) for v in z) or 1
    cols = []
    for j in range(5):
        h = (B.abs(z[j]) or scale)*(1e-3 if B.kind == "double" else B.mp.mpf(10)**(-B.mp.dps//3))
        zp = z[:]; zp[j] += h; zm = z[:]; zm[j] -= h
        rp = alg_residual_n(Y, {k: [zp[i]] for i, k in enumerate(Z_NAMES)}, T0, 0, a, M, K)
        rm = alg_residual_n(Y, {k: [zm[i]] for i, k in enumerate(Z_NAMES)}, T0, 0, a, M, K)
        cols.append([(rp[i] - rm[i])/(2*h) for i in range(5)])
    return [[cols[j][i] for j in range(5)] for i in range(5)]


def solve_Z0(Y0, Z_guess, T0, a, M, K, B, iters=60):
    """Newton for the order-0 algebraic unknowns at a new expansion point.
    Returns (Z0, A0) with A0 the Jacobian AT THE CONVERGED POINT -- it is needed
    by the recursion even when the guess is already converged."""
    Y = {k: [Y0[k]] for k in Y_NAMES}
    z = [Z_guess[k] for k in Z_NAMES]
    tol = 1e-14 if B.kind == "double" else B.mp.mpf(10)**(-B.mp.dps + 5)
    for it in range(iters):
        r = alg_residual_n(Y, {k: [z[i]] for i, k in enumerate(Z_NAMES)}, T0, 0, a, M, K)
        rel = max(B.abs(v) for v in r)
        if rel < tol:
            break
        J = _alg_jacobian(Y, z, T0, a, M, K, B)
        dz = B.solve(J, [-v for v in r])
        z = [z[i] + dz[i] for i in range(5)]
    else:
        raise RuntimeError(f"order-0 algebraic Newton did not converge (residual {rel})")
    return dict(zip(Z_NAMES, z)), _alg_jacobian(Y, z, T0, a, M, K, B)


def taylor_expand(Y0, Z0, A0, x0, N, a, M, B):
    """Taylor coefficients of all 12 functions at x0, to order N."""
    zero = B.c(0)
    T = trig_at(x0, N, B)
    K = 8*B.pi*a*(1 - a)
    Y = {k: [Y0[k]] + [zero]*N for k in Y_NAMES}
    Z = {k: [Z0[k]] + [zero]*N for k in Z_NAMES}
    for n in range(N):
        if n > 0:
            r = alg_residual_n(Y, Z, T, n, a, M, K)          # with Z_n = 0 still
            zn = B.solve(A0, [-v for v in r])
            for i, k in enumerate(Z_NAMES):
                Z[k][n] = zn[i]
        rhs = ode_rhs_n(Y, Z, T, n, a, M)
        for i, k in enumerate(Y_NAMES):
            Y[k][n + 1] = rhs[i]/(n + 1)
    return Y, Z


def evaluate(series, h):
    out = {}
    for k, cf in series.items():
        acc = 0
        for coef in reversed(cf):
            acc = acc*h + coef
        out[k] = acc
    return out


def integrate(Y0, Z_guess, x_start, x_targets, a, M, N=30, B=None, safety=0.35, tol=None,
              verbose=False):
    """Step from x_start down through every x in x_targets. Returns {x: I(x)}."""
    B = B or Backend("double")
    tol = tol if tol is not None else (1e-15 if B.kind == "double" else B.mp.mpf(10)**(-B.mp.dps + 3))
    K = 8*B.pi*a*(1 - a)
    targets = sorted([B.c(x) if B.kind != "double" else x for x in x_targets], key=lambda v: -abs(v))
    x0 = x_start
    Y0 = dict(Y0)
    out = {}
    steps = 0
    Zg = dict(Z_guess)
    while targets:
        T0 = trig_at(x0, 0, B)
        Z0, A0 = solve_Z0(Y0, Zg, T0, a, M, K, B)
        Y, Z = taylor_expand(Y0, Z0, A0, x0, N, a, M, B)
        # radius from the decay of the tail coefficients of H and b
        est = []
        for k in ("H", "X1", "b"):
            cf = Y[k]
            mags = [B.abs(cf[n]) for n in range(N - 6, N + 1) if B.abs(cf[n]) > 0]
            ns = [n for n in range(N - 6, N + 1) if B.abs(cf[n]) > 0]
            for n, m in zip(ns, mags):
                est.append(float(m)**(-1.0/n) if m != 0 else float("inf"))
        r = min(est) if est else 1.0
        h = -safety*r
        tgt = targets[0]
        if (x0 + h).real < tgt.real if B.kind != "double" else x0 + h < tgt:
            h = tgt - x0
        # truncation check: last term relative to value
        lastterm = max(float(B.abs(Y[k][N]*h**N)) for k in ("H", "X1", "b", "I"))
        scale_ = max(float(B.abs(Y0[k])) for k in ("X1", "b")) + 1e-300
        if lastterm > float(tol)*scale_*10:
            h = h/2
        Yn = evaluate(Y, h)
        Zg = evaluate(Z, h)
        x0 = x0 + h
        Y0 = Yn
        steps += 1
        if verbose:
            print(f"   step {steps}: x = {complex(x0).real:.6f}  radius ~ {r:.3f}  h = {complex(h).real:.4f}")
        if abs(x0 - tgt) < 1e-12:
            out[targets.pop(0)] = Y0["I"]
        if steps > 400:
            raise RuntimeError("too many Taylor steps")
    return out, steps
