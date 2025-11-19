#!/usr/bin/env python3
"""Verify that rotations preserve internal coordinates.

This script checks that bond lengths, bond angles, and dihedral angles
are preserved after rotation (within numerical precision).
"""

import numpy as np
from pathlib import Path
from typing import Tuple

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"


def read_xyz(file_path: Path) -> Tuple[list[str], np.ndarray]:
    """Read XYZ file and return atom symbols and positions.
    
    Returns:
        Tuple of (atom_symbols, positions_array)
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    n_atoms = int(lines[0].strip())
    data_start = 1
    
    # Check for properties line
    if len(lines) > 1 and lines[1].strip().startswith("Properties="):
        data_start = 2
    
    atoms = []
    positions = []
    i = data_start
    while len(atoms) < n_atoms and i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 4:
            atoms.append(parts[0])
            positions.append([float(parts[1]), float(parts[2]), float(parts[3])])
    
    if len(atoms) != n_atoms:
        raise ValueError(f"Expected {n_atoms} atoms, but found {len(atoms)}")
    
    return atoms, np.array(positions)


def compute_bond_lengths(positions: np.ndarray) -> dict[Tuple[int, int], float]:
    """Compute all pairwise bond lengths.
    
    Returns:
        Dictionary mapping (i, j) pairs to distances (i < j)
    """
    n = len(positions)
    bond_lengths = {}
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.linalg.norm(positions[i] - positions[j])
            bond_lengths[(i, j)] = dist
    return bond_lengths


def compute_bond_angles(positions: np.ndarray) -> dict[Tuple[int, int, int], float]:
    """Compute all bond angles.
    
    For atoms i-j-k, computes angle at j.
    
    Returns:
        Dictionary mapping (i, j, k) triplets to angles in radians
    """
    n = len(positions)
    angles = {}
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for k in range(j + 1, n):
                if k == i or k == j:
                    continue
                # Angle at j between vectors j->i and j->k
                vec1 = positions[i] - positions[j]
                vec2 = positions[k] - positions[j]
                cos_angle = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Handle numerical errors
                angle = np.arccos(cos_angle)
                # Store both orderings
                angles[(i, j, k)] = angle
                angles[(k, j, i)] = angle
    return angles


def compute_dihedral_angles(positions: np.ndarray) -> dict[Tuple[int, int, int, int], float]:
    """Compute all dihedral angles.
    
    For atoms i-j-k-l, computes dihedral angle around j-k bond.
    
    Returns:
        Dictionary mapping (i, j, k, l) quadruplets to angles in radians
    """
    n = len(positions)
    dihedrals = {}
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for k in range(n):
                if k == i or k == j:
                    continue
                for l in range(n):
                    if l == i or l == j or l == k:
                        continue
                    # Dihedral angle around j-k bond
                    b1 = positions[j] - positions[i]
                    b2 = positions[k] - positions[j]
                    b3 = positions[l] - positions[k]
                    
                    n1 = np.cross(b1, b2)
                    n2 = np.cross(b2, b3)
                    
                    n1_norm = np.linalg.norm(n1)
                    n2_norm = np.linalg.norm(n2)
                    
                    if n1_norm < 1e-10 or n2_norm < 1e-10:
                        continue  # Skip if vectors are collinear
                    
                    cos_dihedral = np.dot(n1, n2) / (n1_norm * n2_norm)
                    cos_dihedral = np.clip(cos_dihedral, -1.0, 1.0)
                    dihedral = np.arccos(cos_dihedral)
                    
                    # Determine sign
                    sign = np.sign(np.dot(np.cross(n1, n2), b2))
                    dihedral *= sign
                    
                    dihedrals[(i, j, k, l)] = dihedral
    return dihedrals


def compare_internal_coordinates(
    atoms1: list[str],
    pos1: np.ndarray,
    atoms2: list[str],
    pos2: np.ndarray,
    tolerance: float = 1e-10,
) -> bool:
    """Compare internal coordinates between two structures.
    
    Returns:
        True if all internal coordinates match within tolerance
    """
    if len(atoms1) != len(atoms2):
        print(f"ERROR: Different number of atoms: {len(atoms1)} vs {len(atoms2)}")
        return False
    
    if atoms1 != atoms2:
        print(f"ERROR: Different atom types")
        return False
    
    # Compare bond lengths
    bonds1 = compute_bond_lengths(pos1)
    bonds2 = compute_bond_lengths(pos2)
    
    if set(bonds1.keys()) != set(bonds2.keys()):
        print(f"ERROR: Different bond pairs")
        return False
    
    max_bond_diff = 0.0
    for key in bonds1:
        diff = abs(bonds1[key] - bonds2[key])
        max_bond_diff = max(max_bond_diff, diff)
        if diff > tolerance:
            print(f"ERROR: Bond length mismatch for {key}: {bonds1[key]:.15f} vs {bonds2[key]:.15f} (diff: {diff:.2e})")
            return False
    
    print(f"✓ Bond lengths preserved (max diff: {max_bond_diff:.2e})")
    
    # Compare bond angles
    angles1 = compute_bond_angles(pos1)
    angles2 = compute_bond_angles(pos2)
    
    # Only compare unique angles (i < j < k)
    unique_angles1 = {k: v for k, v in angles1.items() if k[0] < k[2]}
    unique_angles2 = {k: v for k, v in angles2.items() if k[0] < k[2]}
    
    if set(unique_angles1.keys()) != set(unique_angles2.keys()):
        print(f"ERROR: Different angle triplets")
        return False
    
    max_angle_diff = 0.0
    for key in unique_angles1:
        diff = abs(unique_angles1[key] - unique_angles2[key])
        max_angle_diff = max(max_angle_diff, diff)
        if diff > tolerance:
            print(f"ERROR: Bond angle mismatch for {key}: {unique_angles1[key]:.15f} vs {unique_angles2[key]:.15f} (diff: {diff:.2e})")
            return False
    
    print(f"✓ Bond angles preserved (max diff: {max_angle_diff:.2e})")
    
    # Compare dihedral angles (if we have enough atoms)
    if len(pos1) >= 4:
        dihedrals1 = compute_dihedral_angles(pos1)
        dihedrals2 = compute_dihedral_angles(pos2)
        
        # Only compare unique dihedrals (i < j < k < l)
        unique_dihedrals1 = {k: v for k, v in dihedrals1.items() if k[0] < k[1] < k[2] < k[3]}
        unique_dihedrals2 = {k: v for k, v in dihedrals2.items() if k[0] < k[1] < k[2] < k[3]}
        
        if len(unique_dihedrals1) > 0 and len(unique_dihedrals2) > 0:
            if set(unique_dihedrals1.keys()) != set(unique_dihedrals2.keys()):
                print(f"WARNING: Different dihedral quadruplets (this may be OK)")
            else:
                max_dihedral_diff = 0.0
                for key in unique_dihedrals1:
                    diff = abs(unique_dihedrals1[key] - unique_dihedrals2[key])
                    # Handle angle wraparound (angles are periodic)
                    diff = min(diff, 2 * np.pi - diff)
                    max_dihedral_diff = max(max_dihedral_diff, diff)
                    if diff > tolerance:
                        print(f"ERROR: Dihedral angle mismatch for {key}: {unique_dihedrals1[key]:.15f} vs {unique_dihedrals2[key]:.15f} (diff: {diff:.2e})")
                        return False
                
                print(f"✓ Dihedral angles preserved (max diff: {max_dihedral_diff:.2e})")
    
    return True


def main():
    """Main entry point."""
    print("=" * 60)
    print("Verifying rotations preserve internal coordinates")
    print("=" * 60)
    
    # Check example_3 vs example_8
    print("\nChecking example_3.xyz vs example_8.xyz:")
    print("-" * 60)
    atoms3, pos3 = read_xyz(DATA_DIR / "example_3.xyz")
    atoms8, pos8 = read_xyz(DATA_DIR / "example_8.xyz")
    
    print(f"Original: {len(atoms3)} atoms")
    print(f"Rotated:  {len(atoms8)} atoms")
    
    if compare_internal_coordinates(atoms3, pos3, atoms8, pos8):
        print("✓ example_8 preserves all internal coordinates")
    else:
        print("✗ example_8 FAILED verification")
        return 1
    
    # Check example_7 vs example_9
    print("\nChecking example_7.xyz vs example_9.xyz:")
    print("-" * 60)
    atoms7, pos7 = read_xyz(DATA_DIR / "example_7.xyz")
    atoms9, pos9 = read_xyz(DATA_DIR / "example_9.xyz")
    
    print(f"Original: {len(atoms7)} atoms")
    print(f"Rotated:  {len(atoms9)} atoms")
    
    if compare_internal_coordinates(atoms7, pos7, atoms9, pos9):
        print("✓ example_9 preserves all internal coordinates")
    else:
        print("✗ example_9 FAILED verification")
        return 1
    
    print("\n" + "=" * 60)
    print("All rotations verified successfully!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

