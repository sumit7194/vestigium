import numpy as np
from math import factorial
from scipy.special import gammaincc, gamma
PI = np.pi

# 1. derivative check on an interior range (my earlier grid straddled the eps->pi pole)
e = np.linspace(0.2, 2.8, 200001)
num = np.gradient(e**2/(PI**2-e**2), e)
ana = 2*PI**2*e/(PI**2-e**2)**2
print(f"a_L' analytic vs numeric on [0.2,2.8]: max rel dev {np.max(np.abs(num-ana)/ana):.2e}")
num2 = np.gradient(ana, e); ana2 = 2*PI**2*(PI**2+3*e**2)/(PI**2-e**2)**3
print(f"a_L'' analytic vs numeric            : max rel dev {np.max(np.abs(num2-ana2)/ana2):.2e}")

# 2. C4 for the TRUNCATED family, closed form via upper incomplete gamma
def moments_trunc(eps, n, u):
    out = []
    for k in range(n):
        a, b = PI-eps, PI+eps
        g = lambda A, x: gammaincc(A, x)*gamma(A)
        out.append(0.5*(g(k+3, a*u)/a**(k+3) + (-1)**k * g(k+3, b*u)/b**(k+3)))
    return out
def hankels(m, Ms=(1,2,3,4)):
    return [np.linalg.det(np.array([[m[j+k] for k in range(M)] for j in range(M)])) for M in Ms]
print("\nC4 Hankel determinants for TRUNCATED members (rho_u >= 0 => must be >= 0):")
for u in (0.0, 2.0, 5.0):
    for eps in (0.8, 1.5, 2.5):
        d = hankels(moments_trunc(eps, 8, u))
        ok = "OK" if min(d) >= 0 else "FAIL"
        print(f"  u={u:4.1f} eps={eps:4.1f}  " +
              "  ".join(f"{v:+.2e}" for v in d) + f"   {ok}")
# known-fail control on the same machinery
m = moments_trunc(1.5, 8, 2.0); m[3] *= -4.0
print(f"  corrupted control: min det = {min(hankels(m)):+.2e}  "
      f"{'test NOT vacuous' if min(hankels(m))<0 else '*** vacuous ***'}")
