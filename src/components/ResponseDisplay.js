// ResponseDisplay.js
import React, { useState, useEffect } from 'react';

function ResponseDisplay() {
  const [response, setResponse] = useState('');

  useEffect(() => {
    const fetchResponse = async () => {
      try {
        const res = await fetch('/assistant');
        const data = await res.json();
        setResponse(data.response);
      } catch (error) {
        console.error('Error fetching response:', error);
      }
    };

    fetchResponse();
  }, []);

  return (
    <div>
      <h2>Assistant Response:</h2>
      <p>{response}</p>
    </div>
  );
}

export default ResponseDisplay;
