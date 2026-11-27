"""S2 design, FLOAT ONLY (no rigour): the numbers the S2 amendment cites, and the float pre-runs of the controls.
Usage: python s2f.py design <beta> | ctl_i | ctl_ii | ctl_iii
  design <b> : Newton-refine the 3pi/2 homoclinic of the section multiple-shooting system at beta b; report ||F||,
               sigma_min, ||A||, ||D^2 F||, the float noise in F, the local-manifold endpoint sizes, and the
               radii-polynomial precision requirement eps_res < (1 - Z)^2 / (4 ||A||^2 ||D^2F||)  -> s2f_design_<b>.json
  ctl_i      : beta = 0, the same square system from an S1 point: what the float validator would see -> s2f_ctl_i.json
  ctl_ii     : beta = 0, c = s_u FIXED and an unfolding alpha * grad K_r at the end: two distinct c, alpha -> 0;
               the same at beta = 3e-2 (alpha != 0 off the zero: the transition) -> s2f_ctl_ii.json
  ctl_iii    : sabotage (drop the 3 beta^2 term of the metric function G): F_sab at the true zero, and the zero's
               displacement, against the would-be ball radius -> s2f_ctl_iii.json
Uses s1.py (Pstep, fixed_point, flow) unchanged. Written by Claude Opus 5.5 (Quantum)."""
import sys, os, json, time, numpy as np, sympy as sp
import s1
from s1 import Pstep, fixed_point, flow, Kr
HERE = s1.HERE


def Kgrad(w):                                   # grad of K_r(x, p_x) on the section, central differences
    e = 1e-7; x, px = w
    return np.array([(Kr(x + e, px) - Kr(x - e, px)) / (2 * e), (Kr(x, px + e) - Kr(x, px - e)) / (2 * e)])


class Hom:
    """section multiple shooting. Square form (c free): X = (s_u, z_1..z_{n-1}, s_s).
    Unfolded form (c fixed): X = (z_1..z_{n-1}, s_s, alpha), last block P(z_{n-1}) - w_s(s_s) - alpha g."""
    def __init__(self, f, fp, vu, vs, n, c=None, g=None):
        self.f, self.fp, self.vu, self.vs, self.n, self.c, self.g = f, fp, vu, vs, n, c, g

    def split(self, X):
        n = self.n
        if self.c is None: return X[0], X[1:2 * n - 1].reshape(n - 1, 2), X[2 * n - 1], 0.0
        return self.c, X[0:2 * n - 2].reshape(n - 1, 2), X[2 * n - 2], X[2 * n - 1]

    def F(self, X, jac=True):
        n = self.n; su, Z, ss, al = self.split(X); D = 2 * n
        pts = [self.fp + su * self.vu] + list(Z)
        R = np.zeros(D); Jm = np.zeros((D, D)); Js = []
        for i in range(n):
            out = Pstep(self.f, pts[i])
            if out is None: raise RuntimeError("return %d left the domain" % i)
            Js.append(out[2]); tgt = pts[i + 1] if i < n - 1 else self.fp + ss * self.vs + (al * self.g if self.c is not None else 0)
            R[2 * i:2 * i + 2] = out[0] - tgt
        if not jac: return R, None
        off = 0 if self.c is not None else 1
        if self.c is None: Jm[0:2, 0] = Js[0] @ self.vu
        for i in range(n - 1):
            col = off + 2 * i
            Jm[2 * i:2 * i + 2, col:col + 2] = -np.eye(2)
            Jm[2 * i + 2:2 * i + 4, col:col + 2] = Js[i + 1]
        if self.c is None: Jm[D - 2:D, D - 1] = -self.vs
        else: Jm[D - 2:D, D - 2] = -self.vs; Jm[D - 2:D, D - 1] = -self.g
        return R, Jm

    def x0_from(self, su_or_c, ss_guess=None):
        z = self.fp + su_or_c * self.vu; Z = []
        for i in range(self.n - 1):
            z = Pstep(self.f, z)[0]; Z.append(z)
        zl = Pstep(self.f, z)[0]; ss = float(np.dot(zl - self.fp, self.vs)) if ss_guess is None else ss_guess
        if self.c is None: return np.concatenate([[su_or_c], np.ravel(Z), [ss]])
        return np.concatenate([np.ravel(Z), [ss], [0.0]])


