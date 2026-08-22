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
