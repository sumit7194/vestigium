# Referee guide: which file proves which claim, in what order, and what you should see

**DRAFT (2026-11-28).** For: S. Pal, "Chaotic geodesics in the Manko–Novikov spacetime: a computer-assisted proof and
a Melnikov theorem (AI-assisted)".

All paths are relative to the software record vestigium v2026.11.28 (doi:10.5281/zenodo.24602464, the GitHub tag
v2026.11.28). Unless stated otherwise, they live under `qsim/mn_homoclinic_spike/` (written below as `S/`).

**A reading note.** In these files, "registered" or "PREREG" means *decision rules and expected outcomes written and
committed before the computation*. "Non-author read" means *a check by a separate AI session*, **not** human peer
review.

## 0. Environment
- **Library versions:**
  - CAPD, git commit 2f06098 (built with MPFR 4.2.2 and GMP 6.3.0);
  - python-flint 0.9.0, mpmath 1.3.0, Python 3.13;
  - macOS on Apple silicon (the original runs).
- **Build** the proof program with the guard (no non-MPFR interval types are allowed):
  `CXXEXTRA="-I qsim/capd/horseshoe" qsim/capd/tests/guard_build.sh S/capd/s2_main.cpp s2_main`
  (add `-DSABFIELD` to CXXEXTRA for the control-(iii) field).
  - The field header is `qsim/capd/horseshoe/gen/mn_field.h`, sha256 4c1c7b57….

## 1. Theorem 1 (β = 3/100), in order
| Step | Claim | Run | Input spec | Expected output line (in `S/s2v4/mn/*.out`) | Time |
|---|---|---|---|---|---|
| 1 | hyperbolic fixed point, radius 1e−19 | `s2_main fp` | `S/s2/mn/fp.spec` | `RESULT fp CERTIFIED`; `KRAWCZYK Y 1.546…e-21 Z 2.887…e-08` | ~8 min |
| 2 | local unstable manifold (cone lemma A11) | `s2_main cone` | `S/s2/mn/cone.spec` | `RESULT cone CERTIFIED L 1.2029…e-02 … deltastar 3.7354…e-11` | ~6 min |
| 3 | symmetric homoclinic point and transversality | `s2_main bvp` | `S/s2/mn/bvp.spec` | `KRAWCZYK Y 7.835…e-16 Z 3.422…e-04`; `v[0] [1.12448…e+07,1.13003…e+07]`; `SIGNTEST v_x EXCLUDES 0 ; v_px EXCLUDES 0` | ~80 min |

- Each run takes a third argument, a dump file, which writes the exact enclosures used in the decisions.
- `S/s2v4/run_chain.sh` runs steps 1–3 in order.
- **Lemmas used:**
  - A1 (reversible transversality): `S/PREREG.md`, amendment A1;
  - A11 (the cone lemma, with proof): `S/PREREG.md`, amendment A11.
- **The result write-up:** `S/S2_RESULT.md`.

## 2. Controls (the same program)
| Control | Spec | Expected | Time |
|---|---|---|---|
| (i) Kerr, β = 0: must NOT certify transversality | `S/s2/kerr_i/{fp,cone,bvp}.spec` | `SIGNTEST v_x CONTAINS 0` | ~60 min |
| (ii) Kerr homoclinics form an arc | `s2_main meet S/s2/meet_ii/meet.spec` | `RESULT meet krawczyk CERTIFIED klemma OK` | ~100 min |
| (iii) the β² term removed (build with `-DSABFIELD`) | `S/s2/sab_iii/*.spec` | x of p disjoint from MN's (compare the bvp outputs) | ~90 min |
| (iv) the validator reproduces CKMJ's L4 homoclinic | `S/capd/s2_l4.cpp`, `S/s2/l4_iv/bvp2.spec.gz` (gunzip) | `S/s2/l4_iv/bvp2_v4.out`: certified, with distance to CKMJ's p̄ < their r | ~few min (+ float set-up, `S/l4run.py`) |

- Control (ii)'s exact Carter bracket: `python S/carter_check.py` gives `S/carter_check.json`.

## 3. The second arithmetic library (seconds)
- `python S/tier1_check.py run` re-evaluates every decision of steps 1–3 and controls (i)–(iii) from the dumps in
  `S/s2v4/`, using Arb. Expected: `"VERDICT": {"MN": true, "control_i": true, "control_ii": true, "control_iii": true}`.
- `python S/tier1_check.py mustfail` runs the corrupted-input cases. Each must be refused; see `S/PREREG.md` A13.1–A13.2
  for the record, including one mis-designed case that was disclosed.

## 4. The independent field (seconds)
- `python S/tier2a/compare.py` compares the separately written `S/tier2a/indep/mn_indep.py` (from Gair–Li–Mandel,
  frozen by sha256 before the comparison) with the header and with the Melnikov module.
- Expected: `"VERDICT": "AGREE"`. The must-fail cases fire. See `S/tier2a/TIER2A_RESULT.md`.

## 5. Theorem 2 (every small β)
- **The argument, with every hypothesis and step:** `S/STEP_A_MELNIKOV_GLUE.md`.
  - It cites Robinson (Contemp. Math. 198, 1996), Thm 3.4 and Rem. 3.10. Its hypotheses were checked at source; see (H4)
    in that file.
- **The certified Melnikov coefficients:** `qsim/mn_melnikov/`.
  - `mel_cert.py` (via `mel_launch.sh`) gives L₂ and the gates and controls: `CHECKS.json` and `run.out`. About 2.5 h.
  - `t3_cert.py --set full` (via `mel_launch_s2.sh`) gives L₄ and the tail bound T₃: `T3.json`. About 24 h.
  - The result is in `RESULT.md`. Expected: L₂ = −4.77482114974644e−5 ± 6.81e−20, and the margin
    |L₂| − 4|L₄| − T₃ = +1.5242e−5 at (σ, τ) = (0.13, 0.6).

## 6. What to look at first if you doubt something
- **The integrator:** CAPD is the single validated integrator here (no second integrator has been run).
- **The section crossing rule** and the domain checks: `S/capd/s2_main.cpp`, functions `pass` and `mn_domain`.
- **The NaN rule** (every enclosure checked finite): A12.9 in `S/PREREG.md`, and the v4 rerun, which is identical.
- **The thin Melnikov margin:** T₃ uses 68% of |L₂| at the one closing point.
