export type NotificationType = 'success' | 'error' | 'warning' | 'info' | 'system'

export type NotificationPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface Notification {
  id: string
  type: NotificationType
  title: string
  message: string
  timestamp: Date
  priority: NotificationPriority
  autoDismiss?: boolean
  dismissTimeout?: number
  read: boolean
  action?: {
    label: string
    onClick: () => void
  }
  metadata?: Record<string, any>
}

export interface NotificationPreferences {
  enabled: boolean
  soundEnabled: boolean
  visualAlertsEnabled: boolean
  autoDismiss: boolean
  defaultTimeout: number
  enableDesktop: boolean
  types: {
    [key in NotificationType]: {
      enabled: boolean
      sound: boolean
      autoDismiss: boolean
      timeout: number
    }
  }
  priorities: {
    [key in NotificationPriority]: {
      sound: boolean
      autoDismiss: boolean
      timeout: number
    }
  }
}

export interface NotificationSound {
  type: NotificationType
  src: string
  volume: number
}

export interface WebSocketNotification {
  id: string
  type: NotificationType
  title: string
  message: string
  priority: NotificationPriority
  timestamp: string
  metadata?: Record<string, any>
}
