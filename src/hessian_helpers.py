"""Standalone UMA helpers for reproducing Hessian analysis examples.

This module exposes ``StandaloneUMACalculator`` which mirrors the UMA portion of
QME while depending only on ASE, FairChem, NumPy and PyTorch.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from ase import Atoms
from ase.calculators.calculator import Calculator, CalculatorSetupError, all_changes


def _resolve_default_device() -> str:
    """Return ``cuda`` when available, otherwise ``cpu``."""
    try:
        import torch

        if torch.cuda.is_available():  # type: ignore[attr-defined]
            return "cuda"
    except Exception:
        pass
    return "cpu"


class StandaloneUMACalculator(Calculator):
    """Minimal UMA calculator implementing energy, forces, and analytical Hessians."""

    implemented_properties = ["energy", "forces", "hessian"]

    def __init__(
        self,
        model_name: str = "uma-s-1p1",
        *,
        device: str | None = None,
        default_charge: int = 0,
        default_spin: int = 1,
        inference_settings: Any | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.model_name = model_name
        self.device = device or _resolve_default_device()
        self.default_charge = int(default_charge)
        self.default_spin = int(default_spin)
        self.inference_settings = inference_settings
        self._calc: Any | None = None
        self.predictor: Any | None = None

    # ------------------------------------------------------------------
    # ASE calculator interface
    # ------------------------------------------------------------------
    def ensure_loaded(self) -> Any:
        """Ensure the underlying FairChem calculator and model are loaded."""
        if self._calc is None:
            self._load_calculator()
        return self._calc

    def calculate(
        self,
        atoms: Atoms | None = None,
        properties: Sequence[str] | None = None,
        system_changes: Sequence[str] = all_changes,
    ) -> None:
        """Delegate energy/force calculations to the FairChem calculator."""
        super().calculate(atoms, properties, system_changes)

        if self.atoms is None:
            raise ValueError("ASE calculator expects `atoms` to be provided")

        self._ensure_charge_spin(self.atoms)
        backend = self.ensure_loaded()

        atoms_copy = self.atoms.copy()
        self._ensure_charge_spin(atoms_copy)
        backend.calculate(atoms_copy, properties, system_changes)

        prop_list = list(properties) if properties is not None else self.implemented_properties
        if "energy" in prop_list and "energy" in backend.results:
            self.results["energy"] = float(backend.results["energy"])
        if "forces" in prop_list and "forces" in backend.results:
            self.results["forces"] = np.asarray(backend.results["forces"], dtype=float)

    # ------------------------------------------------------------------
    # Analytical Hessian
    # ------------------------------------------------------------------
    def get_hessian(
        self,
        atoms: Atoms | None = None,
        *,
        method: str = "auto",
        symmetrize: bool = True,
    ) -> np.ndarray:
        """Compute UMA analytical Hessian using PyTorch autograd."""
        if atoms is not None:
            self.atoms = atoms
        if self.atoms is None:
            raise ValueError("Atoms must be set before calling `get_hessian`")

        self._ensure_charge_spin(self.atoms)
        self.ensure_loaded()

        try:
            import torch
            from fairchem.core.datasets import data_list_collater
            from fairchem.core.datasets.atomic_data import AtomicData
        except ImportError as exc:
            msg = (
                "FairChem and PyTorch are required for UMA Hessian computations. "
                "Install fairchem-core and torch."
            )
            raise ImportError(msg) from exc

        if self.predictor is None:
            raise CalculatorSetupError("UMA predictor not loaded. Call `ensure_loaded()` first.")

        if method == "auto":
            method = "double_backward"

        device = next(self.predictor.model.parameters()).device

        atoms_copy = self.atoms.copy()
        self._ensure_charge_spin(atoms_copy)

        # Get model dtype to ensure data matches
        model_dtype = next(self.predictor.model.parameters()).dtype

        data = AtomicData.from_ase(
            atoms_copy,
            task_name="omol",
            r_edges=False,
            r_data_keys=["spin", "charge"],
        ).to(device)

        batch = data_list_collater([data], otf_graph=True).to(device)

        # Convert batch to match model dtype after collation
        # This ensures dtype consistency throughout the computation
        # The collater may create new tensors, so we convert after collation
        if batch.pos.dtype != model_dtype:
            batch.pos = batch.pos.to(dtype=model_dtype)
        if hasattr(batch, "cell") and batch.cell is not None and batch.cell.dtype != model_dtype:
            batch.cell = batch.cell.to(dtype=model_dtype)

        # Ensure positions have requires_grad=True for gradient computation
        # Note: otf_graph=True doesn't automatically set this, it's required for autograd
        batch.pos.requires_grad_(True)

        # Match FairChem's approach: only set head.training = True
        # Do NOT set model.train() or manually disable dropout
        # Turn on create_graph for the first derivative (matches FairChem)
        model_module = self.predictor.model.module
        energy_wrapper = model_module.output_heads["energyandforcehead"]
        prev_head_training = energy_wrapper.head.training
        energy_wrapper.head.training = True

        result = self.predictor.predict(batch)
        energy = result["energy"]

        if method == "double_backward":
            hessian_tensor = self._compute_hessian_double_backward(energy, batch.pos)
        elif method == "vmap":
            forces = -torch.autograd.grad(
                energy,
                batch.pos,
                create_graph=True,
                retain_graph=True,
            )[0]
            # Use fairchem_style with vmap (same algorithm)
            hessian_tensor = self._compute_hessian_fairchem_style(
                forces,
                batch.pos,
                use_vmap=True,
            )
        elif method in {"fairchem", "fairchem_vmap"}:
            # Use forces directly from predict() when head is in training mode
            # This matches the reference implementation which uses pred["forces"]
            # When head.training = True, forces should have computation graph
            forces = result["forces"]
            hessian_tensor = self._compute_hessian_fairchem_style(
                forces,
                batch.pos,
                use_vmap=True,
            )
        elif method == "fairchem_loop":
            # Use forces directly from predict() when head is in training mode
            # This matches the reference implementation which uses pred["forces"]
            # When head.training = True, forces should have computation graph
            forces = result["forces"]
            hessian_tensor = self._compute_hessian_fairchem_style(
                forces,
                batch.pos,
                use_vmap=False,
            )
        else:
            raise ValueError(
                f"Unknown Hessian method '{method}'. "
                "Use 'double_backward', 'vmap', 'fairchem', 'fairchem_loop', or 'auto'."
            )

        # Turn off create_graph for the first derivative (match FairChem's cleanup)
        energy_wrapper.head.training = prev_head_training

        n_atoms = len(self.atoms)
        expected_shape = (3 * n_atoms, 3 * n_atoms)

        if hessian_tensor.shape != expected_shape:
            total = hessian_tensor.numel()
            if total != expected_shape[0] * expected_shape[1]:
                raise ValueError(
                    f"Hessian tensor has unexpected shape {tuple(hessian_tensor.shape)}, "
                    f"expected {expected_shape}"
                )
            hessian_tensor = hessian_tensor.reshape(expected_shape)

        hessian_np = hessian_tensor.detach().cpu().numpy()

        if symmetrize:
            asymmetry = np.max(np.abs(hessian_np - hessian_np.T))
            if asymmetry > 1e-5:
                import warnings

                warnings.warn(
                    f"Hessian asymmetry detected (max deviation {asymmetry:.2e}); applying symmetrization.",
                    UserWarning,
                    stacklevel=2,
                )
            hessian_np = self._symmetrize_hessian(hessian_np)

        return hessian_np

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_calculator(self) -> None:
        """Load UMA predictor and FairChem calculator."""
        try:
            from fairchem.core import FAIRChemCalculator, pretrained_mlip
        except ImportError as exc:
            raise CalculatorSetupError(
                "Failed to import FairChem modules. Install fairchem-core."
            ) from exc

        device = "cuda" if self.device == "cuda" else "cpu"
        try:
            if self.inference_settings is not None:
                self.predictor = pretrained_mlip.get_predict_unit(
                    self.model_name, device=device, inference_settings=self.inference_settings
                )
            else:
                self.predictor = pretrained_mlip.get_predict_unit(self.model_name, device=device)
        except Exception as exc:
            raise CalculatorSetupError(
                f"Failed to load UMA model '{self.model_name}': {exc}"
            ) from exc

        self._set_model_precision("float32")

        try:
            self._calc = FAIRChemCalculator(self.predictor, task_name="omol")
        except Exception as exc:
            raise CalculatorSetupError(f"Failed to construct FairChem calculator: {exc}") from exc

    def _set_model_precision(self, precision: str) -> None:
        """Adjust predictor precision to avoid dtype mismatches."""
        if self.predictor is None:
            return
        model = getattr(self.predictor, "model", None)
        if model is None:
            return
        try:
            if precision == "float32" and hasattr(model, "float"):
                model.float()
            elif precision == "double" and hasattr(model, "double"):
                model.double()
        except Exception:
            pass

    def _ensure_charge_spin(self, atoms: Atoms) -> None:
        """Ensure charge and spin metadata are regular Python integers."""
        info = atoms.info
        info["charge"] = int(info.get("charge", self.default_charge))
        info["spin"] = int(info.get("spin", self.default_spin))

    def _compute_hessian_double_backward(self, energy, positions) -> Any:
        """Compute Hessian via double backward on the energy."""
        import torch

        n_atoms = positions.shape[0]
        num_elements = 3 * n_atoms

        forces = -torch.autograd.grad(
            energy,
            positions,
            create_graph=True,
            retain_graph=True,
        )[0]

        forces_flat = forces.view(-1)
        rows = []
        for idx in range(num_elements):
            hess_row = torch.autograd.grad(
                forces_flat[idx],
                positions,
                retain_graph=True,
                create_graph=False,
                allow_unused=False,
            )[0]
            rows.append((-hess_row).view(-1))
        return torch.stack(rows)

    def _compute_hessian_fairchem_style(self, forces, positions, *, use_vmap: bool) -> Any:
        """Replicate FairChem PR #1361 Hessian logic exactly."""
        import torch

        forces_flat = forces.flatten()
        num_dofs = forces_flat.shape[0]

        if use_vmap and hasattr(torch, "vmap"):
            # Match FairChem's vmap implementation exactly
            hessian = torch.vmap(
                lambda vec: torch.autograd.grad(
                    -forces_flat,
                    positions,
                    grad_outputs=vec,
                    retain_graph=True,
                )[0],
            )(torch.eye(num_dofs, dtype=forces_flat.dtype, device=forces_flat.device))
            return hessian
        else:
            # Match FairChem's non-vmap implementation exactly
            # Compute gradient of each force component separately
            hessian_list = []
            for i in range(num_dofs):
                grad_pos = torch.autograd.grad(
                    -forces_flat[i],
                    positions,
                    retain_graph=True,
                )[0]
                hessian_list.append(grad_pos.flatten())
            return torch.stack(hessian_list, dim=0)

    @staticmethod
    def _symmetrize_hessian(hessian: np.ndarray) -> np.ndarray:
        """Return the symmetrized Hessian matrix."""
        return 0.5 * (hessian + hessian.T)


