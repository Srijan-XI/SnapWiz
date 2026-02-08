"""
Logger Module
Handles logging of installation activities and history tracking
"""

import os
import json
from datetime import datetime


class InstallLogger:
    """Log installation activities and maintain history"""
    
    def __init__(self, log_dir=None):
        """Initialize logger with log directory"""
        if log_dir is None:
            # Use user's home directory for logs
            home = os.path.expanduser("~")
            log_dir = os.path.join(home, ".snapwiz")
        
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, "installation_history.json")
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize log file if it doesn't exist
        if not os.path.exists(self.log_file):
            self._init_log_file()
    
    def _init_log_file(self):
        """Initialize empty log file"""
        with open(self.log_file, 'w') as f:
            json.dump([], f)
    
    def log_installation(self, package_path, success, message):
        """Log an installation attempt"""
        try:
            # Read existing history
            history = self.get_history()
            
            # Create new log entry
            entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'package': package_path,
                'package_name': os.path.basename(package_path),
                'success': success,
                'message': message
            }
            
            # Append to history
            history.append(entry)
            
            # Write back to file
            with open(self.log_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error logging installation: {e}")
            return False
    
    def get_history(self):
        """Get installation history"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error reading history: {e}")
            return []
    
    def clear_history(self):
        """Clear installation history"""
        try:
            self._init_log_file()
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
    
    def get_successful_installations(self):
        """Get only successful installations"""
        history = self.get_history()
        return [entry for entry in history if entry.get('success', False)]
    
    def get_failed_installations(self):
        """Get only failed installations"""
        history = self.get_history()
        return [entry for entry in history if not entry.get('success', False)]
    
    def get_stats(self):
        """Get installation statistics"""
        history = self.get_history()
        total = len(history)
        successful = len(self.get_successful_installations())
        failed = len(self.get_failed_installations())
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }
    
    def export_history(self, export_path):
        """Export history to a file"""
        try:
            history = self.get_history()
            with open(export_path, 'w') as f:
                json.dump(history, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting history: {e}")
            return False
