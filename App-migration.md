# SnapWiz Application Migration Plan: PyQt5 to Tauri

## 1. Objective

Migrate SnapWiz from its monolithic PyQt5/Python desktop UI to a Tauri 2 desktop application with:

- A web frontend written in TypeScript.
- A Rust Tauri backend for native desktop integration and package operations.
- The existing Linux package-manager behavior preserved for `.deb`, `.rpm`, `.snap`, and `.flatpak`.
- Existing user settings, installation history, translations, keyboard shortcuts, drag-and-drop, system-tray behavior, and progress reporting retained.

This plan assumes “tarui” means **Tauri**. The target is Linux-first; Windows and macOS packaging should remain out of scope until Linux behavior reaches parity.

## 2. Current-State Findings

| Area | Current implementation | Migration implication |
|---|---|---|
| Entry point/UI | `main.py` contains `InstallerThread`, `MainWindow`, four tabs, styling, dialogs, shortcuts, tray integration, and event handlers. | Split the UI into frontend components and move native work behind typed Tauri commands/events. |
| Package operations | `src/package_handler.py` detects managers, validates files, extracts metadata, verifies packages, installs packages, and invokes `pkexec`. | Reimplement the process boundary in Rust; preserve command selection, timeouts, exit-code handling, and stderr/stdout messages. |
| Installation workflow | `InstallerThread.run()` emits validation, verification, metadata, dependency, installation, configuration, and completion progress. | Define a typed installation event contract and stream progress to the frontend without blocking the webview. |
| History | `src/logger.py` stores JSON at `~/.snapwiz/installation_history.json`, with search, filters, import, and JSON/CSV export. | Keep the file format compatible for the first release; use Tauri path APIs and Rust serialization. |
| Settings | `src/config.py` and `main.py` persist theme, language, verification, checksum, and window-related preferences under `~/.snapwiz`. | Introduce a versioned settings schema and migration fallback for existing JSON. |
| Localization | `locales/{en,fr,de,es,it,ru}/LC_MESSAGES` contains PO/JSON translations; `src/language.py` loads JSON first and gettext as fallback. | Keep translation keys and language codes; load JSON in the frontend or expose a backend translation command. |
| Tests | Tests cover configuration and exceptions; package handler, logger, language, retry, and GUI coverage are incomplete. | Add backend unit tests and frontend/component/E2E tests before declaring parity. |
| Packaging | `install.sh`, `app.sh`, `setup.py`, and Python requirements package the PyQt application. | Replace with `package.json`, Tauri configuration, Rust dependencies, Linux bundle metadata, and CI artifacts. |

Primary source anchors: [`main.py`](./main.py), [`src/package_handler.py`](./src/package_handler.py), [`src/logger.py`](./src/logger.py), [`src/config.py`](./src/config.py), [`src/language.py`](./src/language.py), and [`test/`](./test/).

## 3. Target Architecture

```text
Tauri window
  └── TypeScript frontend
      ├── Install view
      ├── Uninstall view
      ├── History view
      ├── Settings view
      └── typed API/event client
          └── Tauri invoke/listen
              └── Rust backend
                  ├── package service
                  │   ├── validation and metadata
                  │   ├── verification/checksums
                  │   ├── install/uninstall command runner
                  │   └── manager detection
                  ├── history service
                  ├── settings service
                  ├── localization/resource service
                  └── tray, notifications, dialogs, paths
```

### Recommended target choices

- **Tauri:** Tauri 2.x.
- **Frontend:** TypeScript with React and a lightweight component/style system. Keep the existing visual language initially; do not redesign while migrating behavior.
- **Backend:** Rust commands and events. Do not retain Python as a runtime dependency in the shipped application unless a temporary compatibility phase proves necessary.
- **Serialization:** `serde`/`serde_json`.
- **Async process execution:** Tokio-backed Tauri commands, with cancellation and timeout support.
- **Packaging:** Linux AppImage and Debian package first; add RPM only after the Linux release workflow is stable.

## 4. Migration Principles

