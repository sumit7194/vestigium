"""
Normal variational equations of stationary axisymmetric geodesic flows, derived
symbolically from the inverse metric -- not copied from any paper.

Part of the Morales-Ramis tool, Stage 1 (PREREG_morales_ramis_tool.md, 59c4ae3).

Setup. Coordinates (t, x, y, phi), inverse metric components as functions of
(x, y), with p_t = -E and p_phi = L conserved. H = (1/2) g^{ab} p_a p_b = -mu^2/2.
The particular solution lies in the invariant plane y = 0, p_y = 0 -- which is
invariant only if every component is EVEN in y; that is CHECKED, not assumed.

Along it, with xi1 = dy, xi2 = dp_y and x as independent variable (d/dtau = xdot d/dx):
    xi1' =  (A / xdot) xi2,        A = d^2 H / dp_y^2      at y = 0
    xi2' = -(B / xdot) xi1,        B = d^2 H / dy^2         at y = 0, p_y = 0
with xdot^2 = g^{xx} (-mu^2 - V0) from the constraint (V0 = the E, L part of 2H).
Eliminating xi1:  xi2'' - (b'/b) xi2' + a b xi2 = 0,  a = A/xdot, b = B/xdot, so
    p = -(B'/B - (xdot^2)'/(2 xdot^2)),  q = A B / xdot^2   -- both RATIONAL in x.
Reduced form y'' = r y with r = p^2/4 + p'/2 - q (changes G only by a scalar factor).
Eliminating xi2 instead gives the xi1 equation; both are returned, and they must
give the same verdict.
"""
import sympy as sp


def nve_equatorial(ginv, x, y, E, L, mu):
    """ginv: dict with keys 'tt', 'tphi', 'phiphi', 'xx', 'yy' (inverse metric, in x, y).
    Returns dict(r_xi2, r_xi1, xdot2, A, B)."""
    comps = {k: sp.sympify(v) for k, v in ginv.items()}
    for k, v in comps.items():
        odd = sp.simplify(sp.diff(v, y).subs(y, 0))
        if odd != 0:
            raise ValueError(f"g^{k} is not even in y at y=0 (d/dy = {odd}): the plane y=0 "
                             "is not invariant and this NVE does not apply")
    px = sp.Symbol("p_x")
    V = comps["tt"]*E**2 - 2*comps["tphi"]*E*L + comps["phiphi"]*L**2
    # constraint at y = 0, p_y = 0:  V0 + g^xx px^2 = -mu^2
    V0 = V.subs(y, 0)
    gxx0 = comps["xx"].subs(y, 0)
    px2 = sp.together((-mu**2 - V0)/gxx0)
    xdot2 = sp.factor(sp.together(gxx0**2*px2))
    A = sp.together(comps["yy"].subs(y, 0))
    Hfull = sp.Rational(1, 2)*(V + comps["xx"]*px**2)          # p_y = 0 part
    B = sp.diff(Hfull, y, 2).subs(y, 0).subs(px**2, px2)
    B = sp.factor(sp.together(sp.simplify(B)))
    # xi2 equation
    p2 = -(sp.diff(B, x)/B - sp.diff(xdot2, x)/(2*xdot2))
    q = A*B/xdot2
    r2 = sp.factor(sp.together(p2**2/4 + sp.diff(p2, x)/2 - q))
    # xi1 equation: xi1'' - (a'/a) xi1' + a b xi1 = 0
    p1 = -(sp.diff(A, x)/A - sp.diff(xdot2, x)/(2*xdot2))
    r1 = sp.factor(sp.together(p1**2/4 + sp.diff(p1, x)/2 - q))
    return dict(r_xi2=r2, r_xi1=r1, xdot2=xdot2, A=A, B=B)


# ---------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------
def zipoy_voorhees(delta, x, y):
    """Zipoy-Voorhees (gamma) metric, m = 1, prolate spheroidal (x, y):
       ds^2 = -f dt^2 + f^{-1}[ e^{2g}(x^2-y^2)(dx^2/(x^2-1) + dy^2/(1-y^2))
                                 + (x^2-1)(1-y^2) dphi^2 ],
       f = ((x-1)/(x+1))^delta,  e^{2g} = ((x^2-1)/(x^2-y^2))^{delta^2}.
    delta = 1 is Schwarzschild. Returns the inverse metric."""
    f = ((x - 1)/(x + 1))**delta
    e2g = ((x**2 - 1)/(x**2 - y**2))**(delta**2)
    g_xx = e2g*(x**2 - y**2)/(x**2 - 1)/f
    g_yy = e2g*(x**2 - y**2)/(1 - y**2)/f
    g_pp = (x**2 - 1)*(1 - y**2)/f
    return dict(tt=-1/f, tphi=0, phiphi=1/g_pp, xx=1/g_xx, yy=1/g_yy)


def kerr(M, a, r, u):
    """Kerr in Boyer-Lindquist (t, r, u = cos theta, phi). Inverse metric; note
    g^{uu} = g^{theta theta} sin^2 theta = (1-u^2)/rho^2."""
    rho2 = r**2 + a**2*u**2
    Delta = r**2 - 2*M*r + a**2
    s2 = 1 - u**2
    return dict(tt=-((r**2 + a**2)**2 - a**2*Delta*s2)/(rho2*Delta),
                tphi=-2*M*a*r/(rho2*Delta),
                phiphi=(Delta - a**2*s2)/(rho2*Delta*s2),
                xx=Delta/rho2,
                yy=s2/rho2)