def newton(H, X, it=12, log=None):
    hist = []
    for k in range(it):
        R, Jm = H.F(X); nr = float(np.max(np.abs(R))); hist.append(nr)
        if log: print("   newton %2d  ||F||_inf %.3e" % (k, nr), flush=True)
        if nr < 1e-15: break
        dX = np.linalg.solve(Jm, -R); X = X + dX
        if np.max(np.abs(dX)) < 1e-16: break
    R, Jm = H.F(X)
    return X, R, Jm, hist


def d2norm(H, X, h=1e-6, ndir=6, seed=7):
    rng = np.random.default_rng(seed); best = 0.0
    dirs = [np.eye(len(X))[j] for j in range(min(4, len(X)))] + [v / np.max(np.abs(v)) for v in rng.normal(size=(ndir, len(X)))]
    for v in dirs:
        _, Jp = H.F(X + h * v); _, Jn = H.F(X - h * v)
        best = max(best, np.linalg.norm((Jp - Jn) / (2 * h), np.inf))     # ||D^2F[v]||_inf with ||v||_inf = 1
    return float(best)


def zero_s(beta, which=3 * np.pi / 2):
    r = json.load(open(os.path.join(HERE, "s1_beta_%g.json" % beta)))
    c = min(r["cond"], key=lambda c: abs(c["psi"] - which)); return c["s_u"], c["n"]


def design(beta):
    t0 = time.time(); f = flow(beta); fp, err, lam, vu, vs, J, T = fixed_point(f)
    su, n = zero_s(beta)
    # endpoints near fp: start k fundamental domains EARLIER so |s_u| and |s_s| are small (cond does not depend on n)
    res = dict(beta=beta, lam_u=lam, fp=list(fp), runs=[])
    Xprev = None
    for shift in (0, 2):
        nn = n + 2 * shift; H = Hom(f, fp, vu, vs, nn); print("beta %g shift %d n %d" % (beta, shift, nn), flush=True)
        if shift == 0: X = H.x0_from(su)
        else:   # k extra returns at each end: start k domains earlier on W^u, end k returns deeper on W^s
            k = shift; su0, Z0, ss0, _ = Hom(f, fp, vu, vs, n).split(Xprev); c0 = su0 / lam ** k
            Zs = []; z = fp + c0 * vu
            for j in range(k): z = Pstep(f, z)[0]; Zs.append(z)
            Zs[-1] = fp + su0 * vu                                       # = w_u(s_u) of the shift-0 solution
            Zs += list(Z0) + [fp + ss0 / lam ** j * vs for j in range(k)]
            X = np.concatenate([[c0], np.ravel(Zs), [ss0 / lam ** k]])
        X, R, Jm, hist = newton(H, X, log=True); Xprev = X
        sv = np.linalg.svd(Jm, compute_uv=False); Ainv = np.linalg.inv(Jm)
        nA = float(np.linalg.norm(Ainv, np.inf)); d2 = d2norm(H, X)
        # float noise in F: tighter integration (DOP853 floor) against the registered 1e-13
        s1.RT.update(rtol=3e-14, atol=3e-14); R2, _ = H.F(X, jac=False); s1.RT.update(rtol=1e-13, atol=1e-13)
        noise = float(np.max(np.abs(R2 - R)))
        req = 1.0 / (4 * nA ** 2 * d2)                       # Z0 = Z1 = 0 idealisation: (1 - Z)^2 -> 1
        Y = float(np.max(np.abs(Ainv @ R)))
        run = dict(shift=shift, n=nn, s_u=float(X[0]), s_s=float(X[-1]), newton_hist=hist, F_inf=float(np.max(np.abs(R))),
                   F_noise=noise, smin=float(sv[-1]), smax=float(sv[0]), cond2=float(sv[0] / sv[-1]), A_inf=nA, D2F_inf=d2,
                   eps_res_required=req, Y_float=Y, ball_r_float=2 * Y, disc_float=float(1 - 4 * nA * d2 * Y))
        print("   n %d s_u %.3e s_s %.3e |F| %.2e noise %.2e smin %.3e ||A|| %.3e ||D2F|| %.3e -> need eps_res < %.2e; float Y %.2e disc %.3f"
              % (nn, run["s_u"], run["s_s"], run["F_inf"], noise, run["smin"], nA, d2, req, Y, run["disc_float"]), flush=True)
        res["runs"].append(run)
    res["seconds"] = time.time() - t0
    json.dump(res, open(os.path.join(HERE, "s2f_design_%g.json" % beta), "w"), indent=1)


