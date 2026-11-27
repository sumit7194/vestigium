"""Tier-1 independent re-check of the S2 decisions (PREREG A13). python-flint (Arb ball arithmetic), 256-bit.
Written FROM THE REGISTERED FORMULAS (A1, A6, A10-A12, the A11 lemma); it does NOT import or port s2_main's decision
code. Inputs: the committed specs (decimals -> exact rationals) and the v4 Tier-1 dumps (exact MPFR hex endpoints).
Written by Claude Opus 5.5 (Quantum), 2026-11-27. Its verdict counts only after the Bridge's non-author read.

MAPPING (registered inequality -> checker function):
  S2-1  Krawczyk for P(w) - w (A6; CKMJ Thm 30: Zr - r + Y < 0, Z < 1) ............ check_fp
  S2-2  A11 lemma: (H1) mu = a_min - |b| L > 1, |c| + |d| L <= L mu ; (H2) nu = |c|/L + |d| < 1 ;
        rho' = ||T^-1||_inf r_fp ; delta* = (delta - rho') / (kappa max(1, L)), kappa = |a|_max + |b| L ;
        the L, rho', delta* used downstream must be implied by these .......................... check_cone
  S2-3  half BVP (A1, A3, A11): X = (u, z_1..z_{m-1}); F_0 = P(c + u U + h S) - z_1, h in [-eta, eta],
        eta = rho' + L(|u| + rho') (A11 lemma), thin mean-value form (D_0 S)[-eta, eta];
        F_i = P(z_i) - z_{i+1}; F_{m-1} = p_x(P(z_{m-1})); DF with d/du = D_0 U + (D_0 S)[-L, L];
        Y = ||A F||, Z = ||I - A DF||; reach |u| + r + rho' <= delta* ........................ check_bvp
  S2-4  A1: v = D_{m-1}..D_0 U + [-L, L] D_{m-1}..D_0 S ; 0 notin v_x and 0 notin v_px (MN), 0 in v_x (Kerr) ... check_bvp
  (ii)  meeting system with phase row (A12.1) + K_r lemma: grad K_r . g sign-definite on the meeting hull .. check_meet
  (iii) p_sab and p_MN disjoint (A7(iii)) ............................................... check_disjoint
  coverage: every pass input box contains the set the registration requires ................ cover()
  finiteness: every dumped endpoint finite (NaN rule) ........................................ parse
Usage: python tier1_check.py [run|mustfail]"""
import os, re, sys, json, copy
from flint import arb, fmpq, ctx
ctx.prec = 256
HERE = os.path.dirname(os.path.abspath(__file__)); S2 = os.path.join(HERE, "s2"); V4 = os.path.join(HERE, "s2v4")


# ---- EXACT coverage (fmpq; arb ball containment rounds radii to 30-bit mags, too coarse for 128-bit endpoint slack)
def E(d, tag, nm, i=0, j=0): return d[(tag, nm, i, j)]                         # exact (lo, hi)
def covers(outer, lo, hi): return outer[0] <= lo and hi <= outer[1]
def affine_box(c, cols, ranges):
    """exact range of c + sum_k cols[k] * t_k, t_k in [lo_k, hi_k] (affine: extremes at endpoints, separably)"""
    lo = hi = c
    for a, (tl, th) in zip(cols, ranges):
        v1, v2 = a * tl, a * th; lo += min(v1, v2); hi += max(v1, v2)
    return lo, hi
def absq(x): return x if x >= 0 else -x


class CheckFail(Exception):
    pass


def q_dec(s):
    """decimal / rational / exponent string -> exact fmpq"""
    s = s.strip(); neg = s.startswith("-"); s = s.lstrip("+-")
    if "/" in s:
        n, d = s.split("/"); v = fmpq(int(n), int(d))
    else:
        ex = 0
        if "e" in s or "E" in s:
            s, e = re.split("[eE]", s); ex = int(e)
        if "." in s:
            a, b = s.split("."); v = fmpq(int(a + b) if (a + b) else 0, 10 ** len(b))
        else:
            v = fmpq(int(s))
        v = v * (fmpq(10) ** ex if ex >= 0 else fmpq(1, 10 ** (-ex)))
    return -v if neg else v


