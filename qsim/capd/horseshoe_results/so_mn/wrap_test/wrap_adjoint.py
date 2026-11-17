"""Wrapping test (WRAPPING_TEST.md): the analysis. Pure post-processing of the segment dumps; no CAPD.
Usage: wrap_adjoint.py <chain name> <segment id> [<segment id> ...]   -> result_<chain>.txt (and printed)
For every checkpoint met in the chain and every checkpoint covector u (u1, u2, nH, off0..off3):
  W_tot  = width of the run's own projection <u, X> (the CPROJ interval; equals the run's PROJ/CHECKPOINT width);
  W_box  = sum_j |<u, B_T e_j>| w(re_T,j): the error part of that projection, as the run's box representation holds it;
  P      = W_tot - W_box: the polynomial part (and the centre), unaffected by how E is represented;
  W_lin  = the u-width of the WRAPPING-FREE linear image of the same error sources over the chain's window:
           e_k = D_k e_{k-1} + s_k  (D_k = mid of the run's centre variational matrix D1c, s_k = the box the run itself
           injected at step k), e_0 = B_0 re_0 (the start state's parallelepiped, carried exactly). By the adjoint
           w_T = u, w_{k-1} = D_k^T w_k:   W_lin = sum_k sum_i |w_k,i| w(s_k,i) + sum_j |<w_0, B_0 e_j>| w(re_0,j).
           W_lin is what a representation with NO wrapping (an unreduced zonotope) would hold for the same injections.
  F      = W_box / W_lin  (>= 1 up to rounding; F < 1 - 1e-6 is a HARNESS-ERROR).
  the B17 test re-evaluated with W_lin in place of W_box (P + W_lin), against the same thresholds (K = 5).
Also: per-column table of the box at T (|<u, B_j>| w(re_j)), and the split of W_lin into the start parallelepiped and the
injections (by part p0/p1/p2/dDe, and by time bin of 0.25)."""
import sys, re
from pathlib import Path
import mpmath as mp
mp.mp.prec = 256
W = Path(__file__).resolve().parent; FT = W.parent / "fix_test"; CPD = W.parent.parent / "mn_smoke"
K = 5

def hx(s):                                      # MPFR %Ra -> exact mpf
    neg = s.startswith("-"); s = s.lstrip("-")
    if s in ("0", "0x0p+0"): return mp.mpf(0)
    m = re.fullmatch(r"0x([0-9a-f]+)(?:\.([0-9a-f]*))?p([+-]\d+)", s)
    if not m: raise ValueError("bad MPFR hex: " + s)
    a, b, e = m.group(1), m.group(2) or "", int(m.group(3))
    v = mp.ldexp(mp.mpf(int(a + b, 16)), e - 4 * len(b)); return -v if neg else v
