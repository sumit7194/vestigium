#!/bin/zsh
# Build a PROOF-BEARING CAPD program under the trust-rule-1 guard. Usage: guard_build.sh prog.cpp [out]
#  1. guard compile at -O0 -fno-inline (so template code is emitted as symbols and nm can see it), then
#     check_proof_object.sh: no CAPD interval/vector/matrix/map with a double, long-double or double-interval scalar;
#  2. only if the guard passes: the real -O2 build.
# proof_guard.h (included last by the program) poisons every non-MPFR CAPD type name at compile time.
setopt pipefail
D=${0:A:h}; P=$HOME/opt/capd-2f06098-install
CF=($(echo $($P/bin/capd-config --cflags)) -I/opt/homebrew/include -I$D)
LF=($(echo $($P/bin/capd-config --libs)) -L/opt/homebrew/lib -lmpfr -lgmp)
src=$1; out=${2:-${src:r}}
grep -q '#include "proof_guard.h"' $src || { echo "GUARD FAIL: $src does not include proof_guard.h"; exit 2; }
c++ -std=c++17 -c $src $CF -O0 -fno-inline -o ${out}_guard.o || { echo "GUARD FAIL: guard compile failed"; exit 2; }
$D/check_proof_object.sh ${out}_guard.o || exit 1
c++ -std=c++17 $src $CF $LF -o $out && echo "BUILT $out (guard passed)"
