# E representation: the registered main run (Z-sym)

- Registration: `qsim/capd/horseshoe/E_REP_PREREG.md`, REGISTERED and amended by A1.
- Pre-run tests (all PASS): T1 (`../T1`), T2 (`../T2`), T3 (`../T3`), and the zsym resume check (`../T4_resume`).
- Run: `mn_so_erep` with SO_EREP=zsym, W0 1/10000000, `mn_smoke/b17_cp_1e-7.txt`, from t = 0 through the checkpoint at
  291.8852393126. SO_FIXED_REDO is off. Detached, nice 10, under the Bridge's slot and guard.
  The command line is in `launch.txt`, written at launch.
- Reading: `read_result.sh` applies section 5/6 of the registration mechanically:
  - primary: the CHECKPOINT line at t = 291.8852 (u1, u2 and the fake ratio, each <= K = 5);
  - secondary: 290.8497, and no THREW line (S4/S9);
  - C-floor: `b17_containment.py` against the 8 W0 = 0 reference runs in `so_mn/contain/ref_1e-7_*.out`, plus no
    HARNESS-ERROR (W/tu < 0.98);
  - C-steps: no BUG.
  Any control failure gives the verdict INVALID.

## Guard rule change (2026-11-18 16:47:38, the Bridge)
- Before: stop if (swap > 2 GB OR pressure level != 1), sustained 600 s.
- After: stop if (swap > 2 GB AND level >= 2), or level >= 4 (critical), sustained 600 s. Disk < 5 GB and the run's own
  footprint > 300 MB still stop at once.
- Reason: at launch the kernel level read 2 (warning) for 120 s with ~48% of memory free, a sticky kernel level rather
  than a real squeeze.
- The guard was replaced (old PID 37817, new PID 40851, both verified, both logged in guard.log). The run itself (PID 37679)
  was not touched.