def ctl_i():
    """beta = 0: the square system has a 1-D kernel in exact arithmetic (W^u = W^s). Float: run the same Newton from the
    S1 point; report sigma_min against beta = 3e-2 and the radii-polynomial discriminant the validator would face."""
    f = flow(0.0); fp, err, lam, vu, vs, J, T = fixed_point(f)
    su, n = zero_s(0.03); out = dict(beta=0.0, runs=[])
    for c0 in (su, su * lam ** 0.37):
        H = Hom(f, fp, vu, vs, n); X = H.x0_from(c0); X, R, Jm, hist = newton(H, X, log=True)
        sv = np.linalg.svd(Jm, compute_uv=False); nA = float(np.linalg.norm(np.linalg.inv(Jm), np.inf)); d2 = d2norm(H, X)
        Y = float(np.max(np.abs(np.linalg.solve(Jm, R))))
        run = dict(c0=c0, s_u_final=float(X[0]), moved=float(X[0] - c0), hist=hist, smin=float(sv[-1]), cond2=float(sv[0] / sv[-1]),
                   A_inf=nA, D2F_inf=d2, Y=Y, disc=float(1 - 4 * nA * d2 * Y))
        print("  c0 %.4e -> s_u %.4e  smin %.2e cond %.2e ||A|| %.2e Y %.2e disc %.3e" % (c0, X[0], run["smin"], run["cond2"], nA, Y, run["disc"]), flush=True)
        out["runs"].append(run)
    json.dump(out, open(os.path.join(HERE, "s2f_ctl_i.json"), "w"), indent=1)


def ctl_ii(kend=3):
    """c = s_u FIXED, unfolding alpha * g (g = grad K_r / |grad K_r| at the end) and kend extra returns at the stable end
    (so the linear local W^s is accurate to ~ s_s^2). beta = 0: alpha must vanish (to float noise) for EVERY c across a
    fundamental domain (the family). beta = 3e-2: alpha(c) must be non-zero off the zeros (the transition)."""
    out = dict(kend=kend, runs=[])
    for beta in (0.0, 0.03):
        f = flow(beta); fp, err, lam, vu, vs, J, T = fixed_point(f); su, n = zero_s(0.03)
        for frac in np.linspace(0, 1, 8, endpoint=False):
            c = su * lam ** frac; nn = n + kend
            z = fp + c * vu; Z = []
            for i in range(n - 1): z = Pstep(f, z)[0]; Z.append(z)
            zl = Pstep(f, z)[0]; ss = float(np.dot(zl - fp, vs))
            Z += [fp + ss / lam ** j * vs for j in range(kend)]
            X = np.concatenate([np.ravel(Z), [ss / lam ** kend], [0.0]])
            g = Kgrad(fp + (ss / lam ** kend) * vs); g = g / np.linalg.norm(g)
            H = Hom(f, fp, vu, vs, nn, c=c, g=g)
            try:
                X, R, Jm, hist = newton(H, X); sv = np.linalg.svd(Jm, compute_uv=False)
                nA = float(np.linalg.norm(np.linalg.inv(Jm), np.inf)); Y = float(np.max(np.abs(np.linalg.solve(Jm, R))))
                run = dict(beta=beta, c=c, frac=float(frac), n=nn, s_s=float(X[-2]), alpha=float(X[-1]), F_inf=float(np.max(np.abs(R))),
                           cond2=float(sv[0] / sv[-1]), A_inf=nA, Y=Y, hist=hist)
                print("  beta %g c %.4e (frac %.3f) n %d: alpha %+.3e  s_s %.2e |F| %.2e cond %.2e ||A|| %.2e Y %.2e" % (
                    beta, c, frac, nn, run["alpha"], run["s_s"], run["F_inf"], run["cond2"], nA, Y), flush=True)
            except Exception as ex:
                run = dict(beta=beta, c=c, frac=float(frac), n=nn, failed=str(ex)); print("  beta %g frac %.3f FAILED %s" % (beta, frac, ex), flush=True)
            out["runs"].append(run)
    json.dump(out, open(os.path.join(HERE, "s2f_ctl_ii.json"), "w"), indent=1)


