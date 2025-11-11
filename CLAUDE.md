# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

**QR Code 3D Model Generator** - Desktop application and CLI tool for generating 3D-printable QR code models from URLs or images. Designed for credit card-sized (55x55mm) physical QR codes optimized for 3D printing.

**Current Version:** 0.3.0

## Recent Updates (v0.3.0)

**New Features:**
1. **Synchronized Relief Heights** - QR and text relief always have same height (`generator.text_height = generator.qr_relief`)
2. **Dynamic Relief Label** - UI label updates based on mode: "QR Relief:" vs "QR/Text Relief:" (app.py:592-596)
3. **Drag & Drop JSON Loading** - Drop JSON metadata files onto GUI to load all settings (app.py:924-1002)
4. **Smart Output Naming** - Auto-generated names include size/thickness: `{name}-{size}-{thickness}` (generator.py:492-495)
5. **Optimized Layout** - Better GUI spacing and proportions (app.py:218, 245-246, etc.)

**Key Improvements:**
- Relief label stored as reference for dynamic updates (`self.relief_label`)
- Size labels: small (0.5x), medium (1.0x), large (2.0x)
- Thickness labels: thin (≤0.6mm), medium (0.7-1.3mm), thick (≥1.4mm)
- Both single and batch generation sync text height with QR relief

## Technology Stack

- **Python 3.13** (venv-gui)
- **PyQt6** - Desktop GUI framework
- **PyVista/VTK** - 3D visualization (available but not actively used)
- **Pillow** - Image processing
- **qrcode[pil]** - QR code generation with PIL support
- **OpenSCAD** - External tool for STL rendering (CLI)

## Project Structure

```
QRs/
├── src/
│   └── qr3d/                  # Main Python package (v0.3.0)
│       ├── __init__.py        # Package init (__version__ = "0.3.0")
│       ├── app.py             # Desktop GUI application with drag-and-drop support
│       ├── generator.py       # Backend generator with smart naming
│       ├── __main__.py        # CLI entry point
│       └── gui/
│           ├── __init__.py
│           └── viewer_widget.py  # PyVista 3D viewer component (unused)
├── scripts/
│   └── qr_generate.sh         # CLI wrapper script
├── tests/                     # Test suite (pytest)
│   ├── test_generator.py      # Generator tests
│   └── test_version.py        # Version tests
├── venv-gui/                  # Python 3.13 virtual environment
├── generated/                 # Output directory (subdirectories per model)
│   ├── example-medium-medium/ # Format: {name}-{size}-{thickness}
│   │   ├── example-medium-medium.png
│   │   ├── example-medium-medium.json
│   │   ├── example-medium-medium.scad
│   │   └── example-medium-medium.stl
│   ├── github-large-thin/     # Large (2.0x), thin (0.5mm)
│   └── mysite-small-thick/    # Small (0.5x), thick (1.5mm)
├── batch/                     # Batch processing (user-specific, gitignored)
│   └── config.json            # Batch configuration file
├── pyproject.toml             # Package configuration (v0.3.0)
├── pytest.ini                 # Test configuration
├── qr3d.spec                  # PyInstaller build specification
├── README.md                  # User documentation
├── INSTALL.md                 # Installation guide
└── CLAUDE.md                  # This file
```

## Architecture

### Backend: src/qr3d/generator.py

**Class: QRModelGenerator**

Core generator that:
1. Accepts URLs or image file paths
2. Generates QR codes from URLs using `qrcode` library
3. Processes images with Pillow (sampling for performance)
4. Generates OpenSCAD (.scad) code
5. Calls OpenSCAD CLI to render STL files

**Key Methods:**
- `is_url(text)` - Static method to detect URLs
- `generate_qr_image(data, output_path)` - Static method to create QR codes
- `load_and_process_image()` - Image processing with sampling
- `generate_openscad(matrix, dimensions)` - SCAD code generation
- `create_metadata_json(dimensions, matrix, qr_input)` - Generate JSON metadata (NEW)
- `export_stl(scad_path, stl_path)` - OpenSCAD CLI invocation
- `generate(qr_input)` - Main workflow orchestration

