"""B15e A8 tests: choose the T2 interrupt points from a full journal (registered: by journal record index).
  python pick.py SA <journal> <maxdepth_a>   -> lines "<label> <record index>"
  python pick.py SE <journal>
  python pick.py flip <journal> <out>        -> T4: copy with the first A record's ok flipped 1 -> 0 (prints its index)
  python pick.py torn <journal> <out>        -> T5: keep ~60% of the records, a NUL line before the last kept record,
                                                then that record cut in half (no final newline)
A record index n means: SIGTERM once the journal holds n J records (the n-th record is the last one written).
Written by Claude Opus 5.5 (Quantum-personal).
"""
import sys


def recs(path):
    out = []
    for l in open(path, "rb").read().decode("latin-1").split("\n"):
        if not l.startswith("J "):
            continue
        t = l.split(" ")
        ph, key, p = t[1], t[2], t[3]
        out.append(dict(line=l, ph=ph, key=key, path="" if p == "-" else p, f1=int(t[4]), f2=int(t[5]),
                        why=bytes.fromhex(t[-2]).decode("latin-1") if t[-2] != "-" else ""))
    return out


def first(rs, cond):
    # only records whose NEXT record belongs to the same top-level piece: the kill then lands mid-piece (no P/EP yet)
    for i, r in enumerate(rs):
        if i + 1 < len(rs) and rs[i + 1]["key"] == r["key"] and cond(i, r):
            return i + 1
    return None


def main():
    mode = sys.argv[1]
    rs = recs(sys.argv[2])
    if mode == "SA":
        md = int(sys.argv[3])
        for d in (1, 2, 4, md):
            print(f"depth{d} {first(rs, lambda i, r: len(r['path']) == d)}")
        print(f"throw {first(rs, lambda i, r: r['why'].startswith('piece cap') and len(r['path']) > 0)}")
        # a failing node below the depth cap whose next record is not its first child: the leaf-cap test stopped it
        def leafcap(i, r):
            if r["f1"] != 0 or len(r["path"]) >= md:
                return False
            return rs[i + 1]["path"] != r["path"] + "0"
        print(f"leafcap {first(rs, leafcap)}")
    elif mode == "SE":
        for d in (1, 2, 4):
            print(f"depth{d} {first(rs, lambda i, r: len(r['path']) == d)}")
        print(f"certfail {first(rs, lambda i, r: r['f2'] == 1 and len(r['path']) > 0)}")
    elif mode == "flip":
        lines = open(sys.argv[2], "rb").read().decode("latin-1").split("\n")
        n = 0; done = None
        for j, l in enumerate(lines):
            if l.startswith("J "):
                n += 1
                t = l.split(" ")
                if done is None and t[1] == "A" and t[4] == "1":
                    t[4] = "0"; lines[j] = " ".join(t); done = n
        open(sys.argv[3], "wb").write("\n".join(lines).encode("latin-1"))
        print(done)
    elif mode == "torn":
        lines = open(sys.argv[2], "rb").read().decode("latin-1").split("\n")
        jidx = [j for j, l in enumerate(lines) if l.startswith("J ")]
        k = jidx[int(len(jidx) * 0.6)]
        keep = lines[:k] + ["NUL\x00LINE"]
        cut = lines[k][: len(lines[k]) // 2]
        open(sys.argv[3], "wb").write(("\n".join(keep) + "\n" + cut).encode("latin-1"))
        print(int(len(jidx) * 0.6))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
