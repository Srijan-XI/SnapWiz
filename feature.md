# SnapWiz — Feature Roadmap

## Current State
The app is feature-complete for its core purpose — install/uninstall `.deb`, `.rpm`, `.snap`, `.flatpak` packages with history/verification. Dependencies are PyQt5-only; all logic uses stdlib. No TODOs or stubs exist.

---

## New Features We Can Add

### 🔒 Safety & Pre-Install Checks

| Feature | Why | Complexity |
|---|---|---|
| **Disk space check before install** | Prevent failed installs due to full disk; use `shutil.disk_usage()` | Low |
| **Auto-detect checksum sidecars** | If `package.deb.sha256` exists alongside a package, auto-load it into the checksum field | Low |
| **Batch checksum manifest** | Let user import a `.json`/`.csv` mapping filenames → expected checksums for batch mode (currently manual checksum is disabled in batch) | Medium |
| **Architecture mismatch warning** | Detect system arch vs package arch (e.g., warn if installing `arm64` on `x86_64`) | Low |

---

### 📦 Package Management

| Feature | Why | Complexity |
|---|---|---|
| **Installation profiles/presets** | Save named sets of packages (e.g., "Dev Setup", "Office Suite"), load & install all at once | Medium |
| **Bookmarked directories** | Remember recently used folders; shown above file dialog for quick access | Low |
| **Recent files quick-add** | Show last 10 used package paths in a dropdown — no dialog needed | Low |
| **Rollback / backup list** | Before installing, snapshot the installed package list so it can be diffed after | Medium |
| **Dependency preview** | Run `apt-get install --dry-run` / `dnf install --assumeno` and show what extra packages will be pulled | Medium |

---

### 📊 Statistics & Reporting

| Feature | Why | Complexity |
|---|---|---|
| **Statistics dashboard tab** | Charts for installs over time, success rate, top formats — using `QLabel`-based bar charts (no matplotlib needed) | Medium |
| **Package notes / tags in history** | Let users annotate history entries with custom text or emoji tags | Medium |
| **Install time tracking** | Record how long each installation took; show in history details | Low |

---

### 🔄 Automation & Integration

| Feature | Why | Complexity |
|---|---|---|
| **CLI argument support** | `python main.py --install file.deb` to trigger GUI install directly from terminal/file manager context menu | Low |
| **Post-install script runner** | After successful install, optionally run a user-defined `.sh` script (e.g., copy config files) | Medium |
| **Auto-update checker** | Poll GitHub Releases API for new SnapWiz versions; show a dismissible banner if newer version exists | Medium |
| **Desktop file association** | Register SnapWiz in the OS to open `.deb`/`.rpm` files by double-click in the file manager | Low |

---

### 🎨 UI/UX

| Feature | Why | Complexity |
|---|---|---|
| **Package details side panel** | When user selects a queued item, show full package metadata (name, version, maintainer, description) inline | Medium |
| **Search in log output** | `Ctrl+F` to search/highlight text in the installation log | Low |
| **Notification history** | Small panel showing the last N tray notifications (they disappear too fast) | Low |
| **Window geometry persistence** | Save/restore window size and position between sessions | Low |
| **Animated install button** | Pulsing glow animation on the "Start Installation" button when packages are queued | Low |

---

### 🌐 Language & Accessibility

| Feature | Why | Complexity |
|---|---|---|
| **Live language switching** | Apply language change without restart (rebuild UI strings in-place) | High |
| **Font size / scaling preference** | Slider in Settings to scale all UI text for accessibility | Medium |
| **High contrast theme** | A third theme preset alongside Light/Dark | Low |

---

## Priority Recommendation (Quick Wins First)

### Do First — Low Complexity, High Value
1. Disk space check before install
2. Auto-detect checksum sidecar files
3. Window geometry persistence (2 lines of code)
4. Recent files quick-add
5. Install time tracking in history
6. CLI argument support (`sys.argv` parsing)
7. Desktop file association registration

### Do Next — Medium Complexity
8. Package details side panel in the install queue
9. Installation profiles/presets
10. Statistics dashboard tab
11. Dependency preview (`--dry-run`)
12. Auto-update checker (GitHub API via `urllib`)
