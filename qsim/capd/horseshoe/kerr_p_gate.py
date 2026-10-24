"""Gate for kerr_p.dylib (the compiled B15 map candidate) against mn_numerics.MNFlow (the Python map B15 uses):
at N sample points around the B15 saddle z* = (1.8411884397812655, 0) (perturbations of size 1e-6 .. 1e-3, where the
constructor's manifold arcs live), compare py_of, P (image, return time, and the 2x2 section derivative with jac),
and Pinv. Criterion (proposed for the registered amendment): max relative difference <= 1e-10 in every compared
quantity at every point where both return within tmax; any point where exactly one of them returns is a FAIL.
Also reports wall time per call for both. The library defaults to kerr_p.dylib; pass kerr_rs/target/release/libkerr_rs.dylib
(same C ABI) to gate the Rust candidate.  Usage: kerr_p_gate.py [N] [tmax] [library]"""
import sys, time, ctypes, random, numpy as np, sympy as sp
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mn_numerics as MNN
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12; TMAX = float(sys.argv[2]) if len(sys.argv) > 2 else 2000.0
LIB = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / "kerr_p.dylib"
lib = ctypes.CDLL(str(LIB if LIB.is_absolute() else HERE / LIB)); print("library:", LIB, flush=True)
lib.kerr_set.argtypes = [ctypes.c_double] * 7
lib.kerr_py.restype = ctypes.c_double; lib.kerr_py.argtypes = [ctypes.c_double, ctypes.c_double]
lib.kerr_P.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
lib.kerr_Pinv.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
lib.kerr_set(39.0, -0.625, 0.0, 49 / 50, 445 / 2, 1e-12, 1e-12)
kerr = MNN.MNFlow(89, 80, 0, sp.Rational(49, 50), sp.Rational(445, 2))
rnd = random.Random(20261024)
z = np.array([1.8411884397812655, 0.0])
pts = [z + 10 ** rnd.uniform(-6, -3) * np.array([np.cos(a), np.sin(a)]) for a in (rnd.uniform(0, 2 * np.pi) for _ in range(N))]
worst = 0.0; bad = 0; tc = tp = 0.0
rel = lambda a, b: abs(a - b) / max(1.0, abs(b))
for w in pts:
    out = (ctypes.c_double * 7)()
    t0 = time.time(); okc = lib.kerr_P(w[0], w[1], 1, 1, TMAX, out); tc += time.time() - t0
    t0 = time.time(); rp = kerr.P(w, 1, jac=True, tmax=TMAX); tp += time.time() - t0
    pyc, pyp = lib.kerr_py(w[0], w[1]), kerr.py_of(w[0], w[1])
    worst = max(worst, rel(pyc, pyp))
    if bool(okc) != (rp is not None): bad += 1; print("RETURN MISMATCH at", w, okc, rp is not None); continue
    if not okc: continue
    (x2, T, D) = (rp[0], rp[1], rp[2])
    diffs = [rel(out[0], x2[0]), rel(out[1], x2[1]), rel(out[2], T)] + [rel(out[3 + 2 * i + j], D[i][j]) for i in range(2) for j in range(2)]
    worst = max(worst, max(diffs))
    oinv = (ctypes.c_double * 2)(); okic = lib.kerr_Pinv(w[0], w[1], TMAX, oinv); rinv = kerr.Pinv(w, tmax=TMAX)
    if bool(okic) != (rinv is not None): bad += 1; print("PINV MISMATCH at", w); continue
    if okic: worst = max(worst, rel(oinv[0], rinv[0]), rel(oinv[1], rinv[1]))
    print("w=(%.10f, %.10f) T=%.4f  max rel diff %.2e" % (w[0], w[1], T, max(diffs)), flush=True)
print("GATE: %d points, %d return mismatches, worst relative difference %.3e -> %s" % (N, bad, worst, "PASS" if bad == 0 and worst <= 1e-10 else "FAIL"))
print("wall: compiled %.3f s total, Python %.1f s total (speed-up ~%.0fx)" % (tc, tp, tp / max(tc, 1e-9)))
