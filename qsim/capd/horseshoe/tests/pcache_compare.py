"""Read-only comparison of two pcache journals (no truncation): every key present in both must have bitwise-identical
values (pickled bytes of the value). Usage: pcache_compare.py ref.journal other.journal"""
import sys, struct, pickle, hashlib
def read(fn):
    d = open(fn, "rb").read(); o = 0; recs = []; first = True
    while o + 8 <= len(d):
        n, crc = struct.unpack("<II", d[o:o + 8]); body = d[o + 8:o + 8 + n]
        if len(body) < n or hashlib.sha256(body).digest()[:4] != struct.pack("<I", crc): break
        o += 8 + n; rec = pickle.loads(body)
        if first: first = False; continue
        recs.append((rec["key"], pickle.dumps(rec["val"], protocol=4)))
    return recs
A, B = read(sys.argv[1]), read(sys.argv[2]); da = dict(A); db = dict(B)
common = [k for k, _ in A if k in db]; diff = [k for k in common if da[k] != db[k]]
order_ok = [k for k, _ in A][:len(B)] == [k for k, _ in B][:len(A)]
print("ref records %d, other %d, common %d, differing %d, same call order: %s" % (len(A), len(B), len(common), len(diff), order_ok))
print("PCACHE RESUME", "PASS" if not diff and order_ok and len(common) > 0 else "FAIL")
