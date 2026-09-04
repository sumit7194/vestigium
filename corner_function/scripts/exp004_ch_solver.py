"""
EXP-004: direct numerical solution of the Casini-Huerta(-Leitao) ODE system for the corner
function of a free scalar at finite angle.  Source of every equation: Casini, Huerta, Leitao,
Nucl.Phys.B 814 (2009) 594, Appendix B eqs (72)-(89) [= Casini-Huerta NPB 764 (2007) eqs (22)-(39)].

  tr G_S(x, M, a) = 8 pi (1-a) a  Int_x^pi H_a(y) dy                                     (72)
  ODEs (73)-(78) for (H, X1, X2, c, b, u); algebraic (79)-(83) for (B1, B2, B12, beta1, beta2);
  boundary values at x = pi: (84)-(89), mu1 = sqrt(4 M^2 - 1).
  Renyi-n, REAL scalar [CH07 eq (40)]:
     s_n(x) = sum_{k=1}^{n-1} 8k(n-k)/(n^2 (n-1)) Int_{1/2}^inf dM M sqrt(M^2-1/4) Int_x^pi H_{k/n}(y,M) dy
  EE, COMPLEX scalar [CHL09 eq (61)]:
     s_S(x) = Int_0^inf dt 2/cosh^2(pi t) Int_{1/2}^inf dM M sqrt(M^2-1/4) tr G_S(x, M, 1/2 - i t)

delta = pi - x. x = pi is a regular singular point; the solution is started from a power series
in delta whose coefficients are found by least squares on the coefficient equations (leading
orders derived by hand: beta1^1 beta2^1 = [a(a-1)+M^2(1+b0 c0)]/(4M^2), beta1^1 c0 = b0 beta2^1,
u^1 = M c0 beta1^1, H^1 = 1/(16 pi a(1-a)) + M(beta1^1 X2^0 + beta2^1 X1^0)).
The sign of beta^1 is a genuine two-fold ambiguity of the local expansion; branch -1 is physical:
branch +1 gives H^1(M) that does not decay in M, so its mass integral (sigma_2) cannot converge,
while branch -1 reproduces sigma_2 = 1/(48 pi^2) (see exp004_run.py output).
Mass integral: M = sqrt(1/4 + p^2), M sqrt(M^2-1/4) dM = p^2 dp.
"""
import numpy as np, sys, math
from math import pi
from scipy.special import gamma as Gamma, digamma
from scipy.optimize import least_squares
from scipy.integrate import solve_ivp

def bc_values(M, a):
    mu = np.sqrt(4*M*M - 1 + 0j)
    def Xpi(a):
        Impsi = (digamma(0.5 + a + 1j*mu/2) - digamma(0.5 + a - 1j*mu/2))/(2j)
        absG2 = Gamma(0.5 - a + 1j*mu/2)*Gamma(0.5 - a - 1j*mu/2)
        num = Gamma(-a)*(np.cosh(pi*mu/2)*Impsi - (pi/2)*np.sinh(pi*mu/2))
        den = 2**(2*a)*mu*(np.cos(2*a*pi) + np.cosh(pi*mu))*Gamma(1+a)*absG2
        return num/den
    def bpi(a):
        absG2 = Gamma(0.5 + a + 1j*mu/2)*Gamma(0.5 + a - 1j*mu/2)
        return 2**(1-2*a)*a*(1-a)*absG2/(M*Gamma(1+a)**2)
    return Xpi(a), Xpi(1-a), bpi(a), bpi(1-a)

class S:
    __slots__=('c','K')
    def __init__(s, c, K):
        c = np.asarray(c, dtype=complex)
        s.c = c[:K] if len(c)>=K else np.concatenate([c, np.zeros(K-len(c))]); s.K = K
    def __add__(s,o): return S(s.c + (o.c if isinstance(o,S) else np.concatenate([[o],np.zeros(s.K-1)])), s.K)
    __radd__ = __add__
    def __sub__(s,o): return s + (-1)*o
    def __rsub__(s,o): return (-1)*s + o
    def __mul__(s,o):
        if isinstance(o,S): return S(np.convolve(s.c,o.c)[:s.K], s.K)
        return S(s.c*o, s.K)
    __rmul__ = __mul__
    def Dx(s): return S(-np.arange(1,s.K)*s.c[1:], s.K)

