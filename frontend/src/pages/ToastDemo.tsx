import { useState } from 'react'
import { useNotifications } from '../context/NotificationContext'
import { NotificationType, NotificationPriority } from '../types/notifications'
import { 
  CheckCircle, 
  AlertCircle, 
  AlertTriangle, 
  Info, 
  Settings,
  Bell,
  Volume2,
  VolumeX
} from 'lucide-react'

const typeIcons = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
  system: Settings
}

export default function ToastDemo() {
  const { addNotification, preferences, updatePreferences } = useNotifications()
  const [selectedType, setSelectedType] = useState<NotificationType>('info')
  const [selectedPriority, setSelectedPriority] = useState<NotificationPriority>('medium')
  const [customMessage, setCustomMessage] = useState('This is a sample notification message!')
  const [customTitle, setCustomTitle] = useState('Sample Notification')

  const showToast = (type: NotificationType, priority: NotificationPriority = 'medium', autoDismiss = true) => {
    addNotification({
      type,
      title: `${type.charAt(0).toUpperCase() + type.slice(1)} Notification`,
      message: `This is a ${type} notification with ${priority} priority.`,
      priority,
      autoDismiss,
      dismissTimeout: autoDismiss ? 5000 : undefined,
      action: type === 'error' ? {
        label: 'Retry',
        onClick: () => console.log('Retry action clicked')
      } : undefined
    })
  }

  const showCustomNotification = () => {
    addNotification({
      type: selectedType,
      title: customTitle,
      message: customMessage,
      priority: selectedPriority,
      autoDismiss: preferences.autoDismiss,
      dismissTimeout: preferences.autoDismiss ? preferences.defaultTimeout : undefined
    })
  }

  const showBatchNotifications = () => {
    const types: NotificationType[] = ['success', 'error', 'warning', 'info', 'system']
    const priorities: NotificationPriority[] = ['low', 'medium', 'high', 'urgent']
    
    types.forEach((type, index) => {
      setTimeout(() => {
        showToast(type, priorities[index % priorities.length])
      }, index * 500)
    })
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">Toast Notification System Demo</h1>
        <p className="text-gray-600">Explore the comprehensive toast notification system with multiple types, positions, and features.</p>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border p-6 space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button
            onClick={() => showToast('success')}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors"
          >
            <CheckCircle className="h-4 w-4" />
            Success
          </button>
          <button
            onClick={() => showToast('error')}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors"
          >
            <AlertCircle className="h-4 w-4" />
            Error
          </button>
          <button
            onClick={() => showToast('warning')}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-yellow-50 text-yellow-700 rounded-lg hover:bg-yellow-100 transition-colors"
          >
            <AlertTriangle className="h-4 w-4" />
            Warning
          </button>
          <button
            onClick={() => showToast('info')}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <Info className="h-4 w-4" />
            Info
          </button>
        </div>

        <button
          onClick={showBatchNotifications}
          className="w-full px-4 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors"
        >
          Show Batch Notifications (Stacking Demo)
        </button>
      </div>

      {/* Custom Notification Builder */}
      <div className="bg-white rounded-lg shadow-sm border p-6 space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">Custom Notification Builder</h2>
        
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
            <input
              type="text"
              value={customTitle}
              onChange={(e) => setCustomTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter notification title"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value as NotificationType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {Object.keys(typeIcons).map(type => (
                <option key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
          <textarea
            value={customMessage}
            onChange={(e) => setCustomMessage(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
            placeholder="Enter notification message"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
          <div className="flex gap-2">
            {(['low', 'medium', 'high', 'urgent'] as NotificationPriority[]).map(priority => (
              <button
                key={priority}
                onClick={() => setSelectedPriority(priority)}
                className={`px-3 py-1 rounded-lg border transition-colors ${
                  selectedPriority === priority
                    ? 'bg-blue-50 border-blue-300 text-blue-700'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {priority.charAt(0).toUpperCase() + priority.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={showCustomNotification}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Show Custom Notification
        </button>
      </div>

      {/* Priority Demo */}
      <div className="bg-white rounded-lg shadow-sm border p-6 space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">Priority Levels Demo</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {(['low', 'medium', 'high', 'urgent'] as NotificationPriority[]).map(priority => (
            <button
              key={priority}
              onClick={() => showToast('info', priority)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                priority === 'urgent' ? 'bg-red-600 text-white hover:bg-red-700' :
                priority === 'high' ? 'bg-orange-500 text-white hover:bg-orange-600' :
                priority === 'medium' ? 'bg-blue-500 text-white hover:bg-blue-600' :
                'bg-gray-500 text-white hover:bg-gray-600'
              }`}
            >
              {priority.charAt(0).toUpperCase() + priority.slice(1)}
            </button>
          ))}
        </div>
        <p className="text-sm text-gray-600">Notice how urgent notifications have stronger visual indicators and don't auto-dismiss.</p>
      </div>

      {/* Settings */}
      <div className="bg-white rounded-lg shadow-sm border p-6 space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">Notification Settings</h2>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {preferences.soundEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
              <span className="text-sm font-medium text-gray-700">Sound Effects</span>
            </div>
            <button
              onClick={() => updatePreferences({ soundEnabled: !preferences.soundEnabled })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                preferences.soundEnabled ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  preferences.soundEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              <span className="text-sm font-medium text-gray-700">Auto-dismiss</span>
            </div>
            <button
              onClick={() => updatePreferences({ autoDismiss: !preferences.autoDismiss })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                preferences.autoDismiss ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  preferences.autoDismiss ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Default Timeout</span>
            <select
              value={preferences.defaultTimeout}
              onChange={(e) => updatePreferences({ defaultTimeout: Number(e.target.value) })}
              className="px-3 py-1 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={3000}>3 seconds</option>
              <option value={5000}>5 seconds</option>
              <option value={8000}>8 seconds</option>
              <option value={10000}>10 seconds</option>
            </select>
          </div>
        </div>
      </div>

      {/* Features Overview */}
      <div className="bg-white rounded-lg shadow-sm border p-6 space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">✅ Features Implemented</h2>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Multiple notification types (success, error, warning, info, system)</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Stackable notifications with configurable limits</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Auto-dismiss with visual progress indicator</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Manual dismiss functionality</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Position options (top, bottom, corners, center)</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Priority levels with visual indicators</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Accessibility announcements (aria-live)</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Sound effects and desktop notifications</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
