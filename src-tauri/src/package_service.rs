use crate::{
    app_state::{PackageManagerStatus, validate_package_path},
    history::{HistoryEntry, append_history},
};
use serde::Serialize;
use std::{
    fs::File,
    io::Read,
    path::Path,
    process::{Child, Command, Output, Stdio},
    time::Duration,
};
use md5::Md5;
use sha2::{Digest, Sha256};
use tauri::{AppHandle, Emitter};
use wait_timeout::ChildExt;

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PackageInfo {
    pub path: String,
    pub file_name: String,
    pub format: String,
    pub size_bytes: u64,
    pub metadata: String,
}

#[derive(Debug, Serialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct InstallProgress {
    pub package_path: String,
    pub stage: String,
    pub progress: u8,
    pub message: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct InstallResult {
    pub success: bool,
    pub message: String,
}

#[derive(Debug, serde::Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct VerificationRequest {
    pub package_path: String,
    pub checksum: Option<String>,
    pub checksum_type: Option<String>,
    pub check_signature: bool,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct VerificationDetails {
    pub file_exists: bool,
    pub file_size: u64,
    pub checksum_match: Option<bool>,
    pub signature_valid: Option<bool>,
    pub integrity_ok: bool,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct VerificationResult {
    pub success: bool,
    pub message: String,
    pub details: VerificationDetails,
}

fn command_exists(command: &str) -> bool {
    #[cfg(target_os = "windows")]
    let lookup = "where";
    #[cfg(not(target_os = "windows"))]
    let lookup = "which";

    Command::new(lookup)
        .arg(command)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|status| status.success())
        .unwrap_or(false)
}

fn calculate_checksum(path: &Path, checksum_type: &str) -> Result<String, String> {
    let mut file = File::open(path).map_err(|error| format!("Unable to read package: {error}"))?;
    let mut buffer = [0_u8; 8192];
    match checksum_type.to_ascii_lowercase().as_str() {
        "sha256" => {
            let mut hasher = Sha256::new();
            loop {
                let bytes_read = file
                    .read(&mut buffer)
                    .map_err(|error| format!("Unable to calculate checksum: {error}"))?;
                if bytes_read == 0 {
                    break;
                }
                hasher.update(&buffer[..bytes_read]);
            }
            Ok(format!("{:x}", hasher.finalize()))
        }
        "md5" => {
            let mut hasher = Md5::new();
            loop {
                let bytes_read = file
                    .read(&mut buffer)
                    .map_err(|error| format!("Unable to calculate checksum: {error}"))?;
                if bytes_read == 0 {
                    break;
                }
                hasher.update(&buffer[..bytes_read]);
            }
            Ok(format!("{:x}", hasher.finalize()))
        }
        unsupported => Err(format!(
            "Unsupported checksum type: {unsupported}. Use sha256 or md5."
        )),
    }
}

fn integrity_check(format: &str, package_path: &str) -> Result<(), String> {
    let (program, arguments): (&str, Vec<&str>) = match format {
        ".deb" => ("dpkg-deb", vec!["--info", package_path]),
        ".rpm" => ("rpm", vec!["-qp", package_path]),
        _ => return Ok(()),
    };
    if !command_exists(program) {
        return Ok(());
    }
    let output = Command::new(program)
        .args(arguments)
        .output()
        .map_err(|error| format!("Unable to check package integrity: {error}"))?;
    if output.status.success() {
        Ok(())
    } else {
        Err("Package appears to be corrupted or invalid".into())
    }
}

fn signature_check(format: &str, package_path: &str) -> Result<(), String> {
    let (program, arguments): (&str, Vec<String>) = match format {
        ".deb" => {
            let signature_path = ["asc", "sig"]
                .iter()
                .map(|extension| format!("{package_path}.{extension}"))
                .find(|candidate| Path::new(candidate).is_file())
                .ok_or_else(|| "No signature file found (.asc or .sig required)".to_string())?;
            ("gpg", vec!["--verify".into(), signature_path, package_path.into()])
        }
        ".rpm" => ("rpm", vec!["--checksig".into(), package_path.into()]),
        _ => return Err("Unsupported package type for signature verification".into()),
    };
    if !command_exists(program) {
        return Err(format!("{program} is not installed"));
    }
    let output = Command::new(program)
        .args(arguments)
        .output()
        .map_err(|error| format!("Unable to verify package signature: {error}"))?;
    let diagnostics = String::from_utf8_lossy(&output.stderr);
    let stdout = String::from_utf8_lossy(&output.stdout);
    if output.status.success() && (format != ".rpm" || stdout.contains("OK")) {
        Ok(())
    } else {
        Err(if diagnostics.trim().is_empty() {
            stdout.trim().to_string()
        } else {
            diagnostics.trim().to_string()
        })
    }
}

