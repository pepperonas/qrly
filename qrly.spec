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

# OpenSCAD will be bundled AFTER PyInstaller build to avoid symlink conflicts
# (PyInstaller has issues with Tree() on macOS frameworks with symlinks)

a = Analysis(
    ['src/qrly/app.py'],
    pathex=['src'],
    binaries=[],
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
        # Exclude unused PyQt6 modules to avoid symlink conflicts
        'PyQt6.QtBluetooth',
        'PyQt6.QtDBus',
        'PyQt6.QtDesigner',
        'PyQt6.QtHelp',
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
        'PyQt6.QtNetwork',
        'PyQt6.QtNetworkAuth',
        'PyQt6.QtNfc',
        'PyQt6.QtOpenGL',
        'PyQt6.QtOpenGLWidgets',
        'PyQt6.QtPositioning',
        'PyQt6.QtPrintSupport',
        'PyQt6.QtQml',
        'PyQt6.QtQuick',
        'PyQt6.QtQuick3D',
        'PyQt6.QtQuickWidgets',
        'PyQt6.QtRemoteObjects',
        'PyQt6.QtSensors',
        'PyQt6.QtSerialPort',
        'PyQt6.QtSql',
        'PyQt6.QtSvg',
        'PyQt6.QtSvgWidgets',
        'PyQt6.QtTest',
        'PyQt6.QtWebChannel',
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtWebEngineQuick',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebSockets',
        'PyQt6.QtXml',
        'PyQt6.Qt3DAnimation',
        'PyQt6.Qt3DCore',
        'PyQt6.Qt3DExtras',
        'PyQt6.Qt3DInput',
        'PyQt6.Qt3DLogic',
        'PyQt6.Qt3DRender',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# macOS: BUNDLE mode handles all frameworks correctly, no filtering needed
# Previously we filtered Qt frameworks to avoid symlink issues in COLLECT mode,
# but BUNDLE mode can handle framework symlinks properly
if sys.platform == 'darwin':
    print("Using PyInstaller BUNDLE - all frameworks will be included")
    print(f"Binaries: {len(a.binaries)}")
    print(f"Datas: {len(a.datas)}")

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

# macOS: .app bundle creation now works after filtering Qt frameworks
# PyInstaller BUNDLE creates proper .app structure with correct Python paths
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='Qrly.app',
        icon='assets/icons/app_icon.icns',
        bundle_identifier='com.qrly.app',
        info_plist={
            'CFBundleName': 'Qrly',
            'CFBundleDisplayName': 'Qrly - QR Code 3D Generator',
            'CFBundleVersion': '0.3.1',
            'CFBundleShortVersionString': '0.3.1',
            'NSHighResolutionCapable': 'True',
            'LSMinimumSystemVersion': '10.13.0',
        },
    )
