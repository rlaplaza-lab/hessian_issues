# FairChem-Core Regression Analysis: Comprehensive Version Comparison

This document provides a comprehensive analysis of Hessian computation accuracy across multiple fairchem-core versions, identifying regressions introduced between version 2.7.1 (baseline) and 2.11.0.

## Executive Summary

Testing across 9 example systems reveals significant regressions in fairchem-core versions 2.8.0 and later, with the most severe issues affecting small molecules (3-5 atoms). The regression appears to have been partially mitigated in version 2.11.0 for some examples, but critical issues persist.

**Key Findings:**
- **Critical failures** in examples 3 and 7 (distorted methane and equilibrium water) in versions 2.8.0 and 2.10.0 - Hessian computation produces NaN values causing all methods to fail
- **Critical regressions** in examples 3 and 7 in version 2.11.0 with RMS errors increasing by 400-600x compared to baseline
- **Moderate regressions** in examples 5 and 6
- **Minor regressions** in examples 1 and 9
- **Example 8** runs successfully across all versions (previously reported as failed due to parsing issues, now resolved)
- **Examples 2 and 4** remain unaffected across all versions

## Summary: RMS Error Comparison Across Versions

| Example | Structure | Atoms | v2.7.1 RMS | v2.8.0 RMS | v2.10.0 RMS | v2.11.0 RMS | Max Increase | Status |
|---------|-----------|-------|------------|------------|-------------|-------------|--------------|--------|
| **example_3** | example_3.xyz | 5 | **0.158** | **FAILED** | **FAILED** | **67.839** | **429x** | 🔴 **CRITICAL** |
| **example_7** | example_7.xyz | 3 | **0.041** | **FAILED** | **FAILED** | **25.510** | **622x** | 🔴 **CRITICAL** |
| example_5 | example_5.xyz | 12 | 0.001 | 0.179 | 0.179 | 0.179 | 179x | 🟡 Moderate |
| example_6 | example_6.xyz | 3 | 0.000 | 0.212 | 0.212 | 0.212 | ∞ | 🟡 Moderate |
| example_1 | example_1.xyz | 51 | 0.000 | 0.013 | 0.013 | 0.013 | ∞ | 🟢 Minor |
| example_9 | example_9.xyz | 3 | 0.000 | 0.029 | 0.029 | 0.029 | ∞ | 🟢 Minor |
| example_2 | example_2.xyz | 3 | 0.001 | 0.001 | 0.001 | 0.001 | 1x | ✅ OK |
| example_4 | example_4.xyz | 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0x | ✅ OK |
| example_8 | example_8.xyz | 5 | 0.001 | 0.122 | 0.122 | 0.122 | 122x | 🟡 Moderate |

**Note:** Examples 3 and 7 fail in versions 2.8.0 and 2.10.0 because Hessian computation produces NaN values (all 225 elements for example_3, all 81 elements for example_7), causing eigenvalue computation to fail. Version 2.11.0 computes Hessians but with massive errors.

## Critical Failures: NaN Values in Hessian Computation

### Root Cause Analysis

In versions 2.8.0 and 2.10.0, examples 3 and 7 fail completely because the Hessian computation produces NaN (Not a Number) values for all matrix elements:

- **Example 3:** All 225 elements (15×15 matrix) are NaN
- **Example 7:** All 81 elements (9×9 matrix) are NaN

This occurs across **all Hessian computation methods** (`double_backward`, `vmap`, `fairchem`, `fairchem_loop`), indicating a fundamental issue in the underlying computation rather than a method-specific bug.

**Technical Details:**
- The NaN values are detected before eigenvalue computation
- Eigenvalue computation fails with `LinAlgError: Eigenvalues did not converge` when attempting to process NaN-containing matrices
- The issue is not CUDA cache-related; clearing cache does not resolve it
- Version 2.11.0 fixes the NaN issue but introduces massive numerical errors instead

**Possible Causes:**
- Division by zero in autograd computation paths
- Numerical instability in gradient/hessian computation for small systems
- Changes to tensor operations or dtype handling between 2.7.1 and 2.8.0
- Issues with batch processing or vectorization for small molecules

## Critical Offenders (RMS Error > 10 eV/Å²)

### 🔴 Example 3: Distorted Methane (5 atoms)

