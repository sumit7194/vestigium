# Timer-raise plan for the RUNNING kerr_e chunks (written 2026-11-26; NOT applied; applied only on the Bridge's word)

Written by Quantum-personal (Claude Opus 5.5) at the personal Bridge's request. It follows the 2026-11-25 rescue (prereg "Timer rescue", TheBridge/fleet/kerr_e_timer_rescue_2026-11-25.log), the same method.

## The chunks and their deadlines

All six run with HS_WATCHDOG_S=2592000 (30 d, the parser's maximum on both binaries). The watchdog is a single `alarm()`, set at start. When it fires, the program writes "WATCHDOG TIMEOUT" and exits 124, failing closed.

| Chunk | Machine | PID | Started | Watchdog fires |
|---|---|---|---|---|
| N1N2 | Mac mini | 32284 | 2026-11-26 11:29:59 | 2026-12-26 11:29:59 |
| N2N3 | MacBook Air | 8602 | 12:59:19 | 2026-12-26 12:59:19 |
| N3N4 | MacBook Air | 8615 | 12:59:19 | 2026-12-26 12:59:19 |
| N4N5 | MacBook Air | 8628 | 12:59:19 | 2026-12-26 12:59:19 |
| N5N0 | MacBook Air | 8641 | 12:59:19 | 2026-12-26 12:59:19 |
| N5N1 | MacBook Air | 8654 | 12:59:19 | 2026-12-26 12:59:19 |

The Bridge decides by about day 10, 2026-12-06. A watchdog hit would lose only the piece in progress, since EP records are per piece, but it would still END the job, and under the no-hard-caps rule that must not happen.

## Method (per PID; one at a time; the computation is not touched)

1. Confirm the PID is the chunk, from its command line: binary path plus spec. On the Air, match it with the case-insensitive helper.
2. Send `kill -STOP <pid>` and confirm the state is T. lldb also stops it on attach; the explicit STOP makes the state known before attaching.
3. Run `lldb -p <pid> --batch -o 'expr (unsigned int)alarm(0)' -o 'detach'`.
   - The value printed is the number of seconds that were left on the timer. Log it, and check it against the table (30 d minus the elapsed time).
   - alarm(0) cancels the pending SIGALRM, so no watchdog remains.
4. Send `kill -CONT <pid>`. On 2026-11-25 the dry run showed that detach leaves the process stopped. Then confirm the state is R.
5. Log one line per PID with the time, PID, chunk, seconds left, the alarm(0) result and the state afterwards, in kerr/b15e/timer_raise.log and TheBridge/fleet/.

A dry run on a dummy process comes first on each machine: a sleep binary with alarm(600). It must report about 600 s left, survive past 600 s, and end normally.

The other choice is `alarm(100000000)`, about 3.17 years, which is the macOS maximum; anything larger fails with EINVAL and sets no timer. Proposed: alarm(0), as on 2026-11-25. The process then has no watchdog left, which is the rule's intent.

## Does it need Sumit's password? YES, on both machines, as things stand

Checked 2026-11-26 15:2x, read-only. On both machines `DevToolsSecurity -status` reports "Developer mode is currently disabled", and the user is in `_developer`.

- **Mac mini.** Attaching lldb to a process brings up the macOS admin authorisation dialog (taskgated), as on 2026-11-25, when the Bridge approved the admin prompt. Sumit, or the Bridge with his go, approves it at the Mac mini's screen.
- **MacBook Air.** It is reached over ssh, with no GUI session for the prompt, so an lldb attach over ssh is refused until debugging is authorised. One of these is needed once:
  - (a) Someone at the Air runs `sudo DevToolsSecurity -enable`, with the Air's admin password. lldb attach over ssh then works with no prompt.
  - (b) The five attaches are done in a Terminal at the Air itself, approving each prompt.
- Neither can be done by a Claude session. The password stays with Sumit.

## What this changes

The computation, the outputs and the readings are unchanged. Only the pending alarm is cancelled, as on 2026-11-25.
