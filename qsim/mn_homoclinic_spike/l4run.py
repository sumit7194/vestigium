"""S2 control (iv) driver: float set-up for capd/s2_l4 (the CKMJ Thm 3 L4 homoclinic, PCRTBP mu = 1/2, E = 3).
All decisions are made by s2_l4 (MPFR intervals). Checkpoints in s2/l4_iv/. Written by Claude Opus 5.5 (Quantum)."""
import os, json, re, time, subprocess, numpy as np, mpmath as mp
from scipy.integrate import solve_ivp
mp.mp.dps = 50
HERE = os.path.dirname(os.path.abspath(__file__)); CAPD = os.path.join(HERE, "capd"); D = os.path.join(HERE, "s2", "l4_iv"); os.makedirs(D, exist_ok=True)
mu = 0.5; L4 = np.array([mu - 0.5, 0.0, np.sqrt(3) / 2, 0.0])
PBAR = ["-0.037058535628028", "-0.007623220519232", "0.873641524369283", "0.033084516464648"]   # CKMJ Table 4, x1 = p-bar
DELTA = "1e-7"; RHO = 2.5e-8; NIT = int(os.environ.get("L4NIT", "60")); TSEG = float(os.environ.get("L4TSEG", "0.5")); RT = dict(rtol=1e-13, atol=1e-15)
d17 = lambda v: repr(float(v))
d40 = lambda v: mp.nstr(mp.mpf(v), 40, min_fixed=-mp.inf, max_fixed=mp.inf)


def Om_x(x, y):
    r1 = np.hypot(x - mu, y); r2 = np.hypot(x + 1 - mu, y)
    return (1 - mu) * (x - mu) * (1 - r1 ** -3) + mu * (x + 1 - mu) * (1 - r2 ** -3), (1 - mu) * y * (1 - r1 ** -3) + mu * y * (1 - r2 ** -3)
def f4(z, al=0.0):
    x, p, y, q = z; ox, oy = Om_x(x, y)
    return np.array([p + al * 2 * ox, 2 * q + ox - al * 2 * p, q + al * 2 * oy, -2 * p + oy - al * 2 * q])
def hess(x, y):
    r1 = np.hypot(x - mu, y); r2 = np.hypot(x + 1 - mu, y); a1, a2 = r1 ** -3, r2 ** -3; b1, b2 = r1 ** -5, r2 ** -5
    Oxx = (1 - mu) * ((1 - a1) + 3 * (x - mu) ** 2 * b1) + mu * ((1 - a2) + 3 * (x + 1 - mu) ** 2 * b2)
    Oyy = (1 - mu) * ((1 - a1) + 3 * y ** 2 * b1) + mu * ((1 - a2) + 3 * y ** 2 * b2)
    Oxy = 3 * (1 - mu) * (x - mu) * y * b1 + 3 * mu * (x + 1 - mu) * y * b2
    return Oxx, Oxy, Oyy
def J4(z, al=0.0):
    """analytic Jacobian of f + alpha grad E"""
    Oxx, Oxy, Oyy = hess(z[0], z[2])
    J0 = np.array([[0, 1, 0, 0], [Oxx, 0, Oxy, 2], [0, 0, 0, 1], [Oxy, -2, Oyy, 0]], float)
    JE = np.array([[2 * Oxx, 0, 2 * Oxy, 0], [0, -2, 0, 0], [2 * Oxy, 0, 2 * Oyy, 0], [0, 0, 0, -2]], float)
    return J0 + al * JE
def gradE(z):
    ox, oy = Om_x(z[0], z[2]); return np.array([2 * ox, -2 * z[1], 2 * oy, -2 * z[3]])
def flow(z, T, al=0.0, var=False):
    """time-T flow of z' = f + alpha grad E (4-D), with the 4x4 STM and the T- and alpha-derivatives if var."""
    if not var:
        return solve_ivp(lambda t, s: f4(s, al), (0, T), z, method="DOP853", **RT).y[:, -1]
    def rhs(t, s):
        zz = s[:4]; Phi = s[4:20].reshape(4, 4); da = s[20:24]
        g = gradE(zz)
        Jz = J4(zz, al); return np.concatenate([f4(zz, al), (Jz @ Phi).ravel(), Jz @ da + g])
    s0 = np.concatenate([z, np.eye(4).ravel(), np.zeros(4)])
    s = solve_ivp(rhs, (0, T), s0, method="DOP853", **RT).y[:, -1]
    zT = s[:4]; return zT, s[4:20].reshape(4, 4), f4(zT, al), s[20:24]


