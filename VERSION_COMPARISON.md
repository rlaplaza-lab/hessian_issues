# FairChem-Core Version Comparison Analysis

This document summarizes the results of testing intermediate fairchem-core versions to identify when Hessian computation issues were introduced.

## Tested Versions

- **2.7.1** (baseline - working)
- **2.8.0** (first intermediate)
- **2.10.0** (second intermediate)
- **2.11.0** (latest)

## Key Findings

### Example 3 (Distorted Methane)

| Version | RMS Error | MAE | Max Error | Status |
|---------|-----------|-----|-----------|--------|
| 2.7.1   | 0.158     | 0.085 | 0.515 | ✓ Working |
| 2.8.0   | 67.839    | 12.898 | 360.150 | ⚠️ Degraded |
| 2.10.0  | 67.839    | 12.898 | 360.150 | ⚠️ Degraded |
| 2.11.0  | 67.839    | 12.898 | 360.150 | ⚠️ Degraded |

**Conclusion:** Regression introduced in **2.8.0** - RMS error increased by ~430x

### Example 7 (Equilibrium Water)

| Version | RMS Error | MAE | Max Error | Status |
|---------|-----------|-----|-----------|--------|
| 2.7.1   | 0.041     | 0.019 | 0.137 | ✓ Working |
| 2.8.0   | 25.510    | 8.036 | 81.313 | ⚠️ Degraded |
| 2.10.0  | 25.510    | 8.036 | 81.313 | ⚠️ Degraded |
| 2.11.0  | 25.510    | 8.036 | 81.313 | ⚠️ Degraded |

**Conclusion:** Regression introduced in **2.8.0** - RMS error increased by ~622x

### Other Examples

Examples 1, 2, 4, 5, and 6 show consistent results across all versions with minimal differences.

## Regression Timeline

1. **Version 2.7.1**: All examples work correctly
2. **Version 2.8.0**: **REGRESSION INTRODUCED** - Examples 3 and 7 show severe accuracy degradation
3. **Version 2.10.0**: Same regression persists
4. **Version 2.11.0**: Same regression persists

## Error Patterns

### Example 3 Issues
- Some analytical methods fail with "Eigenvalues did not converge" errors in 2.8.0 and 2.10.0
- Best available method shows RMS error of 67.839 eV/Å² (vs 0.158 in 2.7.1)
- This represents a **429x increase** in error

### Example 7 Issues
- Some analytical methods fail with "Eigenvalues did not converge" errors in 2.8.0 and 2.10.0
- Best available method shows RMS error of 25.510 eV/Å² (vs 0.041 in 2.7.1)
- This represents a **622x increase** in error

## Recommendations

1. **Root Cause**: The regression was introduced in fairchem-core **2.8.0**
2. **Investigation**: Review changes between 2.7.1 and 2.8.0, particularly:
   - Hessian computation methods
   - Autograd/gradient computation changes
   - Numerical stability improvements that may have introduced issues
3. **Impact**: Two specific test cases (distorted methane and equilibrium water) are severely affected
4. **Stability**: The regression has persisted through 2.10.0 and 2.11.0 without improvement

## Next Steps

To further narrow down the issue:
1. Check fairchem-core release notes for version 2.8.0
2. Review git commits between 2.7.1 and 2.8.0 tags
3. Test patch versions between 2.7.1 and 2.8.0 if available (e.g., 2.7.2, 2.7.3)
4. Consider testing 2.9.0 if it exists between 2.8.0 and 2.10.0

