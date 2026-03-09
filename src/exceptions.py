"""
Custom Exception Classes for SnapWiz
Provides specific error types for better error handling and user feedback
"""

class SnapWizError(Exception):
    """Base exception for all SnapWiz errors"""
    def __init__(self, message, details=None, suggestion=None):
        self.message = message
        self.details = details
        self.suggestion = suggestion
        super().__init__(self.message)
    
    def get_full_message(self):
        """Get full error message with details and suggestion"""
        msg = self.message
        if self.details:
            msg += f"\n\nDetails: {self.details}"
        if self.suggestion:
            msg += f"\n\nSuggestion: {self.suggestion}"
        return msg


# ==================== Package-Related Errors ====================

class PackageError(SnapWizError):
    """Base class for package-related errors"""
    pass


class PackageNotFoundError(PackageError):
    """Package file not found"""
    def __init__(self, package_path):
        super().__init__(
            message=f"Package file not found: {package_path}",
            details="The specified package file does not exist or is not accessible.",
            suggestion="Check the file path and ensure the file exists."
        )
        self.package_path = package_path


class InvalidPackageError(PackageError):
    """Invalid or corrupted package file"""
    def __init__(self, package_path, reason=None):
        details = reason if reason else "The package file appears to be invalid or corrupted."
        super().__init__(
            message=f"Invalid package: {package_path}",
            details=details,
            suggestion="Try redownloading the package file from a trusted source."
        )
        self.package_path = package_path


class UnsupportedPackageFormatError(PackageError):
    """Package format not supported"""
    def __init__(self, package_path, detected_format=None):
        supported = ".deb, .rpm, .snap, .flatpak"
        details = f"Detected format: {detected_format}" if detected_format else "Unknown format"
        super().__init__(
            message=f"Unsupported package format: {package_path}",
            details=f"{details}. Supported formats: {supported}",
            suggestion=f"Ensure the file is one of: {supported}"
        )
        self.package_path = package_path
        self.detected_format = detected_format


class PackageVerificationError(PackageError):
    """Package verification failed (checksum, signature, etc.)"""
    def __init__(self, package_path, verification_type, expected=None, actual=None):
        details = f"{verification_type} verification failed."
        if expected and actual:
            details += f"\nExpected: {expected}\nActual: {actual}"
        super().__init__(
            message=f"Package verification failed: {package_path}",
            details=details,
            suggestion="The package may be corrupted or tampered with. Download it again from a trusted source."
        )
        self.package_path = package_path
        self.verification_type = verification_type


# ==================== Installation Errors ====================

class InstallationError(SnapWizError):
    """Base class for installation-related errors"""
    pass


class PackageManagerNotFoundError(InstallationError):
    """Required package manager not found"""
    def __init__(self, package_type, required_manager):
        install_cmd = {
            'deb': 'sudo apt install apt',
            'rpm': 'sudo dnf install dnf',
            'snap': 'sudo apt install snapd',
            'flatpak': 'sudo apt install flatpak'
        }.get(package_type, 'N/A')
        
        super().__init__(
            message=f"Package manager '{required_manager}' not found",
            details=f"Required to install {package_type} packages.",
            suggestion=f"Install it using: {install_cmd}"
        )
        self.package_type = package_type
        self.required_manager = required_manager


class DependencyError(InstallationError):
    """Package dependency issues"""
    def __init__(self, package_name, missing_dependencies=None):
        details = "Package has unresolved dependencies."
        if missing_dependencies:
            details += f"\nMissing: {', '.join(missing_dependencies)}"
        super().__init__(
            message=f"Dependency error for package: {package_name}",
            details=details,
            suggestion="Install missing dependencies manually or use the system package manager to resolve them."
        )
        self.package_name = package_name
        self.missing_dependencies = missing_dependencies


class InstallationTimeoutError(InstallationError):
    """Installation timed out"""
    def __init__(self, package_name, timeout_seconds):
        super().__init__(
            message=f"Installation timed out: {package_name}",
            details=f"Installation exceeded {timeout_seconds} seconds.",
            suggestion="The package may be very large, or there may be network issues. Try again with a better connection."
        )
        self.package_name = package_name
        self.timeout_seconds = timeout_seconds


class InstallationCancelledError(InstallationError):
    """Installation was cancelled by user"""
    def __init__(self, package_name):
        super().__init__(
            message=f"Installation cancelled: {package_name}",
            details="The installation was cancelled by the user.",
            suggestion=None
        )
        self.package_name = package_name


# ==================== Permission Errors ====================

class PermissionError(SnapWizError):
    """Permission-related errors"""
    pass


class InsufficientPrivilegesError(PermissionError):
    """User lacks required privileges"""
    def __init__(self, operation):
        super().__init__(
            message=f"Insufficient privileges for: {operation}",
            details="Administrator/root privileges are required.",
            suggestion="Ensure you enter the correct password when prompted, or run with sudo/pkexec."
        )
        self.operation = operation


