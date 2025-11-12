#!/usr/bin/env python3
"""
Generate app icons for all platforms from a source PNG image.
Usage: python scripts/generate_icons.py <source_image.png>
"""

import sys
import os
from PIL import Image

def generate_icons(source_path):
    """Generate icons for macOS (.icns), Windows (.ico), and Linux (.png)"""

    if not os.path.exists(source_path):
        print(f"Error: Source image not found: {source_path}")
        sys.exit(1)

    # Load source image
    img = Image.open(source_path)

    # Ensure RGBA mode
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Create output directory
    output_dir = "assets/icons"
    os.makedirs(output_dir, exist_ok=True)

    # Save original as app_icon.png (1024x1024 for high quality)
    img_1024 = img.resize((1024, 1024), Image.Resampling.LANCZOS)
    img_1024.save(os.path.join(output_dir, "app_icon.png"))
    print(f"✓ Created: {output_dir}/app_icon.png (1024x1024)")

    # Generate Windows .ico (multiple sizes in one file)
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = [img.resize(size, Image.Resampling.LANCZOS) for size in ico_sizes]
    ico_path = os.path.join(output_dir, "app_icon.ico")
    ico_images[0].save(
        ico_path,
        format='ICO',
        sizes=ico_sizes,
        append_images=ico_images[1:]
    )
    print(f"✓ Created: {output_dir}/app_icon.ico (multi-size)")

    # Generate macOS .icns using pillow-icns or iconutil
    # For now, we'll create PNG files and note that .icns needs to be created manually
    # or using iconutil on macOS

    # Create iconset directory for macOS
    iconset_dir = os.path.join(output_dir, "app_icon.iconset")
    os.makedirs(iconset_dir, exist_ok=True)

    # macOS icon sizes (standard iconset format)
    macos_sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    for size, filename in macos_sizes:
        icon_img = img.resize((size, size), Image.Resampling.LANCZOS)
        icon_img.save(os.path.join(iconset_dir, filename))

    print(f"✓ Created: {iconset_dir}/ (iconset directory)")

    # Try to create .icns using iconutil (macOS only)
    if sys.platform == 'darwin':
        import subprocess
        try:
            icns_path = os.path.join(output_dir, "app_icon.icns")
            subprocess.run(
                ['iconutil', '-c', 'icns', iconset_dir, '-o', icns_path],
                check=True
            )
            print(f"✓ Created: {output_dir}/app_icon.icns (macOS)")

            # Clean up iconset directory
            import shutil
            shutil.rmtree(iconset_dir)
            print(f"✓ Cleaned up iconset directory")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠ Could not create .icns: {e}")
            print(f"  Keep iconset directory for manual conversion")
    else:
        print(f"⚠ Not on macOS - .icns creation skipped")
        print(f"  To create .icns on macOS, run:")
        print(f"  iconutil -c icns {iconset_dir} -o {output_dir}/app_icon.icns")

    # Generate Linux icons (standard sizes)
    linux_sizes = [16, 32, 48, 64, 128, 256, 512]
    linux_dir = os.path.join(output_dir, "linux")
    os.makedirs(linux_dir, exist_ok=True)

    for size in linux_sizes:
        linux_img = img.resize((size, size), Image.Resampling.LANCZOS)
        linux_img.save(os.path.join(linux_dir, f"icon_{size}x{size}.png"))

    print(f"✓ Created: {linux_dir}/ (Linux icons)")

    print("\n✅ All icons generated successfully!")
    print("\nNext steps:")
    print("1. Review the generated icons in assets/icons/")
    print("2. Update qrly.spec to use the new icons")
    print("3. Commit the icons to the repository")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/generate_icons.py <source_image.png>")
        print("Example: python scripts/generate_icons.py ~/Downloads/app_icon.png")
        sys.exit(1)

    generate_icons(sys.argv[1])
