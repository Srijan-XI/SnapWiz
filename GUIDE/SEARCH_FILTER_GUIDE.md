# 🔍 Search & Filter Feature - SnapWiz

**Feature Status**: ✅ **IMPLEMENTED** (v1.1)  
**Date Added**: 2026-02-08

---

## Overview

The Search & Filter feature allows you to quickly find specific installations in your history by searching for package names and applying various filters.

---

## Features

### 🔍 **Real-Time Search**
- Search by package name as you type
- Instant results without clicking buttons
- Case-insensitive matching
- Matches both package filename and full path

### 📊 **Status Filter**
Filter installations by their outcome:
- **All** - Show all installations
- **✅ Success** - Show only successful installations
- **❌ Failed** - Show only failed installations

### 📦 **Package Type Filter**
Filter by package format:
- **All** - Show all package types
- **.deb** - Show only Debian packages
- **.rpm** - Show only RPM packages

### 🔄 **Clear Filters**
- Reset all filters with one click
- Instantly return to showing all history

### 📈 **Results Counter**
- Shows how many results match your filters
- Displays "Showing X of Y results" when filtered
- Helpful for understanding your installation history

---

## How to Use

### Basic Search

1. Go to the **📋 Installation History** tab
2. Type in the **Search** box
3. Results appear instantly as you type

**Example**:
- Type "firefox" to find all Firefox installations
- Type ".deb" to find all Debian packages

### Using Filters

#### Filter by Status
1. Click the **Status** dropdown
2. Select:
   - **All** for all installations
   - **✅ Success** for successful only
   - **❌ Failed** for failures only

#### Filter by Package Type
1. Click the **Type** dropdown
2. Select:
   - **All** for all types
   - **.deb** for Debian packages
   - **.rpm** for RPM packages

### Combining Search and Filters

You can combine search withfilters for powerful queries:

**Example 1**: Find failed Firefox installations
1. Search: "firefox"
2. Status: "❌ Failed"

**Example 2**: Find successful .deb installations
1. Status: "✅ Success"
2. Type: ".deb"

**Example 3**: Search for Chrome among .deb packages
1. Search: "chrome"
2. Type: ".deb"

### Clearing Filters

Click the **🔄 Clear Filters** button to:
- Clear the search box
- Reset status to "All"
- Reset type to "All"
- Show all history again

---

## User Interface

### Search & Filter Panel

```
┌─────────────────────────────────────────────────┐
│ 🔍 Search & Filter                              │
│                                                 │
│ Search: [Type to search packages...         ]  │
│                                                 │
│ Status: [ All ▼ ]  Type: [ All ▼ ]  [Clear]   │
└─────────────────────────────────────────────────┘

Showing 15 of 45 results

┌─────────────────────────────────────────────────┐
│ ✅ package1.deb - 2026-02-08 14:30:00          │
│ ❌ package2.rpm - 2026-02-07 10:15:00          │
│ ✅ package3.deb - 2026-02-06 16:45:00          │
└─────────────────────────────────────────────────┘
```

---

## Keyboard Shortcuts

- **F5** - Refresh history (respects active filters)
- **Ctrl+F** - Focus search box (future enhancement)
- **Esc** - Clear search (future enhancement)

---

## Technical Details

### Backend Methods (logger.py)

#### `search_history(query)`
```python
# Search by package name
results = logger.search_history("firefox")
```

#### `filter_history(status, package_type, date_from, date_to)`
```python
# Filter by multiple criteria
results = logger.filter_history(
    status="success",      # 'success', 'failed', or None
    package_type="deb",    # 'deb', 'rpm', or None
    date_from="2026-01-01",  # Optional
    date_to="2026-02-28"     # Optional
)
```

### UI Components

- **`search_input`** - QLineEdit for search queries
- **`status_filter`** - QComboBox for status filtering
- **`type_filter`** - QComboBox for package type filtering
- **`results_label`** - QLabel showing result count
- **`apply_filters()`** - Method that combines all filters
- **`clear_filters()`** - Method to reset all filters

---

## Performance

- **Real-time search**: Filters as you type
- **Optimized**: Works smoothly with 1000+ history entries
- **No lag**: Instant updates when changing filters
- **Efficient**: Uses Python list comprehensions for speed

---

## Examples

### Example 1: Find All Failed Installations
```
1. Click History tab
2. Status dropdown → "❌ Failed"
3. Review all failures
```

### Example 2: Search for Specific Package
```
1. Click History tab
2. Type "apache" in search box
3. See all Apache-related installations
```

### Example 3: Find All .deb Packages
```
1. Click History tab
2. Type dropdown → ".deb"
3. See all Debian package installations
```

### Example 4: Complex Query
```
1. Search: "lib"
2. Status: "✅ Success"
3. Type: ".deb"
Result: All successfully installed .deb libraries
```

---

## Tips & Tricks

### 💡 Power User Tips

1. **Quick failed package review**: Set Status to "❌ Failed" to see what needs attention

2. **Package type audit**: Use Type filter to see how many .deb vs .rpm packages you've installed

3. **Search by version**: Many package names include versions - search for "2.4" to find specific versions

4. **Case doesn't matter**: Search is case-insensitive - "FIREFOX", "firefox", and "Firefox" all work

5. **Partial matches**: Searching "fire" will find "firefox", "firewall", etc.

### 🎯 Common Use Cases

| Task | How To |
|------|--------|
| Find recent failures | Status: Failed, then look at dates |
| Check .deb installations | Type: .deb |
| Search specific app | Type app name in search |
| Review successful installs | Status: Success |
| Clear view | Click "Clear Filters" |

---

## Troubleshooting

### "No results found"
- **Cause**: Filters are too restrictive
- **Solution**: Click "Clear Filters" and try again

### Search not working
- **Cause**: Typo in search query
- **Solution**: Check spelling, try partial search

### Filter seems stuck
- **Cause**: Filter selection not reset
- **Solution**: Click "Clear Filters" button

---

## Future Enhancements

Planned for future versions:

- 📅 **Date Range Filter**: Filter by specific date ranges
- 🔢 **Advanced Search**: Search by message content
- 📊 **Sort Options**: Sort by date, name, or status
- 💾 **Save Filters**: Save commonly-used filter combinations
- 🔍 **Regex Search**: Advanced pattern matching
- 📈 **Visual Statistics**: Charts showing install success rates

---

## Related Features

- **Export/Import History** - Export filtered results
- **Installation History** - The data being searched
- **Clear History** - Remove old entries

---

## Changelog

### v1.1 (2026-02-08)
- ✨ Initial implementation
- ✅ Real-time search functionality
- ✅ Status filter (Success/Failed)
- ✅ Package type filter (.deb/.rpm)
-✅ Results counter
- ✅ Clear filters button

---

**Last Updated**: 2026-02-08  
**Feature Version**: 1.1  
**Status**: Production Ready ✅
