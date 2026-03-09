"""
Logger Module
Handles logging of installation activities and history tracking
"""

import os
import json
from datetime import datetime
from . import config


class InstallLogger:
    """Log installation activities and maintain history"""
    
    def __init__(self, log_dir=None):
        """Initialize logger with log directory"""
        if log_dir is None:
            # Use user's home directory for logs
            log_dir = str(config.USER_CONFIG_DIR)
        
        self.log_dir = log_dir
        self.log_file = str(config.HISTORY_FILE)
        
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
    
    def export_history(self, export_path, format='json'):
        """Export history to a file in JSON or CSV format"""
        try:
            history = self.get_history()
            
            if format.lower() == 'csv':
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    if history:
                        fieldnames = ['timestamp', 'package_name', 'success', 'message']
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for entry in history:
                            writer.writerow({
                                'timestamp': entry.get('timestamp', ''),
                                'package_name': entry.get('package_name', ''),
                                'success': 'Success' if entry.get('success') else 'Failed',
                                'message': entry.get('message', '')
                            })
            else:  # JSON
                export_data = {
                    'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_entries': len(history),
                    'entries': history
                }
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data,f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting history: {e}")
            return False
    
    def import_history(self, import_path, merge=True):
        """Import history from a JSON file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # Handle both old format (array) and new format (object with metadata)
            if isinstance(imported_data, list):
                imported_entries = imported_data
            elif isinstance(imported_data, dict) and 'entries' in imported_data:
                imported_entries = imported_data['entries']
            else:
                return False
            
            if merge:
                # Merge with existing history
                current_history = self.get_history()
                current_history.extend(imported_entries)
                final_history = current_history
            else:
                # Replace existing history
                final_history = imported_entries
            
            # Write to file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(final_history, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error importing history: {e}")
            return False
    
    def search_history(self, query):
        """Search history by package name"""
        if not query:
            return self.get_history()
        
        history = self.get_history()
        query_lower = query.lower()
        
        return [entry for entry in history 
                if query_lower in entry.get('package_name', '').lower() or
                   query_lower in entry.get('package', '').lower()]
    
    def filter_history(self, status=None, package_type=None, date_from=None, date_to=None):
        """Filter history by various criteria"""
        history = self.get_history()
        filtered = history
        
        # Filter by status
        if status == 'success':
            filtered = [e for e in filtered if e.get('success', False)]
        elif status == 'failed':
            filtered = [e for e in filtered if not e.get('success', False)]
        
        # Filter by package type
        if package_type:
            if package_type == 'deb':
                filtered = [e for e in filtered if e.get('package_name', '').endswith('.deb')]
            elif package_type == 'rpm':
                filtered = [e for e in filtered if e.get('package_name', '').endswith('.rpm')]
        
        # Filter by date range
        if date_from or date_to:
            def parse_date(date_str):
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                except:
                    return None
            
            if date_from:
                from_dt = datetime.strptime(date_from, '%Y-%m-%d')
                filtered = [e for e in filtered 
                           if parse_date(e.get('timestamp', '')) and 
                              parse_date(e.get('timestamp', '')) >= from_dt]
            
            if date_to:
                to_dt = datetime.strptime(date_to, '%Y-%m-%d')
                filtered = [e for e in filtered 
                           if parse_date(e.get('timestamp', '')) and 
                              parse_date(e.get('timestamp', '')) <= to_dt]
        
        return filtered

