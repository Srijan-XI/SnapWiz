#!/usr/bin/env python3
"""
SnapWiz - The Magical Package Installer
A simple GUI tool to help new Linux users install .deb and .rpm packages
Install packages in a snap, like a wizard!
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QProgressBar, QTextEdit, QTabWidget, QListWidget,
                             QMessageBox, QGroupBox, QComboBox, QSystemTrayIcon,
                             QMenu, QAction, QShortcut, QListWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QKeySequence, QPixmap
from package_handler import PackageHandler
from logger import InstallLogger
import json
import time

class InstallerThread(QThread):
    """Thread to handle installation without blocking UI"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    step = pyqtSignal(str)  # New signal for detailed steps
    
    def __init__(self, package_path, package_handler):
        super().__init__()
        self.package_path = package_path
        self.package_handler = package_handler
        
    def run(self):
        """Run the installation process with detailed progress"""
        try:
            # Step 1: Initialization
            self.step.emit("📋 Initializing installation process...")
            self.status.emit("Starting installation...")
            self.progress.emit(5)
            time.sleep(0.3)
            
            # Step 2: Validation
            self.step.emit("🔍 Validating package file...")
            self.status.emit("Checking package type...")
            self.progress.emit(15)
            
            if not self.package_handler.validate_package(self.package_path):
                self.finished.emit(False, "Invalid package file")
                return
            
            time.sleep(0.2)
            self.progress.emit(25)
            
            # Step 3: Reading package information
            self.step.emit("📖 Reading package metadata...")
            self.status.emit("Analyzing package contents...")
            self.progress.emit(35)
            time.sleep(0.3)
            
            # Step 4: Checking dependencies
            self.step.emit("🔗 Checking dependencies...")
            self.status.emit("Verifying system requirements...")
            self.progress.emit(45)
            time.sleep(0.3)
            
            # Step 5: Installing
            self.step.emit("⚙️ Installing package...")
            self.status.emit("Installing package (this may take a while)...")
            self.progress.emit(55)
            
            success, message = self.package_handler.install_package(self.package_path)
            
            if success:
                # Step 6: Configuring
                self.step.emit("🔧 Configuring installation...")
                self.progress.emit(85)
                time.sleep(0.2)
                
                # Step 7: Finalizing
                self.step.emit("✅ Finalizing installation...")
                self.progress.emit(95)
                time.sleep(0.2)
                
                self.progress.emit(100)
                self.step.emit("✅ Installation completed successfully!")
            else:
                self.step.emit("❌ Installation failed!")
            
            self.finished.emit(success, message)
            
        except Exception as e:
            self.step.emit("❌ Error occurred during installation!")
            self.finished.emit(False, f"Error: {str(e)}")


