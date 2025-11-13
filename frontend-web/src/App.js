// src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; 

import FileUpload from './components/FileUpload';
import SummaryStats from './components/SummaryStats';
import HistoryList from './components/HistoryList';
import EquipmentChart from './components/EquipmentChart';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

function App() {
  const [currentSummary, setCurrentSummary] = useState(null);
  const [historyList, setHistoryList] = useState([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/history/`);
      setHistoryList(response.data);
    } catch (err) {
      console.error("Error fetching history:", err);
    }
  };

  const handleUploadSuccess = (newUploadData) => {
    // newUploadData from the upload endpoint has the full summary
    setCurrentSummary(newUploadData.summary_data);
    // We just re-fetch the list to get the new item
    fetchHistory();
  };

  const loadHistorySummary = async (historyId) => {
    try {
      // Call our Django endpoint
      const response = await axios.get(`${API_BASE_URL}/summary/${historyId}/`);
      // The response.data IS the summary object
      setCurrentSummary(response.data);
    } catch (err) {
      console.error("Error loading summary:", err);
      alert("Could not load summary for that item.");
    }
  };

  // --- ADD THIS NEW DELETE FUNCTION ---
  /**
   * Deletes a specific history item from the database
   * and refreshes the UI.
   */
  const handleDeleteHistory = async (historyId) => {
    // Optional: Add a confirmation dialog
    if (!window.confirm("Are you sure you want to delete this summary? This action cannot be undone.")) {
      return;
    }

    try {
      // Use the DELETE method on the same endpoint
      await axios.delete(`${API_BASE_URL}/summary/${historyId}/`);
      
      // Refresh the history list from the server
      fetchHistory();
      
      // Clear the current summary view
      // This prevents showing data that has just been deleted
      setCurrentSummary(null); 

    } catch (err) {
      console.error("Error deleting summary:", err);
      alert("Could not delete summary.");
    }
  };
  // -------------------------------------

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chemical Equipment Parameter Visualizer</h1>
      </header>
      
      <div className="main-content">
        <FileUpload onUploadSuccess={handleUploadSuccess} />
        <SummaryStats summary={currentSummary} />
        
        {/* Pass BOTH functions as props */}
        <HistoryList 
          history={historyList} 
          onHistorySelect={loadHistorySummary} 
          onHistoryDelete={handleDeleteHistory} 
        />
        
        <EquipmentChart distribution={currentSummary?.type_distribution} />
      </div>
    </div>
  );
}

export default App;