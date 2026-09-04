# Handoff — paused 2026-09-05, resume in the morning

State at pause: `cbc5fe0` on `main`, pushed. Tree clean. Gate green, **58 assertions,
23 negative**. Nothing running from this repo. Keep-alive stopped (see §6).

---

## 1. What happened over the last three days

**09-02 — the LRL method-validation task.** Built `qsim/lrl_secular.py` to test the
secular-average lemma (*if `Q` survives to first order, the orbit average
`A = ⟨{H₁,Q}⟩` must vanish*) on Kepler with the Laplace–Runge–Lenz vector. Two
averaging routes sharing no code path agree to `1.5e-10`. All three controls pass —
the trivial one (same system reparametrised) averages to `1e-15` **while its bracket
is nonzero pointwise by up to 11.0**, which is what makes it a control rather than
decoration. Four findings not in the framing: `A_x ≡ 0` by parity for every central
perturbation; `A` is **minus** the secular rate; the integral is **absolutely**
convergent (convergence is not where the problem is); and the load-bearing gap is the
**bounded-`F₁`** step, which holds per orbit but is applied on an open set and is not
uniform there. Window: `(εβ)/(ka) < 0.29 e(1−e)`, vanishing at both ends.
→ `qsim/LRL_FINDINGS.md`, gate `qsim/lrl_gate.py` (12 assertions).

**09-04 — an outside workspace found `a(120°)` violating a theorem, and it was right.**
The committed `0.0038956` sits **13.3 % below** the BWK16 bound `(π²C_T/3)log[1/sin(θ/2)]`,
which has no fitted parameter. Diagnosed: `ξ/N = 0.62`, so the **box, not the mass**,
was the IR cutoff, and the fit window `R = 4..14` sat in lattice corrections. Corrected
`a(120°) = 0.004465` measured (**+14.6 %**), `0.0044915` extrapolated — `0.9992×` the
bound, still marginally below, while the 4-param fit measures `1.0054×` above. **The
honest verdict is the bracket, not a pass**: consistent with the bound at the level the
method resolves. `a(60°)` 0.0242324 → 0.0256670 (+5.9 %) confirms on a different angle
and shape. → `qsim/CORNER_BOUND_FINDINGS.md`.

**09-04 — imported and *checked* an outside result.** `corner_function/` (κ
non-localisation: C1–C6 do not bound `κ/C_T`). All three requested checks pass; two
documentation errors found that the proof does not use; `κ/C_T` reaches `8.4e64` under
the constraints. Literature sweep on the two routes a missing constraint could have
entered — **neither exists**. → `corner_function/PROVENANCE.md`.

**09-05 — hygiene, currency, and two self-caught defects.** Public-repo audit: no
prior-art PDF is tracked and none ever was; no personal data; none of the off-limits
project names appear. **Three of eight arXiv IDs I wrote from memory were wrong** and
were caught by cross-checking the imported verified bibliography before they went
public. Then `regime_gate.py`, and the finding in §3 below.

---

## 2. The pattern worth carrying forward

Five times this week a **measurement held and its summary statistic carried a
parameter that was held fixed and never varied**:

| # | the number | the axis never varied |
|---|---|---|
| 1 | LRL window quoted as `ε < 0.37 e(1−e)` | `a` — it was an `a = 1.3` scan |
| 2 | corner uncertainty quoted as 1.85 % | all four regulators shared one `(N, m, window)` |
| 3 | "bound satisfied" | `r = 3.1` imported from a different window (measured: 4.56) |
| 4 | `ξ/L ≈ 2.5` on the chain | region scale is locked to `L`; it is a composite |
| 5 | the s-family's `s⁻²` law | `ξ/L = 0.625` fixed at every `s`, by construction |

**#2 was diagnosed in someone else's number and #3 committed in the same session.**
#5 is the worst to notice because the fixed axis is *required* by the study's own logic —
correct design is what makes the blindness invisible.

