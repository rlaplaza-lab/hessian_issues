# UMA Hessian Analysis Summary

**FairChem-Core Version:** 2.11.0
**Number of Examples:** 7

---

## Summary Table

| Example | Structure | Atoms | Device | Best Method | RMS Error | MAE | Max Error | Neg Freqs |
|---------|-----------|-------|--------|-------------|-----------|-----|-----------|-----------|
| example_1 | example_1.xyz | 51 | cuda | double_backward (no-sym) | 0.013 | 0.002 | 0.392 | 0 |
| example_2 | example_2.xyz | 3 | cuda | fairchem_loop (no-sym) | 0.001 | 0.001 | 0.006 | 0 |
| example_3 | example_3.xyz | 5 | cuda | fairchem (sym) | 67.839 | 12.898 | 360.150 | 0 |
| example_4 | example_4.xyz | 5 | cuda | fairchem_loop (no-sym) | 0.000 | 0.000 | 0.002 | 0 |
| example_5 | example_5.xyz | 12 | cuda | vmap (sym) | 0.179 | 0.021 | 2.753 | 0 |
| example_6 | example_6.xyz | 3 | cuda | vmap (no-sym) | 0.212 | 0.068 | 0.905 | 0 |
| example_7 | example_7.xyz | 3 | cuda | fairchem_loop (no-sym) | 25.510 | 8.036 | 81.313 | 0 |

---

## EXAMPLE_1

**Structure:** example_1.xyz  
**Atoms:** 51  
**Device:** cuda

### Analytical Methods Comparison

| Method | Symmetrize | RMS Error | MAE | Max Error | Symmetry Error | Neg Freqs | Status |
|--------|------------|-----------|-----|-----------|----------------|-----------|--------|
| double_backward | Yes | 0.013 | 0.002 | 0.392 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 0.013 | 0.002 | 0.392 | 0.000011 | 0 | ✓ Success |
| vmap | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| vmap | No | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| fairchem | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| fairchem | No | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| fairchem_loop | Yes | 0.013 | 0.002 | 0.392 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.013 | 0.002 | 0.392 | 0.000008 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 22.48 cm⁻¹
- Max frequency: 3234.37 cm⁻¹
- Mean absolute frequency: 1160.54 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 22.63 cm⁻¹
- Max frequency: 3234.59 cm⁻¹
- Mean absolute frequency: 1161.06 cm⁻¹
- Negative frequencies: 0

### Finite Difference Convergence

| Delta (Å) | RMS Error | MAE | Max Error | Neg Freqs |
|-----------|-----------|-----|-----------|-----------|
| 0.05 | 0.025 | 0.004 | 0.493 | 1 |
| 0.01 | 0.003 | 0.000 | 0.163 | 0 |
| 0.005 | 0.001 | 0.000 | 0.058 | 0 |
| 0.001 | Reference | Reference | Reference | 0 |

---

## EXAMPLE_2

**Structure:** example_2.xyz  
**Atoms:** 3  
**Device:** cuda

### Analytical Methods Comparison

| Method | Symmetrize | RMS Error | MAE | Max Error | Symmetry Error | Neg Freqs | Status |
|--------|------------|-----------|-----|-----------|----------------|-----------|--------|
| double_backward | Yes | 0.001 | 0.001 | 0.006 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 0.001 | 0.001 | 0.006 | 0.000008 | 0 | ✓ Success |
| vmap | Yes | 0.001 | 0.001 | 0.006 | 0.000000 | 0 | ✓ Success |
| vmap | No | 0.001 | 0.001 | 0.006 | 0.000010 | 0 | ✓ Success |
| fairchem | Yes | 0.001 | 0.001 | 0.006 | 0.000000 | 0 | ✓ Success |
| fairchem | No | 0.001 | 0.001 | 0.006 | 0.000006 | 0 | ✓ Success |
| fairchem_loop | Yes | 0.001 | 0.001 | 0.006 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.001 | 0.001 | 0.006 | 0.000008 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 1621.66 cm⁻¹
- Max frequency: 3920.08 cm⁻¹
- Mean absolute frequency: 3120.76 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 1621.68 cm⁻¹
- Max frequency: 3920.17 cm⁻¹
- Mean absolute frequency: 3120.82 cm⁻¹
- Negative frequencies: 0

### Finite Difference Convergence

| Delta (Å) | RMS Error | MAE | Max Error | Neg Freqs |
|-----------|-----------|-----|-----------|-----------|
| 0.05 | 0.101 | 0.060 | 0.267 | 0 |
| 0.01 | 0.005 | 0.003 | 0.014 | 0 |
| 0.005 | 0.002 | 0.001 | 0.008 | 0 |
| 0.001 | Reference | Reference | Reference | 0 |