def mine_sab(M, aa, beta, E, L):
    """mn_s5_gate.mine with ONE beta term dropped: the 3 beta^2 (P3^2 - P2^2)/R^6 term of the metric function G."""
    G = s1.G; Q = G.Q
    X, Y = sp.symbols("x y", positive=True)
    chi = sp.Rational(aa, M); kk = sp.sqrt(M**2 - aa**2); alpha = (-1 + sp.sqrt(1 - chi**2)) / chi
    Rr = sp.sqrt(X**2 + Y**2 - 1); u = X*Y/Rr; P = [sp.legendre(l, u) for l in range(4)]
    psi = beta*P[2]/Rr**3
    aexp = -alpha*sp.exp(-2*beta*(-1 + sum((X - Y)*P[l]/Rr**(l + 1) for l in range(3))))
    bexp = alpha*sp.exp(2*beta*(1 + sum((-1)**(3 - l)*(X + Y)*P[l]/Rr**(l + 1) for l in range(3))))
    Gx = 2*beta*sum(((X - Y) + (-1)**l*(X + Y))*P[l]/Rr**(l + 1) - 2 for l in range(3)) + 8*beta     # SABOTAGE: 3 beta^2 term gone
    sub = {Q.x: X, Q.y: Y, Q.a: aexp, Q.b: bexp, Q.k: kk, Q.al: alpha}
    A_, B_, C_ = (e.subs(sub) for e in (Q.A, Q.B, Q.C))
    Qp, _ = sp.div(sp.Poly(sp.expand((Q.x**2 - 1)*(1 - Q.y**2)*Q.B**2 - 4*Q.C**2), Q.x, Q.y, Q.a, Q.b),
                   sp.Poly(Q.A, Q.x, Q.y, Q.a, Q.b))
    Q_ = Qp.as_expr().subs(sub)
    w0 = 4*kk*alpha/(1 - alpha**2); rho2 = kk**2*(X**2 - 1)*(1 - Y**2); E2 = sp.exp(2*psi)
    Lp = L + w0*E
    V = sp.Rational(1, 2)*(E2*A_*Lp**2 - 4*kk*C_*E*Lp - kk**2*E**2*Q_/E2)/(rho2*B_)
    gxx = E2*(X**2 - 1)*(1 - alpha**2)**2/(kk**2*B_*sp.exp(Gx))
    gyy = E2*(1 - Y**2)*(1 - alpha**2)**2/(kk**2*B_*sp.exp(Gx))
    return X, Y, gxx, gyy, V


