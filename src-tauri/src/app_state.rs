use serde::{Deserialize, Serialize};
use std::{
    fs,
    path::{Path, PathBuf},
};

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct AppInfo {
    pub name: &'static str,
    pub version: &'static str,
    pub supported_formats: [&'static str; 4],
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AppSettings {
    pub theme: String,
    pub language: String,
    pub verify_integrity: bool,
    pub verify_signature: bool,
    pub checksum_type: String,
}

impl Default for AppSettings {
    fn default() -> Self {
        Self {
            theme: "Light".into(),
            language: "en".into(),
            verify_integrity: true,
            verify_signature: false,
            checksum_type: "sha256".into(),
        }
    }
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PackageManagerStatus {
    pub managers: Vec<String>,
}

pub fn config_dir() -> Result<PathBuf, String> {
    let home = std::env::var_os("HOME")
        .or_else(|| std::env::var_os("USERPROFILE"))
        .ok_or_else(|| "Unable to determine the user home directory".to_string())?;
    Ok(PathBuf::from(home).join(".snapwiz"))
}

pub fn settings_path() -> Result<PathBuf, String> {
    Ok(config_dir()?.join("settings.json"))
}

pub fn history_path() -> Result<PathBuf, String> {
    Ok(config_dir()?.join("installation_history.json"))
}

pub fn read_settings() -> Result<AppSettings, String> {
    let path = settings_path()?;
    if !path.exists() {
        return Ok(AppSettings::default());
    }

    let content =
        fs::read_to_string(&path).map_err(|error| format!("Unable to read settings: {error}"))?;
    let value: serde_json::Value = serde_json::from_str(&content)
        .map_err(|error| format!("Invalid settings JSON: {error}"))?;
    let mut settings = AppSettings::default();
    if let Some(object) = value.as_object() {
        if let Some(value) = object.get("theme").and_then(|v| v.as_str()) {
            settings.theme = value.to_string();
        }
        if let Some(value) = object.get("language").and_then(|v| v.as_str()) {
            settings.language = value.to_string();
        }
        if let Some(value) = object.get("verify_integrity").and_then(|v| v.as_bool()) {
            settings.verify_integrity = value;
        }
        if let Some(value) = object.get("verify_signature").and_then(|v| v.as_bool()) {
            settings.verify_signature = value;
        }
        if let Some(value) = object.get("checksum_type").and_then(|v| v.as_str()) {
            settings.checksum_type = value.to_string();
        }
    }
    Ok(settings)
}

pub fn write_settings(settings: &AppSettings) -> Result<(), String> {
    let directory = config_dir()?;
    fs::create_dir_all(&directory)
        .map_err(|error| format!("Unable to create config directory: {error}"))?;
    let path = settings_path()?;
    let temporary_path = path.with_extension("json.tmp");
    let content = serde_json::to_string_pretty(settings)
        .map_err(|error| format!("Unable to serialize settings: {error}"))?;
    fs::write(&temporary_path, content)
        .map_err(|error| format!("Unable to write settings: {error}"))?;
    fs::rename(&temporary_path, path)
        .map_err(|error| format!("Unable to replace settings: {error}"))?;
    Ok(())
}

pub fn validate_package_path(path: &Path) -> Result<String, String> {
    if !path.is_file() {
        return Err("Package file not found".into());
    }
    let extension = path
        .extension()
        .and_then(|value| value.to_str())
        .map(|value| format!(".{}", value.to_ascii_lowercase()))
        .ok_or_else(|| "Package file has no supported extension".to_string())?;
    if [".deb", ".rpm", ".snap", ".flatpak"].contains(&extension.as_str()) {
        Ok(extension)
    } else {
        Err("Unsupported package format".into())
    }
}
