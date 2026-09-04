"""
EXP-003: the corner function as a positive spectral integral, and what the known general
constraints can and cannot say about kappa/C_T.

Representation (derived here from the Casini-Huerta 2012 reflection-positivity inequalities,
det{d^{j+k+2} a / dtheta^{j+k+2}}_{j,k<M} >= 0 for all M and all theta, which are the local form of
positive-definiteness of a kernel in theta_i+theta_j; by Bernstein-Widder such a function is a
Laplace transform of a positive measure):

    a''(theta) = Int drho(s) cosh(s (pi-theta)),   rho >= 0  (symmetrised by a(2pi-theta)=a(theta))
    a(theta)   = Int drho(s) [cosh(s eps) - 1]/s^2,   eps = pi - theta,   using a(pi)=a'(pi)=0
    sigma^{(p-1)} = M_{2p-2}/(2p)!,   M_k = Int s^k drho(s)         (smooth-limit coefficients)
    total mass M_0 = 2 sigma = pi^2 C_T/12                          (theorem, FLP16)
    tail  rho(s) ~ 2 kappa s^2 e^{-pi s}  <=>  a ~ kappa/theta       (sharp limit)

Constraints tested numerically for every candidate:
    C1 reflection a(2pi-theta)=a(theta)      C2 a>=0, a'<=0, a''>=0 on (0,pi)  [HT07, SSA]
    C3 CHL: a'' + a'/sin(theta) >= 0        [CHL09, SSA+Lorentz]   C4 sigma = pi^2 C_T/24
    C5 Hankel/moment positivity of {sigma^{(p)}}  [CH12]            C6 a ~ kappa/theta as theta->0
"""
import numpy as np
from math import pi, gamma, log, sin, cos, sinh, cosh, factorial
from scipy.integrate import quad

CT = 1.0  # work in units of C_T; sigma = pi^2/24
SIG = pi**2/24

# ---------- known closed forms (units of C_T) ----------
def a_min(th):  return (pi**2/3)*log(1/sin(th/2))                      # BWK16, rho_min = (pi^2/3) s/sinh(pi s)
def a_lif(th):  return (th-pi)**2/(th*(2*pi-th))                        # Fradkin-Moore Lifshitz shape, rho = 2 s^2 e^{-pi s}/(1) up to norm
def a_emi(th):  return 1+(pi-th)/np.tan(th)                             # EMI shape, rho = (pi/2) s^2 / sinh^2(pi s/2)

def sigma_of(f, eps=1e-3):   return f(pi-eps)/eps**2
def kappa_of(f, th=1e-4):    return f(th)*th

def derivs(f, th, h=1e-3):
    f0,fp,fm,fpp,fmm = f(th),f(th+h),f(th-h),f(th+2*h),f(th-2*h)
    d1=(fp-fm)/(2*h); d2=(fp-2*f0+fm)/h**2
    return d1,d2

def check_all(f, name, thetas=np.linspace(0.05, pi-0.05, 40)):
    ok=True; worst=+np.inf
    for th in thetas:
        d1,d2=derivs(f,th)
        c2 = (f(th)>=-1e-12) and (d1<=1e-9) and (d2>=-1e-9)
        chl = d2 + d1/sin(th)
        worst=min(worst, chl)
        refl = abs(f(th)-f(2*pi-th))<1e-9*max(1,abs(f(th)))
        ok = ok and c2 and refl and (chl>=-1e-7)
    print(f"  {name:38s} C1 refl+C2 signs+C3 CHL: {'PASS' if ok else 'FAIL'}   min[a''+a'/sin] = {worst:+.3e}   sigma={sigma_of(f):.6f} (target {SIG:.6f})   kappa={kappa_of(f):.4f}")
    return ok

def hankel_check(sig, label):
    # sig = [sigma^{(0)}, sigma^{(1)}, ...] ; M_{2p-2} = (2p)! sigma^{(p-1)}, even moments of a symmetric measure
    M = [factorial(2*(p+1))*sig[p] for p in range(len(sig))]       # M_0, M_2, M_4, ...
    n = len(M)//2
    H0 = np.array([[M[j+k] for k in range(n)] for j in range(n)])          # moments M_{2(j+k)} -> Hankel in x = s^2
    H1 = np.array([[M[j+k+1] for k in range(n)] for j in range(n)])        # M_{2(j+k)+2}
    e0,e1 = np.linalg.eigvalsh(H0), np.linalg.eigvalsh(H1)
    print(f"  {label:38s} Hankel(M_2(j+k)) min eig/max eig = {e0.min()/e0.max():+.3e} ; Hankel(M_2(j+k)+2) = {e1.min()/e1.max():+.3e}  -> {'PASS' if e0.min()>=-1e-12*e0.max() and e1.min()>=-1e-12*e1.max() else 'FAIL'}")