def mine_nopsi(M, aa, beta, E, L):
    """gross sabotage: mine with the first-order potential term psi = beta P2 / R^3 set to 0 (all else as mine)."""
    X, Y, gxx, gyy, V = None, None, None, None, None
    src = mine_sab.__code__  # (documentation only)
    G = s1.G; Q = G.Q
    X, Y = sp.symbols("x y", positive=True)
    chi = sp.Rational(aa, M); kk = sp.sqrt(M**2 - aa**2); alpha = (-1 + sp.sqrt(1 - chi**2)) / chi
    Rr = sp.sqrt(X**2 + Y**2 - 1); u = X*Y/Rr; P = [sp.legendre(l, u) for l in range(4)]
    psi = 0     # SABOTAGE
    aexp = -alpha*sp.exp(-2*beta*(-1 + sum((X - Y)*P[l]/Rr**(l + 1) for l in range(3))))
    bexp = alpha*sp.exp(2*beta*(1 + sum((-1)**(3 - l)*(X + Y)*P[l]/Rr**(l + 1) for l in range(3))))
    Gx = 3*beta**2*(P[3]**2 - P[2]**2)/Rr**6 + 2*beta*sum(((X - Y) + (-1)**l*(X + Y))*P[l]/Rr**(l + 1) - 2 for l in range(3)) + 8*beta
    sub = {Q.x: X, Q.y: Y, Q.a: aexp, Q.b: bexp, Q.k: kk, Q.al: alpha}
    A_, B_, C_ = (e.subs(sub) for e in (Q.A, Q.B, Q.C))
    Qp, _ = sp.div(sp.Poly(sp.expand((Q.x**2 - 1)*(1 - Q.y**2)*Q.B**2 - 4*Q.C**2), Q.x, Q.y, Q.a, Q.b),
                   sp.Poly(Q.A, Q.x, Q.y, Q.a, Q.b))
    Q_ = Qp.as_expr().subs(sub)
    w0 = 4*kk*alpha/(1 - alpha**2); rho2 = kk**2*(X**2 - 1)*(1 - Y**2); E2 = sp.exp(2*psi)
    Lp = L + w0*E
    V = sp.Rational(1, 2)*(E2*A_*Lp**2 - 4*kk*C_*E*Lp - kk**2*E**2*Q_/E2)/(rho2*B_)
    gxx = E2*(X**2 - 1)*(1 - alpha**2)**2/(kk**2*B_*sp.exp(Gx))
    gyy = E2*(1 - Y**2)*(1 - alpha**2)**2/(kk**2*B_*sp.exp(Gx))
    return X, Y, gxx, gyy, V


def ctl_iii():
    """sabotage on the S2 (symmetric) formulation at beta = 3e-2: the symmetric point p and the transversality ratio
    |v_x|/|v| for the true field, the subtle sabotage (3 beta^2 term of G dropped) and the gross one (psi = 0)."""
    out = {"true": sym(0.03)}
    orig = s1.G.mine
    for tag, fn in (("drop_beta2_G", mine_sab), ("drop_psi", mine_nopsi)):
        s1.G.mine = fn
        try: out[tag] = sym(0.03)
        finally: s1.G.mine = orig
        out[tag]["dp_inf"] = float(np.max(np.abs(np.array(out[tag]["p"]) - np.array(out["true"]["p"]))))
        out[tag]["dratio_rel"] = float(out[tag]["t_ratio"] / out["true"]["t_ratio"] - 1)
        print("  %s: |dp| %.3e, ratio change %.3e" % (tag, out[tag]["dp_inf"], out[tag]["dratio_rel"]), flush=True)
    json.dump(out, open(os.path.join(HERE, "s2f_ctl_iii.json"), "w"), indent=1)




