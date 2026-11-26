> **Superseded (2026-11-26):** registered as B15e A7 in PREREG_chaos_horseshoe_phase2.md, with corrections. The rot90 pair runs as ordinary twin_a chunks in its registered queue place (not unchunked, not first), so C1 gates nothing. A7 governs; this draft is kept as written.

# B15e A7 DRAFT (not registered): the interior (a) phase, i.e. the twin (a) chunks, the two rot90 resumes and the 8 Kerr (a) chunks

Drafted 2026-11-26 by Quantum-personal (Claude Opus 5.5) for the personal Bridge. NOTHING here runs until the Bridge agrees
and the text is registered in PREREG_chaos_horseshoe_phase2.md. The B15e order, sets, specs (except one checkpoint line
per kerr_a spec, §3), caps, depth, precision, classifier, merge rule and readings are unchanged.

## 1. What is left of the registered B15e work
- **Kerr edges (kerr_e):**
  - N0N0 and N0N1 are DONE;
  - N1N2 is running on the Mac mini (b15e2, edge checkpoints);
  - N2N3, N3N4, N4N5, N5N0 and N5N1 are running on the Air (A6).
  - KERR-EARLY is logged when all 8 are complete (§5).
- **Twin, as B15e requires:** "every twin merge complete with no HARNESS-ERROR" before KERR is final. twin_table()
  covers all 12 twin coverings, rot90 included.
  - The swap and rot90 edge chunks (twin_e) are complete.
  - No twin (a) chunk has run.
  - The two unchunked rot90 coverings (N0N0 and N0N3, adopted under B15d-2) ended in WATCHDOG TIMEOUT (the old 48 h
    binary). Their (a) checkpoints hold 101/256 and 34/256 finished top-level pieces (ckpt/twin/, 6.3 and 6.2 MB,
    newline-terminated).
- **Kerr (a) (kerr_a):** none has run; ckpt/kerr/ is empty.

