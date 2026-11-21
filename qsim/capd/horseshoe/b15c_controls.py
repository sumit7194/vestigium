"""B15c controls scorer (registered: B15c §6 a126a6b + B15c-1 7ca093d). Non-counted. Runs the constructor-stage
controls 1, 2, 3 (constructor part), 4, 5, 6, 7 and 8, plus 2b (the diagnostic arm's copy equals the frozen function at
lam = 7.3). Writes horseshoe_results/kerr/b15c/controls.json and, only if every control PASSES, controls_PASS.json
(with the driver's sha256), which the counted constructor stage requires.

  b15c_controls.py            run the controls
  b15c_controls.py --seal     draw the T2 run list's planted positions (seeded; the seed and the label map stay in
                              gitignored qsim/scratch/b15c/; only the sha256 of the sealed file is printed for the record)
  b15c_controls.py --score-T2 after T2: read the seal and score the planted entries (control 3 in the run)

The rigorous-stage controls (gate GB and control 3's rigorous twin) are b15c_rigorous_controls.py, at the slot."""
import hashlib, json, random, secrets, sys, time
import numpy as np
import b15_steps34 as D
import hs_construct as H

RES = {}


def put(name, ok, **info):
    RES[name] = dict(PASS=bool(ok), **info)
    print("%-34s %s  %s" % (name, "PASS" if ok else "FAIL", json.dumps(info, default=str)[:300]), flush=True)


def c1_selection():
    rec = json.loads((D.KERR / "b15_kerr_rust.json").read_text()); cr = rec["step2"]["crossings"]
    acc = json.loads((D.KERR / "b15_g6_summary.json").read_text())["accepts"]
    T = D.tiers(cr, acc)
    ok1 = T["T1"] == [4155]
    # shuffled copy: permute the crossing list, select, map back
    rng = random.Random(1); perm = list(range(len(cr))); rng.shuffle(perm)        # new position k holds old perm[k]
    cr2 = [cr[i] for i in perm]; inv = {old: new for new, old in enumerate(perm)}
    acc2 = [dict(a, n=inv[a["n"]]) for a in acc]
    T2 = D.tiers(cr2, acc2)
    # NB the index tie-break is the last key; with distinct (|k|, angle) the choice cannot depend on the order
    ok2 = perm[T2["T1"][0]] == 4155
    toy = [dict(k_u=-3, k_s=-3, angle=0.02), dict(k_u=-2, k_s=-4, angle=0.03), dict(k_u=-5, k_s=-2, angle=0.5)]   # sum 7: loses on |k| despite the largest angle; tie (sum 6) between 0 and 1
    tacc = [dict(n=i, measured=True) for i in range(3)]
    ok3 = D.tiers(toy, tacc)["T1"] == [1]
    meas = {a["n"]: a["measured"] for a in acc}
    srt = sorted([i for i in meas], key=lambda i: D.b14_key(cr[i], i))
    ok4 = (T["T2"] == [i for i in srt if meas[i] and i != 4155] and T["T3"] == [i for i in srt if not meas[i]]
           and len(T["T2"]) == 80 and len(T["T3"]) == 66)
    put("1 selection", ok1 and ok2 and ok3 and ok4, T1=T["T1"], shuffled=ok2, tie=ok3, orders=ok4,
        nT2=len(T["T2"]), nT3=len(T["T3"]))


def c2_hh_positive():
    # exercise the map switch first: one Kerr call, then HH
    D.use_system("kerr"); _ = H.P(np.array([1.8411884397812655, 0.0]), 1)
    z, eu, es, c = D.hh_pi4()
    s3 = D.step3("hh", z, eu, es, c)
    ex = json.loads((D.RES / "construct" / "hh_chain_explore.json").read_text())
    dX = max(float(np.max(np.abs(np.array(s3["X"][j]) - np.array(ex["X"][j])))) for j in range(ex["m"] + 1))
    dU = max(float(np.max(np.abs(np.array(s3["U"][j]) - np.array(ex["U"][j])))) for j in range(ex["m"] + 1))
    dS = max(float(np.max(np.abs(np.array(s3["S"][j]) - np.array(ex["S"][j])))) for j in range(ex["m"] + 1))
    ok_xus = s3["m"] == ex["m"] and max(dX, dU, dS) <= 1e-12
    lad = D.ladder("hh", z, eu, es, s3["X"], s3["U"], s3["S"])
    a = lad["accepted"]
    ok_lad = bool(a) and (a["a0"], a["a"], a["bf0"], a["bf"], a["chain"]) == (0.03, 0.01, 0.5, 0.5, [3, 4, 5, 6])
    ok_sets = False
    if a:
        sets = D.exact_sets(z, eu, es, s3["X"], s3["U"], s3["S"], a)
        ref = json.loads((D.RES / "hh2_exact_checks.json").read_text())["sets"]
        mine = {k: [[str(x) for x in t] for t in v] for k, v in sets.items()}
        ok_sets = mine == ref
    put("2 HH-SECONDARY reproduced", ok_xus and ok_lad and ok_sets, m=s3["m"], dX=dX, dU=dU, dS=dS,
        ladder=(a and dict(a0=a["a0"], a=a["a"], bf0=a["bf0"], bf=a["bf"], chain=a["chain"])), sets_identical=ok_sets)
    return z, eu, es, c, s3


