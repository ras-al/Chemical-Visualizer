import React, { useState } from 'react';
import { API_BASE_URL } from '../constants';
import axios from 'axios';

const API_URL = `${API_BASE_URL}/upload/`;

function FileUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setError('');
    setMessage('');
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setMessage('Uploading...');
      const response = await axios.post(API_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      onUploadSuccess(response.data);
      setMessage('Upload successful!');
      setSelectedFile(null);
    } catch (err) {
      if (err.response) {
        setError(err.response.data.error || 'Upload failed.');
      } else {
        setError('Upload failed. Is the backend server running?');
      }
      setMessage('');
    }
  };

  return (
    <div className="card file-upload-card" style={{ border: 'none', boxShadow: 'none', padding: 0, background: 'transparent' }}>

      <label className="upload-container">
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="file-input"
        />


        <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>

        <span className="upload-text">
          {selectedFile ? selectedFile.name : "Click to upload CSV"}
        </span>
        <span className="upload-subtext">
          {selectedFile ? "File selected - Click 'Upload' to process" : "or drag and drop"}
        </span>
      </label>


      {selectedFile && (
        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <button onClick={handleUpload} style={{ width: '100%', maxWidth: '200px' }}>
            Process File
          </button>
        </div>
      )}

      {error && <p className="error">{error}</p>}
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default FileUpload;