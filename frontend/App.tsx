import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { open } from "@tauri-apps/plugin-dialog";
import { useCallback, useEffect, useState } from "react";
import "./App.css";

// ─── Types ───────────────────────────────────────────────────────────────────

type AppInfo = {
  name: string;
  version: string;
  supportedFormats: string[];
};

type PackageInfo = {
  path: string;
  fileName: string;
  format: string;
  sizeBytes: number;
  metadata: string;
};

type InstalledPackage = {
  name: string;
  version: string;
  format: string;
};

type HistoryEntry = {
  timestamp: string;
  package: string;
  packageName: string;
  success: boolean;
  message: string;
};

type VerificationResult = {
  success: boolean;
  message: string;
  details: {
    fileExists: boolean;
    fileSize: number;
    checksumMatch: boolean | null;
    signatureValid: boolean | null;
    integrityOk: boolean;
  };
};

type InstallProgress = {
  packagePath: string;
  stage: string;
  progress: number;
  message: string;
};

type AppSettings = {
  theme: string;
  language: string;
  verifyIntegrity: boolean;
  verifySignature: boolean;
  checksumType: string;
};

// ─── Root App ────────────────────────────────────────────────────────────────

function App() {
  const [activeTab, setActiveTab] = useState("Install");
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Install tab state (lifted so progress events work from any tab)
  const [queue, setQueue] = useState<PackageInfo[]>([]);
  const [selectedPackage, setSelectedPackage] = useState<PackageInfo | null>(null);
  const [progress, setProgress] = useState<InstallProgress | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [installing, setInstalling] = useState(false);
  const [settings, setSettings] = useState<AppSettings>({
    theme: "Light",
    language: "en",
    verifyIntegrity: true,
    verifySignature: false,
    checksumType: "sha256",
  });

  useEffect(() => {
    invoke<AppInfo>("get_app_info")
      .then(setAppInfo)
      .catch((reason: unknown) => setError(String(reason)));
    invoke<AppSettings>("get_settings")
      .then(setSettings)
      .catch((reason: unknown) => setError(String(reason)));

    let unlisten: (() => void) | undefined;
    listen<InstallProgress>("installation-progress", (event) => {
      setProgress(event.payload);
      setLogs((current) => [...current, event.payload.message]);
    }).then((cleanup) => {
      unlisten = cleanup;
    }).catch((reason: unknown) => setError(String(reason)));

    return () => unlisten?.();
  }, []);

  const addPackages = useCallback(async (paths: string[]) => {
    setError(null);
    const newPackages: PackageInfo[] = [];
    for (const path of paths) {
      if (
        queue.some((item) => item.path === path) ||
        newPackages.some((item) => item.path === path)
      ) {
        continue;
      }
      try {
        const info = await invoke<PackageInfo>("get_package_info", { packagePath: path });
        newPackages.push(info);
      } catch (reason) {
        setError(`${path}: ${String(reason)}`);
      }
    }
    if (newPackages.length > 0) {
      setQueue((current) => [...current, ...newPackages]);
      setSelectedPackage((current) => current ?? newPackages[0]);
    }
  }, [queue]);

  useEffect(() => {
    let unlisten: (() => void) | undefined;
    listen<{ paths: string[] }>("tauri://drag-drop", (event) => {
      void addPackages(event.payload.paths);
    }).then((cleanup) => {
      unlisten = cleanup;
    }).catch((reason: unknown) => setError(String(reason)));
    return () => unlisten?.();
  }, [addPackages]);

  const choosePackages = async () => {
    const selected = await open({
      multiple: true,
      directory: false,
      filters: [{ name: "Linux packages", extensions: ["deb", "rpm", "snap", "flatpak"] }],
    });
    if (selected) {
      await addPackages(Array.isArray(selected) ? selected : [selected]);
    }
  };

  const verifyAndInstall = async () => {
    if (!selectedPackage || installing) return;
    setError(null);
    setLogs([]);
    setProgress(null);
    setInstalling(true);
    try {
      const verification = await invoke<VerificationResult>("verify_package_command", {
        request: {
          packagePath: selectedPackage.path,
          checksum: null,
          checksumType: settings.checksumType,
          checkSignature: settings.verifySignature,
        },
      });
      if (!verification.success) throw new Error(verification.message);
      const result = await invoke<{ success: boolean; message: string }>("install_package_command", {
        packagePath: selectedPackage.path,
      });
      if (!result.success) throw new Error(result.message);
    } catch (reason) {
      setError(String(reason));
    } finally {
      setInstalling(false);
    }
  };

  const removeSelected = () => {
    if (!selectedPackage) return;
    const remaining = queue.filter((item) => item.path !== selectedPackage.path);
    setQueue(remaining);
    setSelectedPackage(remaining[0] ?? null);
  };

  const handleDrop = async (event: React.DragEvent<HTMLElement>) => {
    event.preventDefault();
    const paths = Array.from(event.dataTransfer.files)
      .map((file) => (file as File & { path?: string }).path)
      .filter((path): path is string => Boolean(path));
    if (paths.length > 0) await addPackages(paths);
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">SnapWiz</p>
          <h1>The magical way to install packages</h1>
          <p className="subtitle">A Tauri migration shell backed by the existing package workflows.</p>
        </div>
        <span className="version">{appInfo ? `v${appInfo.version}` : "Loading..."}</span>
      </header>

      <nav className="tabs" aria-label="Application sections">
        {["Install", "Uninstall", "History", "Settings"].map((tab) => (
          <button
            className={activeTab === tab ? "tab active" : "tab"}
            key={tab}
            onClick={() => setActiveTab(tab)}
            type="button"
          >
            {tab}
          </button>
        ))}
      </nav>

      <section className="content-card">
        <h2>{activeTab}</h2>

        {activeTab === "Install" && (
          <>
            <p>Select package files or drop them into the queue.</p>
            <div className="drop-zone" onDragOver={(e) => e.preventDefault()} onDrop={handleDrop}>
              <button className="primary-button" type="button" onClick={choosePackages} disabled={installing}>
                Choose package files
              </button>
              <span>or drag and drop supported packages here</span>
            </div>
            {queue.length > 0 && (
              <div className="install-layout">
                <div>
                  <h3>Install queue</h3>
                  <ul className="package-list">
                    {queue.map((item) => (
                      <li key={item.path}>
                        <button
                          className={selectedPackage?.path === item.path ? "package-item selected" : "package-item"}
                          type="button"
                          onClick={() => setSelectedPackage(item)}
                        >
                          <strong>{item.fileName}</strong>
                          <small>{item.format} · {(item.sizeBytes / 1024).toFixed(1)} KB</small>
                        </button>
                      </li>
                    ))}
                  </ul>
                  <button type="button" onClick={removeSelected} disabled={!selectedPackage || installing}>
                    Remove selected
                  </button>
                  <button type="button" onClick={() => { setQueue([]); setSelectedPackage(null); }} disabled={installing}>
                    Clear queue
                  </button>
                </div>
                <div className="package-details">
                  <h3>{selectedPackage?.fileName}</h3>
                  <pre>{selectedPackage?.metadata}</pre>
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.verifySignature}
                      onChange={(e) => setSettings({ ...settings, verifySignature: e.target.checked })}
                    />
                    {" "}Verify signature
                  </label>
                  <button
                    className="primary-button"
                    type="button"
                    onClick={verifyAndInstall}
                    disabled={!selectedPackage || installing}
                  >
                    {installing ? "Installing..." : "Verify and install"}
                  </button>
                  {progress && (
                    <div className="progress-area">
                      <progress max="100" value={progress.progress} />
                      <span>{progress.stage}: {progress.progress}%</span>
                    </div>
                  )}
                  {logs.length > 0 && <pre className="logs">{logs.join("\n")}</pre>}
                </div>
              </div>
            )}
            <p className="formats">
              Supported formats: {appInfo?.supportedFormats.join(", ") ?? "Loading..."}
            </p>
          </>
        )}

        {activeTab === "Uninstall" && <UninstallTab setError={setError} />}
        {activeTab === "History" && <HistoryTab setError={setError} />}
        {activeTab === "Settings" && (
          <SettingsTab settings={settings} setSettings={setSettings} setError={setError} />
        )}

        {error && <p className="error">Error: {error}</p>}
      </section>
    </main>
  );
}

