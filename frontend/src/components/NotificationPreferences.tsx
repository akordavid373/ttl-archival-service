import React, { useState, useEffect } from 'react'
import { 
  Bell, 
  Mail, 
  Smartphone, 
  Volume2, 
  VolumeX,
  Clock,
  Settings,
  Check,
  X,
  Calendar,
  User,
  Archive,
  AlertTriangle,
  Info,
  CheckCircle,
  Filter,
  Trash2,
  Search
} from 'lucide-react'
import { cn } from '../utils/cn'

interface NotificationPreference {
  id: string
  type: 'email' | 'push' | 'in_app'
  category: 'system' | 'archive' | 'policy' | 'security' | 'performance'
  enabled: boolean
  frequency: 'immediate' | 'hourly' | 'daily' | 'weekly'
  quietHours: {
    enabled: boolean
    start: string
    end: string
  }
}

interface NotificationHistory {
  id: string
  type: 'email' | 'push' | 'in_app'
  category: string
  title: string
  message: string
  timestamp: string
  read: boolean
  actionTaken?: string
}

interface QuietHoursSettings {
  enabled: boolean
  timezone: string
  start: string
  end: string
  weekends: boolean
}

interface NotificationPreferencesProps {
  className?: string
}

export function NotificationPreferences({ className }: NotificationPreferencesProps) {
  const [preferences, setPreferences] = useState<NotificationPreference[]>([
    {
      id: '1',
      type: 'email',
      category: 'system',
      enabled: true,
      frequency: 'daily',
      quietHours: { enabled: true, start: '22:00', end: '08:00' }
    },
    {
      id: '2',
      type: 'push',
      category: 'archive',
      enabled: true,
      frequency: 'immediate',
      quietHours: { enabled: true, start: '22:00', end: '08:00' }
    },
    {
      id: '3',
      type: 'in_app',
      category: 'security',
      enabled: true,
      frequency: 'immediate',
      quietHours: { enabled: false, start: '22:00', end: '08:00' }
    }
  ])

  const [quietHours, setQuietHours] = useState<QuietHoursSettings>({
    enabled: true,
    timezone: 'UTC',
    start: '22:00',
    end: '08:00',
    weekends: true
  })

  const [history, setHistory] = useState<NotificationHistory[]>([
    {
      id: '1',
      type: 'email',
      category: 'system',
      title: 'System Maintenance Scheduled',
      message: 'Scheduled maintenance will occur tonight at 2 AM UTC',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      read: true,
      actionTaken: 'Acknowledged'
    },
    {
      id: '2',
      type: 'push',
      category: 'archive',
      title: 'Archive Process Completed',
      message: 'Your archive #12345 has been successfully processed',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      read: false
    },
    {
      id: '3',
      type: 'in_app',
      category: 'security',
      title: 'New Login Detected',
      message: 'New login from Chrome on Windows',
      timestamp: new Date(Date.now() - 10800000).toISOString(),
      read: false
    }
  ])

  const [activeTab, setActiveTab] = useState<'preferences' | 'history' | 'quiet_hours'>('preferences')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState<string>('all')

  const notificationTypes = [
    { id: 'email', label: 'Email', icon: Mail, description: 'Receive notifications via email' },
    { id: 'push', label: 'Push', icon: Smartphone, description: 'Receive push notifications on mobile devices' },
    { id: 'in_app', label: 'In-App', icon: Bell, description: 'Receive notifications within the application' }
  ]

  const categories = [
    { id: 'system', label: 'System', icon: Settings, color: 'blue' },
    { id: 'archive', label: 'Archive', icon: Archive, color: 'green' },
    { id: 'policy', label: 'Policy', icon: ShieldCheck, color: 'purple' },
    { id: 'security', label: 'Security', icon: AlertTriangle, color: 'red' },
    { id: 'performance', label: 'Performance', icon: Activity, color: 'yellow' }
  ]

  const frequencies = [
    { id: 'immediate', label: 'Immediate', description: 'Send as soon as event occurs' },
    { id: 'hourly', label: 'Hourly', description: 'Batch notifications every hour' },
    { id: 'daily', label: 'Daily', description: 'Daily digest at 9 AM' },
    { id: 'weekly', label: 'Weekly', description: 'Weekly summary on Mondays' }
  ]

  const updatePreference = (id: string, updates: Partial<NotificationPreference>) => {
    setPreferences(prev => 
      prev.map(pref => pref.id === id ? { ...pref, ...updates } : pref)
    )
  }

  const toggleQuietHours = (enabled: boolean) => {
    setQuietHours(prev => ({ ...prev, enabled }))
    setPreferences(prev => 
      prev.map(pref => ({ 
        ...pref, 
        quietHours: { ...pref.quietHours, enabled } 
      }))
    )
  }

  const clearHistory = () => {
    setHistory([])
  }

  const markAsRead = (id: string) => {
    setHistory(prev => 
      prev.map(item => item.id === id ? { ...item, read: true } : item)
    )
  }

  const deleteNotification = (id: string) => {
    setHistory(prev => prev.filter(item => item.id !== id))
  }

  const filteredHistory = history.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.message.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = filterCategory === 'all' || item.category === filterCategory
    return matchesSearch && matchesCategory
  })

  const unreadCount = history.filter(item => !item.read).length

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Notification Preferences</h2>
          <p className="text-muted-foreground">Manage your notification settings and history</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-medium">
            {unreadCount} unread
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-accent/30 p-1 rounded-xl">
        <button
          onClick={() => setActiveTab('preferences')}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            activeTab === 'preferences' 
              ? 'bg-background text-foreground shadow-sm' 
              : 'text-muted-foreground hover:text-foreground'
          )}
        >
          <Settings className="h-4 w-4" />
          Preferences
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            activeTab === 'history' 
              ? 'bg-background text-foreground shadow-sm' 
              : 'text-muted-foreground hover:text-foreground'
          )}
        >
          <Clock className="h-4 w-4" />
          History
        </button>
        <button
          onClick={() => setActiveTab('quiet_hours')}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            activeTab === 'quiet_hours' 
              ? 'bg-background text-foreground shadow-sm' 
              : 'text-muted-foreground hover:text-foreground'
          )}
        >
          <VolumeX className="h-4 w-4" />
          Quiet Hours
        </button>
      </div>

      {/* Preferences Tab */}
      {activeTab === 'preferences' && (
        <div className="space-y-6">
          {/* Notification Types */}
          <div className="bg-card/80 backdrop-blur-sm border border-border/40 rounded-xl p-6">
            <h3 className="font-semibold text-lg mb-4">Notification Channels</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {notificationTypes.map(type => {
                const Icon = type.icon
                const enabledCount = preferences.filter(p => p.type === type.id && p.enabled).length
                return (
                  <div key={type.id} className="border border-border/40 rounded-lg p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 bg-accent/50 rounded-lg">
                        <Icon className="h-5 w-5" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium">{type.label}</h4>
                        <p className="text-xs text-muted-foreground">{type.description}</p>
                      </div>
                      <div className="text-sm font-medium text-muted-foreground">
                        {enabledCount} active
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Category Preferences */}
          <div className="bg-card/80 backdrop-blur-sm border border-border/40 rounded-xl p-6">
            <h3 className="font-semibold text-lg mb-4">Category Preferences</h3>
            <div className="space-y-4">
              {categories.map(category => {
                const categoryPreferences = preferences.filter(p => p.category === category.id)
                return (
                  <div key={category.id} className="border border-border/40 rounded-lg p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <div className={cn('p-2 rounded-lg bg-accent/50')}>
                        <category.icon className={cn('h-5 w-5 text-' + category.color + '-500')} />
                      </div>
                      <h4 className="font-medium">{category.label}</h4>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      {notificationTypes.map(type => {
                        const pref = categoryPreferences.find(p => p.type === type.id)
                        return (
                          <div key={type.id} className="flex items-center justify-between p-3 bg-accent/30 rounded-lg">
                            <div className="flex items-center gap-2">
                              <type.icon className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm">{type.label}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <select
                                value={pref?.frequency || 'immediate'}
                                onChange={(e) => {
                                  if (pref) {
                                    updatePreference(pref.id, { frequency: e.target.value as any })
                                  }
                                }}
                                className="text-xs px-2 py-1 bg-background border border-border/40 rounded"
                                disabled={!pref?.enabled}
                              >
                                {frequencies.map(freq => (
                                  <option key={freq.id} value={freq.id}>{freq.label}</option>
                                ))}
                              </select>
                              <button
                                onClick={() => {
                                  if (pref) {
                                    updatePreference(pref.id, { enabled: !pref.enabled })
                                  }
                                }}
                                className={cn(
                                  'w-10 h-5 rounded-full transition-colors relative',
                                  pref?.enabled ? 'bg-primary' : 'bg-muted'
                                )}
                              >
                                <div className={cn(
                                  'absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform',
                                  pref?.enabled ? 'translate-x-5' : 'translate-x-0.5'
                                )} />
                              </button>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          {/* Search and Filters */}
          <div className="bg-card/80 backdrop-blur-sm border border-border/40 rounded-xl p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search notifications..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-accent/30 border border-border/40 rounded-lg text-sm"
                />
              </div>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="px-4 py-2 bg-accent/30 border border-border/40 rounded-lg text-sm"
              >
                <option value="all">All Categories</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.label}</option>
                ))}
              </select>
              <button
                onClick={clearHistory}
                className="flex items-center gap-2 px-4 py-2 bg-destructive/10 text-destructive rounded-lg hover:bg-destructive/20 transition-colors text-sm"
              >
                <Trash2 className="h-4 w-4" />
                Clear All
              </button>
            </div>
          </div>

          {/* Notification List */}
          <div className="space-y-2">
            {filteredHistory.map(notification => {
              const typeInfo = notificationTypes.find(t => t.id === notification.type)
              const categoryInfo = categories.find(c => c.id === notification.category)
              const TypeIcon = typeInfo?.icon || Bell
              const CategoryIcon = categoryInfo?.icon || Info

              return (
                <div
                  key={notification.id}
                  className={cn(
                    'bg-card/80 backdrop-blur-sm border border-border/40 rounded-xl p-4 transition-colors',
                    !notification.read && 'bg-primary/5 border-primary/20'
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex items-center gap-2">
                      <div className="p-2 bg-accent/50 rounded-lg">
                        <TypeIcon className="h-4 w-4" />
                      </div>
                      <div className="p-1 bg-accent/30 rounded">
                        <CategoryIcon className="h-3 w-3" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium text-sm">{notification.title}</h4>
                          <p className="text-sm text-muted-foreground mt-1">{notification.message}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <span className="text-xs text-muted-foreground">
                              {new Date(notification.timestamp).toLocaleString()}
                            </span>
                            {notification.actionTaken && (
                              <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">
                                {notification.actionTaken}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {!notification.read && (
                            <button
                              onClick={() => markAsRead(notification.id)}
                              className="p-1.5 text-muted-foreground hover:text-foreground transition-colors"
                            >
                              <Check className="h-4 w-4" />
                            </button>
                          )}
                          <button
                            onClick={() => deleteNotification(notification.id)}
                            className="p-1.5 text-muted-foreground hover:text-destructive transition-colors"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
            
            {filteredHistory.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                <Bell className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-sm">No notifications found</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Quiet Hours Tab */}
      {activeTab === 'quiet_hours' && (
        <div className="space-y-6">
          <div className="bg-card/80 backdrop-blur-sm border border-border/40 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  <VolumeX className="h-5 w-5" />
                  Quiet Hours
                </h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Suppress notifications during specific hours
                </p>
              </div>
              <button
                onClick={() => toggleQuietHours(!quietHours.enabled)}
                className={cn(
                  'w-12 h-6 rounded-full transition-colors relative',
                  quietHours.enabled ? 'bg-primary' : 'bg-muted'
                )}
              >
                <div className={cn(
                  'absolute top-1 w-4 h-4 bg-white rounded-full transition-transform',
                  quietHours.enabled ? 'translate-x-7' : 'translate-x-1'
                )} />
              </button>
            </div>

            {quietHours.enabled && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Start Time</label>
                    <input
                      type="time"
                      value={quietHours.start}
                      onChange={(e) => setQuietHours(prev => ({ ...prev, start: e.target.value }))}
                      className="w-full px-3 py-2 bg-accent/30 border border-border/40 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">End Time</label>
                    <input
                      type="time"
                      value={quietHours.end}
                      onChange={(e) => setQuietHours(prev => ({ ...prev, end: e.target.value }))}
                      className="w-full px-3 py-2 bg-accent/30 border border-border/40 rounded-lg"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Timezone</label>
                  <select
                    value={quietHours.timezone}
                    onChange={(e) => setQuietHours(prev => ({ ...prev, timezone: e.target.value }))}
                    className="w-full px-3 py-2 bg-accent/30 border border-border/40 rounded-lg"
                  >
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                    <option value="Europe/London">London</option>
                    <option value="Asia/Tokyo">Tokyo</option>
                  </select>
                </div>

                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="weekends"
                    checked={quietHours.weekends}
                    onChange={(e) => setQuietHours(prev => ({ ...prev, weekends: e.target.checked }))}
                    className="rounded"
                  />
                  <label htmlFor="weekends" className="text-sm">
                    Apply quiet hours on weekends
                  </label>
                </div>

                <div className="p-4 bg-accent/30 rounded-lg">
                  <p className="text-sm text-muted-foreground">
                    <strong>Current quiet hours:</strong> {quietHours.start} - {quietHours.end} ({quietHours.timezone})
                    {quietHours.weekends && ' including weekends'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Hook for managing notifications
export function useNotificationPreferences() {
  const [preferences, setPreferences] = useState<NotificationPreference[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPreferences = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/notifications/preferences')
      if (!response.ok) throw new Error('Failed to fetch preferences')
      const data = await response.json()
      setPreferences(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }

  const updatePreferences = async (updates: NotificationPreference[]) => {
    try {
      const response = await fetch('/api/notifications/preferences', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })
      if (!response.ok) throw new Error('Failed to update preferences')
      setPreferences(updates)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  return {
    preferences,
    isLoading,
    error,
    fetchPreferences,
    updatePreferences
  }
}
