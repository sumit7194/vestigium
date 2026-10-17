# CAPD upstream posts: what goes where (for the user to post; nothing has been posted)

Repository: https://github.com/CAPDGroup/CAPD (issues tab). Post them in this order. Each file has a **Title** line
(issues only) and a **Body** to paste.

| # | File | Where it goes | What it is |
|---|---|---|---|
| 1 | 01_issueA_log_nan.md | NEW issue | Thanks note plus Issue A: `MpInterval` log of an interval reaching below 0 returns NaN endpoints; the NaN-test macros don't compile or don't fire. Includes the differential-check context. |
| 2 | 02_comment_on_27.md | COMMENT on the existing issue #27 (by kunalsheth) | Issue C: #27 reproduces on the MPFR path too. |
| 3 | 03_issueB_sin_cost.md | NEW issue, cross-referencing #28 | Issue B: MPFR sin/cos argument-reduction cost is linear in \|x\|. |
| 4 | 04_issue_arm64_ctest.md | NEW issue | Issues D and E: three ctest failures on arm64 NATIVE that are test-side. |
| 5 | 05_issue_mpfr_api.md | NEW issue | Issues F and G: undefined MpReal constructors; Hermite–Obreshkov sets don't compile with MPFR. |

Every reproducer was compiled and run on 2026-10-17 against the commit named in each post.
