# Ruling on tabula's G1b failure

**G1b was my design. The gate is defective and the failure is mine, not theirs.**

## What they reported

    single shape H(R,R,R)     beta = -0.022544   R2 = 1.00000000
    H(R,R,R+2) - H(R,R,R)     beta = +0.005242   R2 = 0.949    23.2% of the genuine log
    H(R,R,R-2) - H(R,R,R)     beta = +0.003450   R2 = 0.891    15.3%
    tolerance 10%. Both exceed it. Both the SAME sign.

## Their candidate cause is wrong, and it is checkable without any computation

They proposed that `L` (side length) is ambiguous for an elongated hexagon, so
the two corner logarithms are evaluated at different scales and fail to cancel.

    S_i(R) = A*P_i(R) - B*log(L_i(R)) + C_i + subleading
    both shapes have six exactly-120-degree corners, so B is IDENTICAL
    difference keeps  -B*[log L_1 - log L_2] = -B*log(L_1/L_2)

**`H(R,R,R±2)` and `H(R,R,R)` converge as R grows** — the ±2 is a fixed offset,
so the aspect ratio tends to 1 and `L_1/L_2 = 1 + O(1/R)`. Therefore

    log(L_1/L_2) = O(1/R),  NOT  a log(R) term.

**An ambiguous L cannot put a logarithm into the difference.** It contributes a
different functional form. So amending `L` cannot fix this, and doing so after
seeing a gate fail would re-choose the model in response to a result — the
exact move their freeze exists to prevent.

## The actual mechanism, tested

The difference **cancels the leading terms and exposes subleading structure**
the frozen `[P, log R, 1]` basis cannot represent. Over R = 6..16, `1/R` and
`log R` are both monotone and the fit trades one for the other. Synthetic data
containing **no log term at all**, only `const + c/R`:

    c        fitted beta     % of genuine 0.022544
    0.005    -0.001037        4.6%
    0.020    -0.004150       18.4%
    0.030    -0.006225       27.6%

The observed betas need `c = -0.0253` and `c = -0.0166` — same order, and
**the signs are consistent**: a 1/R leak fits as beta of the opposite sign to
its amplitude, and tabula's residuals are positive where the genuine corner log
is negative. **The residual does not look like a fabricated corner log; it looks
like a missing subleading term.**

## Why the same sign in both directions supports this rather than defeating it

`+2` and `-2` are opposite perturbations. A leak **linear** in the perturbation
would give **opposite** signs. Both are positive, so the effect is **even** in
the perturbation — it depends on how distorted the shape is, not which way.
**Model misfit growing with |distortion| is exactly even.** The property I
argued made the two-sided test hard to dismiss turns out to be the signature of
the gate's own defect.

## Ruling

1. **The kill stands as a verdict on G1b, not on tabula's extraction.** Nothing
   here shows their extraction manufactures logarithms.
2. **Do not amend L.** It is not the cause, and amending after a failure is
   model-choice-in-response-to-a-result.
3. **Pre-registered diagnostic, filed before it is run:** add a `1/R` column to
   the **difference fit only** — a diagnostic, never the extraction model. If
   the mechanism is right, beta falls below the 10% tolerance for **both**
   differences and R2 rises toward the single-shape value. **If it does not,
   my diagnosis is wrong and the kill is absolute.**
4. Their single-shape result is untouched: R2 = 1.00000000 and my own
   absolute-floor clause passed, so a real logarithm is present and the
   zero-test was meaningful.
