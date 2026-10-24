#!/bin/bash
# kerr_build.sh -- the ONLY sanctioned build of the B15b compiled maps (kerr_rs, kerr_p.dylib), with provenance.
# Fails if any fast-math style option or intrinsic is present (it would reorder or contract float operations and
# silently void every B15b gate): -ffast-math, -Ofast, -funsafe-math-optimizations, -fassociative-math,
# -freciprocal-math, -fno-signed-zeros, -ffinite-math-only in the C++ flags or source pragmas; RUSTFLAGS that are
# not empty; Rust fast/algebraic float intrinsics in the source. Records the toolchains, flags, the C++
# floating-point contraction setting (clang's default -ffp-contract=on permits FMA within an expression: IEEE-legal,
# not fast-math, but a real difference from Rust, which never contracts), and the sha256 of every source and output.
# Writes kerr_build_provenance.json.
set -euo pipefail
cd "$(dirname "$0")"
CXXFLAGS="-std=c++17 -O2 -shared -fPIC"
BAD='ffast-math|Ofast|funsafe-math|fassociative-math|freciprocal-math|fno-signed-zeros|ffinite-math-only'
if echo "$CXXFLAGS" | grep -Eq -- "$BAD"; then echo "BUILD REFUSED: fast-math flag in CXXFLAGS"; exit 1; fi
if grep -Eq "pragma.*(float_control|fp_contract|clang fp|GCC optimize)|$BAD" kerr_p.cpp gen/mn_field.h; then echo "BUILD REFUSED: float pragma or fast-math in C++ source"; exit 1; fi
if [ -n "${RUSTFLAGS:-}" ] || [ -n "${CARGO_ENCODED_RUSTFLAGS:-}" ]; then echo "BUILD REFUSED: RUSTFLAGS set"; exit 1; fi
if grep -Eq "_fast\(|fadd_fast|fmul_fast|fsub_fast|fdiv_fast|algebraic_|mul_add|core::intrinsics" kerr_rs/src/*.rs; then echo "BUILD REFUSED: Rust fast/algebraic/fused float operation in source"; exit 1; fi
if grep -Eq "rustflags|target-cpu|fast" kerr_rs/Cargo.toml; then echo "BUILD REFUSED: codegen flags in Cargo.toml"; exit 1; fi
[ -e kerr_rs/.cargo/config.toml ] && { echo "BUILD REFUSED: kerr_rs/.cargo/config.toml present"; exit 1; }
(cd kerr_rs && cargo build --release 2>&1 | grep -E "^(warning|error)|Finished")
c++ $CXXFLAGS -I/opt/homebrew/include kerr_p.cpp -o kerr_p.dylib.new && mv kerr_p.dylib.new kerr_p.dylib
sha() { shasum -a 256 "$1" | cut -c1-64; }
cat > kerr_build_provenance.json <<EOF
{
 "date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
 "git_head": "$(git rev-parse HEAD)",
 "rustc": "$(rustc -V)",
 "cargo": "$(cargo -V)",
 "rust_target": "$(rustc -vV | sed -n 's/^host: //p')",
 "rust_profile": "release: opt-level 3, codegen-units 1, lto true, strip false (Cargo.toml); RUSTFLAGS empty",
 "cxx": "$(c++ --version | head -1)",
 "cxx_flags": "$CXXFLAGS",
 "cxx_fp_contract": "clang default (-ffp-contract=on: FMA within an expression permitted); not fast-math",
 "fast_math_check": "passed (flags, pragmas, intrinsics, Cargo.toml, .cargo/config)",
 "sha256": {
  "kerr_rs/src/lib.rs": "$(sha kerr_rs/src/lib.rs)", "kerr_rs/src/dopri5.rs": "$(sha kerr_rs/src/dopri5.rs)",
  "kerr_rs/src/scalar.rs": "$(sha kerr_rs/src/scalar.rs)", "kerr_rs/src/mn_field.rs": "$(sha kerr_rs/src/mn_field.rs)",
  "kerr_rs/Cargo.toml": "$(sha kerr_rs/Cargo.toml)", "kerr_rs/Cargo.lock": "$(sha kerr_rs/Cargo.lock)",
  "kerr_p.cpp": "$(sha kerr_p.cpp)", "gen/mn_field.h": "$(sha gen/mn_field.h)",
  "libkerr_rs.dylib": "$(sha kerr_rs/target/release/libkerr_rs.dylib)", "kerr_p.dylib": "$(sha kerr_p.dylib)"
 }
}
EOF
echo "built; provenance in kerr_build_provenance.json"
