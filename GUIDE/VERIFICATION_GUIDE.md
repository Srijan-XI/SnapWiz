# 🔐 Package Verification Feature - SnapWiz

**Feature Status**: ✅ **IMPLEMENTED** (v1.3)  
**Date Added**: 2026-02-08

---

## Overview

The Package Verification feature adds comprehensive security checks to SnapWiz, ensuring that packages are valid, intact, and authentic before they are installed on your system. This protects you from corrupted downloads, malicious tampering, and invalid package files.

---

## Features

### ✅ **Integrity Checking**
- Verifies package file structure
- Detects corrupted downloads
- Checks if file is a valid .deb/.rpm archive
- Blocks installation of empty or broken files

### 🔏 **GPG Signature Verification**
- Verifies cryptographic signatures
- Supports .asc and .sig signature files (Debian)
- Supports RPM internal signatures (Fedora/RHEL)
- Ensures package authenticity

### 🔢 **Checksum Verification**
- Manual checksum validation
- Supports **SHA256** and **MD5**
- Compare against official hashes
- Detects even single-bit errors

### 🛡️ **Safety Defaults**
- Integrity checks enabled by default
- Blocks installation on verification failure
- Detailed error reporting

---

## How to Use

### Configuring Verification Settings

1. **Open SnapWiz**
2. Go to **⚙️ Settings** tab
3. Locate **🔐 Package Verification** section

**Available Options**:
- **✓ Always verify package integrity**: (Default: On) Performs basic structural checks.
- **✓ Verify GPG signatures**: (Default: Off) Checks for cryptographic signatures. Requires .asc/.sig files for .deb or signed RPMs.
- **Checksum**: (Optional) Enter a known SHA256 or MD5 hash to verify against.

### Verifying a Package (Single Install)

1. **Download** a package and its checksum (from official website).
2. Open SnapWiz **Settings**.
3. Select **Checksum Type** (SHA256 or MD5).
4. **Paste** the official checksum into the "Checksum" field.
5. Go to **Install Package** tab.
6. Select your package.
7. Click **Install**.
8. SnapWiz will verify the checksum matches BEFORE installing.
   - If match: installation proceeds ✅
   - If mismatch: installation blocked with error ❌

### Verifying Batch Installations

**Note**: Manual checksum verification is disabled for batch installation (as you can't enter different checksums for multiple files at once). 

However, **Integrity Checks** and **GPG Signature Verification** (if enabled) run for *every* package in the queue automatically.

---

## Verification Process

When you click Install, the following checks occur in order:

1. **File Existence**: Checks if file still exists.
2. **File Size**: Checks for suspicious sizes (< 1KB).
3. **Checksum**: (If provided) Calculates file hash and compares with input.
4. **GPG Signature**: (If enabled) Check for .asc/.sig file and runs `gpg --verify`, or `rpm --checksig`.
5. **Integrity**: Runs `dpkg-deb --info` or `rpm -qp` to verify archive structure.

If **ANY** check fails, the installation is **ABORTED** immediately.

---

## User Interface

### Settings Tab

```
┌──────────────────────────────────────────────┐
│ 🔐 Package Verification                      │
│ Enable verification checks before installation:│
│                                              │
│ [x] Always verify package integrity          │
│ [ ] Verify GPG signatures (if available)     │
│                                              │
│ Optional: Verify checksum (SHA256/MD5):      │
│ Leave blank to skip checksum verification    │
│ Type: [SHA256 ▼]                             │
│ Checksum: [______________________________]   │
└──────────────────────────────────────────────┘
```

### Installation Progress

```
📋 Initializing installation process...
Starting installation...

🔍 Validating package file...
Checking package type...

🔐 Verifying package security...  <-- NEW STEP
Checking package integrity and signatures...

✅ Package verification passed   <-- SUCCESS
```

---

## Troubleshooting

### Checksum Mismatch Error

**Error**: `SHA256 checksum mismatch! Expected: abc... Got: xyz...`

**Causes**:
- Corrupted download
- Outdated checksum (new version downloaded)
- Wrong checksum type selected (MD5 vs SHA256)
- Man-in-the-middle attack (rare)

**Solution**:
- Re-download the package
- Double check the checksum from the source website
- Ensure you selected correct algorithm (SHA256/MD5)

### GPG Signature Verification Failed

**Error**: `GPG signature verification failed: No public key`

**Causes**:
- Missing public key for the package signer
- Missing detached signature file (.asc/.sig) for .deb
- Corrupted signature

**Solution**:
- Import the developer's public key (`gpg --import key.asc`)
- Ensure .asc/.sig file is in same folder as .deb
- Disable GPG verification in Settings if not needed

### Package Integrity Check Failed

**Error**: `Package appears to be corrupted or invalid`

**Causes**:
- Incomplete download
- Not a valid .deb/.rpm file
- Disk error

**Solution**:
- Re-download the file
- Try installing via terminal to see detailed errors

---

## Technical Details

### Checksum Calculation
- Uses Python `hashlib`
- Streams file in 8KB chunks (memory efficient)
- Supports large files (> 4GB)

### GPG Verification commands
- **Debian**: `gpg --verify package.deb.asc package.deb`
- **RPM**: `rpm --checksig package.rpm`

### Integrity Check commands
- **Debian**: `dpkg-deb --info package.deb` (checks if metadata is readable)
- **RPM**: `rpm -qp package.rpm` (queries package info)

---

## Best Practices

### ✅ **DO**
1. **Always** keep integrity checks enabled.
2. **Use checksums** for sensitive software (wallets, security tools).
3. **Verify signatures** if the vendor provides them.

### ❌ **DON'T**
1. **Don't ignore** verification failures. They usually mean something is wrong.
2. **Don't disable** integrity checks unless debugging.
3. **Don't use** MD5 if SHA256 is available (SHA256 is more secure).

---

## Changelog

### v1.3 (2026-02-08)
- ✨ Added package verification system
- ✅ SHA256/MD5 manual checksum verification
- ✅ GPG signature support
- ✅ Automated integrity checks
- ✅ Verification settings UI
- ✅ Integration with Install threads

---

**Last Updated**: 2026-02-08  
**Feature Version**: 1.3  
**Status**: Production Ready ✅
