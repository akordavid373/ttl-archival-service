import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { WagmiProvider } from 'wagmi'
import { HelmetProvider } from 'react-helmet-async'
import * as Sentry from "@sentry/react"
import { config } from './utils/wagmi'
import App from './App.tsx'
import './index.css'
import { ThemeProvider } from './context/ThemeContext'
import { SettingsProvider } from './context/SettingsContext'
import { QueryProvider } from './providers/QueryProvider'
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
      <HelmetProvider>
        <WagmiProvider config={config}>
          <QueryClientProvider client={new QueryClient()}>
            <QueryProvider>
              <ThemeProvider>
                <SettingsProvider>
                  <App />
                </SettingsProvider>
              </ThemeProvider>
            </QueryProvider>
          </QueryClientProvider>
        </WagmiProvider>
      </HelmetProvider>
    </BrowserRouter>
  </React.StrictMode>
)
