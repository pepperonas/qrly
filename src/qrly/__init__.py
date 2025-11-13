"""qrly - Generate 3D-printable QR code models

This package provides tools to create 3D-printable QR code models
from URLs or images, with support for various shapes and text labels.
"""

__version__ = "0.3.2"
__author__ = "Martin Pfeffer"

from .generator import QRModelGenerator
from .app import SimpleMainWindow

__all__ = ['QRModelGenerator', 'SimpleMainWindow', '__version__']
