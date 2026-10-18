"""Non-rigorous h-set constructor tools (prereg §3.7 as amended by B14). Double precision is allowed here: seeds,
frames and widths are proposals; only hs_cover's MPFR certification counts.

System: Hénon–Heiles, H = (px²+py²)/2 + (x²+y²)/2 + x²y − y³/3 at E = 1/6, section Θ₁ = {x = 0, ẋ > 0}, coordinates
w = (y, py), px = +sqrt(1/3 − py² − y² + 2y³/3). P = first return; DP from the variational equations."""
import numpy as np
from scipy.integrate import solve_ivp

E = 1.0 / 6.0
SADDLES = [(0.0, 1.0), (np.sqrt(3) / 2, -0.5), (-np.sqrt(3) / 2, -0.5)]   # (x, y) of the escape saddles


def px_of(y, py):
    r = 2 * E - py * py - y * y + 2 * y ** 3 / 3
    return np.sqrt(r) if r > 0 else np.nan


def rhs(t, s):
    x, y, px, py = s[:4]
    f = [px, py, -x - 2 * x * y, -y - x * x + y * y]
    if len(s) == 4:
        return f
    J = np.array([[0, 0, 1, 0], [0, 0, 0, 1], [-1 - 2 * y, -2 * x, 0, 0], [-2 * x, -1 + 2 * y, 0, 0]])
    Phi = s[4:].reshape(4, 4)
    return np.concatenate([f, (J @ Phi).ravel()])


def _event(t, s):
    return s[0]
_event.direction = 1.0


def P(w, n=1, jac=False, tmax=60.0, rtol=1e-12, atol=1e-13):
    """n-th return to Θ₁ with ẋ > 0. Returns (w', T[, DP 2x2 in section coordinates]) or None if no return."""
    y, py = w
    px = px_of(y, py)
    if not np.isfinite(px):
        return None
    s = np.array([0.0, y, px, py] + (list(np.eye(4).ravel()) if jac else []))
    T = 0.0
    for _ in range(n):
        sol = solve_ivp(rhs, (0, tmax), s, method="DOP853", rtol=rtol, atol=atol, events=_event,
                        first_step=1e-6, max_step=0.5)
        ev = [t for t in sol.t_events[0] if t > 1e-6]
        if not ev:
            return None
        k = list(sol.t_events[0]).index(ev[0])
        s = sol.y_events[0][k].copy(); s[0] = 0.0; T += ev[0]
    w2 = np.array([s[1], s[3]])
    if not jac:
        return w2, T
    Phi = s[4:].reshape(4, 4)
    # section map Jacobian: initial perturbation (dy, dpy) with dpx from the energy constraint (dx = 0);
    # final: project out the flow direction so that x stays 0, then read (dy, dpy).
    y0, py0 = w; px0 = px_of(y0, py0)
    # px² = 2E − py² − y² + 2y³/3  =>  dpx/dy = (y² − y)/px,  dpx/dpy = −py/px
    D_in = np.array([[0, 0], [1, 0], [(y0 * y0 - y0) / px0, -py0 / px0], [0, 1]])
    V = Phi @ D_in                               # 4x2 variation at the return time
    f = np.array(rhs(0, s[:4]))
    V = V - np.outer(f, V[0] / f[0])             # slide along the flow to the section x = 0
    DP = np.array([V[1], V[3]])
    return w2, T, DP


def find_periodic(seed, n, iters=30, tol=1e-12):
    """Newton on P^n(w) − w; returns (w*, DP^n) or None."""
    w = np.array(seed, float)
    for _ in range(iters):
        r = P(w, n, jac=True)
        if r is None:
            return None
        w2, _, D = r
        F = w2 - w
        if np.linalg.norm(F) < tol:
            return w, D
        try:
            dw = np.linalg.solve(D - np.eye(2), -F)
        except np.linalg.LinAlgError:
            return None
        lam = 1.0
        while lam > 1e-3:
            wt = w + lam * dw
            if np.isfinite(px_of(*wt)):
                break
            lam /= 2
        w = w + lam * dw
    return None


