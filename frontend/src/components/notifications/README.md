# Notification System

A comprehensive notification system for the TTL-Archival Service with toast notifications, notification center, real-time updates, and customizable preferences.

## Features

- **Toast Notifications**: Auto-dismissing notifications with progress indicators
- **Notification Center**: Full history with filtering and management
- **Real-time Updates**: WebSocket integration for live notifications
- **Sound & Visual Alerts**: Configurable audio and visual feedback
- **Notification Preferences**: Granular control over notification behavior
- **Desktop Notifications**: Native OS notifications
- **Priority Levels**: Low, Medium, High, Urgent
- **Notification Types**: Success, Error, Warning, Info, System

## Components

### NotificationProvider
Wrap your application with this provider to enable notifications throughout your app.

```tsx
import { NotificationProvider } from './context/NotificationContext'

function App() {
  return (
    <NotificationProvider>
      <YourApp />
    </NotificationProvider>
  )
}
```

### useNotifications Hook
Access notification functionality in any component.

```tsx
import { useNotifications } from './context/NotificationContext'

function MyComponent() {
  const { addNotification, notifications, unreadCount } = useNotifications()
  
  const handleSuccess = () => {
    addNotification({
      type: 'success',
      title: 'Success!',
      message: 'Operation completed successfully.',
      priority: 'medium',
      autoDismiss: true,
      dismissTimeout: 3000
    })
  }
  
  return (
    <div>
      <button onClick={handleSuccess}>Show Success</button>
      <p>Unread: {unreadCount}</p>
    </div>
  )
}
```

### NotificationBell
Add a notification bell to your header.

```tsx
import { NotificationBell } from './components/notifications'

function Header() {
  return <NotificationBell />
}
```

### ToastContainer
Automatically displays toast notifications (usually included in App.tsx).

```tsx
import { ToastContainer } from './components/notifications'

function App() {
  const { notifications, removeNotification } = useNotifications()
  
  return (
    <ToastContainer 
      notifications={notifications}
      onClose={removeNotification}
      position="top-right"
      maxToasts={5}
    />
  )
}
```

### NotificationCenter
Full notification center with history and filtering.

```tsx
import { NotificationCenter } from './components/notifications'

function App() {
  const { 
    notifications, 
    isNotificationCenterOpen, 
    markAsRead, 
    deleteNotification,
    clearAll,
    markAllAsRead,
    closeNotificationCenter 
  } = useNotifications()
  
  return (
    <NotificationCenter
      notifications={notifications}
      isOpen={isNotificationCenterOpen}
      onClose={closeNotificationCenter}
      onMarkAsRead={markAsRead}
      onDelete={deleteNotification}
      onClearAll={clearAll}
      onMarkAllAsRead={markAllAsRead}
    />
  )
}
```

### NotificationPreferences
Settings panel for notification configuration.

```tsx
import { NotificationPreferences } from './components/notifications'

function Settings() {
  const { preferences, updatePreferences } = useNotifications()
  
  return (
    <NotificationPreferences 
      preferences={preferences}
      onChange={updatePreferences}
    />
  )
}
```

## Notification Types

### Basic Types
- `success`: Green, checkmark icon
- `error`: Red, alert icon
- `warning`: Yellow, warning icon
- `info`: Blue, info icon
- `system`: Gray, settings icon

### Priority Levels
- `low`: Minimal visual emphasis
- `medium`: Standard visual emphasis
- `high`: Strong visual emphasis, no auto-dismiss
- `urgent`: Maximum emphasis with pulse animation

## Configuration

### Notification Interface
```tsx
interface Notification {
  id: string                    // Auto-generated
  type: NotificationType         // success | error | warning | info | system
  title: string                 // Notification title
  message: string               // Detailed message
  timestamp: Date               // Creation time
  priority: NotificationPriority  // low | medium | high | urgent
  autoDismiss?: boolean          // Override default auto-dismiss
  dismissTimeout?: number        // Custom timeout in ms
  read: boolean                 // Read status
  action?: {                   // Optional action button
    label: string
    onClick: () => void
  }
  metadata?: Record<string, any>  // Additional data
}
```

