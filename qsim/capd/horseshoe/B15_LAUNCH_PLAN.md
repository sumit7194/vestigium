# B15 counted run with the compiled map (B15_MAP=rust): launch plan

Status: DRAFT for the Bridge to take to Sumit, 2026-11-20. **Nothing launches without Sumit's OK.**
Written by Claude Opus 5.5 (session "Quantum").

## 1. What has passed

- **The gates.** B15b G0, G0b-field, G0c, G2 and G5 passed earlier; G1, G3 and G4 PASS and the G4c reference was accepted
  on 2026-11-20 (9e6e6f1). That makes G0–G5 complete, which the registration requires before the counted run.
  G6 runs alongside it.
- **The wiring (326dc45; code and tests only).**
  - `b15_kerr_ck.py` with `B15_MAP=rust` uses kerr_rs behind MNFlow's interface.
  - Its dylib sha256 is 42ea6c3c…, the same build the gates used.
  - `delta_floor = max(1e-6, 100 × 2.03e-11) = 1e-6`.
  - It writes new files: `b15_rust.journal`, `b15_kerr_rust.json` and `b15_rust_arcs.npz`. A rust run never replays an
    MNFlow journal.
  - Each certified plunge is appended crash-safe to `b15_rust_plunges.jsonl` (for G6 P5).
  - A `MapCheckFailed` (−1, or an uncertified −2) stops the run; it is never turned into "no return".
  - If a connection is accepted, the B15b-2 scope note is written (steps 3–4 are not implemented).
- **Smoke test.** Step 1 alone with the rust map: z reproduces exactly, and λ_u = 62.620268580319085, 2.6e-13
  relative from G5.
- **G6 driver** (`b15b_g6_run.py`). It applies the committed decision functions (b15b_g6.py; toys PASS, 9e5b94b) to the
  run's own records. Its end-to-end test (`test_b15b_g6_run.py`) runs the real `b15_kerr_ck.py` on a test-only toy map: the
  standard map with an outer hole and an interior band hole. It checks:
  - **Complete:** the replica is bit-identical, and the D1/D4/D6/D7 counts equal the run's.
  - **Flags thin decisions:** the near-tangent crossings, with angles ~4e-12, are flagged and sent to the 1e-14
    recompute.
  - **Drops and chords:** drops are recorded and chord segments are found.
  - **Negative controls:** a 1-ulp change to one arc point, or one journal entry removed, gives INCOMPLETE.

## 2. The run

1. Launch `B15_MAP=rust python -u b15_kerr_ck.py` in `qsim/capd/horseshoe`, detached (tools/detach.sh). Steps 1 and 2
   follow the registration unchanged: the frozen constructor, the B14 parameters, and TMAX 1e6.
2. Then run G6: `python b15b_g6_run.py`, which writes `b15_g6.json`.
3. Then the findings. They cover:
   - the constructor verdict;
   - the G6 verdict: INCOMPLETE, UNRESOLVED (with the decisions named), or PASS with its flags;
   - D8 under B15b-2;
   - the P5 plunge summary;
   - every flag.

## 3. Resource estimate (measured inputs)

- **Map cost:** one kerr_rs return takes 4–12 ms (measured today on G4 points, T from 693 to 65,354; 1e-14 takes about
  2× as long as 1e-12).
- **Run, steps 1–2:** the old MNFlow run had 26,047 W^u points. With refinement calls, about 10⁵ map calls, so about
  10–20 min on 1 core.
  - The plunge-certificate cost per None is not yet measured. It is reported from the run, and I'd expect it to be
    small.
- **G6:**
  - fresh Jacobians at every arc point, about 5×10⁴ × 10 ms ≈ 10 min;
  - the near-miss scan (vectorised), minutes;
  - the 1e-14/1e-13 recomputes of thin decisions, 8 orbits × ≤ 5 returns × ~10 ms each, so ~0.4 s per decision. Even
    10⁴ thin decisions take ~1 h.
- **Memory and disk:** the journal is held in memory, well under 1 GB; on disk tens of MB.
- **In total:** 1 core, under 2 h wall, < 1 GB, < 100 MB of disk.

## 4. Points for the Bridge and Sumit to decide

1. **Priority.**
   - The registration says "one process, not low-priority. No wall-time cap (B16)". The shared-box rules (2026-11-17)
     came later and say nice ≥ 10.
   - Proposal: nice 10, detached, with the usual guard: the sustained-pressure rule, a 2 GB own-footprint cap, and the
     disk stop.
   - That changes only scheduling, not the run. Sumit's call.
2. **The G6 design.** B15B_G6_DESIGN.md was written for the Bridge's review on 2026-10-24. Its decision list is in the
   registered G6 text, and the driver follows it. Please confirm it as agreed, together with these implementation
   choices (all conservative, none weakening a check):
   - (a) the per-point error is e_k = Σ_{j<k} ‖DF(q_{k−1})⋯DF(q_{j+1})‖ e_map(T_j), plus the start-point error
     carried by the full product;
   - (b) the 1e-14 recompute measures its own error by self-convergence (1e-14 against 1e-13, ×3) on the recomputed
     orbits, so the propagation is included in the measured difference;
   - (c) near-misses are recomputed only where the angle could reach 0.01;
   - (d) a crossing exactly at a vertex is THIN (the toy has two).
3. **Expected consequence of the norm-based gain.** Near the saddle, ‖DP‖ is about 62 per return, so 62⁵ ≈ 9×10⁸ at
   level 5. First-pass errors at the high levels will be large (∼10⁻²), and many decisions will be thin on the first
   pass. They are then decided by the 1e-14 recompute's measured error. That is the registered path. It costs ~1 h at
   most (above); it is not a problem. It is stated now so that a long flag list is not a surprise.
4. **Steps 3–4 are not implemented.** If step 2 accepts a non-chord connection, the outcome is "registered prediction
   NOT CONFIRMED because of an implementation scope limit; not a negative result" (B15b-2). Steps 3–4 would need code and
   their own amendment.