**Workflow (generate method):**
1. Create model-specific subdirectory (`generated/model-name/`)
2. Load and process QR code image
3. Calculate model dimensions
4. Move/place QR PNG in subdirectory
5. **Generate and save JSON metadata** (before STL for fast access)
6. Generate OpenSCAD code
7. Save SCAD file
8. Export STL (time-consuming, runs last)
9. Return paths: (scad_file, stl_file, json_file)

**Default Parameters:**
```python
card_width = 55      # mm (ISO 7810 credit card size)
card_height = 1.25   # mm
qr_margin = 0.5      # mm (minimized for max QR area)
qr_relief = 1.0      # mm (raised QR code height)
corner_radius = 2    # mm

# Text mode parameters (NEW in 2025)
text_content = ""    # Text to display under QR code
text_size = 6        # Font size in mm (DYNAMIC: auto-scaled 3-6mm based on text length)
                     # Dynamic calculation: char_width_factor=0.8, safety_buffer=4mm
                     # Example: "berlinometer" (12 chars) → 4.79mm with qr_margin=2.0
text_height = 1.0    # Relief height of text (same as QR)
text_margin = 2      # Distance between QR code and text in mm
text_rotation = 0    # Z-axis rotation (0 or 180 degrees)
```

**Modes:**
- `square`: 55x55x1.25mm - Classic square card
- `pendant`: 55x61x1.25mm with 5mm diameter hole for keychain
- `rectangle-text`: 54x64x1.25mm with text label under QR code
- `pendant-text`: 55x~65x1.25mm with hole and text label under QR code

### GUI: src/qr3d/app.py

**Class: SimpleMainWindow (QMainWindow)**

Desktop application with:
- Left panel: Input controls and parameter adjustments
- Progress tracking with QProgressBar
- Background thread for STL generation (non-blocking UI)

**Class: GeneratorThread (QThread)**

Background worker that:
1. Detects if input is URL
2. Generates QR code if needed
3. Creates QRModelGenerator instance
4. Applies custom parameters
5. Generates SCAD and STL files
6. Emits signals for progress and completion

**Class: BatchGeneratorThread (QThread)**

Background worker for batch processing that:
1. Loads `batch/config.json` configuration
2. Parses global parameters and models array
3. Iterates through all models sequentially
4. For each model:
   - Validates required fields (name, url, mode)
   - Generates QR code from URL if needed
   - Creates QRModelGenerator with global params
   - Applies model-specific parameter overrides
   - Generates SCAD and STL files
   - Emits progress signals (current/total)
5. Collects success/failure statistics
6. Emits final summary with details

**Batch Processing Features:**
- **Auto-refresh**: QTimer checks config status every 5 seconds
- **Status display**: Shows config existence, model count, or JSON errors
- **Button states**: Dynamic text ("Create Config", "Start Batch (X models)")
- **Config template**: Creates `batch/config.json` with 4 example models
- **Error handling**: Skips failed models, continues with remaining ones
- **Progress tracking**: Real-time updates showing "Processing X/Y: model-name"
- **Global parameters**: card_height, qr_margin, qr_relief, corner_radius
- **Model overrides**: Individual models can override global params
- **Output**: All files saved to `generated/` directory

**Batch Config Structure (`batch/config.json`):**
```json
{
  "global_params": {
    "card_height": 1.25,
    "qr_margin": 2.0,
    "qr_relief": 1.0,
    "corner_radius": 2
  },
  "models": [
    {
      "name": "example-square",
      "url": "https://example.com",
      "mode": "square"
    },
    {
      "name": "custom-params",
      "url": "https://github.com",
      "mode": "pendant-text",
      "text": "GITHUB",
      "card_height": 1.5
    }
  ]
}
```

**Important: No 3D Viewer**
- ViewerWidget exists but is NOT used in src/qr3d/app.py
- PyVista 3D rendering has compatibility issues on macOS
- Users open STL files in external viewers/slicers

## Critical Design Decisions

### 1. Text Mode Implementation (NEW in 2025)

**Feature:** Optional text labels under QR code for personalization

