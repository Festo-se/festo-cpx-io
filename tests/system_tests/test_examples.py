"""Test the examples"""

import subprocess


def test_example_e():
    """Test example for CPX-E"""
    result = subprocess.run(
        ["python3", "examples/example_e.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0, f"Script failed with output: {result.stdout}"


def test_example_ap():
    """Test example for CPX-E"""
    result = subprocess.run(
        ["python3", "examples/example_ap.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0, f"Script failed with output: {result.stdout}"
