"""
Kovacic's algorithm, and the Morales-Ramis verdict built on it.

Pre-registered in PREREG_morales_ramis_tool.md (59c4ae3) before this file existed.
Implemented from the published algorithm (Kovacic, J. Symbolic Comput. 2 (1986)
3-43, and its standard restatements), not from any fleet or third-party code.
Runs under the repo's sims/.venv (sympy 1.14).

Input: y'' = r(z) y, r rational in z with exactly computable poles, no free
parameters. Output of `morales_ramis_verdict`: one of

  OBSTRUCTION     G0 of the differential Galois group proven NON-abelian
  NO_OBSTRUCTION  G0 proven abelian (proves nothing about integrability)
  INCONCLUSIVE    undetermined; never mapped to either verdict

From Kovacic's case to G0:
  case 4 (no Liouvillian solution): G = SL(2)            -> OBSTRUCTION
  case 3 (finite primitive):         G0 = {1}             -> NO_OBSTRUCTION
  case 2 (imprimitive):              G0 in diagonal torus -> NO_OBSTRUCTION
  case 1 (reducible, y1 = exp(int w)): G in the Borel group. G0 is the FULL
         Borel group (non-abelian) iff y1 is transcendental AND no rational R
         solves R' - 2wR = 1 (the additive part is non-trivial). Both are
         checked explicitly. Weber y'' = (z^2+1) y is the calibration case.
"""
import itertools
import sympy as sp

OBSTRUCTION, NO_OBSTRUCTION, INCONCLUSIVE = "OBSTRUCTION", "NO_OBSTRUCTION", "INCONCLUSIVE"
MAX_DEGREE = 60          # polynomial searches above this degree -> INCONCLUSIVE


class Inconclusive(Exception):
    """The input is outside what the exact algorithm can decide."""


# ----------------------------------------------------------------------------
# exact series helpers
# ----------------------------------------------------------------------------
def _simp(x):
    return sp.nsimplify(sp.simplify(x)) if x.is_number else sp.simplify(x)


def _series_div(num, den, n):
    """First n coefficients of num(e)/den(e), num and den as coefficient lists
    in ascending powers, den[0] != 0."""
    num = list(num) + [0]*n
    den = list(den) + [0]*n
    out = []
    for k in range(n):
        v = num[k] - sum(out[j]*den[k - j] for j in range(k))
        out.append(sp.simplify(v/den[0]))
    return out


def _series_sqrt(f, n):
    """First n coefficients of sqrt(sum f_k e^k), f_0 != 0 (principal branch)."""
    g = [sp.sqrt(f[0])]
    for k in range(1, n):
        s = sum(g[j]*g[k - j] for j in range(1, k))
        g.append(sp.simplify((f[k] - s)/(2*g[0])))
    return g


def _ascending(poly_expr, var):
    p = sp.Poly(sp.expand(poly_expr), var)
    cs = p.all_coeffs()[::-1]
    return [sp.simplify(c) for c in cs]


class RationalR:
    """r = s/t with its poles, orders and exact Laurent data."""

    def __init__(self, r, z):
        self.z = z
        r = sp.cancel(sp.together(sp.sympify(r)))
        if r.free_symbols - {z}:
            raise Inconclusive(f"free parameters {r.free_symbols - {z}}: specialise them first")
        if not r.is_rational_function(z):
            raise Inconclusive("r is not a rational function of z")
        self.r = r
        s, t = sp.fraction(r)
        self.s, self.t = sp.Poly(s, z), sp.Poly(t, z)
        lc = self.t.LC()
        self.s, self.t = sp.Poly(self.s.as_expr()/lc, z), sp.Poly(self.t.as_expr()/lc, z)
        if self.s.is_zero:
            self.zero = True
            self.poles = {}
            self.ord_inf = sp.oo
            return
        self.zero = False
        rts = sp.roots(self.t, z)
        if sum(rts.values()) != self.t.degree():
            raise Inconclusive("the poles of r are not all explicitly computable")
        self.poles = {sp.simplify(c): m for c, m in rts.items()}
        self.ord_inf = self.t.degree() - self.s.degree()

    def laurent_at(self, c, n):
        """Coefficients f_0..f_{n-1} with r = (z-c)^{-m} sum f_k (z-c)^k, m = order."""
        e = sp.Symbol("e_")
        m = self.poles[c]
        s_sh = _ascending(self.s.as_expr().subs(self.z, c + e), e)
        t_sh = _ascending(self.t.as_expr().subs(self.z, c + e), e)
        t_sh = [sp.simplify(x) for x in t_sh]
        if any(sp.simplify(x) != 0 for x in t_sh[:m]):
            raise Inconclusive("pole multiplicity bookkeeping failed")
        return _series_div(s_sh, t_sh[m:], n)

    def laurent_at_inf(self, n):
        """Coefficients f_0.. with r = z^{-o} sum f_k z^{-k}, o = ord_inf."""
        w = sp.Symbol("w_")
        ds, dt = self.s.degree(), self.t.degree()
        s_rev = _ascending(sp.expand(w**ds*self.s.as_expr().subs(self.z, 1/w)), w)
        t_rev = _ascending(sp.expand(w**dt*self.t.as_expr().subs(self.z, 1/w)), w)
        return _series_div(s_rev, t_rev, n)


