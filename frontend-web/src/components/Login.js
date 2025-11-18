import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../constants';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = 'Basic ' + btoa(username + ':' + password);

    try {
      await axios.get(`${API_BASE_URL}/history/`, {
        headers: { 'Authorization': token }
      });
      onLogin(token);
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="card login-card">
      <h3>Login</h3>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          placeholder="Username" 
          value={username} 
          onChange={e => setUsername(e.target.value)} 
        />
        <input 
          type="password" 
          placeholder="Password" 
          value={password} 
          onChange={e => setPassword(e.target.value)} 
        />
        <button type="submit">Login</button>
        {error && <p style={{color: 'red'}}>{error}</p>}
      </form>
    </div>
  );
}
export default Login;