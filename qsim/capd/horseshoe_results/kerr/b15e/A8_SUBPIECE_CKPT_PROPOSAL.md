# A8 PROPOSAL (draft, not registered): sub-piece checkpoints and a progress file, for the next binary revision

Drafted 2026-11-26 by Quantum-personal (Claude Opus 5.5) at the personal Bridge's request.

**This changes nothing that is running.**
- The 6 kerr_e chunks keep hs_cover_b15e2 77eb34a6 and hs_cover_b15e2s df234aa2.
- A7's interior phase stays on 77eb34a6 as registered.
- A new binary would be used only for chunks that START after it is registered and has passed §4. Each such switch needs its own Bridge yes.

## 1. Problem
- A5/A5b checkpoints are written once per TOP-LEVEL piece, as P/F records for (a) and EP/EF records for edges.
- A crash, power loss or watchdog hit therefore loses the whole bisection tree under the piece in progress.
  - (a): up to 65536 leaves per covering, depth 16.
  - Edges: depth 12, a cumulative 2 × 4096 leaves.
- The liveness check on 2026-11-26 (liveness/NOTE.md) showed this can be hours of work: N1N2 spent 3.5 h without one record.
- There is also no visible progress. The only way to tell slow from stuck was stack sampling.

## 2. Change 1: per-evaluation journal inside cover_a / cover_b (opt-in)
- **Turned on by** a new spec line, `subckpt on`. With the line absent, the binary's code path and output are byte-identical to 77eb34a6 (§4 T0).
- **What a resume must reproduce.** Each call of cover_a/cover_b first evaluates image() on its box, and that includes INTERNAL nodes, which fail and are then bisected. Whether a node bisects depends on three things:
  - its own outcome;
  - its depth;
  - the running leaf count `st.leaves`, through the cap test `st.leaves + 2 <= MAXLEAF`.
  - `st.nsteps` and the return-time hull `st.rt` also build up over every evaluation, including partial replay steps from a call that THROWS.
  - So a resume has to rebuild these from records, one record per evaluation.
- **Record.** One line per evaluated node, appended and fsynced in depth-first order:
  - Edge form: `EN <toplevel key> <path> <outcome> <dnsteps> <rtflag> [rt lo hi hex] <why-hex> #`
  - (a) form: `AN …`, the same fields.
  - `<path>` is the bisection path from the top-level piece, e.g. `LRL` (lo/hi at each split; for (a), u or s is implied by the registered along-u rule).
  - `<outcome>` is the node's full classification:
    - edge: land 0, land 1, fail, or certfail;
    - (a): ok-strong, ok-weak, or fail.
  - The FAILPIECE text is not stored. It is rebuilt from the same fields, using the same failline() code.
- **Resume.** The same depth-first walk runs again. At each node with a complete record, the recorded outcome and deltas are used instead of calling image(); the cap tests and bisection logic run unchanged. The first node without a record is evaluated live.
- **Existing records are kept.** The top-level P/EP record is still written when the piece completes, and the readers already ignore unknown record types (the one-record buffer rule). After a P/EP record exists, that piece's EN/AN lines are never read, so top-level reload works exactly as now.
- **Cost.** One fsync per image() call. A Kerr evaluation takes minutes, so this is negligible. An HH (a) leaf takes about 0.1 to 1 s, so the progress file's batching (below) applies instead: for (a), records are flushed every `subckpt_flush <k>` evaluations (default 1).
- **Disk.** About 150 B per node. That is ≤ ~20 MB for a capped (a) covering, which is within the guards' 3 GB floor.

## 3. Change 2: a progress file (opt-in, never in the .out)
- The binary's stderr and stdout go to the same .out, which the readers, promote_air.sh and the byte-identity tests all parse. So progress must NOT go to stderr.
- **Turned on by** a spec line, `progress <path> <N>`. Every N image() calls, and at the start and end of each top-level piece, the binary writes ONE line to `<path>.tmp` and then renames it over `<path>`, so the file always holds one complete line.
- **Contents:** wall time; phase (a or E); top-level key; current depth; leaves done; image() calls; nsteps; and calls since the last record.
- The binary itself never reads this file, so it cannot affect a result.
- Watchers can then report slow versus stuck by reading the file: "calls since last record" keeps rising while the process is alive.

## 4. Identity tests (before registration; on the Mac mini, then the Air for the static build)
- **T0, regression.** Every A4 stored output and the A5 T1/T3 and A5b B1 outputs are rerun on the new binary WITHOUT the new spec lines. They must be byte-identical.
- **T1, nothing lost with the options on.** hh2_N0N0, both (a) and edges, with `subckpt on` and `progress`:
  - the .out must be byte-identical to the stored output;
  - the progress file must hold one line, and that line must parse.
- **T2, interrupt at sub-piece depth** (the case this exists for).
  - SIGTERM at 5 points chosen to land inside a bisection tree at depths 1, 2, 4, 8 and the deepest seen, choosing points from a first run's journal.
  - At least one interrupt falls right after a node that THREW, and at least one right after the leaf-cap test turned a bisection into a final failure.
  - After the restart, the .out must be byte-identical (ignoring the EDGES/PIECES RELOADED lines).
- **T3, solver state.** Engine reuses one CAPD solver and Poincaré map for every call, so skipping evaluations could in principle change later step-size choices. Whole-piece skips already pass A5/A5b, but sub-piece skips are a finer test. T2 covers this directly: a mismatch there would show carried state. T3 adds a test that compares one Kerr edge piece end to end with and without a mid-tree resume, as a slow-system check.
- **T4, must-fire.** A copy of a journal with one EN record's outcome flipped (land 0 → fail) must change the COVER line, or the FAILPIECE set.
- **T5, torn last line.** A journal cut mid-line must resume as in A5's newline-repair rule: the partial record is ignored and the node is re-evaluated.
- **T6, Air.** The static build passes T0–T2 byte-identical with the Mac mini.
- **Cost of the tests:** about 3–4 core-h in all (hh2 runs of 17–80 min each, plus one Kerr edge piece for T3 of perhaps 1–3 h), on 1 core, NOT COUNTED.

## 5. Hard limits (listed per the registration rule)
- These are unchanged: HS_WATCHDOG_S (30 d, fails closed), the leaf and depth caps (registered checks that end a piece as a counted failure, not a job), and guards that only pause.
- With the journal on, a watchdog hit or crash loses at most one image() evaluation instead of one bisection tree.

## 6. Decisions for the Bridge
1. Whether this should be built at all, and if so whether before kerr_a starts, or only for chunks after the kerr_a pilot's cost report.
2. Whether the journal should cover both (a) and edges, or only Kerr (where an evaluation takes minutes); HH (a) is fast enough that per-top-level records may be enough.
3. Default N for the progress file: 1 for Kerr, about 100 for HH.
4. Whether chunks already running, or resumed under A7 on 77eb34a6, may switch binaries at a resume. The proposal says NO: a chunk keeps its binary from start to DONE.
