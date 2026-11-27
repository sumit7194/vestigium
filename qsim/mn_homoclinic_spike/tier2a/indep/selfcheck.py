"""Self-checks for mn_indep.py.  Run: nice -n 10 <venv python> -I selfcheck.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpmath import mp, mpf, sqrt, log, nstr, diff, legendre
import mn_indep as mn

mp.dps = 60
print("mp.dps =", mp.dps)
M, chi, alpha, k = mn._params()
print("params: M =", nstr(M, 20), " chi =", nstr(chi, 20), " alpha =", nstr(alpha, 40),
      " k =", nstr(k, 40))
print("  alpha + 1/3 =", nstr(alpha + mpf(1) / 3, 5), "  k - 4 =", nstr(k - 4, 5))

# ---------------------------------------------------------------- check 1
# Textbook Boyer-Lindquist Kerr (contravariant), G=c=1, sig (-,+,+,+):
#  Sigma = r^2 + a^2 cos^2, Delta = r^2 - 2 M r + a^2
#  g^tt = -((r^2+a^2)^2 - a^2 Delta sin^2)/(Sigma Delta), g^tphi = -2 M a r/(Sigma Delta)
#  g^phiphi = (Delta - a^2 sin^2)/(Sigma Delta sin^2), g^rr = Delta/Sigma, g^thth = 1/Sigma
# r = M + kK x, cos(theta) = y (theta in (0, pi), sin > 0)
# p_r = p_x / (dr/dx) = p_x / kK ;  p_theta = p_y dy/dtheta = -sin(theta) p_y
def H_kerr(x, y, px, py, E, L):
    Mk, ak = mpf(5), mpf(3)
    kK = sqrt(Mk**2 - ak**2)
    r = Mk + kK * x
    c = y
    s2 = 1 - c**2
    Sig = r**2 + ak**2 * c**2
    Del = r**2 - 2 * Mk * r + ak**2
    gtt = -((r**2 + ak**2)**2 - ak**2 * Del * s2) / (Sig * Del)
    gtp = -2 * Mk * ak * r / (Sig * Del)
    gpp = (Del - ak**2 * s2) / (Sig * Del * s2)
    grr = Del / Sig
    gthth = 1 / Sig
    pr = px / kK
    pth = -sqrt(s2) * py
    pt, pp = -E, L
    return (gtt * pt**2 + 2 * gtp * pt * pp + gpp * pp**2 + grr * pr**2 + gthth * pth**2) / 2

pts = [  # x, y, px, py, E, L
    ("2.5", "0.0", "1.0", "2.0", "0.95", "3.2"),
    ("3.1", "0.3", "-4.5", "1.5", "0.93", "2.9"),
    ("4.0", "-0.45", "7.0", "-3.0", "0.97", "-2.5"),
    ("4.7", "0.6", "-2.25", "9.5", "0.9", "3.6"),
    ("5.5", "-0.6", "3.3", "-8.0", "0.96", "4.1"),
    ("6.2", "0.12", "-9.8", "5.5", "0.94", "-3.3"),
    ("7.0", "-0.21", "1.7", "-1.1", "0.98", "3.0"),
    ("8.3", "0.5", "-6.1", "7.7", "0.92", "2.2"),
    ("9.1", "-0.33", "4.4", "2.6", "0.95", "5.0"),
    ("10.0", "0.58", "-1.2", "-6.6", "0.97", "-4.4"),
    ("11.0", "-0.05", "8.8", "3.9", "0.99", "3.7"),
    ("2.75", "0.41", "-3.7", "-4.2", "0.91", "2.6"),
]
print("\n== Check 1: beta = 0 vs textbook BL Kerr (M=5, a=3) ==")
worst = mpf(0); worstF = mpf(0)
for p in pts:
    x, y, px, py, E, L = [mpf(v) for v in p]
    h1 = mn.H(x, y, px, py, 0, E, L)
    h2 = H_kerr(x, y, px, py, E, L)
    rel = abs(h1 - h2) / abs(h2)
    worst = max(worst, rel)
    # field vs Kerr field (both by mpmath.diff)
    F1 = mn.field(x, y, px, py, 0, E, L)
    F2 = (diff(lambda s: H_kerr(x, y, s, py, E, L), px),
          diff(lambda s: H_kerr(x, y, px, s, E, L), py),
          -diff(lambda s: H_kerr(s, y, px, py, E, L), x),
          -diff(lambda s: H_kerr(x, s, px, py, E, L), y))
    relF = max(abs(a - b) / max(abs(b), mpf(10)**-30) for a, b in zip(F1, F2))
    worstF = max(worstF, relF)
    print(f"  x={p[0]:>5} y={p[1]:>5}  H_MN={nstr(h1, 25):>30}  H_Kerr={nstr(h2, 25):>30}"
          f"  rel={nstr(rel, 3)}  field maxrel={nstr(relF, 3)}")
print("  WORST H rel diff =", nstr(worst, 3), "  WORST field rel diff =", nstr(worstF, 3),
      "  PASS" if worst <= mpf(10)**-30 else "  FAIL")

# ---------------------------------------------------------------- check 2
print("\n== Check 2: asymptotics (M, J, omega) ==")
for beta in (mpf(0), mpf(3) / 100):
    print(f"  beta = {nstr(beta, 5)}")
    for y in (mpf(0), mpf("0.5")):
        for X in (mpf(10)**8, mpf(10)**12, mpf(10)**16):
            g_tt, g_tp, g_pp, g_xx, g_yy = mn.metric(X, y, beta)
            mf = mn.metric_functions(X, y, beta)
            r = M + k * X                      # Kerr-limit BL radius
            s2 = 1 - y**2
            M_est = (1 + g_tt) * r / 2
            J_est = -g_tp * r / (2 * s2)
            print(f"    y={nstr(y, 3)} x=1e{int(log(X, 10) + mpf('0.5'))}: M_est={nstr(M_est, 25)}"
                  f"  J_est={nstr(J_est, 25)}  omega={nstr(mf['omega'], 5)}"
                  f"  e2gamma-1={nstr(mf['e2gamma'] - 1, 5)}")
const = -4 * k * alpha / (1 - alpha**2)
print("  gauge constant -4 k alpha/(1-alpha^2) =", nstr(const, 30))
print("  omega at x=1e30, y=0.3, beta=3/100:", nstr(mn.metric_functions(mpf(10)**30, mpf("0.3"), mpf(3) / 100)['omega'], 5))

# ---------------------------------------------------------------- check 3
print("\n== Check 3: mass quadrupole ==")
# Paper eq. (4): M2 = -k^3 [beta + 4 alpha^2 (1+alpha^2)(1-alpha^2)^-3]
# Numerical: on the axis (y = 1, z = k x), Re xi = (1-f)/(1+f) + O(z^-4),
# with xi = (1-E)/(1+E) the Ernst potential; FHP: xi = sum m_j z^-(j+1), M2 = Re m2.
def M2_paper(beta):
    return -k**3 * (beta + 4 * alpha**2 * (1 + alpha**2) / (1 - alpha**2)**3)

def M2_numeric(beta, z):
    X = z / k
    mf = mn.metric_functions(X, mpf(1), beta)   # y = 1 exactly (axis)
    f = mf['f']
    g = z * (1 - f) / (1 + f)                   # = m0 + m1/z + m2/z^2 + m3/z^3 + ...
    return (g - M) * z**2                       # m1 = 0, m3 real part = M3 = 0

# Axis evaluation check: y = 1 is allowed in metric_functions (A,B,C,f finite)
for beta in (mpf(0), mpf(3) / 100, mpf(-3) / 100, mpf("0.5")):
    nums = [M2_numeric(beta, mpf(10)**e) for e in (6, 8, 10)]
    print(f"  beta={nstr(beta, 4):>6}: M2 paper eq.(4) = {nstr(M2_paper(beta), 25):>28};"
          f" numeric (z=1e6,1e8,1e10) = {', '.join(nstr(n, 20) for n in nums)}")
    print(f"           M2 - M2_Kerr = {nstr(M2_paper(beta) - M2_paper(0), 20)} (= -k^3 beta = {nstr(-k**3 * beta, 20)});"
          f"  q = -(M2-M2Kerr)/M^3 = {nstr(-(M2_paper(beta) - M2_paper(0)) / M**3, 20)}")
print("  Kerr M2 = -M a^2 =", -5 * 9)

# ---------------------------------------------------------------- extra checks
print("\n== Extra A: gamma' on the axis / at infinity (typo resolution in eq. 3h) ==")
for beta in (mpf(3) / 100, mpf("0.5")):
    for X in (mpf(2), mpf(7)):
        gp = mn.metric_functions(X, mpf(1), beta)['gammap']
        e2 = mn.metric_functions(X, mpf(1), beta)['e2gamma']
        print(f"  beta={nstr(beta, 3)} y=1 x={nstr(X, 3)}: gamma'={nstr(gp, 5)}  e^(2gamma)-1={nstr(e2 - 1, 5)}"
              f"   [literal '-2 inside sum' would give gamma' - 4 beta = {nstr(gp - 4 * beta, 5)}]")
    gp_inf = mn.metric_functions(mpf(10)**20, mpf("0.3"), beta)['gammap']
    print(f"  beta={nstr(beta, 3)} x=1e20 y=0.3: gamma'={nstr(gp_inf, 5)}")

print("\n== Extra B: Legendre via mpmath.legendre vs explicit polynomials ==")
u = mpf("0.3141592653")
expl = [1, u, (3 * u**2 - 1) / 2, (5 * u**3 - 3 * u) / 2]
print("  max |diff| =", nstr(max(abs(legendre(n, u) - expl[n]) for n in range(4)), 3))

print("\n== Extra C: vacuum field equations in Weyl (rho, z), beta = 0 and 3/100 ==")
# ds^2 = -f(dt - w dphi)^2 + f^-1[e^{2g}(drho^2+dz^2) + rho^2 dphi^2]
# R1 = f lap f - |grad f|^2 + f^4 rho^-2 |grad w|^2            (= 0)
# R2 = d_rho(rho^-1 f^2 w_rho) + d_z(rho^-1 f^2 w_z)           (= 0)
# R3 = g_rho - [rho/(4f^2)(f_rho^2 - f_z^2) - f^2/(4 rho)(w_rho^2 - w_z^2)]
# R4 = g_z   - [rho/(2f^2) f_rho f_z - f^2/(2 rho) w_rho w_z]
def to_xy(rho, z):
    rp = sqrt(rho**2 + (z + k)**2); rm = sqrt(rho**2 + (z - k)**2)
    return (rp + rm) / (2 * k), (rp - rm) / (2 * k)

def fns(rho, z, beta, which):
    X, Y = to_xy(rho, z)
    m = mn.metric_functions(X, Y, beta)
    if which == 'f': return m['f']
    if which == 'w': return m['omega']
    return log(m['e2gamma']) / 2

for beta in (mpf(0), mpf(3) / 100, mpf("0.5")):
    for (X0, Y0) in ((mpf(3), mpf("0.3")), (mpf("6.5"), mpf("-0.55"))):
        rho = k * sqrt((X0**2 - 1) * (1 - Y0**2)); z = k * X0 * Y0
        d = lambda w, n: diff(lambda a, b: fns(a, b, beta, w), (rho, z), n)
        f = fns(rho, z, beta, 'f'); w = fns(rho, z, beta, 'w')
        fr, fz, frr, fzz = d('f', (1, 0)), d('f', (0, 1)), d('f', (2, 0)), d('f', (0, 2))
        wr, wz, wrr, wzz = d('w', (1, 0)), d('w', (0, 1)), d('w', (2, 0)), d('w', (0, 2))
        gr, gz = d('g', (1, 0)), d('g', (0, 1))
        t1 = [f * (frr + fr / rho + fzz), fr**2 + fz**2, f**4 / rho**2 * (wr**2 + wz**2)]
        R1 = t1[0] - t1[1] + t1[2]
        t2 = [f**2 / rho * (wrr + wzz), f**2 * wr / rho**2, 2 * f / rho * (fr * wr + fz * wz)]
        R2 = t2[0] - t2[1] + t2[2]
        t3 = [gr, rho / (4 * f**2) * (fr**2 - fz**2), f**2 / (4 * rho) * (wr**2 - wz**2)]
        R3 = t3[0] - t3[1] + t3[2]
        t4 = [gz, rho / (2 * f**2) * fr * fz, f**2 / (2 * rho) * wr * wz]
        R4 = t4[0] - t4[1] + t4[2]
        sc = lambda t: max(abs(v) for v in t)
        print(f"  beta={nstr(beta, 3)} (x,y)=({nstr(X0, 3)},{nstr(Y0, 3)}): rel residuals "
              f"R1={nstr(R1 / sc(t1), 3)} R2={nstr(R2 / sc(t2), 3)} R3={nstr(R3 / sc(t3), 3)} R4={nstr(R4 / sc(t4), 3)}")

print("\n== Extra D: derivative method cross-check (mpmath.diff step vs quad Cauchy contour; error / max(abs(value),1)) ==")
for p in pts[:4]:
    x, y, px, py, E, L = [mpf(v) for v in p]
    b0 = mpf(3) / 100
    s_x = diff(lambda s: mn.H(s, y, px, py, b0, E, L), x)
    q_x = diff(lambda s: mn._H(s, y, px, py, b0, E, L), x, method='quad', radius=mpf("0.25"))
    s_y = diff(lambda s: mn.H(x, s, px, py, b0, E, L), y)
    q_y = diff(lambda s: mn._H(x, s, px, py, b0, E, L), y, method='quad', radius=mpf("0.1"))
    s_b = mn.dH_dbeta(x, y, px, py, E, L)
    q_b = diff(lambda s: mn._H(x, y, px, py, s, E, L), mpf(0), method='quad', radius=mpf("0.01"))
    print(f"  x={p[0]:>4} y={p[1]:>5}: dH/dx rel={nstr(abs(s_x - q_x) / max(abs(s_x), 1), 3)}"
          f"  dH/dy rel={nstr(abs(s_y - q_y) / max(abs(s_y), 1), 3)}  dH/dbeta|0 = {nstr(s_b, 25)} rel={nstr(abs(s_b - q_b) / max(abs(s_b), 1), 3)}")

print("\n== Sample outputs (beta = 3/100) ==")
for p in pts[:3]:
    x, y, px, py, E, L = p
    print("  H     =", nstr(mn.H(x, y, px, py, "0.03", E, L), 30))
    print("  field =", [nstr(v, 25) for v in mn.field(x, y, px, py, "0.03", E, L)])
    print("  dH/dbeta|0 =", nstr(mn.dH_dbeta(x, y, px, py, E, L), 30))
