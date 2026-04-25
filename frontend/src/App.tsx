import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Policies, Archives, Blockchain, Performance } from './pages/index'
import { Settings } from './pages/Settings'
import { ABTestingProvider } from './context/ABTestingContext'
import { analytics } from './services/analytics'
import { Demo } from './pages/Demo'

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
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/policies" element={<Policies />} />
          <Route path="/archives" element={<Archives />} />
          <Route path="/blockchain" element={<Blockchain />} />
          <Route path="/performance" element={<Performance />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/demo" element={<Demo />} />
        </Routes>
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
    <ABTestingProvider>
      <NotificationProvider>
        <AppContent />
      </NotificationProvider>
    </ABTestingProvider>
  )
}

export default App
