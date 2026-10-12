"""Resume of MN eq 0 primary (bridge scheduling suggestion, recorded in MR_REPLAY.md): the old per-loop layout made
each process compute ALL loops, so ONE process's output is a complete row. The three processes were stopped after 34/54
segments each; this re-runs PROCESS 1's EXACT input (old layout; its sha256 reproduces the checkpoint name, verified),
which reloads its 34 checkpointed segments and computes the remaining ones for all loops. The combine then takes every
loop from that single output (bit-identical copies, determinism check) with the same CAPD combine and finish_row."""
import hashlib, json, subprocess, sys, time
sys.path.insert(0, '.'); import mr_replay as R
R.PREC = 128
F, b = R.fields_bridge(R.bridge_json_for('mneq', 0)); G = R.prune_exps(F); cert = R.cert_for('mneq', 0)
tag = "mneq_0_primary_o30_p128_cg3"
src, coef = R.gen_header_local(G, tag)
assert src == open(R.GEN / f"{tag}.h").read()
exe = R.GEN / ("replay_" + tag)
base = R.build_input(coef, cert, order=30, tol=1e-25).replace("\nORDER", "\nSUBSEG 32\nORDER", 1)
names = sorted(set(cert['g'].split('*') + cert['h'].split('*')))
n = names[0]; safe = n.replace("[", "_").replace("]", "_").replace(",", "_")
inp = base.replace("END\n", "") + "ONLY %s\nNOCERT\nEND\n" % n          # process 1's exact (old-layout) input
ck = R.GEN / f"{tag}.{safe}.{hashlib.sha256(inp.encode()).hexdigest()[:16]}.ckpt"
assert ck.exists(), "checkpoint must exist (hash reproduces)"
inp = inp.replace("\nTOL ", "\nCKPT %s\nTOL " % ck, 1)
t0 = time.time()
with open(R.GEN / f"{tag}.resume.err", "w") as ef:
    r = subprocess.run([str(exe)], input=inp, stdout=subprocess.PIPE, stderr=ef, text=True)
(R.GEN / f"{tag}.resume.out").write_text(r.stdout)
assert r.returncode == 0 and "VERDICT LOOPS_ONLY" in r.stdout, "resume run failed"
ent = {}
for ln in r.stdout.splitlines():
    p = ln.split()
    if p and p[0] == "LOOP": ent.setdefault(p[1], {})[p[2]] = (p[3], p[4])
assert set(ent) == set(names), "single output must contain every loop"
comb = [l for l in base.splitlines() if l.split()[:1] in (["PREC"], ["ORDER"], ["TOL"])]
for i, c in enumerate(coef):
    lo, hi = R.enclose(c); comb.append("PAR %d %s %s" % (i, lo, hi))
for nm in names:
    e = ent[nm]; vals = []
    for i in range(2):
        for j in range(2): vals += [*e[f"M{i}{j}re"], *e[f"M{i}{j}im"]]
    comb.append("MAT %s %s" % (nm, " ".join(vals)))
comb += ["WORD g %s" % cert["g"], "WORD h %s" % cert["h"], "END"]
with open(R.GEN / (tag + ".err"), "w") as ef:
    rc = subprocess.run([str(exe)], input="\n".join(comb) + "\n", stdout=subprocess.PIPE, stderr=ef, text=True)
rc.stderr = (R.GEN / (tag + ".err")).read_text(); (R.GEN / (tag + ".out")).write_text(rc.stdout)
a5 = {l.split()[0]: l.split()[1] for l in r.stdout.splitlines() if l.startswith("A5_")}
res, _ = R.finish_row(dict(tag=tag, family="mneq", row=0, label="primary", layout="resume of process 1 (old layout, all loops)",
                           seconds_resume=round(time.time() - t0, 1), rc=rc.returncode, a5=a5, prec=128, tol=1e-25, codegen=3, subseg=32),
                      rc, cert, "mneq", 0, "primary")
json.dump(res, open(R.HERE / "replay_results" / (tag + ".json"), "w"), indent=1, default=str)
print(json.dumps({k: res.get(k) for k in ("verdict", "consistency", "a5", "seconds_resume", "max_width_tr_comm")}, default=str))
