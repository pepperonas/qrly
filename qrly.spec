# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Qrly - QR Code 3D Generator
Builds standalone executables with bundled OpenSCAD for macOS, Windows, and Linux
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect PyQt6 data files
pyqt6_datas = collect_data_files('PyQt6')

# Collect all necessary modules
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'PyQt6.QtGui',
    'PIL',
    'PIL.Image',
    'PIL.ImageQt',
    'qrcode',
    'qrcode.image.pil',
    'qrly',
    'qrly.app',
    'qrly.generator',
    'qrly.gui',
    'qrly.gui.viewer_widget',
]

# OpenSCAD binary paths (will be bundled during build)
# These will be added dynamically by the build script
openscad_binaries = []
if os.path.exists('openscad_bundle'):
    if sys.platform == 'darwin':
        openscad_binaries = [('openscad_bundle/OpenSCAD.app', 'OpenSCAD.app')]
    elif sys.platform == 'win32':
        openscad_binaries = [('openscad_bundle/*', 'openscad')]
    else:  # Linux
        openscad_binaries = [('openscad_bundle/*', 'openscad')]

a = Analysis(
    ['src/qrly/app.py'],
    pathex=['src'],
    binaries=openscad_binaries,
    datas=[
        ('src/qrly/__init__.py', 'qrly'),
        ('src/qrly/generator.py', 'qrly'),
        ('src/qrly/gui/', 'qrly/gui'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ] + pyqt6_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'tkinter',
        'pytest',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Qrly',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico' if sys.platform == 'win32' else 'assets/icons/app_icon.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Qrly',
)

# macOS: Create .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='Qrly.app',
        icon='assets/icons/app_icon.icns',
        bundle_identifier='com.qrly.app',
        info_plist={
            'CFBundleName': 'Qrly',
            'CFBundleDisplayName': 'Qrly - QR Code 3D Generator',
            'CFBundleVersion': '0.3.0',
            'CFBundleShortVersionString': '0.3.0',
            'NSHighResolutionCapable': 'True',
            'LSMinimumSystemVersion': '10.13.0',
        },
    )