## 2. Binary and identity basis
- **The binary:** hs_cover_b15e2 77eb34a6 on the Mac mini, with HS_WATCHDOG_S = 2592000 (30 d, the parser's maximum).
  It carries A4 (the watchdog setting), A5 (edge checkpoints) and A5b (crash-safe (a) reading).
- **Identity basis already on record:**
  - A4: 5 stored outputs reproduce byte for byte.
  - A5: T1, T3, T4, T5, T6 and T6b pass.
  - A5b: B1 to B5 pass. B3 is the case that matters most here: an OLD-format (B15d) (a) checkpoint, reloaded on the
    unchunked hh2_N0N0 spec, gives a byte-identical COVER line. That is exactly the rot90 resume case.
- **One gap, and a proposed test (C1, ~40 min, one core, NOT COUNTED):** an UNCHUNKED spec with a checkpoint writes P
  records ((a)) and EP records (edges) into ONE file. B3 ran that case once, uninterrupted. An interruption DURING the
  edge phase of such a run has not been tested.
  - C1: gb/hh2_N0N0.spec with a fresh checkpoint path, SIGTERM after ≥ 32 EP records, then restart.
  - It must be byte-identical to gb/hh2_N0N0.out, ignoring the EDGES RELOADED line and reloaded_pieces.
  - Must-fire: a copy with one EP record's leaf count tampered must change the COVER line.
  - C1 gates the rot90 resumes only.
- **The Air (b15e2s df234aa2) is NOT proposed for (a) work yet.**
  - Its A6 identity covered T1 (unchunked, no checkpoint) and the edge-checkpoint tests, not the A5b (a)-reader tests.
  - promote_air.sh promotes edge chunks only (it checks 128 EP records).
  - If the Bridge wants the Air for (a) chunks once its kerr_e chunks end, that is a later addendum: A5b B1 to B5 on
    the Air with b15e2s (~1.5 h), plus an (a)-chunk promotion rule (complete .out, all 256 P records).

## 3. One spec change: a separate checkpoint path for kerr_a
- **Finding:** kerr_a/<c>.spec and the A5 kerr_e/<c>.spec name the SAME file, ckpt/kerr/<c>.ckpt.
  - The two readers ignore each other's record types (P/F against EP/EF), so this is not a correctness bug.
  - But for N1N2 the edge chunk is writing that file now. An audit, a pull or a truncation repair then mixes two
    chunks' records in one file, and a later (a) restart would repair the newline of a file that another chunk owns.
- **Proposal:** each kerr_a spec's checkpoint line points to ckpt/kerr_a/<c>.ckpt, recording the spec sha old → new.
  - No kerr_a chunk has ever run, so nothing is lost.
  - The twin_a specs keep ckpt/twin/<t>.ckpt; those files are theirs alone.

## 4. Order and placement
- **Order (B15e step 3):**
  1. The two rot90 resumes come first, after C1 passes. In the registered order they were "running"; they resume from
     their checkpoints under their ORIGINAL unchunked specs (twin/rot90_N0N0.spec, twin/rot90_N0N3.spec).
     - The WATCHDOG outputs are moved, not deleted, to twin_void_watchdog/.
     - Their merged class is read as B15d-2 registered: the unchunked COVER line, with its edge part checked against
       twin_e.
  2. Then the registered interleave, twin_a[0], kerr_a[0], twin_a[1], kerr_a[1], …:
     - twin_a = swap_N0N0, swap_N0N3, swap_N3N4, swap_N4N5, swap_N5N6, swap_N6N0, rot90_N3N4, rot90_N4N5,
       rot90_N5N6, rot90_N6N0;
     - kerr_a = N0N0, N0N1, N1N2, N2N3, N3N4, N4N5, N5N0, N5N1;
     - the twin list's tail runs after the Kerr list ends.
  - That is 20 jobs in all.
- **Placement:** Mac mini only, as cores free under the Quantum cap (a5_mycap/a4_mycap: 7).
  - The 4 retry pieces hold 4 cores for ~4–5 more days, and the 2 refs workers hold 2.
  - So in practice the (a) phase starts on the core N1N2 frees, plus the refs' cores when they finish.
  - A launcher of the same form as a5_launch.sh: verified-sha binary, refuses a chunk that is alive or has DONE, moves
    old outputs aside, nice 10, stdbuf -oL, a kerr_guard each (pause-only), and a file-adjustable cap.

## 5. Readings (unchanged; produced by the registered code, not re-implemented)
- **KERR-EARLY:** when all 8 kerr_e outputs are in b15d/kerr_e/, with the Air ones promoted by promote_air.sh, one line
  "KERR-EARLY: <json>" from b15d_split.kerr_table(), to the Bridge. It is never the result.
- **Final:** a short b15e_read.py that imports b15d_split and runs b15d_split.run()'s closing block VERBATIM:
  - the TWIN line, and the "TWIN not PASS" hold if it applies;
  - TWIN-1V;
  - "KERR (B15e, final)" if every twin merge is complete with no HARNESS-ERROR and swap PASS, else "KERR WITHHELD";
  - written to b15d/run.log through b15d_run.log.
  - The runner that used to log these lines is retired, so this keeps the same text from the same functions.
- The sealed-prediction graders (grade_prediction.py, grade_kerr_prediction.py) read those lines; neither changes.

## 6. Cost and hard limits (listed together, per the registration rule)
- **Twin (a)** (HH, fast steps): up to the 65536-leaf cap per covering. The B15d-4 estimate is ~90 h per capped
  covering on one core; coverings that pass take minutes to hours (hh2: 17–80 min each).
  - rot90 N0N0 and N0N3 have spent ~27.7k failing leaves each (F lines in their checkpoints), so each resume is bounded
    by the remaining ~37.8k leaves.
  - Total, all 12 twin coverings: ≤ ~12 × 90 ≈ 1100 core-h worst case; much less if the swap (a) chunks pass early.
- **Kerr (a): the cost is NOT known.** The only measured rate is ~13 min per edge evaluation (N0N0/N0N1 on the Mac mini).
  - At that rate, 256 top-level pieces with no bisection come to ≈ 55 h per chunk, a lower bound.
  - The 65536-leaf cap allows far more. No estimate is credible before a measurement.
  - Proposal: the first kerr_a chunk (N0N0) is itself the pilot. Its checkpoint gives per-piece leaves and time after
    its first ~10 top-level pieces. A cost report goes to the Bridge before a second kerr_a chunk starts.
  - The pilot IS the counted run (checkpointed), so nothing is spent twice.
- **Hard limits that can end a job:** only HS_WATCHDOG_S (30 d wall clock, pauses included; it fails closed).
  - Every (a) job here is checkpointed per top-level piece, so a watchdog hit loses at most one piece; the rerun
    resumes from the checkpoint.
  - Leaf and depth caps are part of the registered check: they end a piece as a counted failure and the job still
    prints COVER and DONE.
  - Guards pause only (disk < 3 GB, memory red sustained); nothing kills.
- **Memory:** ~30 MB per Kerr process; HH (a) processes ~100 MB.
- **Disk:** twin checkpoints ~6 MB each at ~28k failing leaves, so ≤ ~15 MB each at the cap; ≤ ~0.3 GB in all.

## 7. Decisions for the Bridge
1. C1 (the combined-file interrupt test) as a gate before the rot90 resumes: yes or no.
2. The kerr_a checkpoint path change (§3).
3. b15e_read.py as the reading step (§5).
4. The kerr_a pilot rule (§6): a cost report after ~10 pieces of kerr_a N0N0, before kerr_a[1] starts.
5. The Air for (a) work later (§2): only after its own A5b tests and a promotion rule.
