"""
High-precision (mpmath) layer for the CHL solver.

Needed because b, c, u ~ e^{-pi M} against B1, B2 ~ e^{+pi M}: the system sheds
roughly pi M / ln(10) ~ 1.4 M decimal digits near x = pi (measured wall in double:
q ~ 3-4). Run under the repo's own sims/.venv, which has mpmath (pure-Python
backend, so this is slow and is used only where double demonstrably fails).

Start series at x = pi by MIXED-PRECISION ITERATIVE REFINEMENT: the Jacobian is
formed in double at the double iterate (exact for these quadratic equations up to
rounding); residuals are evaluated in mpmath; z <- z - J^{-1} r repeatedly. Each
pass gains ~ -log10(cond * 1e-16) digits. Convergence to the target precision is
REQUIRED, not assumed -- the call raises otherwise.
"""
import numpy as np
import mpmath as mpm

NAMES = ["H", "X1", "X2", "b", "c", "u", "beta1", "beta2", "B1", "B2", "B12"]


def start_data_mp(a, M):
    """chl_corner.start_data in mpmath, incl. the reflection form of (35)."""
    a, M = mpm.mpc(a), mpm.mpf(M)
    mu = mpm.sqrt(4*M*M - 1)
    def pairgamma(z0):
        return mpm.gamma(z0 + 0.5j*mu)*mpm.gamma(z0 - 0.5j*mu)
    def impsi(z0):
        return (mpm.digamma(z0 + 0.5j*mu) - mpm.digamma(z0 - 0.5j*mu))/2j
    def X1_pi(a):
        num = mpm.gamma(-a)*(mpm.cosh(mpm.pi*mu/2)*impsi(0.5 + a) - mpm.pi/2*mpm.sinh(mpm.pi*mu/2))
        return num*pairgamma(0.5 + a)/(mpm.power(2, 2*a + 1)*mpm.pi**2*mu*mpm.gamma(1 + a))
    def b_pi(a):
        return mpm.power(2, 1 - 2*a)*a*(1 - a)*pairgamma(0.5 + a)/(M*mpm.gamma(1 + a)**2)
    X1, X2, b, c = X1_pi(a), X1_pi(1 - a), b_pi(a), b_pi(1 - a)
    k = -mpm.sqrt((a*(a - 1) + M*M*(1 + b*c))/(4*M*M*b*c))
    K = 8*mpm.pi*a*(1 - a)
    # (81), (80) at pi -> B1, B2
    A11, A12, r1 = 2*k*c, -2*k*b, c*X1 - b*X2
    A21, A22, r2 = M*c, M*b, 1/K + 2*M*k*(b*X2 + c*X1)
    det = A11*A22 - A12*A21
    B1 = (r1*A22 - A12*r2)/det
    B2 = (A11*r2 - r1*A21)/det
    return dict(X1=X1, X2=X2, b=b, c=c, k=k, B1=B1, B2=B2,
                H1=M*(b*B2 + c*B1)/2, u1=M*k*b*c)


