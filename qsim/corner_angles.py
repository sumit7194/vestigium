"""
The corner FUNCTION a(theta) — turning last night's single point into a curve.

corner_coefficient.py measured theta = pi/2 only, and I flagged the limitation
without addressing it: a square lattice can only make 90-degree corners cleanly,
because any other angle needs a staircase boundary whose steps are THEMSELVES
90-degree corners. Measuring N staircase corners is not measuring a(theta).

THE FIX IS A DIFFERENT LATTICE. On a TRIANGULAR lattice the natural angles are
multiples of 60 degrees, and two clean shapes exist:
    EQUILATERAL TRIANGLE of side l  ->  3 corners at  60 deg,  perimeter 3l
    REGULAR HEXAGON  of side R      ->  6 corners at 120 deg,  perimeter 6R
Both scale linearly, both are exact on the lattice, neither needs a staircase.

Extraction (the log coefficient is insensitive to the length convention, since
ln(c*l) only shifts the constant):
    S = A*perimeter + B*ln(l) + C ,   B = -(number of corners) * a(theta)

WHY THIS IS A STRONGER TEST THAN 90 DEGREES ALONE. If a(theta) is universal it
cannot depend on the regulator OR on the lattice. So combining a(60), a(120) from
the triangular lattice with a(90) from the square lattice tests LATTICE-independence
as well as regulator-independence — a strictly stronger claim than either alone.

=============================== PRE-REGISTRATION ==============================
Written before running. Falsification conditions stated.

P1 ORDERING (the hard prediction): a(60) > a(90) > a(120), strictly.
   Reason: a(theta) measures how much a corner contributes; it diverges as the
   corner closes (theta -> 0) and vanishes as the boundary flattens (theta -> pi).
   FALSIFIED by any inversion of that ordering.

P2 REGULATOR-INDEPENDENCE AT EACH ANGLE: the across-regulator spread of a(60)
   and of a(120) each sits at or below the method floor, while the AREA
   coefficient stays regulator-dependent at both angles (tens of percent).
   FALSIFIED if a corner spread is comparable to the area spread.

P3 SOFT expectation, not a gate: if the near-flat quadratic form a ~ (pi-theta)^2
   held everywhere it would give a(60)/a(90) = 1.78 and a(90)/a(120) = 2.25.
   The true a(theta) diverges faster than quadratic as theta -> 0, so I expect
   a(60)/a(90) LARGER than 1.78. Recorded as an expectation, not a criterion.

CONTROL THAT CAN FAIL (new, and specific to this geometry): the AREA coefficient
A is a property of the cut, not of the region's shape. So A extracted from
TRIANGLES and from HEXAGONS on the same lattice with the same regulator MUST
agree. If they disagree, the extraction is broken and no corner number is
trustworthy. This control has a genuine failure mode and is not decoration.

MODEL ROBUSTNESS (the bridge's lesson from last night, applied up front): the
3-parameter model is not the only legitimate one, and a 1% unmodelled 1/l term
moved the square-lattice answer by 7%. So every number here is also reported
under a 4-parameter fit that includes 1/l, and the spread is quoted BOTH ways.
===============================================================================
"""
import json, os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"          # machine is oversubscribed; be a good neighbour
import numpy as np

# ---- triangular-lattice dispersions, normalised so every one -> m^2 + k^2 ----
# index-space phases: u1 = th1, u2 = th2, u3 = th1 - th2  (the three bond directions)
def _u(th1, th2):
    return th1, th2, th1 - th2

def K2t(th1, th2):                                   # 2nd-order, 6 neighbours
    return (4/3)*sum(1 - np.cos(u) for u in _u(th1, th2))

def K4t(th1, th2):                                   # 4th-order improved
    h = lambda u: (8/3)*(1 - np.cos(u)) - (1/6)*(1 - np.cos(2*u))
    return (2/3)*sum(h(u) for u in _u(th1, th2))

def make_regs(m):
    return {"nn":           lambda a, b: m*m + K2t(a, b),
            "improved":     lambda a, b: m*m + K4t(a, b),
            "higher_deriv": lambda a, b: m*m + K2t(a, b) + 0.25*K2t(a, b)**2,
            "smeared":      lambda a, b: m*m + K2t(a, b)*np.exp(0.15*K2t(a, b))}
NAMES = ["nn", "improved", "higher_deriv", "smeared"]

def kernels(N, reg):
    n = np.arange(N)
    t1, t2 = np.meshgrid(2*np.pi*n/N, 2*np.pi*n/N, indexing="ij")
    w = np.sqrt(reg(t1, t2))
    return np.real(np.fft.ifft2(1.0/w))/2.0, np.real(np.fft.ifft2(w))/2.0

def entropy(sites, N, GX, GP):
    d1 = (sites[:, 0][:, None] - sites[:, 0][None, :]) % N
    d2 = (sites[:, 1][:, None] - sites[:, 1][None, :]) % N
    X, P = GX[d1, d2], GP[d1, d2]
    e, U = np.linalg.eigh(X)
    Xh = (U*np.sqrt(np.clip(e, 1e-300, None))) @ U.T
    C = Xh @ P @ Xh
    nu = np.maximum(np.sqrt(np.clip(np.linalg.eigvalsh(0.5*(C + C.T)), 0.25, None)), 0.5 + 1e-12)
    a, b = nu + 0.5, nu - 0.5
    return float(np.sum(a*np.log(a) - b*np.log(b)))

# ---- the two exact shapes on a triangular lattice ----
def triangle(l, N):     # 3 corners at 60 deg
    o = N//2 - l//2
    return np.array([(o+i, o+j) for i in range(l) for j in range(l - i)])

