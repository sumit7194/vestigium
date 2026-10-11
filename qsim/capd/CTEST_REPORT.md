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
