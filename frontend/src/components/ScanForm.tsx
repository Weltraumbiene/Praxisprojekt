import React, { useState, useEffect } from 'react';
import '../css/style.css';
import loadingIcon from '../images/loading.png';
import scanSteps from '../data/scanSteps.json';
import { HelpCircle, X } from 'lucide-react';

const ScanForm: React.FC = () => {
  const [url, setUrl] = useState('https://');
  const [exclude, setExclude] = useState('');
  const [issues, setIssues] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanComplete, setScanComplete] = useState(false);
  const [statusText, setStatusText] = useState("Initialisiere Scanner...");
  const [fullScan, setFullScan] = useState(true);
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    const showRandomStep = () => {
      const randomIndex = Math.floor(Math.random() * scanSteps.length);
      setStatusText(scanSteps[randomIndex]);
      const delay = Math.floor(Math.random() * (5000 - 2000 + 1)) + 2000;
      timeout = setTimeout(showRandomStep, delay);
    };
    if (loading) showRandomStep();
    else setStatusText("");
    return () => clearTimeout(timeout);
  }, [loading]);

  const handleScan = async () => {
    setLoading(true);
    setError(null);
    setIssues([]);
    setScanComplete(false);

    const excludeArray = exclude
      .split(',')
      .map(entry => entry.trim())
      .filter(entry => entry.length > 0);

    try {
      const response = await fetch('http://localhost:8000/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, exclude: excludeArray, full: fullScan }),
      });

      if (!response.ok) throw new Error('Scan fehlgeschlagen.');

      const data = await response.json();
      setIssues(data.issues);
    } catch (err) {
      setError("Fehler beim Scannen. Bitte URL prüfen und Backend läuft.");
    } finally {
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

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            aria-label="Website URL"
            className="input"
            placeholder="z. B. https://www.beispiel.de"
            style={{ flexGrow: 1, minWidth: '240px', maxWidth: '320px' }}
          />
          <div className="toggle-wrapper" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <label className="switch">
              <input type="checkbox" checked={fullScan} onChange={() => setFullScan(!fullScan)} />
              <span className="slider"></span>
            </label>
            <span style={{ fontSize: '0.85rem' }}>
              {fullScan ? "Gesamte Website" : "Nur diese Seite"}
            </span>
          </div>
        </div>

        <p className="instruction" style={{ marginTop: '1.5rem' }}>
          Sollen einzelne Bereiche ignoriert werden?{" "}
          <span style={{ position: "relative", display: "inline-block" }}>
            <HelpCircle
              size={16}
              style={{ cursor: "pointer", verticalAlign: "middle" }}
              onClick={() => setShowTooltip(!showTooltip)}
            />
            {showTooltip && (
              <div className="tooltip">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <strong style={{ fontSize: "0.95rem" }}>Pfad-Ausschlüsse</strong>
                  <X size={16} style={{ cursor: "pointer" }} onClick={() => setShowTooltip(false)} />
                </div>
                <hr style={{ margin: "0.4rem 0" }} />
                <p style={{ margin: 0, fontSize: "0.85rem" }}>
                  Du kannst Pfade oder Wildcards wie <code>/blog/*</code>, <code>/hilfe.html</code> eingeben.
                  <br />Mehrere Werte trennst du mit Kommas.
                </p>
              </div>
            )}
          </span>
        </p>

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
            {loading ? "Prüfe..." : "Prüfung starten"}
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div className="loading-container">
          <img src={loadingIcon} alt="Lade..." className="loading-icon" />
          <p>{statusText}</p>
        </div>
      )}

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