def sym(beta, kshift=2):
    """R-symmetric half BVP (R: (x, y, p_x, p_y) -> (x, -y, -p_x, p_y), Fix R on the section = {p_x = 0}).
    X = (s_u, z_1..z_{m-1}); equations z_{i} = P(z_{i-1}) (z_0 = w_u(s_u)), and p_x(P(z_{m-1})) = 0. Square, 2m - 1.
    Transversality of W^u and W^s = R W^u at the symmetric point p  <=>  the tangent v of W^u at p is neither along
    Fix R (= the Krawczyk isolation of the half BVP) nor perpendicular to it: |v_x| / |v| > 0 is the S2 inequality."""
    f = flow(beta); fp, err, lam, vu, vs, J, T = fixed_point(f)
    su, n = zero_s(0.03 if beta == 0 else beta)
    # the apo return of the full orbit: the forward return with the largest x
    z = fp + su * vu; pts = [z]
    for i in range(n): z = Pstep(f, z)[0]; pts.append(z)
    m = int(np.argmax([p[0] for p in pts])); c0 = su / lam ** kshift; m2 = m + kshift
    z = fp + c0 * vu; Z = []
    for i in range(m2 - 1): z = Pstep(f, z)[0]; Z.append(z)
    X = np.concatenate([[c0], np.ravel(Z)]); D = 2 * m2 - 1; hist = []
    for it in range(14):
        su_, Zs = X[0], X[1:].reshape(m2 - 1, 2); w = [fp + su_ * vu] + list(Zs); R = np.zeros(D); Jm = np.zeros((D, D)); Js = []
        for i in range(m2):
            o = Pstep(f, w[i]); Js.append(o[2])
            if i < m2 - 1: R[2 * i:2 * i + 2] = o[0] - w[i + 1]
            else: R[D - 1] = o[0][1]
        Jm[0:2, 0] = Js[0] @ vu
        for i in range(m2 - 1):
            col = 1 + 2 * i
            if 2 * i + 2 < D - 1: Jm[2 * i:2 * i + 2, col:col + 2] = -np.eye(2); Jm[2 * i + 2:2 * i + 4, col:col + 2] = Js[i + 1]
            else: Jm[2 * i:2 * i + 2, col:col + 2] = -np.eye(2); Jm[D - 1, col:col + 2] = Js[i + 1][1]
        nr = float(np.max(np.abs(R))); hist.append(nr)
        if nr < 1e-15: break
        X = X - np.linalg.solve(Jm, R)
    # tangent of W^u at p: v = J_m ... J_1 vu
    v = vu.copy()
    for Jk in Js: v = Jk @ v
    p = Pstep(f, X[1:].reshape(m2 - 1, 2)[-1])[0]
    sv = np.linalg.svd(Jm, compute_uv=False); nA = float(np.linalg.norm(np.linalg.inv(Jm), np.inf))
    out = dict(beta=beta, m=m2, s_u=float(X[0]), p=list(p), F_inf=hist[-1], hist=hist, cond2=float(sv[0] / sv[-1]), smin=float(sv[-1]),
               A_inf=nA, v=list(v), t_ratio=float(abs(v[0]) / np.linalg.norm(v)), K_p_minus_K_fp=float(Kr(*p) - Kr(*fp)))
    print("beta %g m %d |F| %.2e cond %.3e ||A|| %.3e  p (%.12f, %.2e)  v (%.4e, %.4e)  |v_x|/|v| = %.4e" % (
        beta, m2, out["F_inf"], out["cond2"], nA, p[0], p[1], v[0], v[1], out["t_ratio"]), flush=True)
    return out


def sym_all():
    res = [sym(b) for b in (0.03, 0.01, 0.0)]
    json.dump(res, open(os.path.join(HERE, "s2f_sym.json"), "w"), indent=1)





def ctl_ii_meet(f, fp, vu, m, c, cp, Zf, Zb, g, it=14):
    """forward chain from w_u(c) (m returns) meets R(backward chain from w_u(c')) (m returns) at the outer crossing:
    P(z_{m-1}) = R P(z'_{m-1}) + alpha g. X = (z_1..z_{m-1}, z'_1..z'_{m-1}, c', alpha); c fixed."""
    Rm = np.diag([1.0, -1.0]); D = 4 * (m - 1) + 2
    X = np.concatenate([np.ravel(Zf), np.ravel(Zb), [cp, 0.0]]); hist = []
    for k in range(it):
        Zf_ = X[:2 * (m - 1)].reshape(m - 1, 2); Zb_ = X[2 * (m - 1):4 * (m - 1)].reshape(m - 1, 2); cp_, al = X[-2], X[-1]
        R = np.zeros(D); Jm = np.zeros((D, D)); off_b = 2 * (m - 1)
        wf = [fp + c * vu] + list(Zf_); wb = [fp + cp_ * vu] + list(Zb_)
        Of = [Pstep(f, w) for w in wf]; Ob = [Pstep(f, w) for w in wb]
        if any(o is None for o in Of + Ob): raise RuntimeError("left the domain")
        row = 0
        for i in range(m - 1):                                   # forward links: P(w_i) - z_{i+1}
            R[row:row + 2] = Of[i][0] - Zf_[i]
            if i > 0: Jm[row:row + 2, 2 * (i - 1):2 * i] = Of[i][2]
            Jm[row:row + 2, 2 * i:2 * i + 2] = -np.eye(2); row += 2
        for i in range(m - 1):                                   # backward-chain links (also forward in time from w_u(c'))
            R[row:row + 2] = Ob[i][0] - Zb_[i]
            if i == 0: Jm[row:row + 2, D - 2] = Ob[0][2] @ vu
            else: Jm[row:row + 2, off_b + 2 * (i - 1):off_b + 2 * i] = Ob[i][2]
            Jm[row:row + 2, off_b + 2 * i:off_b + 2 * i + 2] = -np.eye(2); row += 2
        R[row:row + 2] = Of[m - 1][0] - Rm @ Ob[m - 1][0] - al * g      # the meeting
        Jm[row:row + 2, 2 * (m - 2):2 * (m - 1)] = Of[m - 1][2]
        Jm[row:row + 2, off_b + 2 * (m - 2):off_b + 2 * (m - 1)] = -Rm @ Ob[m - 1][2]
        Jm[row:row + 2, D - 1] = -g
        nr = float(np.max(np.abs(R))); hist.append(nr)
        if nr < 1e-15: break
        X = X - np.linalg.solve(Jm, R)
    sv = np.linalg.svd(Jm, compute_uv=False)
    return X, nr, hist, float(sv[0] / sv[-1]), float(np.linalg.norm(np.linalg.inv(Jm), np.inf)), float(np.max(np.abs(np.linalg.solve(Jm, R))))


