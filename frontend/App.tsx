import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { open } from "@tauri-apps/plugin-dialog";
import { useCallback, useEffect, useState } from "react";
import "./App.css";

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
  verifyIntegrity: boolean;
  verifySignature: boolean;
  checksumType: string;
};

function App() {
  const [activeTab, setActiveTab] = useState("Install");
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [queue, setQueue] = useState<PackageInfo[]>([]);
  const [selectedPackage, setSelectedPackage] = useState<PackageInfo | null>(null);
  const [progress, setProgress] = useState<InstallProgress | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [installing, setInstalling] = useState(false);
  const [settings, setSettings] = useState<AppSettings>({
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
      if (queue.some((item) => item.path === path) || newPackages.some((item) => item.path === path)) {
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
      if (!verification.success) {
        throw new Error(verification.message);
      }
      const result = await invoke<{ success: boolean; message: string }>("install_package_command", {
        packagePath: selectedPackage.path,
      });
      if (!result.success) {
        throw new Error(result.message);
      }
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
        {activeTab === "Install" ? (
          <>
            <p>Select package files or drop them into the queue.</p>
            <div className="drop-zone" onDragOver={(event) => event.preventDefault()} onDrop={handleDrop}>
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
                  <button type="button" onClick={removeSelected} disabled={!selectedPackage || installing}>Remove selected</button>
                  <button type="button" onClick={() => { setQueue([]); setSelectedPackage(null); }} disabled={installing}>Clear queue</button>
                </div>
                <div className="package-details">
                  <h3>{selectedPackage?.fileName}</h3>
                  <pre>{selectedPackage?.metadata}</pre>
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.verifySignature}
                      onChange={(event) => setSettings({ ...settings, verifySignature: event.target.checked })}
                    />
                    Verify signature
                  </label>
                  <button className="primary-button" type="button" onClick={verifyAndInstall} disabled={!selectedPackage || installing}>
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
        ) : (
          <p className="placeholder">This view will be implemented in the next migration slice.</p>
        )}
        {error && <p className="error">Backend unavailable: {error}</p>}
      </section>
    </main>
  );
}

export default App;
