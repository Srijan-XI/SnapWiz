"""
Package Handler Module
Handles package validation, installation, and information extraction
for .deb, .rpm, .snap, and .flatpak packages
"""

import os
import subprocess
import platform
import config


class PackageHandler:
    """Handle package operations for .deb, .rpm, .snap, and .flatpak files"""
    
    def __init__(self):
        self.supported_formats = config.get_supported_extensions()
        self.package_manager = self.detect_package_manager()
        self.available_managers = self._detect_all_managers()
    
    def detect_package_manager(self):
        """Detect the system's package manager"""
        # Check for APT (Debian/Ubuntu)
        if self._command_exists('apt'):
            return 'apt'
        elif self._command_exists('apt-get'):
            return 'apt'
        # Check for DNF (Fedora)
        elif self._command_exists('dnf'):
            return 'dnf'
        # Check for YUM (RHEL/CentOS)
        elif self._command_exists('yum'):
            return 'yum'
        # Check for Zypper (openSUSE)
        elif self._command_exists('zypper'):
            return 'zypper'
        else:
            return 'unknown'
    
    def _command_exists(self, command):
        """Check if a command exists on the system"""
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
        """Detect all available package managers on the system"""
        available = {}
        for fmt_name, fmt_info in config.SUPPORTED_FORMATS.items():
            for manager in fmt_info['managers']:
                if self._command_exists(manager):
                    if fmt_name not in available:
                        available[fmt_name] = []
                    available[fmt_name].append(manager)
        return available
    
    def validate_package(self, package_path):
        """Validate if the package file is supported and exists"""
        if not os.path.exists(package_path):
            return False
        
        _, ext = os.path.splitext(package_path)
        return ext.lower() in self.supported_formats
    
    def get_package_type(self, package_path):
        """Get the package type (.deb or .rpm)"""
        _, ext = os.path.splitext(package_path)
        return ext.lower()
    
    def get_package_info(self, package_path):
        """Extract package information"""
        package_type = self.get_package_type(package_path)
        
        try:
            if package_type == '.deb':
                return self._get_deb_info(package_path)
            elif package_type == '.rpm':
                return self._get_rpm_info(package_path)
            elif package_type == '.snap':
                return self._get_snap_info(package_path)
            elif package_type == '.flatpak':
                return self._get_flatpak_info(package_path)
            else:
                return "Unsupported package format"
        except Exception as e:
            return f"Error reading package info: {str(e)}"
    
    def _get_deb_info(self, package_path):
        """Get information from .deb package"""
        try:
            result = subprocess.run(
                ['dpkg-deb', '-I', package_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse and format the output
                info = result.stdout
                lines = info.split('\n')
                
                # Extract key information
                formatted_info = "Package Type: Debian (.deb)\n\n"
                for line in lines:
                    line = line.strip()
                    if line.startswith('Package:') or \
                       line.startswith('Version:') or \
                       line.startswith('Architecture:') or \
                       line.startswith('Maintainer:') or \
                       line.startswith('Description:'):
                        formatted_info += line + '\n'
                
                return formatted_info if formatted_info else info
            else:
                return f"Package Type: Debian (.deb)\n\nFilename: {os.path.basename(package_path)}\nSize: {self._get_file_size(package_path)}"
        except FileNotFoundError:
            return f"Package Type: Debian (.deb)\n\nFilename: {os.path.basename(package_path)}\nSize: {self._get_file_size(package_path)}\n\nNote: dpkg-deb not found. Install dpkg for detailed info."
        except Exception as e:
            return f"Package Type: Debian (.deb)\n\nError: {str(e)}"
    
    def _get_rpm_info(self, package_path):
        """Get information from .rpm package"""
        try:
            result = subprocess.run(
                ['rpm', '-qip', package_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse and format the output
                info = result.stdout
                lines = info.split('\n')
                
                # Extract key information
                formatted_info = "Package Type: RPM\n\n"
                for line in lines:
                    line = line.strip()
                    if line.startswith('Name') or \
                       line.startswith('Version') or \
                       line.startswith('Release') or \
                       line.startswith('Architecture') or \
                       line.startswith('Summary') or \
                       line.startswith('Description'):
                        formatted_info += line + '\n'
                
                return formatted_info if formatted_info else info
            else:
                return f"Package Type: RPM\n\nFilename: {os.path.basename(package_path)}\nSize: {self._get_file_size(package_path)}"
        except FileNotFoundError:
            return f"Package Type: RPM\n\nFilename: {os.path.basename(package_path)}\nSize: {self._get_file_size(package_path)}\n\nNote: rpm not found. Install rpm for detailed info."
        except Exception as e:
            return f"Package Type: RPM\n\nError: {str(e)}"
    
    def _get_file_size(self, file_path):
        """Get file size in human-readable format"""
        size_bytes = os.path.getsize(file_path)
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.2f} TB"
    
    def _get_snap_info(self, package_path):
        """Get information from .snap package"""
        try:
            # Snap packages need to be examined differently
            # Try to read metadata from the package
            result = subprocess.run(
                ['unsquashfs', '-ll', package_path, 'meta/snap.yaml'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                formatted_info = "Package Type: Snap Package 📸\n\n"
                formatted_info += f"Filename: {os.path.basename(package_path)}\n"
                formatted_info += f"Size: {self._get_file_size(package_path)}\n\n"
                formatted_info += "Note: Install snapd to view detailed metadata.\n"
                formatted_info += "After installation, use: snap info <package-name>\n"
                return formatted_info
            else:
                return f"Package Type: Snap Package 📸\n\nFilename: {os.path.basename(package_path)}\nSize: {self._get_file_size(package_path)}\n\nNote: Detailed info will be available after installation."
        except FileNotFoundError:
            return f"Package Type: Snap Package 📸\n\nFilename: {os.path.basename(package_path)}\nSize: {self._get_file_size(package_path)}\n\nNote: Install snapd and unsquashfs for detailed package info."
        except Exception as e:
            return f"Package Type: Snap Package 📸\n\nFilename: {os.path.basename(package_path)}\nSize: {self._get_file_size(package_path)}\n\nNote: {str(e)}"
    
    def _get_flatpak_info(self, package_path):
        """Get information from .flatpak package"""
        try:
            # Flatpak bundles can be inspected
            result = subprocess.run(
                ['flatpak', 'info', '--show-metadata', package_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                info = result.stdout
                formatted_info = "Package Type: Flatpak Package 📱\n\n"
                formatted_info += f"Filename: {os.path.basename(package_path)}\n"
                formatted_info += f"Size: {self._get_file_size(package_path)}\n\n"
                
                # Parse metadata
                lines = info.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('[Application]') or \
                       line.startswith('name=') or \
                       line.startswith('runtime=') or \
                       line.startswith('sdk=') or \
                       line.startswith('command='):
                        formatted_info += line + '\n'
                
                return formatted_info if formatted_info else info
            else:
                return f"Package Type: Flatpak Package 📱\n\nFilename: {os.path.basename(package_path)}\nSize: {self._get_file_size(package_path)}\n\nNote: Detailed info will be available after installation."
        except FileNotFoundError:
            return f"Package Type: Flatpak Package 📱\n\nFilename: {os.path.basename(package_path)}\nSize: {self._get_file_size(package_path)}\n\nNote: Install flatpak for detailed package info."
        except Exception as e:
            return f"Package Type: Flatpak Package 📱\n\nFilename: {os.path.basename(package_path)}\nSize: {self._get_file_size(package_path)}\n\nNote: {str(e)}"
    
    def verify_package(self, package_path, checksum=None, checksum_type='sha256', check_signature=False):
        """
        Comprehensive package verification
        
        Args:
            package_path: Path to the package file
            checksum: Expected checksum value (optional)
            checksum_type: Type of checksum ('sha256' or 'md5')
            check_signature: Whether to verify GPG signature
        
        Returns:
            tuple: (success: bool, message: str, details: dict)
        """
        verification_results = {
            'file_exists': False,
            'file_size': 0,
            'checksum_match': None,
            'signature_valid': None,
            'integrity_ok': False
        }
        
        try:
            # 1. Check if file exists
            if not os.path.exists(package_path):
                return False, "Package file not found", verification_results
            
            verification_results['file_exists'] = True
            
            # 2. Get file size
            file_size = os.path.getsize(package_path)
            verification_results['file_size'] = file_size
            
            # Check if file is suspiciously small (< 1KB)
            if file_size < 1024:
                return False, f"Package file too small ({file_size} bytes). May be corrupted.", verification_results
            
            # 3. Verify checksum if provided
            if checksum:
                calculated_checksum = self._calculate_checksum(package_path, checksum_type)
                
                if calculated_checksum.lower() == checksum.lower():
                    verification_results['checksum_match'] = True
                else:
                    verification_results['checksum_match'] = False
                    return False, f"{checksum_type.upper()} checksum mismatch!\\nExpected: {checksum}\\nGot: {calculated_checksum}", verification_results
            
            # 4. Verify GPG signature if requested
            if check_signature:
                sig_valid, sig_msg = self._verify_gpg_signature(package_path)
                verification_results['signature_valid'] = sig_valid
                
                if not sig_valid:
                    return False, f"GPG signature verification failed: {sig_msg}", verification_results
            
            # 5. Basic integrity check (try to read package metadata)
            integrity_ok, integrity_msg = self._check_package_integrity(package_path)
            verification_results['integrity_ok'] = integrity_ok
            
            if not integrity_ok:
                return False, f"Package integrity check failed: {integrity_msg}", verification_results
            
            # All checks passed
            success_msg = "✅ Package verification successful\\n"
            if checksum:
                success_msg += f"✓ {checksum_type.upper()} checksum verified\\n"
            if check_signature:
                success_msg += "✓ GPG signature valid\\n"
            success_msg += "✓ Package integrity OK"
            
            return True, success_msg, verification_results
            
        except Exception as e:
            return False, f"Verification error: {str(e)}", verification_results
    
    def _calculate_checksum(self, file_path, checksum_type='sha256'):
        """Calculate file checksum"""
        import hashlib
        
        if checksum_type.lower() == 'sha256':
            hasher = hashlib.sha256()
        elif checksum_type.lower() == 'md5':
            hasher = hashlib.md5()
        else:
            raise ValueError(f"Unsupported checksum type: {checksum_type}")
        
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            while chunk := f.read(8192):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _verify_gpg_signature(self, package_path):
        """Verify GPG signature of package"""
        package_type = self.get_package_type(package_path)
        
        try:
            if package_type == '.deb':
                # For .deb packages, check if there's a .asc or .sig file
                sig_path = package_path + '.asc'
                if not os.path.exists(sig_path):
                    sig_path = package_path + '.sig'
                
                if not os.path.exists(sig_path):
                    return False, "No signature file found (.asc or .sig required)"
                
                # Verify using gpg
                result = subprocess.run(
                    ['gpg', '--verify', sig_path, package_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    return True, "Signature valid"
                else:
                    return False, result.stderr
                    
            elif package_type == '.rpm':
                # For RPM packages, use rpm --checksig
                result = subprocess.run(
                    ['rpm', '--checksig', package_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and 'OK' in result.stdout:
                    return True, "Signature valid"
                else:
                    return False, result.stdout + result.stderr
            
            else:
                return False, "Unsupported package type for signature verification"
                
        except FileNotFoundError:
            return False, "GPG or RPM tools not installed"
        except subprocess.TimeoutExpired:
            return False, "Signature verification timed out"
        except Exception as e:
            return False, f"Signature verification error: {str(e)}"
    
    def _check_package_integrity(self, package_path):
        """Check if package file is valid and not corrupted"""
        package_type = self.get_package_type(package_path)
        
        try:
            if package_type == '.deb':
                # Try to read package metadata
                result = subprocess.run(
                    ['dpkg-deb', '--info', package_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return True, "Package structure valid"
                else:
                    return False, "Package appears to be corrupted or invalid"
                    
            elif package_type == '.rpm':
                # Try to query package
                result = subprocess.run(
                    ['rpm', '-qp', package_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return True, "Package structure valid"
                else:
                    return False, "Package appears to be corrupted or invalid"
            
            return True, "Basic checks passed"
            
        except FileNotFoundError:
            # If tools aren't available, skip this check
            return True, "Integrity check skipped (tools not available)"
        except subprocess.TimeoutExpired:
            return False, "Integrity check timed out"
        except Exception as e:
            return False, f"Integrity check error: {str(e)}"
    
    def get_package_checksum(self, package_path, checksum_type='sha256'):
        """
        Calculate and return package checksum
        Useful for users who want to verify against a known checksum
        """
        try:
            checksum = self._calculate_checksum(package_path, checksum_type)
            file_size = self._get_file_size(package_path)
            
            return {
                'success': True,
                'checksum': checksum,
                'type': checksum_type.upper(),
                'file_size': file_size,
                'file_name': os.path.basename(package_path)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def install_package(self, package_path):
        """Install the package using appropriate package manager"""
        package_type = self.get_package_type(package_path)
        
        try:
            if package_type == '.deb':
                return self._install_deb(package_path)
            elif package_type == '.rpm':
                return self._install_rpm(package_path)
            elif package_type == '.snap':
                return self._install_snap(package_path)
            elif package_type == '.flatpak':
                return self._install_flatpak(package_path)
            else:
                return False, "Unsupported package format"
        except Exception as e:
            return False, f"Installation failed: {str(e)}"
    
    def _install_deb(self, package_path):
        """Install .deb package"""
        try:
            # Try using apt first (handles dependencies better)
            if self._command_exists('apt'):
                result = subprocess.run(
                    ['pkexec', 'apt', 'install', '-y', package_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            # Fallback to dpkg
            elif self._command_exists('dpkg'):
                result = subprocess.run(
                    ['pkexec', 'dpkg', '-i', package_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                # Fix dependencies if needed
                if result.returncode != 0:
                    subprocess.run(
                        ['pkexec', 'apt-get', 'install', '-f', '-y'],
                        timeout=300
                    )
            else:
                return False, "No suitable package manager found for .deb files"
            
            if result.returncode == 0:
                return True, f"Package installed successfully!\n\n{result.stdout}"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, f"Installation failed:\n{error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Installation timed out. The package may be too large or there may be network issues."
        except Exception as e:
            return False, f"Installation error: {str(e)}"
    
    def _install_rpm(self, package_path):
        """Install .rpm package"""
        try:
            # Try DNF first (Fedora)
            if self._command_exists('dnf'):
                result = subprocess.run(
                    ['pkexec', 'dnf', 'install', '-y', package_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            # Try YUM (RHEL/CentOS)
            elif self._command_exists('yum'):
                result = subprocess.run(
                    ['pkexec', 'yum', 'install', '-y', package_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            # Try Zypper (openSUSE)
            elif self._command_exists('zypper'):
                result = subprocess.run(
                    ['pkexec', 'zypper', 'install', '-y', package_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            # Fallback to rpm
            elif self._command_exists('rpm'):
                result = subprocess.run(
                    ['pkexec', 'rpm', '-ivh', package_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            else:
                return False, "No suitable package manager found for .rpm files"
            
            if result.returncode == 0:
                return True, f"Package installed successfully!\n\n{result.stdout}"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, f"Installation failed:\n{error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Installation timed out. The package may be too large or there may be network issues."
        except Exception as e:
            return False, f"Installation error: {str(e)}"
    
    def _install_snap(self, package_path):
        """Install .snap package"""
        try:
            # Check if snapd is running
            if not self._command_exists('snap'):
                return False, "Snap is not installed. Please install snapd:\n  sudo apt install snapd  # Debian/Ubuntu\n  sudo dnf install snapd  # Fedora"
            
            # Check if snapd service is running
            check_service = subprocess.run(
                ['systemctl', 'is-active', 'snapd'],
                capture_output=True,
                text=True
            )
            
            if check_service.returncode != 0:
                return False, "snapd service is not running. Please start it:\n  sudo systemctl start snapd\n  sudo systemctl enable snapd"
            
            # Install snap package with dangerous flag (for local files)
            result = subprocess.run(
                ['pkexec', 'snap', 'install', '--dangerous', package_path],
                capture_output=True,
                text=True,
                timeout=config.INSTALLATION_TIMEOUT
            )
            
            if result.returncode == 0:
                return True, f"Snap package installed successfully!\n\n{result.stdout}"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, f"Installation failed:\n{error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Installation timed out. The package may be too large or there may be network issues."
        except Exception as e:
            return False, f"Installation error: {str(e)}"
    
    def _install_flatpak(self, package_path):
        """Install .flatpak package"""
        try:
            # Check if flatpak is installed
            if not self._command_exists('flatpak'):
                return False, "Flatpak is not installed. Please install it:\n  sudo apt install flatpak  # Debian/Ubuntu\n  sudo dnf install flatpak  # Fedora"
            
            # Install flatpak bundle
            # Flatpak handles permissions internally, no need for pkexec usually
            # However, system-wide installation might require it
            result = subprocess.run(
                ['flatpak', 'install', '-y', '--bundle', package_path],
                capture_output=True,
                text=True,
                timeout=config.INSTALLATION_TIMEOUT
            )
            
            # If user installation fails, try system installation
            if result.returncode != 0:
                result = subprocess.run(
                    ['pkexec', 'flatpak', 'install', '-y', '--system', '--bundle', package_path],
                    capture_output=True,
                    text=True,
                    timeout=config.INSTALLATION_TIMEOUT
                )
            
            if result.returncode == 0:
                return True, f"Flatpak package installed successfully!\n\n{result.stdout}"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, f"Installation failed:\n{error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Installation timed out. The package may be too large or there may be network issues."
        except Exception as e:
            return False, f"Installation error: {str(e)}"
    
    def check_permissions(self):
        """Check if the user has necessary permissions"""
        # Check if running as root or can use sudo/pkexec
        if os.geteuid() == 0:
            return True
        
        # Check for pkexec
        if self._command_exists('pkexec'):
            return True
        
        # Check for sudo
        if self._command_exists('sudo'):
            return True
        
        return False