def ctl_ii():
    """(ii) positive non-isolation, float pre-run. beta = 0: alpha(c) must vanish to float noise for EVERY c across a
    fundamental domain, with the system well conditioned (then a uniform-contraction proof over c-intervals plus K
    conservation gives a continuum of homoclinics). beta = 3e-2: alpha(c) must be non-zero off the 4 zeros (transition)."""
    out = dict(runs=[]); Rm = np.diag([1.0, -1.0])
    for beta in (0.0, 0.03):
        f = flow(beta); fp, err, lam, vu, vs, J, T = fixed_point(f); su, n = zero_s(0.03)
        # m = returns from w_u(su) to the outer crossing (the 3pi/2 orbit's apo); a c in [su, su*lam) needs the same m
        z = fp + su * vu; pts = [z]
        for i in range(n): z = Pstep(f, z)[0]; pts.append(z)
        m = int(np.argmax([p[0] for p in pts]))
        grid = [su * lam ** (j / 48) for j in range(-96, 48)]; Yg = []      # c' may sit up to 2 domains below su
        for cg in grid:
            z = fp + cg * vu; ch = []
            for i in range(m):
                o = Pstep(f, z); z = o[0] if o is not None else np.array([np.nan, np.nan]); ch.append(z)
            Yg.append(ch)
        for j in range(96, 144, 6):
            c = grid[j]; yf = Yg[j][-1]
            jb = int(np.nanargmin([np.linalg.norm(Rm @ Yb[-1] - yf) for Yb in Yg]))
            g = Kgrad(yf); g = g / np.linalg.norm(g)
            try:
                X, nr, hist, cnd, nA, Y = ctl_ii_meet(f, fp, vu, m, c, grid[jb], Yg[j][:-1], Yg[jb][:-1], g)
                run = dict(beta=beta, c=c, frac=(j - 96) / 48, m=m, cprime=float(X[-2]), alpha=float(X[-1]), F_inf=nr, cond2=cnd, A_inf=nA, Y=Y, hist=hist)
                print("  beta %g frac %.3f m %d: alpha %+.3e  c' %.4e  |F| %.2e cond %.2e ||A|| %.2e" % (beta, (j - 96) / 48, m, X[-1], X[-2], nr, cnd, nA), flush=True)
            except Exception as ex:
                run = dict(beta=beta, c=c, frac=(j - 96) / 48, failed=str(ex)); print("  beta %g frac %.3f FAILED %s" % (beta, (j - 96) / 48, ex), flush=True)
            out["runs"].append(run)
    json.dump(out, open(os.path.join(HERE, "s2f_ctl_ii.json"), "w"), indent=1)


if __name__ == "__main__":
    a = sys.argv[1:]
    {"design": lambda: design(float(a[1])), "ctl_i": ctl_i, "ctl_ii": ctl_ii, "ctl_iii": ctl_iii, "sym": sym_all}[a[0]]()