def q_hex(h):
    """MPFR %Ra hex float -> exact fmpq; NaN / inf -> CheckFail (the NaN rule)"""
    h = h.strip()
    if re.search(r"nan|inf", h, re.I): raise CheckFail("non-finite dump endpoint: " + h)
    neg = h.startswith("-"); h = h.lstrip("+-")
    m_ = re.fullmatch(r"0x([0-9a-fA-F]*)\.?([0-9a-fA-F]*)p([+-]?\d+)", h)
    if not m_: raise CheckFail("bad hex " + h)
    ip, fp, ex = m_.group(1) or "0", m_.group(2), int(m_.group(3))
    mant = int(ip + fp, 16) if (ip + fp) else 0; ex -= 4 * len(fp)
    v = fmpq(mant) * (fmpq(2) ** ex if ex >= 0 else fmpq(1, 2 ** (-ex)))
    return -v if neg else v


def iv(lo, hi):
    if lo > hi: raise CheckFail("inverted interval")
    return arb(lo).union(arb(hi))


def spec(fn):
    kv = {}
    for line in open(fn):
        if line.strip() and not line.startswith("#"):
            p = line.split(); kv[p[0]] = p[1:]
    return kv


_TEXT_MUT = None                                         # must-fail hook (m2): fn, text -> text, applied before parsing
def dump(fn):
    d = {}; txt = open(fn).read()
    if _TEXT_MUT: txt = _TEXT_MUT(fn, txt)
    for line in txt.splitlines():
        tag, nm, i, j, lo, hi = line.split()
        d[(tag, nm, int(i), int(j))] = (q_hex(lo), q_hex(hi))
    return d


def I(d, tag, nm, i=0, j=0):
    lo, hi = d[(tag, nm, i, j)]; return iv(lo, hi)


# ---- small rigorous linear algebra on lists of arb
def mv(M, v): return [sum((M[i][k] * v[k] for k in range(len(v))), arb(0)) for i in range(len(M))]
def mm(A, B): return [[sum((A[i][k] * B[k][j] for k in range(len(B))), arb(0)) for j in range(len(B[0]))] for i in range(len(A))]
def mag(x): return abs(x).upper()            # rigorous upper bound of |x| (an arf/arb upper endpoint)
def upper(x): return x.upper()
def lower(x): return x.lower()
def norm_inf_v(v):
    best = arb(0)
    for x in v:
        u = finite(abs(x)).upper()                 # exact endpoint comparison (no float keys)
        if u > best: best = u
    return best
def norm_inf_m(M):
    best = arb(0)
    for row in M:
        s = sum((abs(x) for x in row), arb(0))
        if s.upper() > best.upper(): best = s
    return best.upper()
def sym(r): return arb(0).union(arb(r)).union(arb(-r)) if not isinstance(r, arb) else arb(0).union(r.upper()).union(-r.upper())
def contains_box(outer, inner):
    return all(o.contains(i) for o, i in zip(outer, inner))
def finite(x):
    if not x.is_finite(): raise CheckFail("non-finite quantity in a decision")
    return x


def certainly_neg(x): finite(x); return x < 0
def certainly_lt(x, y): finite(x); finite(y); return x < y


def inv2(T):
    det = T[0][0] * T[1][1] - T[0][1] * T[1][0]
    if det.contains(0): raise CheckFail("frame singular")
    return [[T[1][1] / det, -T[0][1] / det], [-T[1][0] / det, T[0][0] / det]]


def krawczyk(Y, Z, r):
    v = Z * r - r + Y
    return dict(Y=float(Y.upper()), Z=float(Z.upper()), r=float(r.upper()), margin=float(v.upper()),
                ok=bool(certainly_lt(Z, arb(1)) and certainly_neg(v)))