print("=== Tier-1 style: does the spectral (moment) structure hold for the real theories? ===")
holo = [pi**2/24, 5/192, 37/(1536*pi**2), 195/(8192*pi**4), 3133/(131072*pi**6), 25233/(1048576*pi**8)]   # BWK16 eq V.6, units C_T
CTc = 3/(16*pi**2)
boson = [x/CTc for x in [1/128, (20+3*pi**2)/(9216*pi**2), 5.34655497e-5, 5.40160621e-6, 5.45758486e-7, 5.51156763e-8, 5.57181927e-9, 5.63580458e-10]]
fermi = [x/CTc for x in [1/128, (16+3*pi**2)/(9216*pi**2), 4.8129970e-5, 4.8552317e-6, 4.9173353e-7, 4.9777097e-8, 5.0411447e-9]]
hankel_check(holo, "Einstein (6 exact coefficients)")
hankel_check(boson, "complex scalar (8 coefficients)")
hankel_check(fermi, "Dirac fermion (7 coefficients)")
# a deliberately broken sequence (what would a wrong function score?): flip the sign of the p=3 term's excess
broken = list(holo); broken[3] = 0.5*holo[3]
hankel_check(broken, "CONTROL: Einstein with sigma''' halved")

print("\n=== closed-form shapes, normalised to the universal sigma ===")
for f,name in [(a_min,"a_min (BWK bound)"), (lambda t: SIG*pi**3/2*a_lif(t)*2/pi**3*pi**3/2 if False else (SIG/ (1/pi**2))*a_lif(t), "Lifshitz shape, sigma-normalised"), (lambda t: (SIG/(1/3))*a_emi(t), "EMI shape, sigma-normalised")]:
    check_all(f,name)
# spectral densities of the three closed forms (units C_T): rho_min = (pi^2/3) s/sinh(pi s); rho_lif = norm*2 s^2 e^{-pi s}; rho_emi = norm*(pi/2) s^2/sinh^2(pi s/2)
# unnormalised shapes: a_min has sigma=pi^2/24 already; a_lif has sigma=1/pi^2; a_emi has sigma=1/3.
# densities (unnormalised): rho_min=(pi^2/3) s/sinh(pi s) ; rho_lif=pi s^2 e^{-pi s} ; rho_emi=(pi/2) s^2/sinh^2(pi s/2)
for rho,name,scale in [(lambda s:(pi**2/3)*s/np.sinh(pi*s),"rho_min (sigma-normalised)",1.0),
                       (lambda s: pi*s*s*np.exp(-pi*s),"rho_lif (sigma-normalised)",SIG/(1/pi**2)),
                       (lambda s:(pi/2)*s*s/np.sinh(pi*s/2)**2,"rho_emi (sigma-normalised)",SIG/(1/3))]:
    m0,_=quad(rho,0,np.inf); m2,_=quad(lambda s: s*s*rho(s),0,np.inf)
    print(f"  {name}: total mass {scale*m0:.6f} (2 sigma = {2*SIG:.6f});  sigma' = M_2/24 = {scale*m2/24:.6f}")
# cross-check the moment identity against the closed forms' Taylor coefficients: a_lif sigma'/sigma = ?, a_emi: 2 zeta(4)/pi^4 / (2 zeta(2)/pi^2) = (pi^4/45)/(pi^2/3) / pi^2 = 1/15
print(f"  check: a_emi sigma'/sigma exact = 1/15 = {1/15:.6f}; a_lif sigma'/sigma exact = 1/pi^2 = {1/pi**2:.6f}; Einstein sigma'/sigma = (5/192)/(pi^2/24) = {(5/192)/(pi**2/24):.6f}; a_min sigma'/sigma = 1/24 = {1/24:.6f}")

print("\n=== explicit admissible corner functions with any kappa: a = (1-lam) a_min + tail(s1) ===")
def make(s1, kap):
    # tail measure rho_t(s) = 2 kap s^2 e^{-pi s} Theta(s-s1)  -> a_t(theta) = kap [e^{-theta s1}/theta + e^{-(2pi-theta) s1}/(2pi-theta) - 2 e^{-pi s1}/pi]
    def a_t(th): return kap*(np.exp(-th*s1)/th + np.exp(-(2*pi-th)*s1)/(2*pi-th) - 2*np.exp(-pi*s1)/pi)
    mass_t = 2*kap*quad(lambda s: s*s*np.exp(-pi*s), s1, np.inf)[0]
    lam = mass_t/(2*SIG)             # fraction of the universal mass carried by the tail
    if lam>1: return None, lam
    return (lambda th: (1-lam)*a_min(th) + a_t(th)), lam
for s1,kap in [(0.0, 3.0), (2.0, 10.0), (4.0, 100.0), (6.0, 1e4), (8.0, 1e6), (0.0, 1e-3)]:
    f,lam = make(s1,kap)
    if f is None: print(f"  s1={s1}, kappa={kap}: tail mass exceeds 2 sigma (lam={lam:.2f}) -> not admissible at this sigma"); continue
    ok = check_all(f, f"s1={s1:>3}, kappa/C_T={kap:<8g} lam={lam:.3f}")
print("\nkappa/C_T of the known theories for scale: ECG 3.672..3.747, Einstein 3.709, Dirac 3.8005, real scalar 4.179")
