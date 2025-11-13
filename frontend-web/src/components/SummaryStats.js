// src/components/SummaryStats.js
import React from 'react';

function SummaryStats({ summary }) {
  if (!summary) {
    return null;
  }

  const { total_count, averages } = summary;

  return (
    // Add the "summary-stats" className here
    <div className="card summary-stats"> 
      <h3>2. Data Summary</h3>
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
    </div>
  );
}

export default SummaryStats;