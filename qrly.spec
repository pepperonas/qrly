# -*- mode: python ; coding: utf-8 -*-
"""
Simple PyInstaller spec for Qrly - macOS .app bundle
"""

import sys

block_cipher = None

a = Analysis(
    ['src/qrly/app.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy packages we don't use
        'pyvista',
        'pyvistaqt',
        'vtk',
        'vtkmodules',
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.icns',
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

# Create macOS .app bundle
app = BUNDLE(
    coll,
    name='Qrly.app',
    icon='assets/icons/app_icon.icns',
    bundle_identifier='com.qrly.app',
    version='0.3.3',
    info_plist={
        'CFBundleName': 'Qrly',
        'CFBundleDisplayName': 'Qrly - QR Code 3D Generator',
        'CFBundleVersion': '0.3.3',
        'CFBundleShortVersionString': '0.3.3',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