**Design Decisions:**
- **Text size**: 3-6mm (dynamically scaled, supports up to 20 characters)
- **Text margin**: 2mm from QR code (close but not touching)
- **Text relief**: 1mm (same as QR code for uniform appearance)
- **Font**: Liberation Mono Bold (monospace for consistent character width)
- **Card dimensions**:
  - Rectangle-text: 54x64mm (10mm shorter than initial 74mm prototype)
  - Pendant-text: ~55x65mm (dynamically calculated based on text area)

**OpenSCAD Implementation:**
```scad
module text_label() {
    if (has_text) {
        translate([text_offset_x, text_offset_y, card_height])
        linear_extrude(height=text_height)
        text(text_content, size=text_size, font="Liberation Mono:style=Bold",
             halign="center", valign="bottom");
    }
}
```

**GUI Implementation:**
- Text input field (QLineEdit) with 20 character limit
- Dynamic show/hide based on selected mode (only visible for *-text modes)
- Validation: Text required for text modes
- Mode mapping: Indices 2 and 3 are text modes

**CLI Implementation:**
```bash
./qr_generate.sh URL --mode rectangle-text --text "YOUR TEXT" --name output
```

**Iterative Refinement Process:**
1. Initial: 8mm text, 74mm card → Text too large, card too long
2. Adjustment: 6mm text → Fits up to 7-8 characters at maximum size
3. Adjustment: 64mm card → Better proportions
4. Adjustment: 2mm margin → Text closer to QR code
5. Added: Text rotation (0° or 180°) for flexible text orientation

**Text Rotation Feature (Added 2025-01-07):**

**Problem:** Users wanted text to be readable from different orientations, especially for pendant mode where the text should be upside-down relative to the QR code for better readability when hanging.

**Solution:**
- **Rectangle-text mode**: User-selectable via checkbox (0° or 180°)
- **Pendant-text mode**: Always 180° (automatic)
- **OpenSCAD**: `rotate([0, 0, text_rotation])` before text extrusion
- **Margin correction**: When rotated 180°, text grows upward from anchor point
  - Normal (0°): `text_offset_y = base_offset`
  - Rotated (180°): `text_offset_y = base_offset + text_size` (adds 6mm)

**GUI Implementation:**
- Checkbox "Rotate text 180° (upside down)" visible only for rectangle-text mode
- Hidden for pendant-text (automatic rotation)
- Dynamic show/hide based on mode selection

**CLI Implementation:**
```bash
--text-rotation {0,180}  # Default: 0, ignored for pendant-text (always 180)
```

**Dynamic Text Sizing Feature (Added 2025-01-10):**

**Problem:** Fixed 6mm text size caused overflow with longer text strings. Example: "berlinometer" (12 characters) extended beyond the model boundaries.

**Solution:** Implemented dynamic text size calculation that auto-scales between 3-6mm based on:
- Text length (character count)
- Available width (card width minus margins and safety buffer)
- Character width factor for Liberation Mono Bold font

**Implementation Details:**

1. **Character Width Factor: 0.8**
   - Liberation Mono Bold character width ≈ 0.8 × font_size
   - Started at 0.65 (too optimistic) → 0.7 (still slight overflow) → **0.8 (perfect fit)**
   - Conservative estimate ensures text never overflows

2. **Safety Buffer: 4mm**
   - Initially 2mm → insufficient margin
   - Increased to **4mm** for guaranteed fit
   - Available width = card_width - (2 × qr_margin) - 4mm

3. **Calculation Formula:**
   ```python
   available_width = card_width - (2 * qr_margin) - 4  # safety buffer
   max_text_size = available_width / (len(text) * 0.8)  # char_width_factor
   text_size = max(3.0, min(max_text_size, 6.0))  # constrain 3-6mm
   ```

4. **Examples:**
   - With **qr_margin=0.5** (standard): 49mm available → 20 chars fit perfectly at 3.06mm
   - With **qr_margin=2.0** (large): 46mm available → 20 chars at minimum 3.0mm (may slightly exceed by ~2mm)
   - "A" (1 char): 6.00mm (at maximum)
   - "HELLO" (5 chars): 6.00mm (at maximum)
   - "berlinometer" (12 chars): 4.79mm (with qr_margin=2.0)
   - "berlinometer.de" (15 chars): 3.83mm (with qr_margin=2.0)
   - 20 characters: 3.06mm (with qr_margin=0.5, perfect fit)

