import React from 'react';
import { ShieldCheck, Database, Clock, Fingerprint, Activity, Zap, Cpu, History } from 'lucide-react';
import { BlockchainStatus, ContractState } from '../../types/blockchain';
import { cn } from '../../utils/cn';

interface ContractStatusProps {
  status: BlockchainStatus | null;
  state: ContractState | null;
  isLoading: boolean;
}

export function ContractStatus({ status, state, isLoading }: ContractStatusProps) {
  if (isLoading || !status || !state) {
    return (
      <div className="p-8 rounded-[2.5rem] bg-card border border-border/50 shadow-sm animate-pulse space-y-12 h-full min-h-[400px]">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-accent/20 rounded-2xl"></div>
          <div className="space-y-2 flex-1">
            <div className="h-4 bg-accent/20 rounded w-1/3"></div>
            <div className="h-3 bg-accent/20 rounded w-1/4"></div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
           <div className="h-24 bg-accent/10 rounded-3xl"></div>
           <div className="h-24 bg-accent/10 rounded-3xl"></div>
        </div>
        <div className="h-40 bg-accent/5 rounded-3xl"></div>
      </div>
    );
  }

  return (
    <div className="p-8 rounded-[2.5rem] bg-card border border-border/50 shadow-sm relative overflow-hidden group h-full">
      {/* Network Health Header */}
      <div className="flex items-center justify-between mb-10">
        <div className="flex items-center gap-4">
          <div className={cn(
             "p-4 rounded-2xl shadow-lg transition-all duration-500",
             status.status === 'Healthy' ? "bg-emerald-500/10 text-emerald-500 shadow-emerald-500/10" : "bg-amber-500/10 text-amber-500 shadow-amber-500/10"
          )}>
            <Fingerprint className="h-6 w-6 transition-transform group-hover:scale-110" />
          </div>
          <div>
            <h3 className="text-xl font-bold tracking-tight">Contract Integrity</h3>
            <p className="text-[10px] text-muted-foreground uppercase font-extrabold tracking-widest mt-1">Stellar Virtual Machine (SVM)</p>
          </div>
        </div>
        <div className={cn(
           "px-4 py-2 rounded-2xl text-[10px] font-bold uppercase tracking-widest border transition-all",
           status.status === 'Healthy' ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20" : "bg-amber-500/10 text-amber-500 border-amber-500/20"
        )}>
          {status.status}
        </div>
      </div>

      <div className="space-y-10">
        {/* Core Metrics */}
        <div className="grid grid-cols-2 gap-6">
           <div className="p-5 rounded-3xl bg-accent/10 border border-border/40 hover:bg-accent/20 transition-colors group">
              <label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2 mb-3">
                <Database className="h-3 w-3" />
                Total Anchored
              </label>
              <p className="text-2xl font-extrabold tracking-tighter leading-none">{state.total_archives.toLocaleString()}</p>
              <p className="text-[10px] text-muted-foreground font-medium mt-2">Verified Proofs</p>
           </div>
           <div className="p-5 rounded-3xl bg-accent/10 border border-border/40 hover:bg-accent/20 transition-colors group">
              <label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2 mb-3">
                <ShieldCheck className="h-3 w-3" />
                Active Policies
              </label>
              <p className="text-2xl font-extrabold tracking-tighter leading-none">{state.active_policies}</p>
              <p className="text-[10px] text-muted-foreground font-medium mt-2">Compliance Nodes</p>
           </div>
        </div>

        {/* Network Specification */}
        <div className="space-y-4">
           <label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
             <Activity className="h-3.5 w-3.5 text-primary" />
             Live Network Telemetry
           </label>
           <div className="space-y-3">
             <div className="flex items-center justify-between p-4 bg-muted/5 rounded-2xl border border-border/20">
                <span className="text-xs text-muted-foreground flex items-center gap-2">
                   <Cpu className="h-3.5 w-3.5" /> Network Height
                </span>
                <span className="text-xs font-bold font-mono text-primary">{status.network_height.toLocaleString()}</span>
             </div>
             <div className="flex items-center justify-between p-4 bg-muted/5 rounded-2xl border border-border/20">
                <span className="text-xs text-muted-foreground flex items-center gap-2">
                   <Clock className="h-3.5 w-3.5" /> Average Close
                </span>
                <span className="text-xs font-bold font-mono">{status.avg_close_time}s</span>
             </div>
             <div className="flex items-center justify-between p-4 bg-muted/5 rounded-2xl border border-border/20">
                <span className="text-xs text-muted-foreground flex items-center gap-2">
                   <Zap className="h-3.5 w-3.5" /> Contract Version
                </span>
                <span className="text-xs font-extrabold uppercase tracking-widest text-primary">v{state.version}</span>
             </div>
           </div>
        </div>

        {/* Contract ID */}
        <div className="space-y-3">
           <label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
             <History className="h-3.5 w-3.5" />
             Smart Contract ID
           </label>
           <div className="p-4 bg-primary/5 rounded-2xl border border-primary/10 font-mono text-[11px] text-primary/80 break-all leading-relaxed relative group hover:bg-primary/10 transition-colors">
              {status.contract_id}
              <button className="absolute inset-y-0 right-0 px-4 opacity-0 group-hover:opacity-100 transition-opacity font-bold uppercase tracking-widest">
                Copy
              </button>
           </div>
           <p className="text-[10px] text-muted-foreground font-medium italic">
             All state transitions are validated by Soroban validators on the {status.network.toUpperCase()} network.
           </p>
        </div>
      </div>
    </div>
  );
}