**Baseline (2.7.1):**
- RMS = 0.158 eV/Å²
- MAE = 0.085 eV/Å²
- Max = 0.515 eV/Å²
- Best method: `double_backward` (sym)

**Regression (2.11.0):**
- RMS = **67.839 eV/Å²** (429x increase)
- MAE = **12.899 eV/Å²** (152x increase)
- Max = **360.151 eV/Å²** (699x increase)
- Best method: `vmap` (no-sym)

**Impact:**
- This is a **distorted geometry** test case designed to test Hessian accuracy on non-equilibrium structures
- The massive error increase makes Hessian computations unreliable for transition states and distorted geometries
- All methods show severe degradation in 2.11.0

**Version Timeline:**
- 2.7.1: ✅ Baseline (RMS = 0.158)
- 2.8.0: 🔴 **FAILED** - Hessian computation produces NaN values (all 225 elements are NaN), causing all methods to fail
- 2.10.0: 🔴 **FAILED** - Hessian computation produces NaN values (all 225 elements are NaN), causing all methods to fail
- 2.11.0: 🔴 Critical regression (RMS = 67.839) - Hessian computation succeeds but with massive errors

### 🔴 Example 7: Equilibrium Water (3 atoms)

**Baseline (2.7.1):**
- RMS = 0.041 eV/Å²
- MAE = 0.019 eV/Å²
- Max = 0.137 eV/Å²
- Best method: `fairchem` (no-sym)

**Regression (2.11.0):**
- RMS = **25.510 eV/Å²** (622x increase)
- MAE = **8.036 eV/Å²** (423x increase)
- Max = **81.313 eV/Å²** (593x increase)
- Best method: `fairchem_loop` (no-sym)

**Impact:**
- This is an **equilibrium geometry** test case, showing the regression affects both equilibrium and distorted structures
- The error is catastrophic for a simple 3-atom system
- This suggests fundamental issues with small molecule handling in newer versions

**Version Timeline:**
- 2.7.1: ✅ Baseline (RMS = 0.041)
- 2.8.0: 🔴 **FAILED** - Hessian computation produces NaN values (all 81 elements are NaN), causing all methods to fail
- 2.10.0: 🔴 **FAILED** - Hessian computation produces NaN values (all 81 elements are NaN), causing all methods to fail
- 2.11.0: 🔴 Critical regression (RMS = 25.510) - Hessian computation succeeds but with massive errors

## Moderate Impact (RMS Error 0.1 - 10 eV/Å²)

### 🟡 Example 5: Transition State Structure (12 atoms)

**Baseline (2.7.1):**
- RMS = 0.001 eV/Å²
- Best method: `double_backward_float64` (sym)

**Regression (2.11.0):**
- RMS = 0.179 eV/Å² (179x increase)
- Best method: `double_backward` (sym)

**Impact:**
- Significant relative increase but absolute error still manageable
- Transition state structures are affected, which is concerning for reaction pathway analysis

**Version Timeline:**
- 2.7.1: ✅ Baseline (RMS = 0.001)
- 2.8.0: 🟡 Regression (RMS = 0.179) - introduced in 2.8.0
- 2.10.0: 🟡 Regression (RMS = 0.179) - persists
- 2.11.0: 🟡 Regression (RMS = 0.179) - persists

### 🟡 Example 6: Distorted Water (3 atoms)

**Baseline (2.7.1):**
- RMS = 0.000 eV/Å² (perfect match)
- Best method: `fairchem_loop` (sym)

**Regression (2.11.0):**
- RMS = 0.212 eV/Å²
- Best method: `vmap` (no-sym)

**Impact:**
- Regression introduced where previously perfect accuracy was achieved
- Absolute error is small but represents a significant relative change

**Version Timeline:**
- 2.7.1: ✅ Baseline (RMS = 0.000)
- 2.8.0: 🟡 Regression (RMS = 0.212) - introduced in 2.8.0
- 2.10.0: 🟡 Regression (RMS = 0.212) - persists
- 2.11.0: 🟡 Regression (RMS = 0.212) - persists

## Minor Impact (RMS Error < 0.1 eV/Å²)

### 🟢 Example 1: Large Organic Molecule (51 atoms)

**Baseline (2.7.1):**
- RMS = 0.000 eV/Å²
- Best method: `double_backward_float64` (sym)

**Regression (2.11.0):**
- RMS = 0.013 eV/Å²
- Best method: `double_backward` (no-sym)