def saddle_info(D):
    ev, V = np.linalg.eig(D)
    if np.iscomplexobj(ev) and np.any(np.abs(ev.imag) > 1e-12):
        return None
    ev = ev.real; V = V.real
    iu, is_ = (0, 1) if abs(ev[0]) > abs(ev[1]) else (1, 0)
    if not (abs(ev[iu]) > 1.0 + 1e-6 and abs(ev[is_]) < 1.0 - 1e-6):
        return None
    return dict(lam_u=ev[iu], lam_s=ev[is_], e_u=V[:, iu] / np.linalg.norm(V[:, iu]),
                e_s=V[:, is_] / np.linalg.norm(V[:, is_]))


# ---------------------------------------------------------------- inverse map and invariant-manifold arcs
def _rhs_back(t, s):
    return [-v for v in rhs(t, s)]


def _event_back(t, s):
    return s[0]
_event_back.direction = -1.0            # in reversed time x decreases through 0  <=>  forward-time crossing with xdot > 0


def Pinv(w, tmax=60.0, rtol=1e-12, atol=1e-13):
    """previous crossing of Θ₁ (ẋ > 0) in forward time, i.e. P^{-1}; None if none within tmax"""
    y, py = w
    px = px_of(y, py)
    if not np.isfinite(px):
        return None
    sol = solve_ivp(_rhs_back, (0, tmax), [0.0, y, px, py], method="DOP853", rtol=rtol, atol=atol,
                    events=_event_back, first_step=1e-6, max_step=0.5)
    ev = [i for i, t in enumerate(sol.t_events[0]) if t > 1e-6]
    if not ev:
        return None
    s = sol.y_events[0][ev[0]]
    return np.array([s[1], s[3]])


def manifold_arcs(p, e, lam, forward=True, K=6, eps=1e-6, n0=40, dmax=0.01, maxpts=4000):
    """Arcs of W^u(p) (forward, e = e_u, lam = lam_u) or W^s(p) (backward, e = e_s, lam = 1/lam_s): the image under
    F^k (F = P or P^{-1}) of the fundamental segment p + t e, t in [eps, eps*|lam|], k = 0..K, refined so consecutive
    points are within dmax. Returns a list of polylines [(k, array Nx2)]. Both branches (+e, -e) are traced."""
    F = (lambda w: (P(w, 1) or (None,))[0]) if forward else Pinv
    out = []
    for sign in (+1, -1):
        ts = list(np.geomspace(eps, eps * abs(lam), n0))
        pts = [np.array(p) + sign * t * np.array(e) for t in ts]
        for k in range(K + 1):
            out.append((k * sign, np.array(pts)))
            if k == K:
                break
            new_ts, new_pts = [], []
            imgs = [F(q) for q in pts]
            i = 0
            while i < len(ts):
                if imgs[i] is None:
                    i += 1; continue
                new_ts.append(ts[i]); new_pts.append(imgs[i])
                if i + 1 < len(ts) and imgs[i + 1] is not None and np.linalg.norm(imgs[i + 1] - imgs[i]) > dmax \
                        and len(ts) < maxpts:
                    tm = np.sqrt(ts[i] * ts[i + 1])                         # refine in the original parameter
                    pm = np.array(p) + sign * tm * np.array(e)
                    for _ in range(k):
                        pm = F(pm)
                        if pm is None: break
                    if pm is not None:
                        ts.insert(i + 1, tm); pts.insert(i + 1, pm)
                        imgs.insert(i + 1, F(pm)); continue
                i += 1
            ts, pts = new_ts, new_pts
    return out


def _seg_intersect(a, b, c, d):
    r, s = b - a, d - c
    den = r[0] * s[1] - r[1] * s[0]
    if abs(den) < 1e-18:
        return None
    t = ((c - a)[0] * s[1] - (c - a)[1] * s[0]) / den
    u = ((c - a)[0] * r[1] - (c - a)[1] * r[0]) / den
    if 0 <= t <= 1 and 0 <= u <= 1:
        ang = abs(den) / (np.linalg.norm(r) * np.linalg.norm(s))
        return a + t * r, ang
    return None


