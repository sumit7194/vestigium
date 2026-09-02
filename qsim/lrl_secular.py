#!/usr/bin/env python3
"""Is the orbit-averaged Poisson bracket a valid destroyer-test for the LRL vector?

THE LEMMA. H = H0 + e*H1 with H0 Kepler. Q = LRL vector, {H0,Q} = 0. Then
dQ/dt = e*{Q,H1}, so to first order Q(t) = Q(0) + e*(A*t + F1(t)) where A is
the average of {Q,H1} over a CLOSED UNPERTURBED orbit and F1 is the oscillating
remainder. A != 0 forces a secular drift, so A != 0 PROVES Q does not survive.
A = 0 proves nothing -- it is a necessary condition only.

WHAT IS TESTED HERE, in the order that matters:

  CALIBRATION   {H0, A_i} = 0 pointwise, and the so(3) algebra {L_z,A_x} = -A_y.
                An instrument that cannot reproduce these is measuring nothing.
  TRIVIAL       H1 = -1/r, i.e. a change of the Kepler constant k. Maps Kepler to
                Kepler, so the OLD A is not conserved but is exactly periodic ->
                the average MUST vanish identically in (a,e). The bracket is
                NONZERO POINTWISE, so this catches an instrument that is
                measuring the parametrisation. This is the control people skip.
  NEGATIVE      H1 = H0. Bracket vanishes pointwise. Tests the algebra only.
  POSITIVE      H1 = beta/r^2. Known to precess the perihelion; the analytic
                secular rate is in the literature and is reproduced below.
  POSITIVE-2    H1 = F.r (uniform field). Non-central, so it also tests the
                vector structure that the central case hides by parity.

Every average is computed by TWO independent routes: closed-form quadrature in
the true anomaly using the exact Kepler parametrisation, and time-averaging
along a numerically integrated unperturbed orbit. They share no code path.

Then the lemma itself is tested dynamically: the FULL perturbed system is
integrated for many orbits and the measured secular drift of A is compared with
e*A*t. That checks the lemma, not merely this implementation of it.
"""
import numpy as np
from scipy.integrate import solve_ivp, quad

K = 1.0                                   # Kepler constant; unit mass throughout


# ---------------------------------------------------------------- kinematics
def kepler_state(a, e, th, k=K):
    """Exact Kepler orbit at true anomaly th, perihelion along +x, L along +z."""
    p_s = a*(1.0 - e*e)
    r = p_s/(1.0 + e*np.cos(th))
    L = np.sqrt(k*p_s)
    rdot = (k/L)*e*np.sin(th)
    thdot = L/(r*r)
    er = np.array([np.cos(th), np.sin(th), 0.0])
    et = np.array([-np.sin(th), np.cos(th), 0.0])
    return r*er, rdot*er + r*thdot*et


def lrl(rv, pv, k=K):
    return np.cross(pv, np.cross(rv, pv)) - k*rv/np.linalg.norm(rv)


def H0(rv, pv, k=K):
    return 0.5*pv @ pv - k/np.linalg.norm(rv)


def period(a, k=K):
    return 2.0*np.pi*a**1.5/np.sqrt(k)


# ------------------------------------------------------- Poisson brackets
def pb_numeric(F, G, rv, pv, h=1e-6):
    """{F,G} by central differences. Used ONLY to calibrate the analytic form."""
    out = 0.0
    for j in range(3):
        d = np.zeros(3); d[j] = h
        dFdr = (F(rv+d, pv) - F(rv-d, pv))/(2*h)
        dGdp = (G(rv, pv+d) - G(rv, pv-d))/(2*h)
        dFdp = (F(rv, pv+d) - F(rv, pv-d))/(2*h)
        dGdr = (G(rv+d, pv) - G(rv-d, pv))/(2*h)
        out += dFdr*dGdp - dFdp*dGdr
    return out


def dA_dp(rv, pv):
    """M[i,j] = dA_i/dp_j = 2 p_j r_i - r_j p_i - (r.p) delta_ij.  Derived, then
    calibrated below against pb_numeric."""
    rp = rv @ pv
    return 2.0*np.outer(rv, pv) - np.outer(pv, rv) - rp*np.eye(3)


def bracket_H1_A(gradH1_r, rv, pv):
    """{H1, A} for momentum-independent H1: sum_j (dH1/dr_j) M[i,j]."""
    return dA_dp(rv, pv) @ gradH1_r


