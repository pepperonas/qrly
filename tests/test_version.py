"""Tests for version module"""

import re
from qrly import __version__


def test_version_exists():
    """Test that version string exists"""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_version_format():
    """Test that version follows semantic versioning format"""
    # Semantic versioning pattern: MAJOR.MINOR.PATCH
    pattern = r'^\d+\.\d+\.\d+$'
    assert re.match(pattern, __version__), f"Version '{__version__}' does not match semantic versioning format"


def test_version_is_032():
    """Test that current version is 0.3.2"""
    assert __version__ == "0.3.2"
