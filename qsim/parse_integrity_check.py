"""Parse-integrity check (bridge request, 2026-10-11): tabula found that Python 3.12's C tokenizer can crash or
silently corrupt the heap when sympy.parse_expr reads the large single-line srepr strings in the TS2 component files.
We run Python 3.13. Each invocation parses ALL metric files our pipelines read, with the same loaders, and prints a
sha256 of srepr(component) per file. Run it in fresh processes under PYTHONMALLOC=debug -X faulthandler; every
run's hashes must be identical."""
import hashlib, os, sys
import sympy as sp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mr_ts2 as T2, mr_mn_axis as MA
out = []
for f in (T2.TS_P1, T2.TS_P2, T2.KERR_P1, T2.KERR_P2):
    C = T2._read_components(os.path.join(T2.PKG, f))
    out.append((f, hashlib.sha256("|".join(f"{k}={sp.srepr(C[k])}" for k in sorted(C)).encode()).hexdigest()[:16]))
for f in ("mn_metric_components_p1.txt", "mn_metric_components_p2.txt", "mn_metric_components_KERR_p1.txt",
          "mn_metric_components_KERR_p2.txt"):
    C, x, y = MA.load(f)
    out.append((f, hashlib.sha256("|".join(f"{k}={sp.srepr(C[k])}" for k in sorted(C)).encode()).hexdigest()[:16]))
print(" ".join(f"{f}:{h}" for f, h in out))
