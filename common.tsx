import React from 'react'
import { AlertCircle } from 'lucide-react'
import { cn } from '../../lib/utils'

export function SectionTitle({ title, icon: Icon, description }: { title: string, icon: React.ElementType, description: string }) {
  return (
    <div className="space-y-1">
      <div className="flex items-center gap-3 text-primary">
         <Icon className="h-5 w-5" />
         <h3 className="font-bold text-xl tracking-tight text-foreground">{title}</h3>
      </div>
      <p className="text-xs text-muted-foreground font-medium">{description}</p>
    </div>
  )
}

export function FormField({ label, children, error, description }: { label: string, children: React.ReactNode, error?: string, description?: string }) {
  return (
    <div className="space-y-2">
      <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">{label}</label>
      {children}
      {error && <p className="text-[10px] font-bold text-rose-500 flex items-center gap-1"><AlertCircle className="h-3 w-3" /> {error}</p>}
      {description && !error && <p className="text-[10px] text-muted-foreground/60 font-medium">{description}</p>}
    </div>
  )
}

export function SwitchField({ label, description, icon: Icon, checked, onChange }: { label: string, description: string, icon: React.ElementType, checked: boolean, onChange: (val: boolean) => void }) {
  return (
    <div className="flex items-center justify-between p-5 rounded-2xl bg-accent/20 border border-transparent hover:border-border/40 transition-all group">
       <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-card border border-border/50 flex items-center justify-center text-muted-foreground group-hover:text-primary transition-colors">
             <Icon className="h-5 w-5" />
          </div>
          <div className="space-y-0.5">
             <p className="text-sm font-bold">{label}</p>
             <p className="text-[10px] text-muted-foreground font-medium">{description}</p>
          </div>
       </div>
       <button 
         type="button" 
         onClick={() => onChange(!checked)}
         className={cn(
           "w-12 h-6 rounded-full transition-all relative",
           checked ? "bg-primary" : "bg-muted"
         )}
       >
          <div className={cn(
             "absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-all shadow-sm",
             checked ? "translate-x-6" : "translate-x-0"
          )} />
       </button>
    </div>
  )
}

export function ThemeCard({ label, icon: Icon, active, onClick }: { id: string, label: string, icon: React.ElementType, active: boolean, onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "p-6 rounded-2xl border-2 flex flex-col items-center gap-4 transition-all duration-300",
        active 
          ? "border-primary bg-primary/5 shadow-2xl shadow-primary/10 scale-105" 
          : "border-border/40 hover:border-border hover:bg-accent/30"
      )}
    >
      <div className={cn(
        "w-12 h-12 rounded-xl flex items-center justify-center transition-colors",
        active ? "bg-primary text-primary-foreground shadow-lg shadow-primary/30" : "bg-accent text-muted-foreground"
      )}>
        <Icon className="h-6 w-6" />
      </div>
      <p className={cn("text-xs font-bold uppercase tracking-widest", active ? "text-primary" : "text-muted-foreground")}>{label}</p>
    </button>
  )
}