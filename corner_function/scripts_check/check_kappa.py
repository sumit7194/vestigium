import numpy as np
from scipy.integrate import quad
from math import factorial
PI = np.pi

print("="*70); print("CHECK 3 - C3 for a_L reduces to (4.1), and (4.1) holds on [0,pi]")
print("="*70)
e = np.linspace(1e-9, PI-1e-9, 400001)
up  = 2*PI**2*e/(PI**2-e**2)**2                      # d a_L/d eps
upp = 2*PI**2*(PI**2+3*e**2)/(PI**2-e**2)**3         # d2 a_L/d eps2
chl = upp - up/np.sin(e)                             # a''(th) + a'(th)/sin th
f   = (PI**2+3*e**2)*np.sin(e) - e*(PI**2-e**2)
print(f"  my independent derivative check: a_L'  matches  {np.allclose(up, np.gradient(e**2/(PI**2-e**2), e), rtol=1e-4)}")
print(f"  CHL[a_L] min on (0,pi)   : {chl.min():.6e}   (>=0 required)  {'OK' if chl.min()>=0 else 'FAIL'}")
print(f"  f(eps)   min on (0,pi)   : {f.min():.6e}")
print(f"  sign(CHL)==sign(f) all   : {np.all(np.sign(chl)==np.sign(f))}  -> reduction CONFIRMED")
print(f"  f/eps^3 as eps->0        : {f[5]/e[5]**3:.6f}  vs 4-pi^2/6 = {4-PI**2/6:.6f}")
print(f"  cubic bound alone valid to eps <= sqrt(2(4-pi^2/6)) = {np.sqrt(2*(4-PI**2/6)):.4f} (they say 2.170)")

print("\n"+"="*70); print("CHECK 1 - C1-C6 for the endpoints")
print("="*70)
aL = lambda eps: (PI**2/24)*PI**2*eps**2/(PI**2-eps**2)     # C_T = 1
print(f"  C5  sigma  = {aL(1e-6)/1e-12:.8f}   vs pi^2/24 = {PI**2/24:.8f}")
print(f"  C6  kappa  = {aL(PI-1e-7)*1e-7:.6f}   vs pi^5/48 = {PI**5/48:.6f}")
print(f"  C2  a>=0 {bool(np.all(aL(e)>=0))}, a'(th)<=0 {bool(np.all(-up<=0))}, a''>=0 {bool(np.all(upp>=0))}")
# C4: moments of the symmetrised positive measure, closed form
def moments(eps, n, lo=0.0):
    """m_k = int_lo^inf s^(k+2) e^{-pi s} [cosh|sinh](s eps) ds, exact for lo=0."""
    out = []
    for k in range(n):
        if lo == 0.0:
            v = 0.5*factorial(k+2)*(1/(PI-eps)**(k+3) + (-1)**k/(PI+eps)**(k+3))
        else:
            fn = np.cosh if k % 2 == 0 else np.sinh
            v = quad(lambda s: s**(k+2)*np.exp(-PI*s)*fn(s*eps), lo, np.inf, limit=400)[0]
        out.append(v)
    return out
def hankels(m, Ms=(1,2,3,4)):
    return [np.linalg.det(np.array([[m[j+k] for k in range(M)] for j in range(M)])) for M in Ms]
print("\n  C4 Hankel determinants for a_L (all must be >= 0):")
for eps in (0.5, 1.5, 2.5, 3.0):
    d = hankels(moments(eps, 8))
    print(f"    eps={eps:4.1f}  " + "  ".join(f"M={M}:{v:+.3e}" for M, v in zip((1,2,3,4), d))
          + ("   OK" if min(d) >= 0 else "   FAIL"))
print("\n  C4 known-fail control (corrupt one moment, sign must flip):")
m = moments(1.5, 8); m[3] *= -4.0
d = hankels(m)
print(f"    " + "  ".join(f"M={M}:{v:+.3e}" for M, v in zip((1,2,3,4), d))
      + ("   test is NOT vacuous" if min(d) < 0 else "   *** test vacuous ***"))

print("\n"+"="*70); print("CHECK 2 - the truncated family: C3, and kappa/C_T -> infinity")
print("="*70)
def K(s, eps): return np.cosh(s*eps) - np.sinh(s*eps)/(s*np.sin(eps))
def CHL_u(eps, uu):
    return quad(lambda s: 2*s**2*np.exp(-PI*s)*K(s, eps), uu, np.inf, limit=400)[0]
es = np.linspace(0.05, PI-0.05, 200)
print(f"  {'u':>6}{'min_eps CHL[a_u]':>20}{'sigma_u':>13}{'kappa/C_T after C5':>21}")
for uu in (0.0, 0.5, 2.0, 5.0, 20.0, 50.0):
    v = min(CHL_u(x, uu) for x in es)
    su = np.exp(-PI*uu)*(uu**2/PI + 2*uu/PI**2 + 2/PI**3)
    print(f"  {uu:6.1f}{v:20.6e}{su:13.3e}{(PI**2/24)/su:21.4e}"
          + ("  OK" if v >= -1e-12 else "  FAIL"))
print("\n  C4 for a truncated member (u=2, rho>=0 so Hankels must stay >=0):")
d = hankels(moments(1.5, 8, lo=2.0))
print(f"    " + "  ".join(f"M={M}:{v:+.3e}" for M, v in zip((1,2,3,4), d))
      + ("   OK" if min(d) >= 0 else "   FAIL"))

print("\n"+"="*70); print("Their claim 'C1,C2,C4,C6 hold for every rho>=0'")
print("="*70)
a_cs = lambda eps: quad(lambda s: (np.cosh(s*eps)-1)/s**2, 0.1, 1.0)[0]
val = a_cs(PI-1e-9)
print(f"  rho = 1 on [0.1,1] (compact support), rho>=0:")
print(f"    a(theta->0) = {val:.6f}  FINITE, so kappa = lim theta*a = 0")
print(f"    -> C6 (kappa>0) FAILS for this rho>=0. The blanket statement is false;")
print(f"       C6 needs the tail rho ~ 2 kappa s^2 e^{{-pi s}}, which their family has.")
