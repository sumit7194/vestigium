"""
Boundary conditions for the CH07 cut-sphere system, VALIDATED FROM THE DERIVATION.

Part of the CHL sub-45 check (PREREG_cuspis_sub45_check.md). Sources: CH07 =
Casini & Huerta, hep-th/0606256, eqs (34)-(39) and Appendix A; restated as
CHL09 = arXiv:0811.1968, Appendix B eqs (84)-(89). No cuspis code consulted,
none in history read (no git archaeology).

WHY THIS FILE EXISTS. Text extraction of eqs (35) and (38) is ambiguous: it
does not settle whether Gamma(1/2 -+ a + i mu/2) enters squared or as a modulus
squared, nor on which side of the fraction. Choosing among parse variants by
whichever reproduces the published s(pi/2) would be TUNING TO THE CONTROLS --
the exact hunt the pre-registration names. So the boundary values are instead
computed DIRECTLY from Appendix A's definitions, which never mention s:

  at x = pi the cut is a half great circle; rotate its endpoints to the poles.
  S1 = F(theta) e^{i a phi}, F solving (-Lap + m^2) f = 0, regular at the far
  pole (F ~ s^a), with singular coefficient 1/(4 pi a) at the near one (65).
    X1(pi) = int dOmega |S1|^2                                   (95)
    b(pi)  from the s^a coefficient of S1(Rz) = (M/2) b/(4 pi a(1-a))   (66)

RESULT (run 2026-09-22, six (a, M) pairs incl. a = 0.7 > 1/2):
  (35) with |Gamma(1/2 - a + i mu/2)|^2 in the DENOMINATOR: ratio 1 to 1e-8..1e-10.
       Numerator placement: off by 1e-8 .. 2.4.  Plain square: same modulus but
       COMPLEX, excluded because X1 = int |S1|^2 is real.
  (38) with |Gamma(1/2 + a + i mu/2)|^2: ratio 1.0000000000 at all six.
  Direct route stable to 4e-10 under its own endpoint parameters.

THE FINDING THIS SURFACED. At x = pi, (82) forces beta1 beta2 = 3/8 and (83)
forces beta1 c = b beta2; then (79) with H(pi) = 0 would require
X1 c + b X2 = 0. All four quantities are now verified and POSITIVE, so that
cannot hold -- the premise (finite beta and B12 at x = pi) is false. Some
auxiliary variable is SINGULAR at the point where the boundary data live. An
integrator started at pi - delta with finite beta would return garbage, and
possibly plausible garbage. Resolving the local structure is the next step.

Two earlier attempts at a consistency test here were WRONG and are recorded:
  - |A+B|/(|A|+|B|) returned "exactly 1.000" for two variants. That metric is 1
    for ANY same-signed pair; it measured sign, not agreement.
  - The condition itself assumed regularity it never checked.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import gamma, psi
PI = np.pi

def frob_c(a, M):
    """Second Frobenius coefficient: F = s^a (1 + c s^2 + ...) near a pole.
    Derived here from F'' + cot F' - (a^2/sin^2 + M^2) F = 0 at order s^a:
    c (4a + 4) = M^2 + a(a+1)/3."""
    return (M*M + a*(a+1)/3.0) / (4.0*(a+1))

def X1_direct(a, M, s0=1e-3, th0=1e-3):
    def rhs(th, y):
        F, dF, I = y
        d2F = -np.cos(th)/np.sin(th)*dF + (a*a/np.sin(th)**2 + M*M)*F
        return [dF, d2F, -F*F*np.sin(th)]
    c = frob_c(a, M)
    # start at theta = pi - s0 on the regular solution s^a (1 + c s^2); d/dth = -d/ds
    F0 = s0**a*(1 + c*s0**2)
    dF0 = -(a*s0**(a-1) + c*(a+2)*s0**(a+1))
    sol = solve_ivp(rhs, [PI - s0, th0], [F0, dF0, 0.0], method="DOP853",
                    rtol=1e-12, atol=1e-14)
    if not sol.success:
        raise RuntimeError(sol.message)
    F, dF, I = sol.y[:, -1]
    t = th0
    # local basis at theta -> 0:  u1 = t^-a (1 + d t^2),  u2 = t^a (1 + c t^2)
    d = frob_c(-a, M)
    u1, du1 = t**-a*(1 + d*t*t), -a*t**(-a-1) + d*(2-a)*t**(1-a)
    u2, du2 = t**a*(1 + c*t*t),  a*t**(a-1) + c*(a+2)*t**(a+1)
    A, B = np.linalg.solve([[u1, u2], [du1, du2]], [F, dF])
    # tails, F^2 sin ~ integrated with the leading local forms
    I += A*A*t**(2-2*a)/(2-2*a) + 2*A*B*t*t/2 + B*B*t**(2+2*a)/(2+2*a)
    I += s0**(2*a+2)/(2*a+2)
    return 2*PI*I/(4*PI*a*A)**2

def X1_typeset(a, M, variant):
    m = np.sqrt(4*M*M - 1)
    num = gamma(-a)*(np.cosh(PI*m/2)*np.imag(psi(0.5+a+1j*m/2)) - PI/2*np.sinh(PI*m/2))
    g = gamma(0.5 - a + 1j*m/2)
    G2 = {"mod": abs(g)**2, "sq": g**2}[variant[0]]
    den = 2**(2*a)*m*(np.cos(2*a*PI)+np.cosh(PI*m))*gamma(1+a)
    return num/(den*G2) if variant[1] == "den" else num*G2/den

if __name__ == "__main__":
    # convergence of the direct route in its own numerical parameters first
    a, M = 0.3, 1.5
    print("direct route, stability in (s0, th0):")
    for s0, th0 in [(3e-3,3e-3),(1e-3,1e-3),(3e-4,3e-4)]:
        print(f"   s0={s0:.0e} th0={th0:.0e}   X1 = {X1_direct(a,M,s0,th0):.10f}")
    print()
    print(f"{'a':>5} {'M':>5} {'direct':>14}" + "".join(f" {str(v):>16}" for v in [("mod","den"),("mod","num"),("sq","den"),("sq","num")]))
    for a, M in [(0.2,1.0),(0.35,2.5),(0.1,0.7),(0.45,3.0),(0.3,1.5),(0.7,1.2)]:
        d = X1_direct(a, M)
        row = "".join(f" {abs(X1_typeset(a,M,v))/d:>16.10f}" for v in [("mod","den"),("mod","num"),("sq","den"),("sq","num")])
        print(f"{a:>5} {M:>5} {d:>14.8e}{row}    <- ratio typeset/direct")


def A_coeff(a, M, s0=1e-3, th0=1e-3):
    """Singular coefficient A of theta^{-a} for the solution with unit s^a at the far pole."""
    def rhs(th, y):
        F, dF = y
        return [dF, -np.cos(th)/np.sin(th)*dF + (a*a/np.sin(th)**2 + M*M)*F]
    c = frob_c(a, M)
    sol = solve_ivp(rhs, [PI - s0, th0],
                    [s0**a*(1 + c*s0**2), -(a*s0**(a-1) + c*(a+2)*s0**(a+1))],
                    method="DOP853", rtol=1e-12, atol=1e-14)
    if not sol.success:
        raise RuntimeError(sol.message)
    F, dF = sol.y[:, -1]; t = th0; d = frob_c(-a, M)
    u1, du1 = t**-a*(1 + d*t*t), -a*t**(-a-1) + d*(2-a)*t**(1-a)
    u2, du2 = t**a*(1 + c*t*t),  a*t**(a-1) + c*(a+2)*t**(a+1)
    return np.linalg.solve([[u1, u2], [du1, du2]], [F, dF])[0]

def b_direct(a, M):
    # S1 normalised: singular coeff 1/(4 pi a)  =>  regular coeff K = 1/(4 pi a A).
    # (66): the s^a coefficient of S1(Rz) near phi1 is (M/2) b / (4 pi a (1-a)).
    return 2*(1 - a)/(M*A_coeff(a, M))

def b_typeset(a, M):
    m = np.sqrt(4*M*M - 1)
    return 2**(1-2*a)*a*(1-a)*abs(gamma(0.5+a+1j*m/2))**2/(M*gamma(1+a)**2)

if __name__ == "__main__":
    print()
    print("b(pi): direct from Appendix A (65)+(66) vs typeset (38)/(88)")
    print(f"{'a':>5} {'M':>5} {'direct':>14} {'typeset':>14} {'ratio':>14}")
    for a, M in [(0.2,1.0),(0.35,2.5),(0.1,0.7),(0.45,3.0),(0.3,1.5),(0.7,1.2)]:
        bd, bt = b_direct(a, M), b_typeset(a, M)
        print(f"{a:>5} {M:>5} {bd:>14.8e} {bt:>14.8e} {bt/bd:>14.10f}")
