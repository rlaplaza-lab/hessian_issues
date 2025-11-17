#!/usr/bin/env python3
"""Test intermediate fairchem-core versions to identify when changes were introduced.

This script creates conda environments for intermediate versions, runs examples,
and generates comparison reports.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# Versions to test (between 2.7.1 and 2.11.0)
VERSIONS_TO_TEST = ["2.8.0", "2.10.0"]
BASE_ENV = "py312"


def run_command(cmd: list[str], check: bool = True) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            print(f"Command failed: {' '.join(cmd)}")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return False


def create_env_for_version(version: str) -> bool:
    """Create a conda environment cloned from base with specific fairchem-core version."""
    env_name = f"{BASE_ENV}-fairchem{version.replace('.', '')}"
    
    print(f"\n{'='*60}")
    print(f"Creating environment: {env_name} with fairchem-core {version}")
    print(f"{'='*60}")
    
    # Check if environment already exists
    result = subprocess.run(
        ["conda", "env", "list"],
        capture_output=True,
        text=True,
        check=True
    )
    if env_name in result.stdout:
        print(f"Environment {env_name} already exists. Skipping creation.")
        return True
    
    # Clone base environment
    if not run_command(["conda", "create", "--name", env_name, "--clone", BASE_ENV, "-y"]):
        return False
    
    # Install specific fairchem-core version
    print(f"Installing fairchem-core {version}...")
    install_cmd = [
        "conda", "run", "-n", env_name,
        "pip", "install", f"fairchem-core=={version}"
    ]
    if not run_command(install_cmd):
        print(f"Warning: Failed to install fairchem-core {version}")
        return False
    
    print(f"✓ Environment {env_name} created successfully")
    return True


def run_examples_in_env(env_name: str, version: str) -> bool:
    """Run all examples in the specified environment."""
    print(f"\n{'='*60}")
    print(f"Running examples in {env_name} (fairchem-core {version})")
    print(f"{'='*60}")
    
    # Verify version first
    verify_cmd = ["conda", "run", "-n", env_name, "python", "-m", "pip", "show", "fairchem-core"]
    result = subprocess.run(verify_cmd, capture_output=True, text=True, check=True)
    for line in result.stdout.split("\n"):
        if line.startswith("Version:"):
            installed_version = line.split(":", 1)[1].strip()
            print(f"Installed fairchem-core version: {installed_version}")
            break
    
    # Run each example script
    examples_dir = REPO_ROOT / "examples"
    success_count = 0
    for i in range(1, 8):
        example_file = examples_dir / f"example_{i}.py"
        if not example_file.exists():
            print(f"Warning: {example_file} does not exist, skipping")
            continue
        
        print(f"\nRunning example_{i}.py...")
        cmd = ["conda", "run", "-n", env_name, "python", str(example_file)]
        if run_command(cmd, check=False):
            success_count += 1
            print(f"✓ example_{i}.py completed")
        else:
            print(f"✗ example_{i}.py failed")
    
    print(f"\nCompleted {success_count}/7 examples")
    return success_count > 0


def generate_summary_for_version(env_name: str, version: str) -> bool:
    """Generate summary for a specific version."""
    print(f"\nGenerating summary for fairchem-core {version}...")
    
    # Import and use the generate_summary logic directly
    # We'll create a simple script that can be run in the conda environment
    summary_code = '''import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = REPO_ROOT / "results"

def get_fairchem_version():
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "fairchem-core"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.split("\\n"):
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
        return "Unknown"
    except Exception:
        return "Unknown"

def load_results():
    results = {}
    for i in range(1, 8):
        result_file = RESULTS_DIR / f"example_{i}.json"
        if result_file.exists():
            with open(result_file, "r") as f:
                results[f"example_{i}"] = json.load(f)
    return results

def format_number(value, precision=3):
    if value is None:
        return "N/A"
    return f"{value:.{precision}f}"

def get_best_method(result):
    best = None
    best_rms = float("inf")
    for method in result.get("analytical_methods", []):
        if "error" in method:
            continue
        metrics = method.get("metrics_vs_reference")
        if metrics and metrics.get("rms_error") is not None:
            rms = metrics["rms_error"]
            if rms < best_rms:
                best_rms = rms
                best = method
    return best

version = get_fairchem_version()
results = load_results()

output_file = REPO_ROOT / f"summary_fairchem{version.replace('.', '')}.md"

lines = [
    "# UMA Hessian Analysis Summary",
    "",
    f"**FairChem-Core Version:** {version}",
    f"**Number of Examples:** {len(results)}",
    "",
    "---",
    "",
    "## Summary Table",
    "",
    "| Example | Structure | Atoms | Device | Best Method | RMS Error | MAE | Max Error | Neg Freqs |",
    "|---------|-----------|-------|--------|-------------|-----------|-----|-----------|-----------|",
]

for example_name in sorted(results.keys()):
    result = results[example_name]
    structure = result.get("structure", "N/A")
    n_atoms = result.get("n_atoms", "N/A")
    device = result.get("device", "N/A")
    
    best_method = get_best_method(result)
    if best_method:
        method_name = best_method.get("method", "N/A")
        sym = "sym" if best_method.get("symmetrize", False) else "no-sym"
        method_label = f"{method_name} ({sym})"
        metrics = best_method.get("metrics_vs_reference", {})
        rms = format_number(metrics.get("rms_error"))
        mae = format_number(metrics.get("mean_absolute_error"))
        max_err = format_number(metrics.get("max_absolute_error"))
        summary = best_method.get("summary", {})
        n_neg = summary.get("n_negative", "N/A")
    else:
        method_label = "Failed"
        rms = "N/A"
        mae = "N/A"
        max_err = "N/A"
        n_neg = "N/A"
    
    lines.append(
        f"| {example_name} | {structure} | {n_atoms} | {device} | {method_label} | {rms} | {mae} | {max_err} | {n_neg} |"
    )

output_file.write_text("\\n".join(lines), encoding="utf-8")
print(f"Summary saved to: {output_file}")
'''
    
    summary_script = REPO_ROOT / "generate_summary_temp.py"
    summary_script.write_text(summary_code)
    summary_script.chmod(0o755)
    
    try:
        cmd = ["conda", "run", "-n", env_name, "python", str(summary_script)]
        success = run_command(cmd)
        return success
    finally:
        # Clean up temp script
        if summary_script.exists():
            summary_script.unlink()


def main():
    """Main entry point."""
    print("=" * 60)
    print("Testing Intermediate FairChem-Core Versions")
    print("=" * 60)
    
    for version in VERSIONS_TO_TEST:
        env_name = f"{BASE_ENV}-fairchem{version.replace('.', '')}"
        
        # Create environment
        if not create_env_for_version(version):
            print(f"✗ Failed to create environment for version {version}")
            continue
        
        # Run examples
        if not run_examples_in_env(env_name, version):
            print(f"✗ Failed to run examples for version {version}")
            continue
        
        # Generate summary
        if not generate_summary_for_version(env_name, version):
            print(f"✗ Failed to generate summary for version {version}")
            continue
        
        print(f"\n✓ Completed testing for fairchem-core {version}")
    
    print("\n" + "=" * 60)
    print("All intermediate versions tested!")
    print("=" * 60)
    print("\nCheck the summary files to compare results:")
    for version in VERSIONS_TO_TEST:
        safe_version = version.replace(".", "")
        print(f"  - summary_fairchem{safe_version}.md")


if __name__ == "__main__":
    main()

