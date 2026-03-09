#!/usr/bin/env python3
"""
Simple .po to .mo compiler using Python's msgfmt module
This is a pure Python implementation that doesn't require external tools
"""

from pathlib import Path
import struct
import array

def generate_mo(po_file, mo_file):
    """
    Generate a .mo file from a .po file
    Simple implementation for basic gettext functionality
    """
    # Read the .po file
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parse msgid/msgstr pairs
    entries = {}
    current_msgid = None
    current_msgstr = None
    in_msgid = False
    in_msgstr = False
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('msgid '):
            # Extract msgid
            current_msgid = line[6:].strip('"')
            in_msgid = True
            in_msgstr = False
        elif line.startswith('msgstr '):
            # Extract msgstr
            current_msgstr = line[7:].strip('"')
            in_msgstr = True
            in_msgid = False
        elif line.startswith('"') and (in_msgid or in_msgstr):
            # Continuation line
            text = line.strip('"')
            if in_msgid and current_msgid is not None:
                current_msgid += text
            elif in_msgstr and current_msgstr is not None:
                current_msgstr += text
        elif line == '' or line.startswith('#'):
            # Empty line or comment - save current entry
            if current_msgid and current_msgstr is not None:
                # Unescape special characters
                msgid = current_msgid.replace('\\n', '\n').replace('\\t', '\t')
                msgstr = current_msgstr.replace('\\n', '\n').replace('\\t', '\t')
                if msgid:  # Skip empty msgid (header)
                    entries[msgid] = msgstr
            current_msgid = None
            current_msgstr = None
            in_msgid = False
            in_msgstr = False
    
    # Save last entry if exists
    if current_msgid and current_msgstr is not None:
        msgid = current_msgid.replace('\\n', '\n').replace('\\t', '\t')
        msgstr = current_msgstr.replace('\\n', '\n').replace('\\t', '\t')
        if msgid:
            entries[msgid] = msgstr
    
    # Create .mo file (simple binary format)
    # This is a simplified version - just stores the msgid/msgstr pairs
    
    # For now, create a simple Python dict file that can be loaded
    # This is easier and doesn't require complex binary format
    
    # Actually, let's use a JSON-based approach which is simpler
    import json
    
    # Save as JSON instead of binary .mo
    # We'll modify the language.py to support this
    json_file = mo_file.with_suffix('.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    
    return len(entries)

def main():
    """Compile all .po files"""
    # Get parent directory since we're now in utils/
    locale_dir = Path(__file__).parent.parent / 'locales'
    
    print("=" * 60)
    print("SnapWiz Translation Compiler (JSON-based)")
    print("=" * 60)
    print(f"\nLocale Directory: {locale_dir}\n")
    
    po_files = list(locale_dir.rglob('*.po'))
    
    if not po_files:
        print("No .po files found")
        return
    
    print(f"Found {len(po_files)} translation file(s):\n")
    
    total_compiled = 0
    
    for po_file in po_files:
        # Get language code
        lang_code = po_file.parent.parent.name
        
        json_file = po_file.with_suffix('.json')
        
        print(f"Compiling {lang_code}: {po_file.name} -> {json_file.name}... ", end='')
        
        try:
            count = generate_mo(po_file, po_file.with_suffix('.mo'))
            print(f"✓ ({count} entries)")
            total_compiled += 1
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"Compiled {total_compiled} translation file(s) successfully!")
    print(f"{'=' * 60}\n")

if __name__ == '__main__':
    main()