# --------------------------------------------------------- perturbations
class Pert:
    def __init__(self, name, kind, V, gradV, note):
        self.name, self.kind, self.V, self.gradV, self.note = name, kind, V, gradV, note


def make_perts(dk=1.0, beta=1.0, Fvec=np.array([1.0, 0.0, 0.0])):
    def V_dk(rv):     return -dk/np.linalg.norm(rv)
    def g_dk(rv):
        r = np.linalg.norm(rv); return dk*rv/r**3
    def V_r2(rv):     return beta/ (np.linalg.norm(rv)**2)
    def g_r2(rv):
        r = np.linalg.norm(rv); return -2.0*beta*rv/r**4
    def V_st(rv):     return Fvec @ rv
    def g_st(rv):     return Fvec.copy()
    return [
        Pert("TRIVIAL  dk/r      ", "trivial",  V_dk, g_dk,
             "change of Kepler constant: Kepler -> Kepler, A must average to zero"),
        Pert("POSITIVE beta/r^2  ", "positive", V_r2, g_r2,
             "known perihelion precession; analytic rate below"),
        Pert("POSITIVE F.r       ", "positive", V_st, g_st,
             "uniform field, non-central: tests the vector structure"),
    ]


# --------------------------------------------------- route A: true-anomaly
def A_avg_theta(pert, a, e, k=K, n=20001):
    """Average of {H1,A} over one orbit, exact Kepler parametrisation.
    dt = r^2 dtheta / L, so <X> = (1/T) * integral X r^2 dtheta / L."""
    th = np.linspace(0.0, 2.0*np.pi, n)
    L = np.sqrt(k*a*(1.0 - e*e))
    acc = np.zeros((n, 3))
    w = np.empty(n)
    for i, t in enumerate(th):
        rv, pv = kepler_state(a, e, t, k)
        acc[i] = bracket_H1_A(pert.gradV(rv), rv, pv)
        w[i] = (rv @ rv)/L
    T = period(a, k)
    return np.trapezoid(acc*w[:, None], th, axis=0)/T


# ------------------------------------------------------- route B: ODE time
def A_avg_time(pert, a, e, k=K, rtol=1e-12, atol=1e-13):
    """Average along a numerically integrated UNPERTURBED orbit. Shares no code
    path with route A: different parametrisation, different quadrature."""
    rv0, pv0 = kepler_state(a, e, 0.0, k)
    T = period(a, k)

    def rhs(t, y):
        r = y[:3]; p = y[3:]
        rn = np.linalg.norm(r)
        return np.concatenate([p, -k*r/rn**3])

    ts = np.linspace(0.0, T, 4001)
    sol = solve_ivp(rhs, (0.0, T), np.concatenate([rv0, pv0]), t_eval=ts,
                    rtol=rtol, atol=atol, method="DOP853")
    vals = np.array([bracket_H1_A(pert.gradV(sol.y[:3, i]), sol.y[:3, i], sol.y[3:, i])
                     for i in range(len(ts))])
    return np.trapezoid(vals, ts, axis=0)/T


# ------------------------------------------------ dynamical validation
def measured_drift(pert, a, e, eps, n_orb=60, k=K):
    """Integrate the FULL perturbed system and measure the secular rate of A.

    NOT by fitting A_y(t) to a line: the secular motion of A is a ROTATION, so
    A_y is linear only while the turn angle is small -- which would make this a
    small-eps check, exactly the crutch the ask rules out. Instead track the
    UNWRAPPED angle of A in the plane, which is linear for arbitrarily many
    turns, and convert: at t=0, A = (k e, 0, 0), so dA_y/dt = |A| dphi/dt.
    Sampled STROBOSCOPICALLY at whole unperturbed periods so the orbit-periodic
    part is evaluated at the same phase every time and drops out of the fit."""
    rv0, pv0 = kepler_state(a, e, 0.0, k)
    T = period(a, k)

    def rhs(t, y):
        r = y[:3]; p = y[3:]
        rn = np.linalg.norm(r)
        return np.concatenate([p, -k*r/rn**3 - eps*pert.gradV(r)])

    ts = np.arange(n_orb + 1)*T                      # stroboscopic, one per orbit
    sol = solve_ivp(rhs, (0.0, ts[-1]), np.concatenate([rv0, pv0]), t_eval=ts,
                    rtol=1e-12, atol=1e-13, method="DOP853")
    Av = np.array([lrl(sol.y[:3, i], sol.y[3:, i], k) for i in range(len(ts))])
    phi = np.unwrap(np.arctan2(Av[:, 1], Av[:, 0]))
    mag = np.linalg.norm(Av, axis=1)
    rate = np.polyfit(ts, phi, 1)[0]*mag.mean()
    return rate, (mag.max() - mag.min())/mag.mean(), phi[-1] - phi[0]


