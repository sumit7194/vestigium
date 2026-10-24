"""B15b G6 (registered; design B15B_G6_DESIGN.md with the Bridge's review points; chord rule B15b-2 once registered).
Part 1: the REPLICA of hs_construct.manifold_arcs' bookkeeping. It has the same control flow, line for line, and calls
P and Pinv in the same order with the same arguments, so under pcache every call is a journal hit. It also records, for
every output polyline, the original parameter of each point and every DROP:
  - a point whose image is None at level j (it is absent from level j + 1 on);
  - a refinement midpoint whose orbit was lost before reaching level j (never inserted).
Both are recorded with drop level j.
A segment of the level-m polyline is a CHORD if a drop with level j < m has its parameter strictly between the
segment's endpoint parameters (B15b-2, rule 1). The replica's arcs must equal the constructor's arcs BIT FOR BIT; if
they do not, G6 is INCOMPLETE (B15b-2, rule 5).
"""
import numpy as np


def arcs_replica(P, Pinv, p, e, lam, forward=True, K=6, eps=1e-6, n0=40, dmax=0.01, maxpts=4000):
    """returns (out, meta): out exactly as manifold_arcs; meta[i] = dict(sign, k, ts) for out[i];
    plus drops = {sign: [(param, level)]}"""
    F = (lambda w: (P(w, 1) or (None,))[0]) if forward else Pinv
    out, meta, drops = [], [], {+1: [], -1: []}
    for sign in (+1, -1):
        ts = list(np.geomspace(eps, eps * abs(lam), n0))
        pts = [np.array(p) + sign * t * np.array(e) for t in ts]
        for k in range(K + 1):
            out.append((k * sign, np.array(pts))); meta.append(dict(sign=sign, k=k, ts=np.array(ts)))
            if k == K:
                break
            new_ts, new_pts = [], []
            imgs = [F(q) for q in pts]
            i = 0
            while i < len(ts):
                if imgs[i] is None:
                    drops[sign].append((ts[i], k))                  # exists at level k, no image: gone from k + 1
                    i += 1; continue
                new_ts.append(ts[i]); new_pts.append(imgs[i])
                if i + 1 < len(ts) and imgs[i + 1] is not None and np.linalg.norm(imgs[i + 1] - imgs[i]) > dmax \
                        and len(ts) < maxpts:
                    tm = np.sqrt(ts[i] * ts[i + 1])
                    pm = np.array(p) + sign * tm * np.array(e)
                    lost = None
                    for j in range(k):
                        pm = F(pm)
                        if pm is None: lost = j; break                # its orbit existed at levels 0..j only
                    if pm is not None:
                        ts.insert(i + 1, tm); pts.insert(i + 1, pm)
                        imgs.insert(i + 1, F(pm)); continue
                    drops[sign].append((tm, lost))
                i += 1
            ts, pts = new_ts, new_pts
    return out, meta, drops


def chord_mask(meta_i, drops):
    """boolean per segment of one polyline: True if the segment is a chord (B15b-2 rule 1)"""
    ts, k, d = meta_i["ts"], meta_i["k"], drops[meta_i["sign"]]
    dd = np.array([q for q, j in d if j < k]) if d else np.zeros(0)
    m = np.zeros(max(len(ts) - 1, 0), bool)
    if len(dd) == 0: return m
    lo, hi = np.minimum(ts[:-1], ts[1:]), np.maximum(ts[:-1], ts[1:])
    for q in dd:
        m |= (lo < q) & (q < hi)
    return m


def arcs_equal(a, b):
    """bit-for-bit equality of two arc lists [(k, array)]"""
    if len(a) != len(b): return False
    for (ka, A), (kb, B) in zip(a, b):
        if ka != kb or A.shape != B.shape or not np.array_equal(A, B): return False
    return True


# ---------------------------------------------------------------- Part 2: decision margins (B15B_G6_DESIGN.md D1-D8)
# Each function re-derives one constructor decision from logged data and returns its outcome, its margin in its own
# units, the error-normalised margin, and thin = (margin < 10 x the propagated error). They are pure functions of their
# inputs (tested on toys with known margins before any run data is used).
import mpmath

THIN_FACTOR = 10.0


def d1_newton(residuals, tol, e_map):
    """D1: find_periodic's test ||P(w) - w|| < tol per iteration. The error of the residual is e_map (the map error,
    as an envelope). Returns per-iteration records, plus tol_too_tight if tol < 10 e_map."""
    out = [dict(it=i, res=r, converged=bool(r < tol), margin=abs(r - tol), thin=bool(abs(r - tol) < THIN_FACTOR * e_map))
           for i, r in enumerate(residuals)]
    return dict(iterations=out, tol_too_tight=bool(tol < THIN_FACTOR * e_map))


