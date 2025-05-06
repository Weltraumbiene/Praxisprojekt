import React from 'react';
import ScanForm from './components/ScanForm';

const App: React.FC = () => {
  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Barrierefreiheit prüfen</h1>
      <ScanForm />
    </div>
  );
};

export default App;
