import React from 'react'
import { UseFormRegister, FieldErrors } from 'react-hook-form'
import { Globe, Info } from 'lucide-react'
import { SettingsFormData } from '../../pages/Settings'
import { SectionTitle, FormField } from './common'

interface PreferencesProps {
  register: UseFormRegister<SettingsFormData>
  errors: FieldErrors<SettingsFormData>
}

export function Preferences({ register, errors }: PreferencesProps) {
  return (
    <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
      <SectionTitle title="Application Preferences" icon={Globe} description="System-level settings and regional defaults." />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
        <FormField label="Language" error={errors.language?.message}>
          <select 
            {...register('language')}
            className="w-full bg-accent/40 border border-border/40 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
          >
            <option value="en">English (US)</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
            <option value="de">Deutsch</option>
          </select>
        </FormField>

        <FormField label="Timezone" error={errors.timezone?.message}>
          <select 
            {...register('timezone')}
            className="w-full bg-accent/40 border border-border/40 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
          >
            <option value="UTC">UTC (GMT+0)</option>
            <option value="EST">Eastern Time (ET)</option>
            <option value="PST">Pacific Time (PT)</option>
            <option value="CET">Central European Time (CET)</option>
          </select>
        </FormField>
      </div>

      <div className="p-4 rounded-2xl bg-primary/5 border border-primary/10 flex gap-4 mt-8">
        <Info className="h-5 w-5 text-primary shrink-0" />
        <p className="text-xs text-primary/80 leading-relaxed font-medium">
          Changing language and timezone will affect timestamp generation and verification reports across the application.
        </p>
      </div>
    </div>
  )
}