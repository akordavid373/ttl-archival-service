import React from 'react'
import { Toast } from './Toast'
import { Notification } from '../../types/notifications'

interface ToastContainerProps {
  notifications: Notification[]
  onClose: (id: string) => void
  onAction?: (notification: Notification) => void
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'
  maxToasts?: number
}

const positionClasses = {
  'top-right': 'top-4 right-4',
  'top-left': 'top-4 left-4',
  'bottom-right': 'bottom-4 right-4',
  'bottom-left': 'bottom-4 left-4',
  'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
  'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2'
}

export function ToastContainer({ 
  notifications, 
  onClose, 
  onAction, 
  position = 'top-right',
  maxToasts = 5 
}: ToastContainerProps) {
  const displayNotifications = notifications.slice(-maxToasts)

  return (
    <div 
      className={`fixed z-50 space-y-2 ${positionClasses[position]}`}
      role="region"
      aria-label="Notifications"
      aria-live="polite"
    >
      {displayNotifications.map((notification) => (
        <Toast
          key={notification.id}
          notification={notification}
          onClose={onClose}
          onAction={onAction}
        />
      ))}
    </div>
  )
}