def hexagon(R, N):      # 6 corners at 120 deg
    o = N//2
    return np.array([(o+i, o+j) for i in range(-R, R+1) for j in range(-R, R+1)
                     if abs(i + j) <= R])

def fit(xs, S, per_unit, rich=False):
    x = np.array(xs, float)
    cols = [per_unit*x, np.log(x), np.ones(x.size)] + ([1.0/x] if rich else [])
    c, *_ = np.linalg.lstsq(np.vstack(cols).T, np.array(S), rcond=None)
    return c[0], c[1]                                 # A, B

# ================================ measurement ================================
N, m = 160, 0.01
TRI = [8, 12, 16, 20, 24, 28]
HEX = [4, 6, 8, 10, 12, 14]
print(f"triangular lattice N={N}, m={m} (xi={1/m:.0f})")
print(f"  triangles l={TRI}  (max {len(triangle(TRI[-1],N))} sites)")
print(f"  hexagons  R={HEX}  (max {len(hexagon(HEX[-1],N))} sites)")

res = {}
REG = make_regs(m)
for nm in NAMES:
    GX, GP = kernels(N, REG[nm])
    S_t = [entropy(triangle(l, N), N, GX, GP) for l in TRI]
    S_h = [entropy(hexagon(R, N), N, GX, GP) for R in HEX]
    At3, Bt3 = fit(TRI, S_t, 3);  Ah3, Bh3 = fit(HEX, S_h, 6)
    At4, Bt4 = fit(TRI, S_t, 3, True); Ah4, Bh4 = fit(HEX, S_h, 6, True)
    res[nm] = dict(a60_3=-Bt3/3, a120_3=-Bh3/6, a60_4=-Bt4/3, a120_4=-Bh4/6,
                   A_tri=At3, A_hex=Ah3)

print("\nCONTROL THAT CAN FAIL — area coefficient must not depend on region SHAPE")
print(f"{'regulator':>13} {'A from triangles':>17} {'A from hexagons':>16} {'disagreement':>13}")
ctrl_ok = True
for nm in NAMES:
    d = abs(res[nm]['A_tri'] - res[nm]['A_hex'])/abs(res[nm]['A_tri'])*100
    ctrl_ok &= d < 5.0
    print(f"{nm:>13} {res[nm]['A_tri']:17.5f} {res[nm]['A_hex']:16.5f} {d:12.2f}%")
print(f"  -> {'PASSED' if ctrl_ok else '*** FAILED ***'} (bar: <5%)")

print("\nCORNER FUNCTION")
print(f"{'regulator':>13} {'a(60)':>10} {'a(120)':>10} {'a(60) 4par':>11} {'a(120) 4par':>12}")
for nm in NAMES:
    r = res[nm]
    print(f"{nm:>13} {r['a60_3']:10.5f} {r['a120_3']:10.5f} {r['a60_4']:11.5f} {r['a120_4']:12.5f}")

def spread(v):
    v = np.array(v); return (v.max()-v.min())/abs(v.mean())*100
s60_3 = spread([res[n]['a60_3'] for n in NAMES]);  s120_3 = spread([res[n]['a120_3'] for n in NAMES])
s60_4 = spread([res[n]['a60_4'] for n in NAMES]);  s120_4 = spread([res[n]['a120_4'] for n in NAMES])
sA    = spread([res[n]['A_tri'] for n in NAMES])
a60, a120 = np.mean([res[n]['a60_3'] for n in NAMES]), np.mean([res[n]['a120_3'] for n in NAMES])
a90 = 0.011604                                   # nn value, square lattice, same m

print(f"\nACROSS-REGULATOR SPREAD")
print(f"  area coefficient        : {sA:6.1f}%   <- must stay large")
print(f"  a(60)   3-param/4-param : {s60_3:6.2f}% / {s60_4:.2f}%")
print(f"  a(120)  3-param/4-param : {s120_3:6.2f}% / {s120_4:.2f}%")

print(f"\nVERDICT AGAINST PRE-REGISTRATION")
print(f"  a(60) = {a60:.5f}   a(90) = {a90:.5f} (square lattice)   a(120) = {a120:.5f}")
p1 = a60 > a90 > a120
print(f"  P1 ordering a(60) > a(90) > a(120) : {'CONFIRMED' if p1 else '*** FALSIFIED ***'}")
p2 = max(s60_3, s120_3) < sA/5
print(f"  P2 corners universal, area not     : {'CONFIRMED' if p2 else '*** FALSIFIED ***'}")
print(f"  P3 ratios: a(60)/a(90) = {a60/a90:.2f} (expected >1.78), "
      f"a(90)/a(120) = {a90/a120:.2f} (quadratic form gives 2.25)")

json.dump({"lattice": "triangular", "N": N, "m": m,
           "prereg": {"P1": "a(60)>a(90)>a(120)", "P2": "corner spread << area spread",
                      "P3_soft": "a(60)/a(90) > 1.78"},
           "per_regulator": {n: {k: float(v) for k, v in res[n].items()} for n in NAMES},
           "spreads": {"area": sA, "a60_3": s60_3, "a60_4": s60_4,
                       "a120_3": s120_3, "a120_4": s120_4},
           "values": {"a60": a60, "a90_square_lattice": a90, "a120": a120},
           "control_shape_independence_passed": bool(ctrl_ok),
           "verdict": {"P1": bool(p1), "P2": bool(p2)}},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "corner_angles.json"), "w"), indent=1)
print("\nsaved -> qsim/corner_angles.json")
