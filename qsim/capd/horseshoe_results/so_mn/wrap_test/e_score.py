"""e_score.py: the offline scorer for the E-representation candidates (qsim/capd/horseshoe/E_REPRESENTATION_DESIGN.md).
Post-processing of the wrapping test's dumps only: no CAPD, no run. It is an ESTIMATE in float64, not an enclosure.
Widths are taken from the dumped intervals; centres are carried as floats.
Usage: e_score.py <chain> <segment ids...>   -> escore_<chain>.txt

Candidates, as the design states them:
  Z0 / Z0sym   the unreduced zonotope with the injections as dumped (control: Z0 must equal W_lin from result_<chain>.txt).
  Z1 / Z1sym   the same with the dDe feedback bound: S'_k = P0 + P1 + P2 + lambda_k * DDE_k, where lambda_k is the smallest
               factor with hull(Z_{k-1}) inside lambda_k * (B_{k-1} re_{k-1}), taking the max over components.
  ZR(Nmax,Nkeep) in Z1 mode: oldest-first merge into an SVD frame when N > Nmax.
  S            the adjoint slabs = W_lin (design section 2); no separate replay. Its numbers are the "B17 with W_lin" lines.
Controls:
  C1 (float, loose): replaying re_k = (iB_k D_k B_{k-1}) re_{k-1} + iB_k S_k with |.| sums gives widths >= the dumped
     re_k widths and within a factor 1.01. The QR/Krawczyk path is not replayed bitwise, so this checks only the reading.
  C2: Z0 = W_lin (relative 1e-6) for every covector at every checkpoint.
  C3: lambda_k <= 1 at every step (in Z0 and Z1).
  C4: every ZR width >= the matching Z1 width."""
import sys, time, re as _re
from pathlib import Path
import numpy as np
W = Path(__file__).resolve().parent
sys.path.insert(0, str(W))
import wrap_adjoint as WA                       # read_state, read_cpfile (thresholds), FT, CPD

NAMES = ["u1", "u2", "nH", "off0", "off1", "off2", "off3"]
fh = float.fromhex
def iv(tok): a = np.array([fh(x) for x in tok]); return a[0::2], a[1::2]     # (lo, hi)

def read_dump(p):
    recs, cps, cur = [], [], None
    for line in p.read_text().splitlines():
        t = line.split(); k = t[0]
        if k == "STEP": lo, hi = iv(t[2:4]); cur = dict(step=int(t[1]), t=(lo[0] + hi[0]) / 2)
        elif k in ("D1c", "B"): lo, hi = iv(t[1:]); cur[k] = ((lo + hi) / 2).reshape(8, 8)
        elif k in ("S", "P0", "P1", "P2", "DDE", "RE"): cur[k] = iv(t[1:])
        elif k == "END": recs.append(cur)
        elif k == "CPROJ":
            lo, hi = iv(t[4:]); cps.append(dict(step=recs[-1]["step"], name=t[1], u=(lo + hi) / 2))
    return recs, cps

def ivsum(*ps): return sum(p[0] for p in ps), sum(p[1] for p in ps)