1. Establish a behavior baseline before changing implementation.
2. Keep package-manager invocation in one backend service; the frontend must never construct shell commands.
3. Use argument arrays, not shell strings, and validate every user-selected path.
4. Preserve the existing history JSON shape and migrate settings conservatively.
5. Make backend commands and events typed and versionable.
6. Keep privileged operations explicit through `pkexec`; never bundle or store administrator credentials.
7. Prefer incremental vertical slices over a UI-only rewrite followed by a backend rewrite.
8. Keep the old Python application runnable until Tauri parity is demonstrated.

## 5. Proposed Repository Layout

```text
SnapWiz/
├── src/                         # TypeScript frontend
│   ├── app/
│   ├── components/
│   ├── features/
│   │   ├── install/
│   │   ├── uninstall/
│   │   ├── history/
│   │   └── settings/
│   ├── i18n/
│   ├── lib/tauri/
│   └── styles/
├── src-tauri/
│   ├── src/
│   │   ├── commands/
│   │   ├── package_service/
│   │   ├── history.rs
│   │   ├── settings.rs
│   │   ├── localization.rs
│   │   └── lib.rs
│   ├── capabilities/
│   ├── icons/
│   └── tauri.conf.json
├── locales/                     # Reused and adapted translation resources
├── test/                        # Existing Python regression tests during transition
├── tests/                       # Frontend and integration tests
├── package.json
├── tsconfig.json
└── vite.config.ts
```

Avoid moving the existing Python modules until their behavior has been captured and the replacement has been validated.

## 6. Phased Implementation Plan

### Phase 0 — Baseline and migration scaffolding

1. Confirm the target platform matrix, Tauri frontend framework, application identifier, and release formats.
2. Run the existing Python test suite and record the result.
3. Add a behavior checklist for:
   - Selecting one or many supported package files.
   - Dragging files into the window.
   - Viewing package metadata.
   - Integrity, signature, and checksum verification.
   - Single and batch installation.
   - Cancellation, timeout, failure, and retry behavior.
   - Uninstalling selected packages.
   - History search, status/type/date filters, clear, import, JSON export, and CSV export.
   - Theme and language changes.
   - Tray minimize/restore/quit and keyboard shortcuts.
4. Create the Tauri project alongside the Python application.
5. Add formatting, linting, type-checking, Rust checks, and CI placeholders.

**Exit criteria:** the old application still starts, its baseline tests pass, and the empty Tauri shell builds.

### Phase 1 — Backend contracts and persistence

1. Define shared TypeScript/Rust contracts:
   - `PackageFormat`, `PackageInfo`, `PackageEntry`.
   - `VerificationOptions`.
   - `InstallRequest`, `InstallProgress`, `InstallResult`.
   - `InstalledPackage`, `HistoryEntry`, `HistoryFilter`.
   - `AppSettings`.
2. Implement Tauri commands for:
   - `get_app_info`
   - `get_settings` / `save_settings`
   - `detect_package_managers`
   - `validate_package`
   - `get_package_info`
   - `get_installed_packages`
   - `get_history` / `clear_history`
   - `import_history` / `export_history`
3. Implement a versioned settings loader that accepts the existing settings JSON and supplies defaults for missing fields.
4. Preserve the existing history JSON entries (`timestamp`, `package`, `package_name`, `success`, `message`).
5. Centralize path resolution in Rust using Tauri's app/config directory APIs, with compatibility handling for `~/.snapwiz`.

**Exit criteria:** backend unit tests prove persistence compatibility and package validation/metadata behavior without a GUI.

### Phase 2 — Package operation service

**Status:** ✅ Complete. Manager detection, validation, metadata, checksum/integrity/signature verification, safe argument-array execution, timeout handling (300 s install / 30 s enumeration), progress events, installation history recording, uninstall, `get_installed_packages` (dpkg/rpm/snap/flatpak), structured `error_category` on `InstallResult` (`timeout`, `permission_denied`, `missing_manager`, `unsupported_format`, `verification_failed`, `process_failed`), and unit tests are all implemented. The command is exposed as `get_installed_packages_command` via `lib.rs`.