**Impact:**
- Small regression but still acceptable for large systems
- Suggests larger systems are less affected than small molecules

**Version Timeline:**
- 2.7.1: ✅ Baseline (RMS = 0.000)
- 2.8.0: 🟢 Minor regression (RMS = 0.013) - introduced in 2.8.0
- 2.10.0: 🟢 Minor regression (RMS = 0.013) - persists
- 2.11.0: 🟢 Minor regression (RMS = 0.013) - persists

### 🟢 Example 9: Rotated Equilibrium Water (3 atoms)

**Baseline (2.7.1):**
- RMS = 0.000 eV/Å²
- Best method: `double_backward_float64` (sym)

**Regression (2.11.0):**
- RMS = 0.029 eV/Å²
- Best method: `fairchem` (sym)

**Impact:**
- This is a rotated version of example_7 (equilibrium water)
- Shows that the regression affects rotated geometries as well
- Error is much smaller than example_7, suggesting some orientation dependence

**Version Timeline:**
- 2.7.1: ✅ Baseline (RMS = 0.000)
- 2.8.0: 🟢 Minor regression (RMS = 0.029) - introduced in 2.8.0
- 2.10.0: 🟢 Minor regression (RMS = 0.029) - persists
- 2.11.0: 🟢 Minor regression (RMS = 0.029) - persists

## Unaffected Systems

### ✅ Example 2: Water Molecule (3 atoms)

**All Versions:**
- RMS = 0.001 eV/Å² consistently across all versions
- No regression observed

**Impact:**
- Demonstrates that not all small molecules are affected
- Suggests geometry-specific or method-specific issues

### ✅ Example 4: Equilibrium Methane (5 atoms)

**All Versions:**
- RMS = 0.000 eV/Å² consistently across all versions
- No regression observed

**Impact:**
- Equilibrium methane (example_4) is unaffected while distorted methane (example_3) shows critical regression
- Strongly suggests geometry-dependent issues

## Moderate Impact (continued)

### 🟡 Example 8: Rotated Distorted Methane (5 atoms)

**Baseline (2.7.1):**
- RMS = 0.001 eV/Å²
- Best method: `double_backward_float64` (sym)

**Regression (2.8.0+):**
- RMS = 0.122 eV/Å² (122x increase)
- Best method: `fairchem_loop` (sym)

**Impact:**
- Rotated version of example_3 shows moderate regression
- Regression introduced in 2.8.0 and persists through 2.11.0
- Note: Example 3 itself fails completely in 2.8.0/2.10.0, but the rotated version (example_8) runs with errors

**Version Timeline:**
- 2.7.1: ✅ Baseline (RMS = 0.001)
- 2.8.0: 🟡 Regression (RMS = 0.122) - introduced in 2.8.0
- 2.10.0: 🟡 Regression (RMS = 0.122) - persists
- 2.11.0: 🟡 Regression (RMS = 0.122) - persists

## Key Observations

### 1. Small Molecules Most Affected
- Examples 3, 6, 7, and 9 (3-5 atoms) show the most severe regressions
- Example 1 (51 atoms) shows only minor regression
- Suggests numerical stability issues in small system handling

### 2. Geometry Dependence
- **Distorted geometries** (example_3) show critical regression
- **Equilibrium geometries** (example_4) remain unaffected
- **Equilibrium water** (example_7) shows critical regression while **equilibrium methane** (example_4) does not
- Pattern is complex and geometry-specific

### 3. Version-Specific Behavior
- **2.8.0 and 2.10.0:** Critical failures for examples 3 and 7 - Hessian computation produces NaN values (all elements are NaN), causing eigenvalue computation to fail. All methods fail with "Hessian contains invalid values" errors.
- **2.11.0:** Examples 3 and 7 run successfully but show massive errors (RMS errors of 67.839 and 25.510 respectively)
- Suggests changes between 2.10.0 and 2.11.0 fixed the NaN issue but introduced numerical accuracy problems
- **Root cause:** The NaN values in 2.8.0/2.10.0 indicate a fundamental bug in Hessian computation for these specific geometries, likely related to numerical instability or division by zero in the autograd computation

### 4. Method Dependence
- Best methods vary across versions:
  - 2.7.1: `double_backward_float64` often best
  - 2.11.0: `vmap`, `fairchem`, or `fairchem_loop` often best