def main():
    chain, sids = sys.argv[1], sys.argv[2:]
    rows = {l.split("\t")[0]: l.split("\t") for l in (W / "segments.tsv").read_text().splitlines() if l and not l.startswith("#")}
    st0 = WA.read_state(WA.FT / rows[sids[0]][3])
    B0 = np.array([[float(WA.mid(e)) for e in r] for r in st0["B"]])
    re0 = (np.array([float(e[0]) for e in st0["re"]]), np.array([float(e[1]) for e in st0["re"]]))
    recs, cps = [], []
    for s in sids:
        if (W / "runs" / s / "CHECK.txt").read_text().splitlines()[0] != "IDENTICAL": raise SystemExit("segment %s not IDENTICAL" % s)
        r, c = read_dump(W / "runs" / s / "dump"); recs += r; cps += c
    steps = [r["step"] for r in recs]
    if steps != list(range(steps[0], steps[0] + len(steps))) or steps[0] != st0["steps"] + 1: raise SystemExit("HARNESS-ERROR: steps")
    cpf = WA.read_cpfile(WA.CPD / rows[sids[0]][2])
    out = []; pr = out.append
    pr("E-REPRESENTATION SCORES, chain %s (%s), window steps %d..%d (%d steps). float64 ESTIMATES from the dumps; not enclosures."
       % (chain, " ".join(sids), steps[0], steps[-1], len(steps)))

    # the run's box hull e_k = B_k re_k (interval product, B thin) and its re-width check (C1)
    def boxhull(B, re):
        m, r = (re[0] + re[1]) / 2, (re[1] - re[0]) / 2
        c = B @ m; d = np.abs(B) @ r; return c - d, c + d
    hulls = [boxhull(B0, re0)] + [boxhull(r["B"], r["RE"]) for r in recs]
    c1 = []
    prevB, prevre = B0, re0
    for r in recs:
        iB = np.linalg.inv(r["B"]); M = iB @ r["D1c"] @ prevB
        rr = (prevre[1] - prevre[0]) / 2; sr = (r["S"][1] - r["S"][0]) / 2
        pred = np.abs(M) @ rr + np.abs(iB) @ sr; got = (r["RE"][1] - r["RE"][0]) / 2
        c1.append(np.max(pred / np.maximum(got, 1e-300))); prevB, prevre = r["B"], r["RE"]
    c1 = np.array(c1)
    pr("C1 (reading check, float): predicted/dumped re radius, max over components: min %.6f median %.6f max %.6f -> %s"
       % (c1.min(), np.median(c1), c1.max(), "OK" if c1.min() > 0.999999 and c1.max() < 1.01 else "CHECK"))

    cpsteps = sorted({c["step"] for c in cps}); idx = {s: i for i, s in enumerate(steps)}
    Wlin_ref = {}
    rf = W / ("result_%s.txt" % chain)
    if rf.exists():
        cur = None
        for l in rf.read_text().splitlines():
            m = _re.match(r"== checkpoint t = ([\d.]+) \(step (\d+)\)", l)
            if m: cur = int(m.group(2))
            m = _re.match(r"\s+(\S+)\s+W_tot (\S+) = P (\S+) \+ W_box (\S+) \| W_lin (\S+)", l)
            if m and cur: Wlin_ref[(cur, m.group(1))] = dict(Wtot=float(m.group(2)), P=float(m.group(3)), Wbox=float(m.group(4)), Wlin=float(m.group(5)))

    def replay(sym, feedback, red=None):
        t0 = time.time()
        if sym: c = np.zeros(8); G = B0 * np.maximum(np.abs(re0[0]), np.abs(re0[1]))
        else: c = B0 @ ((re0[0] + re0[1]) / 2); G = B0 * ((re0[1] - re0[0]) / 2)
        lam, nred, res, Nmax_seen = [], 0, {}, 0
        for k, r in enumerate(recs):
            hl = np.abs(G).sum(1); h_lo, h_hi = c - hl, c + hl
            e_lo, e_hi = hulls[k]
            lk = max(np.max(np.maximum(h_hi, 0) / e_hi), np.max(np.maximum(-h_lo, 0) / (-e_lo)))
            lam.append(lk)
            if feedback: S = ivsum(r["P0"], r["P1"], r["P2"], (lk * r["DDE"][0], lk * r["DDE"][1]))
            else: S = r["S"]
            if sym: mu = np.zeros(8); rho = np.maximum(np.abs(S[0]), np.abs(S[1]))
            else: mu = (S[0] + S[1]) / 2; rho = (S[1] - S[0]) / 2
            c = r["D1c"] @ c + mu; G = np.hstack([r["D1c"] @ G, np.diag(rho)])
            if red and G.shape[1] > red[0]:
                nR = G.shape[1] - red[1] + 8; GR = G[:, :nR]
                U = np.linalg.svd(GR, full_matrices=True)[0]; d = np.abs(U.T @ GR).sum(1) * (1 + 1e-12)
                G = np.hstack([U * d, G[:, nR:]]); nred += 1
            Nmax_seen = max(Nmax_seen, G.shape[1])
            if r["step"] in cpsteps:
                for cp in [x for x in cps if x["step"] == r["step"]]:
                    res[(r["step"], cp["name"])] = 2 * np.abs(cp["u"] @ G).sum()
        return dict(res=res, lam=np.array(lam), nred=nred, N=Nmax_seen, sec=time.time() - t0)

    modes = [("Z0", False, False, None), ("Z0sym", True, False, None), ("Z1", False, True, None), ("Z1sym", True, True, None),
             ("ZR(64,32)", False, True, (64, 32)), ("ZR(256,128)", False, True, (256, 128)), ("ZR(1024,512)", False, True, (1024, 512))]
    R = {}
    for name, sym, fb, red in modes:
        R[name] = replay(sym, fb, red); x = R[name]
        pr("%-12s replay %.1f s, N max %d, reductions %d; lambda_k min %.4f median %.4f max %.4f%s" % (
            name, x["sec"], x["N"], x["nred"], x["lam"].min(), np.median(x["lam"]), x["lam"].max(),
            "" if x["lam"].max() <= 1 + 1e-9 else "   C3 FAIL (lambda > 1)"))
    for cs in cpsteps:
        T = recs[idx[cs]]; tT = T["t"]
        cp = [c for c in cpf if c["kind"] == "t" and abs(c["t"] - tT) < 1e-6][0]; g = cp["g"]
        pr(""); pr("== checkpoint t = %.10f (step %d); thresholds: u1 %.3e, u2 %.3e, fake %.3e (K = 5); lambda at T: %s" % (
            tT, cs, 5 * cp["tu1"], 5 * cp["tu2"], 5 * cp["tu2"] * g[1], "  ".join("%s %.4f" % (n, R[n]["lam"][idx[cs]]) for n in ("Z0", "Z1"))))
        pr("  %-5s %11s %11s | %s" % ("cov", "W_box", "W_lin", "  ".join("%-12s" % n for n, *_ in modes)))
        for nm in NAMES:
            ref = Wlin_ref.get((cs, nm))
            pr("  %-5s %11.4e %11.4e | %s" % (nm, ref["Wbox"] if ref else float("nan"), ref["Wlin"] if ref else float("nan"),
                                              "  ".join("%-12.4e" % R[n]["res"][(cs, nm)] for n, *_ in modes)))
        if all((cs, nm) in Wlin_ref for nm in NAMES):
            c2 = max(abs(R["Z0"]["res"][(cs, nm)] / Wlin_ref[(cs, nm)]["Wlin"] - 1) for nm in NAMES)
            pr("  C2: max |Z0/W_lin - 1| = %.2e -> %s" % (c2, "OK" if c2 < 1e-3 else "FAIL"))
            c4 = min(R[n]["res"][(cs, nm)] / R["Z1"]["res"][(cs, nm)] for n, *_ in modes if n.startswith("ZR") for nm in NAMES)
            pr("  C4: min ZR/Z1 = %.6f -> %s" % (c4, "OK" if c4 >= 1 - 1e-9 else "FAIL"))
            for n, *_ in modes:
                v = {nm: Wlin_ref[(cs, nm)]["P"] + R[n]["res"][(cs, nm)] for nm in NAMES}
                fake = sum(v[nm] * g[2 + q] for q, nm in enumerate(["nH", "off0", "off1", "off2", "off3"]))
                r1, r2, rf_ = v["u1"] / cp["tu1"], v["u2"] / cp["tu2"], fake / (cp["tu2"] * g[1])
                pr("  B17 with %-12s u1 %.3f  u2 %.3f  fake ratio %.3f -> %s   (u2: W/W_box %.4f, W/W_lin %.3f)" % (
                    n, r1, r2, rf_, "PASS" if max(r1, r2, rf_) <= 5 else "FAIL",
                    R[n]["res"][(cs, "u2")] / Wlin_ref[(cs, "u2")]["Wbox"], R[n]["res"][(cs, "u2")] / Wlin_ref[(cs, "u2")]["Wlin"]))
    # the injection split on u2 at the last checkpoint, Z1: P2 vs lambda*DDE (adjoint-weighted)
    cs = cpsteps[-1]; u = [c for c in cps if c["step"] == cs and c["name"] == "u2"][0]["u"]; w = u.copy()
    parts = dict(P2=0.0, DDE_run=0.0, DDE_Z1=0.0)
    for k in range(idx[cs], -1, -1):
        r = recs[k]; aw = np.abs(w)
        parts["P2"] += aw @ (r["P2"][1] - r["P2"][0]); d = aw @ (r["DDE"][1] - r["DDE"][0])
        parts["DDE_run"] += d; parts["DDE_Z1"] += R["Z1"]["lam"][k] * d; w = r["D1c"].T @ w
    pr(""); pr("u2 injections at step %d (adjoint-weighted widths): P2 %.3e | DDE as run %.3e | DDE under Z1 %.3e" % (cs, parts["P2"], parts["DDE_run"], parts["DDE_Z1"]))
    txt = "\n".join(out) + "\n"; (W / ("escore_%s.txt" % chain)).write_text(txt); print(txt)

if __name__ == "__main__":
    main()