1. Port manager detection and supported-format rules from `src/package_handler.py`.
2. Implement safe subprocess execution:
   - Use `Command` with separate arguments.
   - Never invoke a shell.
   - Verify executable availability before use.
   - Apply operation-specific timeouts.
   - Capture stdout and stderr separately.
   - Return structured errors with an actionable category and original diagnostic.
3. Preserve command policy:
   - `.deb`: `apt`/`apt-get` or `dpkg`.
   - `.rpm`: `dnf`, `yum`, `zypper`, or `rpm`.
   - `.snap`: `snap` and daemon availability.
   - `.flatpak`: `flatpak`.
   - Privileged operations use `pkexec` where required.
4. Implement checksum verification using Rust hashing libraries and preserve supported algorithms.
5. Implement an asynchronous install job:
   - Emit the existing nine logical progress stages.
   - Emit output lines as diagnostic events.
   - Support cancellation between stages and while waiting on a child process.
   - Always write a history entry for success and failure.
6. Implement uninstall as a separate backend operation with per-package results, matching the current partial-success behavior.

**Exit criteria:** fixture-based and mocked-process tests cover success, unsupported files, missing managers, non-zero exits, timeout, cancellation, verification failure, and partial batch failure.

### Phase 3 — Frontend vertical slices

**Status:** In progress. The Install slice now supports native multi-file selection, package metadata loading, queue management, drag-and-drop paths, verification, installation progress events, diagnostics, and result/error handling. Uninstall, history, settings, and application-shell slices remain.

Implement one complete slice at a time:

1. **Install:** file picker, drag/drop, queue, remove/clear queue, metadata panel, verification options, progress, logs, confirmation, and result notification.
2. **Uninstall:** installed-package loading, search/type filter, multi-select, confirmation, execution, and result summary.
3. **History:** list rendering, search, status/type/date filters, refresh, clear, import, JSON export, and CSV export.
4. **Settings:** light/dark theme, language selection, verification defaults, checksum algorithm/input, and persistence.
5. **Application shell:** responsive sizing, tabs/navigation, shortcuts (`Ctrl+O`, `Ctrl+I`, `F5`, `Ctrl+Q`, `Ctrl+Tab`), tray menu, close-to-tray, notifications, and about information.

Use a single frontend state model for queue, active operation, progress, logs, history, settings, and errors. Do not duplicate operation state in individual components.

**Exit criteria:** each slice can be demonstrated independently against the real Rust commands, with no Python process required.

### Phase 4 — Localization, resources, and desktop integration

1. Preserve all six supported language codes and existing translation keys.
2. Convert PO/JSON resources to the selected frontend i18n format without changing user-visible meanings.
3. Add Tauri capabilities only for required operations:
   - Dialog open/save.
   - File drag/drop.
   - Notifications.
   - Tray.
   - App/config path access.
   - Backend command invocation.
4. Configure application icons, desktop entry metadata, version, license, and repository URL.
5. Ensure bundled resources resolve correctly in both development and packaged builds.

**Exit criteria:** packaged builds launch with translations, tray behavior, dialogs, and history/settings paths working on a clean Linux machine.

### Phase 5 — Verification, cutover, and cleanup

1. Run the behavior checklist against both implementations using the same package fixtures and history/settings fixtures.
2. Add end-to-end tests for the critical user flows.
3. Test on supported distributions and package-manager combinations.
4. Compare installation command selection and exit/error behavior against the Python implementation.
5. Update README, guides, development documentation, installation instructions, and troubleshooting content.
6. Replace `setup.py`, `requirements.txt`, `install.sh`, and `app.sh` only when equivalent Tauri build/install paths are available.
7. Keep a documented rollback path to the Python launcher for one release.
8. Remove unused PyQt/Python runtime packaging only after the release candidate passes parity checks.

**Exit criteria:** Tauri is the default launcher, release artifacts are reproducible, critical flows pass, and rollback instructions are tested.

## 7. Contract and Behavior Details to Preserve

### Install queue and progress

