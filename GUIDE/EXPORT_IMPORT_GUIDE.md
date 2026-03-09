# 📦 Export/Import History Feature - SnapWiz

**Feature Status**: ✅ **IMPLEMENTED** (v1.1)  
**Date Added**: 2026-02-08

---

## Overview

The Export/Import History feature allows you to backup your installation history and restore it later. Perfect for moving to a new machine, sharing installation logs with support, or analyzing your package management data in spreadsheets.

---

## Features

### 📊 **Export to CSV**
- Export history to comma-separated values format
- Perfect for Excel, Google Sheets, LibreOffice Calc
- Easy to analyze and create charts
- Simplified format with key information

**CSV Columns**:
- Timestamp
- Package Name
- Status (Success/Failed)
- Message

### 📦 **Export to JSON**
- Export complete history with full metadata
- Preserves all installation details
- Can be re-imported into SnapWiz
- Includes export timestamp and entry count
- Human-readable format

**JSON Structure**:
```json
{
  "export_date": "2026-02-08 18:30:00",
  "total_entries": 25,
  "entries": [
    {
      "timestamp": "2026-02-08 14:30:00",
      "package": "/path/to/package.deb",
      "package_name": "package.deb",
      "success": true,
      "message": "Package installed successfully"
    }
  ]
}
```

### 📥 **Import from JSON**
- Restore history from JSON backup
- Two import modes:
  - **Merge** - Add to existing history
  - **Replace** - Overwrite all history
- Validates file format before importing
- Shows entry count after import

---

## How to Use

### Exporting to CSV

1. Go to **📋 Installation History** tab
2. Click **📊 Export CSV** button
3. Choose where to save the file
4. Default filename: `snapwiz_history.csv`
5. Click **Save**
6. Success message will confirm export

**Use Cases**:
- Analyze installation trends in Excel
- Create charts and graphs
- Share with support teams
- Document your system setup
- Generate reports

### Exporting to JSON

1. Go to **📋 Installation History** tab
2. Click **📦 Export JSON** button
3. Choose where to save the file
4. Default filename: `snapwiz_history.json`
5. Click **Save**
6. Success message shows entry count

**Use Cases**:
- Backup before system reinstall
- Transfer history to another machine
- Archive old installations
- Version control your system state
- Debugging and troubleshooting

### Importing from JSON

1. Go to **📋 Installation History** tab
2. Click **📥 Import** button
3. Select a JSON file to import
4. Choose import mode:
   - **Yes** - Merge (keeps existing + adds imported)
   - **No** - Replace (deletes existing, uses imported)
   - **Cancel** - Abort import
5. Confirm import
6. History automatically refreshes

**Use Cases**:
- Restore backup after reinstall
- Combine histories from multiple machines
- Recover deleted history
- Import from old backups

---

## User Interface

### History Tab with Export/Import Buttons

```
┌──────────────────────────────────────────────────┐
│ 📋 Installation History                          │
│                                                  │
│ [Search box and filters...                    ] │
│                                                  │
│ [History list...                               ] │
│                                                  │
│ ┌────────────────────────────────────────────┐ │
│ │ [🔄 Refresh] [🗑️ Clear]                    │ │
│ │ [📊 Export CSV] [📦 Export JSON] [📥 Import]│ │
│ └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

---

## Step-by-Step Examples

### Example 1: Create a Monthly Backup

**Goal**: Export your history at the end of each month

```
1. Click "📦 Export JSON"
2. Save as: "snapwiz_backup_2026-02.json"
3. Store in your Documents/Backups folder
4. Repeat monthly
```

### Example 2: Analyze in Excel

**Goal**: See which packages failed most often

```
1. Click "📊 Export CSV"
2. Save as: "snapwiz_analysis.csv"  
3. Open in Excel
4. Sort by "Status" column
5. Filter for "Failed"
6. Create pie chart of failures
```

### Example 3: Transfer to New Machine

**Goal**: Move your history to a fresh Linux install

**On old machine**:
```
1. Click "📦 Export JSON"
2. Save as: "snapwiz_backup.json"
3. Copy to USB drive or cloud storage
```

**On new machine**:
```
1. Install SnapWiz
2. Click "📥 Import"
3. Select "snapwiz_backup.json"
4. Choose "No" (Replace) for clean import
5. All history restored!
```

### Example 4: Merge Two Histories

**Goal**: Combine installation records from two machines

```
1. Export from Machine A → "machine_a.json"
2. Export from Machine B → "machine_b.json"
3. On Machine A: Import "machine_b.json"
4. Choose "Yes" (Merge)
5. Now Machine A has both histories
```

---

## File Formats

### CSV Format (Spreadsheet)

```csv
timestamp,package_name,success,message
2026-02-08 14:30:00,firefox.deb,Success,Package installed successfully
2026-02-07 10:15:00,chrome.deb,Failed,Dependency conflict detected
2026-02-06 16:45:00,vim.deb,Success,Installation completed
```

**Advantages**:
- ✅ Universal format (works everywhere)
- ✅ Easy to read
- ✅ Perfect for analysis
- ✅ Import into any spreadsheet

**Limitations**:
- ❌ Cannot be re-imported into SnapWiz
- ❌ Some details may be truncated
- ❌ No metadata included

### JSON Format (Backup)

```json
{
  "export_date": "2026-02-08 18:30:00",
  "total_entries": 3,
  "entries": [
    {
      "timestamp": "2026-02-08 14:30:00",
      "package": "/home/user/Downloads/firefox.deb",
      "package_name": "firefox.deb",
      "success": true,
      "message": "Package installed successfully"
    }
  ]
}
```

**Advantages**:
- ✅ Can be re-imported
- ✅ Preserves all details
- ✅ Includes metadata
- ✅ Version-safe

**Limitations**:
- ❌ Not as easy to read
- ❌ Requires JSON-aware tools

---

## Import Modes Explained

### Merge Mode (Yes)

**What it does**: Adds imported entries to existing history

```
Before: [A, B, C]
Import: [D, E]
After:  [A, B, C, D, E]
```

**Use when**:
- Combining histories from multiple sources
- Adding old backups to current history
- Don't want to lose current data

### Replace Mode (No)

**What it does**: Deletes current history and uses imported only

```
Before: [A, B, C]
Import: [D, E]
After:  [D, E]
```

**Use when**:
- Restoring from backup after data loss
- Want clean slate with imported data
- Migrating to new system

---

## Tips & Best Practices

### 💡 Backup Strategy

**Recommended**:
1. Export JSON monthly for backups
2. Store backups in cloud storage (Dropbox, Google Drive)
3. Name files with dates: `snapwiz_2026-02.json`
4. Keep at least 3 months of backups

### 📊 Analysis Workflow

**For data analysis**:
1. Export CSV when you need to analyze
2. Use Excel PivotTables for insights
3. Create charts to visualize trends
4. Export doesn't affect your original data

### 🔒 Data Safety

**Before major operations**:
1. Always export before clearing history
2. Export before importing (in case something goes wrong)
3. Test imports on merge mode first
4. Keep backups before system reinstall

### 📁 File Organization

**Suggested structure**:
```
Documents/
  SnapWiz-Backups/
    Monthly/
      snapwiz_2026-01.json
      snapwiz_2026-02.json
    Analysis/
      installations_report.csv
    Old/
      snapwiz_2025-12.json
