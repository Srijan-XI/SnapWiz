"""
Enhanced Package Handler with Better Error Handling
Example implementation showing integration of custom exceptions and retry logic
"""

import os
import sys
import subprocess
import platform

# Add parent directory to path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import config
from src.exceptions import (
    PackageNotFoundError,
    InvalidPackageError,
    UnsupportedPackageFormatError,
    PackageManagerNotFoundError,
    DependencyError,
    InstallationTimeoutError,
    InsufficientPrivilegesError,
    ServiceNotRunningError,
    get_error_icon,
    is_retryable_error
)
from src.retry_utils import (
    retry_on_failure,
    NETWORK_RETRY_CONFIG,
    INSTALLATION_RETRY_CONFIG,
    RetryConfig
)


class EnhancedPackageHandler:
    """
    Enhanced Package Handler with comprehensive error handling
    
    This is an example showing how to integrate the new error handling system.
    Merge these methods into the existing package_handler.py
    """
    
    def __init__(self):
        self.supported_formats = config.get_supported_extensions()
        self.package_manager = self.detect_package_manager()
        self.available_managers = self._detect_all_managers()
    
    # ==================== Validation with Better Errors ====================
    
    def validate_package(self, package_path):
        """
        Validate package file with specific error messages
        
        Args:
            package_path: Path to package file
            
        Returns:
            bool: True if valid
            
        Raises:
            PackageNotFoundError: File doesn't exist
            InvalidPackageError: File is corrupted or invalid
            UnsupportedPackageFormatError: Format not supported
        """
        # Check if file exists
        if not os.path.exists(package_path):
            raise PackageNotFoundError(package_path)
        
        # Check if it's a file (not directory)
        if not os.path.isfile(package_path):
            raise InvalidPackageError(
                package_path,
                reason="Path is a directory, not a file."
            )
        
        # Check file size (not empty)
        if os.path.getsize(package_path) == 0:
            raise InvalidPackageError(
                package_path,
                reason="File is empty (0 bytes)."
            )
        
        # Check extension
        _, ext = os.path.splitext(package_path)
        if ext.lower() not in self.supported_formats:
            raise UnsupportedPackageFormatError(
                package_path,
                detected_format=ext
            )
        
        # File appears valid
        return True
    
    # ==================== Installation with Retry Logic ====================
    
    @retry_on_failure(
        config=INSTALLATION_RETRY_CONFIG,
        on_retry_callback=lambda attempt, exc, delay: print(
            f"⚠️ Installation attempt {attempt} failed: {exc}\n"
            f"🔄 Retrying in {delay:.1f} seconds..."
        )
    )
    def install_package_with_retry(self, package_path, callback=None):
        """
        Install package with automatic retry on failure
        
        Args:
            package_path: Path to package file
            callback: Progress callback function
            
        Returns:
            tuple: (success: bool, message: str)
            
        Raises:
            Various specific exceptions based on failure type
        """
        # Validate first
        self.validate_package(package_path)
        
        # Get package type
        package_type = self.get_package_type(package_path)
        
        # Check if we have the right package manager
        format_info = config.get_package_format_by_extension(f".{package_type}")
        required_managers = format_info.get('managers', [])
        
        has_manager = any(
            mgr in self.available_managers
            for mgr in required_managers
        )
        
        if not has_manager:
            raise PackageManagerNotFoundError(
                package_type,
                required_managers[0] if required_managers else 'unknown'
            )
        
        # Route to appropriate installer
        if package_type == 'deb':
            return self._install_deb_enhanced(package_path, callback)
        elif package_type == 'rpm':
            return self._install_rpm_enhanced(package_path, callback)
        elif package_type == 'snap':
            return self._install_snap_enhanced(package_path, callback)
        elif package_type == 'flatpak':
            return self._install_flatpak_enhanced(package_path, callback)
        else:
            raise UnsupportedPackageFormatError(package_path, package_type)
    
    # ==================== Format-Specific Installers ====================
    
    def _install_snap_enhanced(self, package_path, callback=None):
        """Install .snap with better error handling"""
        # Check if snapd is running
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'snapd'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise ServiceNotRunningError('snapd', 'snap')
        except subprocess.TimeoutExpired:
            raise ServiceNotRunningError('snapd', 'snap')
        except FileNotFoundError:
            # systemctl not available, try installing anyway
            pass
        
        # Attempt installation
        try:
            cmd = ['pkexec', 'snap', 'install', '--dangerous', package_path]
            
            if callback:
                callback(50, "Installing snap package...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config.INSTALLATION_TIMEOUT
            )
            
            if result.returncode == 0:
                if callback:
                    callback(100, "Installation complete!")
                return True, "Snap package installed successfully!"
            else:
                # Parse error message
                error_msg = result.stderr or result.stdout
                if 'permission denied' in error_msg.lower():
                    raise InsufficientPrivilegesError('snap installation')
                else:
                    raise InvalidPackageError(
                        package_path,
                        reason=f"Installation failed: {error_msg}"
                    )
        
        except subprocess.TimeoutExpired:
            raise InstallationTimeoutError(
                os.path.basename(package_path),
                config.INSTALLATION_TIMEOUT
            )
    
    def _install_deb_enhanced(self, package_path, callback=None):
        """Install .deb with better error handling"""
        try:
            cmd = ['pkexec', 'apt', 'install', '-y', '-f', package_path]
            
            if callback:
                callback(50, "Installing Debian package...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config.INSTALLATION_TIMEOUT
            )
            
            if result.returncode == 0:
                if callback:
                    callback(100, "Installation complete!")
                return True, "Debian package installed successfully!"
            else:
                error_output = result.stderr or result.stdout
                
                # Check for specific errors
                if 'unmet dependencies' in error_output.lower():
                    # Try to extract dependency names
                    raise DependencyError(
                        os.path.basename(package_path),
                        missing_dependencies=self._parse_dependencies(error_output)
                    )
                elif 'permission denied' in error_output.lower():
                    raise InsufficientPrivilegesError('apt installation')
                else:
                    raise InvalidPackageError(
                        package_path,
                        reason=f"Installation failed: {error_output[:200]}"
                    )
        
        except subprocess.TimeoutExpired:
            raise InstallationTimeoutError(
                os.path.basename(package_path),
                config.INSTALLATION_TIMEOUT
            )
    
    # ==================== Helper Methods ====================
    
    def _parse_dependencies(self, error_output):
        """Parse missing dependencies from error output"""
        # Simple parser - can be enhanced
        dependencies = []
        lines = error_output.split('\n')
        for line in lines:
            if 'depends' in line.lower():
                # Extract package name
                parts = line.split()
                if len(parts) > 1:
                    dependencies.append(parts[1])
        return dependencies if dependencies else None
    
    def detect_package_manager(self):
        """Detect system package manager"""
        # Same as before, but could raise ConfigurationError if none found
        if self._command_exists('apt'):
            return 'apt'
        elif self._command_exists('dnf'):
            return 'dnf'
        elif self._command_exists('yum'):
            return 'yum'
        elif self._command_exists('zypper'):
            return 'zypper'
        else:
            return 'unknown'
    
    def _command_exists(self, command):
        """Check if command exists"""
        try:
            subprocess.run(
                ['which', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _detect_all_managers(self):
        """Detect all available package managers"""
        managers = {}
        
        # Check each manager type
        for manager in ['apt', 'dnf', 'yum', 'zypper', 'snap', 'flatpak']:
            if self._command_exists(manager):
                managers[manager] = True
        
        return managers
    
    def get_package_type(self, package_path):
        """Get package type from extension"""
        _, ext = os.path.splitext(package_path)
        ext = ext.lower()
        
        type_map = {
            '.deb': 'deb',
            '.rpm': 'rpm',
            '.snap': 'snap',
            '.flatpak': 'flatpak'
        }
        
        return type_map.get(ext, 'unknown')


# ==================== Error Handler for UI ====================

def handle_package_error(error, show_dialog_func=None):
    """
    Handle package errors with user-friendly messages
    
    Args:
        error: The exception that occurred
        show_dialog_func: Function to show error dialog to user
                         Should accept (title, message, icon)
    
    Returns:
        dict: Error information for logging/display
    """
    from exceptions import get_error_category, get_error_icon, SnapWizError
    
    # Get error details
    category = get_error_category(error)
    icon = get_error_icon(error)
    
    if isinstance(error, SnapWizError):
        message = error.get_full_message()
    else:
        message = str(error)
    
    # Create error info
    error_info = {
        'category': category,
        'icon': icon,
        'message': message,
        'exception_type': type(error).__name__,
        'retryable': is_retryable_error(error) if hasattr(error, '__class__') else False
    }
    
    # Show dialog if function provided
    if show_dialog_func:
        title = f"{icon} {category}"
        show_dialog_func(title, message, icon)
    
    return error_info


# ==================== Usage Example ====================

def example_usage():
    """Example of how to use the enhanced error handling"""
    
    handler = EnhancedPackageHandler()
    package_file = "/path/to/package.deb"
    
    try:
        # This will auto-retry on timeout/network errors
        success, message = handler.install_package_with_retry(
            package_file,
            callback=lambda progress, status: print(f"{progress}%: {status}")
        )
        
        print(f"✅ {message}")
    
    except PackageNotFoundError as e:
        print(f"❌ Package not found")
        print(e.get_full_message())
    
    except InvalidPackageError as e:
        print(f"❌ Invalid package")
        print(e.get_full_message())
    
    except PackageManagerNotFoundError as e:
        print(f"❌ Package manager missing")
        print(e.get_full_message())
    
    except DependencyError as e:
        print(f"❌ Dependency issues")
        print(e.get_full_message())
        if e.missing_dependencies:
            print(f"Missing: {', '.join(e.missing_dependencies)}")
    
    except InstallationTimeoutError as e:
        print(f"❌ Installation timed out")
        print(e.get_full_message())
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    example_usage()