# ============================================================ CALIBRATION
def calibrate():
    """Known answers, checked before the instrument is used for anything."""
    rng = np.random.default_rng(7)
    print("CALIBRATION -- known identities, numeric bracket vs analytic form\n")
    worst_h0, worst_alg, worst_M = 0.0, 0.0, 0.0
    for _ in range(200):
        a = rng.uniform(0.6, 2.5); e = rng.uniform(0.05, 0.85)
        th = rng.uniform(0, 2*np.pi)
        rv, pv = kepler_state(a, e, th)
        scale = np.linalg.norm(lrl(rv, pv)) + 1e-30

        # (1) {H0, A_i} = 0 exactly -- A is conserved by the unperturbed flow
        for i in range(3):
            b = pb_numeric(lambda r, p: H0(r, p),
                           lambda r, p, i=i: lrl(r, p)[i], rv, pv)
            worst_h0 = max(worst_h0, abs(b)/scale)

        # (2) so(3): {L_i, A_j} = eps_ijk A_k, so {L_z,A_x}=+A_y, {L_z,A_y}=-A_x.
        # THE ORBIT MUST BE ROTATED FIRST. With perihelion fixed along +x, A_y is
        # identically zero and the first relation reads 0 = 0 -- a test that
        # passes for any implementation. Caught because the UNROTATED version
        # failed at exactly 2.0, which is |2*A_x|/|A| when A lies along x.
        c, s = np.cos(1.1), np.sin(1.1)
        R = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
        rr, pr = R @ rv, R @ pv
        Ar = lrl(rr, pr)
        Lz = lambda r, p: np.cross(r, p)[2]
        b1 = pb_numeric(Lz, lambda r, p: lrl(r, p)[0], rr, pr)
        b2 = pb_numeric(Lz, lambda r, p: lrl(r, p)[1], rr, pr)
        worst_alg = max(worst_alg, abs(b1 - Ar[1])/scale, abs(b2 + Ar[0])/scale)

        # (2b) so(4), non-degenerate and independent of (2): {A_x,A_y} = -2 H0 L_z
        bAA = pb_numeric(lambda r, p: lrl(r, p)[0], lambda r, p: lrl(r, p)[1], rr, pr)
        pred = -2.0*H0(rr, pr)*np.cross(rr, pr)[2]
        worst_alg = max(worst_alg, abs(bAA - pred)/(abs(pred) + 1e-12))

        # (3) the analytic dA/dp against finite differences
        M = dA_dp(rv, pv)
        for i in range(3):
            for j in range(3):
                d = np.zeros(3); d[j] = 1e-6
                num = (lrl(rv, pv+d)[i] - lrl(rv, pv-d)[i])/2e-6
                worst_M = max(worst_M, abs(num - M[i, j])/(abs(M[i, j]) + 1.0))

    print(f"   {'{H0, A_i} = 0':38s} worst |.|/|A| = {worst_h0:.2e}")
    print(f"   {'so(3)+so(4) algebra (rotated orbit)':38s} worst           = {worst_alg:.2e}")
    print(f"   {'dA_i/dp_j analytic vs numeric':38s} worst rel        = {worst_M:.2e}")
    ok = worst_h0 < 1e-6 and worst_alg < 1e-6 and worst_M < 1e-6
    print(f"\n   {'CALIBRATED' if ok else '*** CALIBRATION FAILED -- everything below is void ***'}")
    return ok