def _is_nonneg_int(x):
    x = sp.simplify(x)
    try:
        xv = complex(sp.N(x, 30))
    except TypeError:
        raise Inconclusive(f"cannot evaluate {x}")
    if abs(xv.imag) > 1e-20:
        return False, None
    k = round(xv.real)
    if abs(xv.real - k) > 1e-20 or k < 0:
        return False, None
    if sp.simplify(x - k) != 0:
        return False, None
    return True, int(k)


def _monic_poly_solution(expr_of_P, d, z):
    """Search a monic polynomial P of degree d with expr_of_P(P) == 0 identically.

    expr_of_P is LINEAR in P, so it is applied to the concrete monomials
    z^0 .. z^d (no symbolic unknowns pass through it) and one exact linear system
    sum_{j<d} c_j N_j = -N_d is solved, N_j the numerators over a common
    denominator. Returns P or None."""
    if d > MAX_DEGREE:
        raise Inconclusive(f"polynomial search of degree {d} exceeds {MAX_DEGREE}")
    outs = [sp.together(sp.expand(expr_of_P(z**j))) for j in range(d + 1)]
    fr = [sp.fraction(o) for o in outs]
    D = sp.Integer(1)
    for _, den in fr:
        D = sp.lcm(D, den)
    nums = [sp.Poly(sp.cancel(num*D/den), z) for num, den in fr]
    deg = max(n.degree() for n in nums)
    if all(n.is_zero for n in nums[:d]) and nums[d].is_zero:
        return z**d
    rows = deg + 1
    A = sp.zeros(rows, d)
    b = sp.zeros(rows, 1)
    for j in range(d + 1):
        cs = nums[j].all_coeffs()[::-1] if not nums[j].is_zero else []
        for i, cval in enumerate(cs):
            if j < d:
                A[i, j] = cval
            else:
                b[i, 0] = -cval
    if d == 0:
        return z**0 if all(sp.simplify(v) == 0 for v in b) else None
    try:
        sol, params = A.gauss_jordan_solve(b)
    except ValueError:
        return None                         # inconsistent: no such P
    sol = sol.subs({t: 0 for t in params})   # any member of the solution family will do
    return sp.expand(z**d + sum(sp.simplify(sol[j])*z**j for j in range(d)))