def _trig_eps(N):
    """sin(e/2), cos(e/2), tan(e/2), cos(e), cos(2e) as mp series lists."""
    def sc(scale):
        s = [mpm.mpf(0)]*(N + 1); c = [mpm.mpf(0)]*(N + 1)
        f = mpm.mpf(1)
        for n in range(N + 1):
            if n > 0:
                f = f*scale/n
            if n % 2 == 0:
                c[n] = f*(-1)**(n//2)
            else:
                s[n] = f*(-1)**((n - 1)//2)
        return s, c
    s, co = sc(mpm.mpf(1)/2)
    _, c1 = sc(mpm.mpf(1))
    _, c2 = sc(mpm.mpf(2))
    tan = _div(s, co)
    return dict(s=s, co=co, tan=tan, cos1=c1, cos2=c2)


def _mul(p, q):
    N = len(p) - 1
    return [mpm.fsum(p[j]*q[n - j] for j in range(n + 1)) for n in range(N + 1)]


def _div(p, q):
    N = len(p) - 1
    r = [mpm.mpf(0)]*(N + 1)
    for n in range(N + 1):
        r[n] = (p[n] - mpm.fsum(r[j]*q[n - j] for j in range(n)))/q[0]
    return r


def _der(p):
    N = len(p) - 1
    return [p[n + 1]*(n + 1) for n in range(N)] + [mpm.mpf(0)]


def _add(*ps):
    return [mpm.fsum(v) for v in zip(*ps)]


def _sc(k, p):
    return [k*v for v in p]


def residuals_mp(F, a, M, T):
    """Exactly chl_series.residuals, in mpmath lists."""
    H, X1, X2, b, c, u = (F[n] for n in ["H", "X1", "X2", "b", "c", "u"])
    b1, b2, B1, B2, B12 = (F[n] for n in ["beta1", "beta2", "B1", "B2", "B12"])
    s, co, tan = T["s"], T["co"], T["tan"]
    N = len(H) - 1
    one = [mpm.mpf(1)] + [mpm.mpf(0)]*N
    K = 8*mpm.pi*a*(1 - a)
    m = _mul
    bx = _add(m(b1, X2), m(b2, X1))
    st = m(s, tan)
    ss, sco = m(s, s), m(s, co)
    uu = m(u, u)
    bc = m(b, c)
    return [
        _add(_der(H), _sc(-M/2, _add(m(b, B2), m(c, B1), _sc(2, m(u, B12))))),
        _add(_der(X1), _sc(-M, _add(m(b, B12), m(u, B1)))),
        _add(_der(X2), _sc(-M, _add(m(c, B12), m(u, B2)))),
        _add(m(s, _der(c)), _sc(-M, m(b2, u)), _sc(-(1 - a), m(c, st))),
        _add(m(s, _der(b)), _sc(-M, m(b1, u)), _sc(-a, m(b, st))),
        _add(m(s, _der(u)), _sc(-M/2, _add(m(b, b2), m(c, b1))), _sc(mpm.mpf(1)/2, m(u, co))),
        _add(_sc(1/K, s), _sc(-1, m(co, H)), _sc(M, bx), _sc(-2*M, m(s, m(u, B12)))),
        _add(_sc(1/K, sco), m(ss, H), _sc(M, m(co, bx)), _sc(-M, m(sco, _add(m(b, B2), m(c, B1))))),
        _add(_sc(-M, m(sco, _add(m(c, X1), _sc(-1, m(b, X2))))),
             _sc(M, m(co, _add(m(b2, B1), _sc(-1, m(b1, B2))))),
             _sc(1 - 2*a, m(ss, B12))),
        _add(_sc(-4*a*(a - 1) - 4*M*M, one), _sc(8*M*M, m(b1, b2)), _sc(-M*M, bc), _sc(-3*M*M, uu),
             _sc(4, m(T["cos1"], _add(_sc(a*(a - 1), one), _sc(M*M, _add(uu, one))))),
             _sc(M*M, m(T["cos2"], _add(bc, _sc(-1, uu))))),
        _add(_sc(2*a - 1, m(u, ss)), _sc(M, m(co, _add(m(b1, c), _sc(-1, m(b, b2)))))),
    ]


def refine_series(Gd, info, a, M, dps, max_passes=40, verbose=False):
    """Iterative refinement of the double series Gd to `dps` digits.
    `info` must carry the double Jacobian (solve_series(..., want_jacobian=True))."""
    mpm.mp.dps = dps
    a, M = mpm.mpc(a), mpm.mpf(M)
    N = len(Gd["H"]) - 1
    sd = start_data_mp(a, M)
    T = _trig_eps(N)
    F = {n: [mpm.mpc(complex(v)) for v in Gd[n]] for n in NAMES}
    for n, v in dict(H=0, X1=sd["X1"], X2=sd["X2"], b=sd["b"], c=sd["c"], u=0).items():
        F[n][0] = mpm.mpc(v)
    J, colscale, idx = info["J"], info["colscale"], info["idx"]
    Jn = J*colscale
    target = mpm.mpf(10)**(-dps + 8)
    scale = None
    for p in range(max_passes):
        R = residuals_mp(F, a, M, T)
        r = [R[i][j] for i in range(len(R)) for j in range(N)]
        mag = max(abs(v) for v in r)
        if scale is None:
            scale = max(1, max(abs(F[n][j]) for n in NAMES for j in range(N + 1)
                               if n in ("B1", "B2")) * max(abs(F[n][j]) for n in ("b", "c") for j in range(1)))
        if verbose:
            print(f"   refine pass {p}: max|res| = {mpm.nstr(mag, 3)}")
        if mag < target*scale:
            return F, dict(residual=mag, passes=p)
        rd = np.array([complex(v) for v in r])
        dz, *_ = np.linalg.lstsq(Jn, -rd, rcond=None)
        dz = dz*colscale
        for (n, j), v in zip(idx, dz):
            F[n][j] += mpm.mpc(complex(v))
    raise RuntimeError(f"mp refinement did not reach 1e-{dps-8} at a={a}, M={M} "
                       f"(residual {mpm.nstr(mag, 3)})")


def evaluate_mp(F, eps):
    out = {}
    for k, cf in F.items():
        acc = mpm.mpc(0)
        for coef in reversed(cf):
            acc = acc*eps + coef
        out[k] = acc
    return out


# =============================================================================
# Block-triangular solve of the start series (no continuation, no double Jacobian)
# =============================================================================
# The start-series Jacobian is block lower-triangular in the orders. A maximum
# bipartite matching of equations to unknowns plus the strongly connected
# components of the induced graph, in topological order, turn the whole solve
# into a SEQUENCE OF SMALL BLOCKS (<= 6 unknowns at N = 16). Low-order blocks
# are nonlinear and are seeded from the closed-form start data (which is where
# the beta branch is chosen); every higher block is linear in its own unknowns.
# Equations left unmatched are REDUNDANT: they must vanish on their own once all
# blocks are solved, and are checked -- a free consistency test.

def btf_structure(N, cache_dir=None):
    """Blocks (row lists, col lists) in solve order, from the sparsity of a
    double Jacobian at a GENERIC complex point (no accidental zeros)."""
    import json, os
    cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "chl_btf_cache")
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"btf_N{N}.json")
    if os.path.exists(path):
        with open(path) as fh:
            d = json.load(fh)
        return d["blocks"], [tuple(x) for x in d["idx"]], d["unmatched_rows"], d["free_cols"]
    import chl_corner as cc, chl_series as cs
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import maximum_bipartite_matching, connected_components
    a, M = 0.5 - 0.37j, float(np.sqrt(0.25 + 1.3**2))
    g = cs.continue_in_t(0.37, M, N=N, keep=[0.37])[0.37]
    _, info = cs.solve_series(a, M, cc.start_data(a, M), N=N, guess=g, want_jacobian=True)
    J = info["J"]*info["colscale"]; idx = info["idx"]
    pat = (np.abs(J) > 1e-9*np.max(np.abs(J))).astype(int)
    nr, nc = pat.shape
    match = maximum_bipartite_matching(csr_matrix(pat), perm_type="column")
    col2row = {int(c): r for r, c in enumerate(match) if c >= 0}
    rows, cols = np.nonzero(pat)
    src, dst = [], []
    for r, c in zip(rows, cols):
        if int(c) in col2row and col2row[int(c)] != r:
            src.append(col2row[int(c)]); dst.append(int(r))
    G = csr_matrix((np.ones(len(src)), (src, dst)), shape=(nr, nr))
    ncomp, lab = connected_components(G, directed=True, connection="strong")
    # topological order of the condensation
    succ = {i: set() for i in range(ncomp)}
    indeg = [0]*ncomp
    for s_, d_ in zip(src, dst):
        ls, ld = lab[s_], lab[d_]
        if ls != ld and ld not in succ[ls]:
            succ[ls].add(ld); indeg[ld] += 1
    order, ready = [], [i for i in range(ncomp) if indeg[i] == 0]
    while ready:
        i = ready.pop(); order.append(i)
        for j in succ[i]:
            indeg[j] -= 1
            if indeg[j] == 0:
                ready.append(j)
    if len(order) != ncomp:
        raise RuntimeError("condensation is not a DAG")
    blocks = []
    for comp in order:
        rws = [r for r in range(nr) if lab[r] == comp and match[r] >= 0]
        if rws:
            blocks.append(dict(rows=rws, cols=[int(match[r]) for r in rws]))
    unmatched_rows = [r for r in range(nr) if match[r] < 0]
    free_cols = sorted(set(range(nc)) - set(int(c) for c in match if c >= 0))
    with open(path, "w") as fh:
        json.dump(dict(blocks=blocks, idx=[list(x) for x in idx],
                       unmatched_rows=unmatched_rows, free_cols=free_cols), fh)
    return blocks, idx, unmatched_rows, free_cols


