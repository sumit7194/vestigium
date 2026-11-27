"""MN transversal-homoclinic spike, stage S1 (float only; PREREG.md, registered e010d1d + a5f2054).
Usage: python s1.py gnorm | beta <value> | read
  gnorm      : gate G-norm (mine's H at beta = 0 and its central beta-difference against mel_gen.H0 / mel_gen.Hb)
  beta <b>   : the S1 measurement at one beta -> s1_beta_<b>.json (a per-beta checkpoint; existing files are not redone)
  read       : the S1 reading over all present beta files, against the registered criteria
Not rigorous: float64, DOP853 rtol = atol = 1e-13. Written by Claude Opus 5.5 (Quantum)."""
import sys, os, json, time, numpy as np, sympy as sp
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe"); sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/mn_melnikov")
import mn_s5_gate as G, mn_numerics as MNN

HERE = os.path.dirname(os.path.abspath(__file__))
M, A, K = 5, 3, 4.0                          # (M, a), k = sqrt(M^2 - a^2)
E = 0.93528150456799871854; L = 12.972532035607280691
UPS = 15.0122754941206972; L2 = -4.77482114974644e-5; L4 = -5.31274262510e-10
TARGET = 4 * UPS * abs(L2)                   # 2.8672e-3 (MELNIKOV.md 0.3 / 7)
XU = (16.0 - M) / K                          # 2.75
RT = dict(rtol=1e-13, atol=1e-13)
NS = 64; S0 = 1e-7
XPL = 1.5   # plunge guard: x < 1.5 is r < 11 (horizon r+ = 9 at x = 1; the loop lives in 2.75 <= x <= 10.63)


def flow(beta):
    return MNN.MNFlow(M, A, sp.Rational(beta).limit_denominator(10 ** 12) if beta else sp.Integer(0), sp.Float(E, 30), sp.Float(L, 30))


def Kr(x, px):
    r = M + K * x; pr = px / K; D = r * r - 2 * M * r + A * A; P = E * (r * r + A * A) - A * L
    return 0.5 * (D * pr * pr - P * P / D + r * r)


def gnorm():
    from flint import acb, ctx; ctx.prec = 128
    import mel_gen as MG
    def Hmine(beta):
        X, Y, gxx, gyy, V = G.mine(M, A, beta, sp.Float(E, 30), sp.Float(L, 30))
        PX, PY = sp.symbols("PXg PYg")                     # names chosen NOT to collide with mn_s5_gate's own symbols
        return sp.lambdify((X, Y, PX, PY), (gxx * PX ** 2 + gyy * PY ** 2) / 2 + V, "mpmath")
    import mpmath as mp; mp.mp.dps = 30
    h0, hp, hm = Hmine(0), Hmine(sp.Rational(1, 10 ** 6)), Hmine(sp.Rational(-1, 10 ** 6))
    rng = np.random.default_rng(1); rows = []; w0 = w1 = 0.0
    for i in range(8):
        x = 2.2 + 8 * rng.random(); y = -0.45 + 0.9 * rng.random(); px = rng.normal(); py = rng.normal()
        a0 = float(h0(x, y, px, py)); ab = float((hp(x, y, px, py) - hm(x, y, px, py)) / mp.mpf("2e-6"))
        m0 = float(MG.H0(acb(x), acb(y), acb(px * px), acb(py * py), acb(E), acb(L)).real.mid())
        mb = float(MG.Hb(acb(x), acb(y), acb(px * px), acb(py * py), acb(E), acb(L)).real.mid())
        r0 = abs(a0 - m0) / abs(m0); r1 = abs(ab - mb) / abs(mb); w0 = max(w0, r0); w1 = max(w1, r1)
        rows.append(dict(x=x, y=y, H0=[a0, m0], Hb=[ab, mb], rel=[r0, r1]))
    res = dict(PASS=bool(w0 <= 1e-6 and w1 <= 1e-6), worst_H0=w0, worst_Hb=w1, points=rows,
               note="central difference h = 1e-6 in beta; mel_gen at 128 bits")
    json.dump(res, open(os.path.join(HERE, "s1_gnorm.json"), "w"), indent=1); print(json.dumps({k: res[k] for k in ("PASS", "worst_H0", "worst_Hb")}))


def aug(f):
    """state (x, y, px, py, lambda): Hamiltonian flow in tau plus Mino time d lambda = d tau / Sigma"""
    def rhs(t, s):
        d = f._f(*s[:4]); r = M + K * s[0]; return [d[0], d[1], d[2], d[3], 1.0 / (r * r + A * A * s[1] * s[1])]
    return rhs


