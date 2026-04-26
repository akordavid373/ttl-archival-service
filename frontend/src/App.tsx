import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Policies, Archives, Blockchain, Performance } from './pages/index'
import { Settings } from './pages/Settings'
import { ABTestingProvider } from './context/ABTestingContext'
import { analytics } from './services/analytics'
import { Demo } from './pages/Demo'
import { NotificationProvider, useNotifications } from './context/NotificationContext'
import { ToastContainer } from './components/ToastContainer'
import { NotificationCenter } from './components/NotificationCenter'

// ✅ Error Boundary imports
import { ErrorBoundary } from './components/ErrorBoundary'
import { ErrorFallback } from './components/ErrorFallback'

// Initialize Analytics
analytics.init('G-XXXXXXXXXX');

function AppContent() {
  const { 
    notifications, 
    isNotificationCenterOpen, 
    removeNotification, 
    markAsRead, 
    markAllAsRead, 
    clearAll, 
    closeNotificationCenter 
  } = useNotifications()

  return (
    <>
      <Layout>
        {/* 🔒 Route-level Error Boundary */}
        <ErrorBoundary
          fallback={
            <ErrorFallback onRetry={() => window.location.reload()} />
          }
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/policies" element={<Policies />} />
            <Route path="/archives" element={<Archives />} />
            <Route path="/blockchain" element={<Blockchain />} />
            <Route path="/performance" element={<Performance />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/demo" element={<Demo />} />
          </Routes>
        </ErrorBoundary>
      </Layout>
      
      <ToastContainer 
        notifications={notifications.filter(
          n => !n.read || n.timestamp.getTime() > Date.now() - 60000
        )}
        onClose={removeNotification}
        position="top-right"
        maxToasts={5}
      />
      
      <NotificationCenter
        notifications={notifications}
        isOpen={isNotificationCenterOpen}
        onClose={closeNotificationCenter}
        onMarkAsRead={markAsRead}
        onDelete={removeNotification}
        onClearAll={clearAll}
        onMarkAllAsRead={markAllAsRead}
      />
    </>
  )
}

function App() {
  return (
    <ABTestingProvider>
      <NotificationProvider>
        {/* 🌍 App-level Error Boundary (global safety net) */}
        <ErrorBoundary
          fallback={
            <ErrorFallback onRetry={() => window.location.reload()} />
          }
        >
          <AppContent />
        </ErrorBoundary>
      </NotificationProvider>
    </ABTestingProvider>
  )
}

export default App