# ----------------------------------------------------------------------------
# Kovacic case 1
# ----------------------------------------------------------------------------
def _case1_data(R):
    z = R.z
    items = []                      # per point: list of (sqrt_part_expr, alpha_expr) for signs +,-
    for c, m in R.poles.items():
        if m == 1:
            items.append(("pole", c, [(sp.Integer(0), sp.Integer(1))]))
        elif m == 2:
            b = R.laurent_at(c, 1)[0]
            rt = sp.sqrt(1 + 4*b)
            items.append(("pole", c, [(sp.Integer(0), sp.Rational(1, 2) + rt/2),
                                      (sp.Integer(0), sp.Rational(1, 2) - rt/2)]))
        elif m % 2 == 0:
            nu = m//2
            f = R.laurent_at(c, nu + 1)
            g = _series_sqrt(f, nu)          # g_0..g_{nu-1}
            part = sum(g[k]*(z - c)**(k - nu) for k in range(nu - 1))   # powers -nu..-2
            a = g[0]
            # b = [coeff of (z-c)^(-nu-1) in r] - [same in ([sqrt r]_c)^2]. Since
            # (sqrt r)^2 = r exactly, the difference is the two cross terms 2 g0 g_{nu-1}.
            b = sp.simplify(2*g[0]*g[nu - 1])
            items.append(("pole", c, [(part, sp.Rational(1, 2)*(b/a + nu)),
                                      (-part, sp.Rational(1, 2)*(-b/a + nu))]))
        else:
            return None                      # odd order > 1: case 1 impossible
    oi = R.ord_inf
    if oi == sp.oo or oi > 2:
        items.append(("inf", None, [(sp.Integer(0), sp.Integer(0)), (sp.Integer(0), sp.Integer(1))]))
    elif oi == 2:
        b = R.laurent_at_inf(1)[0]
        rt = sp.sqrt(1 + 4*b)
        items.append(("inf", None, [(sp.Integer(0), sp.Rational(1, 2) + rt/2),
                                    (sp.Integer(0), sp.Rational(1, 2) - rt/2)]))
    elif oi <= 0 and oi % 2 == 0:
        nu = -oi//2
        f = R.laurent_at_inf(nu + 2)
        g = _series_sqrt(f, nu + 2)          # sqrt r = z^nu sum g_k z^-k
        part = sum(g[k]*z**(nu - k) for k in range(nu + 1))
        a = g[0]
        # coefficient of z^(nu-1): r's minus ([sqrt r]_inf)^2's = the cross terms 2 g0 g_{nu+1}
        b = sp.simplify(2*g[0]*g[nu + 1])
        items.append(("inf", None, [(part, sp.Rational(1, 2)*(b/a - nu)),
                                    (-part, sp.Rational(1, 2)*(-b/a - nu))]))
    else:
        return None                          # odd order at infinity < 2: impossible
    return items


def kovacic_case1(R):
    z = R.z
    if R.zero:
        return [dict(omega=sp.Integer(0), P=sp.Integer(1))]
    items = _case1_data(R)
    if items is None:
        return []
    found = []
    choice_lists = [list(range(len(it[2]))) for it in items]
    for choice in itertools.product(*choice_lists):
        alpha_inf = None; omega = 0; sum_alpha_c = 0
        for it, ch in zip(items, choice):
            part, alpha = it[2][ch]
            if it[0] == "inf":
                alpha_inf = alpha; omega += part
            else:
                c = it[1]
                sum_alpha_c += alpha
                omega += part + alpha/(z - c)
        ok, d = _is_nonneg_int(alpha_inf - sum_alpha_c)
        if not ok:
            continue
        omega = sp.together(omega)
        eq = lambda P, w=omega: sp.diff(P, z, 2) + 2*w*sp.diff(P, z) + (sp.diff(w, z) + w**2 - R.r)*P
        P = _monic_poly_solution(eq, d, z)
        if P is not None:
            found.append(dict(omega=sp.simplify(omega + sp.diff(P, z)/P), P=P, d=d))
    # deduplicate solutions
    uniq = []
    for f in found:
        if not any(sp.simplify(f["omega"] - u["omega"]) == 0 for u in uniq):
            uniq.append(f)
    return uniq


# ----------------------------------------------------------------------------
# Kovacic case 2
# ----------------------------------------------------------------------------
def kovacic_case2(R):
    z = R.z
    if R.zero:
        return None
    E = []
    has_candidate = False
    for c, m in R.poles.items():
        if m == 1:
            E.append((c, [4]))
        elif m == 2:
            b = R.laurent_at(c, 1)[0]
            rt = sp.sqrt(1 + 4*b)
            vals = [v for v in (2, 2 + 2*rt, 2 - 2*rt) if _is_int(v)]
            E.append((c, sorted(set(int(sp.simplify(v)) for v in vals))))
            has_candidate = True
        else:
            E.append((c, [m]))
            if m % 2 == 1:
                has_candidate = True
    if not has_candidate:
        return None                          # necessary condition for case 2 fails
    oi = R.ord_inf
    if oi > 2:
        Einf = [0, 2, 4]
    elif oi == 2:
        b = R.laurent_at_inf(1)[0]
        rt = sp.sqrt(1 + 4*b)
        Einf = sorted(set(int(sp.simplify(v)) for v in (2, 2 + 2*rt, 2 - 2*rt) if _is_int(v)))
    else:
        Einf = [oi]
    lists = [e for _, e in E] + [Einf]
    for combo in itertools.product(*lists):
        if all(x % 2 == 0 for x in combo):
            continue
        ec, einf = combo[:-1], combo[-1]
        dd = sp.Rational(einf - sum(ec), 2)
        if dd < 0 or dd != int(dd):
            continue
        d = int(dd)
        theta = sp.together(sum(sp.Rational(e, 2)/(z - c) for (c, _), e in zip(E, ec)))
        r = R.r
        eq = lambda P, th=theta: (sp.diff(P, z, 3) + 3*th*sp.diff(P, z, 2)
                                  + (3*th**2 + 3*sp.diff(th, z) - 4*r)*sp.diff(P, z)
                                  + (sp.diff(th, z, 2) + 3*th*sp.diff(th, z) + th**3
                                     - 4*r*th - 2*sp.diff(r, z))*P)
        P = _monic_poly_solution(eq, d, z)
        if P is not None:
            return dict(theta=theta, P=P, d=d, phi=sp.simplify(theta + sp.diff(P, z)/P))
    return None