// ─── Uninstall Tab ───────────────────────────────────────────────────────────

function UninstallTab({
  setError,
}: {
  setError: React.Dispatch<React.SetStateAction<string | null>>;
}) {
  const [packages, setPackages] = useState<InstalledPackage[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [formatFilter, setFormatFilter] = useState("all");
  const [selected, setSelected] = useState<InstalledPackage | null>(null);
  const [uninstalling, setUninstalling] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadPackages = async () => {
    setLoading(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const pkgs = await invoke<InstalledPackage[]>("get_installed_packages_command");
      setPackages(pkgs);
    } catch (reason) {
      setError(String(reason));
    } finally {
      setLoading(false);
    }
  };

  const doUninstall = async () => {
    if (!selected || uninstalling) return;
    setError(null);
    setSuccessMsg(null);
    setUninstalling(true);
    try {
      const res = await invoke<{ success: boolean; message: string }>("uninstall_package_command", {
        request: { packageName: selected.name, format: selected.format },
      });
      if (!res.success) throw new Error(res.message);
      setSuccessMsg(`✓ ${selected.name} uninstalled successfully.`);
      setPackages((prev) =>
        prev.filter((p) => !(p.name === selected.name && p.format === selected.format)),
      );
      setSelected(null);
    } catch (reason) {
      setError(String(reason));
    } finally {
      setUninstalling(false);
    }
  };

  const filtered = packages.filter(
    (p) =>
      (formatFilter === "all" || p.format === formatFilter) &&
      p.name.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <>
      <p>Search installed packages to remove.</p>
      <div style={{ display: "flex", gap: 8, marginBottom: 12, flexWrap: "wrap" }}>
        <input
          style={{ flex: 1, minWidth: 160 }}
          placeholder="Search packages…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={formatFilter} onChange={(e) => setFormatFilter(e.target.value)}>
          <option value="all">All formats</option>
          <option value=".deb">.deb</option>
          <option value=".rpm">.rpm</option>
          <option value=".snap">.snap</option>
          <option value=".flatpak">.flatpak</option>
        </select>
        <button type="button" onClick={loadPackages} disabled={loading}>
          {loading ? "Loading…" : packages.length === 0 ? "Load packages" : "Refresh"}
        </button>
      </div>

      {successMsg && (
        <p style={{ color: "#027a48", fontWeight: 600, marginBottom: 12 }}>{successMsg}</p>
      )}

      <div className="install-layout">
        <ul className="package-list">
          {filtered.length === 0 ? (
            <li>
              <p style={{ color: "#667085" }}>
                {packages.length === 0
                  ? "Click \"Load packages\" to enumerate installed packages."
                  : "No packages match the current filter."}
              </p>
            </li>
          ) : (
            filtered.map((pkg) => (
              <li key={`${pkg.format}-${pkg.name}`}>
                <button
                  className={
                    selected?.name === pkg.name && selected?.format === pkg.format
                      ? "package-item selected"
                      : "package-item"
                  }
                  type="button"
                  onClick={() => setSelected(pkg)}
                >
                  <strong>{pkg.name}</strong>
                  <small>
                    {pkg.format}
                    {pkg.version ? ` · ${pkg.version}` : ""}
                  </small>
                </button>
              </li>
            ))
          )}
        </ul>

        <div className="package-details">
          {selected ? (
            <>
              <h3>{selected.name}</h3>
              <p>
                <strong>Version:</strong> {selected.version || "—"}
              </p>
              <p>
                <strong>Format:</strong> {selected.format}
              </p>
              <button
                className="primary-button"
                style={{ background: "#b42318" }}
                type="button"
                onClick={doUninstall}
                disabled={uninstalling}
              >
                {uninstalling ? "Uninstalling…" : `Uninstall ${selected.name}`}
              </button>
            </>
          ) : (
            <p style={{ color: "#667085" }}>Select a package from the list to uninstall it.</p>
          )}
        </div>
      </div>
    </>
  );
}

// ─── History Tab ─────────────────────────────────────────────────────────────

function HistoryTab({
  setError,
}: {
  setError: React.Dispatch<React.SetStateAction<string | null>>;
}) {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "success" | "failed">("all");
  const [expanded, setExpanded] = useState<number | null>(null);

  const load = useCallback(() => {
    invoke<HistoryEntry[]>("get_history")
      .then(setEntries)
      .catch((reason: unknown) => setError(String(reason)));
  }, [setError]);

  useEffect(() => {
    load();
  }, [load]);

  const doClear = async () => {
    try {
      await invoke("clear_installation_history");
      setEntries([]);
      setExpanded(null);
    } catch (reason) {
      setError(String(reason));
    }
  };

  const visible = entries
    .slice()
    .reverse()
    .filter((h) => {
      if (filter === "success" && !h.success) return false;
      if (filter === "failed" && h.success) return false;
      const q = search.toLowerCase();
      return (
        h.packageName.toLowerCase().includes(q) ||
        h.package.toLowerCase().includes(q)
      );
    });

  return (
    <>
      <div style={{ display: "flex", gap: 8, marginBottom: 12, flexWrap: "wrap" }}>
        <input
          style={{ flex: 1, minWidth: 160 }}
          placeholder="Search history…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value as typeof filter)}
        >
          <option value="all">All</option>
          <option value="success">Success</option>
          <option value="failed">Failed</option>
        </select>
        <button type="button" onClick={load}>
          Refresh
        </button>
        <button type="button" onClick={doClear} disabled={entries.length === 0}>
          Clear history
        </button>
      </div>

      {visible.length === 0 ? (
        <p style={{ color: "#667085" }}>
          {entries.length === 0
            ? "No installation history yet. Install a package to see it here."
            : "No entries match the current filter."}
        </p>
      ) : (
        <ul className="package-list">
          {visible.map((h, i) => (
            <li key={i}>
              <button
                className={expanded === i ? "package-item selected" : "package-item"}
                type="button"
                onClick={() => setExpanded(expanded === i ? null : i)}
              >
                <div style={{ display: "flex", justifyContent: "space-between", width: "100%" }}>
                  <strong>{h.packageName}</strong>
                  <span
                    style={{ color: h.success ? "#027a48" : "#b42318", fontWeight: 600 }}
                  >
                    {h.success ? "✓ Success" : "✗ Failed"}
                  </span>
                </div>
                <small style={{ color: "#667085" }}>{h.timestamp}</small>
                {expanded === i && (
                  <pre
                    style={{
                      marginTop: 8,
                      padding: "8px 12px",
                      background: "#202938",
                      color: "#e5e7eb",
                      fontSize: "0.78rem",
                      whiteSpace: "pre-wrap",
                      textAlign: "left",
                      borderRadius: 6,
                      width: "100%",
                    }}
                  >
                    {h.message}
                  </pre>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
      <p style={{ marginTop: 12, color: "#667085", fontSize: "0.85rem" }}>
        {entries.length} total entr{entries.length === 1 ? "y" : "ies"} · showing {visible.length}
      </p>
    </>
  );
}

// ─── Settings Tab ─────────────────────────────────────────────────────────────

function SettingsTab({
  settings,
  setSettings,
  setError,
}: {
  settings: AppSettings;
  setSettings: React.Dispatch<React.SetStateAction<AppSettings>>;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
}) {
  const [form, setForm] = useState<AppSettings>({ ...settings });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    invoke<AppSettings>("get_settings")
      .then((s) => setForm(s))
      .catch((reason: unknown) => setError(String(reason)));
  }, [setError]);

  const field = <K extends keyof AppSettings>(key: K, value: AppSettings[K]) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const save = async () => {
    try {
      await invoke("save_settings", { settings: form });
      setSettings(form);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (reason) {
      setError(String(reason));
    }
  };

  return (
    <div style={{ display: "grid", gap: 20, maxWidth: 440 }}>
      <label>
        <span style={{ display: "block", marginBottom: 4, fontWeight: 600 }}>Theme</span>
        <select
          style={{ width: "100%", padding: "8px 12px" }}
          value={form.theme}
          onChange={(e) => field("theme", e.target.value)}
        >
          <option value="Light">Light</option>
          <option value="Dark">Dark</option>
        </select>
      </label>

      <label>
        <span style={{ display: "block", marginBottom: 4, fontWeight: 600 }}>Language</span>
        <select
          style={{ width: "100%", padding: "8px 12px" }}
          value={form.language}
          onChange={(e) => field("language", e.target.value)}
        >
          {[
            ["en", "English"],
            ["fr", "Français"],
            ["de", "Deutsch"],
            ["es", "Español"],
            ["it", "Italiano"],
            ["ru", "Русский"],
          ].map(([code, label]) => (
            <option key={code} value={code}>
              {label} ({code})
            </option>
          ))}
        </select>
      </label>

      <label>
        <span style={{ display: "block", marginBottom: 4, fontWeight: 600 }}>
          Default checksum algorithm
        </span>
        <select
          style={{ width: "100%", padding: "8px 12px" }}
          value={form.checksumType}
          onChange={(e) => field("checksumType", e.target.value)}
        >
          <option value="sha256">SHA-256 (recommended)</option>
          <option value="md5">MD5</option>
        </select>
      </label>

      <div style={{ display: "grid", gap: 12 }}>
        <label style={{ display: "flex", gap: 10, alignItems: "center", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={form.verifyIntegrity}
            onChange={(e) => field("verifyIntegrity", e.target.checked)}
          />
          <span>Verify package integrity by default</span>
        </label>
        <label style={{ display: "flex", gap: 10, alignItems: "center", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={form.verifySignature}
            onChange={(e) => field("verifySignature", e.target.checked)}
          />
          <span>Verify package signature by default</span>
        </label>
      </div>

      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <button className="primary-button" type="button" onClick={save}>
          Save settings
        </button>
        {saved && (
          <span style={{ color: "#027a48", fontWeight: 600 }}>✓ Settings saved</span>
        )}
      </div>

      <p style={{ color: "#667085", fontSize: "0.85rem", marginTop: 0 }}>
        Settings are persisted to <code>~/.snapwiz/settings.json</code>
      </p>
    </div>
  );
}

export default App;
