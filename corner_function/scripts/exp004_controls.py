"""EXP-004 controls (Renyi-2 real scalar, a=1/2): smooth-limit coefficients from the series start alone,
and the full corner function from the ODE integration, against known values.
  Known (COMPLEX scalar, HHCWM16 Table 3, alpha=2): sigma_2 = 1/(24 pi^2), sigma_2' = (5+pi^2)/(480 pi^4), sigma_2'' = 3.11534753e-5
  Known (real scalar): s_2(pi/2) = 0.0064 [CH07 via KHSM13/BWK16]; complex-boson alpha=2 at 45/90/135 deg: 0.0453(0.0450)/0.0130/0.00273 [HHCWM16 Table 1]
  CH07 eq (40), n=2, real scalar:  s_2(x) = 2 Int_{1/2}^inf dM M sqrt(M^2-1/4) F(x,M),  F = Int_x^pi H_{1/2}.
  Near x=pi: F = H1 d^2/2 + H3 d^4/4 + H5 d^6/6 + ... (d = pi - x; H even coefficients vanish by reflection)."""
import sys, numpy as np
from math import pi
from scipy.integrate import quad
sys.path.insert(0, __file__.rsplit('/',1)[0])
import exp004_ch_solver as cs

a = 0.5
def Hcoef(M, N=8):
    (H,X1,X2,b,c,u,be1,be2,B1,B2,B12), rn, sgn = cs.series_start(M, a, N)
    return H.c.real, rn
# ---- silence the branch prints by wrapping ----
import io, contextlib
def Hboth(M, N=8):
    out = {}
    for want in (+1,-1):
        # run series_start but force the branch: temporarily monkeypatch by evaluating both and selecting
        pass
    return None

# re-implement: get both branches explicitly
def series_both(M, N=8):
    K=N+1
    res={}
    f = io.StringIO()
    with contextlib.redirect_stderr(f):
        # call internal least squares for each sign by copying the logic
        X10, X20, b0, c0 = cs.bc_values(M, a)
        P = (a*(a-1) + M*M*(1 + b0*c0))/(4*M*M)
    # simplest: call series_start twice with a patched sqrt sign is not exposed; instead read both residuals from stderr and rerun with sign fixed
    return None

