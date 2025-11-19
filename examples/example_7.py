#!/usr/bin/env python3
"""UMA Hessian comparison example for equilibrium water (standalone).

This example investigates Hessian consistency issues between analytical and
finite-difference methods for an equilibrium water molecule. The equilibrium
geometry shows very large differences (~81 eV/Å²) between analytical and FD
Hessians, which is significantly worse than the distorted geometry.

Usage
-----
    python example_7.py

Requirements
------------
ASE, NumPy, PyTorch, and fairchem-core must be installed in the active
environment. The UMA pretrained weights are downloaded automatically via the
FairChem loader on first use.

Outputs
-------
The script prints finite-difference and analytical Hessian statistics to stdout
and saves a JSON summary in ``<script_stem>.json`` alongside the script. The
geometry is read from ``<script_stem>.xyz`` in the same directory, so the script
can be copied or renamed without modification.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from ase import units
from ase.io import read
from ase.vibrations import Vibrations

SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_STEM = SCRIPT_PATH.stem
# Find repository root (parent of examples/ directory)
REPO_ROOT = SCRIPT_PATH.parent.parent
HELPER_PATH = REPO_ROOT / "src" / "hessian_helpers.py"
HELPER_MODULE = "hessian_helpers"
helper_spec = importlib.util.spec_from_file_location(HELPER_MODULE, HELPER_PATH)
if helper_spec is None or helper_spec.loader is None:
    raise ImportError(f"Unable to load UMA helper from {HELPER_PATH}")
helper_module = importlib.util.module_from_spec(helper_spec)
sys.modules.setdefault(HELPER_MODULE, helper_module)
helper_spec.loader.exec_module(helper_module)
get_uma_calculator = helper_module.get_uma_calculator
get_uma_calculator_with_inference_settings = (
    helper_module.get_uma_calculator_with_inference_settings
)
get_uma_calculator_with_dtype = helper_module.get_uma_calculator_with_dtype

STRUCTURE_PATH = REPO_ROOT / "data" / f"{SCRIPT_STEM}.xyz"
OUTPUT_PATH = REPO_ROOT / "results" / f"{SCRIPT_STEM}.json"


@dataclass
class FrequencySummary:
    min_frequency: float
    max_frequency: float
    mean_abs_frequency: float
    n_negative: int
    n_small_negative: int


def compute_frequencies_cm(hessian: np.ndarray, masses: np.ndarray) -> np.ndarray:
    """Convert Hessian (eV/Å²) to vibrational frequencies in cm⁻¹."""
    mass_matrix = np.kron(np.diag(1.0 / np.sqrt(masses)), np.eye(3))
    mass_weighted = mass_matrix @ hessian @ mass_matrix
    eigenvalues, _ = np.linalg.eigh(mass_weighted)

    # ASE scaling factor (see ase.vibrations)
    scale = units._hbar * 1e10 / np.sqrt(units._e * units._amu)
    hnu = scale * np.sqrt(eigenvalues.astype(complex))
    freqs_cm = np.abs(hnu / units.invcm)
    freqs_cm[eigenvalues < 0] *= -1
    return freqs_cm


def summarize_frequencies(freqs_cm: np.ndarray) -> FrequencySummary:
    """Create simple statistics for a frequency spectrum."""
    vib = freqs_cm[6:] if freqs_cm.size > 6 else freqs_cm
    neg = vib[vib < 0.0]
    return FrequencySummary(
        min_frequency=float(np.min(vib)),
        max_frequency=float(np.max(vib)),
        mean_abs_frequency=float(np.mean(np.abs(vib))),
        n_negative=int(neg.size),
        n_small_negative=int(np.sum(neg > -50.0)),
    )


def compute_metrics(analytical: np.ndarray, reference: np.ndarray) -> dict[str, float]:
    """Return Hessian error metrics relative to a reference Hessian."""
    diff = analytical - reference
    abs_diff = np.abs(diff)
    return {
        "rms_error": float(np.sqrt(np.mean(diff**2))),
        "mean_absolute_error": float(np.mean(abs_diff)),
        "max_absolute_error": float(np.max(abs_diff)),
    }


def enforce_python_ints(atoms) -> None:
    """Ensure UMA-required metadata use Python ints (avoids numpy scalar issues)."""
    atoms.info["charge"] = int(atoms.info.get("charge", 0))
    atoms.info["spin"] = int(atoms.info.get("spin", 1))


def compute_finite_difference_hessian(atoms, calculator, delta: float) -> tuple[np.ndarray, float]:
    """Compute Hessian using ASE's Vibrations class with central differences."""
    # Ensure calculator is set
    atoms_copy = atoms.copy()
    atoms_copy.calc = calculator
    enforce_python_ints(atoms_copy)

    # Use ASE Vibrations class for finite difference Hessian
    # Create temporary name to avoid cache conflicts
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        vib = Vibrations(atoms_copy, delta=delta, name=os.path.join(tmpdir, "vib"))
        vib.run()
        vib.read()
        hessian = vib.H.copy()
        # Clean up cache to free memory
        vib.clean()

    # Compute symmetry error before any additional symmetrization
    # (ASE already symmetrizes in read(), but check anyway)
    symmetry_error = float(np.max(np.abs(hessian - hessian.T)))
    return hessian, symmetry_error