**Why These Values Work:**
- char_width_factor=0.8 is conservative enough to handle font rendering variations
- 4mm safety buffer accounts for:
  - OpenSCAD text rendering quirks
  - Font edge cases and kerning
  - Manufacturing tolerances in 3D printing
- Result: Text guaranteed to fit within model boundaries for all 1-20 character strings

**Code Location:**
- `calculate_text_size()` method: src/qr3d/generator.py:121-152
- Dynamic sizing call: src/qr3d/generator.py:154-169 in `calculate_dimensions()`

### 2. Performance Optimization: Multi-Layered Strategy

**Layer 1: Pixel Sampling**

**Problem:** 100x100 pixel QR codes → ~10,000 3D cubes → 2-5 minute render time

**Solution:** Sample to 50x50 grid → ~800-1,200 cubes → significantly reduced complexity

**Implementation:**
```python
target_grid = 50
sample_rate = max(width, height) // target_grid

for y in range(0, height, sample_rate):
    for x in range(0, width, sample_rate):
        pixel = img.getpixel((x, y))
        row.append(pixel < threshold)
```

**Why it works:**
- QR codes use Error Correction Level H (30% tolerance)
- 3D printers can't render finer details anyway
- Physical card margins provide required "quiet zone"

**Layer 2: OpenSCAD Rendering Optimization (2025-11-11)**

**Optimizations applied:**
1. **Reduced $fn from 12 to 8 segments** for rounded corners and holes (~33% faster curve rendering)
2. **OpenSCAD fast-csg mode** via `--enable=fast-csg` flag (requires OpenSCAD 2023+)
3. **Automatic binary detection** - Checks `/Applications/OpenSCAD.app` on macOS first, falls back to PATH

**Performance Results:**
- OpenSCAD 2021.01, $fn=12: ~120 seconds per model
- OpenSCAD 2025.11.10, $fn=8, fast-csg: ~1 second per model
- **126x speed improvement!**

**Implementation:**
```python
def find_openscad_binary():
    """Find OpenSCAD binary, checking macOS .app first, then PATH"""
    macos_path = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
    if os.path.exists(macos_path):
        return macos_path
    return 'openscad'

# In export_stl():
openscad_bin = find_openscad_binary()
cmd = [openscad_bin, '-o', str(stl_path), '--enable=fast-csg', str(scad_path)]
```

**Code Location:**
- `find_openscad_binary()`: src/qr3d/generator.py:20-28
- `export_stl()`: src/qr3d/generator.py:411-450
- `$fn` setting: src/qr3d/generator.py:255

**JSON Metadata Optimization (2025-11-11):**
- Float values rounded to 3 decimal places for better readability
- `round_floats()` helper function recursively processes nested dictionaries
- Example: `0.9807692307692307` → `0.981`
- Location: src/qr3d/generator.py:348-356

### 3. Maximized QR Code Area

**Standard QR Spec:** 4 modules border + physical margins

**Our Approach:**
- QR border: 1 module (reduced from 4)
- Physical margin: 0.5mm (reduced from 2mm)
- Result: ~54x54mm QR area on 55x55mm card

**Reasoning:**
- Physical card provides structural border
- Error Correction Level H tolerates missing border modules
- Better scanning (larger codes scan easier)

**Implementation:**
```python
# In generate_qr_image()
qr = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    border=1,  # Minimized for maximum QR area
)
```

### 4. Python Version: 3.13 Required

**Why not 3.14?**
- VTK (required by PyVista) not yet available for Python 3.14
- GUI dependencies need Python 3.13

**Virtual Environment:**
- `venv-gui/` uses Python 3.13
- Created with: `python3.13 -m venv venv-gui`

### 5. GUI Without 3D Preview

**Original Plan:** Full 3D viewer with PyVista/VTK