def _truncate(F, L):
    return {n: v[:L + 1] for n, v in F.items()}


def _trig_trunc(T, L):
    return {k: v[:L + 1] for k, v in T.items()}


def solve_series_btf(a, M, N, dps, verbose=False, max_newton=12):
    """Start series at x = pi in mpmath by block-triangular forward solve."""
    blocks, idx, unmatched_rows, free_cols = btf_structure(N)
    mpm.mp.dps = dps
    a, M = mpm.mpc(a), mpm.mpf(M)
    sd = start_data_mp(a, M)
    Tfull = _trig_eps(N)
    F = {n: [mpm.mpc(0)]*(N + 1) for n in NAMES}
    for n, v in dict(X1=sd["X1"], X2=sd["X2"], b=sd["b"], c=sd["c"]).items():
        F[n][0] = mpm.mpc(v)
    # closed-form seeds for the nonlinear low orders (beta branch chosen here)
    F["H"][1], F["u"][1] = sd["H1"], sd["u1"]
    F["beta1"][1], F["beta2"][1] = sd["k"]*sd["b"], sd["k"]*sd["c"]
    F["B1"][0], F["B2"][0] = sd["B1"], sd["B2"]
    tol = mpm.mpf(10)**(-dps + 10)
    worst = mpm.mpf(0)
    for bi, blk in enumerate(blocks):
        rows, cols = blk["rows"], blk["cols"]
        L = max(r % N for r in rows) + 2
        L = min(L, N)
        T = _trig_trunc(Tfull, L)
        def E(vals):
            for (n, j), v in zip((idx[c] for c in cols), vals):
                F[n][j] = v
            R = residuals_mp(_truncate(F, L), a, M, T)
            return [R[r // N][r % N] for r in rows]
        x = [F[idx[c][0]][idx[c][1]] for c in cols]
        for it in range(max_newton):
            r = E(x)
            mag = max(abs(v) for v in r)
            scale = max([abs(v) for v in x] + [mpm.mpf(1)])
            if mag <= tol*scale:
                break
            n = len(x)
            Jb = [[mpm.mpc(0)]*n for _ in range(n)]
            for j in range(n):
                h = (abs(x[j]) if x[j] != 0 else scale)*mpm.mpf(10)**(-dps//4)
                xp = x[:]; xp[j] += h; xm = x[:]; xm[j] -= h
                rp, rm = E(xp), E(xm)
                for i in range(n):
                    Jb[i][j] = (rp[i] - rm[i])/(2*h)
            dx = mpm.lu_solve(mpm.matrix(Jb), mpm.matrix([-v for v in r]))
            x = [x[i] + dx[i] for i in range(n)]
        else:
            raise RuntimeError(f"block {bi} ({[idx[c] for c in cols]}) did not converge: {mpm.nstr(mag, 3)}")
        E(x)
        worst = max(worst, mag)
    # redundant equations must vanish on their own
    R = residuals_mp(F, a, M, Tfull)
    red = max((abs(R[r // N][r % N]) for r in unmatched_rows if r % N < N - 2), default=mpm.mpf(0))
    return F, dict(worst_block_residual=worst, redundant_residual=red,
                   n_blocks=len(blocks), free=[idx[c] for c in free_cols])