# ================================================== ANALYTIC PREDICTIONS
# For a central perturbation V=f(r) the bracket reduces, using
# V_ijk = (r.p) r - r^2 p = L r (sin th, -cos th, 0), to
#     {f(r), A} = L f'(r) (sin th, -cos th, 0)
# and with dt = r^2 dth / L the orbit average is
#     A_x = (1/T) INT f'(r) r^2 sin th dth      -> ZERO BY PARITY, always
#     A_y = -(1/T) INT f'(r) r^2 cos th dth
#
#   dk/r      : f' r^2 = dk (constant)  -> A_y = 0 IDENTICALLY in (a,e)
#   beta/r^2  : f' r^2 = -2 beta/r      -> A_y = 2 pi beta e / (T a (1-e^2))
#
# The second is not a fit: the known perihelion advance for a 1/r^2 term is
# -2 pi beta / L^2 per orbit, and |A| = k e, giving |dA/dt| = 2 pi beta k e/(L^2 T)
# = 2 pi beta e/(T a(1-e^2)) since L^2 = k a (1-e^2). Same expression.
def A_analytic(kind, a, e, beta=1.0, k=K):
    if kind == "dk":
        return np.zeros(3)
    if kind == "r2":
        return np.array([0.0, 2.0*np.pi*beta*e/(period(a, k)*a*(1.0 - e*e)), 0.0])
    return None


def pointwise_nonzero(pert, a, e, n=9):
    """Is {H1,A} nonzero AT POINTS, even where its average vanishes? If it is
    zero pointwise the trivial control proves nothing about the averaging."""
    m = 0.0
    for th in np.linspace(0.1, 2*np.pi - 0.1, n):
        rv, pv = kepler_state(a, e, th)
        m = max(m, np.linalg.norm(bracket_H1_A(pert.gradV(rv), rv, pv)))
    return m


# ================================================ THE UNSTATED HYPOTHESIS
# Averaging replaces A(t) by its mean drift. The step that makes this legal is
# the claim that the DISCARDED oscillating part is bounded: writing the
# first-order solution as
#       A(t) = A(0) + eps * <g> t + eps * F1(t),      g = {H1, A},
#       F1(th) = INT_0^th (g - <g>) r^2 dth' / L      (bounded, orbit-periodic)
# "F1 is bounded" is true for each fixed orbit -- but the lemma is used over an
# OPEN SET of orbits, and nobody states that the bound must be UNIFORM there.
# It is not. F1 diverges as e -> 1. That, not convergence, is where the
# hypothesis hides.
def F1_amplitude(pert, a, e, k=K, n=20001):
    """Peak-to-peak of the discarded oscillating part, in A_y."""
    th = np.linspace(0.0, 2*np.pi, n)
    L = np.sqrt(k*a*(1.0 - e*e))
    g = np.empty(n)
    r2 = np.empty(n)
    for i, t in enumerate(th):
        rv, pv = kepler_state(a, e, t, k)
        g[i] = bracket_H1_A(pert.gradV(rv), rv, pv)[1]
        r2[i] = rv @ rv
    w = r2/L                                   # dt/dth
    T = np.trapezoid(w, th)
    gbar = np.trapezoid(g*w, th)/T
    F1 = np.concatenate(([0.0], np.cumsum(0.5*(g[1:]*w[1:] - gbar*w[1:]
                                             + g[:-1]*w[:-1] - gbar*w[:-1])
                                          * np.diff(th))))
    return F1.max() - F1.min()


def validity_window(pert, a, e, k=K):
    """Secular theory needs the discarded oscillation small against the thing
    being tracked: eps |F1| << |A_LRL| = k e. Returns the eps at which they
    are equal."""
    return k*e/F1_amplitude(pert, a, e, k)