def c2b_arm_copy(z, eu, es, c):
    D.use_system("hh")
    ku, ks = abs(c["k_u"]), abs(c["k_s"]); su, ss = (int(np.sign(c["k_u"])) or 1), (int(np.sign(c["k_s"])) or 1)
    r0 = H.refine_connection(z, su * eu, z, ss * es, ku, ks, np.array(c["point"]))
    r1 = D.refine_connection_scaled(z, su * eu, z, ss * es, ku, ks, np.array(c["point"]), 7.3)
    same = r0 is not None and r1 is not None and r0["t"] == r1["t"] and r0["tau"] == r1["tau"] and \
        r0["residual"] == r1["residual"] and np.array_equal(r0["h"], r1["h"])
    put("2b arm copy == frozen at 7.3", same, t=(r0 or {}).get("t"), tau=(r0 or {}).get("tau"))


def c3_planted_constructor(z, eu, es, s3):
    lad = D.ladder("hh", z, eu, es, s3["X"], s3["U"], s3["S"], swap=True)
    put("3 planted HH U<->S: no ladder entry", lad["stop"] == "step 4: no ladder entry",
        stop=lad["stop"], entries_tried=len(lad["entries"]), max_n_ok=max([e["n_ok_required"] for e in lad["entries"]] or [0]))


class _Toy:
    """b15b_toyflow's standard map, with a counter of None returns"""
    def __init__(self, raise_at=None):
        import b15b_toyflow as TF
        self.f = TF.ToyFlow(); self.nones = 0; self.raise_at = raise_at
    def P(self, w, n=1, jac=False):
        if self.raise_at is not None:
            import kerr_compiled as KC
            raise KC.MapCheckFailed("HARNESS-ERROR: planted toy integration check failure")
        r = self.f.P(w, n, jac)
        if r is None: self.nones += 1
        return r
    def Pinv(self, w):
        return self.f.Pinv(w)


def c4_plunge():
    t = _Toy(); D._SYS["toy"] = (t.P, t.Pinv, lambda x, px: 1.0)
    z = np.zeros(2); eu = np.array([1.0, 0.0]); es = np.array([0.0, 1.0])
    X = [z, np.array([0.0, 3.0]), z]; U = [eu] * 3; S = [es] * 3              # N1 straddles the hole |y| > 3
    try:
        lad = D.ladder("toy", z, eu, es, X, U, S, stop_at_first=False)
        ran = True
    except Exception as e:                                                   # must not raise
        lad, ran = dict(stop="EXCEPTION %r" % e, entries=[]), False
    fails_with_none = any(v is None for e in lad["entries"] for v in e["detail"].values())
    put("4 plunge None -> covering FAILS", ran and t.nones > 0 and fails_with_none and lad["stop"] == "step 4: no ladder entry",
        nones=t.nones, entries=len(lad["entries"]), stop=lad["stop"])


def c5_mapcheckfailed():
    import kerr_compiled as KC
    t = _Toy(raise_at=0); D._SYS["toy"] = (t.P, t.Pinv, lambda x, px: 1.0); D._SYS["kerr_saved"] = D._SYS.get("kerr")
    D._SYS["kerr"] = D._SYS["toy"]
    ctx = dict(crossings=[dict(k_u=1, k_s=1, angle=0.5, point=[0.1, 0.1])], z=np.zeros(2), e_u=np.array([1.0, 0.0]),
               e_s=np.array([0.0, 1.0]))
    raised, recorded = False, None
    try:
        recorded = D.run_candidate(dict(id="toy", kind="kerr", n=0), ctx)
    except KC.MapCheckFailed:
        raised = True
    finally:
        D._SYS["kerr"] = D._SYS.pop("kerr_saved")
    # the constructor loop turns this exception into a HARNESS-ERROR stop (b15_steps34.constructor); here: it propagates
    # out of run_candidate, and no record (no rejection) was produced
    src = open(D.__file__).read()
    loop_ok = "except KC.MapCheckFailed as e:" in src and 'raise SystemExit("HARNESS-ERROR at' in src
    put("5 MapCheckFailed -> HARNESS-ERROR", raised and recorded is None and loop_ok, raised=raised, loop_handler=loop_ok)


