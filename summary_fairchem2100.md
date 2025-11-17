# UMA Hessian Analysis Summary

**FairChem-Core Version:** 2.10.0
**Number of Examples:** 7

---

## Summary Table

| Example | Structure | Atoms | Device | Best Method | RMS Error | MAE | Max Error | Neg Freqs |
|---------|-----------|-------|--------|-------------|-----------|-----|-----------|-----------|
| example_1 | example_1.xyz | 51 | cuda | fairchem_loop (no-sym) | 0.000 | 0.000 | 0.013 | 0 |
| example_2 | example_2.xyz | 3 | cuda | fairchem_loop (no-sym) | 0.001 | 0.001 | 0.006 | 0 |
| example_3 | example_3.xyz | 5 | cuda | fairchem (sym) | 67.839 | 12.898 | 360.150 | 0 |
| example_4 | example_4.xyz | 5 | cuda | double_backward (sym) | 0.000 | 0.000 | 0.002 | 0 |
| example_5 | example_5.xyz | 12 | cuda | vmap (sym) | 0.001 | 0.000 | 0.006 | 0 |
| example_6 | example_6.xyz | 3 | cuda | fairchem_loop (sym) | 0.000 | 0.000 | 0.001 | 0 |
| example_7 | example_7.xyz | 3 | cuda | fairchem_loop (no-sym) | 25.510 | 8.036 | 81.313 | 0 |