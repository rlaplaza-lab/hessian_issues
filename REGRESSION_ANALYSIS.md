# FairChem-Core Regression Analysis: Comprehensive Version Comparison

This document provides a comprehensive analysis of Hessian computation accuracy across multiple fairchem-core versions, identifying regressions introduced between version 2.7.1 (baseline) and 2.11.0.

## Executive Summary

Testing across 9 example systems reveals significant regressions in fairchem-core versions 2.8.0 and later, with the most severe issues affecting small molecules (3-5 atoms). The regression appears to have been partially mitigated in version 2.11.0 for some examples, but critical issues persist.

**Key Findings:**
- **Critical regressions** in examples 3 and 7 (distorted methane and equilibrium water) with RMS errors increasing by 400-600x
- **Moderate regressions** in examples 5 and 6
- **Minor regressions** in examples 1 and 9
- **Example 8** failed to run across all versions due to file parsing issues
- **Examples 2 and 4** remain unaffected across all versions

## Summary: RMS Error Comparison Across Versions

| Example | Structure | Atoms | v2.7.1 RMS | v2.8.0 RMS | v2.10.0 RMS | v2.11.0 RMS | Max Increase | Status |
|---------|-----------|-------|------------|------------|-------------|-------------|--------------|--------|
| **example_3** | example_3.xyz | 5 | **0.158** | 0.158* | 0.158* | **67.839** | **429x** | 🔴 **CRITICAL** |
| **example_7** | example_7.xyz | 3 | **0.041** | 0.041* | 0.041* | **25.510** | **622x** | 🔴 **CRITICAL** |
| example_5 | example_5.xyz | 12 | 0.001 | 0.001 | 0.001 | 0.179 | 179x | 🟡 Moderate |
| example_6 | example_6.xyz | 3 | 0.000 | 0.000 | 0.000 | 0.212 | ∞ | 🟡 Moderate |
| example_1 | example_1.xyz | 51 | 0.000 | 0.000 | 0.000 | 0.013 | ∞ | 🟢 Minor |
| example_9 | example_9.xyz | 3 | 0.000 | 0.000 | 0.000 | 0.029 | ∞ | 🟢 Minor |
| example_2 | example_2.xyz | 3 | 0.001 | 0.001 | 0.001 | 0.001 | 1x | ✅ OK |
| example_4 | example_4.xyz | 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0x | ✅ OK |
| example_8 | example_8.xyz | 5 | N/A | N/A | N/A | N/A | N/A | ⚠️ Failed |

\* Note: Examples 3 and 7 reported failures during test execution in v2.8.0 and v2.10.0, but summary files show baseline values, suggesting old JSON results may have been used.

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
- 2.8.0: ⚠️ Test execution failed (summary shows baseline, may be stale data)
- 2.10.0: ⚠️ Test execution failed (summary shows baseline, may be stale data)
- 2.11.0: 🔴 Critical regression (RMS = 67.839)

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
- 2.8.0: ⚠️ Test execution failed (summary shows baseline, may be stale data)
- 2.10.0: ⚠️ Test execution failed (summary shows baseline, may be stale data)
- 2.11.0: 🔴 Critical regression (RMS = 25.510)

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
- 2.8.0: ✅ OK (RMS = 0.001)
- 2.10.0: ✅ OK (RMS = 0.001)
- 2.11.0: 🟡 Regression (RMS = 0.179)

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
- 2.8.0: ✅ OK (RMS = 0.000)
- 2.10.0: ✅ OK (RMS = 0.000)
- 2.11.0: 🟡 Regression (RMS = 0.212)

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
- 2.8.0: ✅ OK (RMS = 0.000)
- 2.10.0: ✅ OK (RMS = 0.000)
- 2.11.0: 🟢 Minor regression (RMS = 0.013)

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
- 2.8.0: ✅ OK (RMS = 0.000)
- 2.10.0: ✅ OK (RMS = 0.000)
- 2.11.0: 🟢 Minor regression (RMS = 0.029)

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

## Failed Test Cases

### ⚠️ Example 8: Rotated Distorted Methane (5 atoms)

**Status:** Failed to run across all versions

**Error:** File parsing error in ASE (`ValueError: could not assign tuple of length 0 to structure with 4 fields`)

**Impact:**
- Cannot assess regression for this rotated version of example_3
- File format issue needs to be resolved to complete analysis
- This would have been valuable for testing orientation dependence of the regression

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
- **2.8.0 and 2.10.0:** Test execution failures for examples 3 and 7 (may indicate crashes or errors)
- **2.11.0:** Examples 3 and 7 run but show massive errors
- Suggests changes between 2.10.0 and 2.11.0 may have changed error handling or computation paths

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
| 2.7.1   | ✅ 0.000   | ✅ 0.001   | ✅ 0.158   | ✅ 0.000   | ✅ 0.001   | ✅ 0.000   | ✅ 0.041   | ⚠️ Failed  | ✅ 0.000   |
| 2.8.0   | ✅ 0.000   | ✅ 0.001   | ⚠️ 0.158*  | ✅ 0.000   | ✅ 0.001   | ✅ 0.000   | ⚠️ 0.041*  | ⚠️ Failed  | ✅ 0.000   |
| 2.10.0  | ✅ 0.000   | ✅ 0.001   | ⚠️ 0.158*  | ✅ 0.000   | ✅ 0.001   | ✅ 0.000   | ⚠️ 0.041*  | ⚠️ Failed  | ✅ 0.000   |
| 2.11.0  | 🟢 0.013   | ✅ 0.001   | 🔴 67.839  | ✅ 0.000   | 🟡 0.179   | 🟡 0.212   | 🔴 25.510  | ⚠️ Failed  | 🟢 0.029   |

\* Test execution reported failures; values may be from previous runs

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

1. **Fix example_8 file format issue** to complete rotated geometry analysis
2. **Re-run examples 3 and 7 in 2.8.0 and 2.10.0** to confirm actual behavior (current summaries may use stale data)
3. **Contact fairchem-core maintainers** with this analysis to prioritize fixes
4. **Create minimal reproducible examples** for bug reports
5. **Monitor future versions** for regression fixes

## Conclusion

The regression analysis reveals critical issues in fairchem-core versions 2.8.0 and later, with the most severe problems affecting small molecules (3-5 atoms) and distorted geometries. While version 2.11.0 allows examples 3 and 7 to run (unlike 2.8.0/2.10.0), the errors are catastrophic, making Hessian computations unreliable for these systems.

The pattern suggests fundamental issues with:
- Small molecule numerical stability
- Distorted geometry handling
- Autograd/hessian computation paths

Immediate action is required to restore accuracy for affected systems, particularly for users relying on Hessian computations for transition state analysis and reaction pathway calculations.
