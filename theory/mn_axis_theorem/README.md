# MN axis theorem: general non-integrability of Manko–Novikov geodesics (work in progress)

Imported 2026-11-18 on branch `mn-axis-theorem` (worktree `quantum-mnthm`), not main.

| file | what | model / author | status |
|---|---|---|---|
| `DESIGN.md` | route comparison, Theorem 1 and its proof (sections 1–10) | Claude Fable 5.2, session Quantum-personal, 2026-11-18. Imported VERBATIM from `/Users/sumit/Github/fable_work/mn_general_theorem/DESIGN.md` (sha256 in the commit message) | unreviewed when imported; the review outcome is recorded in REVIEW.md, and DESIGN.md is only changed by later, separately labelled commits |
| `LITERATURE.md` | literature check (Step 0) | Claude Opus 5.5 subagent, briefed by Fable | as written; it lists what it could not verify |
| `THEOREM.md` | corrected statement (revision 1), folding in REVIEW.md | Claude Opus 5.5 | reviewed once; not registered |
| `REVIEW.md` | independent adversarial review: Theorem 1 STANDS WITH CORRECTIONS (9 overruled points, corrected statement) | a fresh Claude Opus 5.5 subagent with no Fable context; recorded by Opus 5.5 | done 2026-11-18 |
| `../../PREREG_mn_axis_lattice_certified.md` | certified tests of the design near x = 0 | Claude Opus 5.5 (prereg and code), agreed by the Bridge | registered reading PASS (qsim/mn_lattice/RESULT.md): T-exact, T-limit and T-L6 at j = 10, 100, 1000; 12/12 Lean-checked |

Independent float check by the Bridge: `TheBridge/falsification/V21_mn_axis_theorem_check` (30231db). C1, C2 and the
static C3 limit pass; the registered verdict is VOID on V21's own monotonicity clause (see its FINDINGS.md).