def ivs(tok):                                   # list of hex tokens -> list of (lo, hi)
    return [(hx(tok[2 * i]), hx(tok[2 * i + 1])) for i in range(len(tok) // 2)]
mid = lambda iv: (iv[0] + iv[1]) / 2
wid = lambda iv: iv[1] - iv[0]

def read_state(p):                              # mn_so save(): steps next_cp t LAST_H / x / C / H / B / re / END
    L = p.read_text().split("\n")
    B = ivs(L[4].split()); re_ = ivs(L[5].split())
    return dict(steps=int(L[0].split()[0]), t=mid(ivs(L[0].split()[2:4])[0]), B=[[B[8 * i + j] for j in range(8)] for i in range(8)], re=re_,
                Bhex=L[4].split(), rehex=L[5].split())

def read_dump(p):
    recs, cps, cur = [], [], None
    for line in p.read_text().splitlines():
        tok = line.split()
        if tok[0] == "STEP": cur = dict(step=int(tok[1]), t=mid(ivs(tok[2:4])[0]))
        elif tok[0] in ("D1c", "B"): v = ivs(tok[1:]); cur[tok[0]] = [[v[8 * i + j] for j in range(8)] for i in range(8)]; cur[tok[0] + "hex"] = tok[1:]
        elif tok[0] in ("S", "P0", "P1", "P2", "DDE", "RE"): cur[tok[0]] = ivs(tok[1:]); cur[tok[0] + "hex"] = tok[1:]
        elif tok[0] == "END": recs.append(cur)
        elif tok[0] == "CPROJ":
            cps.append(dict(step=recs[-1]["step"], name=tok[1], proj=ivs(tok[2:4])[0], u=[mid(v) for v in ivs(tok[4:])]))
    return recs, cps

def read_cpfile(p):
    tok = p.read_text().split(); out = []; i = 0
    while i < len(tok):
        kind, t = tok[i], float(tok[i + 1]); i += 2; v = [float(x) for x in tok[i:i + 24]]; i += 24
        tu1, tu2 = float(tok[i]), float(tok[i + 1]); i += 2; g = [float(x) for x in tok[i:i + 7]]; i += 7 + 4
        out.append(dict(kind=kind, t=t, tu1=tu1, tu2=tu2, g=g))
    return out

def main():
    chain, sids = sys.argv[1], sys.argv[2:]
    rows = {l.split("\t")[0]: l.split("\t") for l in (W / "segments.tsv").read_text().splitlines() if l and not l.startswith("#")}
    out = []; pr = lambda s="": out.append(s)
    for s in sids:
        chk = (W / "runs" / s / "CHECK.txt").read_text().splitlines()[0]
        if chk != "IDENTICAL": raise SystemExit("segment %s is not IDENTICAL (%s): no analysis" % (s, chk))
    st0 = read_state(FT / rows[sids[0]][3]); recs, cps = [], []
    for n, s in enumerate(sids):
        r, c = read_dump(W / "runs" / s / "dump")
        if n > 0:                                                  # the chain joins exactly at the original grid saves
            sst = read_state(FT / rows[s][3])
            if recs[-1]["Bhex"] != sst["Bhex"] or recs[-1]["REhex"] != sst["rehex"] or recs[-1]["step"] != sst["steps"]:
                raise SystemExit("HARNESS-ERROR: chain break between %s and %s" % (sids[n - 1], s))
        recs += r; cps += c
    if recs[0]["step"] != st0["steps"] + 1 or [x["step"] for x in recs] != list(range(recs[0]["step"], recs[0]["step"] + len(recs))):
        raise SystemExit("HARNESS-ERROR: steps not consecutive")
    cpf = read_cpfile(CPD / rows[sids[0]][2])
    d1w = max(wid(e) / max(abs(mid(e)), mp.mpf(10) ** -300) for r in recs for row in r["D1c"] for e in row if mid(e) != 0)
    bw = max(wid(e) for r in recs for row in r["B"] for e in row)
    pr("WRAPPING TEST analysis, chain %s: segments %s; window t %.6f -> %.6f, steps %d..%d (%d)" % (
        chain, " ".join(sids), float(st0["t"]), float(recs[-1]["t"]), recs[0]["step"], recs[-1]["step"], len(recs)))
    pr("  max relative width of D1c entries over the window: %.3e (the transport uses mid(D1c)); max width of any B entry: %.3e" % (d1w, bw))
    names = ["u1", "u2", "nH", "off0", "off1", "off2", "off3"]
    for cstep in sorted({c["step"] for c in cps}):
        m = [i for i, r in enumerate(recs) if r["step"] == cstep][0]; T = recs[m]; tT = float(T["t"])
        cp = [c for c in cpf if c["kind"] == "t" and abs(c["t"] - tT) < 1e-6][0]
        pr(); pr("== checkpoint t = %.10f (step %d); thresholds: u1 %.3e, u2 %.3e, fake %.3e (K = %d)" % (tT, cstep, K * cp["tu1"], K * cp["tu2"], K * cp["tu2"] * cp["g"][1], K))
        res = {}
        for nm in names:
            c = [c for c in cps if c["step"] == cstep and c["name"] == nm][0]; u = c["u"]
            Wtot = wid(c["proj"])
            cols = [abs(mp.fsum(u[i] * mid(T["B"][i][j]) for i in range(8))) * wid(T["RE"][j]) for j in range(8)]
            Wbox = mp.fsum(cols); P = Wtot - Wbox
            w = list(u); inj = mp.mpf(0); parts = {k: mp.mpf(0) for k in ("P0", "P1", "P2", "DDE")}; bins = {}
            for k in range(m, -1, -1):
                r = recs[k]; ck = mp.fsum(abs(w[i]) * wid(r["S"][i]) for i in range(8)); inj += ck
                for p in parts: parts[p] += mp.fsum(abs(w[i]) * wid(r[p][i]) for i in range(8))
                b = float(mp.floor(r["t"] * 4) / 4); bins[b] = bins.get(b, 0) + ck
                w = [mp.fsum(mid(r["D1c"][i][j]) * w[i] for i in range(8)) for j in range(8)]     # w_{k-1} = D_k^T w_k
            init = mp.fsum(abs(mp.fsum(w[i] * mid(st0["B"][i][j]) for i in range(8))) * wid(st0["re"][j]) for j in range(8))
            Wlin = init + inj; F = Wbox / Wlin if Wlin > 0 else mp.inf
            res[nm] = dict(Wtot=Wtot, Wbox=Wbox, P=P, Wlin=Wlin, F=F, init=init, inj=inj, parts=parts, bins=bins, cols=cols)
            pr("  %-4s W_tot %.4e = P %.4e + W_box %.4e | W_lin %.4e (start E %.3e + injections %.3e) | F = W_box/W_lin = %.4g%s" % (
                nm, Wtot, P, Wbox, Wlin, init, inj, F, "   HARNESS-ERROR (F < 1)" if F < 1 - mp.mpf("1e-6") else ""))
        g = cp["g"]
        def b17(key):
            v = {nm: res[nm]["P"] + res[nm][key] for nm in names}
            fake = sum(v[nm] * g[2 + q] for q, nm in enumerate(["nH", "off0", "off1", "off2", "off3"]))
            r1, r2, rf = v["u1"] / cp["tu1"], v["u2"] / cp["tu2"], fake / (cp["tu2"] * g[1])
            return "u1 %.3f  u2 %.3f  fake %.3e vs %.3e (ratio %.3f)  -> %s" % (r1, r2, fake, K * cp["tu2"] * g[1], rf, "PASS" if max(r1, r2, rf) <= K else "FAIL")
        pr("  B17 with the run's box (W_box):         " + b17("Wbox"))
        pr("  B17 with the wrapping-free bound (W_lin): " + b17("Wlin"))
        r = res["u2"]
        pr("  u2 detail: per-column box contributions at T (|<u2, B_j>| w(re_j), largest first):")
        for j in sorted(range(8), key=lambda j: -r["cols"][j]): pr("    col %d  %.4e  (%.1f%%)" % (j, r["cols"][j], 100 * r["cols"][j] / r["Wbox"] if r["Wbox"] > 0 else 0))
        pr("  u2 detail: W_lin injections by part (each part's own width; their sum >= the total's): " + "  ".join("%s %.3e" % (k, v) for k, v in r["parts"].items()))
        pr("  u2 detail: W_lin injections by time bin: " + "  ".join("%.2f: %.3e" % (b, v) for b, v in sorted(r["bins"].items())))
    txt = "\n".join(out) + "\n"; (W / ("result_%s.txt" % chain)).write_text(txt); print(txt)

if __name__ == "__main__":
    main()
