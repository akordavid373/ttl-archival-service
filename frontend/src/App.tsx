import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Policies, Archives, Blockchain } from './pages/index'
import { Settings } from './pages/Settings'

import { NotificationProvider } from './context/NotificationContext'
import { ToastContainer, NotificationCenter } from './components/notifications'
import { useNotifications } from './context/NotificationContext'

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
    <NotificationProvider>
      <AppContent />
    </NotificationProvider>
  )
}

export default App
