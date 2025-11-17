# UMA Hessian Analysis Examples

This repository contains examples for comparing UMA (Universal Model for Atoms) analytical Hessian implementations against finite-difference references. These examples demonstrate various Hessian computation methods and help validate the accuracy of analytical implementations.

## Overview

The examples systematically compare:
- **Finite-difference Hessians** computed at multiple step sizes using ASE's `Vibrations` class
- **Analytical Hessians** computed using PyTorch autograd with multiple methods:
  - `double_backward`: Direct second derivative via double backpropagation
  - `vmap`: Vectorized Jacobian-vector product using `torch.vmap`
  - `fairchem`: FairChem's internal implementation with vmap
  - `fairchem_loop`: FairChem's internal implementation without vmap

Results are compared using vibrational frequency analysis and error metrics (RMS error, mean absolute error, max absolute error).

## Requirements

- **Python**: 3.8 or higher
- **Dependencies**:
  - `ase` (Atomic Simulation Environment)
  - `numpy`
  - `torch` (PyTorch)
  - `fairchem-core`

The UMA pretrained model weights (`uma-s-1p1`) are downloaded automatically via FairChem on first use.

### Installation

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install ase numpy torch fairchem-core
```

For GPU support, ensure PyTorch is installed with CUDA support. The scripts automatically detect and use CUDA if available, otherwise falling back to CPU.

## Usage

Run the example scripts from the repository root:

```bash
python examples/example_1.py
python examples/example_2.py
python examples/example_3.py
python examples/example_4.py
python examples/example_5.py
python examples/example_6.py
python examples/example_7.py
```

Each script:
1. Loads the corresponding `.xyz` geometry file from the `data/` directory
2. Computes finite-difference Hessians at multiple step sizes (0.05, 0.01, 0.005, 0.001 Å)
3. Computes analytical Hessians using multiple methods (with and without symmetrization)
4. Compares results and saves a JSON report to the `results/` directory

### Additional Examples

- `examples/example_inference_settings.py`: Demonstrates usage of `InferenceSettings` for custom model configuration

## Output

Each script generates:
- **Console output**: Frequency statistics and error metrics comparing analytical and finite-difference methods
- **JSON report**: Detailed results saved to `results/<script_name>.json` with:
  - Reference finite-difference Hessian (smallest step size)
  - Finite-difference results at all step sizes with metrics vs. reference
  - Analytical method results with metrics vs. reference
  - Frequency summaries (min, max, mean absolute, negative frequency counts)

## Repository Structure

```
/hessian_issues/
├── README.md                 # This file
├── src/                      # Core implementation
│   └── hessian_helpers.py    # Standalone UMA calculator with Hessian computation
├── requirements.txt          # Python package dependencies
├── examples/                 # Example scripts
│   ├── example_1.py          # Large organic molecule test case (51 atoms)
│   ├── example_2.py          # Water molecule (H₂O) test case
│   ├── example_3.py          # Methane with distorted geometry
│   ├── example_4.py          # Methane with equilibrium geometry
│   ├── example_5.py          # Transition state structure test case
│   ├── example_6.py          # Distorted water molecule test case
│   ├── example_7.py          # Equilibrium water molecule test case
│   └── example_inference_settings.py  # InferenceSettings demonstration
├── data/                     # Input molecular geometries
│   ├── example_1.xyz
│   ├── example_2.xyz
│   ├── example_3.xyz
│   ├── example_4.xyz
│   ├── example_5.xyz
│   ├── example_6.xyz
│   └── example_7.xyz
└── results/                  # Generated output files (created by scripts)
    ├── example_1.json
    ├── example_2.json
    ├── example_3.json
    ├── example_4.json
    ├── example_5.json
    ├── example_6.json
    └── example_7.json
```

## Reproducibility

All scripts are designed to be self-contained and reproducible:
- Dependencies are specified in `requirements.txt` for easy environment setup
- Scripts automatically locate the repository root and find files in `src/`, `data/`, and `results/` directories
- Device selection (CUDA/CPU) is automatic based on availability
- Model weights are downloaded automatically on first use via FairChem
- Results are saved in a standardized JSON format for easy comparison
- All scripts use consistent methodology and parameters for reproducible results

## Example Descriptions

- **example_1.py**: Large organic molecule test case (51 atoms) for validation on complex systems
- **example_2.py**: Water molecule (H₂O) test case for validation on a simple, well-characterized system
- **example_3.py**: Methane (CH₄) molecule with distorted geometry, reproducing a failing test case from the test suite to investigate Hessian accuracy issues
- **example_4.py**: Methane molecule with realistic equilibrium tetrahedral geometry (C-H bond length ~1.087 Å) to compare with the distorted geometry case and determine if accuracy issues are geometry-dependent
- **example_5.py**: Transition state structure test case (12 atoms: C, H, F, Cl, N, O) to validate Hessian computation on transition state geometries
- **example_6.py**: Distorted water molecule test case investigating Hessian consistency issues between analytical and finite-difference methods
- **example_7.py**: Equilibrium water molecule test case comparing Hessian accuracy for equilibrium vs. distorted geometries
