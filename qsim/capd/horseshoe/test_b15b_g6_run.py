"""END-TO-END test of the G6 driver (b15b_g6_run.py) BEFORE it sees a counted run (the Bridge: "a wrapper that never flags
is indistinguishable from a broken one"). The real b15_kerr_ck.py is run with B15_MAP=toy (b15b_toyflow.py, the standard
map with a hole) so the journal, JSON and arcs have exactly the counted run's formats; then:
  T1  the driver is COMPLETE on it: replica bit-identical, D1 / D4 / D6 / D7 counts equal the run's;
  T2  it flags: the run's near-tangent crossings (angles ~1e-12) must be thin (D4 / D6) and go to the 1e-14 recompute;
  T3  the hole produces drops, and chords are identified;
  T4  NEGATIVE: one saved arc point changed by 1 ulp -> INCOMPLETE (replica not bit-identical), D8 never CONNECTION;
  T5  NEGATIVE: one journal entry removed -> INCOMPLETE.
Run: python test_b15b_g6_run.py  (after B15_MAP=toy python b15_kerr_ck.py)"""
import json, sys
from pathlib import Path
import numpy as np
import pcache, b15b_g6_run as GR, b15b_toyflow
D = GR.OUT / "b15_wiring_test"
ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print("%-70s %s" % (name, "ok" if cond else "FAIL"))
run = json.loads((D / "toy.json").read_text()); mem = dict(pcache.Journal(str(D / "toy.journal")).mem)
arcs = dict(np.load(D / "toy_arcs.npz")); model = GR.error_model(GR.OUT / "b15b_gates")
R = GR.Run(run, mem, dict(arcs), [], model, b15b_toyflow.ToyFlow()); rep = GR.g6(R)
(D / "toy_g6.json").write_text(json.dumps(rep, indent=1, default=float))
c = rep["counts"]
check("T1 complete", rep["complete"])
check("T1 replica bit-identical, 0 journal misses", c["replica_bit_identical"] and c["journal_misses"] == 0)
check("T1 D4 count = the run's (%d)" % c["run_crossings"], c["D4_crossings"] == c["run_crossings"])
check("T1 D6 / D7 counts = the run's", c["D6_accepts"] == c["run_D6"] and c["D7_red"] == c["run_D7"])
cr = rep["decisions"]["crossings"]; tiny = [x for x in cr if x["angle"] < 1e-6]
check("T2 the near-tangent crossings (%d) are thin" % len(tiny), tiny and all(x["D4"]["thin"] or x["D6"]["thin"] or x["vertex"]["zero_count_risk"] for x in tiny))
check("T2 every thin crossing went to the 1e-14 recompute", all("recompute_1e-14" in x for x in cr if x["D4"]["thin"] or x["D6"]["thin"] or x["D7"]["thin"] or x["vertex"]["zero_count_risk"] or x["D5_thin"]))
nm = rep["decisions"]["near_misses"]
check("T2 every near-miss that could reach min(0.01, 10 theta) was recomputed (%d of %d)" % (sum(x["could_flag"] for x in nm), len(nm)),
      all("recompute_1e-14" in x for x in nm if x["could_flag"]) and all(x["threshold"] <= 0.01 for x in nm))
import b15b_g6 as G
nd = sum(1 for k, v in mem.items() if v is None)
check("T3 the hole produced None results (%d)" % nd, nd > 0)
check("T3 drops recorded (%d / %d) and chord segments found (%d)" % (c["drops_u"], c["drops_s"], c["chord_segments"]), c["drops_u"] + c["drops_s"] > 0 and c["chord_segments"] > 0)
print("   verdict:", rep["verdict"][:120], "| D8:", rep["decisions"]["D8"]["outcome"])
# T4: 1-ulp corruption of one saved arc point
bad = dict(arcs); kk = sorted(bad)[len(bad) // 2]; A = bad[kk].copy(); A[len(A) // 2, 0] = np.nextafter(A[len(A) // 2, 0], np.inf); bad[kk] = A
rep4 = GR.g6(GR.Run(run, mem, bad, [], model, b15b_toyflow.ToyFlow()))
check("T4 a 1-ulp arc change -> INCOMPLETE", not rep4["complete"] and rep4["verdict"] == "INCOMPLETE")
check("T4 ... and D8 is not CONNECTION", rep4["decisions"].get("D8", {}).get("outcome") != "CONNECTION")
# T5: a journal entry removed (a P call of the manifold stage)
mem5 = dict(mem); drop = [k for k in mem5 if k[0] == "P" and not dict(k[2]).get("jac")][100]; del mem5[drop]
rep5 = GR.g6(GR.Run(run, mem5, dict(arcs), [], model, b15b_toyflow.ToyFlow()))
check("T5 a missing journal entry -> INCOMPLETE", not rep5["complete"])
print("G6 DRIVER TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
