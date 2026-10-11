#!/bin/zsh
# Layer 2 of the guard: the proof object file must not reference any CAPD template instantiated on double,
# long double or a double interval as its SCALAR type (interval/vector/matrix/map element types; member templates
# of MPFR types taking a double argument, e.g. MpInterval::contains<double>, are exact conversions and allowed). FAILS CLOSED: a missing or unreadable
# file, or nm failing, is a GUARD FAIL. Usage: check_proof_object.sh file.o
setopt pipefail
[ -f "$1" ] || { echo "GUARD FAIL: $1 does not exist"; exit 2; }
syms=$(nm -C "$1" 2>&1) || { echo "GUARD FAIL: nm failed on $1"; echo "$syms" | head -3; exit 2; }
[ -n "$syms" ] || { echo "GUARD FAIL: nm returned no symbols for $1"; exit 2; }
bad=$(print -r -- "$syms" | grep -E "capd::" | grep -E "Interval<double|Interval<long double|Vector<double|Vector<long double|Matrix<double|Matrix<long double|Map<capd::vectalg::Matrix<double|Map<capd::vectalg::Matrix<long double" | head -20)
if [ -n "$bad" ]; then echo "GUARD FAIL: non-MPFR CAPD instantiations in $1:"; echo "$bad"; exit 1; fi
echo "GUARD OK: $1 has no double, long-double or double-interval CAPD instantiations"
