import sys, numpy as np
m, n, c = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3] == "c"
rng = np.random.default_rng(0); A = rng.standard_normal((m, n)) + (1j*rng.standard_normal((m, n)) if c else 0)
np.linalg.svd(A, compute_uv=False); print("clean")
