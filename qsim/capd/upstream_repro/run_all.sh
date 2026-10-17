#!/bin/zsh
# Build and run each upstream reproducer against the installed CAPD 2f06098; record outcomes in run_all.out.
P=$HOME/opt/capd-2f06098-install
CF=($(echo $($P/bin/capd-config --cflags)) -I/opt/homebrew/include)
LF=($(echo $($P/bin/capd-config --libs)) -L/opt/homebrew/lib -lmpfr -lgmp)
for f in A_log_nan B_sin_large C_reg27_mpfr D_parse7 F_mpreal_ctors G_ho_mpfr; do
  echo "=== $f"
  if c++ -std=c++17 -w $f.cpp $CF $LF -o $f 2> $f.build.err; then timeout 600 ./$f; echo "(rc $?)"
  else echo "BUILD FAILED:"; grep -E "error|Undefined|symbol" $f.build.err | head -4 | cut -c1-220; fi
done
