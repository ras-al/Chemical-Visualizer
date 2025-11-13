// src/components/HistoryList.js
import React from 'react';

function HistoryList({ history, onHistorySelect, onHistoryDelete }) {
  const sortedHistory = [...history].sort(
    (a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at)
  );

  return (
    <div className="card history-list-card">
      <h3>3. Upload History</h3>
      {history.length === 0 ? (
        <p>No uploads yet.</p>
      ) : (
        <div className="history-list-container">
            <ul>
            {sortedHistory.map((item) => (
                <li key={item.id}>
                
                <div className="history-item-info">
                    <span>{item.filename}</span>
                    <small>Uploaded at: {new Date(item.uploaded_at).toLocaleString()}</small>
                </div>
                <div className="history-item-actions">
                  <button 
                      className="show-button"
                      onClick={() => onHistorySelect(item.id)}
                  >
                      Show
                  </button>
                  <button 
                      className="delete-button"
                      onClick={() => onHistoryDelete(item.id)}
                  >
                      Delete
                  </button>
                </div>

                </li>
            ))}
            </ul>
        </div>
      )}
    </div>
  );
}

export default HistoryList;