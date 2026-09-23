"""
Numerical monodromy -- the Morales-Ramis tool's route that shares no code path
with Kovacic (PREREG_morales_ramis_tool.md, 59c4ae3).

For a FUCHSIAN y'' = r(z) y (every pole of order <= 2, order at infinity >= 2),
Schlesinger's theorem: the differential Galois group is the Zariski closure of
the monodromy group. So G0 can be read, independently of Kovacic, from monodromy
generators computed by integrating around each finite singular point from a
common base point.

Group classification of <M_1..M_k> in SL(2, C), in this order:
  finite         BFS closure of the group terminates           -> G0 = {1}, abelian
  reducible      common eigenvector v; diagonal characters l_j:
                   all roots of unity (finite image)            -> G0 unipotent, abelian
                   a second common eigenvector (diagonalisable)  -> G0 torus, abelian
                   otherwise                                     -> G0 full Borel, NON-abelian
  imprimitive    a pair of lines preserved as a set              -> G0 torus, abelian
  otherwise      irreducible, primitive, infinite                -> G = SL(2), NON-abelian
Numerical, so it CORROBORATES; it is not the proof. det M = 1 is an accuracy check.
"""
import cmath
import itertools
import math
import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp


def is_fuchsian(r, z):
    import mr_kovacic as K
    R = K.RationalR(r, z)
    return (not R.zero and all(m <= 2 for m in R.poles.values()) and R.ord_inf >= 2), R


def _transport(rf, Y0, path, rtol=1e-12, atol=1e-14):
    """Carry the fundamental matrix along z(s), s in [0, 1]; path returns (z, dz/ds)."""
    def f(s, v):
        zz, dz = path(s)
        y, yp = v[0:2], v[2:4]
        return np.concatenate([yp*dz, rf(zz)*y*dz])
    v0 = np.array([Y0[0, 0], Y0[0, 1], Y0[1, 0], Y0[1, 1]], dtype=complex)
    sol = solve_ivp(f, [0.0, 1.0], v0, method="DOP853", rtol=rtol, atol=atol)
    if not sol.success:
        raise RuntimeError(sol.message)
    v = sol.y[:, -1]
    return np.array([[v[0], v[1]], [v[2], v[3]]])


def monodromy_generators(r, z, base=None, rho_frac=0.3, seed=1):
    ok, R = is_fuchsian(r, z)
    if not ok:
        return None, "not Fuchsian: monodromy route not applicable"
    rf = sp.lambdify(z, sp.sympify(r), "numpy")
    cs = [complex(sp.N(c, 30)) for c in R.poles]
    if not cs:
        return [], "no finite singular points"
    rng = np.random.default_rng(seed)
    dmin = min((abs(a - b) for a, b in itertools.combinations(cs, 2)), default=1.0)
    rho = {c: rho_frac*min([abs(c - d) for d in cs if d != c] + [1.0]) for c in cs}
    span = max(abs(c) for c in cs) + 1.0

    def clear(p, q, avoid, margin):
        for d in cs:
            if d == avoid:
                continue
            t = np.clip(((d - p)*np.conj(q - p)).real/abs(q - p)**2, 0, 1)
            if abs(p + t*(q - p) - d) < margin*rho[d]/rho_frac*0.5:
                return False
        return True
    for _ in range(200):
        z0 = base if base is not None else complex(rng.uniform(-span, span), rng.uniform(0.3, span))
        pts = {c: c + rho[c]*(z0 - c)/abs(z0 - c) for c in cs}
        if all(clear(z0, pts[c], c, 1.0) for c in cs) and all(abs(z0 - c) > 2*rho[c] for c in cs):
            break
        base = None
    else:
        raise RuntimeError("no clean base point found")
    gens = []
    for c in cs:
        p = pts[c]
        phi0 = cmath.phase(p - c)
        seg_out = lambda s, a=z0, b=p: (a + s*(b - a), b - a)
        circ = lambda s, c=c, rr=rho[c], ph=phi0: (c + rr*cmath.exp(1j*(ph + 2*math.pi*s)),
                                                   2j*math.pi*rr*cmath.exp(1j*(ph + 2*math.pi*s)))
        seg_in = lambda s, a=p, b=z0: (a + s*(b - a), b - a)
        Y = np.eye(2, dtype=complex)
        for path in (seg_out, circ, seg_in):
            Y = _transport(rf, Y, path)
        gens.append((c, Y))
    return gens, f"base point {z0:.4f}"


