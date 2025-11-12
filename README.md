# UMA Hessian Analysis Examples

Standalone examples for comparing UMA (Universal Model for Atoms) analytical Hessian implementations against finite-difference references. These scripts run without requiring the QME package, using only ASE, FairChem, NumPy, and PyTorch.

## Requirements

- Python 3.8+
- ASE
- NumPy
- PyTorch
- fairchem-core

The UMA pretrained model weights are downloaded automatically via FairChem on first use.

## Files

- `hessian_helpers.py`: Standalone UMA calculator implementation (no QME dependency)
- `example_1.py`: Analysis script for the LBFGS minimum structure
- `example_1.xyz`: Input geometry for example 1
- `example_1.json`: Output summary with frequency statistics and error metrics
- `example_2.py`: Analysis script for an optimized water molecule
- `example_2.xyz`: Optimized water geometry
- `example_2.json`: Output summary for water molecule

## Usage

Each example script is self-contained and infers input/output filenames from its own name:

```bash
python example_1.py
python example_2.py
```

The scripts will:
1. Load the corresponding `.xyz` geometry file
2. Compute finite-difference Hessians at multiple step sizes (0.05, 0.01, 0.005, 0.001 Å)
3. Compute analytical Hessians using multiple methods:
   - `double_backward`: Direct double-backward from energy
   - `vmap`: Vectorized vector-Jacobian products
   - `fairchem`: FairChem PR #1361 style (vmap variant)
   - `fairchem_loop`: FairChem style without vmap
4. Extract vibrational frequencies and compare against the high-resolution finite-difference reference
5. Print summary tables to stdout and save detailed JSON reports

## Output

Each script generates:
- Console output with frequency statistics and error metrics
- A JSON file (`<script_name>.json`) containing:
  - Reference finite-difference Hessian summary
  - Finite-difference results at all step sizes
  - Analytical method results with error metrics vs. reference

## Notes

- The helper module (`hessian_helpers.py`) mirrors the UMA Hessian computation logic from QME but operates independently
- All Hessian methods support optional symmetrization to reduce numerical noise
- The scripts automatically detect and use CUDA if available, otherwise fall back to CPU

