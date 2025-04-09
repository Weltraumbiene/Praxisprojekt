import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [result, setResult] = useState<any>(null)

  const handleCheck = async () => {
    const response = await fetch('http://localhost:8000/check', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    })
    const data = await response.json()
    setResult(data)
  }

  return (
    <div className="container">
      <h1>A-SQA Barrierefreiheitsüberprüfung</h1>

      <input
        type="text"
        placeholder="Gib eine URL ein"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button onClick={handleCheck}>Prüfen</button>

      {result && (
        <div className="results">
          <h2>Ergebnisse</h2>
          <p><strong>Fehler:</strong> {result.errors}</p>
          <p><strong>Warnungen:</strong> {result.warnings}</p>
          <ul>
            {result.suggestions.map((s: string, i: number) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App