**Issue:** PyVista's QtInteractor has rendering problems on macOS
- Window appears in dock but doesn't display
- Main window freezes/doesn't show UI

**Current Solution:**
- Simplified GUI without 3D preview
- `src/qr3d/app.py` is the working application
- Users view STL in external tools (PrusaSlicer, Cura, etc.)

**Files:**
- ✅ `src/qr3d/app.py` - Working GUI
- ❌ `main.py` - Deleted (had PyVista integration issues)
- ⚠️ `ui/viewer_widget.py` - Kept for future attempts

## Common Workflows

### Adding New Parameters

1. **Backend** (`src/qr3d/generator.py`):
   ```python
   class QRModelGenerator:
       def __init__(self, ...):
           self.new_parameter = default_value
   ```

2. **GUI** (`src/qr3d/app.py`):
   - Add QDoubleSpinBox/QSpinBox in `create_controls_panel()`
   - Update `GeneratorThread.run()` to apply parameter
   ```python
   generator.new_parameter = self.params['new_param']
   ```

3. **CLI** (`src/qr3d/generator.py` main()):
   ```python
   parser.add_argument('--new-param', type=float, default=X)
   generator.new_parameter = args.new_param
   ```

### Performance Tuning

**Faster rendering:**
- Reduce `target_grid` in `load_and_process_image()` (less cubes)
- Reduce `$fn` in OpenSCAD generation (less smooth curves)
- Use `background=True` in `export_stl()` for async rendering

**Better quality:**
- Increase `target_grid` (more detail, slower)
- Increase `$fn` value (smoother curves, slower)
- Adjust `qr_relief` for more pronounced QR codes

### Debugging Generation Issues

**Check these in order:**
1. URL detection: `QRModelGenerator.is_url(input)`
2. QR code creation: Check `generated/*.png` exists
3. SCAD generation: Check `generated/*-model.scad` exists and is valid
4. OpenSCAD available: `which openscad`
5. OpenSCAD rendering: Run manually `openscad -o test.stl test.scad`

## Known Issues & Workarounds

### Issue: PyVista 3D Viewer Not Working on macOS

**Symptoms:**
- App appears in dock but no window shows
- Window shows but is blank/frozen
- QtInteractor doesn't render properly

**Attempted Solutions:**
- `window.raise_()` and `window.activateWindow()` - didn't help
- Different Qt backends - no improvement
- Python 3.13 vs 3.14 - same issue

**Current Workaround:**
- Use `src/qr3d/app.py` without 3D viewer
- Users open STL in external applications

**Future Investigation:**
- Try matplotlib 3D plotting instead of PyVista
- Try web-based viewer (Three.js in QWebEngineView)
- Test on Linux (may work better than macOS)

### Issue: OpenSCAD Timeout on Complex QR Codes

**Symptoms:**
- STL generation takes > 2 minutes
- Timeout errors in console

**Solutions:**
- Increase timeout: `subprocess.run(..., timeout=300)`
- Use background mode: `export_stl(..., background=True)`
- Reduce complexity: Lower `target_grid` or `$fn`

## Development Commands

### Start GUI
```bash
./venv-gui/bin/python src/qr3d/app.py
```

### Test CLI
```bash
# Test basic modes
./qr_generate.sh https://example.com --mode pendant --name test

# Test text modes
./qr_generate.sh https://example.com --mode rectangle-text --text "HELLO" --name test-text
./qr_generate.sh https://example.com --mode pendant-text --text "TEST" --name test-pendant
```

### Reinstall Dependencies
```bash
./venv-gui/bin/pip install -r requirements-gui.txt --force-reinstall
```

### Check Generated Files
```bash
ls -lh generated/
```

### Manual OpenSCAD Test
```bash
openscad -o test.stl generated/example-model.scad
```

## Code Style & Conventions

- **PEP 8** compliance
- **Type hints** preferred but not required
- **Docstrings** for all public methods
- **Comments** for complex algorithms (especially sampling logic)
- **Error handling** with try-except and user-friendly messages
- **Progress feedback** via print() or Qt signals

## Important Reminders

