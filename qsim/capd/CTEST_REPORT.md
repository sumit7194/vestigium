# CAPD 2f06098 (NATIVE intervals, MPFR on) on Apple arm64 / clang 21: full ctest, 2026-10-11

`ctest_full.log` (verbatim): **41 / 44 passed, 3 failed.**

**Passed, including everything rigorous:** CRefTest, functorTest, skipCommentsIstreamTest, TexWriterTest,
IComplexTests, DComplexTests, intvtst, divtst, floatMatrixAlgorithmsTest, matrixMDTest, vectMDTest, vecttst,
vectalgTest, C11vectalgTest, **mpsintest**, **MpIntervalTest**, nonAutTest, BasicCnTaylorTest, diffInclTest,
C2CurveMaskTest, C1CurveMaskTest, CnCurveMaskTest, C1MaskTest, CnMaskTest, C2MaskTest, mapTest, **Rect2SetTest**,
CoordReorganization, **Pped2SetTest**, **C0Pped2SetTest**, **CenteredAffineSetTest**, **DoubletonSetTest**,
**AffineSetTest**, **C0RectSetTest**, **C0PpedSetTest**, FactorReorganization, **SolverGetStepTest**,
**ReversibleSolverTest**, **ReversiblePoincareMapTest**, **CnSolverTest**, MapMaskTest.

## The three failures, verbatim, with analysis

**1. #7 intervalTest: one assertion, in `parse_from_sstream`.**

    intervalTest.cpp:97: error: in "parse_from_sstream": difference{2.05392e-16} between a.rightBound(){4.3243243240000009} and 4.324324324{4.324324324} exceeds 0%

- The test parses "[3.21312312, 4.324324324]" into a DOUBLE interval and expects rightBound == the double nearest to
  4.324324324, with 0% tolerance.
- Exact arithmetic (Python Decimal): the nearest double is 4.32432432399999999717…, which is BELOW the decimal. A
  rigorous enclosure must therefore have rightBound = the next double up, 4.32432432400000088534…, and that is
  exactly what CAPD returned.
- **CAPD's arm64 result is the correct outward rounding. The test's expected value would EXCLUDE the true decimal.**
  This is a non-rigorous assertion in the test, not a CAPD defect. (The test presumably passes under filib on x86
  because that path rounds to nearest when parsing.)

**2. #43 DPoincareMapMaskTest: 10 failures, in `xCnTest` and `xNormalFormTest`.** The test uses `DMap`, i.e.
NON-RIGOROUS double arithmetic, with tol = 1e−12 (1e−14 for the normal form). The observed differences are
1.07e−12 to 2.05e−12, and 1.56e−14. That is last-bit variation, plausibly from FMA contraction or libm differences
on arm64. No interval or enclosure is involved.

**3. #44 SingularNaturalPowerTest: 313 assertion lines, in `xCnTest`.** The test uses `LDVector`, i.e. **long double**
(non-interval), with tol = 1e−13. On x86, long double is 80-bit extended; on Apple arm64, **long double is plain
64-bit double**. The observed differences, 1.1e−13 to 7e−13 (and one 1.46e−11), are consistent with losing the
extended precision the tolerance assumed. No interval or enclosure is involved.

## Reading against the trust rules

- No failure involves an interval enclosure being wrong, MPFR, or a rigorous ODE or Poincaré enclosure. All of
  those tests pass.
- Failure 1 is literally in an "interval test", but CAPD's output is provably the rigorous one.
- The ruling is the bridge's. These findings are also candidates for an upstream report, which the user would
  send.

## Bridge ruling (2026-10-11): build ACCEPTED

The bridge independently verified #7. #43 and #44 are non-rigorous tolerance tests and don't count against the
build. The bridge's condition: the compile-time guard must also exclude DMap, long-double and every non-interval
type.

**#7, both bounds checked exactly** (`tests/parse7.cpp`; CAPD's own parse, printed as hex floats):

| decimal | CAPD bound | checked |
|---|---|---|
| 3.21312312 (left) | 0x1.9b479e4f35f32p+1 = 3.21312311999999966616… | ≤ decimal, and the next double up is ≥ decimal: the **largest double ≤ the decimal** |
| 4.324324324 (right) | 0x1.14c1bacf3825ep+2 = 4.32432432400000088534… | ≥ decimal, and the next double down is ≤ decimal: the **smallest double ≥ the decimal** |

So CAPD's parsed interval is the **tightest possible enclosure** of the decimal input, on both sides. The test's
expected rightBound (the nearest double, 4.32432432399999999717…) would exclude the decimal.

## Regression tests for open upstream issues (`tests/reg27.cpp`, `tests/reg28.cpp`), 2026-10-11

**#28, interval sin on large point arguments** (5 s timeout each; a hang is recorded as a failure):

| argument | double NATIVE | **MPFR (MpInterval, 256 bits)** |
|---|---|---|
| ±1e3 … 1e12 | — | **correct enclosures** (true sin from mpmath at 40 digits lies inside every printed interval) |
| 1e13, 3e13, 1e14, 3e14, 1e15, 1e18, 1e20 | — | **NO RESULT (hang)** |
| −5.7e19 | [-1,1] | **hang** |
| −5.8e19, −1e20 | **hang** (reproduces #28) | **hang** |
| +1e20 | [-1,1] | **hang** |

- **New finding: on the MPFR path, which is the one we use, sin hangs for |x| ≳ 1e13**, including POSITIVE
  arguments. That is worse than the double path in #28.
- It is a liveness failure, not a wrong enclosure: every result returned was correct.
- Our planned proofs use no trigonometry (TS δ=2 and Kerr are rational, Hénon–Heiles is polynomial). Any future
  use of trig in proof code must keep arguments far below 1e12. To be added to the upstream report.

**#27, thin initial set at an equilibrium** (x' = 10(1−x), x(0) = 1; t = 0.05):

| set | double IOdeSolver | MPFR MpIOdeSolver |
|---|---|---|
| point [1, 1] | THROW "minimal time step reached" | **THROW "minimal time step reached"** |
| [1 − ulp, 1] | x(0.05) ∈ [0.999999, 1.00001] | x(0.05) ∈ [0.999999, 1.00001] |

- #27 reproduces on BOTH paths: the solver fails on a degenerate point set at an equilibrium and works one ulp
  wider. It throws (fails loudly), so it is not a silent error.
- Our h-sets and boxes are never degenerate points. Recorded as a known limitation.
