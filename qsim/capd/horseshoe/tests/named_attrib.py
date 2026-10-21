"""DIAGNOSTIC ONLY: interval over-widening of the NAMED physical quantities of the MN field (mn_codegen.build's
definitions), at one point on a box of half-width h in (x, y).
For each quantity q, built from named inputs by the formula used in build():
  total  = width of q when every input is itself the naive interval  /  true linear range |grad q| 2h
  local  = width of q when every input is replaced by its TIGHT enclosure (value +- |grad| h)  /  true linear range
'local' isolates the loss of that one formula; 'total' is what the generated code inherits.
Usage: named_attrib.py x y [h] [beta] [aug1,aug2,...]
  aug: names propagated as extra STATE variables (augmented ODE), i.e. entering later formulas as tight enclosures."""
import sys, mpmath as mp, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_field_gate as Qg
mp.mp.dps = 40; mp.iv.dps = 40
x, y = sp.symbols("x y", real=True)
k, al, beta = sp.Integer(39), sp.Rational(-5, 8), sp.Rational(13394411, 1186380)
if len(sys.argv) > 4: beta = sp.Rational(sys.argv[4])
E, L = sp.Rational(19, 20), sp.Integer(267)
X0, Y0 = mp.mpf(sys.argv[1]), mp.mpf(sys.argv[2]); h = mp.mpf(sys.argv[3]) if len(sys.argv) > 3 else mp.mpf("1e-6")

# named quantities: (name, formula in earlier names) -- the same definitions as mn_codegen.build()
S = {n: sp.Symbol(n) for n in "Rr u P0 P1 P2 P3 ea eb a b A B C Qx psi E2 Gx eG V gxx gyy".split()}
P = [S["P0"], S["P1"], S["P2"], S["P3"]]; Rr, u = S["Rr"], S["u"]
Qp, r = sp.div(sp.Poly(sp.expand((Qg.x**2 - 1)*(1 - Qg.y**2)*Qg.B**2 - 4*Qg.C**2), Qg.x, Qg.y, Qg.a, Qg.b),
               sp.Poly(Qg.A, Qg.x, Qg.y, Qg.a, Qg.b))
sub = {Qg.x: x, Qg.y: y, Qg.a: S["a"], Qg.b: S["b"]}
w0 = 4*k*al/(1 - al**2); Lp = L + w0*E; rho2 = k**2*(x**2 - 1)*(1 - y**2)
defs = [
    ("Rr", sp.sqrt(x**2 + y**2 - 1)),
    ("u", x*y/Rr),
    ("P0", sp.Integer(1)), ("P1", u), ("P2", (3*u**2 - 1)/2), ("P3", (5*u**3 - 3*u)/2),
    ("ea", -1 + sum((x - y)*P[l]/Rr**(l + 1) for l in range(3))),
    ("eb", 1 + sum((-1)**(3 - l)*(x + y)*P[l]/Rr**(l + 1) for l in range(3))),
    ("a", -al*sp.exp(-2*beta*S["ea"])),
    ("b", al*sp.exp(2*beta*S["eb"])),
    ("A", Qg.A.subs(sub)), ("B", Qg.B.subs(sub)), ("C", Qg.C.subs(sub)),
    ("Qx", Qp.as_expr().subs(sub)),
    ("psi", beta*P[2]/Rr**3),
    ("E2", sp.exp(2*S["psi"])),
    ("Gx", 3*beta**2*(P[3]**2 - P[2]**2)/Rr**6 + 2*beta*sum(((x - y) + (-1)**l*(x + y))*P[l]/Rr**(l + 1) - 2 for l in range(3)) + 8*beta),
    ("eG", sp.exp(S["Gx"])),
    ("V", (S["E2"]*S["A"]*Lp**2 - 4*k*S["C"]*E*Lp - k**2*E**2*S["Qx"]/S["E2"])/(2*rho2*S["B"])),
    ("gxx", S["E2"]*(x**2 - 1)*(1 - al**2)**2/(k**2*S["B"]*S["eG"])),
    ("gyy", S["E2"]*(1 - y**2)*(1 - al**2)**2/(k**2*S["B"]*S["eG"])),
]

def ev_iv(e, env):
    if e.is_Symbol: return env[e]
    if e.is_Integer: return mp.iv.mpf(int(e))
    if e.is_Rational: return mp.iv.mpf(e.p) / e.q
    a = [ev_iv(q, env) for q in e.args]
    if e.is_Add:
        r_ = a[0]
        for q in a[1:]: r_ = r_ + q
        return r_
    if e.is_Mul:
        r_ = a[0]
        for q in a[1:]: r_ = r_ * q
        return r_
    if e.is_Pow:
        b_, n = a[0], e.args[1]
        if n.is_Integer: return b_ ** int(n) if int(n) >= 0 else 1 / b_ ** (-int(n))
        if n.is_Rational and n.q == 2: return mp.iv.sqrt(b_) ** n.p if n.p > 0 else 1 / mp.iv.sqrt(b_) ** (-n.p)
    if isinstance(e, sp.exp): return mp.iv.exp(a[0])
    raise ValueError(e)

# point values and gradients wrt (x, y) of every named quantity, by full substitution (exact chain rule)
full = {}
for n, e in defs: full[n] = e.subs({S[m]: full[m] for m in full})
pt = {x: X0, y: Y0}
val, grad = {}, {}
for n, _ in defs:
    f_ = sp.lambdify((x, y), full[n], "mpmath")
    gx = sp.lambdify((x, y), sp.diff(full[n], x), "mpmath"); gy = sp.lambdify((x, y), sp.diff(full[n], y), "mpmath")
    val[n] = f_(X0, Y0); grad[n] = (gx(X0, Y0), gy(X0, Y0))
box = {x: mp.iv.mpf([X0 - h, X0 + h]), y: mp.iv.mpf([Y0 - h, Y0 + h])}
AUG = [a_.strip() for a_ in (sys.argv[5].split(",") if len(sys.argv) > 5 else [])]   # names treated as state variables
naive_env = dict(box); tight_env = dict(box)
print("aug = %s" % AUG); print("beta = %s   point (x, y) = (%s, %s)   h = %s" % (beta, mp.nstr(X0, 10), mp.nstr(Y0, 10), mp.nstr(h, 3)))
print("%-5s %12s %10s %10s %10s" % ("name", "value", "true rng", "total", "local"))
for n, e in defs:
    lin = (abs(grad[n][0]) + abs(grad[n][1])) * 2 * h
    e_sym = e
    wn = ev_iv(e_sym, naive_env); naive_env[S[n]] = wn
    if n in AUG: naive_env[S[n]] = mp.iv.mpf([val[n] - lin / 2, val[n] + lin / 2])   # tracked as a state: tight
    wl = ev_iv(e_sym, tight_env)
    tight_env[S[n]] = mp.iv.mpf([val[n] - lin / 2, val[n] + lin / 2])
    def wid(z): return float(z.b) - float(z.a)
    tot = wid(wn) / float(lin) if lin > 0 else float("nan"); loc = wid(wl) / float(lin) if lin > 0 else float("nan")
    print("%-5s %12.4e %10.2e %10.2e %10.2e" % (n, float(val[n]), float(lin), tot, loc))