# ---------------------------------------------------------------- S2-1
def check_fp(lab, d, sp, norm=norm_inf_v):
    w = [arb(q_dec(sp["w"][0])), arb(q_dec(sp["w"][1]))]
    A = [[arb(q_dec(sp["A"][2 * i + j])) for j in range(2)] for i in range(2)]
    rr = arb(E(d, "fp", "r")[1])                          # the exact r the passes covered
    # coverage: the point pass took w, the ball pass w +- r
    wq = [q_dec(sp["w"][0]), q_dec(sp["w"][1])]; rq = E(d, "fp", "r")[1]
    for k, wk in ((0, wq[0]), (2, wq[1])):
        if not covers(E(d, "fp_point", "X0", k), wk, wk): raise CheckFail(lab + " fp point box")
        if not covers(E(d, "fp_ball", "X0", k), wk - rq, wk + rq): raise CheckFail(lab + " fp ball box")
    F = [I(d, "fp_point", "P", 0) - w[0], I(d, "fp_point", "P", 1) - w[1]]
    DP = [[I(d, "fp_ball", "D", i, j) for j in range(2)] for i in range(2)]
    IminusA = [[(arb(1) if i == j else arb(0)) - sum((A[i][k] * (DP[k][j] - (arb(1) if k == j else arb(0))) for k in range(2)), arb(0)) for j in range(2)] for i in range(2)]
    res = krawczyk(arb(norm(mv(A, F))), arb(norm_inf_m(IminusA)), arb(rr))
    res["rho"] = rr; return res


# ---------------------------------------------------------------- S2-2 (A11 lemma)
def check_cone(lab, d, sp_cone, sp_bvp, rfp):
    c = [arb(q_dec(sp_cone["c"][0])), arb(q_dec(sp_cone["c"][1]))]
    T = [[arb(q_dec(sp_cone["T"][2 * i + j])) for j in range(2)] for i in range(2)]; Ti = inv2(T)
    delta = arb(q_dec(sp_cone["delta"][0])); rho = arb(q_dec(sp_cone["rho"][0]))
    if arb(rfp).upper() > rho.upper(): raise CheckFail(lab + " cone rho < certified fp radius")
    cq = [q_dec(v) for v in sp_cone["c"]]; Tq = [[q_dec(sp_cone["T"][2 * i + j]) for j in range(2)] for i in range(2)]; dq = q_dec(sp_cone["delta"][0])
    for i, k in ((0, 0), (1, 2)):
        lo, hi = affine_box(cq[i], [Tq[i][0], Tq[i][1]], [(-dq, dq), (-dq, dq)])
        if not covers(E(d, "cone_box", "X0", k), lo, hi): raise CheckFail(lab + " cone box coverage")
    DP = [[I(d, "cone_box", "D", i, j) for j in range(2)] for i in range(2)]
    M = mm(mm(Ti, DP), T)
    a, b, cc, dd = M[0][0], abs(M[0][1]), abs(M[1][0]), abs(M[1][1])
    L = arb(q_dec(sp_bvp["L"][0]))                       # the L the BVP actually uses must satisfy (H1), (H2)
    mu = a.lower() - b * L; nu = cc / L + dd
    h1 = bool(certainly_lt(arb(1), mu) and finite(cc + dd * L - L * mu).upper() <= 0)      # (H1), both parts required
    h2 = certainly_lt(nu, arb(1))
    rhop = arb(norm_inf_m(Ti)) * rho
    kappa = abs(a).upper() + b * L; mx = L if L.lower() > 1 else arb(1)
    dstar = (delta - rhop) / (kappa * mx)
    used_rhop, used_dstar = arb(q_dec(sp_bvp["rhop"][0])), arb(q_dec(sp_bvp["deltastar"][0]))
    cons = bool(used_rhop.lower() >= rhop.upper())       # the BVP's rho' must be conservative; its reach is re-checked with THIS delta*
    return dict(a_min=float(a.lower()), mu=float(mu.lower()), nu=float(nu.upper()), L=float(L.upper()), rhop=float(rhop.upper()),
                deltastar=float(dstar.lower()), H1=bool(h1), H2=bool(h2), consistent_with_bvp_spec=cons, ok=bool(h1 and h2 and cons), _dstar=dstar.lower())