- Accept multiple files and de-duplicate queue entries.
- Display waiting, installing, and completed queue states.
- Preserve the nine logical progress milestones and detailed log messages.
- Prevent duplicate install actions while a job is active.
- Restore controls and record history after success or failure.
- Show actionable errors for invalid files, missing tools, verification failures, timeouts, and permission cancellation.

### Package safety

- Validate extension and file existence before execution.
- Do not trust a filename to provide package metadata.
- Do not interpolate paths into shell commands.
- Keep checksum and signature verification opt-in/default behavior compatible with current settings.
- Treat user cancellation of `pkexec` as a distinct, visible failure.

### History compatibility

- Read existing array-form history files.
- Export the current JSON envelope and CSV columns where practical.
- Preserve unknown fields during import/export when possible.
- Use atomic writes to avoid corrupting history after an interrupted operation.
- Define behavior for malformed history explicitly: show an error and offer a backup/reset path; do not silently replace it.

### Settings compatibility

- Preserve theme, language, verification, checksum, and checksum-type preferences.
- Add a schema version.
- Use safe defaults for missing or invalid values.
- Write settings atomically.

## 8. Testing Strategy

### Rust backend

- Unit tests for format detection, validation, settings migration, history filtering, CSV/JSON serialization, error mapping, and command construction.
- Mock process-runner tests for every package manager branch.
- Async tests for progress ordering, cancellation, timeout, and history logging.

### Frontend

- Component tests for queue state, filters, settings, progress, errors, and disabled states.
- Type-check and lint checks on every change.
- End-to-end tests for install, uninstall, history import/export, settings persistence, drag/drop, and tray-independent close behavior.

### Manual Linux matrix

| Platform capability | Required checks |
|---|---|
| Debian/Ubuntu | `.deb` metadata, install, uninstall, `pkexec`, history |
| Fedora/RHEL-like | `.rpm` metadata, install, uninstall, manager fallback |
| Snap-enabled host | `.snap` validation, daemon error, install |
| Flatpak-enabled host | `.flatpak` validation and install |
| Missing tools | Clear diagnostics and no crash |
| Permission denied/cancelled | No false success and correct history entry |

## 9. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Tauri frontend cannot directly perform privileged package operations | Keep all process execution in Rust and invoke `pkexec` explicitly. |
| Shell command behavior changes during the port | Record command, arguments, exit code, stdout, and stderr in tests; compare with the Python implementation. |
| History/settings become unreadable | Add compatibility fixtures, atomic writes, schema versioning, and backup-before-reset behavior. |
| Long-running installs freeze the UI | Use async Rust commands and event streams; never block the webview thread. |
| Tray/notification support differs by desktop environment | Test on representative Linux desktops and degrade visibly when a capability is unavailable. |
| Tauri capability configuration is too broad | Allow only the dialogs, paths, notifications, tray, and commands actually used. |
| Migration becomes a visual rewrite instead of a behavior migration | Require the Phase 0 checklist and parity sign-off before removing Python. |
| Existing test coverage misses package/runtime defects | Add mocked process tests and Linux integration tests before cutover. |

## 10. Definition of Done

- Tauri 2 application builds reproducibly for the supported Linux release formats.
- No Python or PyQt runtime is required for the default application.
- All four existing views and critical workflows are available.
- Existing history files and settings load without manual conversion.
- Package operations use validated argument lists, explicit timeouts, and structured errors.
- Progress, cancellation, tray, notifications, shortcuts, drag/drop, themes, and languages behave as documented.
- Backend, frontend, integration, and manual Linux validation pass.
- Documentation and launch/install scripts describe Tauri rather than PyQt/Python.
- The old Python implementation remains available for rollback for the first Tauri release.

## 11. Suggested Delivery Order

1. Baseline tests and behavior checklist.
2. Tauri shell and CI checks.
3. Rust persistence and package contracts.
4. Rust package operations with mocked tests.
5. Install vertical slice.
6. Uninstall vertical slice.
7. History and settings.
8. Tray, notifications, shortcuts, drag/drop, and localization.
9. Packaging and distribution validation.
10. Documentation, cutover, and Python cleanup.
