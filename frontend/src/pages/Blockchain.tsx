import React from 'react'
import { Database, Link2, Share2, ShieldCheck, Activity, Globe, Zap, Cpu, History, RefreshCcw, Box } from 'lucide-react'

export function Blockchain() {
  const transactions = [
    { hash: '0x3a4b...1c2d', type: 'Policy Commit', status: 'Confirmed', network: 'Stellar Mainnet', time: '2m ago' },
    { hash: '0x9e8f...f5a6', type: 'Archive Verification', status: 'Confirmed', network: 'Stellar Mainnet', time: '14m ago' },
    { hash: '0x7c8a...3d4f', type: 'TTL Update', status: 'Pending', network: 'Stellar Testnet', time: '36s ago' },
    { hash: '0x1b2c...9e8f', type: 'Policy Commit', status: 'Confirmed', network: 'Stellar Mainnet', time: '1h ago' },
  ]

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">Blockchain Ledger</h2>
        <p className="text-muted-foreground flex items-center gap-2">
          <Globe className="h-4 w-4 text-primary animate-spin-slow" />
          Synchronized with Stellar Network. Consensus reached.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Network Height', value: '1,284,591', icon: Cpu, color: 'text-blue-500' },
          { label: 'Anchored Archives', value: '842', icon: ShieldCheck, color: 'text-emerald-500' },
          { label: 'Transactions (24h)', value: '124', icon: Activity, color: 'text-purple-500' },
        ].map((stat, i) => (
          <div key={i} className="p-8 rounded-3xl bg-card border border-border/50 hover:border-primary/20 hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-2xl bg-accent ${stat.color} group-hover:scale-110 transition-transform`}>
                <stat.icon className="h-6 w-6" />
              </div>
              <div>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">{stat.label}</p>
                <p className="text-2xl font-bold tracking-tight">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        <div className="lg:col-span-3 space-y-6">
          <div className="p-8 rounded-3xl bg-card border border-border/50 shadow-sm overflow-hidden relative group">
             <div className="flex items-center justify-between mb-8 overflow-hidden">
                <h3 className="font-bold text-lg flex items-center gap-3">
                  <History className="h-5 w-5 text-primary" />
                  Live Ledger Activity
                </h3>
                <button className="flex items-center gap-2 text-xs font-bold text-muted-foreground hover:text-primary transition-colors">
                  <RefreshCcw className="h-3 w-3" />
                  Sync Status
                </button>
             </div>
             <div className="space-y-4">
               {transactions.map((t, i) => (
                 <div key={i} className="p-4 rounded-2xl bg-accent/20 hover:bg-accent/40 transition-colors border border-transparent hover:border-border/40 group cursor-pointer flex items-center justify-between overflow-hidden">
                   <div className="flex items-center gap-4 overflow-hidden">
                     <div className="w-10 h-10 rounded-xl bg-card flex items-center justify-center border border-border/50 shadow-sm overflow-hidden">
                       <Box className={`h-5 w-5 ${t.status === 'Confirmed' ? 'text-primary' : 'text-amber-500 animate-pulse'}`} />
                     </div>
                     <div className="overflow-hidden">
                       <p className="text-xs font-bold text-muted-foreground uppercase tracking-tighter mb-1">{t.type}</p>
                       <p className="text-sm font-semibold truncate max-w-[120px] lg:max-w-[200px]">{t.hash}</p>
                     </div>
                   </div>
                   <div className="flex items-center gap-6 overflow-hidden">
                      <div className="hidden sm:block overflow-hidden">
                        <p className="text-[10px] text-muted-foreground font-bold text-right">{t.network}</p>
                        <p className="text-[10px] text-muted-foreground font-medium text-right">{t.time}</p>
                      </div>
                      <span className={`px-3 py-1 text-[10px] font-bold rounded-full border ${t.status === 'Confirmed' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' : 'bg-amber-500/10 text-amber-500 border-amber-500/20'}`}>
                        {t.status}
                      </span>
                   </div>
                 </div>
               ))}
             </div>
             <button className="w-full mt-6 py-2.5 text-xs font-bold text-primary hover:text-primary/80 transition-colors hover:underline">
               Explore Full Ledger History
             </button>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6 overflow-hidden">
          <div className="p-8 rounded-3xl bg-primary text-primary-foreground shadow-2xl shadow-primary/30 relative overflow-hidden group h-full">
            <div className="absolute -top-12 -right-12 w-48 h-48 bg-white/10 rounded-full blur-3xl group-hover:scale-125 transition-transform duration-700"></div>
            <div className="absolute -bottom-12 -left-12 w-48 h-48 bg-black/10 rounded-full blur-3xl"></div>
            <div className="relative z-10 flex flex-col h-full overflow-hidden">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-md border border-white/30 rounded-2xl flex items-center justify-center mb-6 overflow-hidden">
                <Link2 className="h-6 w-6" />
              </div>
              <h3 className="text-2xl font-bold mb-4 tracking-tight leading-tight">Trustless Proofs & Integrity Verification</h3>
              <p className="text-sm text-primary-foreground/80 leading-relaxed mb-8">
                Every policy action and archive record is cryptographically signed and anchored to the Stellar blockchain, ensuring immutable proof of existence.
              </p>
              <div className="mt-auto space-y-4 overflow-hidden">
                <div className="p-4 rounded-2xl bg-white/10 border border-white/20 backdrop-blur-md overflow-hidden">
                  <div className="flex items-center justify-between mb-2 overflow-hidden">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-primary-foreground/60">Node Integrity</span>
                    <span className="text-[10px] font-bold bg-white text-primary px-2 py-0.5 rounded-full">Secure</span>
                  </div>
                  <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                    <div className="w-[98%] bg-white h-full rounded-full"></div>
                  </div>
                </div>
                <button className="w-full py-4 bg-white text-primary font-bold text-sm rounded-2xl flex items-center justify-center gap-2 hover:bg-white/90 transition-all duration-300">
                  <Share2 className="h-4 w-4" />
                  View Public Node Stats
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
