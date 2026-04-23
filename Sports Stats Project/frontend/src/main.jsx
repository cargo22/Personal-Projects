// main.jsx — entry point for the React app, this is the first file Vite runs

// StrictMode is a built-in React dev tool that runs extra checks to catch bugs early
// it has no effect in production — purely for development
import { StrictMode } from 'react'

// react-dom handles putting React components into the actual HTML page
// createRoot creates the starting point for the app inside the HTML
import { createRoot } from 'react-dom/client'

// App is the main component — default export so no curly braces needed
import App from './App.jsx'

// finds the <div id="root"> in index.html and mounts the entire React app inside it
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
