#!/usr/bin/env python3
# Read-only P-core share of given PIDs (the personal Bridge's yes, 2026-11-27): proc_pid_rusage(RUSAGE_INFO_V6) twice,
# GAP seconds apart. No sudo, no signals, nothing written except stdout. Each PID's argv must contain REQUIRE or it is
# skipped. Fields read (sys/resource.h rusage_info_v6): user/system time, user/system ptime (time on performance cores),
# instructions/pinstructions, cycles/pcycles, runnable_time (reported raw; whether it includes running time is not documented). Times are mach absolute units, converted with
# mach_timebase_info. Written by Claude Opus 5.5 (Quantum-personal). Usage: pcore_read.py GAP REQUIRE PID...
import ctypes, subprocess, sys, time

F = ["user_time", "system_time", "pkg_idle_wkups", "interrupt_wkups", "pageins", "wired_size", "resident_size",
     "phys_footprint", "proc_start_abstime", "proc_exit_abstime", "child_user_time", "child_system_time",
     "child_pkg_idle_wkups", "child_interrupt_wkups", "child_pageins", "child_elapsed_abstime", "diskio_bytesread",
     "diskio_byteswritten", "qos_default", "qos_maintenance", "qos_background", "qos_utility", "qos_legacy",
     "qos_user_initiated", "qos_user_interactive", "billed_system_time", "serviced_system_time", "logical_writes",
     "lifetime_max_phys_footprint", "instructions", "cycles", "billed_energy", "serviced_energy",
     "interval_max_phys_footprint", "runnable_time", "flags", "user_ptime", "system_ptime", "pinstructions", "pcycles"]

class RU(ctypes.Structure):
    _fields_ = [("uuid", ctypes.c_uint8 * 16)] + [(n, ctypes.c_uint64) for n in F] + [("rest", ctypes.c_uint64 * 32)]

class TB(ctypes.Structure):
    _fields_ = [("numer", ctypes.c_uint32), ("denom", ctypes.c_uint32)]

libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
tb = TB(); libc.mach_timebase_info(ctypes.byref(tb)); NS = tb.numer / tb.denom

def read(pid):
    r = RU()
    if libc.proc_pid_rusage(pid, 6, ctypes.byref(r)) != 0:
        return None
    return {n: getattr(r, n) for n in ("user_time", "system_time", "user_ptime", "system_ptime", "instructions",
                                        "pinstructions", "cycles", "pcycles", "runnable_time")}

gap, req, pids = int(sys.argv[1]), sys.argv[2], [int(p) for p in sys.argv[3:]]
ok = []
for p in pids:
    a = subprocess.run(["ps", "-o", "command=", "-p", str(p)], capture_output=True, text=True).stdout.strip()
    if req in a: ok.append((p, a.split()[-1].split("/")[-1]))
    else: print(f"SKIP {p}: argv '{a[:80]}' lacks '{req}'")
print(time.strftime("%F %T"), f"timebase {tb.numer}/{tb.denom}; gap {gap} s; pids {[p for p, _ in ok]}")
r0 = {p: read(p) for p, _ in ok}; t0 = time.time()
time.sleep(gap)
r1 = {p: read(p) for p, _ in ok}; t1 = time.time()
print(time.strftime("%F %T"), f"elapsed {t1 - t0:.1f} s")
print("pid spec | lifetime: cpu_s pcore_share | interval: cpu_s pcore_share runnable_time_s GHz_all GHz_P GHz_E IPC_P IPC_E")
for p, spec in ok:
    a, b = r0[p], r1[p]
    if a is None or b is None: print(f"{p} {spec} READ-FAILED"); continue
    cpu = lambda r: (r["user_time"] + r["system_time"]) * NS / 1e9
    pt = lambda r: (r["user_ptime"] + r["system_ptime"]) * NS / 1e9
    dc, dp = cpu(b) - cpu(a), pt(b) - pt(a); de = dc - dp
    dcy, dpcy = b["cycles"] - a["cycles"], b["pcycles"] - a["pcycles"]
    din, dpin = b["instructions"] - a["instructions"], b["pinstructions"] - a["pinstructions"]
    dwait = (b["runnable_time"] - a["runnable_time"]) * NS / 1e9
    f = lambda x, y: f"{x / y:.2f}" if y > 0 else "-"
    print(f"{p} {spec} | {cpu(b):.0f} {f(pt(b), cpu(b))} | {dc:.1f} {f(dp, dc)} {dwait:.1f} "
          f"{f(dcy / 1e9, dc)} {f(dpcy / 1e9, dp)} {f((dcy - dpcy) / 1e9, de)} {f(dpin, dpcy)} {f(din - dpin, dcy - dpcy)}")
