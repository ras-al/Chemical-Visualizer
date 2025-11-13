// src/components/EquipmentChart.js
import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register the components for a Bar chart
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function EquipmentChart({ distribution }) {
  if (!distribution) {
    return null;
  }

  const data = {
    labels: Object.keys(distribution),
    datasets: [
      {
        label: '# of Equipment',
        data: Object.values(distribution),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)',
        ],
      },
    ],
  };

  const options = {
    // These two options are CRITICAL for good scaling
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false, // We don't need a legend for one dataset
      },
      title: {
        display: true,
        text: 'Equipment Type Distribution',
        font: {
          size: 18,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="card chart-container">
      {/* We pass the options and data to the Bar component */}
      <Bar options={options} data={data} />
    </div>
  );
}

export default EquipmentChart;