import React, { useState, useEffect, useRef } from 'react';
import '../css/style.css';

const ScanForm: React.FC = () => {
  const [url, setUrl] = useState('https://');
  const [exclude, setExclude] = useState('');
  const [issues, setIssues] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [scanComplete, setScanComplete] = useState(false);
  const [fullScan, setFullScan] = useState(false);
  const [maxDepth, setMaxDepth] = useState(1);
  const [logs, setLogs] = useState<string[]>([]);
  const logRef = useRef<HTMLDivElement>(null);
  const userScrolledRef = useRef(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    if (!userScrolledRef.current && logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    const interval = setInterval(fetchLogs, 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await fetch("http://localhost:8000/log-buffer");
      if (res.ok) {
        const data = await res.json();
        setLogs(data.logs || []);
      }
    } catch {
    }
  };

  const pollForCompletion = async () => {
    while (true) {
      try {
        const statusRes = await fetch("http://localhost:8000/scan/status");
        const status = await statusRes.json();
        if (!status.running) return true;
        await new Promise(r => setTimeout(r, 1500));
      } catch {
        await new Promise(r => setTimeout(r, 1500));
      }
    }
  };

  const handleScan = async () => {
    setLoading(true);
    setIssues([]);
    setScanComplete(false);
    setLogs([]);

    const excludeArray = exclude
      .split(',')
      .map(e => e.trim())
      .filter(Boolean);

    try {
      const startRes = await fetch("http://localhost:8000/scan/start", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, exclude: excludeArray, full: fullScan, max_depth: maxDepth })
      });

      if (!startRes.ok) return;

      await pollForCompletion();

      const resultRes = await fetch("http://localhost:8000/scan/result");
      const result = await resultRes.json();
      setIssues(result.issues || []);
      setScanComplete(true);
    } finally {
      setLoading(false);
    }
  };

  const countByType = (type: string) =>
    issues.filter((issue) => issue.type === type).length;

  const handleCrawlDepthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDepth = Number(e.target.value);
    setMaxDepth(newDepth);

    if (newDepth >= 2) {
      setShowWarning(true);
    } else {
      setShowWarning(false);
    }
  };

  return (
    <div className="container">
      <div className="form-section">
        <p className="instruction">Bitte geben Sie die URL der Webseite ein, die Sie überprüfen wollen:</p>
        <div className="url-input-column">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="input centered-input"
            placeholder="z. B. https://www.beispiel.de"
          />
        </div>

        <div className="scan-options">
          <label>
            <input type="checkbox" checked={!fullScan} onChange={() => setFullScan(false)} /> Nur diese Seite
          </label>
          <label>
            <input type="checkbox" checked={fullScan} onChange={() => setFullScan(true)} /> Gesamte Website
          </label>
        </div>

        <p className="instruction" style={{ marginTop: '1.5rem' }}>Crawl-Tiefe:</p>
        <input
          type="number"
          min="1"
          max="5"
          value={maxDepth}
          onChange={handleCrawlDepthChange}
          className="input"
          style={{ width: '60px' }}
        />

        {showWarning && (
          <div className="modal-overlay">
            <div className="modal-box">
              <span className="tooltip-close" onClick={() => setShowWarning(false)}>×</span>
              <h3>Achtung!</h3>
              <p>Das Erhöhen der Crawl-Tiefe kann bei komplexen Webseiten zu erheblichen Datenmengen und sehr langen Testdurchläufen führen.</p>
              <button className="button" onClick={() => setShowWarning(false)}>Schließen</button>
            </div>
          </div>
        )}

        <p className="instruction">Sollen bestimmte Bereiche vom Scan ausgeschlossen werden?</p>
        <div className="exclude-input-row">
          <input
            type="text"
            value={exclude}
            onChange={(e) => setExclude(e.target.value)}
            placeholder="z. B. /blog*, /shop*"
            className="input"
          />
          <span className="info-link" onClick={() => setShowHelp(true)}>Info/Hilfe</span>
        </div>

        {showHelp && (
          <div className="modal-overlay">
            <div className="modal-box">
              <span className="tooltip-close" onClick={() => setShowHelp(false)}>×</span>
              <h3>Musterhilfe für Ausschlüsse</h3>
              <p>Mehrere Muster mit Komma trennen. Wildcards (<code>*</code>) sind erlaubt:</p>
              <table>
                <thead>
                  <tr><th>Muster</th><th>Beispiele auf <code>beispiel.com</code></th></tr>
                </thead>
                <tbody>
                  <tr><td><code>/blog*</code></td><td>/blog, /blogartikel, /blog/2023</td></tr>
                  <tr><td><code>/blog/*</code></td><td>/blog/2023, /blog/news</td></tr>
                  <tr><td><code>/blog</code></td><td>Nur exakt /blog</td></tr>
                  <tr><td><code>/admin*</code></td><td>/admin, /admin/login, /admin2</td></tr>
                  <tr><td><code>/news/2023*</code></td><td>/news/2023, /news/2023/q3</td></tr>
                  <tr><td><code>/*</code> oder <code>*</code></td><td>Alles</td></tr>
                  <tr><td><code>/*/login</code></td><td>/admin/login, /user/login</td></tr>
                  <tr><td><code>*/private*</code></td><td>/area/private, /user/private-files</td></tr>
                </tbody>
              </table>
              <button className="button" onClick={() => setShowHelp(false)}>Schließen</button>
            </div>
          </div>
        )}

        <div style={{ marginTop: '1.5rem' }}>
          <button onClick={handleScan} disabled={loading || url.trim() === ""} className="button primary">
            {loading ? "Scan läuft..." : "Prüfung starten"}
          </button>
        </div>

        {scanComplete && (
          <div className="report-buttons centered">
            <a href="http://localhost:8000/download-csv" target="_blank" rel="noopener noreferrer">
              <button className="button">Bericht als CSV</button>
            </a>
            <a href="http://localhost:8000/download-html" target="_blank" rel="noopener noreferrer">
              <button className="button">Bericht als HTML</button>
            </a>
          </div>
        )}

        <div className="scan-results-container">
          <div className="pseudo-terminal" ref={logRef} onScroll={() => {
            if (logRef.current) {
              const nearBottom = logRef.current.scrollHeight - logRef.current.scrollTop - logRef.current.clientHeight < 50;
              userScrolledRef.current = !nearBottom;
            }
          }}>
            <h3>Statusausgabe</h3>
            <pre className="terminal-log">
              {logs.length === 0
                ? "Keine Ausgaben vorhanden. Bitte Test starten."
                : logs.map((line, i) => (
                    <div key={i} style={{ textAlign: 'left' }}>{line}</div>
                  ))}
            </pre>
          </div>

          <div className="summary-box">
            <p><strong>Gefundene Fehler insgesamt:</strong> {scanComplete ? issues.length : "–"}</p>
            <p>Kontrast-Fehler: {scanComplete ? countByType("contrast_insufficient") : "–"}</p>
            <p>Bilder ohne Alt-Text: {scanComplete ? countByType("image_alt_missing") : "–"}</p>
            <p>Links ohne Alt-Text: {scanComplete ? countByType("link_incomplete") : "–"}</p>
            <p>Semantisch falsche Schaltflächen: {scanComplete ? countByType("nonsemantic_button") : "–"}</p>
            <p>Fehlende Formular-Labels: {scanComplete ? countByType("form_label_missing") : "–"}</p>
            <p>Überschriftenfehler: {scanComplete ? countByType("heading_hierarchy_error") : "–"}</p>
            <p>ARIA-Probleme: {scanComplete ? countByType("aria_label_without_text") : "–"}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScanForm;
