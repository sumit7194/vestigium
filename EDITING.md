# Edits in this repo go through `safe_edit.edit()`

`s.replace(old, new)` returns the string unchanged when the anchor is absent.
That is a **silent no-op with a success message on top**, and it produced three
committed-but-not-applied changes here on 2026-08-22 — one of which shipped a
commit message describing a change that had not happened.

`safe_edit.py` (in the shared coordination directory, written by `thebridge`)
puts the verification inside the call that performs the edit, so the caller does
not *choose* to check — they choose to edit. That is the same move as putting a
null distribution inside the diagnostic that returns the verdict: **the check
rides on an action already being taken for another reason.**

## Validated here before adoption, against this repo's own failures

| failure that actually occurred | result |
|---|---|
| anchor copied from a `sed`-prefixed display, so indentation was wrong | **REFUSED** — anchor not found |
| a loosely-binding ternary evaluating to `s = s` | **REFUSED** — old == new |
| ambiguous anchor matching twice, editing the wrong site *(never hit here, but real)* | **REFUSED** — occurs 2x, expected 1x |
| a valid edit | succeeded, round-trip verified by reading back |

## What it does not close, stated rather than discovered later

The third silent no-op of the day was **an assert that fired while a later
shell invocation committed anyway** — a control-flow gap *between processes*.
`safe_edit` lives inside one process and cannot reach it. That failure is
covered by `.githooks/pre-commit`, which blocks the commit itself.

**Different failure, different ride.** Two mechanisms, neither redundant.


## Model routing (adopted 2026-09-05)

The same rule as the gates — *the cheap check runs first, the expensive one runs on
what the cheap one could not do* — applied to which model does which work.

| tier | use for | why |
|---|---|---|
| **Fable** (heaviest) | hypothesis design; pre-registering the way a test is expected to fail; derivations where a sign or a convention decides the answer (three of this week's errors were exactly that); reading a theorem's *hypotheses*, not its statement; writing the **negative** assertions; judging whether a retraction is over- or under-scoped | these are the steps where a plausible wrong answer survives review |
| **Opus** | synthesising a repo's history from its own docs; findings write-ups; implementing an instrument to a written spec; diagnosing a failing run; extracting equations from a paper | needs judgement, but the target is specified |
| **Sonnet** | literature fetch + extraction against a fixed prompt; capability inventories of sibling repos; log monitoring; running gates and reporting margins; formatting | mechanical, verifiable after the fact |
| **Haiku** | keep-alive ticks; polling | no judgement involved |

Evidence from the day it was adopted: an Opus history pass (~140k tokens) preserved
every caveat the README carries, including recall-check demotions; a Sonnet
capability inventory (~105k tokens) was accurate on tools and interfaces. Watch for the
known failure of the cheap tiers: a summary that *flattens a caveat* — "withdrawn on
provenance" becoming "withdrawn" — which is why write-ups and anything touching the
retraction ledger stay at Opus or above.