# ---------------------------------------------------------------- S2-3 / S2-4
def check_bvp(lab, d, sp, norm=norm_inf_v, dstar_chk=None):
    m = int(sp["m"][0]); Dn = 2 * m - 1
    c = [arb(q_dec(v)) for v in sp["c"]]; T = [[arb(q_dec(sp["T"][2 * i + j])) for j in range(2)] for i in range(2)]
    U = [T[0][0], T[1][0]]; S_ = [T[0][1], T[1][1]]
    L = arb(q_dec(sp["L"][0])); rhop = arb(q_dec(sp["rhop"][0])); dstar = dstar_chk if dstar_chk is not None else arb(q_dec(sp["deltastar"][0]))
    ub = arb(q_dec(sp["ubar"][0])); z = [None] + [[arb(q_dec(sp["z"][2 * (i - 1)])), arb(q_dec(sp["z"][2 * (i - 1) + 1]))] for i in range(1, m)]
    A = [[arb(q_dec(sp["A"][i * Dn + j])) for j in range(Dn)] for i in range(Dn)]
    r = arb(E(d, "bvp", "r")[1]); R_ = r
    # reach (A11): |u| + r + rho' <= delta*
    if not certainly_lt(abs(ub) + R_ + rhop, dstar) and not ((abs(ub) + R_ + rhop).upper() <= dstar.lower()): raise CheckFail(lab + " reach")
    eta = rhop + L * (abs(ub) + rhop)
    w0 = [c[i] + U[i] * ub for i in range(2)]
    # coverage (exact rationals)
    cq = [q_dec(v) for v in sp["c"]]; Tq = [[q_dec(sp["T"][2 * i + j]) for j in range(2)] for i in range(2)]
    Uq, Sq = [Tq[0][0], Tq[1][0]], [Tq[0][1], Tq[1][1]]; ubq = q_dec(sp["ubar"][0]); Lq = q_dec(sp["L"][0]); rpq = q_dec(sp["rhop"][0])
    zq = [None] + [[q_dec(sp["z"][2 * (i - 1)]), q_dec(sp["z"][2 * (i - 1) + 1])] for i in range(1, m)]; rq = E(d, "bvp", "r")[1]
    for i, k in ((0, 0), (1, 2)):
        w = cq[i] + Uq[i] * ubq
        if not covers(E(d, "bvp_pt0", "X0", k), w, w): raise CheckFail(lab + " bvp pt0 box")
        hmax = rpq + Lq * (absq(ubq) + rq + rpq)                       # the eta tube over |u - ubar| <= r
        lo, hi = affine_box(cq[i], [Uq[i], Sq[i]], [(ubq - rq, ubq + rq), (-hmax, hmax)])
        if not covers(E(d, "bvp_ball0", "X0", k), lo, hi): raise CheckFail(lab + " bvp ball0 box (eta tube)")
    for i in range(1, m):
        for j, k in ((0, 0), (1, 2)):
            if not covers(E(d, "bvp_pt%d" % i, "X0", k), zq[i][j], zq[i][j]): raise CheckFail(lab + " bvp pt%d box" % i)
            if not covers(E(d, "bvp_ball%d" % i, "X0", k), zq[i][j] - rq, zq[i][j] + rq): raise CheckFail(lab + " bvp ball%d box" % i)
    P = [[I(d, "bvp_pt%d" % i, "P", 0), I(d, "bvp_pt%d" % i, "P", 1)] for i in range(m)]
    Dm = [[[I(d, "bvp_ball%d" % i, "D", a, b) for b in range(2)] for a in range(2)] for i in range(m)]
    F = [arb(0)] * Dn
    for i in range(m - 1): F[2 * i] = P[i][0] - z[i + 1][0]; F[2 * i + 1] = P[i][1] - z[i + 1][1]
    F[Dn - 1] = P[m - 1][1]
    DS0 = mv(Dm[0], S_); F[0] = F[0] + DS0[0] * sym(eta.upper()); F[1] = F[1] + DS0[1] * sym(eta.upper())
    DF = [[arb(0)] * Dn for _ in range(Dn)]
    DU0 = mv(Dm[0], U); DF[0][0] = DU0[0] + DS0[0] * sym(L.upper()); DF[1][0] = DU0[1] + DS0[1] * sym(L.upper())
    for i in range(m - 1):                          # equation i links z_i -> z_{i+1}
        cz = 1 + 2 * i                              # column block of z_{i+1}
        DF[2 * i][cz] = arb(-1); DF[2 * i + 1][cz + 1] = arb(-1)
    for i in range(1, m):                           # d(eq i)/d z_i = D_i  (eq m-1 is the p_x row only)
        cz = 1 + 2 * (i - 1)
        if i < m - 1:
            for a in range(2):
                for b in range(2): DF[2 * i + a][cz + b] = Dm[i][a][b]
        else:
            DF[Dn - 1][cz] = Dm[i][1][0]; DF[Dn - 1][cz + 1] = Dm[i][1][1]
    AD = mm(A, DF); IM = [[(arb(1) if i == j else arb(0)) - AD[i][j] for j in range(Dn)] for i in range(Dn)]
    res = krawczyk(arb(norm(mv(A, F))), arb(norm_inf_m(IM)), R_)
    vU, vS = U, S_
    for i in range(m): vU = mv(Dm[i], vU); vS = mv(Dm[i], vS)
    v = [vU[k] + vS[k] * sym(L.upper()) for k in range(2)]
    pe = mv(Dm[m - 1], [sym(r), sym(r)]); p = [P[m - 1][0] + pe[0], P[m - 1][1] + pe[1]]
    for x in v + p: finite(x)
    res.update(v_x=[float(v[0].lower()), float(v[0].upper())], v_px=[float(v[1].lower()), float(v[1].upper())],
               vx_contains0=bool(v[0].contains(0)), vpx_contains0=bool(v[1].contains(0)),
               p_x=[float(p[0].lower()), float(p[0].upper())], _p=p)
    return res


