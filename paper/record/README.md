# Chaotic geodesics in the Manko–Novikov spacetime: a computer-assisted proof and a Melnikov theorem (AI-assisted)

**DRAFT record (2026-11-28).** Preprint by Sumit Pal (Independent researcher, ORCID 0009-0000-9541-2793).

## Files in this record
| File | What it is |
|---|---|
| `mn_chaos.pdf` | The paper (6 pages): the theorems, the method, the verification and the limits. |
| `SUMMARY.pdf` | A one-page plain-language summary for non-specialists. |
| `REFEREE_GUIDE.md` | Which file in the software record proves which claim, the order to check them, the expected output lines and the run times. |
| `SHA256SUMS.txt` | SHA-256 checksums of the files above. |

## The code and certificates
The code, specifications, outputs, the second-library checker and the independent field implementation are in the
software record **vestigium v2026.11.28**, doi:10.5281/zenodo.24602464 (all versions: doi:10.5281/zenodo.24602463).
That record supplements this one.

## The claims in one paragraph
- For the Manko–Novikov metric with M = 5, a = 3, at the stated energy level, and with β = 3/100, the return map of
  timelike geodesics has a transversal homoclinic point. This is a computer-assisted proof in interval arithmetic.
  Hence there is a horseshoe and the topological entropy is positive.
- The same holds for every 0 < |β| < β₀, with β₀ not computed. This is a Melnikov theorem with an interval-certified
  coefficient.
- No entropy value is claimed. The flow enclosures rest on one validated integrator (CAPD).

## AI assistance
- This work was carried out with substantial assistance from AI systems, Claude (Anthropic) and Gemini (Google), under
  the author's direction.
- All checks described as independent were done by separate AI sessions or systems; none is human peer review.
- No external expert has yet read the proofs.
