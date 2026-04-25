import React from 'react'
import { Bell } from 'lucide-react'
import { useNotifications } from '../../context/NotificationContext'
import { NotificationPreferences as NotificationPreferencesComponent } from '../notifications'
import { SectionTitle } from './common'

export function Notifications() {
  const { preferences, updatePreferences } = useNotifications()

  return (
    <div className="space-y-8 animate-in slide-in-from-right-4 duration-300">
      <SectionTitle title="Notification Settings" icon={Bell} description="Control how and when you receive archival updates." />
      
      <div className="pt-4">
        <NotificationPreferencesComponent 
          preferences={preferences}
          onChange={updatePreferences}
        />
      </div>
    </div>
  )
}