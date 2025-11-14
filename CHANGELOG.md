# Changelog

All notable changes to the QR Code 3D Model Generator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-11-14

### Added
- **🗺️ Google Review QR Codes**: Simple Place ID workflow for generating direct Google Business review links
  - New `google_review.py` module with Place ID validation
  - `--place-id` CLI argument for direct Place ID input
  - GUI: Place ID input field with help button
  - Batch processing support for Place IDs
  - `CELOX_IO_ANLEITUNG.md`: Complete guide for obtaining Place IDs without API

### Changed
- **Simplified Google Maps Integration**: Removed complex URL parsing
  - Only accepts Place IDs (ChIJ... or EI...)
  - No automatic URL parsing (reduces complexity and improves reliability)
  - Clear error messages with instructions on obtaining Place IDs
- **Clean Architecture**: Removed unused Google Maps modules
  - Deleted `google_maps_utils.py` (complex URL parser)
  - Deleted `google_review_qr.py` (complex integration layer)
  - Deleted `test_google_maps.py` (obsolete tests)
  - Deleted `GOOGLE_REVIEW_WORKFLOW.md` and `WORKFLOW_OHNE_API.md` (consolidated into `CELOX_IO_ANLEITUNG.md`)

### Improved
- More reliable review link generation (Place IDs always work)
- Simpler user workflow (get Place ID, paste, done)
- Better error messages with actionable instructions
- Cleaner codebase (removed ~1500 lines of complex parsing code)

### Documentation
- Updated README with simplified Google Review section
- Added three methods for obtaining Place IDs (Official Finder, Browser Inspector, Business Dashboard)
- Created `CELOX_IO_ANLEITUNG.md` with step-by-step German instructions

---

## [0.1.0] - 2025-11-11

### Changed - BREAKING: Project Reorganization

**Major restructuring to Python src-layout standard**. This is a breaking change for development workflows but maintains end-user functionality.

#### Project Structure
- **BREAKING**: Reorganized codebase to Python src-layout standard:
  - Moved `main_simple.py` → `src/qr3d/app.py`
  - Moved `generate_qr_model.py` → `src/qr3d/generator.py`
  - Moved `__version__.py` → `src/qr3d/__init__.py` (with `__version__ = "0.1.0"`)
  - Moved `qr_generate.sh` → `scripts/qr_generate.sh`
  - Moved `ui/` → `src/qr3d/gui/`
- Created proper Python package structure with `src/qr3d/` namespace
- Added `src/qr3d/__main__.py` for CLI entry point (`python -m qr3d`)
- Created `tests/` directory for test suite (pytest-based)

#### Package Configuration
- Updated `pyproject.toml`:
  - Version bumped to 0.1.0
  - Added `[tool.setuptools.packages.find]` with `where = ["src"]`
  - Updated entry points:
    - `qr3d-gui = "qr3d.app:main"` (GUI command)
    - `qr3d = "qr3d.generator:main"` (CLI command)
- Updated `pytest.ini` with `pythonpath = src` for src-layout compatibility
- Updated `qr3d.spec` (PyInstaller):
  - Entry point: `src/qr3d/app.py`
  - Path configuration for src layout
  - Bundle version: 0.1.0

#### CI/CD
- Updated GitHub Actions workflows (`.github/workflows/`):
  - Changed install method to `pip install -e .`
  - Updated test imports to use `qr3d` package
  - Updated PyInstaller builds for new structure

#### Documentation
- Updated `README.md`:
  - Installation now uses `pip install -e .`
  - GUI command: `qr3d-gui` or `./venv-gui/bin/python -m qr3d.app`
  - CLI command: `qr3d` or `./scripts/qr_generate.sh`
  - Updated project structure diagram
- Updated `CLAUDE.md`:
  - Reflected new file locations
  - Updated all code references
  - Added entry point documentation
  - Version metadata: 0.1.0

#### Scripts
- Updated `scripts/qr_generate.sh`:
  - Fixed paths for new location (in scripts/ subdirectory)
  - Uses `python -m qr3d` instead of direct file reference
  - Updated help text with new paths

### Migration Guide

#### For End Users
No changes required! The functionality remains the same.

**Recommended**: Install with `pip install -e .` and use the new commands:
```bash
# GUI
qr3d-gui

# CLI
qr3d https://example.com --mode pendant --name mysite
```

**Alternative** (still works):
```bash
# GUI
./venv-gui/bin/python -m qr3d.app

# CLI
./scripts/qr_generate.sh https://example.com --mode pendant
```

#### For Developers
1. **File References**:
   - `generate_qr_model.py` → `src/qr3d/generator.py`
   - `main_simple.py` → `src/qr3d/app.py`
   - `qr_generate.sh` → `scripts/qr_generate.sh`

2. **Imports**:
   ```python
   # Old
   from generate_qr_model import QRModelGenerator
   from main_simple import SimpleMainWindow

   # New
   from qr3d.generator import QRModelGenerator
   from qr3d.app import SimpleMainWindow
   from qr3d import __version__
   ```

3. **Running Tests**:
   ```bash
   # pytest automatically picks up pythonpath from pytest.ini
   pytest tests/ -v
   ```

4. **Installation**:
   ```bash
   # Editable install (for development)
   pip install -e .

   # Or with virtual environment
   ./venv-gui/bin/pip install -e .
   ```

### Technical Details
- Maintains backward compatibility for end users
- All existing features work identically
- No changes to generated STL files or quality
- Python 3.13 requirement unchanged
- All dependencies remain the same

### Files Modified
- Core package: 7 files moved/created
- Tests: 2 files updated
- Configuration: 3 files updated (pyproject.toml, pytest.ini, qr3d.spec)
- CI/CD: 2 workflows updated
- Documentation: 2 files updated (README.md, CLAUDE.md)
- Scripts: 1 file moved and updated

---

## [0.0.1] - 2025-01-07

### Added
- Initial release with CI/CD setup
- GitHub Actions workflows for testing and releases
- Multi-platform builds (macOS, Linux, Windows)
- PyInstaller build configuration
- Batch processing feature with JSON configuration
- Text rotation support (0° or 180°)
  - Rectangle-text: User-selectable rotation
  - Pendant-text: Automatic 180° rotation
- Batch processing JSON configuration in `batch/config.json`

### Features
- Desktop GUI application (`main_simple.py`)
- CLI tool (`generate_qr_model.py`)
- Four model modes:
  - Square (55x55mm)
  - Pendant (with keychain hole)
  - Rectangle+Text (with optional text label)
  - Pendant+Text (with hole and text label)
- Dynamic text sizing (3-6mm, auto-scaled)
- QR code generation from URLs or images
- OpenSCAD integration for STL export
- Optimized pixel sampling for fast rendering (~1-2 minutes)
- Text with Liberation Mono Bold font, monospace
- Character spacing adjustment (0.85) for improved readability

### Technology Stack
- Python 3.13
- PyQt6 for GUI
- Pillow for image processing
- qrcode library for QR generation
- OpenSCAD for 3D rendering
- PyInstaller for executable builds

---

[0.1.0]: https://github.com/pepperonas/qr-2-3d/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/pepperonas/qr-2-3d/releases/tag/v0.0.1
