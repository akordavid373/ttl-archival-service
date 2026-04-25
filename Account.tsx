import React, { useState } from 'react'
import { useForm, UseFormRegister, FieldErrors } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { User, Lock, Shield } from 'lucide-react'
import { SettingsFormData } from '../../pages/Settings'
import { SectionTitle, FormField } from './common'

const passwordChangeSchema = z.object({
  currentPassword: z.string().min(1, "Current password is required"),
  newPassword: z.string().min(8, "Password must be at least 8 characters"),
  confirmPassword: z.string()
}).refine(data => data.newPassword === data.confirmPassword, {
  message: "New passwords don't match",
  path: ["confirmPassword"],
});

type PasswordChangeFormData = z.infer<typeof passwordChangeSchema>;

function PasswordChangeModal({ onClose }: { onClose: () => void }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<PasswordChangeFormData>({
    resolver: zodResolver(passwordChangeSchema)
  });

  const onSubmit = async (data: PasswordChangeFormData) => {
    setIsSubmitting(true);
    setApiError(null);
    try {
      // API call to PUT /api/v1/user/password
      const response = await fetch('/api/v1/user/password', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_password: data.currentPassword,
          new_password: data.newPassword
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to change password.');
      }
      
      onClose();

    } catch (error: any) {
      setApiError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-[100] flex items-center justify-center" onClick={onClose}>
      <div className="bg-card p-8 rounded-2xl shadow-2xl w-full max-w-md" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-bold">Change Password</h3>
        <p className="text-sm text-muted-foreground mt-1">Update your account password. After saving, you may be logged out.</p>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mt-6">
          <FormField label="Current Password" error={errors.currentPassword?.message}>
            <input type="password" {...register('currentPassword')} className="w-full bg-accent/40 border border-border/40 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20" />
          </FormField>
          <FormField label="New Password" error={errors.newPassword?.message}>
            <input type="password" {...register('newPassword')} className="w-full bg-accent/40 border border-border/40 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20" />
          </FormField>
          <FormField label="Confirm New Password" error={errors.confirmPassword?.message}>
            <input type="password" {...register('confirmPassword')} className="w-full bg-accent/40 border border-border/40 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20" />
          </FormField>
          
          {apiError && <p className="text-sm text-rose-500">{apiError}</p>}

          <div className="flex justify-end gap-4 pt-4">
            <button type="button" onClick={onClose} disabled={isSubmitting} className="px-4 py-2 text-sm font-bold text-muted-foreground disabled:opacity-50">Cancel</button>
            <button type="submit" disabled={isSubmitting} className="px-6 py-2 bg-primary text-primary-foreground font-bold text-sm rounded-xl disabled:opacity-50">
              {isSubmitting ? 'Updating...' : 'Update Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface AccountProps {
  register: UseFormRegister<SettingsFormData>
  errors: FieldErrors<SettingsFormData>
}

export function Account({ register, errors }: AccountProps) {
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false)

  return (
    <>
      <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
        <SectionTitle title="Account Management" icon={User} description="Manage your profile information and account security." />
        
        <div className="flex items-center gap-6 mb-8 pt-4">
           <div className="w-20 h-20 rounded-3xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-inner">
              <User className="h-10 w-10" />
           </div>
           <div className="space-y-1">
              <p className="font-bold text-lg">David Akoro</p>
              <p className="text-xs text-muted-foreground font-medium">System Administrator • Since Jan 2024</p>
              <button type="button" className="text-[10px] font-bold text-primary hover:underline">Change Avatar</button>
           </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField label="Full Name" error={errors.full_name?.message}>
            <input 
              {...register('full_name')}
              className="w-full bg-accent/40 border border-border/40 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
            />
          </FormField>

          <FormField label="Email Address" error={errors.email?.message}>
            <input 
              {...register('email')}
              className="w-full bg-accent/40 border border-border/40 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
            />
          </FormField>
        </div>

        <div className="pt-8 mt-8 border-t border-border/40 flex flex-col gap-4">
          <button type="button" onClick={() => setIsPasswordModalOpen(true)} className="text-sm font-semibold flex items-center gap-2 text-primary hover:underline w-fit">
             <Lock className="h-4 w-4" />
             Change Account Password
          </button>
          <button type="button" className="text-sm font-semibold flex items-center gap-2 text-rose-500 hover:underline w-fit">
             <Shield className="h-4 w-4" />
             Two-Factor Authentication (Disabled)
          </button>
        </div>
      </div>

      {isPasswordModalOpen && <PasswordChangeModal onClose={() => setIsPasswordModalOpen(false)} />}
    </>
  )
}