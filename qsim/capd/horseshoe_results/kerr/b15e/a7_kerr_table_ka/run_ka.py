"""B15e A7: kerr_table known-answer BRANCH CHECK (the personal Bridge's choice). It is built from b15d_split's OWN canned
fixtures (_E/_A, CFP), so it checks the branches of kerr_table against the code's fixtures; it is NOT an independent
answer. Three scratch copies of the b15d tree layout (kerr/build.json copied; kerr_e/, kerr_a/ outputs written from the
fixtures) under this folder; b15d_split.OUT is pointed at each in turn. Nothing outside this folder is read or written,
except build.json (read). Run with sims/.venv python. Written by Claude Opus 5.5 (Quantum-personal)."""
import json, shutil, sys
from pathlib import Path
H = Path(__file__).resolve().parents[4] / "horseshoe"; sys.path.insert(0, str(H))
import b15d_split as S
ME = Path(__file__).resolve().parent; BUILD = S.OUT / "kerr" / "build.json"
COV = json.loads(BUILD.read_text()); ALL = list(COV["required"]) + list(COV["optional"])
CERT_E = dict(b="0", orient="none", fb="1", cfb="1", extra=[S.CFP])

def tree(name, e_of, a_of):
    d = ME / name
    if d.exists(): shutil.rmtree(d)
    (d / "kerr").mkdir(parents=True); (d / "kerr_e").mkdir(); (d / "kerr_a").mkdir()
    shutil.copy(BUILD, d / "kerr" / "build.json")
    for c in ALL:
        e, a = e_of(c), a_of(c)
        if e is not None: (d / "kerr_e" / f"{c}.out").write_text("\n".join(e) + "\n")
        if a is not None: (d / "kerr_a" / f"{c}.out").write_text("\n".join(a) + "\n")
    S.OUT = d; return S.kerr_table()

res = []
k1 = tree("K1", lambda c: S._E(**CERT_E) if c == "N1N2" else S._E(), lambda c: None)
res.append(("K1 edge-fixed N1N2, no kerr_a", k1["early_chain"].startswith("CERTIFIED-FAIL") and k1["complete"] is False and "chain_class" not in k1, k1["early_chain"], k1["complete"]))
k2 = tree("K2", lambda c: S._E(), lambda c: S._A())
res.append(("K2 all CERTIFIED and complete", k2["complete"] is True and k2.get("chain_class") == "RHO>1" and all(r["final"] == "CERTIFIED" for r in k2["rows"].values()), k2.get("chain_class"), k2["complete"]))
k3 = tree("K3", lambda c: S._E(), lambda c: S._A(done=False) if c == "N3N4" else S._A())
res.append(("K3 kerr_a N3N4 unfinished", k3["complete"] is False and "chain_class" not in k3 and k3["rows"]["N3N4"]["final"] is None, k3.get("chain_class"), k3["complete"]))
ok = all(r[1] for r in res)
out = ["B15e A7 kerr_table known-answer branch check (fixtures from b15d_split's own canned cases; not an independent answer)"]
out += [f"{n}: {'PASS' if g else 'FAIL'} (got {x}, complete={y})" for n, g, x, y in res] + [f"ALL {'PASS' if ok else 'FAIL'}"]
(ME / "results.txt").write_text("\n".join(out) + "\n"); print("\n".join(out)); sys.exit(0 if ok else 1)
