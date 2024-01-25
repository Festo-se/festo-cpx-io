"""Test the examples"""

import subprocess


def test_example_cpxap_iolink_sdas():
    """Test example for CPX-AP"""
    result = subprocess.run(
        ["python3", "examples/example_cpxap_iolink_sdas.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0, f"Script failed with output: {result.stdout}"


def test_example_cpxap():
    """Test example for CPX-AP"""
    result = subprocess.run(
        ["python3", "examples/example_cpxap.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0, f"Script failed with output: {result.stdout}"


def test_example_cpxe_add_module():
    """Test example for CPX-E"""
    result = subprocess.run(
        ["python3", "examples/example_cpxe_add_module.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0, f"Script failed with output: {result.stdout}"


def test_example_cpxe_iolink_ehps():
    """Test example for CPX-E"""
    result = subprocess.run(
        ["python3", "examples/example_cpxe_iolink_ehps.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0, f"Script failed with output: {result.stdout}"


def test_example_cpxe_iolink_sdas():
    """Test example for CPX-E"""
    result = subprocess.run(
        ["python3", "examples/example_cpxe_iolink_sdas.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0, f"Script failed with output: {result.stdout}"


def test_example_cpxe_modulelist():
    """Test example for CPX-E"""
    result = subprocess.run(
        ["python3", "examples/example_cpxe_modulelist.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0, f"Script failed with output: {result.stdout}"


def test_example_cpxe_typecode():
    """Test example for CPX-E"""
    result = subprocess.run(
        ["python3", "examples/example_cpxe_typecode.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0, f"Script failed with output: {result.stdout}"
