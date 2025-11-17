# UMA Hessian Analysis Summary

**FairChem-Core Version:** 2.7.1
**Number of Examples:** 7

---

## Summary Table

| Example | Structure | Atoms | Device | Best Method | RMS Error | MAE | Max Error | Neg Freqs |
|---------|-----------|-------|--------|-------------|-----------|-----|-----------|-----------|
| example_1 | example_1.xyz | 51 | cuda | double_backward_float64 (sym) | 0.000 | 0.000 | 0.014 | 0 |
| example_2 | example_2.xyz | 3 | cuda | fairchem (sym) | 0.001 | 0.001 | 0.006 | 0 |
| example_3 | example_3.xyz | 5 | cuda | double_backward_float64 (sym) | 0.158 | 0.085 | 0.515 | 0 |
| example_4 | example_4.xyz | 5 | cuda | double_backward_float64 (sym) | 0.000 | 0.000 | 0.002 | 0 |
| example_5 | example_5.xyz | 12 | cuda | vmap (sym) | 0.001 | 0.000 | 0.006 | 0 |
| example_6 | example_6.xyz | 3 | cuda | fairchem_loop (sym) | 0.000 | 0.000 | 0.000 | 0 |
| example_7 | example_7.xyz | 3 | cuda | fairchem (no-sym) | 0.041 | 0.019 | 0.137 | 0 |

---

## EXAMPLE_1

**Structure:** example_1.xyz  
**Atoms:** 51  
**Device:** cuda

### Analytical Methods Comparison

| Method | Symmetrize | RMS Error | MAE | Max Error | Symmetry Error | Neg Freqs | Status |
|--------|------------|-----------|-----|-----------|----------------|-----------|--------|
| double_backward | Yes | 0.000 | 0.000 | 0.014 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 0.000 | 0.000 | 0.013 | 0.000011 | 0 | ✓ Success |
| vmap | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| vmap | No | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| fairchem | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| fairchem | No | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| fairchem_loop | Yes | 0.000 | 0.000 | 0.013 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.000 | 0.000 | 0.014 | 0.000009 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | 0.000 | 0.000 | 0.014 | 0.000000 | 0 | ✓ Success |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 22.44 cm⁻¹
- Max frequency: 3234.37 cm⁻¹
- Mean absolute frequency: 1160.54 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 22.53 cm⁻¹
- Max frequency: 3234.43 cm⁻¹
- Mean absolute frequency: 1160.54 cm⁻¹
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
| double_backward | No | 0.001 | 0.001 | 0.006 | 0.000006 | 0 | ✓ Success |
| vmap | Yes | 0.001 | 0.001 | 0.006 | 0.000000 | 0 | ✓ Success |
| vmap | No | 0.001 | 0.001 | 0.006 | 0.000004 | 0 | ✓ Success |
| fairchem | Yes | 0.001 | 0.001 | 0.006 | 0.000000 | 0 | ✓ Success |
| fairchem | No | 0.001 | 0.001 | 0.006 | 0.000004 | 0 | ✓ Success |
| fairchem_loop | Yes | 0.001 | 0.001 | 0.006 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.001 | 0.001 | 0.006 | 0.000006 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | 0.001 | 0.001 | 0.006 | 0.000000 | 0 | ✓ Success |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 1621.66 cm⁻¹
- Max frequency: 3920.07 cm⁻¹
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
| double_backward | Yes | 0.158 | 0.085 | 0.515 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 0.158 | 0.085 | 0.515 | 0.000002 | 0 | ✓ Success |
| vmap | Yes | 0.158 | 0.085 | 0.515 | 0.000000 | 0 | ✓ Success |
| vmap | No | 0.158 | 0.085 | 0.515 | 0.000002 | 0 | ✓ Success |
| fairchem | Yes | 0.158 | 0.085 | 0.515 | 0.000000 | 0 | ✓ Success |
| fairchem | No | 0.158 | 0.085 | 0.515 | 0.000001 | 0 | ✓ Success |
| fairchem_loop | Yes | 0.158 | 0.085 | 0.515 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.158 | 0.085 | 0.515 | 0.000002 | 1 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | 0.158 | 0.085 | 0.515 | 0.000000 | 0 | ✓ Success |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 2.24 cm⁻¹
- Max frequency: 1389.14 cm⁻¹
- Mean absolute frequency: 980.69 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 0.00 cm⁻¹
- Max frequency: 1385.11 cm⁻¹
- Mean absolute frequency: 988.61 cm⁻¹
- Negative frequencies: 0

### Finite Difference Convergence