1. **Always use Python 3.13** (`./venv-gui/bin/python`)
2. **Never commit `generated/` files** - user output only
3. **Test both GUI and CLI** when changing backend
4. **Check QR scannability** after parameter changes
5. **Sampling is critical** - don't remove without careful consideration
6. **Border=1 is intentional** - don't increase without reason

## User Feedback Patterns

Users often request:
- **Larger QR codes** → Reduce margin or border
- **Faster generation** → Optimize sampling or $fn
- **Different shapes** → Add new modes to generate_openscad()
- **Custom text/logos** → ✅ IMPLEMENTED: Text modes with Liberation Mono font
- **Batch processing** → Add loop in CLI or GUI
- **Personalization** → ✅ IMPLEMENTED: Text labels under QR code

When users say "QR code is too small":
- They mean margin is too large
- Solution: Reduce `qr_margin` OR `border` parameter
- Explain trade-off: Smaller margin = better scanning but less structural stability

## Testing Checklist

Before committing changes:
- [ ] GUI launches without errors
- [ ] URL input generates QR code
- [ ] Image file input works
- [ ] Square mode generates correct dimensions (55x55mm)
- [ ] Pendant mode includes hole (55x61mm)
- [ ] Rectangle-text mode generates with text (54x64mm)
- [ ] Pendant-text mode includes hole and text (~55x65mm)
- [ ] Text field shows/hides correctly based on mode
- [ ] Text validation works (required for text modes, max 20 chars)
- [ ] Text renders correctly in STL (Liberation Mono Bold, 6mm, 1mm relief)
- [ ] Text rotation checkbox shows/hides correctly (Rectangle+Text only)
- [ ] Text rotation works correctly (0° and 180°)
- [ ] Pendant-text applies automatic 180° rotation
- [ ] Rotated text margins are correct (no overlap with QR code)
- [ ] Batch status label updates (shows config status)
- [ ] Batch button creates config template when clicked (no config exists)
- [ ] Batch config.json has correct structure (global_params + models array)
- [ ] Batch processing generates all models sequentially
- [ ] Batch progress updates correctly (X/Y models)
- [ ] Failed batch models are skipped (processing continues)
- [ ] Batch completion shows summary (successful/failed counts)
- [ ] QTimer auto-refreshes batch status every 5 seconds
- [ ] Individual model params override global params correctly
- [ ] STL files are valid (open in slicer)
- [ ] Parameters from GUI apply correctly
- [ ] CLI wrapper works
- [ ] CLI --text parameter works for text modes
- [ ] README updated if user-facing changes

## Maintenance Notes

**Regular tasks:**
- Update dependencies: `pip list --outdated`
- Test with various URL lengths
- Verify QR scannability with phone
- Check OpenSCAD compatibility

**Performance monitoring:**
- Target: < 2 minutes per generation
- If slower: Profile and optimize sampling
- If faster: Consider increasing quality

**Code smell indicators:**
- Hard-coded values instead of parameters
- Duplicate code between GUI and CLI
- No error handling around subprocess calls
- Magic numbers without comments

## Contact & Support

For development questions:
1. Read this CLAUDE.md thoroughly
2. Check README.md for user-facing docs
3. Review git history for context on changes
4. Test changes with both GUI and CLI

---

**Last Updated:** 2025-11-11 (v0.1.0: Project reorganization to src-layout)
**Python Version:** 3.13
**Package Version:** 0.1.0
**Package Name:** qr3d (was: qr-3d-generator)
**Primary GUI:** src/qr3d/app.py (entry point: `qr3d-gui` or `python -m qr3d.app`)
**Primary CLI:** src/qr3d/generator.py (entry point: `qr3d` or `python -m qr3d`)
**Status:** Production-ready, GUI functional without 3D viewer, src-layout structure
**Latest Features:**
- **v0.1.0**: Reorganized to Python src-layout standard (src/qr3d/, tests/, scripts/)
- Batch processing: Generate multiple models from JSON configuration
- Text rotation (0° or 180°) for text modes - Rectangle-text: user choice, Pendant-text: automatic
**Developer:** Martin Pfeffer
**License:** MIT