def c6_s8():
    from fractions import Fraction as F
    sets = {"N0": ([F(0), F(0)], [F(1, 10), F(0)], [F(0), F(1, 10)]),
            "N1": ([F(1, 20), F(0)], [F(1, 10), F(0)], [F(0), F(1, 10)])}          # overlapping
    entry = dict(a0=0.03, a=0.01, bf0=0.5, bf=0.5, chain=[1])
    r = D.specs("kerr", sets, entry, "/nonexistent")
    sets_ok = {"N0": sets["N0"], "N1": ([F(1), F(0)], [F(1, 10), F(0)], [F(0), F(1, 10)])}
    r2 = D.specs("kerr", sets_ok, entry, "/tmp/x")
    put("6 S8 overlapping -> stop, no spec", r["stop"] == "S8" and "specs" not in r and r2["stop"] is None and len(r2["specs"]) == 4,
        stop=r["stop"], control_disjoint_specs=len(r2.get("specs", {})))


HH_N6N3 = ("COVER N6 N3 a=1 b=0 strong_a=0 orient=none fail_a=0 fail_b=0 certified_fail_b=0 orient_certified_fail=1 "
           "leaves_a=256 leaves_b=128 maxdepth_a=0 replay_steps=117427 return_time=[6.914823255981e+00,7.110912619906e+00] "
           "COVERS=0 chunk_a=[0,16) edges=yes reloaded_pieces=0")


def c7_classifier():
    ok_line = "COVER A B a=1 b=1 strong_a=0 orient=LR fail_a=0 fail_b=0 certified_fail_b=0 orient_certified_fail=0 COVERS=1"
    no_line = "COVER A B a=0 b=0 strong_a=0 orient=none fail_a=3 fail_b=0 certified_fail_b=0 orient_certified_fail=0 COVERS=0"
    fp_c = "FAILPIECE A>B b edge=R s=[0.1,0.2] CERTIFIED u=[2,3] w1=[0,1]"
    fp_u = "FAILPIECE A>B a depth=28(depth cap) u=[0,0.1] s=[0,0.1] exit"
    cases = [
        ("COVERS=1 + DONE", [ok_line, "DONE"], "CERTIFIED"),
        ("FAILPIECE CERTIFIED + DONE", [fp_c, no_line.replace("certified_fail_b=0", "certified_fail_b=1"), "DONE"], "CERTIFIED-FAIL"),
        ("cap/depth FAILPIECEs only + DONE", [fp_u, no_line, "DONE"], "UNDECIDED"),
        ("FATAL", ["FATAL replay steps exceeded"], "UNDECIDED"),
        ("no DONE", [no_line], "UNDECIDED"),
        ("COVERS=1 AND FAILPIECE CERTIFIED", [fp_c, ok_line, "DONE"], "HARNESS-ERROR"),
        ("uncertified FAILPIECEs only", [fp_u, fp_u, no_line, "DONE"], "UNDECIDED"),
        ("COVERS=1 without DONE", [ok_line], "UNDECIDED"),
        ("B15c-1: HH N6=>N3 verbatim + DONE", [HH_N6N3, "DONE"], "CERTIFIED-FAIL"),
        ("B15c-1: COVERS=1 + orient_certified_fail=1", [ok_line.replace("orient_certified_fail=0", "orient_certified_fail=1"), "DONE"], "HARNESS-ERROR"),
        ("B15c-1: COVERS=0 orient_cf=0 no FAILPIECE + DONE", [no_line, "DONE"], "UNDECIDED"),
    ]
    bad = [(n, D.classify(l), want) for n, l, want in cases if D.classify(l) != want]
    chain_ok = (D.chain_class(["CERTIFIED"] * 4) == "RHO>1" and D.chain_class(["CERTIFIED"] * 3 + ["UNDECIDED"]) == "UNDECIDED"
                and D.chain_class(["CERTIFIED", "CERTIFIED-FAIL", "UNDECIDED"]) == "CERTIFIED-FAIL")
    h_f7 = D.headline(dict(T1=["RHO>1"]))
    h_nt = D.headline(dict(T1=["step 3: refinement failed"], T2=["step 4: no ladder entry", "UNDECIDED", "S8"]))
    h_sup = D.headline(dict(T1=["CERTIFIED-FAIL"], T2=["UNDECIDED"]))
    head_ok = ("F7 STOP" in h_f7 and "NOT TESTED" in h_nt and "no rho" not in h_nt.lower() and "no ρ" not in h_nt
               and "supported by 1 chains" in h_sup)
    put("7 classifier + chain + headline", not bad and chain_ok and head_ok, n_cases=len(cases), mismatches=bad,
        chain=chain_ok, headline=head_ok)


