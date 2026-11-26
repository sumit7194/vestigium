# Power loss / hard crash, 2026-11-26 ~06:52 (powered on 08:45): Quantum's jobs

Written by Claude Opus 5.5 (Quantum) at the Bridge's request.

## Inventory at 06:52
| Job | PID | On-disk state | Lost |
|---|---|---|---|
| A3 main_cont (mn_so_erep, W0 1e-7) | 40882 | `main_cont/st` 06:42, step 7082, t 965.818 (next_cp 9); grid save st.t952.2673 | ~10 min. A3's verdict (FAIL, controls hold) was already final; the run was heading to R4 (sec_return 1018.7, state save only) |
| branch-S piece mm (mn_so_piece) | 77770 | `retry_s/mm/st` 06:23, step 415, t 195.139 | ~29 min (it had logged step 420) |
| branch-S piece mp (mn_so_piece) | 78133 | `retry_s/mp/st` 06:51, step 433, t 200.790 | ~1 min |
| kerr_e N3N4, N4N5, N5N0 (hs_cover_b15d, alarm cancelled 19:41) | 6670/6675/6677 | NONE: edges have no checkpoint, and outputs hold only "PREC 128" (0 FAILPIECE) | ALL: 57.0 h each, 171 core-h |
| kerr_e N5N1, optional (same) | 93687 | NONE (same) | ALL: about 32.8 h (34.2 h minus 1.4 h paused) |
| kerr_e N1N2 rerun (hs_cover_b15e, 30 d) | 14570 | NONE (same) | ALL: 10.6 h |
| A4 launcher, kerr_guards, erep guards and cost watch | 14522 / 91716, 14591 / … | none needed | none |

**Lost compute:** about 214 core-h of Kerr edge work, plus about 40 core-min of A3 and the pieces. No result was lost:
none of these chunks had produced a reading.

## Integrity
- Every mn_so state file was parsed completely against its own format: header, x, C, H, B, re, the EREP block with N
  generator columns (all MPFR hex values valid), the END marker, no trailing data and no NUL (unwritten) bytes. Checked:
  main_cont/st, st.t952.2673, st.pre_sec_down, retry_s/mm/st and retry_s/mp/st. All OK.
- mn_so's load() also refuses a truncated file; all three resumes printed a correct RESUMED line.
- `git fsck`: clean. main = origin/main = e04bcf4.

## Relaunched from verified checkpoints (2026-11-26 08:49; the Bridge allowed resumes at once)
- **A3: PID 2834.** Same command (mn_so_erep 4a48b59a…; zsym, REDO, SAVE_FROM 292 / SAVE_DT 20). RESUMED at
  t 965.818, step 7082. Guard 2841 (--inform); cost watch 2848 (--inform; it reads the run's FIRST RESUMED line, which is
  still the registered "next checkpoint 3").
- **mm: PID 2836** (mn_so_piece 491fb0a1…), RESUMED at step 415. Guard 2843.
- **mp: PID 2838**, RESUMED at step 433. Guard 2845.
- **Not relaunched (from zero, waiting for the Bridge's word):** kerr_e N1N2, N2N3, N3N4, N4N5, N5N0 (required) and
  N5N1 (optional). The A4 launcher is not relaunched.