- Suggests underlying implementation changes affecting different methods differently

### 5. Rotated Geometries
- Example 9 (rotated equilibrium water) shows minor regression vs. example_7 (non-rotated) showing critical regression
- Suggests some orientation dependence, but rotation alone doesn't fully explain the difference

## Version Comparison Matrix

| Version | Example 1 | Example 2 | Example 3 | Example 4 | Example 5 | Example 6 | Example 7 | Example 8 | Example 9 |
|---------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| 2.7.1   | ✅ 0.000   | ✅ 0.001   | ✅ 0.158   | ✅ 0.000   | ✅ 0.001   | ✅ 0.000   | ✅ 0.041   | ✅ 0.001   | ✅ 0.000   |
| 2.8.0   | 🟢 0.013   | ✅ 0.001   | 🔴 FAILED  | ✅ 0.000   | 🟡 0.179   | 🟡 0.212   | 🔴 FAILED  | 🟡 0.122   | 🟢 0.029   |
| 2.10.0  | 🟢 0.013   | ✅ 0.001   | 🔴 FAILED  | ✅ 0.000   | 🟡 0.179   | 🟡 0.212   | 🔴 FAILED  | 🟡 0.122   | 🟢 0.029   |
| 2.11.0  | 🟢 0.013   | ✅ 0.001   | 🔴 67.839  | ✅ 0.000   | 🟡 0.179   | 🟡 0.212   | 🔴 25.510  | 🟡 0.122   | 🟢 0.029   |

**Legend:**
- ✅ OK: No regression
- 🟢 Minor: Small regression (< 0.1 eV/Å²)
- 🟡 Moderate: Moderate regression (0.1 - 10 eV/Å²)
- 🔴 FAILED: Hessian computation produces NaN values, all methods fail
- 🔴 Critical: Severe regression (> 10 eV/Å²)

## Detailed Error Breakdown

### Example 3 (Distorted Methane) - Critical Regression

**Version 2.7.1:**
- Best method: `double_backward` (sym)
- RMS: 0.158 eV/Å²
- MAE: 0.085 eV/Å²
- Max: 0.515 eV/Å²

**Version 2.11.0:**
- Best method: `vmap` (no-sym)
- RMS: 67.839 eV/Å² (429x increase)
- MAE: 12.899 eV/Å² (152x increase)
- Max: 360.151 eV/Å² (699x increase)

**Analysis:**
- All methods show severe degradation
- The regression makes Hessian computation unreliable for distorted geometries
- Critical for transition state and reaction pathway calculations

### Example 7 (Equilibrium Water) - Critical Regression

**Version 2.7.1:**
- Best method: `fairchem` (no-sym)
- RMS: 0.041 eV/Å²
- MAE: 0.019 eV/Å²
- Max: 0.137 eV/Å²

**Version 2.11.0:**
- Best method: `fairchem_loop` (no-sym)
- RMS: 25.510 eV/Å² (622x increase)
- MAE: 8.036 eV/Å² (423x increase)
- Max: 81.313 eV/Å² (593x increase)

**Analysis:**
- Even equilibrium geometries are severely affected
- Simple 3-atom system shows catastrophic errors
- Suggests fundamental issues with small molecule handling

### Example 9 (Rotated Equilibrium Water) - Minor Regression

**Version 2.7.1:**
- Best method: `double_backward_float64` (sym)
- RMS: 0.000 eV/Å²

**Version 2.11.0:**
- Best method: `fairchem` (sym)
- RMS: 0.029 eV/Å²

**Analysis:**
- Rotated version of example_7 shows much smaller error
- Suggests some orientation dependence in the regression
- Still a regression but much less severe than non-rotated case

## Recommendations

### 1. Immediate Actions

**Priority Fix Required:**
- Examples 3 and 7 require immediate attention due to massive error increases (400-600x)
- These represent critical failures for small molecule Hessian computations

**Investigation Focus:**
- Review changes in fairchem-core between 2.7.1 and 2.8.0 related to:
  - Small molecule handling (3-5 atom systems)
  - Hessian computation for distorted geometries
  - Numerical stability in autograd computations
  - Gradient/hessian computation changes
  - Changes to `vmap`, `fairchem`, and `fairchem_loop` implementations

### 2. Testing

