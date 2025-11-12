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
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.model_name = model_name
        self.device = device or _resolve_default_device()
        self.default_charge = int(default_charge)
        self.default_spin = int(default_spin)
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

        data = AtomicData.from_ase(
            atoms_copy,
            task_name="omol",
            r_edges=False,
            r_data_keys=["spin", "charge"],
        ).to(device)

        batch = data_list_collater([data], otf_graph=True).to(device)
        batch.pos = batch.pos.detach().clone().requires_grad_(True)

        self.predictor.model.train()

        # Disable dropout layers for deterministic outputs
        for module in self.predictor.model.modules():
            if getattr(module, "training", False) and hasattr(module, "p"):
                module.p = 0.0

        energy_head = None
        prev_energy_head_state = None
        model_module = getattr(self.predictor.model, "module", None)
        output_heads = getattr(model_module, "output_heads", None)
        if isinstance(output_heads, dict):
            energy_wrapper = output_heads.get("energyandforcehead")
            if energy_wrapper is not None and hasattr(energy_wrapper, "head"):
                energy_head = energy_wrapper.head
        if energy_head is not None:
            prev_energy_head_state = energy_head.training
            energy_head.training = True

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
            hessian_tensor = self._compute_hessian_vmap(forces, batch.pos)
        elif method in {"fairchem", "fairchem_vmap"}:
            hessian_tensor = self._compute_hessian_fairchem_style(
                result["forces"],
                batch.pos,
                use_vmap=True,
            )
        elif method == "fairchem_loop":
            hessian_tensor = self._compute_hessian_fairchem_style(
                result["forces"],
                batch.pos,
                use_vmap=False,
            )
        else:
            raise ValueError(
                f"Unknown Hessian method '{method}'. "
                "Use 'double_backward', 'vmap', 'fairchem', 'fairchem_loop', or 'auto'."
            )

        self.predictor.model.eval()
        if energy_head is not None and prev_energy_head_state is not None:
            energy_head.training = prev_energy_head_state

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

    def _compute_hessian_vmap(self, forces, positions) -> Any:
        """Compute Hessian using vector-Jacobian products with torch.vmap."""
        import torch

        forces_flat = forces.view(-1)
        num_elements = forces_flat.shape[0]

        def get_vjp(vec: torch.Tensor) -> torch.Tensor:
            grad_output = torch.autograd.grad(
                -forces_flat,
                positions,
                grad_outputs=vec,
                retain_graph=True,
                create_graph=False,
                allow_unused=False,
            )[0]
            return grad_output.view(-1)

        identity = torch.eye(num_elements, dtype=forces.dtype, device=forces.device)
        try:
            chunk = 1 if num_elements < 64 else 16
            return torch.vmap(get_vjp, in_dims=0, out_dims=0, chunk_size=chunk)(identity)
        except RuntimeError:
            return self._compute_hessian_loop(forces, positions)

    def _compute_hessian_loop(self, forces, positions) -> Any:
        """Fallback loop-based Hessian computation."""
        import torch

        forces_flat = forces.view(-1)
        num_elements = forces_flat.shape[0]
        rows = []
        for idx in range(num_elements):
            vec = torch.zeros(num_elements, dtype=forces.dtype, device=forces.device)
            vec[idx] = 1.0
            grad_output = torch.autograd.grad(
                -forces_flat,
                positions,
                grad_outputs=vec,
                retain_graph=True,
                create_graph=False,
                allow_unused=False,
            )[0]
            rows.append(grad_output.view(-1))
        return torch.stack(rows)

    def _compute_hessian_fairchem_style(self, forces, positions, *, use_vmap: bool) -> Any:
        """Replicate FairChem PR #1361 Hessian logic."""
        import torch

        forces_flat = forces.view(-1)
        num_dofs = forces_flat.shape[0]
        identity = torch.eye(num_dofs, dtype=forces_flat.dtype, device=forces_flat.device)

        def grad_wrt_positions(vec: torch.Tensor) -> torch.Tensor:
            grad_pos = torch.autograd.grad(
                -forces_flat,
                positions,
                grad_outputs=vec,
                retain_graph=True,
                allow_unused=False,
                create_graph=False,
            )[0]
            return grad_pos.reshape(-1)

        if use_vmap and hasattr(torch, "vmap"):
            try:
                chunk = 1 if num_dofs < 64 else 16
                return torch.vmap(
                    grad_wrt_positions,
                    in_dims=0,
                    out_dims=0,
                    chunk_size=chunk,
                )(identity)
            except RuntimeError:
                pass

        rows = [grad_wrt_positions(identity[idx]) for idx in range(num_dofs)]
        return torch.stack(rows, dim=0)

    @staticmethod
    def _symmetrize_hessian(hessian: np.ndarray) -> np.ndarray:
        """Return the symmetrized Hessian matrix."""
        return 0.5 * (hessian + hessian.T)


def get_uma_calculator(model_name: str = "uma-s-1p1", **kwargs: Any) -> StandaloneUMACalculator:
    """Convenience factory to match the original script signature."""
    return StandaloneUMACalculator(model_name=model_name, **kwargs)


__all__ = [
    "StandaloneUMACalculator",
    "get_uma_calculator",
]