# ---------------------------------------------------------------- (ii)
def check_meet(d, sp, norm=norm_inf_v, dstar_chk=None):
    m = int(sp["m"][0]); Dn = 4 * m - 1; ob = 1 + 2 * (m - 1); rb = 2 * (m - 1); mr = 4 * (m - 1)
    c = [arb(q_dec(v)) for v in sp["c"]]; T = [[arb(q_dec(sp["T"][2 * i + j])) for j in range(2)] for i in range(2)]
    U = [T[0][0], T[1][0]]; S_ = [T[0][1], T[1][1]]
    L = arb(q_dec(sp["L"][0])); rhop = arb(q_dec(sp["rhop"][0])); dstar = dstar_chk if dstar_chk is not None else arb(q_dec(sp["deltastar"][0]))
    cb, cp = arb(q_dec(sp["c0"][0])), arb(q_dec(sp["cprime"][0])); xmid, xrad = arb(q_dec(sp["xmid"][0])), arb(q_dec(sp["xrad"][0]))
    g = [arb(q_dec(v)) for v in sp["g"]]
    z = [None] + [[arb(q_dec(sp["z"][2 * (i - 1)])), arb(q_dec(sp["z"][2 * (i - 1) + 1]))] for i in range(1, m)]
    zp = [None] + [[arb(q_dec(sp["zp"][2 * (i - 1)])), arb(q_dec(sp["zp"][2 * (i - 1) + 1]))] for i in range(1, m)]
    A = [[arb(q_dec(sp["A"][i * Dn + j])) for j in range(Dn)] for i in range(Dn)]
    r = arb(E(d, "meet", "r")[1]); R_ = r
    for u_ in (cb, cp):
        if not ((abs(u_) + R_ + rhop).upper() <= dstar.lower()): raise CheckFail("meet reach")
    eta, etap = rhop + L * (abs(cb) + rhop), rhop + L * (abs(cp) + rhop)
    cq = [q_dec(v) for v in sp["c"]]; Tq = [[q_dec(sp["T"][2 * i + j]) for j in range(2)] for i in range(2)]
    Uq, Sq = [Tq[0][0], Tq[1][0]], [Tq[0][1], Tq[1][1]]; Lq = q_dec(sp["L"][0]); rpq = q_dec(sp["rhop"][0]); rq = E(d, "meet", "r")[1]
    zq = [None] + [[q_dec(sp["z"][2 * (i - 1)]), q_dec(sp["z"][2 * (i - 1) + 1])] for i in range(1, m)]
    zpq = [None] + [[q_dec(sp["zp"][2 * (i - 1)]), q_dec(sp["zp"][2 * (i - 1) + 1])] for i in range(1, m)]
    for tagp, tagb, ctr in (("meet_pt0", "meet_ball0", q_dec(sp["c0"][0])), ("meet_ptp0", "meet_ballp0", q_dec(sp["cprime"][0]))):
        for i, k in ((0, 0), (1, 2)):
            w = cq[i] + Uq[i] * ctr
            if not covers(E(d, tagp, "X0", k), w, w): raise CheckFail("meet " + tagp + " box")
            hmax = rpq + Lq * (absq(ctr) + rq + rpq)
            lo, hi = affine_box(cq[i], [Uq[i], Sq[i]], [(ctr - rq, ctr + rq), (-hmax, hmax)])
            if not covers(E(d, tagb, "X0", k), lo, hi): raise CheckFail("meet " + tagb + " tube")
    for i in range(1, m):
        for tg, tb, zz in (("meet_pt%d" % i, "meet_ball%d" % i, zq[i]), ("meet_ptp%d" % i, "meet_ballp%d" % i, zpq[i])):
            for j, k in ((0, 0), (1, 2)):
                if not covers(E(d, tg, "X0", k), zz[j], zz[j]): raise CheckFail("meet " + tg + " box")
                if not covers(E(d, tb, "X0", k), zz[j] - rq, zz[j] + rq): raise CheckFail("meet " + tb + " box")
    P = [[I(d, "meet_pt%d" % i, "P", 0), I(d, "meet_pt%d" % i, "P", 1)] for i in range(m)]
    Pp = [[I(d, "meet_ptp%d" % i, "P", 0), I(d, "meet_ptp%d" % i, "P", 1)] for i in range(m)]
    Db = [[[I(d, "meet_ball%d" % i, "D", a, b) for b in range(2)] for a in range(2)] for i in range(m)]
    Dp = [[[I(d, "meet_ballp%d" % i, "D", a, b) for b in range(2)] for a in range(2)] for i in range(m)]
    F = [arb(0)] * Dn
    for i in range(m - 1):
        F[2 * i] = P[i][0] - z[i + 1][0]; F[2 * i + 1] = P[i][1] - z[i + 1][1]
        F[rb + 2 * i] = Pp[i][0] - zp[i + 1][0]; F[rb + 2 * i + 1] = Pp[i][1] - zp[i + 1][1]
    F[mr] = P[m - 1][0] - Pp[m - 1][0]; F[mr + 1] = P[m - 1][1] + Pp[m - 1][1]
    F[Dn - 1] = z[m - 1][0] - (xmid + sym(xrad.upper()))
    DS0, DSp = mv(Db[0], S_), mv(Dp[0], S_)
    F[0] += DS0[0] * sym(eta.upper()); F[1] += DS0[1] * sym(eta.upper()); F[rb] += DSp[0] * sym(etap.upper()); F[rb + 1] += DSp[1] * sym(etap.upper())
    DF = [[arb(0)] * Dn for _ in range(Dn)]
    DU0, DUp = mv(Db[0], U), mv(Dp[0], U)
    DF[0][0] = DU0[0] + DS0[0] * sym(L.upper()); DF[1][0] = DU0[1] + DS0[1] * sym(L.upper())
    DF[rb][Dn - 2] = DUp[0] + DSp[0] * sym(L.upper()); DF[rb + 1][Dn - 2] = DUp[1] + DSp[1] * sym(L.upper())
    for i in range(m - 1):
        cz, czp = 1 + 2 * i, ob + 2 * i
        DF[2 * i][cz] = arb(-1); DF[2 * i + 1][cz + 1] = arb(-1); DF[rb + 2 * i][czp] = arb(-1); DF[rb + 2 * i + 1][czp + 1] = arb(-1)
    for i in range(1, m - 1):
        cz, czp = 1 + 2 * (i - 1), ob + 2 * (i - 1)
        for a in range(2):
            for b in range(2): DF[2 * i + a][cz + b] = Db[i][a][b]; DF[rb + 2 * i + a][czp + b] = Dp[i][a][b]
    czl, czpl = 1 + 2 * (m - 2), ob + 2 * (m - 2)
    for a in range(2):
        for b in range(2):
            DF[mr + a][czl + b] = Db[m - 1][a][b]; DF[mr + a][czpl + b] = (-Dp[m - 1][a][b]) if a == 0 else Dp[m - 1][a][b]   # -R D', R = diag(1, -1)
    DF[mr][Dn - 1] = -g[0]; DF[mr + 1][Dn - 1] = -g[1]
    DF[Dn - 1][czl] = arb(1)
    AD = mm(A, DF); IMm = [[(arb(1) if i == j else arb(0)) - AD[i][j] for j in range(Dn)] for i in range(Dn)]
    res = krawczyk(arb(norm(mv(A, F))), arb(norm_inf_m(IMm)), R_)
    # K_r lemma on the meeting hull: y = R P'(z'_{m-1}) over the ball, plus [-r, r] g
    pe = mv(Dp[m - 1], [sym(r), sym(r)]); y = [Pp[m - 1][0] + pe[0], -(Pp[m - 1][1] + pe[1])]
    hull = [y[0] + g[0] * sym(r), y[1] + g[1] * sym(r)]
    gk = Kr_dx(*hull) * g[0] + Kr_dpx(*hull) * g[1]; finite(gk)
    res.update(gradK_g=[float(gk.lower()), float(gk.upper())], klemma=bool(not gk.contains(0)))
    return res


