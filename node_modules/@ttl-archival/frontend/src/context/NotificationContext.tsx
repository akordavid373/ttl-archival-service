import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { 
  Notification, 
  NotificationType, 
  NotificationPriority, 
  NotificationPreferences,
  WebSocketNotification 
} from '../types/notifications'

interface NotificationContextType {
  notifications: Notification[]
  preferences: NotificationPreferences
  isNotificationCenterOpen: boolean
  unreadCount: number
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void
  removeNotification: (id: string) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  clearAll: () => void
  updatePreferences: (preferences: Partial<NotificationPreferences>) => void
  openNotificationCenter: () => void
  closeNotificationCenter: () => void
  playSound: (type: NotificationType) => void
  requestDesktopPermission: () => Promise<boolean>
}

const defaultPreferences: NotificationPreferences = {
  enabled: true,
  soundEnabled: true,
  visualAlertsEnabled: true,
  autoDismiss: true,
  defaultTimeout: 5000,
  enableDesktop: true,
  types: {
    success: { enabled: true, sound: true, autoDismiss: true, timeout: 3000 },
    error: { enabled: true, sound: true, autoDismiss: false, timeout: 0 },
    warning: { enabled: true, sound: true, autoDismiss: true, timeout: 5000 },
    info: { enabled: true, sound: false, autoDismiss: true, timeout: 4000 },
    system: { enabled: true, sound: false, autoDismiss: true, timeout: 6000 }
  },
  priorities: {
    low: { sound: false, autoDismiss: true, timeout: 3000 },
    medium: { sound: true, autoDismiss: true, timeout: 5000 },
    high: { sound: true, autoDismiss: false, timeout: 0 },
    urgent: { sound: true, autoDismiss: false, timeout: 0 }
  }
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [preferences, setPreferences] = useState<NotificationPreferences>(defaultPreferences)
  const [isNotificationCenterOpen, setIsNotificationCenterOpen] = useState(false)
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null)

  // Initialize audio context
  useEffect(() => {
    if (typeof window !== 'undefined' && preferences.soundEnabled) {
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)()
      setAudioContext(ctx)
      return () => ctx.close()
    }
  }, [preferences.soundEnabled])

  // Load preferences from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('notification-preferences')
      if (saved) {
        setPreferences({ ...defaultPreferences, ...JSON.parse(saved) })
      }
    } catch (error) {
      console.error('Failed to load notification preferences:', error)
    }
  }, [])

  // Save preferences to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('notification-preferences', JSON.stringify(preferences))
    } catch (error) {
      console.error('Failed to save notification preferences:', error)
    }
  }, [preferences])

  const unreadCount = notifications.filter(n => !n.read).length

  const generateId = () => Math.random().toString(36).substr(2, 9)

  const playSound = useCallback((type: NotificationType) => {
    if (!preferences.soundEnabled || !audioContext) return

    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)

    // Different frequencies for different notification types
    const frequencies = {
      success: 523.25,    // C5
      error: 261.63,      // C4
      warning: 329.63,    // E4
      info: 392.00,       // G4
      system: 440.00      // A4
    }

    oscillator.frequency.value = frequencies[type]
    oscillator.type = 'sine'
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5)

    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.5)
  }, [preferences.soundEnabled, audioContext])

  const requestDesktopPermission = async (): Promise<boolean> => {
    if (!('Notification' in window)) return false

    if (Notification.permission === 'granted') return true
    if (Notification.permission === 'denied') return false

    const permission = await Notification.requestPermission()
    return permission === 'granted'
  }

  const showDesktopNotification = useCallback((notification: Notification) => {
    if (!preferences.enableDesktop || !('Notification' in window)) return

    if (Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico',
        tag: notification.id,
        requireInteraction: !notification.autoDismiss
      })
    }
  }, [preferences.enableDesktop])

  const addNotification = useCallback((notificationData: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    if (!preferences.enabled) return

    const notification: Notification = {
      ...notificationData,
      id: generateId(),
      timestamp: new Date(),
      read: false,
      autoDismiss: notificationData.autoDismiss ?? preferences.autoDismiss,
      dismissTimeout: notificationData.dismissTimeout ?? preferences.defaultTimeout
    }

    setNotifications(prev => [notification, ...prev])

    // Play sound if enabled for this type
    const typeConfig = preferences.types[notification.type]
    const priorityConfig = preferences.priorities[notification.priority]
    
    if (typeConfig.sound && priorityConfig.sound) {
      playSound(notification.type)
    }

    // Show desktop notification
    showDesktopNotification(notification)

    // Visual alert
    if (preferences.visualAlertsEnabled && notification.priority === 'urgent') {
      document.body.classList.add('notification-pulse')
      setTimeout(() => document.body.classList.remove('notification-pulse'), 1000)
    }
  }, [preferences, playSound, showDesktopNotification])

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev => prev.map(n => 
      n.id === id ? { ...n, read: true } : n
    ))
  }, [])

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }, [])

  const clearAll = useCallback(() => {
    setNotifications([])
  }, [])

  const updatePreferences = useCallback((newPreferences: Partial<NotificationPreferences>) => {
    setPreferences(prev => ({ ...prev, ...newPreferences }))
  }, [])

  const openNotificationCenter = useCallback(() => {
    setIsNotificationCenterOpen(true)
  }, [])

  const closeNotificationCenter = useCallback(() => {
    setIsNotificationCenterOpen(false)
  }, [])

  // WebSocket integration (placeholder - will be implemented separately)
  useEffect(() => {
    // This will be connected to actual WebSocket implementation
    const handleWebSocketMessage = (data: WebSocketNotification) => {
      addNotification({
        type: data.type,
        title: data.title,
        message: data.message,
        priority: data.priority,
        metadata: data.metadata
      })
    }

    // For now, we'll just add this as a placeholder
    // Actual WebSocket connection will be added in the next step
    return () => {}
  }, [addNotification])

  const value: NotificationContextType = {
    notifications,
    preferences,
    isNotificationCenterOpen,
    unreadCount,
    addNotification,
    removeNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    updatePreferences,
    openNotificationCenter,
    closeNotificationCenter,
    playSound,
    requestDesktopPermission
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  )
}

export function useNotifications() {
  const context = useContext(NotificationContext)
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}