def run(mode, spec, out):
    t0 = time.time(); r = subprocess.run([os.path.join(CAPD, "s2_l4"), mode, spec], capture_output=True, text=True)
    open(out, "w").write(r.stdout + ("\nSTDERR\n" + r.stderr if r.stderr.strip() else ""))
    print("  %s %s rc %d (%.0f s)" % (mode, os.path.basename(spec), r.returncode, time.time() - t0), flush=True)
    if r.returncode not in (0, 3): raise RuntimeError(r.stdout[-600:])
    return r.stdout


def writespec(fn, d):
    with open(fn, "w") as fh:
        for k, v in d.items(): fh.write(k + " " + " ".join(v if isinstance(v, (list, tuple)) else [v]) + "\n")


def main():
    js = os.path.join(D, "l4.json")
    if os.path.exists(js): print(open(js).read()); return
    t00 = time.time()
    ev, V = np.linalg.eig(J4(L4)); iu = int(np.argmax(np.real(ev))); is_ = int(np.argmin(np.real(ev)))
    vu, vs = V[:, iu], V[:, is_]
    def nrm(c): return c / np.linalg.norm(c)
    # TRUE real Jordan basis: normalise the complex eigenvector as a whole, then (Re, Im): the linear flow is exactly
    # e^{at} R(bt) in these coordinates, so the radius is monotone (separately normalised Re/Im parts make it elliptical)
    vu = vu / np.linalg.norm(vu); vs = vs / np.linalg.norm(vs)
    Tu = np.column_stack([np.real(vu), np.imag(vu), np.real(vs), np.imag(vs)])
    Ts = np.column_stack([np.real(vs), np.imag(vs), np.real(vu), np.imag(vu)])
    Bu = np.linalg.inv(Tu) @ J4(L4) @ Tu; print("  Jordan check: u-block", np.round(Bu[:2, :2], 6).tolist(), "off-block max %.1e" % np.max(np.abs(Bu[:2, 2:])), flush=True)
    print("L4 eigenvalues", ev[iu], ev[is_], flush=True)
    base = dict(prec="128", order="20", tol="1e-24")
    cones = {}
    for tag, sg, T in (("u", "1", Tu), ("s", "-1", Ts)):
        fn = os.path.join(D, "cone_%s.spec" % tag); writespec(fn, dict(base, sigma=sg, tau="1", delta=DELTA, T=[d17(v) for v in T.ravel()]))
        txt = run("cone", fn, os.path.join(D, "cone_%s.out" % tag))
        m_ = re.search(r"^RESULT cone CERTIFIED L (\S+) mu (\S+) nu (\S+) deltastar (\S+)", txt, re.M)
        if not m_: raise SystemExit("cone %s FAILED" % tag)
        cones[tag] = dict(L=m_.group(1), deltastar=m_.group(4)); print("  cone", tag, cones[tag], flush=True)
        if not RHO < float(m_.group(4)) * 0.9: raise SystemExit("rho does not fit inside deltastar")
    # float homoclinic: two-sided shooting. Forward from w_u(theta) and backward from w_s(phi) are both accurate (each
    # error grows only ~e^{0.63 t} from 1e-16); match the two orbits at p-bar's neighbourhood by Gauss-Newton on
    # (theta, phi, t1, t2) (4 equations, rank 3 by energy -> least squares), started from p-bar's own data.
    pb = np.array([float(v) for v in PBAR]); Tiu = np.linalg.inv(Tu); Tis = np.linalg.inv(Ts)
    eu = lambda t, s: np.linalg.norm((Tiu @ (s - L4))[:2]) - RHO; eu.terminal = True
    sb = solve_ivp(lambda t, s: -f4(s), (0, 60), pb, method="DOP853", events=eu, **RT); tb0 = sb.t_events[0][0]
    cu = (Tiu @ (sb.y_events[0][0] - L4))[:2]; th0 = np.arctan2(cu[1], cu[0])
    sf = solve_ivp(lambda t, s: f4(s), (0, 40), pb, method="DOP853", dense_output=True, **RT)
    tt = np.linspace(15, 40, 5001); tc = tt[int(np.argmin([np.linalg.norm(sf.sol(t) - L4) for t in tt]))]
    zc = sf.sol(tc); sc = (Tis @ (zc - L4))[:2]; rs = np.linalg.norm(sc)
    ers = lambda t, s: np.linalg.norm((Tis @ (s - L4))[:2]) - rs; ers.terminal = True; ers.direction = 1.0
    def back(phi, T=None):
        w = L4 + RHO * (np.cos(phi) * Ts[:, 0] + np.sin(phi) * Ts[:, 1])
        if T is None: return solve_ivp(lambda t, s: -f4(s), (0, 60), w, method="DOP853", events=ers, **RT)
        return solve_ivp(lambda t, s: -f4(s), (0, T), w, method="DOP853", **RT).y[:, -1]
    grid = np.linspace(-np.pi, np.pi, 145)
    def seamd(p):
        o = back(p); return np.linalg.norm(o.y_events[0][0] - zc) if o.t_events[0].size else 1.0
    ph0 = grid[int(np.argmin([seamd(p) for p in grid]))]; o = back(ph0); t2_0 = o.t_events[0][0] + tc   # backward time from w_s to p-bar
    fw = lambda a, T: solve_ivp(lambda t, s: f4(s), (0, T), L4 + RHO * (np.cos(a) * Tu[:, 0] + np.sin(a) * Tu[:, 1]), method="DOP853", **RT).y[:, -1]
    # anchor BOTH halves to p-bar (CKMJ's orbit): Gauss-Newton on (theta, t1) for |phi_t1(w_u(theta)) - p-bar| and on
    # (phi, t2) for |phi_-t2(w_s(phi)) - p-bar|. Each half then passes within ~1e-9 (p-bar's own accuracy) of p-bar.
    def anchor(fun, q0, tag):
        q = np.array(q0, float)
        for it in range(40):
            g = fun(q); ng = np.linalg.norm(g)
            Jg = np.column_stack([(fun(q + h * e) - fun(q - h * e)) / (2 * h) for h, e in zip((1e-7, 1e-7), np.eye(2))])
            dq = np.linalg.lstsq(Jg, g, rcond=None)[0]; lam = 1.0
            while lam > 1e-6 and np.linalg.norm(fun(q - lam * dq)) >= ng: lam /= 2
            if lam <= 1e-6: break
            q = q - lam * dq
        print("   anchor %s: |.| %.2e after %d steps" % (tag, np.linalg.norm(fun(q)), it), flush=True); return q, np.linalg.norm(fun(q))
    (th, t1), d1 = anchor(lambda q: fw(q[0], q[1]) - pb, (th0, tb0), "W^u side")
    if d1 > 1e-8: raise SystemExit("W^u anchor failed: no spec is written")
    # W^s side, built in the LINEAR regime at z_c (distance ~1e-5 from L4): drop z_c's u-part, evolve its stable-plane
    # coordinates under the linearised flow until the stable radius is RHO; that fixes phi* and t* with no winding ambiguity.
    from scipy.linalg import expm
    from scipy.optimize import brentq
    Bm = Tis @ J4(L4) @ Ts; Bs = Bm[:2, :2]; cs = (Tis @ (zc - L4))[:2]
    rad = lambda t: np.linalg.norm(expm(Bs * t) @ cs) - RHO
    tstar = brentq(rad, 0.0, 60.0); sv = expm(Bs * tstar) @ cs; ph = np.arctan2(sv[1], sv[0])
    zE_ = L4 + RHO * (np.cos(ph) * Ts[:, 0] + np.sin(ph) * Ts[:, 1])
    o = solve_ivp(lambda t, s: -f4(s), (0, tstar), zE_, method="DOP853", **RT); taub = tstar
    print("   W^s side (linear seam): t* %.5f phi* %.5f, seam at z_c %.2e (u-part of z_c %.2e)" % (tstar, ph, np.linalg.norm(o.y[:, -1] - zc), np.linalg.norm((Tis @ (zc - L4))[2:])), flush=True)
    Ttot = t1 + tc + taub; n = int(round(Ttot / TSEG)); Tg = Ttot / n
    z0 = L4 + RHO * (np.cos(th) * Tu[:, 0] + np.sin(th) * Tu[:, 1]); zE = L4 + RHO * (np.cos(ph) * Ts[:, 0] + np.sin(ph) * Ts[:, 1])
    sF = solve_ivp(lambda t, s: f4(s), (0, t1), z0, method="DOP853", dense_output=True, **RT)
    sB = solve_ivp(lambda t, s: -f4(s), (0, taub), zE, method="DOP853", dense_output=True, **RT)
    def at(t):
        if t <= t1: return sF.sol(t)
        if t <= t1 + tc: return sf.sol(t - t1)
        return sB.sol(Ttot - t)
    # adaptive segments: each segment's |D phi| <= 8 (CKMJ subdivide their steps the same way); one shared T, fractions c_i
    bnds = [0.0]; t = 0.0
    while t < Ttot - 1e-12:
        dt = min(0.5, Ttot - t)
        while dt > 1e-3 and np.linalg.norm(flow(at(t), dt, 0.0, var=True)[1], 2) > 8.0: dt /= 2
        t = t + dt; bnds.append(min(t, Ttot))
    bnds[-1] = Ttot; n = len(bnds) - 1; Tg = Ttot / n; cfr = [(bnds[i + 1] - bnds[i]) / Tg for i in range(n)]
    times = bnds[1:-1]; nodes = [at(t) for t in times]
    kk = int(np.argmin([abs(t - t1) for t in times])) + 1; tb, tf = t1, tc + taub
    print("  float: adaptive segments n %d, shortest %.4f, longest %.4f" % (n, min(np.diff(bnds)), max(np.diff(bnds))), flush=True)
    print("  float: n %d Tseg %.5f kk %d" % (n, Tg, kk), flush=True)
    wu = lambda a: L4 + RHO * (np.cos(a) * Tu[:, 0] + np.sin(a) * Tu[:, 1]); ws = lambda a: L4 + RHO * (np.cos(a) * Ts[:, 0] + np.sin(a) * Ts[:, 1])
    dwu = lambda a: RHO * (-np.sin(a) * Tu[:, 0] + np.cos(a) * Tu[:, 1]); dws = lambda a: RHO * (-np.sin(a) * Ts[:, 0] + np.cos(a) * Ts[:, 1])
    # ---- bvp2 (A12): Cartesian endpoints u, s in R^2, FIXED segment times, phase row at node kk (fast flow there)
    tau = [c * Tg for c in cfr]; Dm = 4 * n + 1; cs = 2 + 4 * (n - 1)
    u0 = RHO * np.array([np.cos(th), np.sin(th)]); s0 = RHO * np.array([np.cos(ph), np.sin(ph)])
    xref = np.array(nodes[kk - 1]); gph = f4(xref); gph = gph / np.linalg.norm(gph)
    wuC = lambda u: L4 + Tu[:, 0] * u[0] + Tu[:, 1] * u[1]; wsC = lambda s_: L4 + Ts[:, 0] * s_[0] + Ts[:, 1] * s_[1]
    X = np.concatenate([u0, np.ravel(nodes), s0, [0.0]])
    def split(Xv): return Xv[0:2], Xv[2:cs].reshape(n - 1, 4), Xv[cs:cs + 2], Xv[-1]
    def resid(Xv):
        u, xs, s_, al = split(Xv); pts = [wuC(u)] + list(xs); R = np.zeros(Dm)
        for i in range(n): R[4 * i:4 * i + 4] = flow(pts[i], tau[i], al) - (xs[i] if i < n - 1 else wsC(s_))
        R[-1] = gph @ (xs[kk - 1] - xref); return R
    for it in range(NIT):
        u, xs, s_, al = split(X); pts = [wuC(u)] + list(xs); Fv = np.zeros(Dm); DF = np.zeros((Dm, Dm))
        for i in range(n):
            zT, Phi, fz, da = flow(pts[i], tau[i], al, var=True); Fv[4 * i:4 * i + 4] = zT - (xs[i] if i < n - 1 else wsC(s_))
            if i == 0: DF[0:4, 0] = Phi @ Tu[:, 0]; DF[0:4, 1] = Phi @ Tu[:, 1]
            else: DF[4 * i:4 * i + 4, 2 + 4 * (i - 1):2 + 4 * i] = Phi
            if i < n - 1: DF[4 * i:4 * i + 4, 2 + 4 * i:6 + 4 * i] = -np.eye(4)
            else: DF[4 * i:4 * i + 4, cs] = -Ts[:, 0]; DF[4 * i:4 * i + 4, cs + 1] = -Ts[:, 1]
            DF[4 * i:4 * i + 4, Dm - 1] = da
        Fv[-1] = gph @ (xs[kk - 1] - xref); DF[-1, 2 + 4 * (kk - 1):6 + 4 * (kk - 1)] = gph
        nF = np.max(np.abs(Fv)); print("   newton %d |F| %.2e" % (it, nF), flush=True)
        if nF < 1e-13: break
        dX = np.linalg.solve(DF, Fv); lam = 1.0
        while lam > 1e-6:
            Ft = resid(X - lam * dX)
            if np.linalg.norm(Ft) < np.linalg.norm(Fv): break
            lam /= 2
        if lam <= 1e-6:
            if nF < 1e-12: break
            raise SystemExit("bvp2 float Newton stalled: no spec is written")
        X = X - lam * dX
    else:
        if nF > 1e-12: raise SystemExit("bvp2 float Newton did not converge: no spec is written")
    sv = np.linalg.svd(DF, compute_uv=False); A = np.linalg.inv(DF)
    u, xs, s_, al = split(X)
    print("  bvp2 float: cond %.2e ||A||_inf %.2e |u| %.3e |s| %.3e alpha %.1e" % (sv[0] / sv[-1], np.max(np.sum(np.abs(A), 1)), np.linalg.norm(u), np.linalg.norm(s_), al), flush=True)
    if os.environ.get("L4FLOATONLY"): raise SystemExit("float only")
    xk = xs[kk - 1]
    from scipy.optimize import minimize_scalar
    dist = lambda t: np.linalg.norm((flow(xk, t) if t >= 0 else solve_ivp(lambda tt, s: -f4(s), (0, -t), xk, method="DOP853", **RT).y[:, -1]) - pb)
    res = minimize_scalar(dist, bounds=(-1.0, 1.0), method="bounded", options=dict(xatol=1e-12)); tsh = res.x
    print("  bvp2 float: node %d -> p-bar after t = %.6f: float distance %.2e" % (kk, tsh, res.fun), flush=True)
    sp = dict(base, n=str(n), u=[d17(v) for v in u], s=[d17(v) for v in s_], x=[d17(v) for v in np.ravel(xs)], Tseg=d17(Tg), cfrac=[d17(c) for c in cfr],
              Tu=[d17(v) for v in Tu.ravel()], Lu=cones["u"]["L"], Ts=[d17(v) for v in Ts.ravel()], Ls=cones["s"]["L"],
              deltastar_u=cones["u"]["deltastar"], deltastar_s=cones["s"]["deltastar"], A=[d17(a) for a in A.ravel()], rmin="1e-20",
              kk=str(kk), g=[d17(v) for v in gph], xref=[d17(v) for v in xref], pbar=PBAR, tshift=d17(tsh))
    Am = [[mp.mpf(d17(A[i][j])) for j in range(Dm)] for i in range(Dm)]
    for rp in range(3):
        writespec(os.path.join(D, "bvp2_pt%d.spec" % rp), dict(sp, pointonly="1"))
        txt = run("bvp2", os.path.join(D, "bvp2_pt%d.spec" % rp), os.path.join(D, "bvp2_pt%d.out" % rp))
        F = {int(m_.group(1)): mp.mpf(m_.group(2)) for m_ in re.finditer(r"^F\[(\d+)\] \S+ mid (\S+)$", txt, re.M)}
        print("   refine %d: max |F mid| %s" % (rp, mp.nstr(max(abs(v) for v in F.values()), 3)), flush=True)
        Xm = [mp.mpf(v) for v in sp["u"]] + [mp.mpf(v) for v in sp["x"]] + [mp.mpf(v) for v in sp["s"]] + [mp.mpf(0)]
        X2 = [Xm[i] - mp.fsum(Am[i][j] * F[j] for j in range(Dm)) for i in range(Dm)]
        sp["u"] = [d40(v) for v in X2[0:2]]; sp["x"] = [d40(v) for v in X2[2:cs]]; sp["s"] = [d40(v) for v in X2[cs:cs + 2]]
    writespec(os.path.join(D, "bvp2.spec"), sp)
    txt = run("bvp2", os.path.join(D, "bvp2.spec"), os.path.join(D, "bvp2.out"))
    r_ = re.search(r"^RESULT l4bvp krawczyk (\S+) ckmj (\S+)", txt, re.M)
    out = dict(n=n, krawczyk=r_.group(1) if r_ else "FAIL", ckmj=r_.group(2) if r_ else "NO", cones=cones, seconds=time.time() - t00,
               lines=[l for l in txt.splitlines() if l.startswith(("KRAWCZYK", "BALL", "CKMJ", "RESULT"))])
    json.dump(out, open(js, "w"), indent=1); print("  l4", out["krawczyk"], "ckmj", out["ckmj"], flush=True)


if __name__ == "__main__":
    main()
