mod app_state;
mod history;
mod package_service;

use app_state::{
    AppInfo, AppSettings, PackageManagerStatus, read_settings, write_settings,
};
use history::{HistoryEntry, clear_history, read_history};
use package_service::{
    PackageInfo, UninstallRequest, VerificationRequest, VerificationResult, detect_managers,
    install_package, package_info, uninstall_package, verify_package,
};

#[tauri::command]
fn get_app_info() -> AppInfo {
    AppInfo {
        name: "SnapWiz",
        version: "1.4.1",
        supported_formats: [".deb", ".rpm", ".snap", ".flatpak"],
    }
}

#[tauri::command]
fn get_settings() -> Result<AppSettings, String> {
    read_settings()
}

#[tauri::command]
fn save_settings(settings: AppSettings) -> Result<(), String> {
    write_settings(&settings)
}

#[tauri::command]
fn detect_package_managers() -> PackageManagerStatus {
    detect_managers()
}

#[tauri::command]
fn validate_package(package_path: String) -> Result<bool, String> {
    app_state::validate_package_path(std::path::Path::new(&package_path)).map(|_| true)
}

#[tauri::command]
fn get_package_info(package_path: String) -> Result<PackageInfo, String> {
    package_info(&package_path)
}

#[tauri::command]
fn get_history() -> Result<Vec<HistoryEntry>, String> {
    read_history()
}

#[tauri::command]
fn clear_installation_history() -> Result<(), String> {
    clear_history()
}

#[tauri::command]
async fn install_package_command(
    app: tauri::AppHandle,
    package_path: String,
) -> Result<package_service::InstallResult, String> {
    install_package(app, package_path).await
}

#[tauri::command]
async fn uninstall_package_command(
    app: tauri::AppHandle,
    request: UninstallRequest,
) -> Result<package_service::InstallResult, String> {
    uninstall_package(app, request).await
}

#[tauri::command]
async fn verify_package_command(
    request: VerificationRequest,
) -> Result<VerificationResult, String> {
    tauri::async_runtime::spawn_blocking(move || Ok(verify_package(request)))
        .await
        .map_err(|error| format!("Verification task failed: {error}"))?
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            get_app_info,
            get_settings,
            save_settings,
            detect_package_managers,
            validate_package,
            get_package_info,
            get_history,
            clear_installation_history,
            install_package_command,
            uninstall_package_command,
            verify_package_command
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