pub fn verify_package(request: VerificationRequest) -> VerificationResult {
    let path = Path::new(&request.package_path);
    let mut details = VerificationDetails {
        file_exists: path.is_file(),
        file_size: 0,
        checksum_match: None,
        signature_valid: None,
        integrity_ok: false,
    };
    if !details.file_exists {
        return VerificationResult {
            success: false,
            message: "Package file not found".into(),
            details,
        };
    }
    let format = match validate_package_path(path) {
        Ok(format) => format,
        Err(message) => {
            return VerificationResult {
                success: false,
                message,
                details,
            }
        }
    };
    details.file_size = match std::fs::metadata(path) {
        Ok(metadata) => metadata.len(),
        Err(error) => {
            return VerificationResult {
                success: false,
                message: format!("Unable to read package: {error}"),
                details,
            }
        }
    };
    if details.file_size < 1024 {
        return VerificationResult {
            success: false,
            message: format!(
                "Package file too small ({} bytes). It may be corrupted.",
                details.file_size
            ),
            details,
        };
    }
    if let Some(expected) = request.checksum.as_deref().filter(|value| !value.trim().is_empty()) {
        let checksum_type = request.checksum_type.as_deref().unwrap_or("sha256");
        match calculate_checksum(path, checksum_type) {
            Ok(actual) if actual.eq_ignore_ascii_case(expected.trim()) => {
                details.checksum_match = Some(true);
            }
            Ok(actual) => {
                details.checksum_match = Some(false);
                return VerificationResult {
                    success: false,
                    message: format!(
                        "{} checksum mismatch!\nExpected: {}\nGot: {}",
                        checksum_type.to_ascii_uppercase(),
                        expected,
                        actual
                    ),
                    details,
                };
            }
            Err(message) => {
                return VerificationResult {
                    success: false,
                    message,
                    details,
                }
            }
        }
    }
    if request.check_signature {
        match signature_check(&format, &request.package_path) {
            Ok(()) => details.signature_valid = Some(true),
            Err(message) => {
                details.signature_valid = Some(false);
                return VerificationResult {
                    success: false,
                    message: format!("Package signature verification failed: {message}"),
                    details,
                };
            }
        }
    }
    if let Err(message) = integrity_check(&format, &request.package_path) {
        return VerificationResult {
            success: false,
            message: format!("Package integrity check failed: {message}"),
            details,
        };
    }
    details.integrity_ok = true;
    VerificationResult {
        success: true,
        message: "Package verification successful".into(),
        details,
    }
}

fn emit_progress(app: &AppHandle, package_path: &str, stage: &str, progress: u8, message: &str) {
    let _ = app.emit(
        "installation-progress",
        InstallProgress {
            package_path: package_path.to_string(),
            stage: stage.to_string(),
            progress,
            message: message.to_string(),
        },
    );
}

fn run_with_timeout(mut child: Child) -> Result<Output, String> {
    let completed = child
        .wait_timeout(Duration::from_secs(300))
        .map_err(|error| format!("Unable to wait for package manager: {error}"))?;
    if completed.is_none() {
        child
            .kill()
            .map_err(|error| format!("Unable to stop timed-out package manager: {error}"))?;
        let _ = child.wait();
        return Err("Installation timed out after 300 seconds".into());
    }
    child
        .wait_with_output()
        .map_err(|error| format!("Unable to collect package manager output: {error}"))
}

