"""Basic tests for GUI components"""

import pytest
import sys


def test_gui_imports():
    """Test that GUI module can be imported"""
    try:
        import main_simple
        assert hasattr(main_simple, 'SimpleMainWindow')
        assert hasattr(main_simple, 'GeneratorThread')
        assert hasattr(main_simple, 'BatchGeneratorThread')
    except ImportError as e:
        pytest.skip(f"GUI dependencies not available: {e}")


def test_gui_version_import():
    """Test that GUI imports version correctly"""
    try:
        import main_simple
        # The module should import __version__
        assert hasattr(main_simple, '__version__')
    except ImportError as e:
        pytest.skip(f"GUI dependencies not available: {e}")


@pytest.mark.skip(reason="Requires display/X11 server - run manually if needed")
def test_gui_window_creation():
    """Test that main window can be created (skipped in CI)"""
    from PyQt6.QtWidgets import QApplication
    import main_simple

    app = QApplication(sys.argv)
    window = main_simple.SimpleMainWindow()

    # Basic checks
    assert window is not None
    assert window.windowTitle().startswith("QR Code 3D Generator")
    assert "0.0.1" in window.windowTitle()

    app.quit()
