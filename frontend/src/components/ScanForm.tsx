import React, { useState, useEffect } from 'react';
import '../css/style.css';
import loadingIcon from '../images/loading.png';
import scanSteps from '../data/scanSteps.json'; // JSON importieren

const ScanForm: React.FC = () => {
  const [url, setUrl] = useState('https://');
  const [issues, setIssues] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanComplete, setScanComplete] = useState(false);
  const [statusText, setStatusText] = useState("Initialisiere Scanner...");

  // zufällige Statusmeldung anzeigen, solange loading aktiv ist
  useEffect(() => {
    let timeout: NodeJS.Timeout;
  
    const showRandomStep = () => {
      const randomIndex = Math.floor(Math.random() * scanSteps.length);
      setStatusText(scanSteps[randomIndex]);
  
      // Zufällige nächste Laufzeit zwischen 2 und 5 Sekunden
      const delay = Math.floor(Math.random() * (5000 - 2000 + 1)) + 2000;
      timeout = setTimeout(showRandomStep, delay);
    };
  
    if (loading) {
      showRandomStep(); // erste Ausführung starten
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
          <div className="report-buttons">
            <a href="http://localhost:8000/download-csv" target="_blank" rel="noopener noreferrer">
              <button className="button">Bericht als CSV</button>
            </a>
            <a href="http://localhost:8000/download-html" target="_blank" rel="noopener noreferrer">
              <button className="button">Bericht als HTML</button>
            </a>
          </div>

          <h2 className="results-heading">Ergebnisse</h2>
          {issues.length === 0 ? (
            <p className="no-results">Keine Ergebnisse</p>
          ) : (
            issues.map((issue, index) => (
              <pre key={index} className="result-item">
                {JSON.stringify(issue, null, 2)}
              </pre>
            ))
          )}
        </>
      )}
    </div>
  );
};

export default ScanForm;
