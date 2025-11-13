// src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; 

import FileUpload from './components/FileUpload';
import SummaryStats from './components/SummaryStats';
import HistoryList from './components/HistoryList';
import EquipmentChart from './components/EquipmentChart';
import DataTable from './components/DataTable'; 

import { API_BASE_URL } from './constants';

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
    setCurrentSummary(newUploadData);
    fetchHistory();
  };

  const loadHistorySummary = async (historyId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/summary/${historyId}/`);
      setCurrentSummary(response.data);
    } catch (err) {
      console.error("Error loading summary:", err);
      alert("Could not load summary for that item.");
    }
  };

  const handleDeleteHistory = async (historyId) => {
    if (!window.confirm("Are you sure you want to delete this summary? This action cannot be undone.")) {
      return;
    }
    try {
      await axios.delete(`${API_BASE_URL}/summary/${historyId}/`);
      fetchHistory();
      
      if (currentSummary && currentSummary.id === historyId) {
        setCurrentSummary(null);
      }
    } catch (err) {
      console.error("Error deleting summary:", err);
      alert("Could not delete summary.");
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chemical Equipment Parameter Visualizer</h1>
      </header>
      
      <div className="main-content">
        <FileUpload onUploadSuccess={handleUploadSuccess} />
        <SummaryStats dataset={currentSummary} />
        <HistoryList 
          history={historyList} 
          onHistorySelect={loadHistorySummary} 
          onHistoryDelete={handleDeleteHistory} 
        />
        <EquipmentChart distribution={currentSummary?.summary_data?.type_distribution} />
        <DataTable data={currentSummary?.summary_data?.raw_data} />
      </div>
    </div>
  );
}

export default App;