def lift(f, w):
    py = f.py_of(w[0], w[1]); return np.array([w[0], 0.0, w[1], py, 0.0])


def to_apo(f, w, sgn):
    """integrate from the section point w (forward if sgn = +1, backward if -1) to the first outer turning point (p_x = 0
    with x > 6); return (x_apo, Kr_apo, psi0), with psi0 = Upsilon * (Mino time from the nearest z = +z_m turning point
    BEFORE the apo in forward time). Backward runs continue past the apo to find that z_max."""
    rhs0 = aug(f); rhs = rhs0 if sgn > 0 else (lambda t, s: [-v for v in rhs0(t, s)])
    apo = lambda t, s: s[2] if s[0] > 6.0 else (1.0 if sgn > 0 else -1.0)
    apo.terminal = True; apo.direction = -1.0 if sgn > 0 else 1.0
    zmax = lambda t, s: s[3]; zmax.direction = -1.0 if sgn > 0 else 1.0     # p_y: + -> - at a y-maximum (forward time)
    zmax_t = lambda t, s: s[3] if s[1] > 0 else (-1.0 if sgn > 0 else 1.0)   # first y-maximum with y > 0
    zmax_t.direction = zmax.direction; zmax_t.terminal = True
    pl = lambda t, s: s[0] - XPL; pl.terminal = True
    sol = solve_ivp(rhs, (0, 20000), lift(f, w), method="DOP853", events=[apo, zmax, pl], **RT)
    if not sol.t_events[0].size: return None
    sa = sol.y_events[0][0]; lam_apo = sa[4]
    if sgn > 0:
        zs = [s for s in sol.y_events[1] if s[1] > 0 and s[4] < lam_apo]
        if not zs: return None
        lam_z = zs[-1][4]
    else:
        zmax.terminal = False
        s2 = solve_ivp(rhs, (0, 20000), sa, method="DOP853", events=[zmax_t, pl], **RT)
        zs = [s for s in s2.y_events[0] if s[1] > 0]
        if not zs: return None
        lam_z = zs[0][4]
    dl = abs(lam_apo - lam_z)
    return float(sa[0]), float(Kr(sa[0], sa[2])), float((UPS * dl) % (2 * np.pi))


def fixed_point(f):
    # Newton on P(w) - w with the terminal-event return Pstep (f.P integrates its whole tmax: too slow at beta != 0).
    w = np.array([XU, 0.0])
    for it in range(40):
        w2, T, J = Pstep(f, w)
        Fv = w2 - w
        if np.max(np.abs(Fv)) < 1e-13: break
        dw = np.linalg.solve(J - np.eye(2), Fv); lam = 1.0
        while np.max(np.abs(lam * dw)) > 0.05: lam /= 2          # damp large steps only
        w = w - lam * dw
    w2, T, J = Pstep(f, w)
    ev, V = np.linalg.eig(J); iu = int(np.argmax(np.abs(ev))); vu = np.real(V[:, iu]); vs = np.real(V[:, 1 - iu])
    vu = vu / np.linalg.norm(vu) * np.sign(vu[0]); vs = vs / np.linalg.norm(vs) * np.sign(vs[0])
    return w, float(np.max(np.abs(w2 - w))), float(np.real(ev[iu])), vu, vs, J, T


def branch(f, fp, v, lam, sgn):
    out = []
    for j in range(NS):
        s = S0 * lam ** (j / NS); r = to_apo(f, fp + s * v, sgn)
        if r: out.append(dict(s=s, x=r[0], Kr=r[1], psi=r[2]))
    return out


def spline(pts):
    p = np.array([q["psi"] for q in pts]); k = np.array([q["Kr"] for q in pts]); o = np.argsort(p); p, k = p[o], k[o]
    pe = np.concatenate([p - 2 * np.pi, p, p + 2 * np.pi]); ke = np.concatenate([k, k, k])
    return CubicSpline(pe, ke)


def fourier(psi, d):
    cols = [np.ones_like(psi)] + [f(n * psi) for n in range(1, 5) for f in (np.sin, np.cos)]
    c, *_ = np.linalg.lstsq(np.array(cols).T, d, rcond=None)
    return dict(c0=c[0], **{("a%d" % n): c[2 * n - 1] for n in range(1, 5)}, **{("b%d" % n): c[2 * n] for n in range(1, 5)})


