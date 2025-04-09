import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('https://www.beispiel.de')
  const [result, setResult] = useState<any>(null)
  const [file, setFile] = useState<File | null>(null)
  const [selectedOptions, setSelectedOptions] = useState<string[]>([])

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const options = event.dataTransfer.getData('text/plain')
    if (options) {
      setSelectedOptions([...selectedOptions, options])
    }
  }

  const handleCheck = async () => {
    const requestBody: any = file
      ? { html: await file.text() }
      : { url, filter: selectedOptions }

    // ⚠️ Immer neue API nutzen (strukturierte Ausgabe!)
    const response = await fetch('http://localhost:8000/check', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    })

    const data = await response.json()
    setResult(data)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0] || null
    setFile(selected)
  }

  return (
    <div className="container">
      <h1>A-SQA Barrierefreiheitsüberprüfung</h1>

      <input
        type="text"
        placeholder="https://www.beispiel.de"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />

      <div
        className="dropzone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        <p>Funktionen per Drag & Drop hierher ziehen</p>
        <ul>
          {selectedOptions.map((opt, idx) => (
            <li key={idx}>{opt}</li>
          ))}
        </ul>
      </div>

      <input
        type="file"
        accept=".html"
        onChange={handleFileChange}
      />

      <button onClick={handleCheck}>Prüfen</button>

      {result && (
        <div className="results">
          <h2>Ergebnisse für: {result.source}</h2>

          <h3>📊 Zusammenfassung</h3>
          <ul>
            <li><strong>AXE-Fehler:</strong> {result.summary.axe_errors}</li>
            <li><strong>Struktur-Fehler:</strong> {result.summary.structural_issues}</li>
            <li><strong>CSS-Probleme:</strong> {result.summary.css_issues}</li>
            <li><strong>Warnungen (AXE):</strong> {result.summary.warnings}</li>
            <li><strong>Gesamt:</strong> {result.summary.total_errors}</li>
          </ul>

          <h3>🚨 AXE Violations</h3>
          <ul>
            {result.axe_violations?.map((v: any, i: number) => (
              <li key={i}>
                <strong>{v.id}</strong>: {v.description}
              </li>
            ))}
          </ul>

          <h3>📐 Strukturprobleme</h3>
          <ul>
            {result.structural_issues?.map((v: any, i: number) => (
              <li key={i}>
                <strong>{v.type}</strong>: {v.message}
              </li>
            ))}
          </ul>

          <h3>🎨 CSS-Kontrastprobleme</h3>
          <ul>
            {result.css_issues?.map((msg: string, i: number) => (
              <li key={i}>{msg}</li>
            ))}
          </ul>

          <h3>⚠️ Unvollständige Ergebnisse (AXE)</h3>
          <ul>
            {result.incomplete_warnings?.map((v: any, i: number) => (
              <li key={i}>
                <strong>{v.id}</strong>: {v.description}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App
