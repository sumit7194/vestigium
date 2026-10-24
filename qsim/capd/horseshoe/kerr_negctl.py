"""Negative control for the B15b failure path: with E2's bar forced negative (test hook), every crossing must fail E2,
so P, P with jac and Pinv must each return -1 from the library and raise MapCheckFailed in the adapter (never None,
"no return"); with the registered bar restored, the same calls must succeed. Run for both compiled maps."""
import sys, numpy as np
import kerr_compiled as K
w = np.array([1.8411884397812655 + 1e-4, 2e-5]); ok = True
for L in (K.RUST, K.CPP):
    f = K.CompiledFlow(L); f._test_e2_bar(-1.0)
    for name, call in (("P", lambda: f.P(w, 1)), ("P jac", lambda: f.P(w, 1, jac=True)), ("Pinv", lambda: f.Pinv(w))):
        try:
            r = call(); print(L.name, name, "FAIL: returned", "None" if r is None else "a value"); ok = False
        except K.MapCheckFailed:
            st = f.stats(); print(L.name, name, "raised MapCheckFailed; E2 retries %d" % st["e2_retries"])
            ok &= st["e2_retries"] == 11
    f._test_e2_bar(1e-11)
    r = (f.P(w, 1), f.P(w, 1, jac=True), f.Pinv(w)); good = all(x is not None for x in r)
    print(L.name, "restored bar: all succeed" if good else "restored bar: FAIL"); ok &= good
print("NEGATIVE CONTROL", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
