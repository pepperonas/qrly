"""Tests for version module"""

import re
from __version__ import __version__, get_version


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


def test_get_version_function():
    """Test that get_version() returns the correct version"""
    version = get_version()
    assert version == __version__
    assert isinstance(version, str)


def test_version_is_001():
    """Test that current version is 0.0.1"""
    assert __version__ == "0.0.1"
