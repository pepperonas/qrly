"""Tests for QR model generator"""

import os
import tempfile
from pathlib import Path
import pytest
from qrly.generator import QRModelGenerator


def test_is_url():
    """Test URL detection"""
    # Valid URLs
    assert QRModelGenerator.is_url("https://example.com")
    assert QRModelGenerator.is_url("http://example.com")
    assert QRModelGenerator.is_url("https://github.com/user/repo")

    # Invalid URLs
    assert not QRModelGenerator.is_url("/path/to/file.png")
    assert not QRModelGenerator.is_url("file.png")
    assert not QRModelGenerator.is_url("example.com")  # No protocol


def test_generator_initialization():
    """Test that generator initializes with correct defaults"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        generator = QRModelGenerator(tmp_path, "square", "generated")

        # Check default parameters
        assert generator.card_width == 55
        assert generator.card_height == 0.5  # Default: dünn (thin)
        assert generator.qr_margin == 2.0  # Current default
        assert generator.qr_relief == 0.5  # Default: dünn (thin)
        assert generator.corner_radius == 2
        assert generator.mode == "square"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_generator_modes():
    """Test that all supported modes are valid"""
    valid_modes = ["square", "pendant", "rectangle-text", "pendant-text"]

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        for mode in valid_modes:
            generator = QRModelGenerator(tmp_path, mode, "generated")
            assert generator.mode == mode
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_generate_qr_image():
    """Test QR code image generation from URL"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_qr.png"

        # Generate QR code
        QRModelGenerator.generate_qr_image("https://example.com", output_path)

        # Check that file was created
        assert output_path.exists()
        assert output_path.stat().st_size > 0


def test_qr_code_generation_with_url():
    """Test that URL input generates QR code correctly"""
    url = "https://example.com"
    assert QRModelGenerator.is_url(url)

    # This would be tested in integration tests
    # as it requires OpenSCAD to be installed


def test_custom_parameters():
    """Test setting custom parameters"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        generator = QRModelGenerator(tmp_path, "square", "generated")

        # Set custom parameters
        generator.card_height = 2.0
        generator.qr_margin = 1.0
        generator.qr_relief = 1.5
        generator.corner_radius = 3

        # Verify they were set
        assert generator.card_height == 2.0
        assert generator.qr_margin == 1.0
        assert generator.qr_relief == 1.5
        assert generator.corner_radius == 3
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_text_parameters():
    """Test text-related parameters"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        generator = QRModelGenerator(tmp_path, "rectangle-text", "generated")

        # Set text parameters
        generator.text_content = "TEST"
        generator.text_rotation = 180

        # Verify they were set
        assert generator.text_content == "TEST"
        assert generator.text_rotation == 180
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
