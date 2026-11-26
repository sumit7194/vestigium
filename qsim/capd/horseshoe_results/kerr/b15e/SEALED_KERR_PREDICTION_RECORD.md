# Sealed Fable prediction of the Kerr negative control: record (the content was NOT opened)

- **Location.** Branch `fable/2026-11-26-kerr-predict`, commit fd22a7f044728e14365cd5123c3c70e69de3d6ed (parent 74b5f2e,
  2026-11-26 03:31:25). One file: `kerr/b15e/KERR_PREDICTION_SEALED.md`.
- **sha256** 99e33cd0c5aef82f59a5ece2b9b273c41a1e8a50cdac830e1e5fb9045da4604d. The Bridge verified it from the pushed
  commit without reading it.
- **Compute (per the Bridge).** About 20 s of float Python modelling the Kerr section map on the build.json sets. The
  script is in the file's appendix.
- **Disclosed prior knowledge.** From session metadata, Fable knew that N1N2/N2N3 hit the 48 h watchdog and are being
  rerun, and that "a KERR-EARLY step was passed in the queue". It knew no COVER/FAILPIECE line or class beyond
  N0N0/N0N1.
- **Grading rulings (the Bridge, 2026-11-26), applied when grading.**
  - A timeout carries no outcome, so the N1N2/N2N3 edge calls stay in the edge column, with the footnote "predictor
    knew these chunks had timed out (no outcome)".
  - **"KERR-EARLY passed in the queue": no outcome hint, as checked by Quantum.** b15d/run.log contains NO
    KERR-EARLY line at all (`grep -c KERR-EARLY` = 0 at the time of this record): KERR-EARLY has never been reached,
    because not all edge chunks are done. The metadata could at most refer to the queue order printed at start-up (the
    "B15e queue: … then kerr_e … then …" line), which says nothing about results.
  - So it carries no edge outcome. If the prediction reasons from "KERR-EARLY was reached", that premise was false,
    and the grading notes it.
- **Rule.** Quantum does not open the branch or the file until the registered KERR reading exists (B15e step 4: "KERR
  (B15e, final)" or "KERR WITHHELD"). Then: re-check the sha256, grade per §4 of BRIEF_FABLE_KERR_PREDICT.md with the
  rulings above, and send the grades to the Bridge.
- **The Fable worktree** /Users/sumit/Github/quantum-fable-kerr is kept (deletion only with Sumit's OK).

## 2026-11-26 ~12:20: the operating session is the predictions' author (the office Bridge's ruling)
- From 2026-11-26 the session that operates this project, Quantum-personal (Claude Opus 5.5; earlier on Fable 5.2), is the
  AUTHOR of this sealed prediction and knows its content. The office Quantum session paused at its weekly limit.
- The outcome comes only from the registered mechanical reader, which is unchanged and is not to be changed: read_retry.sh
  (retry) or the B15e step-4 KERR reading (Kerr). The operating session changes neither the reader nor its inputs.
- The grading follows brief §4 through a grading script committed BEFORE any result exists, and never edited afterwards.
  The personal Bridge ("Bridge - claude personal") runs it independently, re-checking the sha256 first.