# K_r(x, p_x) = 1/2 [Delta p_r^2 - Pr^2/Delta + r^2], r = M + k x, p_r = p_x/k, Delta = r^2 - 2Mr + a^2,
# Pr = E (r^2 + a^2) - a L  (SETUP.md 1; the registered constants)
Mc, Ac, Kc = arb(5), arb(3), arb(4); Ec, Lc = arb(q_dec("0.93528150456799871854")), arb(q_dec("12.972532035607280691"))
def Kr_dx(x, px):
    r = Mc + Kc * x; pr = px / Kc; Dl = r * r - 2 * Mc * r + Ac * Ac; Pr = Ec * (r * r + Ac * Ac) - Ac * Lc
    dK_dr = ((2 * r - 2 * Mc) * pr * pr - (2 * Pr * (2 * Ec * r) * Dl - Pr * Pr * (2 * r - 2 * Mc)) / (Dl * Dl) + 2 * r) / 2
    return dK_dr * Kc
def Kr_dpx(x, px):
    r = Mc + Kc * x; Dl = r * r - 2 * Mc * r + Ac * Ac; return Dl * px / (Kc * Kc)


def check_disjoint(p1, p2):
    return bool(not p1[0].overlaps(p2[0]) or not p1[1].overlaps(p2[1]))


