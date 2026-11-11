use crate::app_state::history_path;
use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HistoryEntry {
    pub timestamp: String,
    pub package: String,
    pub package_name: String,
    pub success: bool,
    pub message: String,
}

pub fn read_history() -> Result<Vec<HistoryEntry>, String> {
    let path = history_path()?;
    if !path.exists() {
        return Ok(Vec::new());
    }
    let content =
        fs::read_to_string(path).map_err(|error| format!("Unable to read history: {error}"))?;
    serde_json::from_str(&content).map_err(|error| format!("Invalid history JSON: {error}"))
}

pub fn clear_history() -> Result<(), String> {
    let path = history_path()?;
    if let Some(directory) = path.parent() {
        fs::create_dir_all(directory)
            .map_err(|error| format!("Unable to create history directory: {error}"))?;
    }
    fs::write(path, "[]").map_err(|error| format!("Unable to clear history: {error}"))
}

pub fn append_history(entry: HistoryEntry) -> Result<(), String> {
    let path = history_path()?;
    let directory = path
        .parent()
        .ok_or_else(|| "Unable to determine history directory".to_string())?;
    fs::create_dir_all(directory)
        .map_err(|error| format!("Unable to create history directory: {error}"))?;

    let mut history = read_history()?;
    history.push(entry);
    let content = serde_json::to_string_pretty(&history)
        .map_err(|error| format!("Unable to serialize history: {error}"))?;
    let temporary_path = path.with_extension("json.tmp");
    fs::write(&temporary_path, content)
        .map_err(|error| format!("Unable to write history: {error}"))?;
    fs::rename(&temporary_path, path)
        .map_err(|error| format!("Unable to replace history: {error}"))?;
    Ok(())
}
