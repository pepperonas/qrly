# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Qrly - QR Code 3D Generator
Builds standalone executables with bundled OpenSCAD for macOS, Windows, and Linux
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# NOTE: Don't collect PyQt6 data files - they contain Qt frameworks with symlink issues
# PyInstaller will handle PyQt6 Python modules automatically
pyqt6_datas = []

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
    # NOTE: qrly.gui.viewer_widget REMOVED - it pulls in PyVista/VTK (300+ MB!)
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
        # NOTE: qrly/gui/ REMOVED - viewer_widget.py pulls in PyVista/VTK
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
        # Exclude PyVista/VTK (300+ MB!) - we don't use 3D viewer
        'pyvista',
        'pyvistaqt',
        'vtk',
        'vtkmodules',
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

# macOS: Filter Qt frameworks - keep only Core/Widgets/Gui, remove rest (symlink issues)
if sys.platform == 'darwin':
    print("Filtering Qt .framework files (keeping Core/Widgets/Gui only)...")

    # List of Qt frameworks we NEED (minimal set + dependencies)
    required_qt_frameworks = {
        'QtCore.framework',
        'QtWidgets.framework',
        'QtGui.framework',
        'QtDBus.framework',  # Required by QtGui
    }

    def should_keep(path):
        # Keep if not a framework
        if '.framework' not in path:
            return True
        # Keep Python.framework (required by PyInstaller)
        if 'Python.framework' in path:
            return True
        # Keep required Qt frameworks
        for req_fw in required_qt_frameworks:
            if req_fw in path:
                return True
        # Filter out all other Qt frameworks (they have symlink issues)
        if '/Qt' in path and '.framework' in path:
            return False
        return True

    a.binaries = [x for x in a.binaries if should_keep(x[0])]
    a.datas = [x for x in a.datas if should_keep(x[0])]
    print(f"Binaries after filtering: {len(a.binaries)}")
    print(f"Datas after filtering: {len(a.datas)}")

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

# macOS: BUNDLE disabled due to Qt framework symlink issues in COLLECT
# Workflow will manually create .app from onedir output
# if sys.platform == 'darwin':
#     app = BUNDLE(
#         coll,
#         name='Qrly.app',
#         icon='assets/icons/app_icon.icns',
#         bundle_identifier='com.qrly.app',
#         info_plist={
#             'CFBundleName': 'Qrly',
#             'CFBundleDisplayName': 'Qrly - QR Code 3D Generator',
#             'CFBundleVersion': '0.3.1',
#             'CFBundleShortVersionString': '0.3.1',
#             'NSHighResolutionCapable': 'True',
#             'LSMinimumSystemVersion': '10.13.0',
#         },
#     )
