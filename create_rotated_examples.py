#!/usr/bin/env python3
"""Create rotated versions of example_3 and example_7.

Applies a small random 3D rotation to the coordinates and saves as example_8 and example_9.
"""

import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"


def random_rotation_matrix(angle_degrees: float = 5.0) -> np.ndarray:
    """Generate a random 3D rotation matrix.
    
    Args:
        angle_degrees: Maximum rotation angle in degrees (default: 5 degrees)
    
    Returns:
        3x3 rotation matrix
    """
    # Generate random axis
    axis = np.random.randn(3)
    axis /= np.linalg.norm(axis)
    
    # Convert angle to radians
    angle_rad = np.deg2rad(angle_degrees)
    
    # Rodrigues' rotation formula
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    
    R = np.eye(3) + sin_a * K + (1 - cos_a) * np.dot(K, K)
    return R


def rotate_xyz_file(input_file: Path, output_file: Path, rotation_angle: float = 5.0) -> None:
    """Apply rotation to an XYZ file.
    
    Args:
        input_file: Path to input XYZ file
        output_file: Path to output XYZ file
        rotation_angle: Rotation angle in degrees
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Parse header
    n_atoms = int(lines[0].strip())
    header_lines = []
    data_start = 1
    
    # Check for properties line (like in example_7)
    if len(lines) > 1 and lines[1].strip().startswith("Properties="):
        header_lines.append(lines[1])
        data_start = 2
    
    # Parse atom coordinates - read exactly n_atoms non-empty lines
    atoms = []
    positions = []
    i = data_start
    while len(atoms) < n_atoms and i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:  # Skip empty lines
            continue
        parts = line.split()
        if len(parts) >= 4:
            atoms.append(parts[0])
            positions.append([float(parts[1]), float(parts[2]), float(parts[3])])
    
    if len(atoms) != n_atoms:
        raise ValueError(f"Expected {n_atoms} atoms, but found {len(atoms)}")
    
    positions = np.array(positions)
    
    # Center coordinates
    center = positions.mean(axis=0)
    positions_centered = positions - center
    
    # Apply rotation
    R = random_rotation_matrix(rotation_angle)
    positions_rotated = positions_centered @ R.T
    
    # Translate back
    positions_final = positions_rotated + center
    
    # Write output
    with open(output_file, 'w') as f:
        f.write(f"{n_atoms}\n")
        for header_line in header_lines:
            f.write(header_line)
        for atom, pos in zip(atoms, positions_final):
            f.write(f"{atom:2s} {pos[0]:20.15f} {pos[1]:20.15f} {pos[2]:20.15f}\n")
        f.write("\n")


def main():
    """Main entry point."""
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Create rotated versions
    print("Creating rotated versions of example_3 and example_7...")
    
    # Example 8: rotated example_3
    rotate_xyz_file(
        DATA_DIR / "example_3.xyz",
        DATA_DIR / "example_8.xyz",
        rotation_angle=5.0
    )
    print("✓ Created example_8.xyz (rotated example_3)")
    
    # Example 9: rotated example_7
    rotate_xyz_file(
        DATA_DIR / "example_7.xyz",
        DATA_DIR / "example_9.xyz",
        rotation_angle=5.0
    )
    print("✓ Created example_9.xyz (rotated example_7)")
    
    print("\nDone!")


if __name__ == "__main__":
    main()

