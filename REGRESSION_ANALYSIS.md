# FairChem-Core Regression Analysis: Biggest Offenders

This document provides a detailed analysis of which systems are most severely affected by the regression introduced in fairchem-core 2.8.0.

## Summary: RMS Error Comparison

| Example | Structure | Atoms | v2.7.1 RMS | v2.11.0 RMS | Increase | Status |
|---------|-----------|-------|------------|-------------|----------|--------|
| **example_3** | example_3.xyz | 5 | **0.158** | **67.839** | **429x** | 🔴 **CRITICAL** |
| **example_7** | example_7.xyz | 3 | **0.041** | **25.510** | **622x** | 🔴 **CRITICAL** |
| example_5 | example_5.xyz | 12 | 0.001 | 0.179 | 179x | 🟡 Moderate |
| example_6 | example_6.xyz | 3 | 0.000 | 0.212 | ∞ | 🟡 Moderate |
| example_1 | example_1.xyz | 51 | 0.000 | 0.013 | ∞ | 🟢 Minor |
| example_2 | example_2.xyz | 3 | 0.001 | 0.001 | 1x | ✅ OK |
| example_4 | example_4.xyz | 5 | 0.000 | 0.000 | 0x | ✅ OK |

## Critical Offenders (RMS Error > 10 eV/Å²)

### 🔴 Example 3: Distorted Methane (5 atoms)
- **Baseline (2.7.1)**: RMS = 0.158 eV/Å², MAE = 0.085 eV/Å², Max = 0.515 eV/Å²
- **Regression (2.11.0)**: RMS = **67.839 eV/Å²**, MAE = **12.898 eV/Å²**, Max = **360.150 eV/Å²**
- **Impact**: 
  - RMS error increased by **429x**
  - Max error increased by **699x**
  - This is a **distorted geometry** test case (see README)

### 🔴 Example 7: Equilibrium Water (3 atoms)
- **Baseline (2.7.1)**: RMS = 0.041 eV/Å², MAE = 0.019 eV/Å², Max = 0.137 eV/Å²
- **Regression (2.11.0)**: RMS = **25.510 eV/Å²**, MAE = **8.036 eV/Å²**, Max = **81.313 eV/Å²**
- **Impact**:
  - RMS error increased by **622x**
  - Max error increased by **593x**
  - This is an **equilibrium geometry** test case

## Moderate Impact (RMS Error 0.1 - 10 eV/Å²)

### 🟡 Example 5: Transition State Structure (12 atoms)
- **Baseline (2.7.1)**: RMS = 0.001 eV/Å²
- **Regression (2.11.0)**: RMS = 0.179 eV/Å²
- **Impact**: 179x increase, but absolute error still relatively small

### 🟡 Example 6: Distorted Water (3 atoms)
- **Baseline (2.7.1)**: RMS = 0.000 eV/Å² (perfect match)
- **Regression (2.11.0)**: RMS = 0.212 eV/Å²
- **Impact**: Regression introduced, but absolute error is small

## Minor Impact (RMS Error < 0.1 eV/Å²)

### 🟢 Example 1: Large Organic Molecule (51 atoms)
- **Baseline (2.7.1)**: RMS = 0.000 eV/Å²
- **Regression (2.11.0)**: RMS = 0.013 eV/Å²
- **Impact**: Small regression, but still acceptable for large systems

## Unaffected Systems

### ✅ Example 2: Water Molecule (3 atoms)
- **Baseline (2.7.1)**: RMS = 0.001 eV/Å²
- **Regression (2.11.0)**: RMS = 0.001 eV/Å²
- **Status**: No regression observed

### ✅ Example 4: Equilibrium Methane (5 atoms)
- **Baseline (2.7.1)**: RMS = 0.000 eV/Å²
- **Regression (2.11.0)**: RMS = 0.000 eV/Å²
- **Status**: No regression observed

## Key Observations

1. **Small molecules are most affected**: Examples 3 and 7 (3-5 atoms) show the worst regressions
2. **Both distorted and equilibrium geometries affected**: 
   - Example 3 (distorted methane) - 429x increase
   - Example 7 (equilibrium water) - 622x increase
3. **Large systems less affected**: Example 1 (51 atoms) shows only minor regression
4. **Pattern**: The regression appears to affect certain molecular geometries more than others, regardless of system size

## Version Timeline

| Version | Example 3 RMS | Example 7 RMS | Status |
|---------|---------------|---------------|--------|
| 2.7.1   | 0.158         | 0.041         | ✅ Baseline |
| 2.8.0   | 67.839        | 25.510        | 🔴 Regression introduced |
| 2.10.0  | 67.839        | 25.510        | 🔴 Regression persists |
| 2.11.0  | 67.839        | 25.510        | 🔴 Regression persists |

## Recommendations

1. **Priority Fix**: Examples 3 and 7 require immediate attention due to massive error increases
2. **Investigation Focus**: 
   - Review changes in fairchem-core 2.8.0 related to:
     - Small molecule handling
     - Hessian computation for 3-5 atom systems
     - Numerical stability in autograd computations
     - Autograd/gradient computation changes
3. **Testing**: These two examples should be added to fairchem-core's regression test suite
4. **Workaround**: Consider using fairchem-core 2.7.1 for systems matching examples 3 and 7 characteristics

## Next Steps

To further narrow down the issue:
1. Check fairchem-core release notes for version 2.8.0
2. Review git commits between 2.7.1 and 2.8.0 tags
3. Test patch versions between 2.7.1 and 2.8.0 if available (e.g., 2.7.2, 2.7.3)
4. Consider testing 2.9.0 if it exists between 2.8.0 and 2.10.0

## Detailed Error Breakdown

### Example 3 (Distorted Methane)
- **Best method in 2.7.1**: `double_backward_float64` (sym)
- **Best method in 2.11.0**: `fairchem` (sym)
- **Note**: Some methods fail with "Eigenvalues did not converge" in 2.8.0 and 2.10.0

### Example 7 (Equilibrium Water)
- **Best method in 2.7.1**: `fairchem` (no-sym)
- **Best method in 2.11.0**: `fairchem_loop` (no-sym)
- **Note**: Same methods work, but accuracy is severely degraded