def trig(K):
    f = np.array([1.0/math.factorial(i) for i in range(K)]); k = np.arange(K)
    sin_d  = S([0 if i%2==0 else ((-1)**((i-1)//2))*f[i] for i in k], K)
    cos_d  = S([((-1)**(i//2))*f[i] if i%2==0 else 0 for i in k], K)
    sin_h  = S([0 if i%2==0 else ((-1)**((i-1)//2))*f[i]/2**i for i in k], K)
    cos_h  = S([((-1)**(i//2))*f[i]/2**i if i%2==0 else 0 for i in k], K)
    cos_2d = S([((-1)**(i//2))*f[i]*2**i if i%2==0 else 0 for i in k], K)
    return sin_d, cos_d, sin_h, cos_h, cos_2d

def series_start(M, a, N=8, branch=-1, guess=None):
    """Returns ((H,X1,X2,b,c,u,be1,be2,B1,B2,B12) as S objects, residual norm, raw vector)."""
    K = N+1
    X10, X20, b0, c0 = bc_values(M, a)
    sin_d, cos_d, sin_h, cos_h, cos_2d = trig(K)
    one_m_cos = 1 - cos_d; sin_h2 = sin_h*sin_h
    pref = 1/(8*pi*a*(1-a))
    def unpack(v):
        v = v[:len(v)//2] + 1j*v[len(v)//2:]; i = 0
        def take(n, lead):
            nonlocal i
            out = np.concatenate([lead, v[i:i+n]]); i += n; return out
        H  = S(take(N,[0]),K); X1 = S(take(N,[X10]),K); X2 = S(take(N,[X20]),K)
        b  = S(take(N,[b0]),K); c  = S(take(N,[c0]),K); u  = S(take(N,[0]),K)
        be1= S(take(N,[0]),K); be2= S(take(N,[0]),K)
        B1 = S(take(N+1,[]),K); B2 = S(take(N+1,[]),K); B12= S(take(N+1,[]),K)
        return H,X1,X2,b,c,u,be1,be2,B1,B2,B12
    def resid(v):
        H,X1,X2,b,c,u,be1,be2,B1,B2,B12 = unpack(v)
        E73 = H.Dx() + (M/2)*(b*B2 + c*B1 + 2*u*B12)
        E74 = X1.Dx() + M*(b*B12 + u*B1)
        E75 = X2.Dx() + M*(c*B12 + u*B2)
        E76 = sin_d*c.Dx() + 2*M*be2*u*cos_h + (1-a)*c*one_m_cos
        E77 = sin_d*b.Dx() + 2*M*be1*u*cos_h + a*b*one_m_cos
        E78 = sin_h*u.Dx() + (M/2)*(b*be2 + c*be1) - 0.5*u*cos_h
        E79 = pref*sin_h - cos_h*H + M*(be1*X2 + be2*X1) - 2*M*sin_h*u*B12
        E80 = pref*cos_h*sin_h + sin_h2*H + M*cos_h*(be1*X2 + be2*X1) - M*cos_h*sin_h*(b*B2 + c*B1)
        E81 = (-M)*cos_h*sin_h*(c*X1 - b*X2) + M*cos_h*(be2*B1 - be1*B2) + (1-2*a)*sin_h2*B12
        E82 = (-4*a*(a-1)) - M*M*(4 - 8*be1*be2 + b*c + 3*u*u) + 4*cos_d*(a*(a-1) + M*M*(u*u+1)) + M*M*cos_2d*(b*c - u*u)
        E83 = (2*a-1)*u*sin_h2 + M*cos_h*(be1*c - b*be2)
        r = np.concatenate([E73.c[:N],E74.c[:N],E75.c[:N],E76.c[:K],E77.c[:K],E78.c[:K],E79.c[:K],E80.c[:K],E81.c[:K],E82.c[:K],E83.c[:K]])
        return np.concatenate([r.real, r.imag])
    if guess is None:
        P = (a*(a-1) + M*M*(1 + b0*c0))/(4*M*M)
        be1_1 = branch*np.sqrt(P*b0/c0 + 0j); be2_1 = P/be1_1; u1 = M*c0*be1_1
        H1 = 2*pref/1 * 0.5 + M*(be1_1*X20 + be2_1*X10)          # 1/(16 pi a(1-a)) = pref/2
        H1 = pref/2 + M*(be1_1*X20 + be2_1*X10)
        A = np.array([[c0, b0],[be2_1, -be1_1]]); B10, B20 = np.linalg.solve(A, np.array([2*H1/M, (c0*X10 - b0*X20)/2]))
        v0 = np.zeros(8*N + 3*(N+1), dtype=complex)
        v0[0]=H1; v0[5*N]=u1; v0[6*N]=be1_1; v0[7*N]=be2_1; v0[8*N]=B10; v0[8*N+N+1]=B20
        guess = np.concatenate([v0.real, v0.imag])
    sol = least_squares(resid, guess, method='lm', xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=4000)
    return unpack(sol.x), np.linalg.norm(sol.fun), sol.x

DIAG = {'disc_neg':0, 'root_jump':0}
def algebraic(x, M, a, H, X1, X2, b, c, u, be1_prev, branch=-1):
    sh, ch, th = np.sin(x/2), np.cos(x/2), np.tan(x/2)
    D = -(2*a-1)*u*ch/(M*th)
    cx, c2x = np.cos(x), np.cos(2*x)
    P = (4*a*(a-1) + M*M*(4 + b*c + 3*u*u) + 4*cx*(a*(a-1) + M*M*(u*u+1)) - M*M*c2x*(b*c - u*u))/(8*M*M)
    d2 = D*D + 4*c*P*b
    if (d2.real if np.iscomplexobj(d2) else d2) < 0: DIAG['disc_neg'] += 1
    disc = np.sqrt(d2 + 0j)
    # deterministic branch: near x=pi, D->0 and the physical root is branch*sqrt(P b/c) = (D + branch*disc)/(2c)
    be1 = (D + branch*disc)/(2*c)
    other = (D - branch*disc)/(2*c)
    if abs(other - be1_prev) < abs(be1 - be1_prev): DIAG['root_jump'] += 1
    be2 = (be1*c - D)/b
    B12 = (ch/(8*pi*a*(1-a)) - sh*H + M*(be1*X2 + be2*X1))/(2*M*ch*u)
    R80 = 1/(8*pi*a*(1-a)*M) + ch*H/(M*sh) + (be1*X2 + be2*X1)/ch
    R81 = ch*(c*X1 - b*X2) - (1-2*a)*ch*ch*B12/(M*sh)
    B1, B2 = np.linalg.solve(np.array([[c, b],[be2, -be1]]), np.array([R80, R81]))
    return B1, B2, B12, be1, be2

def integrate(M, a, x_min, N=12, delta0=None, rtol=1e-12, atol=1e-16, guess=None, branch=-1):
    """Solve from x = pi - delta0 down to x_min. Returns (sol, series residual, raw series vector).
    State vector: [H, X1, X2, b, c, u, F] with F(x) = Int_x^pi H."""
    if delta0 is None: delta0 = min(0.1, 0.2/abs(M))
    (H,X1,X2,b,c,u,be1,be2,B1,B2,B12), rn, vec = series_start(M, a, N, branch, guess)
    ev = lambda s: np.polyval(s.c[::-1], delta0)
    y0 = np.array([ev(H), ev(X1), ev(X2), ev(b), ev(c), ev(u), sum(H.c[k]*delta0**(k+1)/(k+1) for k in range(1, N+1))], dtype=complex)
    state = {'be1': ev(be1)}
    def rhs(x, y):
        H_,X1_,X2_,b_,c_,u_,F_ = y
        B1_,B2_,B12_,be1_,be2_ = algebraic(x, M, a, H_, X1_, X2_, b_, c_, u_, state['be1'], branch); state['be1'] = be1_
        sx, sh, ch, th, cx = np.sin(x), np.sin(x/2), np.cos(x/2), np.tan(x/2), np.cos(x)
        return [-(M/2)*(b_*B2_ + c_*B1_ + 2*u_*B12_), -M*(b_*B12_ + u_*B1_), -M*(c_*B12_ + u_*B2_),
                -2*M*be1_*u_*sh/sx - b_*a*(1+cx)/sx, -2*M*be2_*u_*sh/sx - c_*(1-a)*(1+cx)/sx,
                -(M/2)*(b_*be2_ + c_*be1_)/ch + 0.5*u_*th, -H_]
    sol = solve_ivp(rhs, [pi-delta0, x_min], y0, method='DOP853', rtol=rtol, atol=atol, dense_output=True)
    dchk = 2*delta0
    F_series = sum(H.c[k]*dchk**(k+1)/(k+1) for k in range(1, N+1))
    F_ode = sol.sol(pi-dchk)[6]
    sol.consistency = abs(F_ode - F_series)/max(abs(F_series), 1e-300)
    return sol, rn, vec, H
