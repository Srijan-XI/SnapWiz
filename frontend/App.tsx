import { invoke } from "@tauri-apps/api/core";
import { useEffect, useState } from "react";
import "./App.css";

type AppInfo = {
  name: string;
  version: string;
  supportedFormats: string[];
};

function App() {
  const [activeTab, setActiveTab] = useState("Install");
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    invoke<AppInfo>("get_app_info")
      .then(setAppInfo)
      .catch((reason: unknown) => setError(String(reason)));
  }, []);

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
            <p>Select package files to begin the migration's first vertical slice.</p>
            <button className="primary-button" type="button" disabled>
              Choose package files
            </button>
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
