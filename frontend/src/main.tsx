import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { WagmiProvider } from 'wagmi'
import { HelmetProvider } from 'react-helmet-async'
import * as Sentry from "@sentry/react"
import { config } from './lib/wagmi'
import App from './App.tsx'
import { ThemeProvider } from './context/ThemeContext'
import { SettingsProvider } from './context/SettingsContext'
import { QueryProvider } from './providers/QueryProvider'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryProvider>
        <ThemeProvider>
          <SettingsProvider>
            <App />
          </SettingsProvider>
        </ThemeProvider>
      </QueryProvider>
    </BrowserRouter>
  </React.StrictMode>
)
