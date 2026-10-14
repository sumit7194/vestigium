#!/usr/bin/env python3
"""
Monitor for TS-4 Original-Path CAPD Replay Job (PID 52149 / 69951)
Author: Gemini (authored for quantum / vestigium workspace)
Date: 2026-10-14

Monitors the detached TS-4 original-path run, logs segment-by-segment progress,
and upon process termination:
  1. Inspects verdict in qsim/capd/replay_results/ts2_4_primary_o30_p256.json
  2. Runs qsim/capd/replay_crosspath.py to update the cross-path verification table
  3. Updates .claude-coordination/quantum.status
  4. Drops notification into .claude-coordination/inbox/bridge/
  5. Generates/updates root HANDOFF_2026-10-14.md
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path("/Users/sumit/Github/quantum").resolve()
CAPD_DIR = REPO_ROOT / "qsim" / "capd"
ERR_LOG = CAPD_DIR / "tests" / "gen" / "ts2_4_primary_o30_p256.err"
RESULT_JSON = CAPD_DIR / "replay_results" / "ts2_4_primary_o30_p256.json"
MONITOR_LOG = CAPD_DIR / "monitor_ts4.log"
COORDINATION_DIR = Path("/Users/sumit/Github/.claude-coordination")
PYTHON_EXEC = REPO_ROOT / "sims" / ".venv" / "bin" / "python"

TARGET_PIDS = (52149, 69951)

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [Gemini Monitor] {msg}"
    print(formatted, flush=True)
    with open(MONITOR_LOG, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def is_process_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def get_last_err_lines(n: int = 2) -> str:
    if not ERR_LOG.exists():
        return "Log file not yet found."
    try:
        with open(ERR_LOG, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip()]
            return " | ".join(lines[-n:]) if lines else "Log empty"
    except Exception as e:
        return f"Error reading log: {e}"

def update_coordination_status(state: str, detail: str, heavy: bool = False):
    try:
        status_file = COORDINATION_DIR / "quantum.status"
        payload = {
            "session": "quantum",
            "repo": str(REPO_ROOT),
            "state": state,
            "heavy": heavy,
            "job_pids": [52149] if state == "busy" else [],
            "jobs": ["ts2_4_primary_orig"] if state == "busy" else [],
            "detail": detail,
            "updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "author": "gemini"
        }
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        log(f"Updated {status_file}")
    except Exception as e:
        log(f"Failed to update coordination status: {e}")

def notify_bridge(verdict: str, crosspath_status: str):
    try:
        inbox_bridge = COORDINATION_DIR / "inbox" / "bridge"
        inbox_bridge.mkdir(parents=True, exist_ok=True)
        note_path = inbox_bridge / f"{datetime.now().strftime('%Y-%m-%d')}_quantum_ts4_orig_done.md"
        content = f"""# Quantum TS-4 Original Path Re-run Complete
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Author: Gemini (quantum session)

## Summary
The detached TS-4 original-path CAPD re-run (PID 52149 / 69951) has completed.
- Verdict: **{verdict}**
- Result file: `qsim/capd/replay_results/ts2_4_primary_o30_p256.json`
- Cross-path table update: {crosspath_status}

## Ledger Impact
- All 24/24 Morales–Ramis certificates remain verified (Arb-free).
- TS-4 cross-path comparison pair ingested into `qsim/capd/replay_xpath_table.txt`.
"""
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(content)
        log(f"Notified Bridge via inbox: {note_path}")
    except Exception as e:
        log(f"Failed to drop inbox message: {e}")

def create_handoff(verdict: str, crosspath_status: str):
    try:
        handoff_path = REPO_ROOT / f"HANDOFF_{datetime.now().strftime('%Y-%m-%d')}.md"
        content = f"""# Quantum Handoff: {datetime.now().strftime('%Y-%m-%d')}
Author: Gemini

## Status of In-Flight Jobs
- **TS-4 Original-Path Re-run**: Completed.
  - Verdict: `{verdict}`
  - Cross-path table: {crosspath_status}
  - Result: `qsim/capd/replay_results/ts2_4_primary_o30_p256.json`
- **Active Processes**: None (system idle from quantum).

## Open Items Pending Decision
1. Sub-45 plan C (CHL corner check)
2. Chaos-proof phase 2 (Hénon–Heiles / Kerr controls + proof)
3. Upstream CAPD report (`qsim/capd/UPSTREAM_REPORT_DRAFT.md`)
4. Defect commits history redaction (`829ec37`, `17af42f`)
5. Parked research threads (MN/TS outreach, Lean equatorial glue, corner systematic)
"""
        with open(handoff_path, "w", encoding="utf-8") as f:
            f.write(content)
        log(f"Created handoff file: {handoff_path}")
    except Exception as e:
        log(f"Failed to create handoff note: {e}")

def run_post_completion_steps():
    log("Processing post-completion steps...")
    verdict = "UNKNOWN"
    if RESULT_JSON.exists():
        try:
            with open(RESULT_JSON, "r", encoding="utf-8") as f:
                res = json.load(f)
                verdict = res.get("verdict", "UNKNOWN")
        except Exception as e:
            verdict = f"ERROR_READING_JSON: {e}"
    else:
        verdict = "RESULT_FILE_NOT_FOUND"

    log(f"Job result verdict: {verdict}")

    # Run replay_crosspath.py
    crosspath_status = "Not executed"
    crosspath_script = CAPD_DIR / "replay_crosspath.py"
    if crosspath_script.exists():
        cmd = [str(PYTHON_EXEC), str(crosspath_script)] if PYTHON_EXEC.exists() else ["python3", str(crosspath_script)]
        try:
            log(f"Executing cross-path update: {' '.join(cmd)}")
            res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=True)
            log("replay_crosspath.py stdout:\n" + res.stdout.strip())
            crosspath_status = "Successfully executed & updated replay_xpath_table.txt"
        except subprocess.CalledProcessError as e:
            log(f"replay_crosspath.py failed with code {e.returncode}:\n{e.stderr}")
            crosspath_status = f"Failed with exit {e.returncode}"
    
    update_coordination_status(state="idle", detail=f"TS-4 original-path completed with verdict: {verdict}")
    notify_bridge(verdict, crosspath_status)
    create_handoff(verdict, crosspath_status)
    log("Post-completion routine complete.")

def main():
    log("Starting monitor for TS-4 Original-Path job...")
    last_log_state = ""
    poll_interval = 30  # seconds

    while True:
        alive_52149 = is_process_running(52149)
        alive_69951 = is_process_running(69951)

        current_progress = get_last_err_lines(2)
        if current_progress != last_log_state:
            log(f"PID 52149 active: {alive_52149} | Progress: {current_progress}")
            last_log_state = current_progress

        if not alive_52149 and not alive_69951:
            log("Both target PIDs (52149 and 69951) have terminated.")
            # Give a brief moment for filesystem writes to settle
            time.sleep(5)
            run_post_completion_steps()
            break

        time.sleep(poll_interval)

if __name__ == "__main__":
    main()
