"""A7 (PREREG_mn_equatorial_v2.md): (1) v1 G0 at N=140; (2) re-replay the row-1 A6 v2 certificate with v1 at N=140."""
import functools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ia_hub as IA


def g0_140():
    import mr_mn_axis as MA
    orig = IA.transport
    IA.transport = functools.partial(orig, N=140)        # the G0 tests, unchanged, at N = 140
    try:
        return MA.g0()
    finally:
        IA.transport = orig


def replay_row1():
    import mr_v2 as V
    d = json.load(open(os.path.join(HERE, "mr_v2_mneq_row1_a6_v2cert.json")))
    S = V.system_equatorial("mn", "p1", 1, 0, 9)
    sing = [complex(s.replace(" ", "")) for s in d["located"]]
    return V.replay_v1(S, d, sing, procs=2, N=140)


if __name__ == "__main__":
    if sys.argv[1] == "G0":
        r = g0_140(); json.dump(r, open(os.path.join(HERE, "mr_v2_a7_G0.json"), "w"), indent=1, default=str)
        print(json.dumps(r, indent=1, default=str))
    else:
        r = replay_row1(); json.dump(r, open(os.path.join(HERE, "mr_v2_a7_row1_replay.json"), "w"), indent=1, default=str)
        print("A7 v1 replay at N=140:", r["replayed"]); print(json.dumps({k: v for k, v in r.items() if "midrad" in k}, indent=1))