---

## EXAMPLE_3

**Structure:** example_3.xyz  
**Atoms:** 5  
**Device:** cuda

### Analytical Methods Comparison

| Method | Symmetrize | RMS Error | MAE | Max Error | Symmetry Error | Neg Freqs | Status |
|--------|------------|-----------|-----|-----------|----------------|-----------|--------|
| double_backward | Yes | 67.839 | 12.898 | 360.150 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 67.839 | 12.898 | 360.150 | 0.264910 | 0 | ✓ Success |
| vmap | Yes | 67.839 | 12.898 | 360.150 | 0.000000 | 0 | ✓ Success |
| vmap | No | 67.839 | 12.898 | 360.150 | 0.219378 | 0 | ✓ Success |
| fairchem | Yes | 67.839 | 12.898 | 360.150 | 0.000000 | 0 | ✓ Success |
| fairchem | No | 67.839 | 12.898 | 360.150 | 0.235605 | 0 | ✓ Success |
| fairchem_loop | Yes | 67.839 | 12.898 | 360.150 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 67.839 | 12.898 | 360.150 | 0.176703 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 8.04 cm⁻¹
- Max frequency: 1401.70 cm⁻¹
- Mean absolute frequency: 1019.61 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 0.13 cm⁻¹
- Max frequency: 10321.07 cm⁻¹
- Mean absolute frequency: 3051.48 cm⁻¹
- Negative frequencies: 0

### Finite Difference Convergence

| Delta (Å) | RMS Error | MAE | Max Error | Neg Freqs |
|-----------|-----------|-----|-----------|-----------|
| 0.05 | 0.026 | 0.013 | 0.113 | 0 |
| 0.01 | 0.012 | 0.007 | 0.036 | 0 |
| 0.005 | 0.012 | 0.007 | 0.037 | 0 |
| 0.001 | Reference | Reference | Reference | 0 |

---

## EXAMPLE_4

**Structure:** example_4.xyz  
**Atoms:** 5  
**Device:** cuda

### Analytical Methods Comparison

| Method | Symmetrize | RMS Error | MAE | Max Error | Symmetry Error | Neg Freqs | Status |
|--------|------------|-----------|-----|-----------|----------------|-----------|--------|
| double_backward | Yes | 0.000 | 0.000 | 0.002 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 0.000 | 0.000 | 0.002 | 0.000002 | 0 | ✓ Success |
| vmap | Yes | 0.000 | 0.000 | 0.002 | 0.000000 | 0 | ✓ Success |
| vmap | No | 0.000 | 0.000 | 0.002 | 0.000004 | 0 | ✓ Success |
| fairchem | Yes | 0.000 | 0.000 | 0.002 | 0.000000 | 0 | ✓ Success |
| fairchem | No | 0.000 | 0.000 | 0.002 | 0.000004 | 0 | ✓ Success |
| fairchem_loop | Yes | 0.000 | 0.000 | 0.002 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.000 | 0.000 | 0.002 | 0.000004 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 1326.08 cm⁻¹
- Max frequency: 3171.34 cm⁻¹
- Mean absolute frequency: 2183.21 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 1326.09 cm⁻¹
- Max frequency: 3171.28 cm⁻¹
- Mean absolute frequency: 2183.19 cm⁻¹
- Negative frequencies: 0

### Finite Difference Convergence

| Delta (Å) | RMS Error | MAE | Max Error | Neg Freqs |
|-----------|-----------|-----|-----------|-----------|
| 0.05 | 0.069 | 0.026 | 0.423 | 0 |
| 0.01 | 0.003 | 0.001 | 0.016 | 0 |
| 0.005 | 0.001 | 0.000 | 0.003 | 0 |
| 0.001 | Reference | Reference | Reference | 0 |

---

## EXAMPLE_5

**Structure:** example_5.xyz  
**Atoms:** 12  
**Device:** cuda

### Analytical Methods Comparison

| Method | Symmetrize | RMS Error | MAE | Max Error | Symmetry Error | Neg Freqs | Status |
|--------|------------|-----------|-----|-----------|----------------|-----------|--------|
| double_backward | Yes | 0.179 | 0.021 | 2.752 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 0.179 | 0.021 | 2.752 | 0.000051 | 0 | ✓ Success |
| vmap | Yes | 0.179 | 0.021 | 2.753 | 0.000000 | 0 | ✓ Success |
| vmap | No | 0.179 | 0.021 | 2.752 | 0.000035 | 0 | ✓ Success |
| fairchem | Yes | 0.179 | 0.021 | 2.752 | 0.000000 | 0 | ✓ Success |
| fairchem | No | 0.179 | 0.021 | 2.753 | 0.000057 | 0 | ✓ Success |
| fairchem_loop | Yes | 0.179 | 0.021 | 2.752 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.179 | 0.021 | 2.752 | 0.000028 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 46.78 cm⁻¹
- Max frequency: 3270.78 cm⁻¹
- Mean absolute frequency: 1030.01 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 75.37 cm⁻¹
- Max frequency: 3271.22 cm⁻¹
- Mean absolute frequency: 1033.29 cm⁻¹
- Negative frequencies: 0

