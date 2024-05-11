// QueryForm.js
import React from 'react';

function QueryForm({ startListening, stopListening, conversationStarted }) {
  const handleClick = () => {
    if (!conversationStarted) {
      startListening();
    } else {
      stopListening();
    }
  };

  return (
    <div>
      <button onClick={handleClick}>{conversationStarted ? 'Stop Listening' : 'Assistant Help'}</button>
    </div>
  );
}

export default QueryForm;