fn installation_command(format: &str, package_path: &str) -> Result<(String, Vec<String>), String> {
    let privileged = command_exists("pkexec");
    let command = |program: &str, arguments: Vec<String>| {
        if privileged {
            Ok(("pkexec".to_string(), {
                let mut prefixed = vec![program.to_string()];
                prefixed.extend(arguments);
                prefixed
            }))
        } else {
            Ok((program.to_string(), arguments))
        }
    };

    match format {
        ".deb" if command_exists("apt") => command(
            "apt",
            vec!["install".into(), "-y".into(), package_path.into()],
        ),
        ".deb" if command_exists("dpkg") => command("dpkg", vec!["-i".into(), package_path.into()]),
        ".rpm" if command_exists("dnf") => command(
            "dnf",
            vec!["install".into(), "-y".into(), package_path.into()],
        ),
        ".rpm" if command_exists("yum") => command(
            "yum",
            vec!["install".into(), "-y".into(), package_path.into()],
        ),
        ".rpm" if command_exists("zypper") => command(
            "zypper",
            vec!["install".into(), "-y".into(), package_path.into()],
        ),
        ".rpm" if command_exists("rpm") => command("rpm", vec!["-ivh".into(), package_path.into()]),
        ".snap" if command_exists("snap") => command(
            "snap",
            vec!["install".into(), "--dangerous".into(), package_path.into()],
        ),
        ".flatpak" if command_exists("flatpak") => Ok((
            "flatpak".into(),
            vec![
                "install".into(),
                "-y".into(),
                "--bundle".into(),
                package_path.into(),
            ],
        )),
        _ => Err(format!(
            "No suitable package manager found for {format} files"
        )),
    }
}

pub async fn install_package(
    app: AppHandle,
    package_path: String,
) -> Result<InstallResult, String> {
    tauri::async_runtime::spawn_blocking(move || {
        let path = Path::new(&package_path);
        let format = validate_package_path(path)?;
        emit_progress(
            &app,
            &package_path,
            "validation",
            15,
            "Package validation passed",
        );
        emit_progress(
            &app,
            &package_path,
            "metadata",
            40,
            "Reading package metadata",
        );

        let (program, arguments) = installation_command(&format, &package_path)?;
        emit_progress(
            &app,
            &package_path,
            "installation",
            60,
            "Installing package",
        );
        let child = Command::new(&program)
            .args(&arguments)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|error| format!("Unable to start {program}: {error}"))?;
        let output = run_with_timeout(child)?;
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        let diagnostics = if stderr.trim().is_empty() {
            stdout.trim().to_string()
        } else {
            stderr.trim().to_string()
        };
        let success = output.status.success();
        let message = if success {
            format!("Package installed successfully!\n\n{diagnostics}")
        } else {
            format!("Installation failed:\n{diagnostics}")
        };

        let file_name = path
            .file_name()
            .and_then(|value| value.to_str())
            .unwrap_or(&package_path)
            .to_string();
        append_history(HistoryEntry {
            timestamp: chrono::Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
            package: package_path.clone(),
            package_name: file_name,
            success,
            message: message.clone(),
        })?;
        emit_progress(
            &app,
            &package_path,
            if success { "completed" } else { "failed" },
            if success { 100 } else { 60 },
            &message,
        );
        Ok(InstallResult { success, message })
    })
    .await
    .map_err(|error| format!("Installation task failed: {error}"))?
}

pub fn detect_managers() -> PackageManagerStatus {
    let candidates = [
        "apt", "apt-get", "dpkg", "dnf", "yum", "zypper", "rpm", "snap", "flatpak",
    ];
    PackageManagerStatus {
        managers: candidates
            .into_iter()
            .filter(|command| command_exists(command))
            .map(str::to_string)
            .collect(),
    }
}

pub fn package_info(package_path: &str) -> Result<PackageInfo, String> {
    let path = Path::new(package_path);
    let format = validate_package_path(path)?;
    let metadata =
        std::fs::metadata(path).map_err(|error| format!("Unable to read package: {error}"))?;
    let file_name = path
        .file_name()
        .and_then(|value| value.to_str())
        .ok_or_else(|| "Package path is not valid UTF-8".to_string())?
        .to_string();

    let command = match format.as_str() {
        ".deb" => Some(("dpkg-deb", vec!["-I", package_path])),
        ".rpm" => Some(("rpm", vec!["-qip", package_path])),
        _ => None,
    };
    let metadata_text = command
        .filter(|(program, _)| command_exists(program))
        .and_then(|(program, arguments)| {
            Command::new(program)
                .args(arguments)
                .output()
                .ok()
                .filter(|output| output.status.success())
                .map(|output| String::from_utf8_lossy(&output.stdout).trim().to_string())
        })
        .unwrap_or_else(|| format!("Filename: {file_name}\nSize: {} bytes", metadata.len()));

    Ok(PackageInfo {
        path: package_path.to_string(),
        file_name,
        format,
        size_bytes: metadata.len(),
        metadata: metadata_text,
    })
}