# =============================================================== REPORT
def report():
    perts = make_perts()
    triv, pos, stark = perts[0], perts[1], perts[2]
    A_GRID = (0.8, 1.3, 2.0)
    E_GRID = (0.1, 0.4, 0.7)

    print("\n" + "="*72)
    print("CONTROLS -- A over an (a,e) grid, two independent routes")
    print("="*72)
    for name, pert, kind in (("TRIVIAL  dk/r   (reparametrisation)", triv, "dk"),
                             ("POSITIVE beta/r^2 (destroys LRL)",    pos,  "r2"),
                             ("POSITIVE F.r    (Stark, non-central)", stark, None)):
        print(f"\n{name}")
        print(f"  {'a':>5}{'e':>6}{'A_y theta-quad':>17}{'A_y ODE-time':>15}"
              f"{'A_y analytic':>15}{'|A_x|':>11}{'|{H1,A}| ptwise':>17}")
        for a in A_GRID:
            for e in E_GRID:
                At = A_avg_theta(pert, a, e)
                Ao = A_avg_time(pert, a, e)
                An = A_analytic(kind, a, e) if kind else None
                ana = f"{An[1]:15.6e}" if An is not None else f"{'--':>15}"
                print(f"  {a:5.1f}{e:6.2f}{At[1]:17.6e}{Ao[1]:15.6e}{ana}"
                      f"{abs(At[0]):11.2e}{pointwise_nonzero(pert, a, e):17.4f}")

    print("\n" + "="*72)
    print("THE HIDDEN HYPOTHESIS -- is the F1 bound UNIFORM in e?")
    print("="*72)
    print(f"  {'e':>6}{'|F1| p-p':>13}{'|F1|(1-e)':>12}{'window eps':>13}"
          f"{'window/[e(1-e)]':>17}")
    for e in (0.10, 0.30, 0.50, 0.70, 0.90, 0.95, 0.99):
        f1 = F1_amplitude(pos, 1.3, e)
        w = validity_window(pos, 1.3, e)
        print(f"  {e:6.2f}{f1:13.2f}{f1*(1-e):12.3f}{w:13.4f}{w/(e*(1-e)):17.3f}")
    print("\n  |F1| ~ C/(1-e) with C constant  =>  window ~ (k/C) e (1-e),")
    print("  vanishing at BOTH ends: e->0 because there is no |A|=k e to destroy,")
    print("  e->1 because the discarded oscillation diverges.")

    print("\n" + "="*72)
    print("CONVERGENCE -- is the averaging integral only conditionally convergent?")
    print("="*72)
    print(f"  {'n exponent':>12}{'e':>7}{'A_y n=2001':>16}{'A_y n=32001':>16}{'rel diff':>12}")
    for n_exp in (2, 5):
        pn = Pert(f"beta/r^{n_exp}", "positive",
                  lambda rv, n=n_exp: 1.0/np.linalg.norm(rv)**n,
                  lambda rv, n=n_exp: -n*rv/np.linalg.norm(rv)**(n+2),
                  "steeper central term: worst case for pericentre convergence")
        for e in (0.90, 0.99):
            lo = A_avg_theta(pn, 1.3, e, n=2001)[1]
            hi = A_avg_theta(pn, 1.3, e, n=32001)[1]
            print(f"  {n_exp:12d}{e:7.2f}{lo:16.8e}{hi:16.8e}"
                  f"{abs(lo-hi)/abs(hi):12.2e}")
    print("\n  Absolutely convergent for every e<1 and every n: the integrand is")
    print("  f'(r) r^2 = -n beta (1+e cos th)^(n-1) / p^(n-1), BOUNDED in th.")
    print("  The r^2 dth measure cancels the pericentre singularity exactly.")

    print("\n" + "="*72)
    print("DYNAMICAL VALIDATION -- no reliance on eps being small in practice")
    print("="*72)
    print(f"  {'eps':>8}{'turns':>8}{'measured drift':>18}{'A predicts':>15}"
          f"{'ratio':>10}{'|A| drift':>12}")
    # n_orb ~ 1/eps, holding the TOTAL turn fixed near one revolution. With a
    # fixed n_orb the turn shrinks with eps, the fit degrades exactly where it
    # must be sharpest, and the ratio walks AWAY from 1 as eps -> 0 (measured:
    # 0.968, 0.993, 1.010, 1.030) -- an artifact of the diagnostic, not physics.
    ratios = []
    for eps in (0.02, 0.01, 0.005, 0.0025, 0.00125):
        meas, magdrift, turn = measured_drift(pos, 1.3, 0.4, eps,
                                              n_orb=int(round(1.2/eps)))
        pred = -eps*A_avg_theta(pos, 1.3, 0.4)[1]
        ratios.append((eps, meas/pred))
        print(f"  {eps:8.4f}{turn/(2*np.pi):8.2f}{meas:18.6e}{pred:15.6e}"
              f"{meas/pred:10.4f}{magdrift:12.2e}")
    (e1, r1), (e2, r2) = ratios[-2], ratios[-1]
    print(f"\n  deviations from 1: " + " ".join(f"{r-1:+.2e}" for _, r in ratios))
    print(f"  halving as eps halves => O(eps). Richardson to eps=0: "
          f"{2*r2 - r1:.5f}")
    print("  SIGN: dA/dt = eps {A,H1} = -eps {H1,A}, and A_avg averages {H1,A}.")
    print("  So the ask's A is MINUS the secular rate of the LRL vector; the")
    print("  ratio above is against -eps*A_avg and converges to +1.")


if __name__ == "__main__":
    import sys
    if not calibrate():
        sys.exit(1)
    report()