def Pstep(f, w, tmax=20000.0):
    """one y = 0 (y-dot > 0) return with its 2 x 2 section Jacobian; TERMINAL event (MNFlow.P integrates all of tmax)"""
    x, px = w; py = f.py_of(x, px)
    if not np.isfinite(py): return None
    s = np.array([x, 0.0, px, py] + list(np.eye(4).ravel()))
    pl = lambda t, s: s[0] - XPL; pl.direction = -1.0; pl.terminal = True    # plunge guard (left the domain, not a cap)
    o1 = solve_ivp(f.rhs, (0, 10.0), s, method="DOP853", events=pl, **RT)
    if o1.t_events[0].size: return None
    s1_ = o1.y[:, -1]   # leave the section first (a return takes ~100+ tau)
    ev = lambda t, s: s[1]; ev.direction = 1.0; ev.terminal = True
    sol = solve_ivp(f.rhs, (10.0, tmax), s1_, method="DOP853", events=[ev, pl], **RT)
    if not sol.t_events[0].size: return None
    st = sol.y_events[0][0]; Phi = st[4:].reshape(4, 4); fv = np.array(f._f(*st[:4]), float)
    # section Jacobian: project out the flow direction to y = 0, then restrict to (x, px) with py from the shell
    Pr = np.eye(4) - np.outer(fv, np.eye(4)[1]) / fv[1]; D = Pr @ Phi
    gxx, gyy, V = f._g(x, 0.0); eps = 1e-7
    dpy = np.array([(f.py_of(x + eps, px) - f.py_of(x - eps, px)) / (2 * eps), -(gxx * px) / (gyy * py)])   # d py / d(x, px) on H = -1/2
    C = np.array([[1, 0], [0, 0], [0, 1], [dpy[0], dpy[1]]]); Jm = D[[0, 2]][:, :] @ C
    return np.array([st[0], st[2]]), float(sol.t_events[0][0]), Jm


def cond_df(f, fp, vu, vs, s_u):
    """CKMJ Lemma-19 structure on the energy-eliminated section: unknowns (s_u, z_1..z_{n-1}, s_s)"""
    z = fp + s_u * vu; Js = []; pts = [z]; best = None
    for i in range(60):
        out = Pstep(f, z)
        if out is None:
            if best is not None: break
            return dict(ok=False, why="orbit left the section/plunged at return %d" % i)
        z2, T, J = out; Js.append(J); pts.append(z2); z = z2
        d = np.linalg.norm(z2 - fp)
        if i > 3 and (best is None or d < best[0]): best = (d, i + 1)
        if i > 3 and best and i + 1 - best[1] > 3: break
    n = best[1]; Js = Js[:n]; zs = pts[1:n]                     # z_1..z_{n-1}
    s_s = float(np.dot(pts[n] - fp, vs)); D = 2 * n; Fm = np.zeros((D, D))
    Fm[0:2, 0] = Js[0] @ vu
    for i in range(n - 1):
        Fm[2 * i:2 * i + 2, 1 + 2 * i:3 + 2 * i] = -np.eye(2)
        Fm[2 * i + 2:2 * i + 4, 1 + 2 * i:3 + 2 * i] = Js[i + 1]
    Fm[D - 2:D, D - 1] = -vs
    sv = np.linalg.svd(Fm, compute_uv=False)
    return dict(ok=True, n=n, cond=float(sv[0] / sv[-1]), smin=float(sv[-1]), smax=float(sv[0]),
                dist_end=float(best[0]), s_s=s_s)


