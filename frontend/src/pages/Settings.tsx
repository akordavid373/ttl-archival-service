import React, { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { 
  Settings as SettingsIcon, 
  Bell, 
  Shield, 
  Monitor,
  User,
  Lock, 
  Save, 
  Loader2, 
  CheckCircle2, 
  AlertCircle,
  Info,
  Key,
  Webhook,
  Activity,
  Palette,
  Sun,
  Moon,
  Laptop
} from 'lucide-react'
import { useSettings } from '../context/SettingsContext'
import { useTheme } from '../context/ThemeContext'
import { useNotifications } from '../context/NotificationContext'
import { cn } from '../utils/cn'
import { Preferences } from '../components/settings/Preferences'
import { Notifications } from '../components/settings/Notifications'
import { Account } from '../components/settings/Account'
import { NotificationPreferences } from '../components/NotificationPreferences'
import { SectionTitle, FormField, SwitchField, ThemeCard } from '../components/settings/common'

// Zod validation schemas
const settingsSchema = z.object({
  full_name: z.string().min(2, "Name must be at least 2 characters").optional().nullable(),
  email: z.string().email("Invalid email address").optional().nullable(),
  language: z.string().optional(),
  timezone: z.string().optional(),
  email_notifications: z.boolean().optional(),
  push_notifications: z.boolean().optional(),
  in_app_notifications: z.boolean().optional(),
  notification_frequency: z.string().optional(),
  api_enabled: z.boolean().optional(),
  api_key: z.string().optional().nullable(),
  webhook_url: z.string().url("Invalid URL").or(z.literal("")).optional().nullable(),
  theme: z.string().optional(),
  accent_color: z.string().optional(),
})

export type SettingsFormData = z.infer<typeof settingsSchema>

export function Settings() {
  const { settings, loading, updateSettings } = useSettings()
  const { theme: currentTheme, setTheme } = useTheme()
  const { preferences, updatePreferences } = useNotifications()
  const [activeTab, setActiveTab] = useState<'general' | 'notifications' | 'api' | 'appearance' | 'account'>('general')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors, isDirty }
  } = useForm<SettingsFormData>({
    resolver: zodResolver(settingsSchema),
    defaultValues: settings || {}
  })

  // Watch for changes in theme in the form to sync with ThemeContext
  const formTheme = watch('theme')
  
  useEffect(() => {
    const themeValue = formTheme as 'light' | 'dark' | 'system' | undefined;
    if (themeValue && themeValue !== currentTheme) {
      setTheme(themeValue);
    }
  }, [formTheme, currentTheme, setTheme]);

  useEffect(() => {
    if (settings) {
      reset(settings)
    }
  }, [settings, reset])

  const onSubmit = async (data: SettingsFormData) => {
    try {
      setSaving(true)
      setError(null)
      await updateSettings(data)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err) {
      setError("Failed to save settings. Please try again.")
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <Loader2 className="h-10 w-10 text-primary animate-spin" />
        <p className="text-muted-foreground font-medium animate-pulse">Loading settings...</p>
      </div>
    )
  }

  const tabs = [
    { id: 'general', label: 'General', icon: SettingsIcon },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'api', label: 'API & Connections', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Monitor },
    { id: 'account', label: 'Account', icon: User },
  ] as const

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      <header className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">Settings & Configuration</h2>
        <p className="text-muted-foreground">Manage your workspace preferences, security settings, and notification alerts.</p>
      </header>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Navigation Tabs */}
        <aside className="w-full md:w-64 space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 font-medium text-sm group",
                activeTab === tab.id
                  ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <tab.icon className={cn("h-4 w-4", activeTab === tab.id ? "" : "group-hover:scale-110 transition-transform")} />
              {tab.label}
              {activeTab === tab.id && <div className="ml-auto w-1 h-4 bg-white/40 rounded-full" />}
            </button>
          ))}
        </aside>

        {/* Form Area */}
        <form onSubmit={handleSubmit(onSubmit)} className="flex-1 space-y-6">
          <div className="p-8 rounded-3xl bg-card border border-border/50 shadow-sm relative overflow-hidden min-h-[500px]">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>

            <div className="relative z-10 space-y-8">
              {/* General Tab */}
              {activeTab === 'general' && (
                <Preferences register={register} errors={errors} />
              )}

              {/* Notifications Tab */}
              {activeTab === 'notifications' && (
                <Notifications />
              )}

              {/* API Tab */}
              {activeTab === 'api' && (
                <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
                  <SectionTitle title="API Configuration" icon={Shield} description="Manage external integrations and webhook triggers." />
                  
                  <div className="space-y-6 pt-4">
                    <SwitchField 
                      label="Enable API Access" 
                      description="Allow external services to interact with your archives." 
                      icon={Key}
                      checked={watch('api_enabled') || false}
                      onChange={(val) => setValue('api_enabled', val, { shouldDirty: true })}
                    />
                    
                    <FormField label="API Key" error={errors.api_key?.message}>
                      <div className="relative group">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input 
                          type="password"
                          {...register('api_key')}
                          placeholder="••••••••••••••••••••••••••••••••"
                          className="w-full bg-accent/40 border border-border/40 rounded-xl pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
                        />
                         <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-primary hover:underline">Regenerate</button>
                      </div>
                    </FormField>

                    <FormField label="Webhook URL" error={errors.webhook_url?.message} description="Webhooks are sent as POST requests with JSON payload.">
                       <div className="relative">
                        <Webhook className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input 
                          type="url"
                          {...register('webhook_url')}
                          placeholder="https://your-domain.com/webhook"
                          className="w-full bg-accent/40 border border-border/40 rounded-xl pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
                        />
                      </div>
                    </FormField>
                  </div>
                </div>
              )}

              {/* Appearance Tab */}
              {activeTab === 'appearance' && (
                <div className="space-y-8 animate-in slide-in-from-right-4 duration-300">
                  <SectionTitle title="Visual Preferences" icon={Palette} description="Customize how the application looks and feels." />
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
                    <ThemeCard 
                      id="light" 
                      label="Light" 
                      icon={Sun} 
                      active={watch('theme') === 'light'} 
                      onClick={() => setValue('theme', 'light', { shouldDirty: true })} 
                    />
                    <ThemeCard 
                      id="dark" 
                      label="Dark" 
                      icon={Moon} 
                      active={watch('theme') === 'dark'} 
                      onClick={() => setValue('theme', 'dark', { shouldDirty: true })} 
                    />
                    <ThemeCard 
                      id="system" 
                      label="System" 
                      icon={Laptop} 
                      active={watch('theme') === 'system'} 
                      onClick={() => setValue('theme', 'system', { shouldDirty: true })} 
                    />
                  </div>

                  <div className="space-y-4 pt-8 border-t border-border/40">
                     <p className="text-sm font-semibold">Accent Color</p>
                     <div className="flex gap-4">
                        {['blue', 'indigo', 'emerald', 'rose', 'amber'].map((color) => (
                           <button
                             key={color}
                             type="button"
                             onClick={() => setValue('accent_color', color, { shouldDirty: true })}
                             className={cn(
                               "w-10 h-10 rounded-full border-2 transition-all p-0.5",
                               watch('accent_color') === color ? "border-primary scale-110 shadow-lg shadow-primary/20" : "border-transparent"
                             )}
                           >
                             <div className={cn("w-full h-full rounded-full", `bg-${color}-500`)} style={{ 
                               backgroundColor: 
                                  color === 'blue' ? '#3b82f6' : 
                                  color === 'indigo' ? '#6366f1' : 
                                  color === 'emerald' ? '#10b981' : 
                                  color === 'rose' ? '#f43f5e' : 
                                  '#f59e0b'
                             }}></div>
                           </button>
                        ))}
                     </div>
                  </div>
                </div>
              )}

              {/* Account Tab */}
              {activeTab === 'account' && (
                <Account register={register} errors={errors} />
              )}
            </div>
          </div>

          {/* Action Bar */}
          <div className="flex items-center justify-between p-6 rounded-2xl bg-card border border-border/50 sticky bottom-4 z-50 shadow-2xl backdrop-blur-md bg-card/90">
             <div className="flex items-center gap-3">
                {saved && (
                   <div className="flex items-center gap-2 text-emerald-500 animate-in fade-in slide-in-from-left-2 duration-300">
                      <CheckCircle2 className="h-5 w-5" />
                      <span className="text-sm font-bold">Preferences Saved Successfully</span>
                   </div>
                )}
                {error && (
                   <div className="flex items-center gap-2 text-rose-500 animate-in fade-in slide-in-from-left-2 duration-300">
                      <AlertCircle className="h-5 w-5" />
                      <span className="text-sm font-bold">{error}</span>
                   </div>
                )}
                {!saved && !error && (
                   <p className="text-xs text-muted-foreground font-medium">
                     {isDirty ? "Account has unsaved changes" : "System settings are up to date"}
                   </p>
                )}
             </div>
             <div className="flex gap-4">
                <button 
                   type="button" 
                   onClick={() => reset(settings || {})}
                   disabled={!isDirty || saving}
                   className="px-6 py-2.5 text-sm font-bold text-muted-foreground hover:text-foreground disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                   Reset Changes
                </button>
                <button 
                   type="submit" 
                   disabled={!isDirty || saving}
                   className={cn(
                      "px-8 py-2.5 bg-primary text-primary-foreground font-bold text-sm rounded-xl shadow-lg shadow-primary/20 transition-all duration-300 flex items-center gap-2 disabled:bg-muted disabled:shadow-none disabled:text-muted-foreground group",
                      saving ? "opacity-80" : "hover:scale-[1.05]"
                   )}
                >
                   {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4 group-hover:scale-110 transition-transform" />}
                   {saving ? "Processing..." : "Save Preferences"}
                </button>
             </div>
          </div>
        </form>
      </div>
    </div>
  )
}