def crossings(arcs_u, arcs_s, min_angle=1e-3, skip_near=None):
    """transverse intersections of unstable and stable polylines (vectorised: each unstable segment against all stable
    segments of an arc at once); returns [(point, angle, k_u, k_s)]"""
    found = []
    for ku, U in arcs_u:
        if len(U) < 2: continue
        for ks, S in arcs_s:
            if len(S) < 2: continue
            if (U[:, 0].max() < S[:, 0].min() or S[:, 0].max() < U[:, 0].min() or
                    U[:, 1].max() < S[:, 1].min() or S[:, 1].max() < U[:, 1].min()): continue
            C, Dd = S[:-1], S[1:]; s_ = Dd - C; sn = np.linalg.norm(s_, axis=1)
            for i in range(len(U) - 1):
                a, b = U[i], U[i + 1]; r = b - a
                den = r[0] * s_[:, 1] - r[1] * s_[:, 0]
                ca = C - a
                with np.errstate(divide="ignore", invalid="ignore"):
                    t = (ca[:, 0] * s_[:, 1] - ca[:, 1] * s_[:, 0]) / den
                    u = (ca[:, 0] * r[1] - ca[:, 1] * r[0]) / den
                ok = (np.abs(den) > 1e-18) & (t >= 0) & (t <= 1) & (u >= 0) & (u <= 1)
                for j in np.nonzero(ok)[0]:
                    ang = abs(den[j]) / (np.linalg.norm(r) * sn[j])
                    if ang < min_angle: continue
                    pt = a + t[j] * r
                    if skip_near is not None and min(np.linalg.norm(pt - z) for z in skip_near) < 1e-3: continue
                    found.append((pt, ang, ku, ks))
    return found


# ---------------------------------------------------------------- homoclinic / heteroclinic point refinement
def _iter(F, w, k):
    for _ in range(k):
        w = F(w)
        if w is None: return None
    return w


def refine_connection(p, eu, q, es, ku, ks, guess, iters=30, tol=1e-13):
    """Solve P^{ku}(p + t eu) = P^{-ks}(q + tau es) for (t, tau) (signed), Newton with central differences.
    The initial (t, tau) come from pulling 'guess' back to the fundamental segments by nearest search."""
    Fw = lambda w: (P(w, 1) or (None,))[0]
    def eqs(v):
        a = _iter(Fw, np.asarray(p) + v[0] * np.asarray(eu), ku)
        b = _iter(Pinv, np.asarray(q) + v[1] * np.asarray(es), ks)
        return None if a is None or b is None else a - b
    best = None                                            # coarse initial guess for the two parameters
    for t in np.concatenate([np.geomspace(1e-4, 1e-4 * 7.3, 40), -np.geomspace(1e-4, 1e-4 * 7.3, 40)]):
        a = _iter(Fw, np.asarray(p) + t * np.asarray(eu), ku)
        if a is not None and (best is None or np.linalg.norm(a - guess) < best[0]): best = (np.linalg.norm(a - guess), t)
    best2 = None
    for tau in np.concatenate([np.geomspace(1e-4, 1e-4 * 7.3, 40), -np.geomspace(1e-4, 1e-4 * 7.3, 40)]):
        b = _iter(Pinv, np.asarray(q) + tau * np.asarray(es), ks)
        if b is not None and (best2 is None or np.linalg.norm(b - guess) < best2[0]): best2 = (np.linalg.norm(b - guess), tau)
    v = np.array([best[1], best2[1]])
    for _ in range(iters):
        r = eqs(v)
        if r is None: return None
        if np.linalg.norm(r) < tol: break
        J = np.zeros((2, 2))
        for i in range(2):
            h = 1e-9 * max(1.0, abs(v[i])); e = np.zeros(2); e[i] = h
            rp, rm = eqs(v + e), eqs(v - e)
            if rp is None or rm is None: return None
            J[:, i] = (rp - rm) / (2 * h)
        v = v - np.linalg.solve(J, r)
    r = eqs(v)
    if r is None or np.linalg.norm(r) > 1e-10: return None
    h = _iter(Fw, np.asarray(p) + v[0] * np.asarray(eu), ku)
    return dict(t=float(v[0]), tau=float(v[1]), h=h, residual=float(np.linalg.norm(r)))


