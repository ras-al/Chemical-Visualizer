// src/components/SummaryStats.js
import React from 'react';
import axios from 'axios'; // <-- ADD THIS
import { API_BASE_URL } from '../constants'; // <-- ADD THIS

function SummaryStats({ dataset }) {
  if (!dataset || !dataset.summary_data) { 
    return null;
  }

  const { total_count, averages } = dataset.summary_data;
 
  const handleDownloadPDF = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/summary/${dataset.id}/report/`, 
        {
          responseType: 'blob',
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      // Use the original filename for the report
      link.setAttribute('download', `${dataset.filename}_report.pdf`); 
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error("Error downloading PDF:", error);
      alert("Failed to download PDF report.");
    }
  };

  return (
    <div className="card summary-stats"> 
      <h3>2. Data Summary</h3>
      {/* ADD FILENAME */}
      <p className="summary-filename">File: {dataset.filename}</p>

      <ul>
        <li>
          <strong>{total_count}</strong>
          <span>Total Equipment</span>
        </li>
        <li>
          <strong>{averages.flowrate_avg}</strong>
          <span>Avg. Flowrate</span>
        </li>
        <li>
          <strong>{averages.pressure_avg}</strong>
          <span>Avg. Pressure</span>
        </li>
        <li>
          <strong>{averages.temperature_avg} °C</strong>
          <span>Avg. Temperature</span>
        </li>
      </ul>

      <button 
        onClick={handleDownloadPDF} 
        className="pdf-button"
      >
        Download PDF Report
      </button>
      {/* ------------------------- */}
    </div>
  );
}

export default SummaryStats;