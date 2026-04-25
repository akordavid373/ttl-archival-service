import { Routes, Route } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { Layout } from './components/Layout'
import { PageLoader } from './components/LoadingSpinner'
import { NotificationProvider } from './context/NotificationContext'
import { ToastContainer, NotificationCenter } from './components/notifications'
import { useNotifications } from './context/NotificationContext'

// Lazy load pages for code splitting
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Policies = lazy(() => import('./pages/Policies'))
const Archives = lazy(() => import('./pages/Archives'))
const Blockchain = lazy(() => import('./pages/Blockchain'))
const Settings = lazy(() => import('./pages/Settings'))

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
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/policies" element={<Policies />} />
            <Route path="/archives" element={<Archives />} />
            <Route path="/blockchain" element={<Blockchain />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Suspense>
      </Layout>
      
      <ToastContainer 
        notifications={notifications.filter(n => !n.read || n.timestamp.getTime() > Date.now() - 60000)}
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
    <NotificationProvider>
      <AppContent />
    </NotificationProvider>
  )
}

export default App
