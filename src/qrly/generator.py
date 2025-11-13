#!/usr/bin/env python3
"""
QR Code 3D Model Generator
Converts QR code images (PNG/JPG) or URLs to 3D-printable OpenSCAD models
"""

import argparse
import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path
from PIL import Image
import subprocess
import qrcode
import tempfile

# Default output directory in user's home folder
DEFAULT_OUTPUT_DIR = Path.home() / "qr-codes"


def find_openscad_binary():
    """Find OpenSCAD binary, checking bundled, system, then PATH"""

    # Get the base path (for PyInstaller bundled apps)
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Check for bundled OpenSCAD (PyInstaller bundle - stored as data files)
    if sys.platform == 'darwin':
        # Check bundled OpenSCAD.app (in openscad_bundle directory as data)
        bundled_path = os.path.join(base_path, 'openscad_bundle', 'OpenSCAD.app', 'Contents', 'MacOS', 'OpenSCAD')
        if os.path.exists(bundled_path):
            return bundled_path
        # Check system installation
        system_path = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
        if os.path.exists(system_path):
            return system_path
    elif sys.platform == 'win32':
        bundled_path = os.path.join(base_path, 'openscad_bundle', 'openscad.exe')
        if os.path.exists(bundled_path):
            return bundled_path
    else:  # Linux
        # Linux: OpenSCAD binary from extracted AppImage
        bundled_path = os.path.join(base_path, 'openscad_bundle', 'openscad', 'usr', 'bin', 'openscad')
        if os.path.exists(bundled_path):
            return bundled_path

    # Fall back to 'openscad' in PATH
    return 'openscad'


