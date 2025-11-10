#!/usr/bin/env python3
"""
QR Code 3D Generator - Simplified GUI without 3D viewer
"""

import sys
import json
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QGridLayout, QProgressBar, QFileDialog, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from generate_qr_model import QRModelGenerator
from __version__ import __version__


class GeneratorThread(QThread):
    """Background thread for STL generation"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str, str)  # success, stl_path, message

    def __init__(self, input_path, output_name, mode, params, text_content='', text_rotation=0):
        super().__init__()
        self.input_path = input_path
        self.output_name = output_name
        self.mode = mode
        self.params = params
        self.text_content = text_content
        self.text_rotation = text_rotation

    def run(self):
        try:
            # Check if input is a URL
            actual_input = self.input_path
            temp_qr_file = None

            if QRModelGenerator.is_url(self.input_path):
                # Generate QR code from URL
                self.progress.emit(f"Generating QR code from URL...")

                # Create QR code image in generated folder
                from pathlib import Path
                import os

                output_dir = Path("generated")
                os.makedirs(output_dir, exist_ok=True)

                qr_filename = f"{self.output_name}.png"
                qr_path = output_dir / qr_filename

                QRModelGenerator.generate_qr_image(self.input_path, qr_path)
                actual_input = str(qr_path)
                self.progress.emit(f"QR code created: {qr_filename}")

            self.progress.emit("Generating 3D model...")

            generator = QRModelGenerator(
                actual_input,
                self.mode,
                "generated"
            )

            # Apply custom parameters
            generator.card_height = self.params['height']
            generator.qr_margin = self.params['margin']
            generator.qr_relief = self.params['relief']
            generator.corner_radius = self.params['corner_radius']
            generator.text_content = self.text_content
            generator.text_rotation = self.text_rotation

            self.progress.emit("Creating 3D model...")
            scad_path, stl_path = generator.generate()

            self.progress.emit("Model generated successfully!")
            self.finished.emit(True, str(stl_path), f"Generated: {Path(stl_path).name}")

        except Exception as e:
            self.finished.emit(False, "", f"Error: {str(e)}")


class BatchGeneratorThread(QThread):
    """Background thread for batch STL generation"""
    progress = pyqtSignal(str)  # Progress message
    model_progress = pyqtSignal(int, int, str)  # current, total, model_name
    finished = pyqtSignal(bool, int, int, str)  # success, successful_count, total_count, message

    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path

    def run(self):
        try:
            # Load configuration
            self.progress.emit("Loading batch configuration...")
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            global_params = config.get('global_params', {})
            models = config.get('models', [])

            if not models:
                self.finished.emit(False, 0, 0, "No models found in configuration")
                return

            total = len(models)
            successful = 0
            failed_models = []

            # Process each model
            for idx, model_config in enumerate(models, 1):
                try:
                    # Validate required fields
                    if 'name' not in model_config or 'url' not in model_config or 'mode' not in model_config:
                        failed_models.append(f"{model_config.get('name', f'Model {idx}')} (missing required fields)")
                        self.progress.emit(f"⚠️ Skipping model {idx}/{total}: Missing required fields")
                        continue

                    name = model_config['name']
                    url = model_config['url']
                    mode = model_config['mode']

                    self.model_progress.emit(idx, total, name)
                    self.progress.emit(f"Processing {idx}/{total}: {name}")

                    # Check if input is a URL
                    actual_input = url
                    if QRModelGenerator.is_url(url):
                        self.progress.emit(f"Generating QR code from URL...")
                        output_dir = Path("generated")
                        os.makedirs(output_dir, exist_ok=True)

                        qr_filename = f"{name}.png"
                        qr_path = output_dir / qr_filename
                        QRModelGenerator.generate_qr_image(url, qr_path)
                        actual_input = str(qr_path)

                    # Create generator
                    generator = QRModelGenerator(actual_input, mode, "generated")

                    # Apply global parameters (with model-specific overrides)
                    generator.card_height = model_config.get('card_height', global_params.get('card_height', 1.25))
                    generator.qr_margin = model_config.get('qr_margin', global_params.get('qr_margin', 0.5))
                    generator.qr_relief = model_config.get('qr_relief', global_params.get('qr_relief', 1.0))
                    generator.corner_radius = model_config.get('corner_radius', global_params.get('corner_radius', 2))

                    # Text mode parameters
                    generator.text_content = model_config.get('text', '')
                    generator.text_rotation = model_config.get('text_rotation', 0)

                    # Generate model
                    self.progress.emit(f"Creating 3D model for {name}...")
                    scad_path, stl_path = generator.generate()

                    successful += 1
                    self.progress.emit(f"✅ {name} completed ({idx}/{total})")

                except Exception as e:
                    failed_models.append(f"{model_config.get('name', f'Model {idx}')} ({str(e)})")
                    self.progress.emit(f"❌ Failed: {model_config.get('name', f'Model {idx}')} - {str(e)}")

            # Final summary
            if successful == total:
                message = f"All {total} models generated successfully!"
            else:
                failed_count = total - successful
                message = f"Completed: {successful}/{total} models. Failed: {failed_count}"
                if failed_models:
                    message += f"\n\nFailed models:\n" + "\n".join(f"• {m}" for m in failed_models)

            self.finished.emit(successful == total, successful, total, message)

        except json.JSONDecodeError as e:
            self.finished.emit(False, 0, 0, f"JSON Parse Error: {str(e)}")
        except Exception as e:
            self.finished.emit(False, 0, 0, f"Batch Error: {str(e)}")


class SimpleMainWindow(QMainWindow):
    """Simplified main window without 3D viewer"""

    def __init__(self):
        super().__init__()
        self.generator_thread = None
        self.batch_thread = None
        self.batch_config_path = Path("batch/config.json")
        self.setup_ui()

        # Setup timer for batch status updates (every 5 seconds)
        self.batch_status_timer = QTimer(self)
        self.batch_status_timer.timeout.connect(self.update_batch_status)
        self.batch_status_timer.start(5000)  # 5000ms = 5 seconds

        # Initial batch status update
        self.update_batch_status()

    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle(f"QR Code 3D Generator v{__version__} (Simple Mode)")
        self.setMinimumSize(600, 700)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("QR Code 3D Model Generator")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Input section
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout()

        # URL/File input
        url_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter URL or select image file...")
        url_layout.addWidget(self.input_field)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        url_layout.addWidget(browse_btn)
        input_layout.addLayout(url_layout)

        # Output name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Output name:"))
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Auto-generated from input")
        name_layout.addWidget(self.name_field)
        input_layout.addLayout(name_layout)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Mode selection
        mode_group = QGroupBox("Model Type")
        mode_layout = QVBoxLayout()

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Square (55x55mm)",
            "Pendant (with hole)",
            "Rectangle + Text (54x64mm)",
            "Pendant + Text (55x65mm)"
        ])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)

        # Text input (only visible for text modes)
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text:"))
        self.text_field = QLineEdit()
        self.text_field.setPlaceholderText("Enter text (max 20 chars)")
        self.text_field.setMaxLength(20)
        text_layout.addWidget(self.text_field)
        mode_layout.addLayout(text_layout)

        # Text rotation checkbox (only visible for Rectangle+Text mode)
        self.text_rotation_checkbox = QCheckBox("Rotate text 180° (upside down)")
        mode_layout.addWidget(self.text_rotation_checkbox)

        # Store text widgets for show/hide
        self.text_label = text_layout.itemAt(0).widget()

        # Initially hide text field and rotation checkbox (square mode is default)
        self.text_label.setVisible(False)
        self.text_field.setVisible(False)
        self.text_rotation_checkbox.setVisible(False)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Parameters section - 2x2 Grid Layout
        params_group = QGroupBox("Parameters")
        params_layout = QGridLayout()

        # Row 1, Column 1: Card Height
        params_layout.addWidget(QLabel("Card Height:"), 0, 0)
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.5, 5.0)
        self.height_spin.setValue(1.25)
        self.height_spin.setSingleStep(0.25)
        self.height_spin.setSuffix(" mm")
        params_layout.addWidget(self.height_spin, 0, 1)

        # Row 1, Column 2: QR Margin
        params_layout.addWidget(QLabel("QR Margin:"), 0, 2)
        self.margin_spin = QDoubleSpinBox()
        self.margin_spin.setRange(0, 10)
        self.margin_spin.setValue(2.0)
        self.margin_spin.setSingleStep(0.25)
        self.margin_spin.setSuffix(" mm")
        params_layout.addWidget(self.margin_spin, 0, 3)

        # Row 2, Column 1: QR Relief
        params_layout.addWidget(QLabel("QR Relief:"), 1, 0)
        self.relief_spin = QDoubleSpinBox()
        self.relief_spin.setRange(0.1, 2.0)
        self.relief_spin.setValue(1.0)
        self.relief_spin.setSingleStep(0.1)
        self.relief_spin.setSuffix(" mm")
        params_layout.addWidget(self.relief_spin, 1, 1)

        # Row 2, Column 2: Corner Radius
        params_layout.addWidget(QLabel("Corner Radius:"), 1, 2)
        self.corner_spin = QDoubleSpinBox()
        self.corner_spin.setRange(0, 5)
        self.corner_spin.setValue(2)
        self.corner_spin.setSingleStep(0.5)
        self.corner_spin.setSuffix(" mm")
        params_layout.addWidget(self.corner_spin, 1, 3)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Generate button
        self.generate_btn = QPushButton("Generate 3D Model")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_model)
        layout.addWidget(self.generate_btn)

        # Batch processing section
        batch_group = QGroupBox("Batch Processing")
        batch_layout = QVBoxLayout()

        # Batch status label
        self.batch_status_label = QLabel("Checking batch configuration...")
        self.batch_status_label.setWordWrap(True)
        self.batch_status_label.setStyleSheet("padding: 8px; color: #666; font-size: 11px;")
        batch_layout.addWidget(self.batch_status_label)

        # Batch button
        self.batch_btn = QPushButton("Start Batch Generation")
        self.batch_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.batch_btn.clicked.connect(self.on_batch_button_clicked)
        batch_layout.addWidget(self.batch_btn)

        batch_group.setLayout(batch_layout)
        layout.addWidget(batch_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("padding: 10px; color: #666; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Info section
        info_label = QLabel(
            "Note: This is simplified mode without 3D preview.\n\n"
            "Tips:\n"
            "• Enter a URL to generate QR code automatically\n"
            "• Or select a PNG/JPG image file\n"
            "• Square mode: 55x55mm\n"
            "• Pendant mode: 55x61mm with chain hole\n"
            "• Rectangle+Text: 54x64mm with text label\n"
            "• Pendant+Text: ~55x65mm with hole and text\n"
            "• Generated files will be in 'generated' folder"
        )
        info_label.setStyleSheet("""
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            font-size: 11px;
            color: #555;
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

    def browse_file(self):
        """Open file browser to select image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select QR Code Image",
            str(Path.home()),
            "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.input_field.setText(file_path)
            # Auto-fill name from filename
            if not self.name_field.text():
                name = Path(file_path).stem
                self.name_field.setText(name)

    def on_mode_changed(self, index):
        """Show/hide text field and rotation checkbox based on selected mode"""
        # Text modes are indices 2 and 3
        is_text_mode = index >= 2
        self.text_label.setVisible(is_text_mode)
        self.text_field.setVisible(is_text_mode)

        # Rotation checkbox only visible for Rectangle+Text (index 2)
        # Pendant+Text (index 3) always uses 180° rotation automatically
        is_rectangle_text = index == 2
        self.text_rotation_checkbox.setVisible(is_rectangle_text)

    def generate_model(self):
        """Start model generation in background thread"""
        input_text = self.input_field.text().strip()
        if not input_text:
            QMessageBox.warning(self, "Input Required", "Please enter a URL or select an image file.")
            return

        # Get output name
        output_name = self.name_field.text().strip()
        if not output_name:
            # Auto-generate from input
            if input_text.startswith(('http://', 'https://')):
                # Extract domain from URL
                from urllib.parse import urlparse
                parsed = urlparse(input_text)
                output_name = parsed.netloc.replace('www.', '').replace('.', '_')
            else:
                output_name = Path(input_text).stem

        # Get mode
        mode_index = self.mode_combo.currentIndex()
        mode_map = {
            0: 'square',
            1: 'pendant',
            2: 'rectangle-text',
            3: 'pendant-text'
        }
        mode = mode_map.get(mode_index, 'square')

        # Get text content (for text modes)
        text_content = self.text_field.text().strip() if mode_index >= 2 else ''

        # Validate text for text modes
        if mode_index >= 2 and not text_content:
            QMessageBox.warning(self, "Text Required", "Please enter text for the text-mode model.")
            return

        # Get text rotation
        # Pendant+Text: always 180° (automatic)
        # Rectangle+Text: user choice via checkbox
        if mode_index == 3:  # pendant-text
            text_rotation = 180
        elif mode_index == 2:  # rectangle-text
            text_rotation = 180 if self.text_rotation_checkbox.isChecked() else 0
        else:
            text_rotation = 0

        # Get parameters
        params = {
            'height': self.height_spin.value(),
            'margin': self.margin_spin.value(),
            'relief': self.relief_spin.value(),
            'corner_radius': self.corner_spin.value()
        }

        # Start generation in background
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Starting generation...")

        self.generator_thread = GeneratorThread(input_text, output_name, mode, params, text_content, text_rotation)
        self.generator_thread.progress.connect(self.on_progress)
        self.generator_thread.finished.connect(self.on_generation_finished)
        self.generator_thread.start()

    def on_progress(self, message: str):
        """Update progress message"""
        self.status_label.setText(message)

    def on_generation_finished(self, success: bool, stl_path: str, message: str):
        """Handle generation completion"""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            stl_file = Path(stl_path)
            success_msg = f"✅ {message}\n📁 Files saved in: generated/"
            self.status_label.setText(success_msg)
            self.status_label.setStyleSheet("padding: 10px; color: #008800; font-size: 12px; font-weight: bold;")
        else:
            self.status_label.setText(f"❌ {message}")
            self.status_label.setStyleSheet("padding: 10px; color: #cc0000; font-size: 12px; font-weight: bold;")
            QMessageBox.critical(self, "Generation Failed", message)

    def check_batch_config(self):
        """Check batch configuration and return status"""
        try:
            if not self.batch_config_path.exists():
                return False, 0, None

            with open(self.batch_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            models = config.get('models', [])
            return True, len(models), None

        except json.JSONDecodeError as e:
            return True, 0, f"JSON Error: {str(e)}"
        except Exception as e:
            return True, 0, f"Error: {str(e)}"

    def update_batch_status(self):
        """Update batch status label"""
        exists, count, error = self.check_batch_config()

        if error:
            self.batch_status_label.setText(f"⚠️ {error}")
            self.batch_status_label.setStyleSheet("padding: 8px; color: #cc0000; font-size: 11px;")
            self.batch_btn.setText("Create New Config")
            self.batch_btn.setEnabled(True)
        elif not exists:
            self.batch_status_label.setText("📄 No batch configuration found")
            self.batch_status_label.setStyleSheet("padding: 8px; color: #666; font-size: 11px;")
            self.batch_btn.setText("Create Config Template")
            self.batch_btn.setEnabled(True)
        elif count == 0:
            self.batch_status_label.setText("📄 Config exists but no models defined")
            self.batch_status_label.setStyleSheet("padding: 8px; color: #666; font-size: 11px;")
            self.batch_btn.setText("Edit Config")
            self.batch_btn.setEnabled(True)
        else:
            self.batch_status_label.setText(f"✅ Ready: {count} model{'s' if count != 1 else ''} in queue")
            self.batch_status_label.setStyleSheet("padding: 8px; color: #28a745; font-size: 11px; font-weight: bold;")
            self.batch_btn.setText(f"Start Batch ({count} models)")
            self.batch_btn.setEnabled(True)

    def create_default_batch_config(self):
        """Create default batch configuration with examples"""
        config = {
            "global_params": {
                "card_height": 1.25,
                "qr_margin": 2.0,
                "qr_relief": 1.0,
                "corner_radius": 2
            },
            "models": [
                {
                    "name": "example-square",
                    "url": "https://example.com",
                    "mode": "square"
                },
                {
                    "name": "github-pendant",
                    "url": "https://github.com",
                    "mode": "pendant"
                },
                {
                    "name": "custom-text",
                    "url": "https://mysite.com",
                    "mode": "rectangle-text",
                    "text": "CUSTOM TEXT",
                    "text_rotation": 0
                },
                {
                    "name": "pendant-text-example",
                    "url": "https://wikipedia.org",
                    "mode": "pendant-text",
                    "text": "WIKI",
                    "card_height": 1.5
                }
            ]
        }

        # Create batch directory
        batch_dir = self.batch_config_path.parent
        os.makedirs(batch_dir, exist_ok=True)

        # Write config
        with open(self.batch_config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def on_batch_button_clicked(self):
        """Handle batch button click"""
        exists, count, error = self.check_batch_config()

        # Case 1: No config or error - create new config
        if not exists or error:
            try:
                self.create_default_batch_config()
                QMessageBox.information(
                    self,
                    "Config Created",
                    f"Batch configuration template created at:\n{self.batch_config_path}\n\n"
                    "Edit this file to customize your batch jobs, then click the button again to start."
                )
                self.update_batch_status()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create config:\n{str(e)}")
            return

        # Case 2: Config exists but no models
        if count == 0:
            QMessageBox.warning(
                self,
                "No Models",
                f"Configuration file exists but contains no models.\n\n"
                f"Edit the file at:\n{self.batch_config_path}"
            )
            return

        # Case 3: Ready to process - start batch
        reply = QMessageBox.question(
            self,
            "Start Batch Processing",
            f"Ready to generate {count} model{'s' if count != 1 else ''}.\n\n"
            "This may take several minutes depending on complexity.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Disable buttons
            self.generate_btn.setEnabled(False)
            self.batch_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, count)
            self.progress_bar.setValue(0)
            self.status_label.setText("Starting batch processing...")

            # Start batch thread
            self.batch_thread = BatchGeneratorThread(str(self.batch_config_path))
            self.batch_thread.progress.connect(self.on_batch_progress)
            self.batch_thread.model_progress.connect(self.on_batch_model_progress)
            self.batch_thread.finished.connect(self.on_batch_finished)
            self.batch_thread.start()

    def on_batch_progress(self, message: str):
        """Update batch progress message"""
        self.status_label.setText(message)

    def on_batch_model_progress(self, current: int, total: int, name: str):
        """Update batch progress bar"""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Processing {current}/{total}: {name}")

    def on_batch_finished(self, success: bool, successful: int, total: int, message: str):
        """Handle batch generation completion"""
        self.generate_btn.setEnabled(True)
        self.batch_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.status_label.setText(f"✅ {message}\n📁 All files saved in: generated/")
            self.status_label.setStyleSheet("padding: 10px; color: #008800; font-size: 12px; font-weight: bold;")
            QMessageBox.information(self, "Batch Complete", message)
        else:
            self.status_label.setText(f"⚠️ {message}")
            self.status_label.setStyleSheet("padding: 10px; color: #cc6600; font-size: 12px; font-weight: bold;")
            QMessageBox.warning(self, "Batch Completed with Issues", message)


def main():
    print("Starting QR Code 3D Generator (Simple Mode)...")

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("QR Code 3D Generator")
    app.setOrganizationName("QRGen")

    # Create and show main window
    window = SimpleMainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