def _is_int(v):
    v = sp.simplify(v)
    try:
        vv = complex(sp.N(v, 30))
    except TypeError:
        return False
    if abs(vv.imag) > 1e-20 or abs(vv.real - round(vv.real)) > 1e-20:
        return False
    return sp.simplify(v - round(vv.real)) == 0


# ----------------------------------------------------------------------------
# Kovacic case 3
# ----------------------------------------------------------------------------
def kovacic_case3(R):
    z = R.z
    if R.zero or any(m > 2 for m in R.poles.values()) or R.ord_inf < 2:
        return None
    r = R.r
    b_inf = R.laurent_at_inf(1)[0] if R.ord_inf == 2 else sp.Integer(0)
    for n in (4, 6, 12):
        E = []
        for c, m in R.poles.items():
            if m == 1:
                E.append((c, [12]))
            else:
                b = R.laurent_at(c, 1)[0]
                rt = sp.sqrt(1 + 4*b)
                vals = [6 + sp.Rational(12*k, n)*rt for k in range(-n//2, n//2 + 1)]
                E.append((c, sorted(set(int(sp.simplify(v)) for v in vals if _is_int(v)))))
        rt = sp.sqrt(1 + 4*b_inf)
        vals = [6 + sp.Rational(12*k, n)*rt for k in range(-n//2, n//2 + 1)]
        Einf = sorted(set(int(sp.simplify(v)) for v in vals if _is_int(v)))
        S = sp.Integer(1)
        for c in R.poles:
            S *= (z - c)
        lists = [e for _, e in E] + [Einf]
        for combo in itertools.product(*lists):
            ec, einf = combo[:-1], combo[-1]
            dd = sp.Rational(n, 12)*(einf - sum(ec))
            if dd < 0 or dd != int(dd):
                continue
            d = int(dd)
            theta = sp.together(sum(sp.Rational(n, 12)*e/(z - c) for (c, _), e in zip(E, ec)))

            Sth = sp.expand(sp.cancel(S*theta))       # polynomial: theta has simple poles at the c
            S2r = sp.expand(sp.cancel(S**2*r))         # polynomial: poles of r have order <= 2
            Sd = sp.diff(S, z)

            def last_P(P, n=n, Sth=Sth, S2r=S2r, Sd=Sd):
                Ps = {n + 1: sp.Integer(0), n: -P}
                for i in range(n, -1, -1):
                    Ps[i - 1] = sp.expand(-S*sp.diff(Ps[i], z) + ((n - i)*Sd - Sth)*Ps[i]
                                          - (n - i)*(i + 1)*S2r*Ps[i + 1])
                return Ps[-1]
            P = _monic_poly_solution(last_P, d, z)
            if P is not None:
                return dict(n=n, group={4: "tetrahedral", 6: "octahedral", 12: "icosahedral"}[n],
                            theta=theta, P=P, d=d)
    return None


# ----------------------------------------------------------------------------
# rational solution of R' - 2 w R = 1  (additive part of the case-1 group)
# ----------------------------------------------------------------------------
def rational_solution_additive(omega, z):
    """Rational R with R' - 2*omega*R = 1, or None. Poles of R can only sit at
    poles of omega (elsewhere R' would dominate): at a simple pole of omega with
    residue rho the order is at most -2*rho; at higher poles R is regular. The
    degree at infinity is bounded from the behaviour of omega there."""
    omega = sp.together(omega)
    num, den = sp.fraction(omega)
    rts = sp.roots(sp.Poly(den, z), z) if sp.Poly(den, z).degree() > 0 else {}
    if sum(rts.values()) != sp.Poly(den, z).degree():
        raise Inconclusive("poles of omega not explicit")
    D = sp.Integer(1)
    order_sum = 0
    for c, m in rts.items():
        if m == 1:
            rho = sp.simplify(sp.limit((z - c)*omega, z, c))
            ok, k = _is_nonneg_int(-2*rho)
            k = k if ok else 0
        else:
            k = 0
        D *= (z - c)**k
        order_sum += k
    # behaviour at infinity: omega ~ beta z^q
    q = sp.Poly(num, z).degree() - sp.Poly(den, z).degree()
    if q >= 0:
        top = 0                              # R must decay like z^{-q}: numerator degree <= order_sum
    else:
        beta = sp.limit(z*omega, z, sp.oo) if q == -1 else 0
        ok, k = _is_nonneg_int(2*beta) if q == -1 else (False, None)
        top = max(1, k if ok else 0)
    nd = order_sum + top + 2                 # generous
    if nd > MAX_DEGREE:
        raise Inconclusive("additive-part degree bound too large")
    cs = sp.symbols(f"a0:{nd + 1}")
    N = sum(cs[i]*z**i for i in range(nd + 1))
    Rr = N/D
    E = sp.together(sp.diff(Rr, z) - 2*omega*Rr - 1)
    eqs = sp.Poly(sp.expand(sp.fraction(E)[0]), z).coeffs()
    sol = sp.solve(eqs, cs, dict=True)
    if not sol:
        return None
    return sp.simplify(Rr.subs({c: sol[0].get(c, 0) for c in cs}))


def _is_algebraic_exp(omega, z):
    """exp(int omega) algebraic  <=>  omega = sum rho_c/(z-c) with every rho_c rational."""
    omega = sp.apart(sp.together(omega), z, full=False) if sp.together(omega).is_rational_function(z) else omega
    num, den = sp.fraction(sp.together(omega))
    if sp.Poly(num, z).degree() >= sp.Poly(den, z).degree():
        return False                         # polynomial part -> exp(polynomial) transcendental
    rts = sp.roots(sp.Poly(den, z), z)
    if sum(rts.values()) != sp.Poly(den, z).degree():
        raise Inconclusive("poles of omega not explicit")
    if any(m > 1 for m in rts.values()):
        return False
    for c in rts:
        rho = sp.simplify(sp.limit((z - c)*omega, z, c))
        if not rho.is_rational:
            return False
    return True


# ----------------------------------------------------------------------------
# the verdict
# ----------------------------------------------------------------------------
def kovacic(r, z):
    R = RationalR(r, z)
    sols = kovacic_case1(R)
    if sols:
        return dict(case=1, solutions=sols, R=R)
    c2 = kovacic_case2(R)
    if c2:
        return dict(case=2, data=c2, R=R)
    c3 = kovacic_case3(R)
    if c3:
        return dict(case=3, data=c3, R=R)
    return dict(case=4, R=R)


def morales_ramis_verdict(r, z):
    """-> (verdict, reason, kovacic_result_or_None). Exceptions -> INCONCLUSIVE."""
    try:
        k = kovacic(r, z)
        if k["case"] == 4:
            return OBSTRUCTION, "Kovacic case 4: no Liouvillian solution, G = SL(2)", k
        if k["case"] == 3:
            return NO_OBSTRUCTION, f"Kovacic case 3 ({k['data']['group']}): G finite", k
        if k["case"] == 2:
            return NO_OBSTRUCTION, "Kovacic case 2: imprimitive, G0 in a torus", k
        # case 1
        sols = k["solutions"]
        if len(sols) >= 2:
            return NO_OBSTRUCTION, "Kovacic case 1 with two exponential solutions: G diagonal", k
        w = sols[0]["omega"]
        if _is_algebraic_exp(w, z):
            return NO_OBSTRUCTION, "Kovacic case 1, y1 algebraic: G0 in the additive group", k
        Rr = rational_solution_additive(w, z)
        if Rr is not None:
            return NO_OBSTRUCTION, "Kovacic case 1, additive part trivial: G0 = C*", k
        return OBSTRUCTION, ("Kovacic case 1 but y1 transcendental and additive part "
                             "non-trivial: G0 = full Borel group, non-abelian"), k
    except Inconclusive as e:
        return INCONCLUSIVE, str(e), None