def c8_duplicates():
    from fractions import Fraction as F
    sets = {"N0": ([F(0), F(0)], [F(1, 10), F(0)], [F(0), F(1, 10)]), "N1": ([F(1), F(0)], [F(1, 10), F(0)], [F(0), F(1, 10)])}
    entry = dict(a0=0.03, a=0.01, bf0=0.5, bf=0.5, chain=[1])
    w = D.write_specs([("c1", "kerr", sets, entry), ("c2", "kerr", dict(sets), dict(entry))], dry_run=True)
    put("8 duplicates", w["c1"]["status"] == "specs" and w["c2"]["status"] == "duplicate" and w["c2"]["of"] == "c1"
        and w["n_specs_written"] == 4, statuses={k: v for k, v in w.items() if k != "n_specs_written"}, n=w["n_specs_written"])


def run():
    t0 = time.time()
    D.kerr_setup(journal_name="b15c_controls.journal", plunges_name="b15c_controls_plunges.jsonl")
    c1_selection()
    z, eu, es, c, s3 = c2_hh_positive()
    c2b_arm_copy(z, eu, es, c)
    c3_planted_constructor(z, eu, es, s3)
    c4_plunge(); c5_mapcheckfailed(); c6_s8(); c7_classifier(); c8_duplicates()
    verdict = "PASS" if all(v["PASS"] for v in RES.values()) else "FAIL"
    out = dict(controls=RES, verdict=verdict, driver_sha256=D.file_sha(D.__file__), controls_sha256=D.file_sha(__file__),
               seconds=round(time.time() - t0, 1))
    (D.OUT / "controls.json").write_text(json.dumps(out, indent=1, default=str))
    if verdict == "PASS":
        (D.OUT / "controls_PASS.json").write_text(json.dumps(out, indent=1, default=str))
    print("CONTROLS", verdict, flush=True)


def seal():
    rec = json.loads((D.KERR / "b15_kerr_rust.json").read_text()); cr = rec["step2"]["crossings"]
    acc = json.loads((D.KERR / "b15_g6_summary.json").read_text())["accepts"]
    T = D.tiers(cr, acc)
    D.SEAL_DIR.mkdir(parents=True, exist_ok=True)
    path = D.SEAL_DIR / "T2_runlist.json"
    if path.exists():
        raise SystemExit("REFUSED: already sealed (%s)" % path)
    seed = secrets.randbits(64); rng = random.Random(seed)
    items = [dict(kind="kerr", n=n) for n in T["T2"]]
    for kind in ("hh_swap", "kerr_t1_swap"):
        items.insert(rng.randrange(len(items) + 1), dict(kind=kind))
    ids = list(range(len(items))); rng.shuffle(ids)                        # opaque ids
    for it, i in zip(items, ids): it["id"] = "T2-%03d" % i
    labels = {it["id"]: it["kind"] for it in items if it["kind"] != "kerr"}
    path.write_text(json.dumps(items, indent=1))
    (D.SEAL_DIR / "T2_seal_labels.json").write_text(json.dumps(dict(seed=seed, labels=labels), indent=1))
    print("sealed: T2_runlist.json sha256", D.file_sha(path), "; labels sha256", D.file_sha(D.SEAL_DIR / "T2_seal_labels.json"))


def score_t2():
    lab = json.loads((D.SEAL_DIR / "T2_seal_labels.json").read_text())["labels"]
    t2 = {r["id"]: r for r in json.loads((D.OUT / "T2.json").read_text())["records"]}
    for i, kind in lab.items():
        r = t2.get(i)
        print(kind, i, r and r.get("stop"))
    hh = [i for i, k in lab.items() if k == "hh_swap"][0]
    ok = t2.get(hh, {}).get("stop") == "step 4: no ladder entry"
    print("CONTROL 3 (in T2, deciding: hh_swap):", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    {"--seal": seal, "--score-T2": score_t2}.get(sys.argv[1] if len(sys.argv) > 1 else "", run)()
