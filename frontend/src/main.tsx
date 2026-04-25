import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { WagmiProvider } from 'wagmi'
import { HelmetProvider } from 'react-helmet-async'
import * as Sentry from "@sentry/react"
import { config } from './utils/wagmi'
import App from './App.tsx'
import { ThemeProvider } from './context/ThemeContext'
import { ShortcutProvider } from './context/ShortcutContext'
import { LanguageProvider } from './context/LanguageContext'
import './utils/i18n'
import './index.css'

// Initialize Sentry
Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN || "https://examplePublicKey@o0.ingest.sentry.io/0",
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  // Performance Monitoring
  tracesSampleRate: 1.0, 
  // Session Replay
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Sentry.ErrorBoundary fallback={<div>Something went wrong.</div>} showDialog>
      <HelmetProvider>
        <WagmiProvider config={config}>
          <QueryClientProvider client={queryClient}>
            <BrowserRouter>
              <LanguageProvider>
                <ThemeProvider>
                  <ShortcutProvider>
                    <App />
                  </ShortcutProvider>
                </ThemeProvider>
              </LanguageProvider>
            </BrowserRouter>
          </QueryClientProvider>
        </WagmiProvider>
      </HelmetProvider>
    </Sentry.ErrorBoundary>
  </React.StrictMode>,
)
