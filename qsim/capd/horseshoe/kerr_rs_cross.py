"""Cross-check of the two compiled B15 map candidates: kerr_rs (Rust, own DOPRI5) against kerr_p.dylib (C++, Boost
DOPRI5) at the kerr_p_gate.py sample points (same seed) plus more, around the B15 saddle z* = (1.8411884397812655, 0).
Both are non-rigorous; this is not the gate against MNFlow (kerr_p_gate.py --lib), only a fast consistency check of
two independent integrators on the same generated field. Usage: kerr_rs_cross.py [N] [tmax] [n]"""
import sys, time, ctypes, random, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200; TMAX = float(sys.argv[2]) if len(sys.argv) > 2 else 2000.0
NRET = int(sys.argv[3]) if len(sys.argv) > 3 else 1
def load(p):
    lib = ctypes.CDLL(str(p))
    lib.kerr_set.argtypes = [ctypes.c_double] * 7
    lib.kerr_py.restype = ctypes.c_double; lib.kerr_py.argtypes = [ctypes.c_double, ctypes.c_double]
    lib.kerr_P.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
    lib.kerr_Pinv.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
    lib.kerr_set(39.0, -0.625, 0.0, 49 / 50, 445 / 2, 1e-12, 1e-12)
    return lib
A, B = load(HERE / "kerr_rs" / "target" / "release" / "libkerr_rs.dylib"), load(HERE / "kerr_p.dylib")
rnd = random.Random(20261024)
z = np.array([1.8411884397812655, 0.0])
pts = [z + 10 ** rnd.uniform(-6, -3) * np.array([np.cos(a), np.sin(a)]) for a in (rnd.uniform(0, 2 * np.pi) for _ in range(N))]
rel = lambda a, b: abs(a - b) / max(1.0, abs(b))
worst = {"py": 0.0, "P": 0.0, "T": 0.0, "DP": 0.0, "Pinv": 0.0}; bad = 0; ta = tb = 0.0
for w in pts:
    worst["py"] = max(worst["py"], rel(A.kerr_py(*w), B.kerr_py(*w)))
    oa, ob = (ctypes.c_double * 7)(), (ctypes.c_double * 7)()
    t0 = time.time(); ka = A.kerr_P(w[0], w[1], NRET, 1, TMAX, oa); ta += time.time() - t0
    t0 = time.time(); kb = B.kerr_P(w[0], w[1], NRET, 1, TMAX, ob); tb += time.time() - t0
    if ka != kb: bad += 1; print("RETURN MISMATCH at", w, ka, kb); continue
    if ka:
        worst["P"] = max(worst["P"], rel(oa[0], ob[0]), rel(oa[1], ob[1])); worst["T"] = max(worst["T"], rel(oa[2], ob[2]))
        worst["DP"] = max([worst["DP"]] + [rel(oa[k], ob[k]) for k in range(3, 7)])
    ia, ib = (ctypes.c_double * 2)(), (ctypes.c_double * 2)()
    ja, jb = A.kerr_Pinv(w[0], w[1], TMAX, ia), B.kerr_Pinv(w[0], w[1], TMAX, ib)
    if ja != jb: bad += 1; print("PINV MISMATCH at", w); continue
    if ja: worst["Pinv"] = max(worst["Pinv"], rel(ia[0], ib[0]), rel(ia[1], ib[1]))
print("CROSS (n=%d): %d points, %d mismatches; worst rel diff: %s" % (NRET, N, bad, ", ".join("%s %.2e" % kv for kv in worst.items())))
print("wall: rust %.3f s, c++ %.3f s (P with jac, per call: %.2f ms vs %.2f ms)" % (ta, tb, 1e3 * ta / N, 1e3 * tb / N))
