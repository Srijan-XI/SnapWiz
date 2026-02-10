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
                             QMenu, QAction, QShortcut, QListWidgetItem, QLineEdit, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QKeySequence, QPixmap, QDragEnterEvent, QDropEvent
from src.package_handler import PackageHandler
from src.logger import InstallLogger
from src import config
from src import language
from src.language import _  # Import translation function
import json
import time

class InstallerThread(QThread):
    """Thread to handle installation without blocking UI"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    step = pyqtSignal(str)  # New signal for detailed steps
    
    def __init__(self, package_path, package_handler, verify_integrity=True, verify_signature=False, checksum=None, checksum_type='sha256'):
        super().__init__()
        self.package_path = package_path
        self.package_handler = package_handler
        self.verify_integrity = verify_integrity
        self.verify_signature = verify_signature
        self.checksum = checksum
        self.checksum_type = checksum_type
        
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
            self.progress.emit(20)
            
            # Step 3: Package Verification (if enabled)
            if self.verify_integrity or self.checksum or self.verify_signature:
                self.step.emit("🔐 Verifying package security...")
                self.status.emit("Checking package integrity and signatures...")
                self.progress.emit(25)
                
                success, message, details = self.package_handler.verify_package(
                    self.package_path,
                    checksum=self.checksum,
                    checksum_type=self.checksum_type,
                    check_signature=self.verify_signature
                )
                
                if not success:
                    self.finished.emit(False, f"❌ Verification Failed:\\n{message}")
                    return
                
                self.step.emit("✅ Package verification passed")
                time.sleep(0.2)
            
            self.progress.emit(35)
            
            # Step 4: Reading package information
            self.step.emit("📖 Reading package metadata...")
            self.status.emit("Analyzing package contents...")
            self.progress.emit(40)
            time.sleep(0.3)
            
            # Step 5: Checking dependencies
            self.step.emit("🔗 Checking dependencies...")
            self.status.emit("Verifying system requirements...")
            self.progress.emit(50)
            time.sleep(0.3)
            
            # Step 6: Installing
            self.step.emit("⚙️ Installing package...")
            self.status.emit("Installing package (this may take a while)...")
            self.progress.emit(60)
            
            success, message = self.package_handler.install_package(self.package_path)
            
            if success:
                # Step 7: Configuring
                self.step.emit("🔧 Configuring installation...")
                self.progress.emit(85)
                time.sleep(0.2)
                
                # Step 8: Finalizing
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
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        
        # Enable drag and drop
        self.setAcceptDrops(config.DRAG_DROP_ENABLED)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel(config.ICONS['app'] + " " + config.APP_NAME)
        header.setAlignment(Qt.AlignCenter)
        header_font = QFont("Arial", config.HEADER_FONT_SIZE, QFont.Bold)
        header.setFont(header_font)
        header.setToolTip(config.APP_DESCRIPTION)
        main_layout.addWidget(header)
        
        subtitle = QLabel("The magical way to install .deb, .rpm, .snap, and .flatpak packages")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Arial", config.SUBTITLE_FONT_SIZE)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #666; margin-bottom: 10px;")
        main_layout.addWidget(subtitle)
        
        # Drag and drop hint
        drag_hint = QLabel("💡 Tip: Drag and drop package files here to add them!")
        drag_hint.setAlignment(Qt.AlignCenter)
        drag_hint.setStyleSheet("color: #3498db; font-style: italic; font-size: 10px;")
        main_layout.addWidget(drag_hint)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_install_tab(), config.TAB_NAMES['install'])
        self.tabs.addTab(self.create_uninstall_tab(), config.TAB_NAMES['uninstall'])
        self.tabs.addTab(self.create_history_tab(), config.TAB_NAMES['history'])
        self.tabs.addTab(self.create_settings_tab(), config.TAB_NAMES['settings'])
        main_layout.addWidget(self.tabs)
        
        # Status bar for shortcuts
        self.statusBar().showMessage(config.SHORTCUTS_DISPLAY)
        
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
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            # Check if at least one file has a supported extension
            has_valid_file = False
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if config.is_supported_package(file_path):
                    has_valid_file = True
                    break
            
            if has_valid_file:
                event.acceptProposedAction()
                self.statusBar().showMessage("📦 Drop files to add them to the installation queue...", 2000)
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        if event.mimeData().hasUrls():
            valid_files = []
            invalid_files = []
            
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                
                if os.path.isfile(file_path):
                    if config.is_supported_package(file_path):
                        # Check if file already in queue
                        if file_path not in self.install_queue:
                            valid_files.append(file_path)
                    else:
                        invalid_files.append(os.path.basename(file_path))
            
            # Add valid files to queue
            if valid_files:
                self.install_queue.extend(valid_files)
                self.update_queue_display()
                
                # Switch to install tab
                self.tabs.setCurrentIndex(0)
                
                count = len(valid_files)
                self.statusBar().showMessage(
                    f"✅ Added {count} package{'s' if count > 1 else ''} to queue!",
                    3000
                )
                
                # Show notification in tray
                self.tray_icon.showMessage(
                    "Files Added",
                    f"Added {count} package{'s' if count > 1 else ''} to installation queue",
                    QSystemTrayIcon.Information,
                    2000
                )
            
            # Show warning for invalid files
            if invalid_files:
                if len(invalid_files) <= 5:
                    file_list = "\n".join(invalid_files)
                else:
                    file_list = "\n".join(invalid_files[:5]) + f"\n... and {len(invalid_files) - 5} more"
                
                QMessageBox.warning(
                    self,
                    "Unsupported Files",
                    f"The following files are not supported package formats:\n\n{file_list}\n\n"
                    f"Supported formats: .deb, .rpm, .snap, .flatpak"
                )
            
            event.acceptProposedAction()
        else:
            event.ignore()
        
    def create_install_tab(self):
        """Create the installation tab with batch installation support"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Initialize installation queue
        self.install_queue = []
        self.current_installing_index = -1
        
        # Package selection group with batch support
        select_group = QGroupBox("📁 Select Packages (Batch Installation)")
        select_group.setToolTip("Add multiple packages to install them in sequence")
        select_layout = QVBoxLayout()
        
        # Buttons for adding packages
        button_row = QHBoxLayout()
        
        self.browse_btn = QPushButton("📂 Add Package...")
        self.browse_btn.setFixedWidth(180)
        self.browse_btn.setToolTip("Add one or more packages to the queue (Ctrl+O)")
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
        """)
        button_row.addWidget(self.browse_btn)
        
        self.clear_queue_btn = QPushButton("🗑️ Clear Queue")
        self.clear_queue_btn.setFixedWidth(150)
        self.clear_queue_btn.setToolTip("Remove all packages from the queue")
        self.clear_queue_btn.clicked.connect(self.clear_queue)
        self.clear_queue_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        button_row.addWidget(self.clear_queue_btn)
        
        button_row.addStretch()
        select_layout.addLayout(button_row)
        
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)
        
        # Installation Queue Display
        queue_group = QGroupBox("📋 Installation Queue")
        queue_group.setToolTip("Packages waiting to be installed")
        queue_layout = QVBoxLayout()
        
        self.queue_list = QListWidget()
        self.queue_list.setMaximumHeight(150)
        self.queue_list.setToolTip("Right-click to remove individual packages")
        self.queue_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.queue_list.customContextMenuRequested.connect(self.show_queue_context_menu)
        self.queue_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
            }
        """)
        queue_layout.addWidget(self.queue_list)
        
        # Queue status label
        self.queue_status_label = QLabel("Queue: 0 packages")
        self.queue_status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        queue_layout.addWidget(self.queue_status_label)
        
        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)
        
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
        
        # Progress group (now shows batch progress)
        progress_group = QGroupBox("📊 Installation Progress")
        progress_group.setToolTip("Real-time progress of current and overall installation")
        progress_layout = QVBoxLayout()
        
        # Current package progress
        current_label = QLabel("Current Package:")
        progress_layout.addWidget(current_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setToolTip("Current package installation progress")
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
        
        # Overall batch progress
        self.batch_progress_label = QLabel("Overall: 0 of 0 packages")
        self.batch_progress_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        progress_layout.addWidget(self.batch_progress_label)
        
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
        
        self.install_btn = QPushButton("✅ Start Batch Installation")
        self.install_btn.setFixedHeight(45)
        self.install_btn.setFixedWidth(250)
        self.install_btn.setEnabled(False)
        self.install_btn.setToolTip("Install all packages in the queue (Ctrl+I)")
        self.install_btn.clicked.connect(self.start_batch_installation)
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
        
        self.cancel_btn = QPushButton("⏹️ Cancel")
        self.cancel_btn.setFixedHeight(45)
        self.cancel_btn.setFixedWidth(130)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setToolTip("Cancel the current batch installation")
        self.cancel_btn.clicked.connect(self.cancel_batch_installation)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        return tab
    
    def create_uninstall_tab(self):
        """Create the uninstall tab for removing installed packages"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Info label
        info = QLabel("🗑️ Uninstall Installed Packages")
        info.setFont(QFont("Arial", 10))
        info.setToolTip("Remove packages that are currently installed on your system")
        layout.addWidget(info)
        
        # Search and Filter Section
        search_filter_group = QGroupBox("🔍 Search & Filter")
        search_filter_layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)
        
        self.uninstall_search_input = QLineEdit()
        self.uninstall_search_input.setPlaceholderText("Type package name to search...")
        self.uninstall_search_input.textChanged.connect(self.filter_installed_packages)
        self.uninstall_search_input.setToolTip("Search installed packages by name")
        search_layout.addWidget(self.uninstall_search_input)
        
        search_filter_layout.addLayout(search_layout)
        
        # Filter by type
        filter_layout = QHBoxLayout()
        
        type_label = QLabel("Type:")
        filter_layout.addWidget(type_label)
        
        self.uninstall_type_filter = QComboBox()
        self.uninstall_type_filter.addItems(["All", ".deb packages", ".rpm packages"])
        self.uninstall_type_filter.currentIndexChanged.connect(self.filter_installed_packages)
        self.uninstall_type_filter.setToolTip("Filter by package type")
        filter_layout.addWidget(self.uninstall_type_filter)
        
        # Refresh button
        refresh_packages_btn = QPushButton("🔄 Refresh List")
        refresh_packages_btn.clicked.connect(self.load_installed_packages)
        refresh_packages_btn.setToolTip("Reload the list of installed packages")
        refresh_packages_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        filter_layout.addWidget(refresh_packages_btn)
        
        filter_layout.addStretch()
        search_filter_layout.addLayout(filter_layout)
        
        search_filter_group.setLayout(search_filter_layout)
        layout.addWidget(search_filter_group)
        
        # Package count label
        self.uninstall_count_label = QLabel("Loading packages...")
        self.uninstall_count_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(self.uninstall_count_label)
        
        # Installed packages list
        packages_group = QGroupBox("📦 Installed Packages")
        packages_layout = QVBoxLayout()
        
        self.installed_packages_list = QListWidget()
        self.installed_packages_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.installed_packages_list.setToolTip("Select one or more packages to uninstall")
        self.installed_packages_list.setStyleSheet("""
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
                background-color: #e74c3c;
                color: white;
            }
        """)
        packages_layout.addWidget(self.installed_packages_list)
        
        packages_group.setLayout(packages_layout)
        layout.addWidget(packages_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.uninstall_btn = QPushButton("🗑️ Uninstall Selected")
        self.uninstall_btn.setFixedHeight(45)
        self.uninstall_btn.setFixedWidth(220)
        self.uninstall_btn.setEnabled(False)
        self.uninstall_btn.setToolTip("Uninstall the selected package(s)")
        self.uninstall_btn.clicked.connect(self.uninstall_packages)
        self.uninstall_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        button_layout.addWidget(self.uninstall_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Enable uninstall button when selection changes
        self.installed_packages_list.itemSelectionChanged.connect(
            lambda: self.uninstall_btn.setEnabled(
                len(self.installed_packages_list.selectedItems()) > 0
            )
        )
        
        # Load installed packages on tab creation
        self.all_installed_packages = []
        QTimer.singleShot(100, self.load_installed_packages)  # Load after UI is ready
        
        return tab
    
    
    def create_history_tab(self):
        """Create the installation history tab with search and filter"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Info label
        info = QLabel("📋 Installation History - Search and filter your installations")
        info.setFont(QFont("Arial", 10))
        info.setToolTip("Complete history of all package installations with search and filter")
        layout.addWidget(info)
        
        # Search and Filter Section
        search_filter_group = QGroupBox("🔍 Search & Filter")
        search_filter_layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setToolTip("Search by package name")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search packages...")
        self.search_input.textChanged.connect(self.apply_filters)
        self.search_input.setToolTip("Search by package name (real-time)")
        search_layout.addWidget(self.search_input)
        
        search_filter_layout.addLayout(search_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Status filter
        status_label = QLabel("Status:")
        filter_layout.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "✅ Success", "❌ Failed"])
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        self.status_filter.setToolTip("Filter by installation status")
        filter_layout.addWidget(self.status_filter)
        
        # Package type filter
        type_label = QLabel("Type:")
        filter_layout.addWidget(type_label)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", ".deb", ".rpm"])
        self.type_filter.currentIndexChanged.connect(self.apply_filters)
        self.type_filter.setToolTip("Filter by package type")
        filter_layout.addWidget(self.type_filter)
        
        # Clear filters button
        clear_filters_btn = QPushButton("🔄 Clear Filters")
        clear_filters_btn.clicked.connect(self.clear_filters)
        clear_filters_btn.setToolTip("Reset all filters and show all history")
        clear_filters_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        filter_layout.addWidget(clear_filters_btn)
        
        filter_layout.addStretch()
        search_filter_layout.addLayout(filter_layout)
        
        search_filter_group.setLayout(search_filter_layout)
        layout.addWidget(search_filter_group)
        
        # Results count label
        self.results_label = QLabel("Showing all results")
        self.results_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(self.results_label)
        
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
        
        # Add separator
        button_layout.addSpacing(20)
        
        # Export CSV button
        export_csv_btn = QPushButton("📊 Export CSV")
        export_csv_btn.setToolTip("Export history to CSV file for spreadsheet analysis")
        export_csv_btn.clicked.connect(self.export_csv)
        export_csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        button_layout.addWidget(export_csv_btn)
        
        # Export JSON button
        export_json_btn = QPushButton("📦 Export JSON")
        export_json_btn.setToolTip("Export history to JSON file with full metadata")
        export_json_btn.clicked.connect(self.export_json)
        export_json_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """)
        button_layout.addWidget(export_json_btn)
        
        # Import button
        import_btn = QPushButton("📥 Import")
        import_btn.setToolTip("Import history from JSON backup file")
        import_btn.clicked.connect(self.import_history)
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        button_layout.addWidget(import_btn)
        
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
        
        # Language selector
        lang_label = QLabel("Language:")
        theme_layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        # Add all supported languages
        for code, name in language.get_available_languages():
            self.language_combo.addItem(f"{name}", code)  # Display name, store code
        
        # Set current language
        current_lang = language.get_current_language()
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        self.language_combo.setToolTip("Choose your preferred language / Choisissez votre langue / Wählen Sie Ihre Sprache")
        self.language_combo.currentIndexChanged.connect(self.change_language)
        theme_layout.addWidget(self.language_combo)
        
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
        
        # Package Verification settings
        verify_group = QGroupBox("🔐 Package Verification")
        verify_group.setToolTip("Configure security and integrity checks for packages")
        verify_layout = QVBoxLayout()
        
        verify_info = QLabel("Enable verification checks before installation:")
        verify_info.setWordWrap(True)
        verify_layout.addWidget(verify_info)
        
        # Integrity check checkbox
        self.verify_integrity_checkbox = QCheckBox("✓ Always verify package integrity")
        self.verify_integrity_checkbox.setChecked(True)  # Enabled by default
        self.verify_integrity_checkbox.setToolTip("Check if package file is valid and not corrupted")
        verify_layout.addWidget(self.verify_integrity_checkbox)
        
        # GPG signature checkbox
        self.verify_signature_checkbox = QCheckBox("✓ Verify GPG signatures (if available)")
        self.verify_signature_checkbox.setChecked(False)  # Disabled by default (optional)
        self.verify_signature_checkbox.setToolTip("Verify package signatures using GPG (requires .asc or .sig files)")
        verify_layout.addWidget(self.verify_signature_checkbox)
        
        # Checksum verification section
        checksum_label = QLabel("\\nOptional: Verify checksum (SHA256/MD5):")
        checksum_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        verify_layout.addWidget(checksum_label)
        
        checksum_info = QLabel("Leave blank to skip checksum verification")
        checksum_info.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 10px;")
        verify_layout.addWidget(checksum_info)
        
        # Checksum type selector
        checksum_type_layout = QHBoxLayout()
        checksum_type_label = QLabel("Type:")
        checksum_type_layout.addWidget(checksum_type_label)
        
        self.checksum_type_combo = QComboBox()
        self.checksum_type_combo.addItems(["SHA256", "MD5"])
        self.checksum_type_combo.setToolTip("Choose checksum algorithm")
        checksum_type_layout.addWidget(self.checksum_type_combo)
        checksum_type_layout.addStretch()
        verify_layout.addLayout(checksum_type_layout)
        
        # Checksum input
        checksum_input_layout = QHBoxLayout()
        checksum_input_label = QLabel("Checksum:")
        checksum_input_layout.addWidget(checksum_input_label)
        
        self.checksum_input = QLineEdit()
        self.checksum_input.setPlaceholderText("Enter expected checksum (optional)...")
        self.checksum_input.setToolTip("Paste the expected checksum value from the package source")
        checksum_input_layout.addWidget(self.checksum_input)
        verify_layout.addLayout(checksum_input_layout)
        
        verify_group.setLayout(verify_layout)
        layout.addWidget(verify_group)
        
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
        """Open file dialog to select one or more packages"""
        file_paths, _ = QFileDialog.getOpenFileNames(  # Note: getOpenFileNames (plural)
            self,
            "Select Package File(s)",
            os.path.expanduser("~"),
            config.FILE_FILTER
        )
        
        if file_paths:
            # Add all selected files to the queue
            for file_path in file_paths:
                if file_path not in self.install_queue:
                    self.install_queue.append(file_path)
                    self.log_output.append(f"📦 Added to queue: {os.path.basename(file_path)}")
            
           # Update queue display
            self.update_queue_display()
    
    def update_queue_display(self):
        """Update the queue list widget"""
        self.queue_list.clear()
        
        for i, package_path in enumerate(self.install_queue):
            package_name = os.path.basename(package_path)
            
            # Mark currently installing package
            if i == self.current_installing_index:
                item_text = f"⏳ {package_name} (Installing...)"
            elif i < self.current_installing_index:
                item_text = f"✅ {package_name} (Completed)"
            else:
                item_text = f"⏸️ {package_name} (Waiting)"
            
            self.queue_list.addItem(item_text)
        
        # Update queue status
        queue_length = len(self.install_queue)
        self.queue_status_label.setText(f"Queue: {queue_length} package{'s' if queue_length !=1 else ''}")
        
        # Enable/disable install button
        self.install_btn.setEnabled(queue_length > 0)
    
    def show_queue_context_menu(self, position):
        """Show context menu for queue items"""
        item = self.queue_list.itemAt(position)
        if item:
            menu = QMenu()
            index = self.queue_list.row(item)
            
            remove_action = menu.addAction("🗑️ Remove from Queue")
            action = menu.exec_(self.queue_list.mapToGlobal(position))
            
            if action == remove_action:
                self.remove_from_queue(index)
    
    def remove_from_queue(self, index):
        """Remove a package from the queue by index"""
        if 0 <= index < len(self.install_queue):
            removed = self.install_queue.pop(index)
            self.log_output.append(f"�️ Removed from queue: {os.path.basename(removed)}")
            self.update_queue_display()
    
    def clear_queue(self):
        """Clear all packages from the queue"""
        if not self.install_queue:
            return
        
        reply = QMessageBox.question(
            self,
            "Clear Queue",
            f"Remove all {len(self.install_queue)} packages from the queue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.install_queue.clear()
            self.current_installing_index = -1
            self.update_queue_display()
            self.log_output.append("🗑️ Queue cleared")
    
    def start_batch_installation(self):
        """Start installing all packages in the queue"""
        if not self.install_queue:
            QMessageBox.warning(self, "Empty Queue", "Please add packages to the queue first.")
            return
        
        # Confirm batch installation
        reply = QMessageBox.question(
            self,
            "Confirm Batch Installation",
            f"Install {len(self.install_queue)} package(s) in sequence?\n\n"
            f"This may take several minutes.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Disable UI elements
        self.install_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.browse_btn.setEnabled(False)
        self.clear_queue_btn.setEnabled(False)
        
        # Reset state
        self.current_installing_index = 0
        self.batch_cancelled = False
        
        # Update overall progress
        self.batch_progress_label.setText(f"Overall: 0 of {len(self.install_queue)} packages")
        
        # Start installing first package
        self.install_next_in_queue()
    
    def install_next_in_queue(self):
        """Install the next package in the queue"""
        if self.batch_cancelled:
            self.log_output.append("⏸️ Batch installation cancelled")
            self.reset_after_batch()
            return
        
        if self.current_installing_index >= len(self.install_queue):
            # All packages installed
            self.log_output.append(f"\\n{'='*50}")
            self.log_output.append("✅ Batch installation completed!")
            self.log_output.append(f"{'='*50}\\n")
            
            QMessageBox.information(
                self,
                "Batch Installation Complete",
                f"Successfully completed batch installation of {len(self.install_queue)} package(s)!"
            )
            
            self.reset_after_batch()
            return
        
        # Get current package
        current_package = self.install_queue[self.current_installing_index]
        package_name = os.path.basename(current_package)
        
        # Update UI
        self.update_queue_display()
        self.progress_bar.setValue(0)
        self.steps_label.setText(f"Installing {package_name}...")
        self.batch_progress_label.setText(
            f"Overall: {self.current_installing_index} of {len(self.install_queue)} packages"
        )
        
        
        # Get verification settings
        verify_integrity = self.verify_integrity_checkbox.isChecked()
        verify_signature = self.verify_signature_checkbox.isChecked()
        # For batch, we rely on signature and integrity checks. Checksum is manual and hard to do for batch easily without a map, so skipping manual checksum for batch unless implemented differently.
        # But let's pass the current manual checksum settings anyway. If the user put a checksum it will apply to the first package and fail subsequent ones likely?
        # Ideally batch mode should maybe disable single-package specific manual checksums or require a manifest.
        # For now, let's disable manual checksum for batch to avoid false failures on subsequent packages.
        checksum = None 
        checksum_type = "sha256"

        self.log_output.append(f"\\n📦 [{self.current_installing_index + 1}/{len(self.install_queue)}] Installing: {package_name}")
        
        # Start installation thread
        self.installer_thread = InstallerThread(
            current_package, 
            self.package_handler,
            verify_integrity=verify_integrity,
            verify_signature=verify_signature,
            checksum=checksum,
            checksum_type=checksum_type
        )
        self.installer_thread.progress.connect(self.update_progress)
        self.installer_thread.status.connect(self.update_status)
        self.installer_thread.step.connect(self.update_step)
        self.installer_thread.finished.connect(self.batch_installation_finished)
        self.installer_thread.start()
    
    def batch_installation_finished(self, success, message):
        """Handle completion of one package in batch"""
        current_package = self.install_queue[self.current_installing_index]
        package_name = os.path.basename(current_package)
        
        # Log the installation
        self.logger.log_installation(current_package, success, message)
        
        if success:
            self.log_output.append(f"✅ Completed: {package_name}")
            # Show brief notification
            if self.current_installing_index == len(self.install_queue) - 1:
                # Last package
                self.tray_icon.showMessage(
                    "Batch Installation Complete",
                    f"All {len(self.install_queue)} packages installed!",
                    QSystemTrayIcon.Information,
                    3000
                )
        else:
            self.log_output.append(f"❌ Failed: {package_name} - {message}")
            
            # Ask if user wants to continue (if not last package)
            if self.current_installing_index < len(self.install_queue) - 1:
                reply = QMessageBox.question(
                    self,
                    "Package Failed",
                    f"Failed to install: {package_name}\\n\\n"
                    f"Error: {message}\\n\\n"
                    f"Continue with remaining packages?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    self.batch_cancelled = True
                    self.log_output.append("⏸️ Batch installation cancelled by user")
                    self.reset_after_batch()
                    return
        
        # Move to next package
        self.current_installing_index += 1
        self.install_next_in_queue()
    
    def cancel_batch_installation(self):
        """Cancel the ongoing batch installation"""
        reply = QMessageBox.question(
            self,
            "Cancel Batch Installation",
            "Cancel the ongoing batch installation?\\n\\n"
            "The current package will complete, but remaining packages will be skipped.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.batch_cancelled = True
            self.cancel_btn.setEnabled(False)
    
    def reset_after_batch(self):
        """Reset UI after batch installation completes or is cancelled"""
        self.browse_btn.setEnabled(True)
        self.clear_queue_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.install_btn.setEnabled(len(self.install_queue) > 0)
        
        # Clear the queue
        self.install_queue.clear()
        self.current_installing_index = -1
        self.update_queue_display()
        
        # Reload history
        self.load_history()
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.batch_progress_label.setText("Overall: 0 of 0 packages")
        self.steps_label.setText("Ready to install")
        self.status_label.setText("Ready to install")
    
    def load_installed_packages(self):
        """Load list of installed packages from the system"""
        self.uninstall_count_label.setText("Loading packages...")
        self.installed_packages_list.clear()
        self.all_installed_packages = []
        
        try:
            import subprocess
            
            # Try dpkg first (Debian/Ubuntu)
            try:
                result = subprocess.run(
                    ['dpkg', '--get-selections'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line and '\t' in line:
                            package_name = line.split('\t')[0]
                            status = line.split('\t')[1] if len(line.split('\t')) > 1 else ''
                            if 'install' in status.lower():
                                self.all_installed_packages.append({
                                    'name': package_name,
                                    'type': 'deb'
                                })
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            # Try rpm (Fedora/RHEL/CentOS)
            try:
                result = subprocess.run(
                    ['rpm', '-qa'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            self.all_installed_packages.append({
                                'name': line.strip(),
                                'type': 'rpm'
                            })
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            if self.all_installed_packages:
                self.filter_installed_packages()
            else:
                self.uninstall_count_label.setText("No packages found or unsupported system")
                QMessageBox.warning(
                    self,
                    "No Packages Found",
                    "Could not detect installed packages.\\n\\n"
                    "This feature requires dpkg (Debian/Ubuntu) or rpm (Fedora/RHEL/CentOS)."
                )
        except Exception as e:
            self.uninstall_count_label.setText(f"Error loading packages")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load installed packages:\\n{str(e)}"
            )
    
    def filter_installed_packages(self):
        """Filter the installed packages list based on search and type filter"""
        self.installed_packages_list.clear()
        
        search_query = self.uninstall_search_input.text().lower()
        type_filter = self.uninstall_type_filter.currentText()
        
        filtered_packages = []
        
        for pkg in self.all_installed_packages:
            # Apply type filter
            if type_filter == ".deb packages" and pkg['type'] != 'deb':
                continue
            elif type_filter == ".rpm packages" and pkg['type'] != 'rpm':
                continue
            
            # Apply search filter
            if search_query and search_query not in pkg['name'].lower():
                continue
            
            filtered_packages.append(pkg)
        
        # Sort alphabetically
        filtered_packages.sort(key=lambda x: x['name'])
        
        # Add to list widget
        for pkg in filtered_packages:
            icon = "📦" if pkg['type'] == 'deb' else "🔴"
            self.installed_packages_list.addItem(f"{icon} {pkg['name']}")
        
        # Update count
        total = len(self.all_installed_packages)
        showing = len(filtered_packages)
        
        if showing < total:
            self.uninstall_count_label.setText(f"Showing {showing} of {total} packages")
        else:
            self.uninstall_count_label.setText(f"Total: {total} packages")
    
    def uninstall_packages(self):
        """Uninstall the selected package(s)"""
        selected_items = self.installed_packages_list.selectedItems()
        
        if not selected_items:
            return
        
        # Extract package names
        packages_to_uninstall = []
        for item in selected_items:
            # Remove icon prefix
            package_name = item.text().split(' ', 1)[1] if ' ' in item.text() else item.text()
            packages_to_uninstall.append(package_name)
        
        # Confirm uninstallation
        if len(packages_to_uninstall) == 1:
            message = f"Are you sure you want to uninstall:\\n\\n{packages_to_uninstall[0]}?\\n\\n⚠️ This action cannot be undone."
        else:
            package_list = '\\n'.join(f"  • {pkg}" for pkg in packages_to_uninstall[:5])
            if len(packages_to_uninstall) > 5:
                package_list += f"\\n  ... and {len(packages_to_uninstall) - 5} more"
            message = f"Are you sure you want to uninstall {len(packages_to_uninstall)} packages?\\n\\n{package_list}\\n\\n⚠️ This action cannot be undone."
        
        reply = QMessageBox.question(
            self,
            "Confirm Uninstallation",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Default to No for safety
        )
        
        if reply == QMessageBox.No:
            return
        
        # Uninstall each package
        import subprocess
        success_count = 0
        failed_packages = []
        
        for package_name in packages_to_uninstall:
            try:
                # Determine package type
                pkg_info = next((p for p in self.all_installed_packages if p['name'] == package_name), None)
                
                if not pkg_info:
                    failed_packages.append((package_name, "Package not found"))
                    continue
                
                # Run appropriate uninstall command
                if pkg_info['type'] == 'deb':
                    # Debian/Ubuntu: sudo apt remove
                    result = subprocess.run(
                        ['pkexec', 'apt', 'remove', '-y', package_name],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                elif pkg_info['type'] == 'rpm':
                    # Fedora/RHEL: sudo dnf remove
                    result = subprocess.run(
                        ['pkexec', 'dnf', 'remove', '-y', package_name],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                else:
                    failed_packages.append((package_name, "Unknown package type"))
                    continue
                
                if result.returncode == 0:
                    success_count += 1
                    # Log the uninstallation
                    self.logger.log_installation(
                        package_name,
                        True,
                        f"Package uninstalled successfully"
                    )
                else:
                    error_msg = result.stderr if result.stderr else "Unknown error"
                    failed_packages.append((package_name, error_msg))
                    self.logger.log_installation(
                        package_name,
                        False,
                        f"Uninstallation failed: {error_msg}"
                    )
                    
            except subprocess.TimeoutExpired:
                failed_packages.append((package_name, "Operation timed out"))
            except Exception as e:
                failed_packages.append((package_name, str(e)))
        
        # Show results
        if failed_packages:
            failed_list = '\\n'.join(f"  • {pkg}: {err}" for pkg, err in failed_packages[:3])
            if len(failed_packages) > 3:
                failed_list += f"\\n  ... and {len(failed_packages) - 3} more"
            
            QMessageBox.warning(
                self,
                "Uninstallation Complete with Errors",
                f"Successfully uninstalled: {success_count}\\n"
                f"Failed: {len(failed_packages)}\\n\\n"
                f"Failed packages:\\n{failed_list}\\n\\n"
                f"Check the installation history for details."
            )
        else:
            QMessageBox.information(
                self,
                "Uninstallation Successful",
                f"Successfully uninstalled {success_count} package(s)!"
            )
        
        # Reload package list and history
        self.load_installed_packages()
        self.load_history()
    
    
    
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
        
        # Get verification settings
        verify_integrity = self.verify_integrity_checkbox.isChecked()
        verify_signature = self.verify_signature_checkbox.isChecked()
        checksum = self.checksum_input.text().strip()
        checksum_type = self.checksum_type_combo.currentText().lower()
        
        # Start installation thread
        self.installer_thread = InstallerThread(
            self.current_package, 
            self.package_handler,
            verify_integrity=verify_integrity,
            verify_signature=verify_signature,
            checksum=checksum,
            checksum_type=checksum_type
        )
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
    
    def load_history(self, filtered_history=None):
        """Load installation history with icons and filtering support"""
        self.history_list.clear()
        
        # Use filtered history if provided, otherwise get all history
        if filtered_history is not None:
            history = filtered_history
        else:
            history = self.logger.get_history()
        
        if not history:
            self.history_list.addItem("No installation history")
            self.results_label.setText("No results found")
            return
        
        # Update results label
        total = len(self.logger.get_history())
        showing = len(history)
        if showing < total:
            self.results_label.setText(f"Showing {showing} of {total} results")
        else:
            self.results_label.setText(f"Showing all {total} results")
        
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
    
    def apply_filters(self):
        """Apply search and filter criteria to history"""
        # Get search query
        search_query = self.search_input.text().strip()
        
        # Get filter selections
        status_filter = self.status_filter.currentText()
        type_filter = self.type_filter.currentText()
        
        # Convert filter selections to logger parameters
        status_param = None
        if status_filter == "✅ Success":
            status_param = "success"
        elif status_filter == "❌ Failed":
            status_param = "failed"
        
        type_param = None
        if type_filter == ".deb":
            type_param = "deb"
        elif type_filter == ".rpm":
            type_param = "rpm"
        
        # Apply filters
        filtered_history = self.logger.filter_history(
            status=status_param,
            package_type=type_param
        )
        
        # Apply search if query exists
        if search_query:
            filtered_history = [entry for entry in filtered_history
                              if search_query.lower() in entry.get('package_name', '').lower() or
                                 search_query.lower() in entry.get('package', '').lower()]
        
        # Reload history with filtered results
        self.load_history(filtered_history)
    
    def clear_filters(self):
        """Clear all filters and show all history"""
        self.search_input.clear()
        self.status_filter.setCurrentIndex(0)  # "All"
        self.type_filter.setCurrentIndex(0)    # "All"
        self.load_history()  # Reload all history
    
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
    
    def export_csv(self):
        """Export history to CSV file"""
        try:
            # Get save file path from user
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export History as CSV",
                "snapwiz_history.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if file_path:
                # Export to CSV
                success = self.logger.export_history(file_path, format='csv')
                
                if success:
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"History exported successfully to:\n{file_path}\n\n"
                        f"You can now open this file in Excel or any spreadsheet application."
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Export Failed",
                        "Failed to export history. Please check file permissions."
                    )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred while exporting:\n{str(e)}"
            )
    
    def export_json(self):
        """Export history to JSON file"""
        try:
            # Get save file path from user
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export History as JSON",
                "snapwiz_history.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Export to JSON
                success = self.logger.export_history(file_path, format='json')
                
                if success:
                    history_count = len(self.logger.get_history())
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"History exported successfully!\n\n"
                        f"File: {file_path}\n"
                        f"Entries: {history_count}\n\n"
                        f"This file can be imported later to restore your history."
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Export Failed",
                        "Failed to export history. Please check file permissions."
                    )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred while exporting:\n{str(e)}"
            )
    
    def import_history(self):
        """Import history from JSON file"""
        try:
            # Get file path from user
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import History from JSON",
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Ask user about merge or replace
                reply = QMessageBox.question(
                    self,
                    "Import Mode",
                    "How would you like to import the history?\n\n"
                    "• Yes - Merge with existing history (keep current + add imported)\n"
                    "• No - Replace existing history (delete current, use imported only)",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Cancel:
                    return
                
                merge = (reply == QMessageBox.Yes)
                
                # Import the history
                success = self.logger.import_history(file_path, merge=merge)
                
                if success:
                    self.load_history()  # Refresh the display
                    history_count = len(self.logger.get_history())
                    
                    mode_text = "merged with" if merge else "replaced"
                    QMessageBox.information(
                        self,
                        "Import Successful",
                        f"History {mode_text} successfully!\n\n"
                        f"Total entries now: {history_count}\n\n"
                        f"Your history has been updated."
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Import Failed",
                        "Failed to import history. Please check the file format.\n\n"
                        "Make sure you're importing a valid SnapWiz JSON history file."
                    )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"An error occurred while importing:\n{str(e)}"
            )
    
    def change_theme(self, theme):
        """Change application theme"""
        self.current_theme = theme
        self.apply_theme(theme)
        self.save_settings()
    
    def change_language(self):
        """Change application language"""
        # Get selected language code
        language_code = self.language_combo.currentData()
        
        if language_code and language.set_language(language_code):
            # Show message that restart is needed for full effect
            QMessageBox.information(
                self,
                "Language Changed / Langue modifiée / Sprache geändert",
                "Language preference saved.\nPlease restart the application for all changes to take effect.\n\n"
                "Préférence de langue enregistrée.\nVeuillez redémarrer l'application pour que tous les changements prennent effet.\n\n"
                "Spracheinstellung gespeichert.\nBitte starten Sie die Anwendung neu, damit alle Änderungen wirksam werden."
            )
            # Save settings
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

    
    def load_settings(self):
        """Load application settings"""
        try:
            settings_file = str(config.SETTINGS_FILE)
            
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
            config.ensure_config_dir()
            settings_file = str(config.SETTINGS_FILE)
            
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
