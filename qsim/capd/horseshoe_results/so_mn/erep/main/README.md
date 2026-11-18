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