def orbit(h, back, fwd):
    """[P^{-back}(h), ..., h, ..., P^{fwd}(h)]"""
    Fw = lambda w: (P(w, 1) or (None,))[0]
    pts = [np.asarray(h)]
    for _ in range(back): pts.insert(0, Pinv(pts[0]))
    for _ in range(fwd): pts.append(Fw(pts[-1]))
    return pts


# ---------------------------------------------------------------- chain construction (B14) and sampled pre-check
def tangent_fwd(p, e, t, k):
    """unit tangent of W^u at P^k(p + t e), by pushing e with DP along the orbit"""
    w = np.asarray(p) + t * np.asarray(e); v = np.asarray(e, float)
    for _ in range(k):
        w2, _, D = P(w, 1, jac=True); v = D @ v; v /= np.linalg.norm(v); w = w2
    return w, v


def tangent_back(q, e, tau, k):
    """unit tangent of W^s at P^{-k}(q + tau e): pull e back with DP^{-1} = (DP at the preimage)^{-1}"""
    w = np.asarray(q) + tau * np.asarray(e); v = np.asarray(e, float)
    for _ in range(k):
        wb = Pinv(w); _, _, D = P(wb, 1, jac=True); v = np.linalg.solve(D, v); v /= np.linalg.norm(v); w = wb
    return w, v


def frame_coords(w, c, U, S):
    """(u, s) of point w in the frame c + u U + s S"""
    return np.linalg.solve(np.column_stack([U, S]), np.asarray(w) - np.asarray(c))


def sampled_cover(src, tgt, n_edge=24, n_int=12):
    """non-rigorous check of N_src => N_tgt under P (Def. 2), sampling the true map.
    Returns margins: (u-gap of the edge images beyond +-1, s-max of the interior image when |u| <= 1) and orientation."""
    (c, U, S), (c2, U2, S2) = src, tgt
    left, right = [], []
    for s in np.linspace(-1, 1, n_edge):
        for side, acc in ((-1, left), (1, right)):
            r = P(np.asarray(c) + side * np.asarray(U) + s * np.asarray(S), 1)
            if r is None: return None
            acc.append(frame_coords(r[0], c2, U2, S2)[0])
    L, R = np.array(left), np.array(right)
    if L.max() < -1 and R.min() > 1: orient, gap = "LR", min(-1 - L.max(), R.min() - 1)
    elif R.max() < -1 and L.min() > 1: orient, gap = "RL", min(-1 - R.max(), L.min() - 1)
    else: return dict(ok=False, orient="none", u_gap=float(min(abs(L).min(), abs(R).min()) - 1))
    smax = 0.0
    for uu in np.linspace(-1, 1, n_int):
        for ss in np.linspace(-1, 1, n_int):
            r = P(np.asarray(c) + uu * np.asarray(U) + ss * np.asarray(S), 1)
            if r is None: return None
            u2, s2 = frame_coords(r[0], c2, U2, S2)
            if abs(u2) <= 1: smax = max(smax, abs(s2))
    return dict(ok=bool(gap > 0 and smax < 1), orient=orient, u_gap=float(gap), s_max=float(smax))


def _corners(N):
    c, U, S = (np.asarray(v) for v in N)
    return np.array([c + su * U + ss * S for su, ss in ((-1, -1), (1, -1), (1, 1), (-1, 1))])


def disjoint(N1, N2):
    """separating-axis test for two parallelograms (float; the exact rational test runs again before certification)"""
    P1, P2 = _corners(N1), _corners(N2)
    for poly in (P1, P2):
        for i in range(4):
            e = poly[(i + 1) % 4] - poly[i]; nrm = np.array([-e[1], e[0]])
            a, b = P1 @ nrm, P2 @ nrm
            if a.max() < b.min() or b.max() < a.min(): return True
    return False
