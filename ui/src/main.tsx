import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
// Assuming you have a standard CSS file for Tailwind base styles or other global styles
// import './index.css'; 

// IMPORTANT: This file ensures the main App component is mounted to the root DOM element.

const rootElement = document.getElementById('root');

if (rootElement) {
    // Create a React root and render the App component inside it.
    ReactDOM.createRoot(rootElement).render(
        <React.StrictMode>
            <App />
        </React.StrictMode>
    );
} else {
    console.error("Failed to find the root element (#root) in the index.html.");
}