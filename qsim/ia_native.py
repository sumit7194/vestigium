"""
Python front end of the iahub v2 native core (PREREG_iahub_v2.md, registered 33321aa).

  * SLPBuilder: compiles SymPy expressions (generic tree walk with memo) and Q(t,E1..E3) polynomials (grouped
    by E-monomial, Horner in t) into a flat straight-line program, evaluated by the Rust core both as
    truncated power series and as scalar balls.
  * write_job / run_job: text job file -> native/iahub binary -> parsed enclosures (python-flint acb balls,
    parsed from Arb's own ball strings, which rounds outward).
  * certificate_gl2: the scale-free certificate for the NON-reduced first-order system (det != 1):
        (i')  tr(g)^2/det(g) not in [0, 4]   (<=> normalised trace not in [-2, 2], either square root)
        (iii) tr(g h g^-1 h^-1) != 2         (the commutator lies in SL(2) automatically)
    each decided with 'certainly' logic on the balls.
"""
import os, subprocess, tempfile
import sympy as sp
from flint import acb, arb, ctx

BIN = "/Users/sumit/Github/quantum/native/iahub/target/release/iahub"
ctx.prec = 192


class SLPBuilder:
    def __init__(self):
        self.ins = []
        self.memo = {}

    def _emit(self, key, line):
        if key is not None and key in self.memo:
            return self.memo[key]
        self.ins.append(line)
        r = len(self.ins) - 1
        if key is not None:
            self.memo[key] = r
        return r

    def var(self):
        return self._emit(("VAR",), "VAR")

    def const(self, q):
        q = sp.Rational(q)
        return self._emit(("C", q), f"CONST {q.p}/{q.q}")

    def add(self, a, b):
        return self._emit(("ADD",) + tuple(sorted((a, b))), f"ADD {a} {b}")

    def sub(self, a, b):
        return self._emit(("SUB", a, b), f"SUB {a} {b}")

    def mul(self, a, b):
        return self._emit(("MUL",) + tuple(sorted((a, b))), f"MUL {a} {b}")

    def neg(self, a):
        return self._emit(("NEG", a), f"NEG {a}")

    def inv(self, a):
        return self._emit(("INV", a), f"INV {a}")

    def exp(self, a):
        return self._emit(("EXP", a), f"EXP {a}")

    def powi(self, a, k):
        assert k >= 1
        key = ("POW", a, k)
        if key in self.memo:
            return self.memo[key]
        if k == 1:
            r = a
        elif k % 2 == 0:
            h = self.powi(a, k//2)
            r = self.mul(h, h)
        else:
            r = self.mul(self.powi(a, k - 1), a)
        self.memo[key] = r
        return r

    # ---- generic SymPy expression in one variable z (+, *, integer powers, exp, rationals) ----
    def expr(self, e, z):
        e = sp.sympify(e)
        key = ("EXPR", e)
        if key in self.memo:
            return self.memo[key]
        if e == z:
            r = self.var()
        elif e.is_Rational:
            r = self.const(e)
        elif e.is_Add:
            r = self.expr(e.args[0], z)
            for a in e.args[1:]:
                r = self.add(r, self.expr(a, z))
        elif e.is_Mul:
            r = self.expr(e.args[0], z)
            for a in e.args[1:]:
                r = self.mul(r, self.expr(a, z))
        elif e.is_Pow:
            b, n = e.args
            if not n.is_Integer:
                raise ValueError(f"non-integer power {e}: refused (branch cut)")
            n = int(n)
            r = self.powi(self.expr(b, z), abs(n)) if n != 0 else self.const(1)
            if n < 0:
                r = self.inv(r)
        elif isinstance(e, sp.exp):
            r = self.exp(self.expr(e.args[0], z))
        else:
            raise ValueError(f"unsupported node {type(e).__name__}: {e}")
        self.memo[key] = r
        return r

    # ---- polynomial in t over Q: Horner ----
    def poly_t(self, coeffs_desc, t):
        """coeffs_desc: list of Rationals, highest degree first."""
        r = self.const(coeffs_desc[0])
        for c in coeffs_desc[1:]:
            r = self.mul(r, t)
            if c != 0:
                r = self.add(r, self.const(c))
        return r

    # ---- polynomial in (t, E1..Em) over Q, grouped by E-monomial, Horner in t ----
    def poly_tE(self, P, gens, Eregs, t):
        """P: sympy Poly in gens = (t, E1, ..., Em); Eregs: registers of E_i."""
        groups = {}
        for mon, c in P.terms():
            groups.setdefault(mon[1:], {})[mon[0]] = sp.Rational(c)
        total = None
        for emon, tc in sorted(groups.items()):
            deg = max(tc)
            coeffs = [tc.get(k, sp.Integer(0)) for k in range(deg, -1, -1)]
            term = self.poly_t(coeffs, t)
            for Er, k in zip(Eregs, emon):
                if k:
                    term = self.mul(term, self.powi(Er, k))
            total = term if total is None else self.add(total, term)
        return total if total is not None else self.const(0)


def fmt(v):
    return repr(float(v))


def write_job(b, entries, loops, bad=(), obst=(), prec=192, N=140, cmax=4.0, hmax=0.25, frac=0.2, threads=4,
              path=None):
    """entries: 2x2 nested list of (num_reg, den_reg); loops: list of (name, [complex points])."""
    lines = [f"PREC {prec}", f"N {N}", f"CMAX {cmax}", f"HMAX {hmax}", f"FRAC {frac}", f"THREADS {threads}"]
    lines += [f"I {s}" for s in b.ins]
    for i in range(2):
        for j in range(2):
            lines.append(f"ENTRY {i} {j} {entries[i][j][0]} {entries[i][j][1]}")
    lines += [f"BAD {fmt(complex(c).real)} {fmt(complex(c).imag)}" for c in bad]
    lines += [f"OBST {fmt(complex(c).real)} {fmt(complex(c).imag)}" for c in obst]
    for name, pts in loops:
        lines.append(f"LOOP {name} {len(pts)}")
        lines += [f"P {fmt(complex(p).real)} {fmt(complex(p).imag)}" for p in pts]
    if path is None:
        fd, path = tempfile.mkstemp(suffix=".job", prefix="iahub_")
        os.close(fd)
    open(path, "w").write("\n".join(lines) + "\n")
    return path


def _ball(s):
    re, im = s.split("|")
    return acb(arb(re), arb(im))


def run_job(path, timeout=None):
    out = subprocess.run([BIN, path], capture_output=True, text=True, timeout=timeout)
    if out.returncode != 0:
        raise RuntimeError(f"iahub failed: {out.stderr[-2000:]}")
    res, cur = {}, None
    for line in out.stdout.splitlines():
        w = line.split(" ", 3)
        if w[0] == "LOOP":
            cur = res.setdefault(w[1], dict(M=[[None, None], [None, None]]))
        elif w[0] == "STATUS":
            cur["status"] = line[len("STATUS "):]
        elif w[0] == "STEPS":
            cur["steps"] = int(w[1])
        elif w[0] == "M":
            cur["M"][int(w[1])][int(w[2])] = _ball(w[3])
    return res


def matmul(A, B):
    return [[A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
            [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]]


def det(A):
    return A[0][0]*A[1][1] - A[0][1]*A[1][0]


def inv(A):
    d = det(A)
    return [[A[1][1]/d, -A[0][1]/d], [-A[1][0]/d, A[0][0]/d]]


def tr(A):
    return A[0][0] + A[1][1]


def certainly_outside_0_4(w):
    return bool(w.imag > 0 or w.imag < 0 or w.real < 0 or w.real > 4)


def certainly_ne(t, v):
    d = t - v
    return bool(d.real > 0 or d.real < 0 or d.imag > 0 or d.imag < 0)


def loxodromic_gl2(g):
    """tr^2/det not in [0,4], certainly."""
    return certainly_outside_0_4(tr(g)**2/det(g))


def certificate_gl2(g, h):
    c = tr(matmul(matmul(g, h), matmul(inv(g), inv(h))))
    ok = loxodromic_gl2(g) and loxodromic_gl2(h) and certainly_ne(c, 2)
    return ok, dict(w_g=str(tr(g)**2/det(g)), w_h=str(tr(h)**2/det(h)), tr_comm=str(c))