| Delta (Å) | RMS Error | MAE | Max Error | Neg Freqs |
|-----------|-----------|-----|-----------|-----------|
| 0.05 | 0.230 | 0.076 | 1.275 | 0 |
| 0.01 | 0.227 | 0.070 | 1.282 | 0 |
| 0.005 | 0.006 | 0.003 | 0.019 | 0 |
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
| fairchem | No | 0.000 | 0.000 | 0.002 | 0.000006 | 0 | ✓ Success |
| fairchem_loop | Yes | 0.000 | 0.000 | 0.002 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.000 | 0.000 | 0.002 | 0.000002 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | 0.000 | 0.000 | 0.002 | 0.000000 | 0 | ✓ Success |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 1326.08 cm⁻¹
- Max frequency: 3171.34 cm⁻¹
- Mean absolute frequency: 2183.21 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 1326.10 cm⁻¹
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
| double_backward | Yes | 0.001 | 0.000 | 0.006 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 0.001 | 0.000 | 0.006 | 0.000031 | 0 | ✓ Success |
| vmap | Yes | 0.001 | 0.000 | 0.006 | 0.000000 | 0 | ✓ Success |
| vmap | No | 0.001 | 0.000 | 0.006 | 0.000031 | 0 | ✓ Success |
| fairchem | Yes | 0.001 | 0.000 | 0.006 | 0.000000 | 0 | ✓ Success |
| fairchem | No | 0.001 | 0.000 | 0.006 | 0.000080 | 0 | ✓ Success |
| fairchem_loop | Yes | 0.001 | 0.000 | 0.006 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.001 | 0.000 | 0.006 | 0.000031 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | 0.001 | 0.000 | 0.006 | 0.000000 | 0 | ✓ Success |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 46.77 cm⁻¹
- Max frequency: 3270.78 cm⁻¹
- Mean absolute frequency: 1030.00 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 46.77 cm⁻¹
- Max frequency: 3270.69 cm⁻¹
- Mean absolute frequency: 1030.01 cm⁻¹
- Negative frequencies: 0

### Finite Difference Convergence

| Delta (Å) | RMS Error | MAE | Max Error | Neg Freqs |
|-----------|-----------|-----|-----------|-----------|
| 0.05 | 0.074 | 0.021 | 0.719 | 0 |
| 0.01 | 0.003 | 0.001 | 0.030 | 0 |
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
| double_backward | Yes | 0.000 | 0.000 | 0.000 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 0.000 | 0.000 | 0.000 | 0.000002 | 0 | ✓ Success |
| vmap | Yes | 0.000 | 0.000 | 0.000 | 0.000000 | 0 | ✓ Success |
| vmap | No | 0.000 | 0.000 | 0.000 | 0.000003 | 0 | ✓ Success |
| fairchem | Yes | 0.000 | 0.000 | 0.000 | 0.000000 | 0 | ✓ Success |
| fairchem | No | 0.000 | 0.000 | 0.000 | 0.000001 | 0 | ✓ Success |
| fairchem_loop | Yes | 0.000 | 0.000 | 0.000 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.000 | 0.000 | 0.000 | 0.000004 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | 0.000 | 0.000 | 0.000 | 0.000000 | 0 | ✓ Success |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 1088.30 cm⁻¹
- Max frequency: 1448.12 cm⁻¹
- Mean absolute frequency: 1226.91 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 1088.30 cm⁻¹
- Max frequency: 1448.11 cm⁻¹
- Mean absolute frequency: 1226.91 cm⁻¹
- Negative frequencies: 0

### Finite Difference Convergence

| Delta (Å) | RMS Error | MAE | Max Error | Neg Freqs |
|-----------|-----------|-----|-----------|-----------|
| 0.05 | 0.056 | 0.021 | 0.202 | 0 |
| 0.01 | 0.003 | 0.001 | 0.009 | 0 |
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
| double_backward | Yes | 0.041 | 0.019 | 0.137 | 0.000000 | 0 | ✓ Success |
| double_backward | No | 0.041 | 0.019 | 0.137 | 0.000004 | 0 | ✓ Success |
| vmap | Yes | 0.041 | 0.019 | 0.137 | 0.000000 | 0 | ✓ Success |
| vmap | No | 0.041 | 0.019 | 0.137 | 0.000006 | 0 | ✓ Success |
| fairchem | Yes | 0.041 | 0.019 | 0.137 | 0.000000 | 0 | ✓ Success |
| fairchem | No | 0.041 | 0.019 | 0.137 | 0.000006 | 0 | ✓ Success |
| fairchem_loop | Yes | 0.041 | 0.019 | 0.137 | 0.000000 | 0 | ✓ Success |
| fairchem_loop | No | 0.041 | 0.019 | 0.137 | 0.000002 | 0 | ✓ Success |
| double_backward_inference_settings | Yes | N/A | N/A | N/A | N/A | N/A | ❌ Error |
| double_backward_float64 | Yes | 0.041 | 0.019 | 0.137 | 0.000000 | 0 | ✓ Success |

### Frequency Summary

**Reference (Finite Difference):**
- Min frequency: 1646.93 cm⁻¹
- Max frequency: 3821.04 cm⁻¹
- Mean absolute frequency: 3067.95 cm⁻¹
- Negative frequencies: 0

**Best Analytical Method:**
- Min frequency: 1646.97 cm⁻¹
- Max frequency: 3815.19 cm⁻¹
- Mean absolute frequency: 3066.02 cm⁻¹
- Negative frequencies: 0

### Finite Difference Convergence

| Delta (Å) | RMS Error | MAE | Max Error | Neg Freqs |
|-----------|-----------|-----|-----------|-----------|
| 0.05 | 0.091 | 0.055 | 0.242 | 0 |
| 0.01 | 0.022 | 0.007 | 0.100 | 0 |
| 0.005 | 0.002 | 0.001 | 0.004 | 0 |
| 0.001 | Reference | Reference | Reference | 0 |

---