def d2_saddle(D, dD):
    """D2: saddle_info on DP = D: real eigenvalues (|Im| <= 1e-12), |lam_u| > 1 + 1e-6, |lam_s| < 1 - 1e-6. Robust iff
    the same classification holds for every matrix in [D +- 10 dD] (mpmath interval eigenvalues of the 2x2)."""
    iv = mpmath.iv; iv.prec = 120
    M = [[iv.mpf([D[i][j] - THIN_FACTOR * dD[i][j], D[i][j] + THIN_FACTOR * dD[i][j]]) for j in range(2)] for i in range(2)]
    tr, det = M[0][0] + M[1][1], M[0][0] * M[1][1] - M[0][1] * M[1][0]
    disc = tr * tr - 4 * det
    real = disc.a > 0
    if not real:
        return dict(real_robust=False, robust=False, thin=True, disc=[float(disc.a), float(disc.b)])
    sq = iv.sqrt(disc); l1, l2 = (tr + sq) / 2, (tr - sq) / 2
    big, small = (l1, l2) if abs(float(l1.mid)) > abs(float(l2.mid)) else (l2, l1)
    ab_big = min(abs(big.a), abs(big.b)) if not (big.a <= 0 <= big.b) else mpmath.mpf(0)
    ab_small = max(abs(small.a), abs(small.b))
    ok_u, ok_s = ab_big > 1 + 1e-6, ab_small < 1 - 1e-6
    return dict(real_robust=True, robust=bool(ok_u and ok_s), thin=not bool(ok_u and ok_s),
                lam_u=[float(big.a), float(big.b)], lam_s=[float(small.a), float(small.b)])


def seg_decision(a, b, c, d, eU, eS):
    """D4 for one segment pair (U: a->b, S: c->d), exactly as hs_construct.crossings computes it, plus the error
    normalisation (the Bridge's point 1): dt = (eU/|r| + eS/|s|) / sin(angle), du likewise. eU, eS are the point errors of
    the two segments' endpoints. Returns None if the lines are parallel to the constructor's 1e-18 cut."""
    r, s = b - a, d - c
    den = r[0] * s[1] - r[1] * s[0]
    if abs(den) < 1e-18:
        return dict(parallel=True, strict=False, thin=True)
    t = ((c - a)[0] * s[1] - (c - a)[1] * s[0]) / den
    u = ((c - a)[0] * r[1] - (c - a)[1] * r[0]) / den
    nr, ns = float(np.linalg.norm(r)), float(np.linalg.norm(s)); ang = abs(den) / (nr * ns)
    dt = (eU / nr + eS / ns) / max(ang, 1e-300); du = dt
    strict = (0 <= t <= 1) and (0 <= u <= 1)
    edge = min(t, 1 - t, u, 1 - u)                                  # > 0 inside, < 0 outside (distance to the boundary)
    return dict(parallel=False, strict=bool(strict), t=float(t), u=float(u), angle=float(ang), dt=float(dt), edge=float(edge),
                thin=bool(abs(edge) < THIN_FACTOR * dt), near_miss=bool((not strict) and abs(edge) < THIN_FACTOR * dt))


def vertex_risk(U, S, j, eU, eS):
    """D4 (a)/(b): for S-segment j against the whole polyline U, compare the STRICT crossing count with the count over the
    parameter range extended by 10 dt. Extended >= 1 with strict 0 is a zero-count risk at a shared vertex or an arc end."""
    c, d = S[j], S[j + 1]; strict = ext = 0
    for i in range(len(U) - 1):
        r = seg_decision(U[i], U[i + 1], c, d, eU, eS)
        if r.get("parallel"): continue
        strict += r["strict"]
        e = THIN_FACTOR * r["dt"]
        ext += (-e <= r["t"] <= 1 + e) and (-e <= r["u"] <= 1 + e)
    return dict(strict=strict, extended=ext, zero_count_risk=bool(ext >= 1 and strict == 0))


def d6_angle(angle, eU, lU, eS, lS, threshold=0.01):
    """D6: angle >= 0.01 (accepted). The angle error is (eU/lU + eS/lS), the endpoint error over the segment length."""
    da = eU / lU + eS / lS
    return dict(accepted=bool(angle >= threshold), margin=abs(angle - threshold), dangle=da, thin=bool(abs(angle - threshold) < THIN_FACTOR * da))


def d7_redflag(angle, theta_floor, dangle, dtheta):
    """D7: red flag angle > 10 theta_floor, with theta_floor's own error dtheta; the margin against the worst case."""
    m = abs(angle - 10 * theta_floor); e = dangle + 10 * dtheta
    return dict(red=bool(angle > 10 * theta_floor), margin=m, err=e, thin=bool(m < THIN_FACTOR * e))


def d8_connection(crossings):
    """D8 (with B15b-2): crossings = [dict(accepted, thin, on_chord)]. A connection is accepted only by a non-chord
    accept. Chord-only accepts give UNRESOLVED; any thin accept/reject near the line also makes the decision thin."""
    acc = [c for c in crossings if c["accepted"]]; nonchord = [c for c in acc if not c["on_chord"]]
    if nonchord:
        outcome = "CONNECTION"
    elif acc:
        outcome = "UNRESOLVED (chord-only accepts, B15b-2)"
    else:
        outcome = "NO CONNECTION"
    return dict(outcome=outcome, thin=any(c["thin"] for c in crossings), n_accept=len(acc), n_chord_accept=len(acc) - len(nonchord))
