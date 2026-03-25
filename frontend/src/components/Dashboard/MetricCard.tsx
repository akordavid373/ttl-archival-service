import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '../../utils/cn';

interface MetricCardProps {
  label: string;
  value: string | number;
  change?: string;
  icon: LucideIcon;
  color: string;
  bg: string;
}

export function MetricCard({ label, value, change, icon: Icon, color, bg }: MetricCardProps) {
  return (
    <div className="group p-6 rounded-3xl bg-card border border-border/50 hover:border-primary/20 hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <div className={cn("p-3 rounded-2xl transition-transform shadow-inner group-hover:scale-110", bg, color)}>
          <Icon className="h-6 w-6" />
        </div>
        {change && (
          <span className={cn(
            "text-[10px] font-bold px-3 py-1 rounded-full border",
            change.startsWith('+') 
              ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' 
              : 'bg-muted text-muted-foreground border-border/40'
          )}>
            {change}
          </span>
        )}
      </div>
      <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest leading-relaxed">{label}</p>
      <p className="text-2xl font-bold tracking-tight mt-1 truncate">{value}</p>
    </div>
  );
}