# ==================== Network Errors ====================

class NetworkError(SnapWizError):
    """Base class for network-related errors"""
    pass


class DownloadError(NetworkError):
    """Failed to download required files"""
    def __init__(self, url, reason=None):
        details = reason if reason else "Download failed for unknown reason."
        super().__init__(
            message=f"Download failed: {url}",
            details=details,
            suggestion="Check your internet connection and try again."
        )
        self.url = url


class NetworkTimeoutError(NetworkError):
    """Network operation timed out"""
    def __init__(self, operation, timeout_seconds):
        super().__init__(
            message=f"Network timeout: {operation}",
            details=f"Operation timed out after {timeout_seconds} seconds.",
            suggestion="Check your internet connection and try again. The server may be slow or unreachable."
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds


# ==================== System Errors ====================

class SystemError(SnapWizError):
    """Base class for system-related errors"""
    pass


class ServiceNotRunningError(SystemError):
    """Required system service not running"""
    def __init__(self, service_name, package_type=None):
        start_cmd = f"sudo systemctl start {service_name}"
        enable_cmd = f"sudo systemctl enable {service_name}"
        
        details = f"The {service_name} service is not running."
        if package_type:
            details += f" It is required for {package_type} packages."
        
        super().__init__(
            message=f"Service not running: {service_name}",
            details=details,
            suggestion=f"Start the service:\n{start_cmd}\n\nEnable on boot:\n{enable_cmd}"
        )
        self.service_name = service_name


class DiskSpaceError(SystemError):
    """Insufficient disk space"""
    def __init__(self, required_mb, available_mb):
        super().__init__(
            message="Insufficient disk space",
            details=f"Required: {required_mb} MB, Available: {available_mb} MB",
            suggestion="Free up disk space and try again."
        )
        self.required_mb = required_mb
        self.available_mb = available_mb


# ==================== Configuration Errors ====================

class ConfigurationError(SnapWizError):
    """Configuration-related errors"""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Invalid configuration value"""
    def __init__(self, config_key, invalid_value, expected_type=None):
        details = f"Invalid value for '{config_key}': {invalid_value}"
        if expected_type:
            details += f"\nExpected type: {expected_type}"
        super().__init__(
            message=f"Invalid configuration: {config_key}",
            details=details,
            suggestion="Check config.py and ensure all values are correct."
        )
        self.config_key = config_key
        self.invalid_value = invalid_value


# ==================== Translation/Language Errors ====================

class LanguageError(SnapWizError):
    """Language/translation errors"""
    pass


class UnsupportedLanguageError(LanguageError):
    """Requested language not supported"""
    def __init__(self, language_code, supported_languages):
        super().__init__(
            message=f"Unsupported language: {language_code}",
            details=f"Supported languages: {', '.join(supported_languages)}",
            suggestion="Choose one of the supported languages from the Settings tab."
        )
        self.language_code = language_code
        self.supported_languages = supported_languages


class TranslationNotFoundError(LanguageError):
    """Translation file not found"""
    def __init__(self, language_code, file_path):
        super().__init__(
            message=f"Translation not found: {language_code}",
            details=f"Missing translation file: {file_path}",
            suggestion="Run: python compile_translations.py"
        )
        self.language_code = language_code
        self.file_path = file_path


# ==================== Helper Functions ====================

def get_error_category(error):
    """Get the category of an error"""
    if isinstance(error, PackageError):
        return "Package Error"
    elif isinstance(error, InstallationError):
        return "Installation Error"
    elif isinstance(error, PermissionError):
        return "Permission Error"
    elif isinstance(error, NetworkError):
        return "Network Error"
    elif isinstance(error, SystemError):
        return "System Error"
    elif isinstance(error, ConfigurationError):
        return "Configuration Error"
    elif isinstance(error, LanguageError):
        return "Language Error"
    elif isinstance(error, SnapWizError):
        return "SnapWiz Error"
    else:
        return "Unknown Error"


def is_retryable_error(error):
    """Check if an error is retryable"""
    retryable_types = (
        NetworkTimeoutError,
        DownloadError,
        InstallationTimeoutError
    )
    return isinstance(error, retryable_types)


def get_error_icon(error):
    """Get emoji icon for error type"""
    if isinstance(error, NetworkError):
        return "🌐"
    elif isinstance(error, PermissionError):
        return "🔐"
    elif isinstance(error, PackageError):
        return "📦"
    elif isinstance(error, InstallationError):
        return "⚙️"
    elif isinstance(error, SystemError):
        return "💻"
    elif isinstance(error, ConfigurationError):
        return "⚙️"
    elif isinstance(error, LanguageError):
        return "🌍"
    else:
        return "❌"
