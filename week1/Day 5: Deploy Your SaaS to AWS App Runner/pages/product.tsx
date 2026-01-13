import React, { useState } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';

export default function ProductPage() {
  const [result, setResult] = useState("");

  const startConsultation = async () => {
    setResult(""); // Clear previous results
    
    // This is the correct way to call your Docker/AWS backend
    await fetchEventSource('/api/consultation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        // add your form data here, e.g.,
        symptoms: "headache", 
        history: "none" 
      }),
      onmessage(ev) {
        const data = JSON.parse(ev.data);
        setResult((prev) => prev + data.text);
      },
      onerror(err) {
        console.error("EventSource failed:", err);
      }
    });
  };

  return (
    <div className="p-8">
      <h1>Healthcare Consultation</h1>
      <button 
        onClick={startConsultation}
        className="bg-blue-500 text-white p-2 rounded"
      >
        Start AI Analysis
      </button>
      <div className="mt-4 whitespace-pre-wrap">{result}</div>
    </div>
  );
}