def run_all(mut=None, norm=norm_inf_v):
    out = {}
    for lab in ("mn", "kerr_i", "sab_iii"):
        dfp, dco, dbv = (dump(os.path.join(V4, lab, n + ".dump")) for n in ("fp", "cone", "bvp"))
        if mut: mut(lab, dfp, dco, dbv)
        spf, spc, spb = (spec(os.path.join(S2, lab, n + ".spec")) for n in ("fp", "cone", "bvp"))
        if spb["c"] != spf["w"] or spc["c"] != spf["w"]: raise CheckFail(lab + ": frame centre differs from the certified fp centre")
        f = check_fp(lab, dfp, spf, norm); co = check_cone(lab, dco, spc, spb, f["rho"]); b = check_bvp(lab, dbv, spb, norm, co.pop("_dstar"))
        out[lab] = dict(fp=f, cone=co, bvp={k: v for k, v in b.items() if k != "_p"}); out[lab]["_p"] = b["_p"]
    spm = spec(os.path.join(S2, "meet_ii", "meet.spec"))
    if spm["c"] != spec(os.path.join(S2, "kerr_i", "fp.spec"))["w"]: raise CheckFail("meet: frame centre differs from the certified Kerr fp centre")
    dm = dump(os.path.join(V4, "meet_ii", "meet.dump"))
    if mut: mut("meet", dm, None, None)
    ck = check_cone("kerr_i", dump(os.path.join(V4, "kerr_i", "cone.dump")), spec(os.path.join(S2, "kerr_i", "cone.spec")), spec(os.path.join(S2, "meet_ii", "meet.spec")), out["kerr_i"]["fp"]["rho"])
    out["meet_ii"] = check_meet(dm, spec(os.path.join(S2, "meet_ii", "meet.spec")), norm, ck["_dstar"]); out["meet_ii"]["cone_ok"] = ck["ok"]
    out["iii_disjoint"] = check_disjoint(out["mn"]["_p"], out["sab_iii"]["_p"])
    for lab in ("mn", "kerr_i", "sab_iii"): out[lab].pop("_p")
    mn, ke, sa, me = out["mn"], out["kerr_i"], out["sab_iii"], out["meet_ii"]
    out["VERDICT"] = dict(
        MN=bool(mn["fp"]["ok"] and mn["cone"]["ok"] and mn["bvp"]["ok"] and not mn["bvp"]["vx_contains0"] and not mn["bvp"]["vpx_contains0"]),
        control_i=bool(ke["fp"]["ok"] and ke["cone"]["ok"] and ke["bvp"]["ok"] and ke["bvp"]["vx_contains0"]),
        control_ii=bool(me["ok"] and me["klemma"] and me["cone_ok"]),
        control_iii=bool(sa["fp"]["ok"] and sa["cone"]["ok"] and sa["bvp"]["ok"] and out["iii_disjoint"]))
    return out