def run_beta(beta):
    fn = os.path.join(HERE, "s1_beta_%g.json" % beta)
    if os.path.exists(fn): print("exists:", fn); return
    t0 = time.time(); f = flow(beta)
    fp, fperr, lam, vu, vs, J, T = fixed_point(f)
    U = branch(f, fp, vu, lam, +1); S = branch(f, fp, vs, lam, -1)
    su, ss = spline(U), spline(S); g = np.linspace(0, 2 * np.pi, 720, endpoint=False); dK = su(g) - ss(g)
    fit = fourier(g, dK)
    # transverse zeros of dK near psi0 = 0 and pi/2 (Lemma S symmetric orbits), and cond(DF) there
    zc = [];
    for k in range(len(g)):
        if dK[k] == 0 or dK[k] * dK[(k + 1) % len(g)] < 0: zc.append(float(g[k]))
    conds = []
    # s_u AT the zero: psi is linear in log s over the fundamental domain (slope -2 pi / log lam), so invert the fit
    lsU = np.log([u["s"] for u in U]); psU = np.unwrap([u["psi"] for u in U]); a_, b_ = np.polyfit(lsU, psU, 1)
    lin_resid = float(np.max(np.abs(psU - (a_ * lsU + b_))))
    for zpsi in zc[:4]:
        ks = [(zpsi + 2 * np.pi * k - b_) / a_ for k in range(-3, 4)]
        ls_ = min(ks, key=lambda v: abs(v - 0.5 * (lsU[0] + lsU[-1])))
        q = min(U, key=lambda u: min(abs(u["psi"] - zpsi), 2 * np.pi - abs(u["psi"] - zpsi)))
        conds.append(dict(psi=zpsi, s_u=float(np.exp(ls_)), **cond_df(f, fp, vu, vs, float(np.exp(ls_))),
                          nearest_sample=dict(s_u=q["s"], **cond_df(f, fp, vu, vs, q["s"]))))
    kr_spread_u = float(np.ptp([u["Kr"] for u in U])); kr_fp = float(Kr(fp[0], fp[1]))
    res = dict(beta=beta, fp=list(fp), fp_err=fperr, G_fp=bool(fperr <= 1e-11), lam_u=lam, T_tau=T, nU=len(U), nS=len(S),
               Kr_fp=kr_fp, Kr_spread_U=kr_spread_u, max_abs_dK=float(np.max(np.abs(dK))), fit=fit, psi_logs_slope=float(a_), psi_logs_lin_resid=lin_resid,
               amp2=float(np.hypot(fit["a2"], fit["b2"])), amp2_over_beta=(float(np.hypot(fit["a2"], fit["b2"]) / beta) if beta else None),
               a2_over_beta=(float(fit["a2"] / beta) if beta else None), zeros=zc, cond=conds, seconds=time.time() - t0,
               U=U, S=S)
    json.dump(res, open(fn, "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("beta", "fp_err", "lam_u", "nU", "nS", "max_abs_dK", "amp2", "amp2_over_beta", "seconds")}))
    print("cond:", [(round(c["psi"], 3), c.get("n"), "%.3e" % c["cond"] if c.get("ok") else c.get("why")) for c in conds])


def read():
    files = sorted(f for f in os.listdir(HERE) if f.startswith("s1_beta_"))
    R = {json.load(open(os.path.join(HERE, f)))["beta"]: json.load(open(os.path.join(HERE, f))) for f in files}
    gn = json.load(open(os.path.join(HERE, "s1_gnorm.json"))) if os.path.exists(os.path.join(HERE, "s1_gnorm.json")) else None
    k0 = R.get(0.0); gk = bool(k0 and k0["max_abs_dK"] <= 1e-9 and k0["Kr_spread_U"] <= 1e-9)
    gf = all(r["G_fp"] for r in R.values())
    print("G-norm:", gn and gn["PASS"], "| G-Kerr:", gk, "(max|dK| %.2e, Kr spread %.2e)" % (k0["max_abs_dK"], k0["Kr_spread_U"]) if k0 else "", "| G-fp:", gf)
    for b in sorted(R):
        r = R[b]; cs = [c["cond"] for c in r["cond"] if c.get("ok")]
        print("beta %-7g amp2/beta %s  a2/beta %s  b2 %.2e  min cond %s  zeros %d" % (b, "%.5e" % r["amp2_over_beta"] if b else "-",
              "%.5e" % r["a2_over_beta"] if b else "-", r["fit"]["b2"], "%.3e" % min(cs) if cs else "-", len(r["zeros"])))
    bs = sorted(b for b in R if b > 0)
    if not bs or not (gn and gn["PASS"]) or not gk or not gf: print("S1 READING: INVALID or incomplete"); return
    bmin = bs[0]; amin = R[bmin]["amp2_over_beta"]
    lin = [R[b]["amp2_over_beta"] for b in bs if b <= 1e-3]
    ca = abs(amin - TARGET) / TARGET <= 0.10 and (max(lin) - min(lin)) / min(lin) <= 0.20
    cb = any(c["cond"] <= 1e8 for b in bs if b >= 1e-2 for c in R[b]["cond"] if c.get("ok"))
    print("criterion (a): |A/beta| at beta %g = %.5e vs target %.5e (%.1f%%), linearity spread %.1f%% -> %s" % (
        bmin, amin, TARGET, 100 * (amin - TARGET) / TARGET, 100 * (max(lin) - min(lin)) / min(lin), ca))
    print("criterion (b): some cond(DF) <= 1e8 at beta >= 1e-2 -> %s" % cb)
    print("S1 READING:", "GO" if (ca and cb) else "STOP")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "gnorm": gnorm()
    elif a[0] == "beta": run_beta(float(a[1]))
    elif a[0] == "read": read()
