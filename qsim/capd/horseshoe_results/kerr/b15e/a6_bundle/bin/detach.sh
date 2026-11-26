#!/bin/bash
# detach.sh LOG CWD CMD [ARGS...] -- start CMD fully detached from the Claude app (memory: run-detached-from-app):
# a NEW SESSION (POSIX::setsid, so it is in its own session and process group, not the app's), stdin from /dev/null,
# stdout+stderr appended to LOG, working directory CWD. The environment of the caller is inherited (set variables
# before the call). Prints the job's PID (perl execs the command, so the PID is the job's). Verify afterwards with
#   ps -o pid,ppid,pgid,sess,command -p PID   (ppid 1 once this shell exits; pgid == pid; sess differs from the shell)
LOG=$1; CWD=$2; shift 2
perl -MPOSIX -e 'POSIX::setsid() != -1 or die "setsid: $!"; open STDIN, "<", "/dev/null"; open STDOUT, ">>", shift @ARGV or die; open STDERR, ">&", \*STDOUT; chdir shift @ARGV or die; exec @ARGV or die "exec: $!"' "$LOG" "$CWD" "$@" &
echo $!