class MainWindow(QMainWindow):
    """Main application window with enhanced UI/UX"""
    
    def __init__(self):
        super().__init__()
        self.package_handler = PackageHandler()
        self.logger = InstallLogger()
        self.current_package = None
        self.current_theme = "Light"  # Default theme
        self.load_settings()
        self.init_ui()
        self.setup_shortcuts()
        self.setup_system_tray()
        self.apply_theme(self.current_theme)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("SnapWiz - The Magical Package Installer")
        self.setGeometry(100, 100, 950, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("⚡🧙‍♂️ SnapWiz")
        header.setAlignment(Qt.AlignCenter)
        header_font = QFont("Arial", 24, QFont.Bold)
        header.setFont(header_font)
        header.setToolTip("Install packages in a snap, like a wizard!")
        main_layout.addWidget(header)
        
        subtitle = QLabel("The magical way to install .deb and .rpm packages")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Arial", 11)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #666; margin-bottom: 10px;")
        main_layout.addWidget(subtitle)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_install_tab(), "📥 Install Package")
        self.tabs.addTab(self.create_history_tab(), "📋 Installation History")
        self.tabs.addTab(self.create_settings_tab(), "⚙️ Settings")
        main_layout.addWidget(self.tabs)
        
        # Status bar for shortcuts
        self.statusBar().showMessage(
            "💡 Shortcuts: Ctrl+O (Open) | Ctrl+I (Install) | F5 (Refresh) | Ctrl+Q (Quit)"
        )
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+O - Open file
        self.open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.open_shortcut.activated.connect(self.browse_package)
        
        # Ctrl+I - Install
        self.install_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        self.install_shortcut.activated.connect(self.install_package)
        
        # Ctrl+Q - Quit
        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.quit_shortcut.activated.connect(self.close)
        
        # F5 - Refresh history
        self.refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        self.refresh_shortcut.activated.connect(self.load_history)
        
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create icon (using default for now)
        icon = self.style().standardIcon(self.style().SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_clicked)
        self.tray_icon.setToolTip("SnapWiz - The Magical Package Installer")
        self.tray_icon.show()
    
    def tray_icon_clicked(self, reason):
        """Handle tray icon clicks"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "SnapWiz",
            "Application minimized to tray. Double-click to restore.",
            QSystemTrayIcon.Information,
            2000
        )
    
    def quit_application(self):
        """Completely quit the application"""
        self.tray_icon.hide()
        QApplication.quit()
        
    def create_install_tab(self):
        """Create the installation tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Package selection group
        select_group = QGroupBox("📁 Select Package")
        select_group.setToolTip("Choose a .deb or .rpm package file to install")
        select_layout = QVBoxLayout()
        
        # File path display
        path_layout = QHBoxLayout()
        self.path_label = QLabel("No package selected")
        self.path_label.setWordWrap(True)
        self.path_label.setToolTip("Path to the selected package file")
        self.path_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                border: 2px dashed #3498db;
                border-radius: 5px;
                background-color: #ecf0f1;
                color: #2c3e50;
            }
        """)
        path_layout.addWidget(self.path_label)
        
        # Browse button
        self.browse_btn = QPushButton("📂 Browse...")
        self.browse_btn.setFixedWidth(140)
        self.browse_btn.setToolTip("Browse for package file (Ctrl+O)")
        self.browse_btn.clicked.connect(self.browse_package)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        path_layout.addWidget(self.browse_btn)
        
        select_layout.addLayout(path_layout)
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)
        
        # Package info group
        info_group = QGroupBox("ℹ️ Package Information")
        info_group.setToolTip("Detailed information about the selected package")
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(100)
        self.info_text.setText("Select a package to see details...")
        self.info_text.setToolTip("Package metadata and description")
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Installation steps display
        steps_group = QGroupBox("🔄 Installation Steps")
        steps_group.setToolTip("Current installation step and progress")
        steps_layout = QVBoxLayout()
        self.steps_label = QLabel("Ready to install")
        self.steps_label.setAlignment(Qt.AlignCenter)
        self.steps_label.setStyleSheet("font-size: 13px; font-weight: bold; padding: 8px;")
        steps_layout.addWidget(self.steps_label)
        steps_group.setLayout(steps_layout)
        layout.addWidget(steps_group)
        
        # Progress group
        progress_group = QGroupBox("📊 Installation Progress")
        progress_group.setToolTip("Real-time progress of the installation")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setToolTip("Installation progress percentage")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to install")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Log output
        log_group = QGroupBox("📝 Installation Log")
        log_group.setToolTip("Detailed output from the installation process")
        log_layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(120)
        self.log_output.setToolTip("Installation commands and output")
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.install_btn = QPushButton("✅ Install Package")
        self.install_btn.setFixedHeight(45)
        self.install_btn.setFixedWidth(220)
        self.install_btn.setEnabled(False)
        self.install_btn.setToolTip("Install the selected package (Ctrl+I)")
        self.install_btn.clicked.connect(self.install_package)
        self.install_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        button_layout.addWidget(self.install_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.setFixedHeight(45)
        self.clear_btn.setFixedWidth(130)
        self.clear_btn.setToolTip("Clear the current selection")
        self.clear_btn.clicked.connect(self.clear_selection)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #5d6d7e;
            }
        """)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        return tab
    
    def create_history_tab(self):
        """Create the installation history tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Info label
        info = QLabel("📋 Installation History - All installed packages")
        info.setFont(QFont("Arial", 10))
        info.setToolTip("Complete history of all package installations")
        layout.addWidget(info)
        
        # History list with custom items
        self.history_list = QListWidget()
        self.history_list.setToolTip("Double-click an item for details (F5 to refresh)")
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        self.load_history()
        layout.addWidget(self.history_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setToolTip("Refresh the installation history (F5)")
        refresh_btn.clicked.connect(self.load_history)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(refresh_btn)
        
        clear_history_btn = QPushButton("🗑️ Clear History")
        clear_history_btn.setToolTip("Permanently delete all history entries")
        clear_history_btn.clicked.connect(self.clear_history)
        clear_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        button_layout.addWidget(clear_history_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return tab
    
    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme settings
        theme_group = QGroupBox("🎨 Appearance")
        theme_group.setToolTip("Customize the application appearance")
        theme_layout = QVBoxLayout()
        
        theme_label = QLabel("Theme:")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(self.current_theme)
        self.theme_combo.setToolTip("Choose between light and dark theme")
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Package manager settings
        pm_group = QGroupBox("📦 Package Manager")
        pm_group.setToolTip("Information about your system's package manager")
        pm_layout = QVBoxLayout()
        
        pm_info = QLabel("Detected Package Manager:")
        pm_layout.addWidget(pm_info)
        
        detected_pm = self.package_handler.detect_package_manager()
        pm_label = QLabel(f"<b>{detected_pm.upper()}</b>")
        pm_label.setToolTip(f"Your system uses {detected_pm} for package management")
        pm_layout.addWidget(pm_label)
        
        pm_group.setLayout(pm_layout)
        layout.addWidget(pm_group)
        
        # About section
        about_group = QGroupBox("ℹ️ About")
        about_group.setToolTip("Information about this application")
        about_layout = QVBoxLayout()
        
        about_text = QLabel(
            "<h3>⚡🧙‍♂️ SnapWiz v1.0</h3>"
            "<p><i>Install packages in a snap, like a wizard!</i></p>"
            "<p>A magical tool to help Linux users install .deb and .rpm packages.</p>"
            "<p><b>Author:</b> Srijan-XI</p>"
            "<p><b>License:</b> MIT License</p>"
            "<p><b>Keyboard Shortcuts:</b></p>"
            "<ul>"
            "<li>Ctrl+O - Open file</li>"
            "<li>Ctrl+I - Install package</li>"
            "<li>F5 - Refresh history</li>"
            "<li>Ctrl+Q - Quit application</li>"
            "</ul>"
        )
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)
        
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)
        
        layout.addStretch()
        return tab
    
    def browse_package(self):
        """Open file dialog to select package"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Package File",
            os.path.expanduser("~"),
            "Package Files (*.deb *.rpm);;Debian Packages (*.deb);;RPM Packages (*.rpm);;All Files (*)"
        )
        
        if file_path:
            self.current_package = file_path
            self.path_label.setText(file_path)
            self.install_btn.setEnabled(True)
            
            # Get package info
            info = self.package_handler.get_package_info(file_path)
            self.info_text.setText(info)
            
            self.log_output.append(f"📦 Selected package: {os.path.basename(file_path)}")
    
    def install_package(self):
        """Start package installation"""
        if not self.current_package:
            QMessageBox.warning(self, "No Package", "Please select a package first.")
            return
        
        # Confirm installation
        reply = QMessageBox.question(
            self,
            "Confirm Installation",
            f"Are you sure you want to install:\n{os.path.basename(self.current_package)}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Disable buttons during installation
        self.install_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.steps_label.setText("Starting installation...")
        
        # Start installation thread
        self.installer_thread = InstallerThread(self.current_package, self.package_handler)
        self.installer_thread.progress.connect(self.update_progress)
        self.installer_thread.status.connect(self.update_status)
        self.installer_thread.step.connect(self.update_step)
        self.installer_thread.finished.connect(self.installation_finished)
        self.installer_thread.start()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def update_status(self, message):
        """Update status label and log"""
        self.status_label.setText(message)
        self.log_output.append(f"💬 {message}")
    
    def update_step(self, step_message):
        """Update installation step display"""
        self.steps_label.setText(step_message)
        self.log_output.append(step_message)
    
    def installation_finished(self, success, message):
        """Handle installation completion"""
        self.browse_btn.setEnabled(True)
        
        if success:
            # Show success notification
            self.tray_icon.showMessage(
                "Installation Successful",
                f"Package installed successfully!",
                QSystemTrayIcon.Information,
                3000
            )
            QMessageBox.information(self, "Success", message)
            self.logger.log_installation(self.current_package, True, message)
            self.load_history()
            self.clear_selection()
        else:
            # Show failure notification
            self.tray_icon.showMessage(
                "Installation Failed",
                f"Installation failed. Check the log for details.",
                QSystemTrayIcon.Critical,
                3000
            )
            QMessageBox.critical(self, "Installation Failed", message)
            self.logger.log_installation(self.current_package, False, message)
            self.install_btn.setEnabled(True)
        
        self.log_output.append(f"\n{'='*50}\n")
    
    def clear_selection(self):
        """Clear current package selection"""
        self.current_package = None
        self.path_label.setText("No package selected")
        self.info_text.setText("Select a package to see details...")
        self.install_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready to install")
        self.steps_label.setText("Ready to install")
        self.log_output.clear()
    
    def load_history(self):
        """Load installation history with icons"""
        self.history_list.clear()
        history = self.logger.get_history()
        
        if not history:
            self.history_list.addItem("No installation history")
            return
        
        for entry in reversed(history[-50:]):  # Show last 50 entries
            success = entry.get('success', False)
            package_name = os.path.basename(entry.get('package', 'Unknown'))
            timestamp = entry.get('timestamp', '')
            
            # Create item with icon
            if success:
                item_text = f"✅ {package_name} - {timestamp}"
            else:
                item_text = f"❌ {package_name} - {timestamp}"
            
            item = QListWidgetItem(item_text)
            if success:
                item.setToolTip(f"Successfully installed: {package_name}")
            else:
                item.setToolTip(f"Failed to install: {package_name}")
            
            self.history_list.addItem(item)
    
    def clear_history(self):
        """Clear installation history"""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear the installation history?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.logger.clear_history()
            self.load_history()
            QMessageBox.information(self, "Success", "History cleared successfully!")
    
    def change_theme(self, theme):
        """Change application theme"""
        self.current_theme = theme
        self.apply_theme(theme)
        self.save_settings()
    
    def apply_theme(self, theme="Light"):
        """Apply the application theme"""
        if theme == "Dark":
            # Dark Theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                }
                QWidget {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #444444;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #e0e0e0;
                }
                QTabWidget::pane {
                    border: 2px solid #444444;
                    border-radius: 5px;
                    background-color: #2d2d2d;
                }
                QTabBar::tab {
                    background-color: #3d3d3d;
                    color: #e0e0e0;
                    padding: 10px 20px;
                    margin-right: 2px;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                }
                QTabBar::tab:selected {
                    background-color: #2d2d2d;
                    border-bottom: 2px solid #3498db;
                }
                QTextEdit {
                    background-color: #252525;
                    color: #e0e0e0;
                    border: 1px solid #444444;
                    border-radius: 5px;
                }
                QListWidget {
                    background-color: #252525;
                    color: #e0e0e0;
                    border: 2px solid #444444;
                    border-radius: 5px;
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #3d3d3d;
                }
                QListWidget::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QComboBox {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #444444;
                    border-radius: 5px;
                    padding: 5px;
                }
                QComboBox:hover {
                    border: 1px solid #3498db;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    selection-background-color: #3498db;
                }
                QProgressBar {
                    border: 2px solid #444444;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    background-color: #252525;
                    color: #e0e0e0;
                }
                QProgressBar::chunk {
                    background-color: #27ae60;
                    border-radius: 3px;
                }
                QStatusBar {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                }
            """)
            
            # Update dynamic elements for dark theme
            self.path_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    border: 2px dashed #3498db;
                    border-radius: 5px;
                    background-color: #252525;
                    color: #e0e0e0;
                }
            """)
        else:
            # Light Theme  
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f6fa;
                    color: #2c3e50;
                }
                QWidget {
                    background-color: #f5f6fa;
                    color: #2c3e50;
                }
                QLabel {
                    color: #2c3e50;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                    background-color: white;
                    color: #2c3e50;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #2c3e50;
                }
                QTabWidget::pane {
                    border: 2px solid #bdc3c7;
                    border-radius: 5px;
                    background-color: white;
                }
                QTabBar::tab {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    padding: 10px 20px;
                    margin-right: 2px;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 2px solid #3498db;
                }
                QTextEdit {
                    background-color: white;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                }
                QListWidget {
                    background-color: white;
                    color: #2c3e50;
                    border: 2px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #ecf0f1;
                }
                QListWidget::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QComboBox {
                    background-color: white;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 5px;
                }
                QComboBox:hover {
                    border: 1px solid #3498db;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #2c3e50;
                    selection-background-color: #3498db;
                }
                QProgressBar {
                    border: 2px solid #bdc3c7;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    background-color: white;
                    color: #2c3e50;
                }
                QProgressBar::chunk {
                    background-color: #27ae60;
                    border-radius: 3px;
                }
                QStatusBar {
                    background-color: white;
                    color: #2c3e50;
                }
            """)
            
            # Update dynamic elements for light theme
            self.path_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    border: 2px dashed #3498db;
                    border-radius: 5px;
                    background-color: #ecf0f1;
                    color: #2c3e50;
                }
            """)
    
    def load_settings(self):
        """Load application settings"""
        try:
            settings_dir = os.path.join(os.path.expanduser("~"), ".snapwiz")
            settings_file = os.path.join(settings_dir, "settings.json")
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get('theme', 'Light')
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.current_theme = "Light"
    
    def save_settings(self):
        """Save application settings"""
        try:
            settings_dir = os.path.join(os.path.expanduser("~"), ".snapwiz")
            os.makedirs(settings_dir, exist_ok=True)
            settings_file = os.path.join(settings_dir, "settings.json")
            
            settings = {
                'theme': self.current_theme
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application info
    app.setApplicationName("SnapWiz")
    app.setOrganizationName("SnapWiz")
    
    # Prevent app from quitting when window closes (for system tray)
    app.setQuitOnLastWindowClosed(False)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
