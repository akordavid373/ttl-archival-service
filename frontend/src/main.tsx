import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import './index.css'
import { ThemeProvider } from './context/ThemeContext'
import { SettingsProvider } from './context/SettingsContext'
import { registerServiceWorker } from './utils/serviceWorker'

// Register service worker
registerServiceWorker({
  onSuccess: (registration) => {
    console.log('Service Worker registered successfully')
  },
  onUpdate: (registration) => {
    console.log('Service Worker updated, new content available')
    // You can show a notification to the user here
  },
  onError: (error) => {
    console.error('Service Worker registration failed:', error)
  }
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <SettingsProvider>
          <App />
        </SettingsProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
)
