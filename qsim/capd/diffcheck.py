"""CAPD trust rule 3 (bridge, 2026-10-11): differential check of CAPD's MPFR interval arithmetic against Arb.

Registered in qsim/capd/DIFFCHECK.md BEFORE the run. For each working precision PREC in {53, 113, 256}, N random
operations (+ - * / sqrt exp log sin cos) on intervals with exactly representable endpoints, including near-tie and
huge/tiny cases, are sent to tests/diffcheck (CAPD MpInterval, built under the proof guard). For every OK result the
TRUE range of the operation over the input box is enclosed by Arb at 1024 bits (refined to 4096 on ambiguity) and
must lie inside CAPD's interval:
  * + - * /: every corner value (the range of these ops over a box is the hull of its corners);
  * sqrt exp log: the value at both endpoints (monotone); log with lo <= 0 requires CAPD's lower bound = -inf;
  * sin cos: both endpoint values, plus +1 / -1 whenever a maximum / minimum point lies inside the box (decided
    rigorously with Arb);
  * plus two random interior sample points for every op.
Verdict: a single certain non-containment, NaN, or inverted interval DISQUALIFIES. A per-call TIMEOUT for an
argument inside the guard's range is also a failure (liveness). THROW is allowed only where the op is
mathematically undefined somewhere on the box (0 in divisor, sqrt/log of a box reaching below 0) or where the trig
guard fires (|x| > 1e12, a control); a THROW anywhere else is counted and reported as a failure.
Usage: diffcheck.py [N_per_prec] [seed]
"""
import gzip, hashlib, json, random, subprocess, sys, time
from pathlib import Path
from flint import arb, ctx, fmpz

HERE = Path(__file__).resolve().parent
EXE = HERE / "tests" / "diffcheck"
OUT = HERE / "diffcheck_results"
EMAX = 2**30 - 1                     # MPFR 4 default exponent range: [1 - 2^30, 2^30 - 1]
TRIG_LIM = 10**12
ctx.prec = 1024                      # generator/sorting arithmetic: operands (<= 256-bit mantissas) are exact

# ---------------------------------------------------------------- exact dyadics: (m, e) means m * 2^e, m an int
def hexstr(m, e):
    return ("-" if m < 0 else "") + "0x%xp%d" % (abs(m), e)

def rnd_float(R, prec, emin, emax):
    """random prec-bit float with binary exponent (of its leading bit) in [emin, emax], random sign"""
    m = R.getrandbits(prec) | (1 << (prec - 1))
    e = R.randint(emin, emax) - (prec - 1)
    return (m if R.random() < 0.5 else -m, e)

def as_arb(d):
    m, e = d
    v = arb(m) * arb(2) ** e
    assert v.rad() == 0, "dyadic conversion not exact"
    return v

def parse_ra(s):
    """MPFR %Ra string -> ('fin', arb exact) | ('inf', +-1) | ('nan', None)"""
    t = s.strip().lower()
    if "nan" in t: return ("nan", None)
    if "inf" in t: return ("inf", -1 if t.startswith("-") else 1)
    neg = t.startswith("-"); t = t.lstrip("-+")
    assert t.startswith("0x"), s
    mant, ex = t[2:].split("p")
    ip, _, fp = mant.partition(".")
    m = int((ip + fp) or "0", 16)
    v = as_arb((-m if neg else m, int(ex) - 4 * len(fp)))
    return ("fin", v)

def key_cmp_le(a, b):
    """certainly a <= b ?  (arb semantics)"""
    return bool(a <= b)

# ---------------------------------------------------------------- generator
UNARY = ["sqrt", "exp", "log", "sin", "cos"]
BINARY = ["add", "sub", "mul", "div"]
OPS = BINARY + UNARY

def gen_interval(R, prec, kind, lo_e=-6, hi_e=6):
    a = rnd_float(R, prec, lo_e, hi_e)
    if kind == "point": return a, a
    if kind == "narrow":
        m, e = a; k = R.randint(1, 8)
        m2 = m + k
        if abs(m2) >= (1 << prec): m2 = m - k; a, b = (m2, e), (m, e)
        else: b = (m2, e)
        return (a, b) if as_arb(a) <= as_arb(b) else (b, a)
    b = rnd_float(R, prec, lo_e, hi_e)                   # wide
    return (a, b) if as_arb(a) <= as_arb(b) else (b, a)