class QRModelGenerator:
    """Generate 3D models from QR code images"""

    def __init__(self, image_path, mode='square', output_dir='.', output_name=None):
        self.image_path = Path(image_path)
        self.mode = mode
        self.output_dir = Path(output_dir)
        self.output_name = output_name  # Optional: override name derived from image_path

        # Design parameters
        self.card_width = 55    # mm - credit card width
        self.card_height = 0.5  # mm - card thickness (default: dünn)
        self.qr_margin = 2.0    # mm - margin around QR code
        self.qr_relief = 0.5    # mm - height of raised QR code (default: dünn)
        self.corner_radius = 2  # mm - rounded corners
        self.size_scale = 1.0   # Scale factor for card dimensions (0.5=klein, 1.0=mittel, 2.0=groß)

        # Pendant mode specific
        self.hole_diameter = 5  # mm
        self.hole_from_top = 6  # mm - distance from top to hole center
        self.top_margin = 8     # mm - total top margin for pendant (hole area + margin)

        # Text mode specific (for rectangle-text, pendant-text, and rectangle-text-2x)
        self.text_content = ""       # Text to display under QR code (or only text for single-text modes)
        self.text_content_top = ""   # Text to display above QR code (only for rectangle-text-2x)
        self.text_size = 6           # Font size in mm (reduced from 8 to fit 12 chars)
        self.text_height = 1.0       # Relief height of text (same as QR)
        self.text_margin = 2         # Distance between QR code and text in mm
        self.text_rotation = 0       # Rotation in Z-axis (0 or 180 degrees)

    @staticmethod
    def is_url(text):
        """Check if the input is a URL"""
        url_pattern = re.compile(
            r'^(https?://|www\.)'  # http://, https://, or www.
            r'([a-zA-Z0-9.-]+)'     # domain
            r'(\.[a-zA-Z]{2,})'     # TLD
            r'([/?].*)?$'           # optional path
        )
        return bool(url_pattern.match(text))

    @staticmethod
    def get_output_name(base_name, card_height=1.25, size_scale=1.0):
        """Generate output directory name with size/thickness labels"""
        size_label = "small" if size_scale == 0.5 else "large" if size_scale == 2.0 else "medium"
        thickness_label = "thin" if card_height <= 0.6 else "thick" if card_height >= 1.4 else "medium"
        return f"{base_name}-{size_label}-{thickness_label}"

    @staticmethod
    def get_unique_output_dir(output_base_dir, base_name, card_height=1.25, size_scale=1.0):
        """Get a unique output directory, adding counter if needed"""
        final_name = QRModelGenerator.get_output_name(base_name, card_height, size_scale)
        model_dir = Path(output_base_dir) / final_name

        counter = 1
        while model_dir.exists() and any(model_dir.iterdir()):  # Skip if exists AND not empty
            model_dir = Path(output_base_dir) / f"{final_name} ({counter})"
            counter += 1

        return model_dir

    @staticmethod
    def generate_qr_image(data, output_path=None):
        """Generate QR code image from text/URL"""
        qr = qrcode.QRCode(
            version=None,  # Auto-size
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
            box_size=10,
            border=1,  # Minimal border (QR spec recommends 4, but we have physical margins)
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        if output_path:
            img.save(output_path)
            return output_path
        else:
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            img.save(temp_file.name)
            return temp_file.name

    def load_and_process_image(self):
        """Load image and convert to binary matrix with sampling for performance"""
        if not self.image_path.exists():
            raise FileNotFoundError(f"Image file not found: {self.image_path}")

        # Load image
        img = Image.open(self.image_path)

        # Convert to grayscale
        img = img.convert('L')

        # Get original dimensions
        width, height = img.size

        # Calculate sampling rate to reduce complexity (like card-generator)
        # Target grid: 50x50 (~800-1200 cubes instead of ~10000)
        # QR codes with Error Correction Level H can tolerate 30% data loss
        target_grid = 50
        sample_rate = max(width, height) // target_grid

        # Ensure sample_rate is at least 1
        if sample_rate < 1:
            sample_rate = 1

        # Convert to binary (threshold at 128)
        threshold = 128

        # Sample pixels to create optimized matrix
        matrix = []
        for y in range(0, height, sample_rate):
            row = []
            for x in range(0, width, sample_rate):
                pixel = img.getpixel((x, y))
                row.append(pixel < threshold)  # Black pixels become True
            matrix.append(row)

        # Return sampled dimensions
        sampled_width = len(matrix[0]) if matrix else 0
        sampled_height = len(matrix)

        return matrix, sampled_width, sampled_height

    def calculate_text_size(self, text, available_width):
        """
        Calculate optimal text size based on text length and available width.

        Liberation Mono Bold character width ≈ 0.65 * font_size

        Args:
            text: Text content
            available_width: Available width in mm for text

        Returns:
            Optimal text size in mm (between 3mm and 6mm)
        """
        if not text or len(text) == 0:
            return 6  # Default size if no text

        # Liberation Mono Bold: character width ≈ 0.8 * font_size
        # Using 0.8 (increased from 0.75) to ensure text definitely fits with maximum safety margin
        char_width_factor = 0.8

        # Calculate maximum text size that fits
        # text_width = len(text) * char_width_factor * text_size
        # We want: text_width <= available_width
        # => text_size <= available_width / (len(text) * char_width_factor)
        max_text_size = available_width / (len(text) * char_width_factor)

        # Constrain to reasonable limits
        min_size = 3.0  # Minimum readable size
        max_size = 6.0  # Maximum size (current default)

        text_size = max(min_size, min(max_text_size, max_size))

        return text_size

    def calculate_dimensions(self, qr_pixels):
        """Calculate model dimensions based on mode"""
        # Calculate dynamic text size if text mode
        if self.mode in ['rectangle-text', 'pendant-text', 'rectangle-text-2x']:
            # Determine available width for text based on mode
            if self.mode in ['rectangle-text', 'rectangle-text-2x']:
                card_width_for_text = 54 * self.size_scale  # Rectangle mode uses 54mm width (scaled)
            else:  # pendant-text
                card_width_for_text = self.card_width * self.size_scale  # 55mm (scaled)

            # Calculate available width (card width minus margins and safety buffer)
            available_text_width = card_width_for_text - (2 * self.qr_margin) - 4  # 4mm safety buffer

            # Calculate and set dynamic text size for bottom text
            if self.text_content:
                self.text_size = self.calculate_text_size(self.text_content, available_text_width)
            # For rectangle-text-2x, also calculate for top text (use same size for consistency)
            if self.mode == 'rectangle-text-2x' and self.text_content_top:
                # Use the max size of both texts to ensure both fit
                top_size = self.calculate_text_size(self.text_content_top, available_text_width)
                if self.text_content:
                    self.text_size = max(self.text_size, top_size)
                else:
                    self.text_size = top_size

        # Text area height calculation (if text mode)
        text_area_height = 0
        text_area_height_top = 0
        if self.mode in ['rectangle-text', 'pendant-text'] and self.text_content:
            text_area_height = self.text_size + self.text_margin + self.qr_margin  # text height + spacing + bottom margin
        elif self.mode == 'rectangle-text-2x':
            # Calculate space for both top and bottom text
            if self.text_content:
                text_area_height = self.text_size + self.text_margin + self.qr_margin  # bottom text
            if self.text_content_top:
                text_area_height_top = self.text_size + self.text_margin + self.qr_margin  # top text

        # Apply size scale to base card width
        scaled_card_width = self.card_width * self.size_scale

        if self.mode == 'square':
            # Square mode: QR code with equal margins
            available_width = scaled_card_width - (2 * self.qr_margin)
            available_height = scaled_card_width - (2 * self.qr_margin)
            card_length = scaled_card_width
            qr_offset_y = self.qr_margin

        elif self.mode == 'rectangle-text':
            # Rectangle-text mode: 54x64mm, QR top, text bottom
            card_width = 54 * self.size_scale  # Custom width for rectangle
            available_width = card_width - (2 * self.qr_margin)
            available_height = available_width  # Keep QR code square
            card_length = 64 * self.size_scale  # Fixed length for rectangle-text (reduced from 74)
            qr_offset_y = self.qr_margin

        elif self.mode == 'rectangle-text-2x':
            # Rectangle-text-2x mode: Text on top AND bottom
            card_width = 54 * self.size_scale  # Custom width for rectangle
            available_width = card_width - (2 * self.qr_margin)
            available_height = available_width  # Keep QR code square
            # Total height: top_text_area + QR_height + bottom_text_area
            card_length = text_area_height_top + available_height + text_area_height
            qr_offset_y = text_area_height_top  # QR starts after top text

        elif self.mode == 'pendant-text':
            # Pendant-text mode: Like pendant but with text area at bottom
            available_width = scaled_card_width - (2 * self.qr_margin)
            available_height = available_width  # Keep QR code square
            scaled_top_margin = self.top_margin * self.size_scale  # Scale top margin
            card_length = (available_height + self.qr_margin + scaled_top_margin + text_area_height)
            qr_offset_y = scaled_top_margin

        else:  # pendant mode
            # Pendant mode: extra space at top for hole
            available_width = scaled_card_width - (2 * self.qr_margin)
            available_height = available_width  # Keep QR code square
            scaled_top_margin = self.top_margin * self.size_scale  # Scale top margin
            card_length = (available_height + self.qr_margin + scaled_top_margin)
            qr_offset_y = scaled_top_margin

        pixel_size = min(available_width / qr_pixels, available_height / qr_pixels)

        # Calculate text position if text mode
        text_offset_y = 0
        text_offset_y_top = 0

        # Bottom text (for all text modes)
        if self.mode in ['rectangle-text', 'pendant-text'] and self.text_content:
            base_offset = qr_offset_y + (pixel_size * qr_pixels) + self.text_margin
            # If text is rotated 180°, we need to adjust the Y position
            # When rotated, the text grows upward from the anchor point instead of downward
            if self.text_rotation == 180:
                # Add the text height to push the anchor point down so rotated text doesn't overlap QR
                text_offset_y = base_offset + self.text_size
            else:
                text_offset_y = base_offset

        # For rectangle-text-2x: calculate both top and bottom text positions
        elif self.mode == 'rectangle-text-2x':
            # Top text (above QR code)
            if self.text_content_top:
                # Top text is at the beginning, rotated 180°
                text_offset_y_top = self.qr_margin + self.text_size  # Add text size because rotated

            # Bottom text (below QR code)
            if self.text_content:
                base_offset = qr_offset_y + (pixel_size * qr_pixels) + self.text_margin
                # Bottom text is also rotated 180°
                text_offset_y = base_offset + self.text_size

        # Determine card width based on mode
        card_width_final = scaled_card_width
        if self.mode in ['rectangle-text', 'rectangle-text-2x']:
            card_width_final = 54 * self.size_scale

        return {
            'card_length': card_length,
            'card_width': card_width_final,
            'pixel_size': pixel_size,
            'qr_offset_x': self.qr_margin,
            'qr_offset_y': qr_offset_y,
            'qr_size': pixel_size * qr_pixels,
            'has_text': bool(self.text_content and self.mode in ['rectangle-text', 'pendant-text', 'rectangle-text-2x']),
            'has_text_top': bool(self.text_content_top and self.mode == 'rectangle-text-2x'),
            'text_offset_y': text_offset_y,
            'text_offset_y_top': text_offset_y_top,
            'text_offset_x': card_width_final / 2,  # Center text (scaled)
            'text_offset_x_top': card_width_final / 2  # Center top text (scaled)
        }

    def generate_openscad(self, matrix, dimensions):
        """Generate OpenSCAD code"""
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0

        # Escape text for OpenSCAD (replace quotes)
        safe_text = self.text_content.replace('"', '\\"') if self.text_content else ""
        safe_text_top = self.text_content_top.replace('"', '\\"') if self.text_content_top else ""

        scad_code = f"""// QR Code 3D Model
// Generated from: {self.image_path.name}
// Mode: {self.mode}

$fn = 8;  // Smoothness of curves (optimized for speed - 8 segments sufficient for 3D printing)

// Parameters
card_width = {dimensions['card_width']};
card_length = {dimensions['card_length']};
card_height = {self.card_height};
corner_radius = {self.corner_radius};
qr_relief = {self.qr_relief};
pixel_size = {dimensions['pixel_size']};

// QR Code position
qr_offset_x = {dimensions['qr_offset_x']};
qr_offset_y = {dimensions['qr_offset_y']};

// Text parameters (bottom text)
has_text = {str(dimensions['has_text']).lower()};
text_content = "{safe_text}";
text_size = {self.text_size};
text_height = {self.text_height};
text_offset_x = {dimensions['text_offset_x']};
text_offset_y = {dimensions['text_offset_y']};
text_rotation = {self.text_rotation};  // Z-axis rotation (0 or 180 degrees)

// Top text parameters (for rectangle-text-2x mode)
has_text_top = {str(dimensions['has_text_top']).lower()};
text_content_top = "{safe_text_top}";
text_offset_x_top = {dimensions['text_offset_x_top']};
text_offset_y_top = {dimensions['text_offset_y_top']};
text_rotation_top = 180;  // Top text always rotated 180 degrees

// Helper module for rounded corners (faster than minkowski)
module rounded_square(width, length, height, radius) {{
    hull() {{
        translate([radius, radius, 0])
            cylinder(r=radius, h=height);
        translate([width-radius, radius, 0])
            cylinder(r=radius, h=height);
        translate([radius, length-radius, 0])
            cylinder(r=radius, h=height);
        translate([width-radius, length-radius, 0])
            cylinder(r=radius, h=height);
    }}
}}

// Text module (bottom text)
module text_label() {{
    if (has_text) {{
        translate([text_offset_x, text_offset_y, card_height])
        rotate([0, 0, text_rotation])
        linear_extrude(height=text_height)
        text(text_content, size=text_size, font="Liberation Mono:style=Bold",
             halign="center", valign="bottom", spacing=0.85);
    }}
}}

// Text module (top text for rectangle-text-2x)
module text_label_top() {{
    if (has_text_top) {{
        translate([text_offset_x_top, text_offset_y_top, card_height])
        rotate([0, 0, text_rotation_top])
        linear_extrude(height=text_height)
        text(text_content_top, size=text_size, font="Liberation Mono:style=Bold",
             halign="center", valign="bottom", spacing=0.85);
    }}
}}

// Main model
difference() {{
    union() {{
        // Base card with rounded corners (hull is MUCH faster than minkowski)
        rounded_square(card_width, card_length, card_height, corner_radius);

        // QR Code pattern (raised)
        translate([qr_offset_x, qr_offset_y, card_height])
            qr_pattern();

        // Top text label (if enabled, for rectangle-text-2x mode)
        text_label_top();

        // Bottom text label (if enabled)
        text_label();
    }}
"""

        # Add hole for pendant modes
        if self.mode in ['pendant', 'pendant-text']:
            hole_x = dimensions['card_width'] / 2
            hole_y = self.hole_from_top * self.size_scale  # Scale hole position
            hole_d = self.hole_diameter * self.size_scale  # Scale hole diameter
            scad_code += f"""
    // Hole for chain
    translate([{hole_x}, {hole_y}, -1])
        cylinder(d={hole_d}, h=card_height + 2);
"""

        scad_code += "}\n\n"

        # QR pattern module
        scad_code += f"""// QR Code Pattern Module
module qr_pattern() {{
"""

        # Generate cubes for each black pixel
        for row in range(rows):
            for col in range(cols):
                if matrix[row][col]:  # Black pixel = raised
                    x = col * dimensions['pixel_size']
                    y = (rows - 1 - row) * dimensions['pixel_size']  # Flip Y axis
                    scad_code += f"    translate([{x:.4f}, {y:.4f}, 0]) cube([pixel_size, pixel_size, qr_relief]);\n"

        scad_code += "}\n"

        return scad_code

    def save_scad_file(self, scad_code, output_path):
        """Save OpenSCAD code to file"""
        with open(output_path, 'w') as f:
            f.write(scad_code)
        print(f"✓ OpenSCAD file created: {output_path}")

    def create_metadata_json(self, dimensions, matrix, qr_input=None):
        """Create JSON metadata file with model configuration"""
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0

        # Helper to round floats to 3 decimal places for readability
        def round_floats(obj):
            if isinstance(obj, float):
                return round(obj, 3)
            elif isinstance(obj, dict):
                return {k: round_floats(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [round_floats(item) for item in obj]
            return obj

        metadata = {
            "generated_at": datetime.now().isoformat(),
            "version": "0.1.0",
            "mode": self.mode,
            "qr_input": qr_input or str(self.image_path.name),
            "dimensions": {
                "card_width_mm": dimensions['card_width'],
                "card_length_mm": dimensions['card_length'],
                "card_height_mm": self.card_height,
                "qr_size_mm": dimensions['qr_size'],
                "qr_pixel_size_mm": dimensions['pixel_size'],
                "qr_grid": f"{cols}x{rows}"
            },
            "parameters": {
                "qr_margin_mm": self.qr_margin,
                "qr_relief_mm": self.qr_relief,
                "corner_radius_mm": self.corner_radius,
                "size_scale": self.size_scale
            }
        }

        # Add pendant-specific data
        if self.mode in ['pendant', 'pendant-text']:
            metadata["pendant"] = {
                "hole_diameter_mm": self.hole_diameter,
                "hole_from_top_mm": self.hole_from_top,
                "top_margin_mm": self.top_margin
            }

        # Add text-specific data
        if self.mode in ['rectangle-text', 'pendant-text'] and self.text_content:
            metadata["text"] = {
                "content": self.text_content,
                "size_mm": self.text_size,
                "height_mm": self.text_height,
                "margin_mm": self.text_margin,
                "rotation_deg": self.text_rotation,
                "font": "Liberation Mono:style=Bold"
            }
        elif self.mode == 'rectangle-text-2x':
            metadata["text"] = {}
            if self.text_content:
                metadata["text"]["content_bottom"] = self.text_content
            if self.text_content_top:
                metadata["text"]["content_top"] = self.text_content_top
            if self.text_content or self.text_content_top:
                metadata["text"].update({
                    "size_mm": self.text_size,
                    "height_mm": self.text_height,
                    "margin_mm": self.text_margin,
                    "rotation_deg": 180,  # Always 180 for both texts in rectangle-text-2x
                    "font": "Liberation Mono:style=Bold"
                })

        # Round all float values to 3 decimal places for better readability
        return round_floats(metadata)

    def export_stl(self, scad_path, stl_path, background=False):
        """Export STL using OpenSCAD command line"""
        try:
            openscad_bin = find_openscad_binary()

            # Build command with fast-csg optimization (requires OpenSCAD 2023+)
            cmd = [openscad_bin, '-o', str(stl_path), '--enable=fast-csg', str(scad_path)]

            if background:
                # Start OpenSCAD in background
                print(f"  Starting OpenSCAD export in background...")
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"⏳ STL export running in background (PID: {process.pid})")
                print(f"   Check {stl_path} in a few minutes")
                return True
            else:
                # Run OpenSCAD synchronously with progress indicator
                print(f"  Rendering 3D model... (this may take 30-60 seconds)")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minutes timeout
                )

                if result.returncode == 0:
                    print(f"✓ STL file created: {stl_path}")
                    return True
                else:
                    print(f"⚠ OpenSCAD export failed:")
                    if result.stderr:
                        # Filter out common non-error messages
                        errors = [line for line in result.stderr.split('\n')
                                 if line and not line.startswith('WARNING:')]
                        if errors:
                            print(f"  {errors[0]}")
                    print(f"  You can open {scad_path} in OpenSCAD GUI and export manually.")
                    return False

        except FileNotFoundError:
            print("⚠ OpenSCAD not found in PATH. Please install OpenSCAD or export STL manually.")
            print(f"  Install: brew install openscad")
            print(f"  Or open {scad_path} in OpenSCAD GUI and export to STL manually.")
            return False
        except subprocess.TimeoutExpired:
            # If timeout, try launching in background
            print("⚠ STL generation taking longer than expected...")
            print(f"  Starting background export...")
            try:
                process = subprocess.Popen(
                    ['openscad', '-o', str(stl_path), str(scad_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"⏳ STL export now running in background (PID: {process.pid})")
                print(f"   File will be ready at: {stl_path}")
                return True
            except Exception as e:
                print(f"⚠ Could not start background process: {e}")
                return False

    def generate(self, qr_input=None):
        """Main generation process"""
        print(f"Processing: {self.image_path.name}")
        print(f"Mode: {self.mode}")

        # Get unique output directory
        base_name = self.output_name or self.image_path.stem  # Use provided name or filename without extension
        model_dir = self.get_unique_output_dir(self.output_dir, base_name, self.card_height, self.size_scale)
        final_name = model_dir.name

        model_dir.mkdir(parents=True, exist_ok=True)
        print(f"→ Output directory: {model_dir}")

        # Load and process image
        print("→ Loading image...")
        matrix, width, height = self.load_and_process_image()
        print(f"  QR code matrix: {width}x{height} pixels")

        # Calculate dimensions
        dimensions = self.calculate_dimensions(width)
        print(f"  Model size: {dimensions['card_width']}x{dimensions['card_length']}x{self.card_height}mm")

        # Determine output filenames (all in model subdirectory, use final_name for consistency)
        qr_file = model_dir / f"{final_name}.png"
        scad_file = model_dir / f"{final_name}.scad"
        stl_file = model_dir / f"{final_name}.stl"
        json_file = model_dir / f"{final_name}.json"

        # Move QR code image to model directory (if it's not already there)
        if self.image_path.parent != model_dir:
            import shutil
            shutil.move(str(self.image_path), str(qr_file))
            print(f"✓ QR code moved to: {qr_file}")

        # Create metadata JSON first (before time-consuming STL generation)
        print("→ Creating metadata JSON...")
        metadata = self.create_metadata_json(dimensions, matrix, qr_input=qr_input)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"✓ Metadata saved: {json_file}")

        # Generate OpenSCAD code
        print("→ Generating OpenSCAD code...")
        scad_code = self.generate_openscad(matrix, dimensions)

        # Save SCAD file
        self.save_scad_file(scad_code, scad_file)

        # Try to export STL (most time-consuming step)
        print("→ Exporting STL...")
        self.export_stl(scad_file, stl_file)

        print(f"\n✅ Done! All files in: {model_dir}")
        return scad_file, stl_file, json_file


def main():
    parser = argparse.ArgumentParser(
        description='Generate 3D printable models from QR code images or URLs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s myqr.png
  %(prog)s celox.png --mode pendant
  %(prog)s https://example.com --mode pendant --name mylink
  %(prog)s "https://github.com/user/repo" --output ./output
        """
    )

    parser.add_argument('input', type=str, help='QR code image file (PNG/JPG) or URL to encode')
    parser.add_argument('--mode', type=str, choices=['square', 'pendant', 'rectangle-text', 'pendant-text', 'rectangle-text-2x'], default='square',
                        help='Model type: square (default), pendant (with hole), rectangle-text (with text bottom), pendant-text (pendant with text), rectangle-text-2x (text top AND bottom)')
    parser.add_argument('--text', '-t', type=str, default='',
                        help='Text to display under QR code (max 20 characters, for *-text modes)')
    parser.add_argument('--text-top', type=str, default='',
                        help='Text to display above QR code (max 20 characters, only for rectangle-text-2x mode)')
    parser.add_argument('--text-rotation', type=int, choices=[0, 180], default=0,
                        help='Rotate text 180 degrees in Z-axis (default: 0, automatic for pendant-text mode, always 180 for rectangle-text-2x)')
    parser.add_argument('--output', '-o', type=str, default=str(DEFAULT_OUTPUT_DIR),
                        help=f'Output directory for generated files (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--name', '-n', type=str, default=None,
                        help='Base name for output files (default: derived from input)')

    args = parser.parse_args()

    # Expand user path and create output directory if needed
    output_dir = Path(args.output).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if input is URL or file
    input_path = args.input
    temp_file = None

    # Determine output name
    output_name = None
    if args.name:
        output_name = args.name
    elif QRModelGenerator.is_url(args.input):
        # Create safe filename from URL
        output_name = re.sub(r'[^\w\-]', '_', args.input)[:50]

    if QRModelGenerator.is_url(args.input):
        # Generate QR code from URL - save to temp location
        print(f"📡 Generating QR code from URL: {args.input}")

        # Generate QR to temporary file (generate() will handle final placement)
        input_path = QRModelGenerator.generate_qr_image(args.input)
        print(f"✓ QR code generated")
        temp_file = input_path
    else:
        # Validate file exists
        if not os.path.exists(args.input):
            print(f"❌ Error: Image file not found: {args.input}")
            sys.exit(1)

    # Validate text parameters
    text_content = args.text.strip()
    text_content_top = args.text_top.strip()

    if text_content and len(text_content) > 20:
        print(f"❌ Error: Text too long ({len(text_content)} characters). Maximum is 20 characters.")
        sys.exit(1)

    if text_content_top and len(text_content_top) > 20:
        print(f"❌ Error: Top text too long ({len(text_content_top)} characters). Maximum is 20 characters.")
        sys.exit(1)

    # Validate text mode compatibility
    if text_content and args.mode not in ['rectangle-text', 'pendant-text', 'rectangle-text-2x']:
        print(f"⚠️  Warning: Text parameter ignored for mode '{args.mode}'. Use text modes for text.")

    if text_content_top and args.mode != 'rectangle-text-2x':
        print(f"⚠️  Warning: Top text parameter ignored for mode '{args.mode}'. Only 'rectangle-text-2x' mode supports top text.")

    # Generate model
    try:
        generator = QRModelGenerator(input_path, args.mode, str(output_dir), output_name=output_name)
        generator.text_content = text_content
        generator.text_content_top = text_content_top

        # Set text rotation (automatic for pendant-text and rectangle-text-2x)
        if args.mode in ['pendant-text', 'rectangle-text-2x']:
            generator.text_rotation = 180  # Always rotated for these modes
        else:
            generator.text_rotation = args.text_rotation

        scad_file, stl_file, json_file = generator.generate(qr_input=args.input)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
