# Changelog

All notable changes to the QR Code 3D Generator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-11-10

### Added

#### Core Features
- Desktop GUI application with PyQt6
- QR code generation from URLs
- Image file input support (PNG, JPG)
- Four model modes:
  - Square (55x55mm)
  - Pendant (55x61mm with keychain hole)
  - Rectangle + Text (54x64mm with text label)
  - Pendant + Text (55x65mm with hole and text)
- Text mode functionality with dynamic sizing (up to 20 characters)
- Text rotation option (0° or 180°) for rectangle-text mode
- Batch processing support via JSON configuration
- Real-time batch status monitoring

#### Parameters
- Customizable card height (0.5-5.0mm)
- Adjustable QR margin (0-10mm)
- QR relief height control (0.1-2.0mm)
- Corner radius adjustment (0-5mm)

#### Build System
- Version management system (v0.0.1)
- PyInstaller .spec file for multi-platform builds
- Platform-specific build scripts:
  - macOS: build_macos.sh (.app bundle + DMG)
  - Windows: build_windows.bat (executable + ZIP)
  - Linux: build_linux.sh (executable + tarball + AppImage)

#### CI/CD
- GitHub Actions workflow for automated testing
  - Tests on macOS, Windows, and Linux
  - Python 3.13 test matrix
  - Import verification
  - Build checks
- GitHub Actions workflow for automated releases
  - Tag-triggered builds (v*)
  - Multi-platform installer creation
  - Automatic GitHub Release publishing

#### Testing
- Comprehensive pytest test suite
  - Version module tests
  - Generator module tests (URL detection, parameters, QR generation)
  - GUI import tests
- pytest configuration (pytest.ini)
- 13 passing tests, 1 skipped (GUI window creation)

#### Documentation
- README.md with installation and usage instructions
- INSTALL.md with detailed setup guide
- CLAUDE.md with development context
- build_scripts/README.md with build documentation
- LICENSE file (MIT)

### Fixed
- GUI window height increased from 700 to 850 pixels to prevent element clipping

### Technical Details
- Python 3.13 required
- PyQt6 for GUI framework
- Pillow for image processing
- qrcode library for QR generation
- OpenSCAD for STL rendering (external dependency)
- Performance-optimized pixel sampling (50x50 grid)
- QR Error Correction Level H (30% tolerance)

### Dependencies
- Pillow >= 10.0.0
- qrcode[pil] >= 7.4.0
- PyQt6 >= 6.6.0

### Development Dependencies
- pyinstaller >= 6.0.0
- pytest >= 7.0.0

---

## [Unreleased]

No unreleased changes at this time.

---

**Note:** This is the initial release establishing the foundational CI/CD infrastructure and version management system. Future releases will follow semantic versioning.