```

---

## Troubleshooting

### Export Failed

**Problem**: "Failed to export history"  
**Causes**:
- No write permission in selected folder
- Disk full
- File already open in another program

**Solutions**:
- Choose a different folder (e.g., Documents)
- Check disk space
- Close Excel/spreadsheet apps
- Try desktop folder

### Import Failed

**Problem**: "Failed to import history"  
**Causes**:
- Not a valid JSON file
- Corrupted file
- Wrong file format (CSV instead of JSON)

**Solutions**:
- Make sure you're importing a SnapWiz JSON export
- Try re-exporting from source
- Check file isn't corrupted
- Only JSON can be imported (not CSV)

### Import Shows Zero Entries

**Problem**: Import successful but no entries appear  
**Cause**: Imported file was empty

**Solution**:
- Check the source file has data
- Open JSON in text editor to verify
- Try exporting again from source

### Lost Data After Replace Import

**Problem**: Accidentally chose "Replace" instead of "Merge"  
**Solution**:
- Unfortunately, replaced data is lost
- Always export BEFORE importing
- Use backup to restore

---

## Keyboard Shortcuts

**Future enhancements**:
- `Ctrl+E` - Quick export JSON
- `Ctrl+Shift+E` - Quick export CSV
- `Ctrl+I` - Import history

---

## Technical Details

### CSV Export Format
- Encoding: UTF-8
- Line endings: System default
- Delimiter: Comma (`,`)
- Headers: Yes (first row)
- Quoting: Auto (for fields with commas)

### JSON Export Format
- Encoding: UTF-8
- Indentation: 2 spaces
- Pretty-printed: Yes
- Schema: SnapWiz History v1.0

### File Size Estimates
| Entries | CSV Size | JSON Size |
|---------|----------|-----------|
| 100     | ~15 KB   | ~25 KB    |
| 500     | ~75 KB   | ~125 KB   |
| 1000    | ~150 KB  | ~250 KB   |
| 5000    | ~750 KB  | ~1.25 MB  |

---

## Security & Privacy

### What's Exported
✅ Installation timestamps  
✅ Package names  
✅ Installation status (success/failed)  
✅ Error messages  
✅ File paths

### What's NOT Exported
❌ Passwords  
❌ System passwords  
❌ Personal files  
❌ Package contents

### Privacy Considerations
- File paths may reveal username
- Consider redacting before sharing publicly
- No sensitive credentials are included
- Safe to share for support purposes

---

## Future Enhancements

Planned for future versions:

- 📅 **Date Range Export** - Export only specific date ranges
- 🎯 **Selective Export** - Export filtered results only
- 🔄 **Auto-Backup** - Automatic weekly/monthly backups
- ☁️ **Cloud Sync** - Sync to cloud storage
- 📧 **Email Export** - Send reports via email
- 🗜️ **Compression** - Compressed backup files
- 📝 **Export Templates** - Custom export formats

---

## Related Features

- **Search & Filter** - Filter before exporting
- **Installation History** - The data being exported
- **Clear History** - Remove entries before export

---

## Changelog

### v1.1 (2026-02-08)
- ✨ Initial implementation
- ✅ CSV export functionality
- ✅ JSON export with metadata
- ✅ JSON import with merge/replace
- ✅ File dialogs for user-friendly operation
- ✅ Detailed success/error messages

---

**Last Updated**: 2026-02-08  
**Feature Version**: 1.1  
**Status**: Production Ready ✅