### Preferences Interface
```tsx
interface NotificationPreferences {
  enabled: boolean
  soundEnabled: boolean
  visualAlertsEnabled: boolean
  autoDismiss: boolean
  defaultTimeout: number
  enableDesktop: boolean
  types: {
    [type in NotificationType]: {
      enabled: boolean
      sound: boolean
      autoDismiss: boolean
      timeout: number
    }
  }
  priorities: {
    [priority in NotificationPriority]: {
      sound: boolean
      autoDismiss: boolean
      timeout: number
    }
  }
}
```

## WebSocket Integration

The system includes WebSocket support for real-time notifications:

```tsx
import { getWebSocketService } from './services/websocket'

// Initialize WebSocket service
const wsService = getWebSocketService('ws://localhost:8080/notifications')

// Connect and handle messages
await wsService.connect()

// Listen for notifications
const unsubscribe = wsService.onMessage((data) => {
  // Automatically handled by NotificationContext
})

// Clean up
unsubscribe()
wsService.disconnect()
```

## Sound System

Built-in audio synthesis for notification sounds:

- Different frequencies for each notification type
- Volume control
- Can be disabled per notification type
- Web Audio API based

## Desktop Notifications

Native OS notification support:

- Automatic permission handling
- Fallback to in-app notifications
- Configurable per notification type
- Click handling for notification actions

## Styling

The notification system uses Tailwind CSS with:

- Consistent color scheme
- Smooth animations
- Responsive design
- Accessibility support
- High contrast mode support

## Examples

### Basic Usage
```tsx
import { useNotifications } from './context/NotificationContext'

function FileUpload() {
  const { addNotification } = useNotifications()
  
  const handleUpload = async (file: File) => {
    try {
      await uploadFile(file)
      addNotification({
        type: 'success',
        title: 'Upload Complete',
        message: `${file.name} uploaded successfully`,
        priority: 'medium'
      })
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Upload Failed',
        message: `Failed to upload ${file.name}: ${error.message}`,
        priority: 'high',
        autoDismiss: false
      })
    }
  }
  
  return <input type="file" onChange={(e) => handleUpload(e.target.files[0])} />
}
```

### With Actions
```tsx
function DataSync() {
  const { addNotification } = useNotifications()
  
  const showSyncNotification = () => {
    addNotification({
      type: 'info',
      title: 'Data Sync Available',
      message: 'New data is ready to sync',
      priority: 'medium',
      action: {
        label: 'Sync Now',
        onClick: () => syncData()
      }
    })
  }
  
  return <button onClick={showSyncNotification}>Check for Updates</button>
}
```

### Custom Hook
```tsx
// hooks/useArchivalNotifications.ts
import { useCallback } from 'react'
import { useNotifications } from '../context/NotificationContext'

export function useArchivalNotifications() {
  const { addNotification } = useNotifications()
  
  const showArchivalComplete = useCallback((archiveName: string) => {
    addNotification({
      type: 'success',
      title: 'Archival Complete',
      message: `Archive "${archiveName}" has been created`,
      priority: 'medium',
      autoDismiss: true,
      dismissTimeout: 3000
    })
  }, [addNotification])
  
  const showTTLWarning = useCallback((itemName: string, expiryDate: Date) => {
    addNotification({
      type: 'warning',
      title: 'TTL Expiry Warning',
      message: `${itemName} expires on ${expiryDate.toLocaleDateString()}`,
      priority: 'high',
      autoDismiss: false
    })
  }, [addNotification])
  
  return { showArchivalComplete, showTTLWarning }
}
```

## Best Practices

1. **Use appropriate types**: Match notification type to the nature of the event
2. **Set correct priorities**: Use higher priority for important notifications
3. **Provide clear messages**: Be specific about what happened
4. **Use actions when helpful**: Give users immediate next steps
5. **Respect preferences**: Check user preferences before showing notifications
6. **Don't over-notify**: Avoid spamming users with too many notifications

## Accessibility

- Screen reader support with ARIA labels
- Keyboard navigation
- High contrast support
- Focus management
- Semantic HTML structure

## Performance

- Efficient state management with React Context
- Debounced sound playing
- Optimized re-renders
- Memory-efficient notification history
- Lazy loading of audio context
