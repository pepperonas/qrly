#!/usr/bin/env python3
"""
QR Code 3D Model Generator
Converts QR code images (PNG/JPG) or URLs to 3D-printable OpenSCAD models
"""

import argparse
import os
import sys
import re
from pathlib import Path
from PIL import Image
import subprocess
import qrcode
import tempfile


class QRModelGenerator:
    """Generate 3D models from QR code images"""

    def __init__(self, image_path, mode='square', output_dir='.'):
        self.image_path = Path(image_path)
        self.mode = mode
        self.output_dir = Path(output_dir)

        # Design parameters
        self.card_width = 55    # mm - credit card width
        self.card_height = 1.25 # mm - card thickness
        self.qr_margin = 2.0    # mm - margin around QR code
        self.qr_relief = 1.0    # mm - height of raised QR code
        self.corner_radius = 2  # mm - rounded corners

        # Pendant mode specific
        self.hole_diameter = 5  # mm
        self.hole_from_top = 6  # mm - distance from top to hole center
        self.top_margin = 8     # mm - total top margin for pendant (hole area + margin)

        # Text mode specific (for rectangle-text and pendant-text)
        self.text_content = ""   # Text to display under QR code
        self.text_size = 6       # Font size in mm (reduced from 8 to fit 12 chars)
        self.text_height = 1.0   # Relief height of text (same as QR)
        self.text_margin = 2     # Distance between QR code and text in mm
        self.text_rotation = 0   # Rotation in Z-axis (0 or 180 degrees)

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
        if self.mode in ['rectangle-text', 'pendant-text'] and self.text_content:
            # Determine available width for text based on mode
            if self.mode == 'rectangle-text':
                card_width_for_text = 54  # Rectangle mode uses 54mm width
            else:  # pendant-text
                card_width_for_text = self.card_width  # 55mm

            # Calculate available width (card width minus margins and safety buffer)
            available_text_width = card_width_for_text - (2 * self.qr_margin) - 4  # 4mm safety buffer

            # Calculate and set dynamic text size
            self.text_size = self.calculate_text_size(self.text_content, available_text_width)

        # Text area height calculation (if text mode)
        text_area_height = 0
        if self.mode in ['rectangle-text', 'pendant-text'] and self.text_content:
            text_area_height = self.text_size + self.text_margin + self.qr_margin  # text height + spacing + bottom margin

        if self.mode == 'square':
            # Square mode: QR code with equal margins
            available_width = self.card_width - (2 * self.qr_margin)
            available_height = self.card_width - (2 * self.qr_margin)
            card_length = self.card_width
            qr_offset_y = self.qr_margin

        elif self.mode == 'rectangle-text':
            # Rectangle-text mode: 54x64mm, QR top, text bottom
            card_width = 54  # Custom width for rectangle
            available_width = card_width - (2 * self.qr_margin)
            available_height = available_width  # Keep QR code square
            card_length = 64  # Fixed length for rectangle-text (reduced from 74)
            qr_offset_y = self.qr_margin

        elif self.mode == 'pendant-text':
            # Pendant-text mode: Like pendant but with text area at bottom
            available_width = self.card_width - (2 * self.qr_margin)
            available_height = available_width  # Keep QR code square
            card_length = available_height + self.qr_margin + self.top_margin + text_area_height
            qr_offset_y = self.top_margin

        else:  # pendant mode
            # Pendant mode: extra space at top for hole
            available_width = self.card_width - (2 * self.qr_margin)
            available_height = available_width  # Keep QR code square
            card_length = available_height + self.qr_margin + self.top_margin
            qr_offset_y = self.top_margin

        pixel_size = min(available_width / qr_pixels, available_height / qr_pixels)

        # Calculate text position if text mode
        text_offset_y = 0
        if self.mode in ['rectangle-text', 'pendant-text'] and self.text_content:
            base_offset = qr_offset_y + (pixel_size * qr_pixels) + self.text_margin
            # If text is rotated 180°, we need to adjust the Y position
            # When rotated, the text grows upward from the anchor point instead of downward
            if self.text_rotation == 180:
                # Add the text height to push the anchor point down so rotated text doesn't overlap QR
                text_offset_y = base_offset + self.text_size
            else:
                text_offset_y = base_offset

        return {
            'card_length': card_length,
            'card_width': self.card_width if self.mode != 'rectangle-text' else 54,
            'pixel_size': pixel_size,
            'qr_offset_x': self.qr_margin,
            'qr_offset_y': qr_offset_y,
            'qr_size': pixel_size * qr_pixels,
            'has_text': bool(self.text_content and self.mode in ['rectangle-text', 'pendant-text']),
            'text_offset_y': text_offset_y,
            'text_offset_x': (54 if self.mode == 'rectangle-text' else self.card_width) / 2  # Center text
        }

    def generate_openscad(self, matrix, dimensions):
        """Generate OpenSCAD code"""
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0

        # Escape text for OpenSCAD (replace quotes)
        safe_text = self.text_content.replace('"', '\\"') if self.text_content else ""

        scad_code = f"""// QR Code 3D Model
// Generated from: {self.image_path.name}
// Mode: {self.mode}

$fn = 12;  // Smoothness of curves (optimized for speed)

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

// Text parameters
has_text = {str(dimensions['has_text']).lower()};
text_content = "{safe_text}";
text_size = {self.text_size};
text_height = {self.text_height};
text_offset_x = {dimensions['text_offset_x']};
text_offset_y = {dimensions['text_offset_y']};
text_rotation = {self.text_rotation};  // Z-axis rotation (0 or 180 degrees)

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

// Text module
module text_label() {{
    if (has_text) {{
        translate([text_offset_x, text_offset_y, card_height])
        rotate([0, 0, text_rotation])
        linear_extrude(height=text_height)
        text(text_content, size=text_size, font="Liberation Mono:style=Bold",
             halign="center", valign="bottom");
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

        // Text label (if enabled)
        text_label();
    }}
"""

        # Add hole for pendant modes
        if self.mode in ['pendant', 'pendant-text']:
            hole_x = dimensions['card_width'] / 2
            hole_y = self.hole_from_top
            scad_code += f"""
    // Hole for chain
    translate([{hole_x}, {hole_y}, -1])
        cylinder(d={self.hole_diameter}, h=card_height + 2);
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

    def export_stl(self, scad_path, stl_path, background=False):
        """Export STL using OpenSCAD command line"""
        try:
            if background:
                # Start OpenSCAD in background
                print(f"  Starting OpenSCAD export in background...")
                process = subprocess.Popen(
                    ['openscad', '-o', str(stl_path), str(scad_path)],
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
                    ['openscad', '-o', str(stl_path), str(scad_path)],
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

    def generate(self):
        """Main generation process"""
        print(f"Processing: {self.image_path.name}")
        print(f"Mode: {self.mode}")

        # Load and process image
        print("→ Loading image...")
        matrix, width, height = self.load_and_process_image()
        print(f"  QR code matrix: {width}x{height} pixels")

        # Calculate dimensions
        dimensions = self.calculate_dimensions(width)
        print(f"  Model size: {dimensions['card_width']}x{dimensions['card_length']}x{self.card_height}mm")

        # Generate OpenSCAD code
        print("→ Generating OpenSCAD code...")
        scad_code = self.generate_openscad(matrix, dimensions)

        # Determine output filenames
        base_name = self.image_path.stem  # filename without extension
        scad_file = self.output_dir / f"{base_name}-model.scad"
        stl_file = self.output_dir / f"{base_name}-model.stl"

        # Save SCAD file
        self.save_scad_file(scad_code, scad_file)

        # Try to export STL
        print("→ Exporting STL...")
        self.export_stl(scad_file, stl_file)

        print("\n✅ Done!")
        return scad_file, stl_file


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
    parser.add_argument('--mode', type=str, choices=['square', 'pendant', 'rectangle-text', 'pendant-text'], default='square',
                        help='Model type: square (default), pendant (with hole), rectangle-text (54x74mm with text), pendant-text (pendant with text)')
    parser.add_argument('--text', '-t', type=str, default='',
                        help='Text to display under QR code (max 12 characters, only for *-text modes)')
    parser.add_argument('--text-rotation', type=int, choices=[0, 180], default=0,
                        help='Rotate text 180 degrees in Z-axis (default: 0, automatic for pendant-text mode)')
    parser.add_argument('--output', '-o', type=str, default='generated',
                        help='Output directory for generated files (default: ./generated)')
    parser.add_argument('--name', '-n', type=str, default=None,
                        help='Base name for output files (default: derived from input)')

    args = parser.parse_args()

    # Create output directory if needed
    os.makedirs(args.output, exist_ok=True)

    # Check if input is URL or file
    input_path = args.input
    temp_file = None

    if QRModelGenerator.is_url(args.input):
        # Generate QR code from URL
        print(f"📡 Generating QR code from URL: {args.input}")

        # Determine output filename
        if args.name:
            qr_filename = f"{args.name}.png"
        else:
            # Create safe filename from URL
            safe_name = re.sub(r'[^\w\-]', '_', args.input)[:50]
            qr_filename = f"{safe_name}.png"

        qr_path = Path(args.output) / qr_filename
        QRModelGenerator.generate_qr_image(args.input, qr_path)
        print(f"✓ QR code saved: {qr_path}")
        input_path = str(qr_path)
    else:
        # Validate file exists
        if not os.path.exists(args.input):
            print(f"❌ Error: Image file not found: {args.input}")
            sys.exit(1)

    # Validate text parameter
    text_content = args.text.strip()
    if text_content and len(text_content) > 12:
        print(f"❌ Error: Text too long ({len(text_content)} characters). Maximum is 12 characters.")
        sys.exit(1)

    if text_content and args.mode not in ['rectangle-text', 'pendant-text']:
        print(f"⚠️  Warning: Text parameter ignored for mode '{args.mode}'. Use 'rectangle-text' or 'pendant-text' mode for text.")

    # Generate model
    try:
        generator = QRModelGenerator(input_path, args.mode, args.output)
        generator.text_content = text_content

        # Set text rotation (automatic for pendant-text, user choice for rectangle-text)
        if args.mode == 'pendant-text':
            generator.text_rotation = 180  # Always rotated for pendant mode
        else:
            generator.text_rotation = args.text_rotation

        generator.generate()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