### Finite Difference Convergence

| Delta (Å) | RMS Error | MAE | Max Error | Neg Freqs |
|-----------|-----------|-----|-----------|-----------|
| 0.05 | 0.074 | 0.021 | 0.719 | 0 |
| 0.01 | 0.003 | 0.001 | 0.029 | 0 |
| 0.005 | 0.001 | 0.000 | 0.008 | 0 |
| 0.001 | Reference | Reference | Reference | 0 |

---

## EXAMPLE_6

**Structure:** example_6.xyz  
**Atoms:** 3  
**Device:** cuda

### Analytical Methods Comparison

| Method | Symmetrize | RMS Error | MAE | Max Error | Symmetry Error | Neg Freqs | Status |
|--------|------------|-----------|-----|-----------|----------------|-----------|--------|
| double_backward | Yes | 0.212 | 0.068 | 0.905 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 0.212 | 0.068 | 0.905 | 0.000001 | 0 | ✓ Success |
| vmap | Yes | 0.212 | 0.068 | 0.905 | 0.000000 | 0 | ✓ Success |
| vmap | No | 0.212 | 0.068 | 0.905 | 0.000002 | 0 | ✓ Success |
| fairchem | Yes | 0.212 | 0.068 | 0.905 | 0.000000 | 0 | ✓ Success |
| fairchem | No | 0.212 | 0.068 | 0.905 | 0.000003 | 0 | ✓ Success |
| fairchem_loop | Yes | 0.212 | 0.068 | 0.905 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.212 | 0.068 | 0.905 | 0.000006 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 1088.29 cm⁻¹
- Max frequency: 1448.12 cm⁻¹
- Mean absolute frequency: 1226.91 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 1121.78 cm⁻¹
- Max frequency: 1515.36 cm⁻¹
- Mean absolute frequency: 1260.49 cm⁻¹
- Negative frequencies: 0

### Finite Difference Convergence

| Delta (Å) | RMS Error | MAE | Max Error | Neg Freqs |
|-----------|-----------|-----|-----------|-----------|
| 0.05 | 0.056 | 0.021 | 0.203 | 0 |
| 0.01 | 0.003 | 0.001 | 0.010 | 0 |
| 0.005 | 0.001 | 0.000 | 0.003 | 0 |
| 0.001 | Reference | Reference | Reference | 0 |

---

## EXAMPLE_7

**Structure:** example_7.xyz  
**Atoms:** 3  
**Device:** cuda

### Analytical Methods Comparison

| Method | Symmetrize | RMS Error | MAE | Max Error | Symmetry Error | Neg Freqs | Status |
|--------|------------|-----------|-----|-----------|----------------|-----------|--------|
| double_backward | Yes | 25.510 | 8.036 | 81.313 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 25.510 | 8.036 | 81.313 | 0.002030 | 0 | ✓ Success |
| vmap | Yes | 25.510 | 8.036 | 81.313 | 0.000000 | 0 | ✓ Success |
| vmap | No | 25.510 | 8.037 | 81.313 | 0.018517 | 0 | ✓ Success |
| fairchem | Yes | 25.510 | 8.036 | 81.313 | 0.000000 | 0 | ✓ Success |
| fairchem | No | 25.510 | 8.036 | 81.313 | 0.005154 | 0 | ✓ Success |
| fairchem_loop | Yes | 25.510 | 8.036 | 81.313 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 25.510 | 8.036 | 81.313 | 0.002399 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 1646.97 cm⁻¹
- Max frequency: 3823.51 cm⁻¹
- Mean absolute frequency: 3068.82 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 1639.10 cm⁻¹
- Max frequency: 3735.90 cm⁻¹
- Mean absolute frequency: 2872.21 cm⁻¹
- Negative frequencies: 0

### Finite Difference Convergence

| Delta (Å) | RMS Error | MAE | Max Error | Neg Freqs |
|-----------|-----------|-----|-----------|-----------|
| 0.05 | 0.091 | 0.054 | 0.242 | 0 |
| 0.01 | 0.003 | 0.002 | 0.009 | 0 |
| 0.005 | 0.002 | 0.001 | 0.004 | 0 |
| 0.001 | Reference | Reference | Reference | 0 |

---
