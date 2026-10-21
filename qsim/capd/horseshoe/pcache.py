"""Crash-safe persistent memo for the constructor's map calls (P, Pinv): a checkpoint that needs no change to the FROZEN
B14 constructor. Every finished call is appended to a journal file (one pickled record, flushed and fsync'ed) keyed by
the exact float64 bytes of the input and the call's flags; a restarted run replays its finished calls from the journal
and recomputes only the call that was in progress. The maps are deterministic (same inputs, same machine, same
library versions -> bitwise the same outputs), so a resumed run reproduces the uninterrupted run exactly; the journal
also records library versions and refuses to replay under different ones.
A torn last record (power loss mid-write) is detected and dropped.
pickle is used because the values are tuples of numpy arrays and floats; the journal is written and read only by this
module, from our own results directory (never from downloaded or third-party files)."""
import os, pickle, struct, hashlib, sys
import numpy as np, scipy


def _versions():
    return dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__)


class Journal:
    def __init__(self, path):
        self.path = path; self.mem = {}; self.hits = 0; self.misses = 0
        if os.path.exists(path):
            with open(path, "rb") as fh:
                data = fh.read()
            off = 0; first = True
            while off + 8 <= len(data):
                n, crc = struct.unpack("<II", data[off:off + 8])
                body = data[off + 8:off + 8 + n]
                if len(body) < n or (hashlib.sha256(body).digest()[:4] != struct.pack("<I", crc)): break   # torn tail
                rec = pickle.loads(body); off += 8 + n
                if first:
                    if rec.get("versions") != _versions():
                        raise SystemExit("pcache: journal written under %s, now %s; refusing to replay" % (rec.get("versions"), _versions()))
                    first = False; continue
                self.mem[rec["key"]] = rec["val"]
            if off != len(data):                      # drop a torn tail so appends stay aligned
                with open(path, "r+b") as fh: fh.truncate(off)
        else:
            self._append(dict(versions=_versions()))

    def _append(self, rec):
        body = pickle.dumps(rec, protocol=4)
        crc = struct.unpack("<I", hashlib.sha256(body).digest()[:4])[0]
        with open(self.path, "ab") as fh:
            fh.write(struct.pack("<II", len(body), crc) + body); fh.flush(); os.fsync(fh.fileno())

    def call(self, tag, fn, w, **kw):
        key = (tag, np.asarray(w, dtype=np.float64).tobytes(), tuple(sorted(kw.items())))
        if key in self.mem:
            self.hits += 1; return self.mem[key]
        self.misses += 1
        val = fn(w, **kw)
        self.mem[key] = val; self._append(dict(key=key, val=val))
        return val


def wrap(H, journal):
    """Route the constructor module's P and Pinv through the journal (the constructor itself is not edited)."""
    P0, Pinv0 = H.P, H.Pinv
    H.P = lambda w, n=1, jac=False: journal.call("P", lambda w_, n, jac: P0(w_, n, jac), w, n=n, jac=jac)
    H.Pinv = lambda w: journal.call("Pinv", lambda w_: Pinv0(w_), w)
    return H
