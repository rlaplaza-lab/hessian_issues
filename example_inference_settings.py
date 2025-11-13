#!/usr/bin/env python3
"""Example script demonstrating InferenceSettings usage.

This script demonstrates how to use InferenceSettings to configure UMA model
inference parameters for Hessian computation. InferenceSettings allows fine-grained
control over model execution settings such as TensorFloat-32, compilation, and
graph generation options.

Usage
-----
    python example_inference_settings.py

Requirements
------------
ASE, NumPy, PyTorch, and fairchem-core must be installed in the active
environment. The UMA pretrained weights are downloaded automatically via the
FairChem loader on first use.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from ase.io import read

SCRIPT_PATH = Path(__file__).resolve()
HELPER_PATH = SCRIPT_PATH.with_name("hessian_helpers.py")
HELPER_MODULE = "hessian_helpers"

helper_spec = importlib.util.spec_from_file_location(HELPER_MODULE, HELPER_PATH)
if helper_spec is None or helper_spec.loader is None:
    raise ImportError(f"Unable to load UMA helper from {HELPER_PATH}")
helper_module = importlib.util.module_from_spec(helper_spec)
sys.modules.setdefault(HELPER_MODULE, helper_module)
helper_spec.loader.exec_module(helper_module)

get_uma_calculator_with_inference_settings = helper_module.get_uma_calculator_with_inference_settings


def select_device() -> str:
    """Automatically select CUDA if available, otherwise CPU."""
    try:
        import torch

        if torch.cuda.is_available():  # type: ignore[attr-defined]
            return "cuda"
    except Exception:
        pass
    return "cpu"


def main() -> None:
    """Demonstrate InferenceSettings usage for UMA Hessian computation."""
    # Load a structure
    structure_path = SCRIPT_PATH.with_name("example_3.xyz")
    if not structure_path.exists():
        raise SystemExit(f"Structure file not found: {structure_path}")

    atoms = read(structure_path)
    atoms.info["charge"] = 0
    atoms.info["spin"] = 1

    device = select_device()
    print(f"Using device: {device}")

    print("\nCreating calculator with InferenceSettings...")
    print("Settings: tf32=False, merge_mole=True, compile=False, etc.")

    # Create calculator with InferenceSettings
    # These settings control model execution behavior:
    # - tf32: Enable TensorFloat-32 precision (faster but less precise)
    # - merge_mole: Merge molecular operations for efficiency
    # - compile: Enable torch.compile optimization
    # - activation_checkpointing: Trade compute for memory
    # - internal_graph_gen_version: Graph generation algorithm version
    # - external_graph_gen: Use external graph generation
    calc = get_uma_calculator_with_inference_settings(
        model_name="uma-s-1p1",
        device=device,
        tf32=False,
        merge_mole=True,
        compile=False,
        activation_checkpointing=False,
        internal_graph_gen_version=2,
        external_graph_gen=False,
    )

    calc.ensure_loaded()
    print("✓ Calculator created successfully")

    # Compute Hessian
    print("\nComputing Hessian using double_backward method...")
    hessian = calc.get_hessian(atoms, method="double_backward", symmetrize=True)
    print(f"✓ Hessian computed: shape {hessian.shape}")
    print(f"  Min value: {hessian.min():.6f} eV/Å²")
    print(f"  Max value: {hessian.max():.6f} eV/Å²")
    print(f"  Mean abs value: {abs(hessian).mean():.6f} eV/Å²")


if __name__ == "__main__":
    main()