def _parallel(u, v, tol):
    return abs(u[0]*v[1] - u[1]*v[0]) < tol*max(1.0, np.linalg.norm(u)*np.linalg.norm(v))


def _trace_is_root_of_unity(M, tol=1e-9, qmax=1000):
    """Is the character of M (its eigenvalue pair l, 1/l) a root of unity?
    Tested on the TRACE, tr M = 2 cos(2 pi p/q), which is accurate to ~eps.
    Eigenvalues of a defective (Jordan-block) matrix are only accurate to
    ~sqrt(eps) ~ 3e-7, so an |l| = 1 test rejected a true -1 in the first version --
    and Jordan-block monodromy (log terms) is exactly what integrable NVEs produce."""
    t = complex(np.trace(M))
    if abs(t.imag) > tol or abs(t.real) > 2 + tol:
        return False
    x = math.acos(max(-1.0, min(1.0, t.real/2)))/(2*math.pi)
    from fractions import Fraction
    f = Fraction(x).limit_denominator(qmax)
    return abs(2*math.cos(2*math.pi*float(f)) - t.real) < 1e-7


def classify(gens, tol=1e-6, max_elems=600):
    Ms = [M for _, M in gens]
    dets = [abs(np.linalg.det(M) - 1) for M in Ms]
    info = dict(det_err=max(dets) if dets else 0.0)
    if not Ms:
        return "trivial", True, info
    # finite?
    elems = [np.eye(2, dtype=complex)]
    frontier = list(elems)
    closed = False
    while frontier and len(elems) < max_elems:
        new = []
        for A in frontier:
            for M in Ms + [np.linalg.inv(M) for M in Ms]:
                B = A @ M
                if not any(np.max(np.abs(B - E)) < 1e-6*max(1, np.max(np.abs(E))) for E in elems):
                    elems.append(B); new.append(B)
        frontier = new
        if not new:
            closed = True
    if closed:
        info["order"] = len(elems)
        return "finite", True, info
    # reducible? a common eigenvector
    nonscalar = [M for M in Ms if np.max(np.abs(M - M[0, 0]*np.eye(2))) > tol]
    if not nonscalar:
        return "scalar", True, info
    w, V = np.linalg.eig(nonscalar[0])
    common = [V[:, i] for i in range(2) if all(_parallel(M @ V[:, i], V[:, i], 1e-6) for M in Ms)]
    if common:
        v = common[0]
        lams = []
        for M in Ms:
            Mv = M @ v
            k = np.argmax(np.abs(v))
            lams.append(Mv[k]/v[k])
        info["characters"] = lams
        if len(common) == 2 and not _parallel(common[0], common[1], 1e-6):
            return "reducible-diagonalisable", True, info
        if all(_trace_is_root_of_unity(M) for M in Ms):
            return "reducible-finite-characters", True, info
        return "reducible-full-Borel", False, info
    # imprimitive? a pair of lines preserved as a set
    for M in Ms:
        w, V = np.linalg.eig(M)
        if abs(w[0] - w[1]) < 1e-8:
            continue
        e1, e2 = V[:, 0], V[:, 1]
        good = True
        for N in Ms:
            a, b = N @ e1, N @ e2
            keeps = _parallel(a, e1, 1e-6) and _parallel(b, e2, 1e-6)
            swaps = _parallel(a, e2, 1e-6) and _parallel(b, e1, 1e-6)
            if not (keeps or swaps):
                good = False; break
        if good:
            return "imprimitive", True, info
    # infinite irreducible primitive -> Zariski dense in SL(2)
    info["tr_commutator"] = [complex(np.trace(A @ B @ np.linalg.inv(A) @ np.linalg.inv(B)))
                             for A, B in itertools.combinations(Ms, 2)]
    return "SL2", False, info


def monodromy_verdict(r, z, **kw):
    import mr_kovacic as K
    try:
        gens, note = monodromy_generators(r, z, **kw)
    except K.Inconclusive as e:
        return "INCONCLUSIVE", f"outside scope: {e}", None
    if gens is None:
        return "NOT_APPLICABLE", note, None
    kind, abelian, info = classify(gens)
    return ("NO_OBSTRUCTION" if abelian else "OBSTRUCTION"), f"{kind} ({note})", info
