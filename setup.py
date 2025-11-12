"""
py2app setup script for Qrly - macOS-specific build
"""

from setuptools import setup

APP = ['src/qrly/app.py']
DATA_FILES = [
    ('assets/icons', ['assets/icons/app_icon.icns']),
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/icons/app_icon.icns',
    'plist': {
        'CFBundleName': 'Qrly',
        'CFBundleDisplayName': 'Qrly - QR Code 3D Generator',
        'CFBundleIdentifier': 'com.qrly.app',
        'CFBundleVersion': '0.3.0',
        'CFBundleShortVersionString': '0.3.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
    'packages': ['PyQt6', 'qrly', 'PIL', 'qrcode'],
    'includes': ['PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui'],
    'excludes': [
        'matplotlib', 'numpy', 'scipy', 'pandas', 'tkinter',
        'PyQt6.QtBluetooth', 'PyQt6.Qt3DCore', 'PyQt6.QtWebEngine',
    ],
}

setup(
    name='Qrly',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
