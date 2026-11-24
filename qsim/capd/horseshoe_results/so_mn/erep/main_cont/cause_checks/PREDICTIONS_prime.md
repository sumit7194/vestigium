# A3 R3a cause checks a′ and b′: predictions, committed BEFORE either check runs (the Bridge's GO, 2026-11-24)

These repair (a)/(b) (RESULTS.md, 5be9f31), whose controls failed because the LINEAR true width was the wrong yardstick
near the thin-width minima. The only change: the true width is now the HULL of the 16 boundary-point images (NB = 4,
DOP853 rtol = atol = 1e-13), the same method as the stored values (tests/b17_checkpoints.py), evaluated through dense
output. Everything else, the hypotheses H1–H4 and the control RULES, is unchanged from PREDICTIONS.md (35741e6), with
w_true now meaning the hull. Diagnostics only; A3's verdict is unchanged. Declared: ≤ 1.5 GB, 1 core, nice 12, about
5–10 min. Written by Claude Opus 5.5 (Quantum).

- **Control a′0:** the hull widths w1 and w2 at the 8 stored time checkpoints match b17_cp_1e-7.txt within 5% (the same
  rule as a0; the same method, so a match far tighter than 5% is expected). If it fails, a′ is VOID.
- **Control b′0:** the state centre matches within 1e-6, and W_poly / w_true(t_k) lies in [0.8, 1.25] at EVERY saved
  state, 792.02 included (the same rule as b0). If it fails, b′'s split is UNRELIABLE.
- **H1/H3 (a′):** the hull w2 has a real, smooth low near 793: w2(793.23) within 5% of 1.895e-7, and w2 within a factor 3
  of it over 793.23 ± 0.5. **H4:** w2(793.23) differs from the stored value by more than 5%, or 793.23 is an outlier.
- **H1 (b′):** no single saved interval holds more than half of the total log growth of W2_E from 292 to 792, and at
  792.02 W2_E > 0.5 × excess, where excess = W_poly + W_E − w_true. **H2:** the 772 → 792 interval holds more than half
  of that log growth, or W2_E jumps by more than 3× between the last two states. **H3:** W_poly / w_true(792.02) > 1.5
  while W_E < 0.5 × excess. If none fits: "cause not identified".
- **Known limit, stated in advance:** DOP853's absolute error (~1e-11) makes the hull noisy where the true width falls
  below ~1e-9 (e.g. near t ≈ 784.5 in (a)'s linear curve). No prediction is made there.