def ensure_charge_spin(atoms) -> None:
    """Set charge/spin required by UMA if missing."""
    atoms.info["charge"] = int(atoms.info.get("charge", 0))
    atoms.info["spin"] = int(atoms.info.get("spin", 1))


def select_device() -> str:
    """Pick CUDA when available, otherwise CPU."""
    try:
        import torch

        if torch.cuda.is_available():  # type: ignore[attr-defined]
            return "cuda"
    except Exception:
        pass
    return "cpu"


def main() -> None:
    if not STRUCTURE_PATH.exists():
        raise SystemExit(f"Structure not found: {STRUCTURE_PATH}")

    atoms = read(STRUCTURE_PATH)
    ensure_charge_spin(atoms)

    device = select_device()
    calc = get_uma_calculator(model_name="uma-s-1p1", device=device)
    calc.ensure_loaded()
    atoms.calc = calc

    masses = atoms.get_masses()

    report: dict[str, Any] = {
        "structure": str(STRUCTURE_PATH.name),
        "n_atoms": len(atoms),
        "device": device,
    }

    # ------------------------------------------------------------------
    # Finite-difference Hessians
    # ------------------------------------------------------------------
    fd_steps = [0.05, 0.01, 0.005, 0.001]
    fd_results: list[dict[str, Any]] = []

    for delta in fd_steps:
        hessian, symmetry_error = compute_finite_difference_hessian(atoms, calc, delta)
        freqs = compute_frequencies_cm(hessian, masses)
        fd_results.append(
            {
                "delta": float(delta),
                "hessian": hessian,
                "symmetry_error": symmetry_error,
                "summary": summarize_frequencies(freqs),
            }
        )

    if not fd_results:
        raise RuntimeError("Failed to compute finite-difference Hessians")

    reference = fd_results[-1]  # smallest delta
    reference_hessian = reference["hessian"]
    reference_summary = reference["summary"]

    for entry in fd_results:
        if entry is reference:
            entry["metrics"] = None
        else:
            entry["metrics"] = compute_metrics(entry["hessian"], reference_hessian)

    # ------------------------------------------------------------------
    # Analytical (autodiff) Hessians
    # ------------------------------------------------------------------
    # These method labels align with FairChem PR #1361:
    #   - double_backward: direct ∂²E/∂r² via double backprop.
    #   - vmap: vectorised VJP of forces (matching their torch.vmap path).
    #   - fairchem / fairchem_loop: their calculator-internal implementation with
    #     and without vmap respectively.
    # Symmetrisation matches PR #1361's final step.
    analytical_results: list[dict[str, Any]] = []
    method_names = ["double_backward", "vmap", "fairchem", "fairchem_loop"]

    for method in method_names:
        for symmetrize in (True, False):
            try:
                hessian = calc.get_hessian(atoms, method=method, symmetrize=symmetrize)
            except Exception as exc:  # pragma: no cover - diagnostic
                analytical_results.append(
                    {
                        "method": method,
                        "symmetrize": symmetrize,
                        "error": str(exc),
                    }
                )
                continue

            symmetry_error = float(np.max(np.abs(hessian - hessian.T)))
            freqs = compute_frequencies_cm(hessian, masses)
            analytical_results.append(
                {
                    "method": method,
                    "symmetrize": symmetrize,
                    "symmetry_error": symmetry_error,
                    "summary": summarize_frequencies(freqs),
                    "metrics": compute_metrics(hessian, reference_hessian),
                }
            )

    # ------------------------------------------------------------------
    # Test new inference settings approaches
    # ------------------------------------------------------------------
    print("\nTesting new inference settings approaches...")

    # Test with InferenceSettings
    try:
        calc_inf = get_uma_calculator_with_inference_settings(
            model_name="uma-s-1p1",
            device=device,
            tf32=False,
            merge_mole=True,
            compile=False,
            activation_checkpointing=False,
            internal_graph_gen_version=2,
            external_graph_gen=False,
        )
        calc_inf.ensure_loaded()
        # Use a fresh atoms copy with no calculator reference to avoid graph reuse issues
        atoms_fresh = atoms.copy()
        atoms_fresh.calc = None
        hessian_inf = calc_inf.get_hessian(atoms_fresh, method="double_backward", symmetrize=True)
        symmetry_error = float(np.max(np.abs(hessian_inf - hessian_inf.T)))
        freqs = compute_frequencies_cm(hessian_inf, masses)
        analytical_results.append(
            {
                "method": "double_backward_inference_settings",
                "symmetrize": True,
                "symmetry_error": symmetry_error,
                "summary": summarize_frequencies(freqs),
                "metrics": compute_metrics(hessian_inf, reference_hessian),
            }
        )
        print("  ✓ InferenceSettings test completed")
    except Exception as exc:
        analytical_results.append(
            {
                "method": "double_backward_inference_settings",
                "symmetrize": True,
                "error": str(exc),
            }
        )
        print(f"  ✗ InferenceSettings test failed: {exc}")

    # Test with float64 dtype
    try:
        calc_f64 = get_uma_calculator_with_dtype(
            model_name="uma-s-1p1",
            dtype="float64",
            device=device,
        )
        # Use a fresh atoms copy with no calculator reference to avoid graph reuse issues
        atoms_fresh = atoms.copy()
        atoms_fresh.calc = None
        hessian_f64 = calc_f64.get_hessian(atoms_fresh, method="double_backward", symmetrize=True)
        symmetry_error = float(np.max(np.abs(hessian_f64 - hessian_f64.T)))
        freqs = compute_frequencies_cm(hessian_f64, masses)
        analytical_results.append(
            {
                "method": "double_backward_float64",
                "symmetrize": True,
                "symmetry_error": symmetry_error,
                "summary": summarize_frequencies(freqs),
                "metrics": compute_metrics(hessian_f64, reference_hessian),
            }
        )
        print("  ✓ float64 dtype test completed")
    except Exception as exc:
        analytical_results.append(
            {
                "method": "double_backward_float64",
                "symmetrize": True,
                "error": str(exc),
            }
        )
        print(f"  ✗ float64 dtype test failed: {exc}")

    # ------------------------------------------------------------------
    # Prepare JSON-friendly report
    # ------------------------------------------------------------------

    def serialise_summary(summary: FrequencySummary) -> dict[str, float | int]:
        return {
            "min_cm-1": summary.min_frequency,
            "max_cm-1": summary.max_frequency,
            "mean_abs_cm-1": summary.mean_abs_frequency,
            "n_negative": summary.n_negative,
            "n_small_negative": summary.n_small_negative,
        }

    def serialise_metrics(metrics: dict[str, float] | None) -> dict[str, float] | None:
        if metrics is None:
            return None
        return {
            "rms_error": metrics["rms_error"],
            "mean_absolute_error": metrics["mean_absolute_error"],
            "max_absolute_error": metrics["max_absolute_error"],
        }

    report["reference"] = {
        "source": "finite_difference",
        "delta": reference["delta"],
        "symmetry_error": reference["symmetry_error"],
        "summary": serialise_summary(reference_summary),
    }

    report["finite_differences"] = [
        {
            "delta": entry["delta"],
            "symmetry_error": entry["symmetry_error"],
            "summary": serialise_summary(entry["summary"]),
            **(
                {"metrics_vs_reference": serialise_metrics(entry["metrics"])}
                if entry["metrics"] is not None
                else {}
            ),
        }
        for entry in fd_results
    ]

    report["analytical_methods"] = [
        {
            "method": entry["method"],
            "symmetrize": entry["symmetrize"],
            "symmetry_error": entry.get("symmetry_error"),
            **({"summary": serialise_summary(entry["summary"])} if "summary" in entry else {}),
            **(
                {"metrics_vs_reference": serialise_metrics(entry.get("metrics"))}
                if entry.get("metrics") is not None
                else {}
            ),
            **({"error": entry["error"]} if "error" in entry else {}),
        }
        for entry in analytical_results
    ]

    # ------------------------------------------------------------------
    # Print concise tables
    # ------------------------------------------------------------------
    def format_summary(summary: FrequencySummary) -> str:
        return (
            f"min {summary.min_frequency:8.1f} cm⁻¹ | "
            f"max {summary.max_frequency:7.1f} cm⁻¹ | "
            f"neg {summary.n_negative:3d}"
        )

    def format_metrics(metrics: dict[str, float] | None) -> str:
        if metrics is None:
            return " "
        return f"RMS {metrics['rms_error']:8.3f} eV/Å² | MAE {metrics['mean_absolute_error']:7.3f}"

    ref_label = f"Δ={reference['delta']:.3f} Å"
    print(f"\nReference (finite difference {ref_label}):")
    print("  " + format_summary(reference_summary))

    print("\nFinite differences (vs reference):")
    for entry in fd_results:
        label = f"Δ={entry['delta']:.3f} Å"
        print(f"  {label:<14} {format_summary(entry['summary'])}")
        if entry["metrics"] is not None:
            print(f"    {format_metrics(entry['metrics'])}")

    print("\nAnalytical UMA methods (vs reference):")
    for entry in analytical_results:
        if "error" in entry:
            print(f"  {entry['method']:<14} sym={entry['symmetrize']} -> ERROR: {entry['error']}")
            continue
        label = f"{entry['method']:<14} sym={str(entry['symmetrize']).lower():<5}"
        print(f"  {label} {format_summary(entry['summary'])}")
        print(f"    {format_metrics(entry['metrics'])}")

    # ------------------------------------------------------------------
    # Persist summary JSON
    # ------------------------------------------------------------------
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved summary to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()