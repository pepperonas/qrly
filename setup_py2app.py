"""
py2app setup script for Qrly
"""
from setuptools import setup
import os

# Check if icon exists, use it if available
icon_file = 'assets/icons/app_icon.icns' if os.path.exists('assets/icons/app_icon.icns') else None

APP = ['src/qrly/app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'semi_standalone': True,  # Don't bundle Python framework, use system Python
    'plist': {
        'CFBundleName': 'Qrly',
        'CFBundleDisplayName': 'Qrly - QR Code 3D Generator',
        'CFBundleIdentifier': 'com.qrly.app',
        'CFBundleVersion': '0.3.2',
        'CFBundleShortVersionString': '0.3.2',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
    'packages': ['PyQt6', 'PIL', 'qrcode', 'qrly'],
    'includes': ['PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui'],
    'excludes': ['matplotlib', 'numpy', 'pandas', 'scipy', 'pyvista', 'pyvistaqt', 'vtk', 'vtkmodules', 'test', 'tkinter', 'Tkinter'],
}

if icon_file:
    OPTIONS['iconfile'] = icon_file

setup(
    app=APP,
    name='Qrly',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
