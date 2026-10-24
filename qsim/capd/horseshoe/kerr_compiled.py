"""Adapter: a compiled B15 map (kerr_rs Rust cdylib, or kerr_p.dylib; same C ABI) behind MNFlow's interface (py_of, P, Pinv
with the same signatures and return conventions), so mn_numerics.plug_into_constructor and pcache wrap it unchanged and
the FROZEN B14 constructor is untouched. NON-RIGOROUS (constructor stage only). The per-call rtol/atol are honoured by
re-setting the library's tolerances whenever they change (the library keeps one global setting)."""
import ctypes, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
RUST = HERE / "kerr_rs" / "target" / "release" / "libkerr_rs.dylib"
CPP = HERE / "kerr_p.dylib"


class CompiledFlow:
    def __init__(self, lib=RUST, k=39.0, alpha=-0.625, beta=0.0, E=49 / 50, L=445 / 2):
        self.lib = L_ = ctypes.CDLL(str(lib)); self.path = str(lib)
        L_.kerr_set.argtypes = [ctypes.c_double] * 7
        L_.kerr_py.restype = ctypes.c_double; L_.kerr_py.argtypes = [ctypes.c_double, ctypes.c_double]
        L_.kerr_P.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
        L_.kerr_Pinv.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
        self.c = (float(k), float(alpha), float(beta), float(E), float(L)); self.tol = None
        self._tol(1e-12, 1e-12)

    def _tol(self, rtol, atol):
        if self.tol != (rtol, atol):
            self.lib.kerr_set(*self.c, float(rtol), float(atol)); self.tol = (rtol, atol)

    def py_of(self, x, px, y=0.0):
        assert y == 0.0, "the compiled lift is on y = 0 only"
        return self.lib.kerr_py(float(x), float(px))

    def P(self, w, n=1, jac=False, tmax=2000.0, rtol=1e-12, atol=1e-12):
        self._tol(rtol, atol); o = (ctypes.c_double * 7)()
        if not self.lib.kerr_P(float(w[0]), float(w[1]), int(n), int(bool(jac)), float(tmax), o):
            return None
        w2, T = np.array([o[0], o[1]]), o[2]
        return (w2, T) if not jac else (w2, T, np.array([[o[3], o[4]], [o[5], o[6]]]))

    def Pinv(self, w, tmax=2000.0, rtol=1e-12, atol=1e-12):
        self._tol(rtol, atol); o = (ctypes.c_double * 2)()
        if not self.lib.kerr_Pinv(float(w[0]), float(w[1]), float(tmax), o):
            return None
        return np.array([o[0], o[1]])
