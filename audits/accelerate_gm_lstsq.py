import sys, numpy as np
kind, m, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rng = np.random.default_rng(0)
if kind == "qr":   np.linalg.qr(rng.standard_normal((m, n)), mode="r")
elif kind == "lstsq_c":
    A = rng.standard_normal((m, n)) + 1j*rng.standard_normal((m, n)); b = rng.standard_normal(m) + 0j
    for _ in range(3): np.linalg.lstsq(A, b, rcond=None)
elif kind == "lstsq_r":
    A = rng.standard_normal((m, n)); b = rng.standard_normal(m)
    for _ in range(3): np.linalg.lstsq(A, b, rcond=None)
print("clean", kind, m, n)
