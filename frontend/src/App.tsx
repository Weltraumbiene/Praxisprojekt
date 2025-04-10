import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('https://www.beispiel.de')
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fullScan, setFullScan] = useState(false)
  const [selectedOptions, setSelectedOptions] = useState<string[]>(['wcag2a', 'wcag2aa'])

  const handleCheck = async () => {
    setLoading(true)
    setError(null)
    setResults([])

    try {
      const endpoint = fullScan ? '/full-check' : '/check'
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, filter: selectedOptions })
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Unbekannter Fehler')
      }

      const data = await response.json()
      setResults(fullScan ? data.results : [{ url: data.source, result: data }])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <h1 className="title">A-SQA Barrierefreiheitscheck</h1>

      <div className="controls">
        <input
          type="text"
          placeholder="https://www.beispiel.de"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />

        <label className="checkbox">
          <input type="checkbox" checked={fullScan} onChange={() => setFullScan(!fullScan)} />
          Vollständiger Website-Scan
        </label>

        <button onClick={handleCheck} disabled={loading}>
          {loading ? 'Prüfe...' : 'Prüfen'}
        </button>
      </div>

      {error && <div className="error">❌ {error}</div>}

      {loading && <div className="loader"></div>}

      {!loading && results.length > 0 && (
        <div className="results">
          <h2>{fullScan ? '🌐 Vollständiger Scan' : 'Ergebnisse'}</h2>
          <p>Geprüfte Seiten: {results.length}</p>

          {results.map((entry, index) => (
            <details key={index} open={index === 0} className="page-entry">
              <summary>{entry.url}</summary>
              {entry.error ? (
                <p className="error">Fehler: {entry.error}</p>
              ) : (
                <div>
                  <h4>📊 Zusammenfassung</h4>
                  <ul>
                    <li><strong>AXE-Fehler:</strong> {entry.result.summary.axe_errors}</li>
                    <li><strong>Struktur-Fehler:</strong> {entry.result.summary.structural_issues}</li>
                    <li><strong>CSS-Probleme:</strong> {entry.result.summary.css_issues}</li>
                    <li><strong>ARIA-Probleme:</strong> {entry.result.summary.aria_issues}</li>
                    <li><strong>Warnungen (AXE):</strong> {entry.result.summary.warnings}</li>
                    <li><strong>Gesamt:</strong> {entry.result.summary.total_errors}</li>
                  </ul>

                  <h4>🚨 AXE Violations</h4>
                  <ul>
                    {entry.result.axe_violations.map((v: any, i: number) => (
                      <li key={i}><strong>{v.id}</strong>: {v.description}</li>
                    ))}
                  </ul>

                  <h4>📐 Strukturprobleme</h4>
                  <ul>
                    {entry.result.structural_issues.map((v: any, i: number) => (
                      <li key={i}><strong>{v.type}</strong>: {v.message}</li>
                    ))}
                  </ul>

                  <h4>🎨 CSS-Kontrastprobleme</h4>
                  <ul>
                    {entry.result.css_issues.map((msg: string, i: number) => (
                      <li key={i}>{msg}</li>
                    ))}
                  </ul>

                  <h4>🧩 ARIA-Probleme</h4>
                  <ul>
                    {entry.result.aria_issues.map((msg: string, i: number) => (
                      <li key={i}>{msg}</li>
                    ))}
                  </ul>

                  <h4>⚠️ Unvollständige Ergebnisse</h4>
                  <ul>
                    {entry.result.incomplete_warnings.map((v: any, i: number) => (
                      <li key={i}><strong>{v.id}</strong>: {v.description}</li>
                    ))}
                  </ul>
                </div>
              )}
            </details>
          ))}
        </div>
      )}
    </div>
  )
}

export default App