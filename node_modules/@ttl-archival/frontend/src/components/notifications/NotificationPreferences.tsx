import React from 'react'
import { Bell, Volume2, Eye, Monitor, Settings as SettingsIcon } from 'lucide-react'
import { NotificationPreferences, NotificationType, NotificationPriority } from '../../types/notifications'
import { cn } from '../../utils/cn'

interface NotificationPreferencesProps {
  preferences: NotificationPreferences
  onChange: (preferences: Partial<NotificationPreferences>) => void
}

const typeLabels: Record<NotificationType, string> = {
  success: 'Success',
  error: 'Error',
  warning: 'Warning',
  info: 'Info',
  system: 'System'
}

const priorityLabels: Record<NotificationPriority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  urgent: 'Urgent'
}

export function NotificationPreferences({ preferences, onChange }: NotificationPreferencesProps) {
  const handleGlobalChange = (key: keyof NotificationPreferences, value: any) => {
    onChange({ [key]: value })
  }

  const handleTypeChange = (type: NotificationType, key: string, value: any) => {
    onChange({
      types: {
        ...preferences.types,
        [type]: {
          ...preferences.types[type],
          [key]: value
        }
      }
    })
  }

  const handlePriorityChange = (priority: NotificationPriority, key: string, value: any) => {
    onChange({
      priorities: {
        ...preferences.priorities,
        [priority]: {
          ...preferences.priorities[priority],
          [key]: value
        }
      }
    })
  }

  return (
    <div className="space-y-6">
      {/* Global Settings */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <SettingsIcon className="h-5 w-5" />
          Global Settings
        </h3>
        
        <div className="space-y-3">
          <label className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              <span>Enable Notifications</span>
            </div>
            <input
              type="checkbox"
              checked={preferences.enabled}
              onChange={(e) => handleGlobalChange('enabled', e.target.checked)}
              className="w-4 h-4"
            />
          </label>

          <label className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Volume2 className="h-4 w-4" />
              <span>Sound Effects</span>
            </div>
            <input
              type="checkbox"
              checked={preferences.soundEnabled}
              onChange={(e) => handleGlobalChange('soundEnabled', e.target.checked)}
              disabled={!preferences.enabled}
              className="w-4 h-4"
            />
          </label>

          <label className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Eye className="h-4 w-4" />
              <span>Visual Alerts</span>
            </div>
            <input
              type="checkbox"
              checked={preferences.visualAlertsEnabled}
              onChange={(e) => handleGlobalChange('visualAlertsEnabled', e.target.checked)}
              disabled={!preferences.enabled}
              className="w-4 h-4"
            />
          </label>

          <label className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Monitor className="h-4 w-4" />
              <span>Desktop Notifications</span>
            </div>
            <input
              type="checkbox"
              checked={preferences.enableDesktop}
              onChange={(e) => handleGlobalChange('enableDesktop', e.target.checked)}
              disabled={!preferences.enabled}
              className="w-4 h-4"
            />
          </label>

          <label className="flex items-center justify-between">
            <span>Auto-dismiss by default</span>
            <input
              type="checkbox"
              checked={preferences.autoDismiss}
              onChange={(e) => handleGlobalChange('autoDismiss', e.target.checked)}
              disabled={!preferences.enabled}
              className="w-4 h-4"
            />
          </label>

          <div className="flex items-center justify-between">
            <span>Default timeout (seconds)</span>
            <input
              type="number"
              min="1"
              max="60"
              value={preferences.defaultTimeout / 1000}
              onChange={(e) => handleGlobalChange('defaultTimeout', parseInt(e.target.value) * 1000)}
              disabled={!preferences.enabled || !preferences.autoDismiss}
              className="w-20 px-2 py-1 border rounded"
            />
          </div>
        </div>
      </div>

      {/* Type-specific Settings */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Notification Types</h3>
        <div className="space-y-3">
          {Object.entries(typeLabels).map(([type, label]) => (
            <div key={type} className="border rounded-lg p-4 space-y-3">
              <h4 className="font-medium">{label}</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <label className="flex items-center justify-between">
                  <span>Enabled</span>
                  <input
                    type="checkbox"
                    checked={preferences.types[type as NotificationType].enabled}
                    onChange={(e) => handleTypeChange(type as NotificationType, 'enabled', e.target.checked)}
                    disabled={!preferences.enabled}
                    className="w-4 h-4"
                  />
                </label>

                <label className="flex items-center justify-between">
                  <span>Sound</span>
                  <input
                    type="checkbox"
                    checked={preferences.types[type as NotificationType].sound}
                    onChange={(e) => handleTypeChange(type as NotificationType, 'sound', e.target.checked)}
                    disabled={!preferences.enabled || !preferences.soundEnabled}
                    className="w-4 h-4"
                  />
                </label>

                <label className="flex items-center justify-between">
                  <span>Auto-dismiss</span>
                  <input
                    type="checkbox"
                    checked={preferences.types[type as NotificationType].autoDismiss}
                    onChange={(e) => handleTypeChange(type as NotificationType, 'autoDismiss', e.target.checked)}
                    disabled={!preferences.enabled}
                    className="w-4 h-4"
                  />
                </label>

                <div className="flex items-center justify-between">
                  <span>Timeout (s)</span>
                  <input
                    type="number"
                    min="1"
                    max="60"
                    value={preferences.types[type as NotificationType].timeout / 1000}
                    onChange={(e) => handleTypeChange(type as NotificationType, 'timeout', parseInt(e.target.value) * 1000)}
                    disabled={!preferences.enabled || !preferences.types[type as NotificationType].autoDismiss}
                    className="w-20 px-2 py-1 border rounded"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Priority-specific Settings */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Priority Levels</h3>
        <div className="space-y-3">
          {Object.entries(priorityLabels).map(([priority, label]) => (
            <div key={priority} className="border rounded-lg p-4 space-y-3">
              <h4 className="font-medium">{label}</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <label className="flex items-center justify-between">
                  <span>Sound</span>
                  <input
                    type="checkbox"
                    checked={preferences.priorities[priority as NotificationPriority].sound}
                    onChange={(e) => handlePriorityChange(priority as NotificationPriority, 'sound', e.target.checked)}
                    disabled={!preferences.enabled || !preferences.soundEnabled}
                    className="w-4 h-4"
                  />
                </label>

                <label className="flex items-center justify-between">
                  <span>Auto-dismiss</span>
                  <input
                    type="checkbox"
                    checked={preferences.priorities[priority as NotificationPriority].autoDismiss}
                    onChange={(e) => handlePriorityChange(priority as NotificationPriority, 'autoDismiss', e.target.checked)}
                    disabled={!preferences.enabled}
                    className="w-4 h-4"
                  />
                </label>

                <div className="flex items-center justify-between">
                  <span>Timeout (s)</span>
                  <input
                    type="number"
                    min="1"
                    max="60"
                    value={preferences.priorities[priority as NotificationPriority].timeout / 1000}
                    onChange={(e) => handlePriorityChange(priority as NotificationPriority, 'timeout', parseInt(e.target.value) * 1000)}
                    disabled={!preferences.enabled || !preferences.priorities[priority as NotificationPriority].autoDismiss}
                    className="w-20 px-2 py-1 border rounded"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
