import React, { useState, useEffect, useRef } from 'react';
import '../css/style.css';

const ScanForm: React.FC = () => {
  const [url, setUrl] = useState('https://');
  const [exclude, setExclude] = useState('');
  const [issues, setIssues] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanComplete, setScanComplete] = useState(false);
  const [fullScan, setFullScan] = useState(false);
  const [maxDepth, setMaxDepth] = useState(3);
  const [logs, setLogs] = useState<string[]>([]);
  const logRef = useRef<HTMLDivElement>(null);

  // Automatisches Scrollen im Log-Bereich
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  // Polling zur Log-Aktualisierung
  useEffect(() => {
    const interval = setInterval(fetchLogs, 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await fetch('http://localhost:8000/log-buffer');
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs || []);
      }
    } catch (error) {
      console.error("Fehler beim Abrufen der Logs:", error);
    }
  };

  const handleScan = async () => {
    setLoading(true);
    setError(null);
    setIssues([]);
    setScanComplete(false);
    setLogs([]);

    const excludeArray = exclude
      .split(',')
      .map(entry => entry.trim())
      .filter(entry => entry.length > 0);

    try {
      const response = await fetch('http://localhost:8000/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url,
          exclude: excludeArray,
          full: fullScan,
          max_depth: maxDepth
        }),
      });

      if (!response.ok) throw new Error('Scan fehlgeschlagen.');

      const data = await response.json();
      setIssues(data.issues);
    } catch (err) {
      setError("Fehler beim Scannen. Bitte URL prüfen und Backend läuft.");
    } finally {
      await fetchLogs(); // Letzte Logs holen
      setLoading(false);
      setScanComplete(true);
    }
  };

  const countByType = (type: string) =>
    issues.filter((issue) => issue.type === type).length;

  return (
    <div className="container">
      <div className="form-section">
        <p className="instruction">Bitte geben Sie die URL der Webseite ein, die Sie überprüfen wollen:</p>

        <div className="url-input-column">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            aria-label="Website URL"
            className="input centered-input"
            placeholder="z. B. https://www.beispiel.de"
          />
        </div>

        <div className="scan-options">
          <label>
            <input
              type="checkbox"
              checked={!fullScan}
              onChange={() => setFullScan(false)}
            />
            Nur diese Seite
          </label>
          <label>
            <input
              type="checkbox"
              checked={fullScan}
              onChange={() => setFullScan(true)}
            />
            Gesamte Website
          </label>
        </div>

        <p className="instruction" style={{ marginTop: '1.5rem' }}>
          Crawltiefe:
          <input
            type="number"
            min="1"
            max="5"
            value={maxDepth}
            onChange={(e) => setMaxDepth(Number(e.target.value))}
            className="input"
            style={{ width: '60px', marginLeft: '1rem' }}
          />
        </p>

        <p className="instruction">Sollen bestimmte Bereiche vom Scan ausgeschlossen werden?</p>
        <input
          type="text"
          value={exclude}
          onChange={(e) => setExclude(e.target.value)}
          aria-label="Ausschlussfilter"
          placeholder="z. B. /blog/*, /shop/*"
          className="input"
        />

        <div style={{ marginTop: '1.5rem' }}>
          <button onClick={handleScan} disabled={loading || url.trim() === ""} className="button primary">
            {loading ? "Scan läuft..." : "Prüfung starten"}
          </button>
        </div>

        <div className="pseudo-terminal" ref={logRef}>
          <h3>Statusausgabe</h3>
          <pre className="terminal-log">
            {logs.length === 0 ? "Keine Ausgaben vorhanden." : logs.map((line, i) => (
              <div key={i}>{line}</div>
            ))}
          </pre>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {scanComplete && !loading && (
        <>
          <div className="summary-box">
            <p><strong>Gefundene Fehler insgesamt:</strong> {issues.length}</p>
            <p>Kontrast-Fehler: {countByType("contrast_insufficient")}</p>
            <p>Bilder ohne Alt-Text: {countByType("image_alt_missing")}</p>
            <p>Links ohne Alt-Text: {countByType("link_incomplete")}</p>
            <p>Semantisch falsche Schaltflächen: {countByType("nonsemantic_button")}</p>
            <p>Fehlende Formular-Labels: {countByType("form_label_missing")}</p>
            <p>Überschriftenfehler: {countByType("heading_hierarchy_error")}</p>
            <p>ARIA-Probleme: {countByType("aria_label_without_text")}</p>
          </div>

          <div className="report-buttons">
            <a href="http://localhost:8000/download-csv" target="_blank" rel="noopener noreferrer">
              <button className="button">Bericht als CSV</button>
            </a>
            <a href="http://localhost:8000/download-html" target="_blank" rel="noopener noreferrer">
              <button className="button">Bericht als HTML</button>
            </a>
          </div>
        </>
      )}
    </div>
  );
};

export default ScanForm;