def near_tie_operands(R, prec, op):
    """deliberately hard cases near rounding boundaries; each returns a list of point/narrow operand intervals"""
    one = (1 << (prec - 1), -(prec - 1))
    def pt(d): return (d, d)
    k = R.randint(prec // 2, prec - 1)
    j = R.randint(1, prec - 1)
    if op in ("add", "sub"):
        # 1 +- half an ulp (+- a quarter): exact result off the grid, at or next to a rounding tie
        y = (1, -prec - (R.randint(0, 2)))
        if R.random() < 0.5: y = (3, -prec - 2 - R.randint(0, 3))
        return [pt(one), pt(y if R.random() < 0.5 else (-y[0], y[1]))]
    if op == "mul":
        # (1 + 2^-j)(1 - 2^-j) = 1 - 2^-2j, and (1+2^-j)^2: products a hair off representable values
        a = ((1 << j) + 1, -j); b = ((1 << j) - 1 if R.random() < 0.5 else (1 << j) + 1, -j)
        return [pt(a), pt(b)]
    if op == "div":
        # q*b + tiny over b: quotient a hair off a representable value; and 1/3, 2/3 style
        if R.random() < 0.5:
            bm = R.getrandbits(prec // 2) | 1; qm = R.getrandbits(prec // 2) | 1
            am = qm * bm * 2 + (1 if R.random() < 0.5 else -1)
            while am.bit_length() > prec: am >>= 1
            return [pt((am, 0)), pt((bm * 2, 0))]
        return [pt((R.choice([1, 2, 5, 7]), 0)), pt((R.choice([3, 7, 9, 11, 13]), 0))]
    if op == "sqrt":
        s = R.getrandbits(prec // 2) | (1 << (prec // 2 - 1)); sq = s * s
        d = R.choice([0, 1, -1])
        return [pt((sq + d, -R.randint(0, 40) * 2))]
    if op == "exp":
        return [pt(R.choice([(0, 0), (1, -k), (-1, -k), (1, -prec - 5)]))]
    if op == "log":
        return [pt(R.choice([((1 << k) + 1, -k), ((1 << k) - 1, -k), (1, 0), (1, R.randint(-500, 500))]))]
    if op in ("sin", "cos"):
        # nearest prec-bit float to n*pi/2 (sin or cos is then tiny), tiny arguments, and 0
        c = R.random()
        if c < 0.6:
            n = R.choice([1, 2, 3, 4, R.randint(1, 10**6), R.randint(1, 10**11)])
            with ctx.workprec(prec + 400):
                x = arb.pi() * n / 2
                man, ex = x.mid().man_exp()
                e = int(ex) + int(man).bit_length() - prec
                m = int((x / arb(2) ** e).floor().unique_fmpz()) + R.choice([0, 1])
                if m.bit_length() > prec: m >>= 1; e += 1
            return [pt((m, e))]
        if c < 0.9: return [pt((R.choice([1, -1]) * (R.getrandbits(prec) | (1 << (prec - 1))), -prec - R.randint(5, 900)))]
        return [pt((0, 0))]
    raise ValueError(op)

def gen_case(R, prec):
    op = R.choice(OPS)
    c = R.random()
    if c < 0.25:
        ivs = near_tie_operands(R, prec, op); cat = "near-tie"
    elif c < 0.40:
        cat = "huge-tiny"
        if op == "exp": lo_e, hi_e = -1100, 40           # |x| <= 2^40 (Arb can enclose exp; result exponent fits fmpz)
        elif op in ("sin", "cos"): lo_e, hi_e = -1100, 39   # inside the guard range
        else: lo_e, hi_e = -(EMAX - 4), EMAX - 4
        ivs = [gen_interval(R, prec, R.choice(["point", "narrow", "wide"]), lo_e, hi_e)
               for _ in range(2 if op in BINARY else 1)]
    elif c < 0.42 and op in ("sin", "cos"):
        cat = "guard-control"                             # |x| > 1e12: the range guard must THROW (fail closed)
        ivs = [gen_interval(R, prec, "point", 40, 70)]
    else:
        cat = R.choice(["point", "narrow", "wide"])
        if op in ("sin", "cos") and cat == "wide" and R.random() < 0.7:
            # boxes of width up to ~7 placed anywhere in |x| <= 1e12, so extrema are inside some of them
            centre = rnd_float(R, prec, -4, R.choice([3, 10, 20, 39]))
            w = rnd_float(R, prec, -60, 2); w = (abs(w[0]), w[1])
            lo = centre; hi = (centre[0] * (1 << max(0, centre[1] - w[1])) + w[0] * (1 << max(0, w[1] - centre[1])),
                               min(centre[1], w[1]))
            while abs(hi[0]).bit_length() > prec:          # round hi UP (ceil) to prec bits: the box only gets wider
                hi = (-((-hi[0]) >> 1), hi[1] + 1)
            assert as_arb(lo) <= as_arb(hi)
            ivs = [(lo, hi)]
        else:
            ivs = [gen_interval(R, prec, cat) for _ in range(2 if op in BINARY else 1)]
    if op in BINARY and len(ivs) == 1: ivs = ivs * 2
    if op in UNARY: ivs = ivs[:1]
    # keep most sqrt/log arguments and most divisors inside the domain (the rest exercise the domain THROW path)
    def pos(iv):
        a, b = (abs(iv[0][0]), iv[0][1]), (abs(iv[1][0]), iv[1][1])
        return (a, b) if as_arb(a) <= as_arb(b) else (b, a)
    if cat != "near-tie" and op in ("sqrt", "log") and R.random() < 0.85: ivs = [pos(ivs[0])]
    if cat != "near-tie" and op == "div" and R.random() < 0.8: ivs = [ivs[0], pos(ivs[1])]
    return op, cat, ivs

# ---------------------------------------------------------------- reference (true range) checks
def f_arb(op, x, y=None):
    return {"add": lambda: x + y, "sub": lambda: x - y, "mul": lambda: x * y, "div": lambda: x / y,
            "sqrt": lambda: x.sqrt(), "exp": lambda: x.exp(), "log": lambda: x.log(),
            "sin": lambda: x.sin(), "cos": lambda: x.cos(), "clog": lambda: x.log()}[op]()

def first_int_geq(t):
    """ceil of a ball that certainly contains no integer; None if ambiguous"""
    n = t.floor().unique_fmpz()
    return None if n is None else int(n) + 1

def int_floor(t):
    n = t.floor().unique_fmpz()
    return None if n is None else int(n)

def extremum_inside(a, b, phase):
    """is there an integer k with a <= phase + 2 pi k <= b ?  (True/False, or None if undecided)"""
    tp = 2 * arb.pi()
    ka = first_int_geq((a - phase) / tp); kb = int_floor((b - phase) / tp)
    if ka is None or kb is None: return None
    return ka <= kb

def required_values(op, ivs, R):
    """list of arb balls (and special markers) that must lie in CAPD's enclosure; computed at the current ctx.prec"""
    xs = [(as_arb(lo), as_arb(hi)) for lo, hi in ivs]
    req = []
    (a, b) = xs[0]
    def sample(lo, hi):
        u = arb(R.getrandbits(30)) / arb(2) ** 30
        if lo == hi: return lo
        s_ = lo + (hi - lo) * u        # an interior point; used only if the whole ball certainly lies in [lo, hi]
        return s_ if (lo <= s_ and s_ <= hi) else lo
    if op in BINARY:
        (c, d) = xs[1]
        # + and - are kept as exact pairs ("SUM", u, w): a huge+tiny sum cannot be enclosed tightly enough by a
        # ball to compare with an endpoint, so contains() compares by rearrangement, (u - B) + w >= 0
        def val(x, y):
            if op == "add": return ("SUM", x, y)
            if op == "sub": return ("SUM", x, -y)
            return f_arb(op, x, y)
        for x in (a, b):
            for y in (c, d):
                req.append(val(x, y))
        for _ in range(2): req.append(val(sample(a, b), sample(c, d)))
    elif op in ("log", "clog") and not (a > 0):
        req.append("NEG_INF_LOWER"); req.append(f_arb(op, b) if b > 0 else None)
    elif op == "sqrt" and not (a >= 0):
        req.append(f_arb(op, b) if b >= 0 else None); req.append(arb(0) if b >= 0 else None)
    else:
        req += [f_arb(op, a), f_arb(op, b)]
        for _ in range(2): req.append(f_arb(op, sample(a, b)))
        if op in ("sin", "cos"):
            hp = arb.pi() / 2
            mx = extremum_inside(a, b, hp if op == "sin" else arb(0))
            mn = extremum_inside(a, b, -hp if op == "sin" else arb.pi())
            if mx is None or mn is None: req.append("UNDECIDED_EXTREMUM")
            if mx: req.append(arb(1))
            if mn: req.append(arb(-1))
    return [r for r in req if r is not None]

def _le(B, v):
    """is the exact bound B <= the value v ?  True / False (certainly not) / None (undecided)"""
    if isinstance(v, tuple):                      # ("SUM", u, w): decide B <= u + w by rearrangement
        _, u, w = v
        big, small = (u, w) if bool(abs(u) >= abs(w)) else (w, u)
        t = (big - B) + small
    else:
        t = v - B
    if t >= 0: return True
    if t < 0: return False
    return None

def _ge(B, v):
    """is the exact bound B >= the value v ?"""
    if isinstance(v, tuple):
        _, u, w = v
        r = _le(-B, ("SUM", -u, -w)); return r
    return _le(-B, -v)

def contains(L, Rr, v):
    """True: certainly inside; False: certainly outside; None: undecided at this precision"""
    if v == "NEG_INF_LOWER": return L[0] == "inf" and L[1] < 0
    if (L[0] == "inf" and L[1] > 0) or (Rr[0] == "inf" and Rr[1] < 0): return False
    lo = True if L[0] == "inf" else _le(L[1], v)
    hi = True if Rr[0] == "inf" else _ge(Rr[1], v)
    if lo is True and hi is True: return True
    if lo is False or hi is False: return False
    return None

def domain_throw_ok(op, ivs):
    if op == "div":
        c, d = as_arb(ivs[1][0]), as_arb(ivs[1][1]); return bool(c <= 0) and bool(d >= 0)
    if op == "sqrt": return bool(as_arb(ivs[0][0]) < 0)
    if op == "log": return bool(as_arb(ivs[0][0]) <= 0)
    return False

def guard_should_fire(op, ivs):
    if op not in ("sin", "cos"): return False
    a, b = as_arb(ivs[0][0]), as_arb(ivs[0][1])
    return not (bool(a >= -TRIG_LIM) and bool(b <= TRIG_LIM))

# ---------------------------------------------------------------- run
def run_harness(prec, lines):
    """feed lines to the harness; restart after a TIMEOUT (exit 3). Returns {id: (status, rest)}"""
    res = {}; todo = lines
    while todo:
        p = subprocess.run([str(EXE), str(prec)], input="\n".join(todo) + "\n", capture_output=True, text=True)
        for ln in p.stdout.splitlines():
            parts = ln.split(" ", 2)
            res[parts[0]] = (parts[1], parts[2] if len(parts) > 2 else "")
        if p.returncode == 3:
            done = set(res); todo = [l for l in todo if l.split(" ", 1)[0] not in done]
            continue
        if p.returncode != 0: raise RuntimeError("harness rc=%d stderr=%s" % (p.returncode, p.stderr[-500:]))
        break
    return res

def check_prec(prec, N, seed):
    R = random.Random("%d-%d" % (seed, prec))
    cases = []; lines = []
    for i in range(N):
        op, cat, ivs = gen_case(R, prec)
        cid = "p%d_%d" % (prec, i)
        flat = [hexstr(*d) for iv in ivs for d in iv]
        cases.append((cid, op, cat, ivs)); lines.append(" ".join([cid, op] + flat))
    for i in range(N_CLOG):     # checked_log controls: must THROW unless the box is > 0, else agree with log
        ivs = [gen_interval(R, prec, R.choice(["point", "narrow", "wide"]))]
        if i % 2 == 0:
            a_, b_ = (abs(ivs[0][0][0]), ivs[0][0][1]), (abs(ivs[0][1][0]), ivs[0][1][1])
            ivs = [(a_, b_) if as_arb(a_) <= as_arb(b_) else (b_, a_)]
        if i % 10 == 1: ivs = [((0, 0), (abs(ivs[0][1][0]), ivs[0][1][1]))]
        cid = "p%d_clog%d" % (prec, i); flat = [hexstr(*d) for d in ivs[0]]
        cases.append((cid, "clog", "guard-control", ivs)); lines.append(" ".join([cid, "clog"] + flat))
    t0 = time.time(); res = run_harness(prec, lines); t_capd = time.time() - t0
    stats = {}; fails = []; undecided = []; ok_cases = []
    Rs = random.Random("samples-%d-%d" % (seed, prec))
    for (cid, op, cat, ivs) in cases:
        st = stats.setdefault(op, {}).setdefault(cat, {"n": 0, "ok_contained": 0, "throw_domain": 0,
                                                         "throw_guard": 0, "max_rel_width": 0.0})
        st["n"] += 1
        status, rest = res.get(cid, ("MISSING", ""))
        gf = guard_should_fire(op, ivs)
        if status == "TIMEOUT": fails.append((cid, op, cat, "TIMEOUT", lines_by_id(lines, cid))); continue
        if status == "BADINPUT": fails.append((cid, op, cat, "BADINPUT(driver bug) " + rest, lines_by_id(lines, cid))); continue
        if status == "THROW":
            if gf and rest.startswith("capd_proof: trig argument"): st["throw_guard"] += 1
            elif op == "clog" and not bool(as_arb(ivs[0][0]) > 0) and rest.startswith("capd_proof: log argument"):
                st["throw_guard"] += 1
            elif domain_throw_ok(op, ivs): st["throw_domain"] += 1
            else: fails.append((cid, op, cat, "UNEXPECTED THROW " + rest, lines_by_id(lines, cid)))
            continue
        if status != "OK": fails.append((cid, op, cat, status, lines_by_id(lines, cid))); continue
        if gf or (op == "clog" and not bool(as_arb(ivs[0][0]) > 0)):
            fails.append((cid, op, cat, "GUARD DID NOT FIRE", lines_by_id(lines, cid))); continue
        Ls, Rs_ = rest.split()
        L, Rr = parse_ra(Ls), parse_ra(Rs_)
        if op == "log" and bool(as_arb(ivs[0][0]) < 0) and L[0] == "nan":
            # KNOWN CAPD DEFECT (found in the seed-1 smoke run, registered in DIFFCHECK.md before the full run):
            # log of a box reaching below 0 returns a NaN lower endpoint instead of throwing (testNaN is compiled
            # out). Counted separately; the upper endpoint must still enclose log(hi) when hi > 0. Proof code is
            # protected by capd_proof::checked_log (throws unless lo > 0) and the formula ban.
            st["log_nan_domain"] = st.get("log_nan_domain", 0) + 1
            hi_ = as_arb(ivs[0][1])
            if bool(hi_ > 0):
                ok_hi = None
                for wp in (1024, 4096):
                    with ctx.workprec(wp):
                        ok_hi = Rr[0] == "inf" and Rr[1] > 0 or (Rr[0] == "fin" and _ge(Rr[1], hi_.log()))
                    if ok_hi: break
                if not ok_hi: fails.append((cid, op, cat, "log upper endpoint wrong " + rest, lines_by_id(lines, cid)))
            continue
        if L[0] == "nan" or Rr[0] == "nan": fails.append((cid, op, cat, "NaN endpoint " + rest, lines_by_id(lines, cid))); continue
        if L[0] == "fin" and Rr[0] == "fin" and not bool(L[1] <= Rr[1]):
            fails.append((cid, op, cat, "INVERTED " + rest, lines_by_id(lines, cid))); continue
        verdict = judge(cid, op, ivs, L, Rr, Rs)
        if verdict is True:
            st["ok_contained"] += 1
            if op in ("sin", "cos"):     # coverage: how many contained boxes had an interior max or min
                with ctx.workprec(1024):
                    a_, b_ = as_arb(ivs[0][0]), as_arb(ivs[0][1]); hp = arb.pi() / 2
                    if extremum_inside(a_, b_, hp if op == "sin" else arb(0)) or \
                       extremum_inside(a_, b_, -hp if op == "sin" else arb.pi()):
                        st["extremum_boxes"] = st.get("extremum_boxes", 0) + 1
            if L[0] == "fin" and Rr[0] == "fin":
                with ctx.workprec(1024):
                    mid = (abs(L[1]) + abs(Rr[1])) / 2
                    if mid != 0:
                        rw = float(((Rr[1] - L[1]) / mid).mid())
                        st["max_rel_width"] = max(st["max_rel_width"], rw)
            if L[0] == "fin" and Rr[0] == "fin" and bool(L[1] < Rr[1]) and len(ok_cases) < N_CONTROL:
                ok_cases.append((cid, op, ivs, L, Rr))
        elif verdict is False: fails.append((cid, op, cat, "NON-CONTAINMENT " + rest, lines_by_id(lines, cid)))
        else: undecided.append((cid, op, cat, rest, lines_by_id(lines, cid)))
    # FIRED CONTROLS: the checker must reject deliberately broken enclosures. For contained results with L < R,
    # collapse CAPD's interval to [R, R] and to [L, L]; each mutant must be judged NON-CONTAINED (False), except
    # where the true range really is that single point (not possible when L < R for a correctly behaving CAPD
    # result unless the range is degenerate at an exact endpoint; any such case is listed, not hidden).
    ctrl = {"n": 0, "detected": 0, "missed": []}
    for (cid, op, ivs, L, Rr) in ok_cases:
        for mut in ((Rr, Rr), (L, L)):
            ctrl["n"] += 1
            v = judge(cid, op, ivs, mut[0], mut[1], Rs)
            if v is False: ctrl["detected"] += 1
            else: ctrl["missed"].append((cid, op, str(v), lines_by_id(lines, cid)))
    return dict(prec=prec, N=N, seed=seed, capd_seconds=round(t_capd, 1),
                ops_sha256=hashlib.sha256("\n".join(lines).encode()).hexdigest(),
                results_sha256=hashlib.sha256("\n".join("%s %s %s" % (k, *res[k]) for k in sorted(res)).encode()).hexdigest(),
                stats=stats, failures=fails, undecided=undecided, control=ctrl), lines, res

N_CONTROL = 3000
N_CLOG = 300

def judge(cid, op, ivs, L, Rr, Rs):
    """does CAPD's [L, Rr] contain the true range?  True / False / None, refining Arb precision on ambiguity"""
    verdict = None
    for wp in (1024, 4096, 16384):
        with ctx.workprec(wp):
            Rs.seed("%s-%s" % (cid, "s"))
            req = required_values(op, ivs, Rs)
            if "UNDECIDED_EXTREMUM" in req: verdict = None; continue
            vs = [contains(L, Rr, v) for v in req]
            if all(v is True for v in vs): return True
            if any(v is False for v in vs): return False
    return verdict

_LINE_INDEX = {}
def lines_by_id(lines, cid):
    if id(lines) not in _LINE_INDEX: _LINE_INDEX[id(lines)] = {l.split(" ", 1)[0]: l for l in lines}
    return _LINE_INDEX[id(lines)][cid]

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20261011
    OUT.mkdir(exist_ok=True)
    summary = []
    for prec in (53, 113, 256):
        t0 = time.time()
        r, lines, res = check_prec(prec, N, seed)
        r["seconds"] = round(time.time() - t0, 1)
        with gzip.open(OUT / ("ops_p%d.txt.gz" % prec), "wt") as f: f.write("\n".join(lines) + "\n")
        with gzip.open(OUT / ("capd_p%d.txt.gz" % prec), "wt") as f:
            f.write("\n".join("%s %s %s" % (k, *res[k]) for k in sorted(res)) + "\n")
        tot = sum(c["n"] for o in r["stats"].values() for c in o.values())
        c = r["control"]
        print("prec %d: %d ops, %d failures, %d undecided, %.0fs; control: %d/%d mutants detected" % (prec, tot, len(r["failures"]), len(r["undecided"]), r["seconds"], c["detected"], c["n"]), flush=True)
        for m_ in c["missed"][:5]: print("   CONTROL MISSED", m_, flush=True)
        for f_ in r["failures"][:10]: print("   FAIL", f_, flush=True)
        summary.append(r)
    total_fail = sum(len(r["failures"]) for r in summary); total_und = sum(len(r["undecided"]) for r in summary)
    ctrl_ok = all(r["control"]["n"] > 0 and r["control"]["detected"] == r["control"]["n"] for r in summary)
    verdict = ("PASS" if total_fail == 0 and total_und == 0 else ("FAIL" if total_fail else "UNDECIDED"))
    if not ctrl_ok: verdict += " (CONTROLS NOT ALL FIRED: checker not validated)"
    json.dump(dict(verdict=verdict, runs=summary), open(OUT / "summary.json", "w"), indent=1, default=str)
    print("VERDICT", verdict, "failures", total_fail, "undecided", total_und)