Second pattern: the **gate caught the same "check that cannot fire" mistake from me
twice in one day** (`>0.0` bars giving infinite margins). The machinery earns its keep;
attention to its output did not.

---

## 3. Newest finding, still warm

`regime_gate.py` (built 09-05, costs microseconds) encodes `R ≪ ξ ≪ L`. Run against
**already-committed** studies it found both `corner_s1` and `corner_s6` outside the
window on the `ξ/L` axis at **0.625** — the same ratio that put `a(120°)` under the
theorem. That is the design (`L = L_base·s`, `m = m_base/s` fixes every dimensionless
ratio), so the finding is not "run wrong" but **"cannot detect a box systematic,
because it never varies the axis carrying one."**

**Does not overturn:** the s-scan publishes regulator *spreads*, and a systematic
common to all four regulators cancels in a spread. **Not supported:** reading "the
spread falls as `s⁻²`" as "the coefficient converges to its universal value."

---

## 4. First things to pick up in the morning

1. **Decide on `PROPOSALS.md`** — three pre-registered hypotheses, none run.
   - **H1** (primary): point the validated LRL instrument at ansatz's own open item,
     *"deformed-Kerr integrability fate: UNDETERMINED"* (their symbolic search swamped
     at 7.5 h). Includes their weeks-old **rank-3** Killing tensor — is higher-rank
     hidden symmetry more fragile than rank 2? Three controls, three cross-oracle
     routes, four named failure modes. ~1 day to implement; runs are CPU-light.
   - **H2** (nearly free, **time-sensitive**): tabula is sweeping mass now. Sealed
     prediction `ξ/L ≈ 2.5`, and it should *not* move between `c = ½` and `c = 1`.
     **This decays in value once their sweep reports** — file it first or not at all.
   - **H3**: the founding question. Darwinism redundancy in a *critical* environment
     should carry a log correction with coefficient fixed by `c`. No sister can test it.
2. **The open question I put to the user and which is still open:** the founding
   question ("when does a quantum possibility become a fact?") got a complete verified
   lab in the founding commit of 2026-07-26 and has been dormant since 08-22. The repo
   has become the fleet's verification instrument. **Redirection or forgetting is the
   user's call, not mine** — nothing should be decided on this without them.
3. Longer-standing and unrun: the **fifth out-of-family regulator**
   `m² + K2 + c(K4 − K2)`, still the right test for the bulk-coupling residual.

---

## 5. Standing constraints

- **ansatz's PID 1655** — a 12+ hour job, ~9 h remaining at last report. *Do not touch.*
  H1 explicitly waits for it. Announce any heavy run with PID + argv + duration; check
  `preflight.py` first; size against **free**, not available.
- **Never `pkill -f <generic word>`** — it is a broadcast on a shared box. Kill by PID
  from the pidfile. Discover with a character class (`grep '[c]onjecture_machine'`),
  never `grep -v grep`, which deletes other sessions' monitors.
- **Off-limits repos** (verify by cwd, not name prefix; treat the list as incomplete):
  `telos`, `eduspace`, `eduvizio*`, `otr.io`.
- **Each session checks its own repo** and answers the bridge itself. Reading a
  sister's files to characterise their work is out of remit — I did it once and was
  corrected. *Accurate and out-of-remit are compatible.*
- Model routing is in `EDITING.md` (Fable for design and failure modes; Opus for
  write-ups and implementation; Sonnet for fetch/inventory; Haiku for ticks).

## 6. Keep-alive — stopped, and how to restart

Both halves are down: the tick cron is cancelled and the writer process stopped by PID
from its pidfile. `quantum.status` will go stale after 300 s, so sisters read this
session as **unknown** rather than idle — the honest signal once the session is not
being watched, and the default their own protocol specifies.

To bring it back in the morning:

```bash
cd /Users/sumit/Github/quantum && ./vestigium_wr_9f2a4c.sh &
```

and ask for the tick job to be recreated (`17,47 * * * *`, session-only, 7-day expiry).
