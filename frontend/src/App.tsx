import React, { useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

interface Issue {
  id?: string;
  description?: string | object;
  message?: string | object;
}

interface PageResult {
  url: string;
  axe_violations?: Issue[];
  structural_issues?: Issue[];
  css_issues?: (string | object)[];
  aria_issues?: (string | object)[];
  incomplete_warnings?: Issue[];
  summary?: {
    axe_errors: number;
    structural_issues: number;
    css_issues: number;
    aria_issues: number;
    warnings: number;
    total_errors: number;
  };
  error?: string;
}

const App: React.FC = () => {
  const [url, setUrl] = useState('');
  const [fullScan, setFullScan] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<PageResult[]>([]);
  const [expandedPageIndex, setExpandedPageIndex] = useState<number | null>(null);

  const toggleExpand = (index: number) => {
    setExpandedPageIndex(prev => (prev === index ? null : index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setResults([]);

    try {
      const endpoint = fullScan ? '/full-check' : '/check';
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      if (!response.ok) {
        const err = await response.json().catch(() => null);
        const message = err?.detail?.message || err?.detail || err?.message || 'Unbekannter Fehler';
        throw new Error(message);
      }

      const data = await response.json();
      const pages: PageResult[] = fullScan
        ? data.results || []
        : [{ ...data, url }];
      setResults(pages);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Verbindungsfehler';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Barrierefreiheits-Check</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="url"
          placeholder="https://www.beispiel.de"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />
        <label>
          <input
            type="checkbox"
            checked={fullScan}
            onChange={(e) => setFullScan(e.target.checked)}
          />
          Gesamtscan
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Analyse läuft...' : 'Prüfen'}
        </button>
      </form>

      {error && <div className="error">❌ {error}</div>}
      {loading && <div className="loader">⏳ Lade Ergebnisse...</div>}

      {!loading && results.length > 0 && (
        <div className="results">
          <h2>Ergebnisse ({results.length} Seite{results.length > 1 ? 'n' : ''})</h2>

          {results.map((entry, index) => (
            <details
              key={index}
              open={expandedPageIndex === index}
              onClick={() => toggleExpand(index)}
              className="result-block"
            >
              <summary>{entry.url}</summary>

              {entry.error ? (
                <p className="error">Fehler: {entry.error}</p>
              ) : (
                <>
                  {entry.summary && (
                    <ul>
                      <li><strong>AXE-Fehler:</strong> {entry.summary.axe_errors}</li>
                      <li><strong>Struktur-Fehler:</strong> {entry.summary.structural_issues}</li>
                      <li><strong>CSS-Kontraste:</strong> {entry.summary.css_issues}</li>
                      <li><strong>ARIA-Probleme:</strong> {entry.summary.aria_issues}</li>
                      <li><strong>Warnungen:</strong> {entry.summary.warnings}</li>
                      <li><strong>Gesamtfehler:</strong> {entry.summary.total_errors}</li>
                    </ul>
                  )}

                  {entry.axe_violations && entry.axe_violations.length > 0 && (
                    <>
                      <h3>🔎 AXE Verstöße</h3>
                      <ul>{entry.axe_violations.map((v, i) => (
                        <li key={i}>{typeof v.description === 'string' ? v.description : typeof v.message === 'string' ? v.message : v.id || JSON.stringify(v)}</li>
                      ))}</ul>
                    </>
                  )}

                  {entry.structural_issues && entry.structural_issues.length > 0 && (
                    <>
                      <h3>📐 Strukturprobleme</h3>
                      <ul>{entry.structural_issues.map((v, i) => (
                        <li key={i}>{typeof v.message === 'string' ? v.message : JSON.stringify(v)}</li>
                      ))}</ul>
                    </>
                  )}

                  {entry.css_issues && entry.css_issues.length > 0 && (
                    <>
                      <h3>🎨 Farbkontrast</h3>
                      <ul>{entry.css_issues.map((msg, i) => (
                        <li key={i}>{typeof msg === 'string' ? msg : JSON.stringify(msg)}</li>
                      ))}</ul>
                    </>
                  )}

                  {entry.aria_issues && entry.aria_issues.length > 0 && (
                    <>
                      <h3>🧩 ARIA</h3>
                      <ul>{entry.aria_issues.map((msg, i) => (
                        <li key={i}>{typeof msg === 'string' ? msg : JSON.stringify(msg)}</li>
                      ))}</ul>
                    </>
                  )}

                  {entry.incomplete_warnings && entry.incomplete_warnings.length > 0 && (
                    <>
                      <h3>⚠️ Unvollständig geprüft</h3>
                      <ul>{entry.incomplete_warnings.map((v, i) => (
                        <li key={i}>{typeof v.description === 'string' ? v.description : typeof v.message === 'string' ? v.message : v.id || JSON.stringify(v)}</li>
                      ))}</ul>
                    </>
                  )}
                </>
              )}
            </details>
          ))}
        </div>
      )}
    </div>
  );
};

export default App;