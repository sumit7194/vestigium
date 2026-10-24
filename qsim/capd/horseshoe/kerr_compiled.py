"""Adapter: a compiled B15 map (kerr_rs Rust cdylib, or kerr_p.dylib; same C ABI) behind MNFlow's interface (py_of, P, Pinv
with the same signatures and return conventions), so mn_numerics.plug_into_constructor and pcache wrap it unchanged and
the FROZEN B14 constructor is untouched. NON-RIGOROUS (constructor stage only). The per-call rtol/atol are honoured by
re-setting the library's tolerances whenever they change (the library keeps one global setting).
A library return of -1 (an integration check failed: E2 / E5 in kerr_rs) raises MapCheckFailed: a numerical failure is
never passed to the constructor as None ("no return"), which it would act on as geometry; pcache journals no raised call.
A return of -2 (step-size collapse, B15b-1) goes to the plunge certificate (kerr_plunge.py): certified -> None, with the
record appended to self.plunges (reason 'plunge-certified'); not certified -> MapCheckFailed. delta_floor is the
registered max(1e-6, 100 x the G4-measured state error); the run script sets it, and 1e-6 is the floor."""
import ctypes, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
RUST = HERE / "kerr_rs" / "target" / "release" / "libkerr_rs.dylib"
CPP = HERE / "kerr_p.dylib"


class MapCheckFailed(RuntimeError):
    pass


class CompiledFlow:
    def __init__(self, lib=RUST, k=39.0, alpha=-0.625, beta=0.0, E=49 / 50, L=445 / 2):
        self.lib = L_ = ctypes.CDLL(str(lib)); self.path = str(lib)
        L_.kerr_set.argtypes = [ctypes.c_double] * 7
        L_.kerr_py.restype = ctypes.c_double; L_.kerr_py.argtypes = [ctypes.c_double, ctypes.c_double]
        L_.kerr_P.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
        L_.kerr_P.restype = ctypes.c_int; L_.kerr_Pinv.restype = ctypes.c_int
        L_.kerr_state_at.restype = ctypes.c_int; L_.kerr_state_at.argtypes = [ctypes.c_double] * 4 + [ctypes.POINTER(ctypes.c_double)]
        self.plunges = []; self.delta_floor = 1e-6
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
        r = self.lib.kerr_P(float(w[0]), float(w[1]), int(n), int(bool(jac)), float(tmax), o)
        if r == -2:
            if int(n) != 1:
                raise MapCheckFailed("HARNESS-ERROR: collapse inside an n = %d call (not certifiable) at w = %r" % (n, tuple(w)))
            return self._plunge("P", w, +1.0)
        if r < 0:
            raise MapCheckFailed("HARNESS-ERROR: kerr_P integration check failed at w = %r (%s)" % (tuple(w), self.path))
        if r == 0:
            return None
        w2, T = np.array([o[0], o[1]]), o[2]
        return (w2, T) if not jac else (w2, T, np.array([[o[3], o[4]], [o[5], o[6]]]))

    def Pinv(self, w, tmax=2000.0, rtol=1e-12, atol=1e-12):
        self._tol(rtol, atol); o = (ctypes.c_double * 2)()
        r = self.lib.kerr_Pinv(float(w[0]), float(w[1]), float(tmax), o)
        if r == -2:
            return self._plunge("Pinv", w, -1.0)
        if r < 0:
            raise MapCheckFailed("HARNESS-ERROR: kerr_Pinv integration check failed at w = %r (%s)" % (tuple(w), self.path))
        if r == 0:
            return None
        return np.array([o[0], o[1]])

    def stats(self):
        """E3 diagnostics of the last call (kerr_rs only): crossings, max |ydot| h dtheta, max E2 difference, min |ydot|
        at a crossing, E2 retries, E5 retries"""
        o = (ctypes.c_double * 6)(); self.lib.kerr_stats(o)
        return dict(zip(("crossings", "event_bound", "restep_diff", "min_ydot", "e2_retries", "e5_retries"), o[:]))

    def _test_e2_bar(self, bar):
        """TEST HOOK for the -1 negative control only (registered E2 bar: 1e-11); never used in a counted run"""
        self.lib.kerr_test_e2_bar.argtypes = [ctypes.c_double]; self.lib.kerr_test_e2_bar(float(bar))

    def _plunge(self, kind, w, sign):
        import kerr_plunge
        c = (ctypes.c_double * 5)(); self.lib.kerr_collapse(c)
        try:
            rec = kerr_plunge.certify(self, kind, w, list(c), sign, self.delta_floor)
        except kerr_plunge.NotCertified as e:
            raise MapCheckFailed("HARNESS-ERROR: %s collapse at w = %r not certified: %s" % (kind, tuple(w), e))
        rec["reason"] = "plunge-certified"; self.plunges.append(rec)
        return None
