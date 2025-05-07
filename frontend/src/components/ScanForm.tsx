import React, { useState, useEffect } from 'react';
import '../css/style.css';
import loadingIcon from '../images/loading.png';
import scanSteps from '../data/scanSteps.json';

const ScanForm: React.FC = () => {
  const [url, setUrl] = useState('https://');
  const [issues, setIssues] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanComplete, setScanComplete] = useState(false);
  const [statusText, setStatusText] = useState("Initialisiere Scanner...");

  useEffect(() => {
    let timeout: NodeJS.Timeout;

    const showRandomStep = () => {
      const randomIndex = Math.floor(Math.random() * scanSteps.length);
      setStatusText(scanSteps[randomIndex]);

      const delay = Math.floor(Math.random() * (5000 - 2000 + 1)) + 2000;
      timeout = setTimeout(showRandomStep, delay);
    };

    if (loading) {
      showRandomStep();
    } else {
      setStatusText("");
    }

    return () => clearTimeout(timeout);
  }, [loading]);

  const handleScan = async () => {
    setLoading(true);
    setError(null);
    setIssues([]);
    setScanComplete(false);

    try {
      const response = await fetch('http://localhost:8000/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
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
      <p className="instruction">Bitte geben Sie die URL der Webseite ein, die Sie überprüfen wollen:</p>

      <div className="form">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          aria-label="Website URL"
          className="input"
        />
        <button onClick={handleScan} disabled={loading || url.trim() === ""} className="button primary">
          {loading ? "Prüfe..." : "Prüfung starten"}
        </button>
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
