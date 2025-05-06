import React, { useState } from 'react';

const ScanForm: React.FC = () => {
  const [url, setUrl] = useState('');
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleScan = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      setIssues(data.issues);
    } catch (error) {
      console.error("Scan error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://example.com"
        style={{ width: '300px', marginRight: '1rem' }}
      />
      <button onClick={handleScan} disabled={loading}>
        {loading ? 'Scanning...' : 'Start Scan'}
      </button>
      <div style={{ marginTop: '2rem' }}>
        <h2>Ergebnisse:</h2>
        {issues.length === 0 && <p>Keine Ergebnisse</p>}
        {issues.map((issue, index) => (
          <pre key={index} style={{ background: "#eee", padding: "1rem", marginBottom: "1rem" }}>
            {JSON.stringify(issue, null, 2)}
          </pre>
        ))}
        <a href="http://localhost:8000/download-csv" download><button>CSV herunterladen</button></a>
        <a href="http://localhost:8000/download-html" download><button>HTML herunterladen</button></a>
      </div>
    </div>
  );
};

export default ScanForm;
