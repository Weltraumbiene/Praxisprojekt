import React from 'react';
import ScanForm from './components/ScanForm';
import './css/style.css';

const App: React.FC = () => {
  return (
    <div className="app-container">
      <h1 className="logo">ASQA BariFree V2.0.1</h1>
      <ScanForm />
    </div>
  );
};

export default App;