**Regression Test Suite:**
- Add examples 3 and 7 to fairchem-core's regression test suite
- Include both equilibrium and distorted geometry test cases
- Test across multiple versions to catch regressions early

**Test Coverage:**
- Small molecules (3-5 atoms) - currently most affected
- Distorted geometries - critical for transition state calculations
- Large molecules (50+ atoms) - currently less affected but should be monitored

### 3. Workarounds

**For Users:**
- Use fairchem-core 2.7.1 for systems matching examples 3 and 7 characteristics:
  - Small molecules (3-5 atoms)
  - Distorted geometries
  - Transition state structures
- For large systems (50+ atoms), version 2.11.0 may be acceptable with minor errors

**For Developers:**
- Consider reverting problematic changes introduced in 2.8.0
- Investigate why examples 3 and 7 failed in 2.8.0/2.10.0 but ran in 2.11.0
- Review numerical stability improvements needed for small systems

### 4. Further Investigation

**Version-Specific Analysis:**
1. Check fairchem-core release notes for versions 2.8.0, 2.10.0, and 2.11.0
2. Review git commits between 2.7.1 and 2.8.0 tags
3. Test patch versions between 2.7.1 and 2.8.0 if available (e.g., 2.7.2, 2.7.3)
4. Investigate why 2.11.0 shows regressions while 2.8.0/2.10.0 showed test failures

**Method-Specific Analysis:**
- Compare `double_backward`, `vmap`, `fairchem`, and `fairchem_loop` implementations across versions
- Investigate why `double_backward_float64` was often best in 2.7.1 but not in 2.11.0
- Review changes to autograd/hessian computation paths

**Geometry-Specific Analysis:**
- Understand why equilibrium methane (example_4) is unaffected while distorted methane (example_3) shows critical regression
- Investigate why equilibrium water (example_7) shows regression while equilibrium methane (example_4) does not
- Test more geometry variations to identify patterns

## Next Steps

1. ✅ **Completed:** Re-run examples 3 and 7 in 2.8.0 and 2.10.0 - confirmed failures due to NaN values in Hessian computation
2. ✅ **Completed:** Example 8 file format issue resolved - rotated geometry analysis now complete
3. **Contact fairchem-core maintainers** with this analysis to prioritize fixes:
   - Report NaN bug in versions 2.8.0 and 2.10.0 for examples 3 and 7
   - Report massive accuracy regression in version 2.11.0 for examples 3 and 7
4. **Create minimal reproducible examples** for bug reports showing:
   - NaN values in Hessian computation (2.8.0/2.10.0)
   - Massive RMS errors (2.11.0)
5. **Investigate root cause** of NaN values in 2.8.0/2.10.0:
   - Check for division by zero or numerical instability in autograd paths
   - Review changes to Hessian computation between 2.7.1 and 2.8.0
6. **Monitor future versions** for regression fixes

## Conclusion

The regression analysis reveals critical issues in fairchem-core versions 2.8.0 and later, with the most severe problems affecting small molecules (3-5 atoms) and distorted geometries.

**Key Findings:**

1. **Versions 2.8.0 and 2.10.0:** Examples 3 and 7 completely fail due to NaN values in Hessian computation. All 225 elements (example_3) or 81 elements (example_7) are NaN, causing eigenvalue computation to fail. This represents a critical bug that makes Hessian computation impossible for these systems.

2. **Version 2.11.0:** Examples 3 and 7 run successfully but show catastrophic errors (RMS errors of 67.839 and 25.510 respectively, representing 429x and 622x increases from baseline). While the NaN bug is fixed, the numerical accuracy is severely degraded.

3. **Other regressions:** Examples 1, 5, 6, 8, and 9 show regressions introduced in 2.8.0 that persist through 2.11.0, though these are less severe than examples 3 and 7.

The pattern suggests fundamental issues with:
- Small molecule numerical stability (NaN values in 2.8.0/2.10.0)
- Distorted geometry handling (example_3 fails/computes incorrectly)
- Equilibrium geometry handling for water (example_7 fails/computes incorrectly)
- Autograd/hessian computation paths (all methods affected)

**Immediate action is required** to restore accuracy for affected systems, particularly for users relying on Hessian computations for transition state analysis and reaction pathway calculations. The NaN bug in 2.8.0/2.10.0 is particularly critical as it completely prevents Hessian computation for affected systems.