# Expose both branches by re-running series_start with a temporary override of np.sqrt sign choice:
def H_branch(M, sgn, N=8):
    import exp004_ch_solver as m
    orig = m.series_start
    # monkeypatch: run the loop for a single sign by temporarily shadowing the tuple
    src_sign_iter = (sgn,)
    def patched(Mx, ax, Nx):
        # copy of series_start body with only one branch
        K = Nx+1
        X10, X20, b0, c0 = m.bc_values(Mx, ax)
        sin_d, cos_d, sin_h, cos_h, cos_2d = m.trig(K)
        one_m_cos = 1 - cos_d; sin_h2 = sin_h*sin_h
        P = (ax*(ax-1) + Mx*Mx*(1 + b0*c0))/(4*Mx*Mx)
        S = m.S
        def unpack(v):
            v = v[:len(v)//2] + 1j*v[len(v)//2:]; i = 0
            def take(n, lead):
                nonlocal i
                out = np.concatenate([lead, v[i:i+n]]); i += n; return out
            H  = S(take(Nx,[0]),K); X1 = S(take(Nx,[X10]),K); X2 = S(take(Nx,[X20]),K)
            b  = S(take(Nx,[b0]),K); c  = S(take(Nx,[c0]),K); u  = S(take(Nx,[0]),K)
            be1= S(take(Nx,[0]),K); be2= S(take(Nx,[0]),K)
            B1 = S(take(Nx+1,[]),K); B2 = S(take(Nx+1,[]),K); B12= S(take(Nx+1,[]),K)
            return H,X1,X2,b,c,u,be1,be2,B1,B2,B12
        def resid(v):
            H,X1,X2,b,c,u,be1,be2,B1,B2,B12 = unpack(v)
            E73 = H.Dx() + (Mx/2)*(b*B2 + c*B1 + 2*u*B12); E74 = X1.Dx() + Mx*(b*B12 + u*B1); E75 = X2.Dx() + Mx*(c*B12 + u*B2)
            E76 = sin_d*c.Dx() + 2*Mx*be2*u*cos_h + (1-ax)*c*one_m_cos; E77 = sin_d*b.Dx() + 2*Mx*be1*u*cos_h + ax*b*one_m_cos
            E78 = sin_h*u.Dx() + (Mx/2)*(b*be2 + c*be1) - 0.5*u*cos_h
            E79 = (1/(8*pi*ax*(1-ax)))*sin_h - cos_h*H + Mx*(be1*X2 + be2*X1) - 2*Mx*sin_h*u*B12
            E80 = (1/(8*pi*ax*(1-ax)))*cos_h*sin_h + sin_h2*H + Mx*cos_h*(be1*X2 + be2*X1) - Mx*cos_h*sin_h*(b*B2 + c*B1)
            E81 = (-Mx)*cos_h*sin_h*(c*X1 - b*X2) + Mx*cos_h*(be2*B1 - be1*B2) + (1-2*ax)*sin_h2*B12
            E82 = (-4*ax*(ax-1)) - Mx*Mx*(4 - 8*be1*be2 + b*c + 3*u*u) + 4*cos_d*(ax*(ax-1) + Mx*Mx*(u*u+1)) + Mx*Mx*cos_2d*(b*c - u*u)
            E83 = (2*ax-1)*u*sin_h2 + Mx*cos_h*(be1*c - b*be2)
            r = np.concatenate([E73.c[:Nx],E74.c[:Nx],E75.c[:Nx],E76.c[:K],E77.c[:K],E78.c[:K],E79.c[:K],E80.c[:K],E81.c[:K],E82.c[:K],E83.c[:K]])
            return np.concatenate([r.real, r.imag])
        be1_1 = sgn*np.sqrt(P*b0/c0 + 0j); be2_1 = P/be1_1; u1 = Mx*c0*be1_1
        H1 = 1/(16*pi*ax*(1-ax)) + Mx*(be1_1*X20 + be2_1*X10)
        A = np.array([[c0, b0],[be2_1, -be1_1]]); B10, B20 = np.linalg.solve(A, np.array([2*H1/Mx, (c0*X10 - b0*X20)/2]))
        nun = 8*Nx + 3*(Nx+1); v0 = np.zeros(nun, dtype=complex)
        v0[0]=H1; v0[5*Nx]=u1; v0[6*Nx]=be1_1; v0[7*Nx]=be2_1; v0[8*Nx]=B10; v0[8*Nx+Nx+1]=B20
        sol = m.least_squares(resid, np.concatenate([v0.real, v0.imag]), xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=20000)
        return unpack(sol.x), np.linalg.norm(sol.fun), sgn
    return patched(M, a, N)

print("M       | branch +1: H1, H2, H3, resid          | branch -1: H1, H2, H3, resid")
for M in [0.501, 0.55, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0, 12.0]:
    row=f"{M:7.3f} |"
    for sgn in (+1,-1):
        (H,*_), rn, _ = H_branch(M, sgn)
        row += f" {H.c[1].real:+.4e} {H.c[2].real:+.1e} {H.c[3].real:+.4e} ({rn:.0e}) |"
    print(row)

print("\n---- sigma_2, sigma_2', sigma_2'' (REAL scalar) from the series coefficients, both branches ----")
# s_2 = 2 Int dM M sqrt(M^2-1/4) F ;  F = H1 d^2/2 + H3 d^4/4 + H5 d^6/6  =>  sigma_2 = Int w H1, sigma_2' = Int w H3/2, sigma_2'' = Int w H5/3, with w = M sqrt(M^2-1/4) dM = p^2 dp
for sgn in (+1,-1):
    def integrand(p, k):
        M = np.sqrt(0.25 + p*p); (H,*_), rn, _ = H_branch(M, sgn); return p*p*H.c[k].real
    vals=[]
    for k,fac in [(1,1.0),(3,0.5),(5,1/3)]:
        v,e = quad(lambda p: integrand(p,k), 0, 30, limit=200, epsabs=1e-12, epsrel=1e-9)
        vals.append(fac*v)
    print(f"branch {sgn:+d}: sigma_2={vals[0]:+.8e} (exact 1/(48pi^2)={1/(48*pi**2):.8e}, ratio {vals[0]/(1/(48*pi**2)):.6f}) ; sigma_2'={vals[1]:+.6e} (exact {(5+pi**2)/(960*pi**4):.6e}, ratio {vals[1]/((5+pi**2)/(960*pi**4)):.5f}) ; sigma_2''={vals[2]:+.6e} (Helmes/2 = {3.11534753e-5/2:.6e}, ratio {vals[2]/(3.11534753e-5/2):.5f})")
