# UMA Hessian Analysis Examples

Examples for comparing UMA (Universal Model for Atoms) analytical Hessian implementations against finite-difference references.

## Requirements

- Python 3.8+
- ASE, NumPy, PyTorch, fairchem-core

The UMA pretrained model weights are downloaded automatically via FairChem on first use.

## Usage

Run the example scripts:

```bash
python example_1.py
python example_2.py
```

Each script:
1. Loads the corresponding `.xyz` geometry file
2. Computes finite-difference Hessians at multiple step sizes
3. Computes analytical Hessians using multiple methods
4. Compares results and saves a JSON report

## Output

Each script generates:
- Console output with frequency statistics and error metrics
- A JSON file (`<script_name>.json`) with detailed results

## Files

- `hessian_helpers.py`: UMA calculator implementation with Hessian computation
- `example_1.py`, `example_2.py`: Analysis scripts
- `example_1.xyz`, `example_2.xyz`: Input geometries
- `example_1.json`, `example_2.json`: Output results
