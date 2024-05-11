import React, { useState } from 'react';
import axios from 'axios';
import "./VirtualAssistant.css"
import Robot from './Robot';

function VirtualAssistant() {
  const [brand, setBrand] = useState('');
  const [price, setPrice] = useState('');
  const [response, setResponse] = useState('');

  const handleFilterLaptops = async () => {
    try {
      const response = await axios.post('/filter_laptops', { criteria: { brand, price } });
      const filteredLaptops = response.data.filtered_laptops;
      setResponse('Here are some laptops that match your criteria:');
      // Process and display the filtered laptops
    } catch (error) {
      console.error('Error filtering laptops:', error);
      setResponse('Error filtering laptops.');
    }
  };

  return (
    <div className="container">
      <h1>Virtual Assistant</h1>
     <Robot/>
      <div className="input-group">
        <label>Brand:</label>
        <input type="text" value={brand} onChange={(e) => setBrand(e.target.value)} />
      </div>
      <div className="input-group">
        <label>Price:</label>
        <input type="text" value={price} onChange={(e) => setPrice(e.target.value)} />
      </div>
      <button onClick={handleFilterLaptops}>Filter Laptops</button>
      <p>{response}</p>
    </div>
  );
}

export default VirtualAssistant;