def get_uma_calculator(model_name: str = "uma-s-1p1", **kwargs: Any) -> StandaloneUMACalculator:
    """Create a convenience factory to match the original script signature."""
    return StandaloneUMACalculator(model_name=model_name, **kwargs)


def get_uma_calculator_with_inference_settings(
    model_name: str = "uma-s-1p1",
    *,
    tf32: bool = False,
    merge_mole: bool = True,
    compile: bool = False,
    activation_checkpointing: bool = False,
    internal_graph_gen_version: int = 2,
    external_graph_gen: bool = False,
    device: str | None = None,
    **kwargs: Any,
) -> StandaloneUMACalculator:
    """Create UMA calculator with custom InferenceSettings.

    Parameters
    ----------
    model_name : str
        UMA model name (default: "uma-s-1p1")
    tf32 : bool
        Enable TensorFloat-32 (default: False)
    merge_mole : bool
        Merge molecular operations (default: True)
    compile : bool
        Enable torch.compile (default: False)
    activation_checkpointing : bool
        Enable activation checkpointing (default: False)
    internal_graph_gen_version : int
        Internal graph generation version (default: 2)
    external_graph_gen : bool
        Use external graph generation (default: False)
    device : str | None
        Device to use ("cuda" or "cpu", default: auto-detect)
    **kwargs
        Additional arguments passed to StandaloneUMACalculator

    Returns
    -------
    StandaloneUMACalculator
        Calculator instance with specified inference settings
    """
    try:
        from fairchem.core.units.mlip_unit import InferenceSettings
    except ImportError:
        # Fallback: try alternative import path
        try:
            from fairchem.core import InferenceSettings
        except ImportError:
            raise ImportError(
                "InferenceSettings not found. Update fairchem-core to a version that supports it."
            ) from None

    inference_settings = InferenceSettings(
        tf32=tf32,
        merge_mole=merge_mole,
        compile=compile,
        activation_checkpointing=activation_checkpointing,
        internal_graph_gen_version=internal_graph_gen_version,
        external_graph_gen=external_graph_gen,
    )

    return StandaloneUMACalculator(
        model_name=model_name,
        device=device,
        inference_settings=inference_settings,
        **kwargs,
    )


def get_uma_calculator_with_dtype(
    model_name: str = "uma-s-1p1",
    *,
    dtype: str = "float32",
    device: str | None = None,
    **kwargs: Any,
) -> StandaloneUMACalculator:
    """Create UMA calculator and set model to specified dtype.

    Parameters
    ----------
    model_name : str
        UMA model name (default: "uma-s-1p1")
    dtype : str
        Model dtype: "float32", "float64", or "double" (default: "float32")
    device : str | None
        Device to use ("cuda" or "cpu", default: auto-detect)
    **kwargs
        Additional arguments passed to StandaloneUMACalculator

    Returns
    -------
    StandaloneUMACalculator
        Calculator instance with model set to specified dtype
    """
    calc = StandaloneUMACalculator(model_name=model_name, device=device, **kwargs)
    calc.ensure_loaded()

    # Set model precision after loading
    if dtype in ("float64", "double"):
        calc._set_model_precision("double")
    else:
        calc._set_model_precision("float32")

    return calc


__all__ = [
    "StandaloneUMACalculator",
    "get_uma_calculator",
    "get_uma_calculator_with_inference_settings",
    "get_uma_calculator_with_dtype",
]