def mustfail():
    """A13 (m1)-(m5): each on an in-memory copy of the real dumps; report whether the checker FAILS (or changes)."""
    base = run_all(); rep = {}
    def m1(lab, a, b, c):                                   # one DP entry shifted by 10x its width
        if lab == "mn": k = ("bvp_ball3", "D", 0, 0); lo, hi = c[("bvp_ball3", "D", 0, 0)]; w = hi - lo; c[k] = (lo + 10 * w, hi + 10 * w)
    def m3(lab, a, b, c):                                   # a flipped sign in a v-chain matrix entry
        if lab == "mn": lo, hi = c[("bvp_ball4", "D", 1, 0)]; c[("bvp_ball4", "D", 1, 0)] = (-hi, -lo)
    def m5(lab, a, b, c):                                   # a pass input box shrunk below node +- r
        if lab == "mn": lo, hi = c[("bvp_ball5", "X0", 0, 0)]; mid = (lo + hi) / 2; c[("bvp_ball5", "X0", 0, 0)] = (mid - (hi - lo) / 8, mid + (hi - lo) / 8)
    def m1p(lab, a, b, c):                                  # POST-HOC supplement (not registered): a point image P(z_3) x-entry shifted by 2 r_bvp
        if lab == "mn": k = ("bvp_pt3", "P", 0, 0); lo, hi = c[k]; s_ = 2 * c[("bvp", "r", 0, 0)][1]; c[k] = (lo + s_, hi + s_)
    for nm, mut in (("m1_shift_DP", m1), ("m3_sign_flip", m3), ("m5_shrunk_box", m5), ("m1p_posthoc_shift_P_2r", m1p)):
        try:
            o = run_all(mut); rep[nm] = dict(MN=o["VERDICT"]["MN"], Y=o["mn"]["bvp"]["Y"], Z=o["mn"]["bvp"]["Z"], base_Y=base["mn"]["bvp"]["Y"], base_Z=base["mn"]["bvp"]["Z"],
                                             v_x=o["mn"]["bvp"]["v_x"], fired=(not o["VERDICT"]["MN"]))
        except CheckFail as e: rep[nm] = dict(fired=True, CheckFail=str(e))
    # (m2) NaN and +inf: one endpoint of a real dump FILE (MN bvp, a D entry) replaced as text, run through the full pipeline
    global _TEXT_MUT
    for nm, tok in (("m2_nan", "nan"), ("m2_inf", "inf"), ("m2_NAN_upper", "@NaN@"), ("m2_INF_upper", "@Inf@")):
        def tm(fn, txt, tok=tok):
            if not fn.endswith(os.path.join("mn", "bvp.dump")): return txt
            out = []; done = False
            for ln in txt.splitlines():
                p = ln.split()
                if not done and p[1] == "D": p[5] = tok; done = True
                out.append(" ".join(p))
            return "\n".join(out)
        _TEXT_MUT = tm
        try: o = run_all(); rep[nm] = dict(fired=(not o["VERDICT"]["MN"]), MN=o["VERDICT"]["MN"])
        except CheckFail as e: rep[nm] = dict(fired=True, CheckFail=str(e))
        finally: _TEXT_MUT = None
    # (m4) norm swap (1-norm for Y instead of the registered inf-norm): must change the verdict margin (A13 wording)
    o = run_all(norm=lambda v: sum((abs(x) for x in v), arb(0)).upper())
    rep["m4_norm_swap"] = dict(base_margin=base["mn"]["bvp"]["margin"], swapped_margin=o["mn"]["bvp"]["margin"], changed=(o["mn"]["bvp"]["margin"] != base["mn"]["bvp"]["margin"]), MN=o["VERDICT"]["MN"])
    return rep


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    try:
        res = run_all() if mode == "run" else mustfail()
    except CheckFail as e:
        res = dict(CHECKFAIL=str(e))
    print(json.dumps(res, indent=1, default=str))
    json.dump(res, open(os.path.join(HERE, "tier1_%s.json" % mode), "w"), indent=1, default=str)
