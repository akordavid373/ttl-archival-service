import React from 'react';
import { History, Box, ArrowUpRight, ExternalLink, RefreshCw, Zap, CheckCircle2, AlertCircle } from 'lucide-react';
import { TransactionRecord } from '../../types/blockchain';
import { cn } from '../../utils/cn';

interface TransactionHistoryProps {
  transactions: TransactionRecord[];
  isLoading: boolean;
  onRefresh: () => void;
  onViewDetails: (tx: TransactionRecord) => void;
}

export function TransactionHistory({ transactions, isLoading, onRefresh, onViewDetails }: TransactionHistoryProps) {
  return (
    <div className="flex-1 space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
      <div className="bg-card border border-border/50 rounded-[2.5rem] overflow-hidden shadow-sm h-full">
        {/* Header Section */}
        <div className="p-8 border-b border-border/40 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-6 bg-accent/5">
           <h3 className="font-bold text-xl flex items-center gap-4">
             <div className="p-3 rounded-2xl bg-primary/10 text-primary shadow-lg shadow-primary/5">
                <History className="h-6 w-6 transition-transform group-hover:scale-110" />
             </div>
             Unified Ledger Activity
           </h3>
           <div className="flex items-center gap-3">
             <button 
               onClick={onRefresh}
               disabled={isLoading}
               className="p-3 bg-secondary text-secondary-foreground rounded-2xl border border-border/50 hover:bg-accent transition-all group disabled:opacity-50"
             >
               <RefreshCw className={cn("h-5 w-5 transition-transform", isLoading && "animate-spin")} />
             </button>
             <div className="flex items-center gap-2 px-4 py-2 bg-amber-500/10 text-amber-500 rounded-full border border-amber-500/20 animate-pulse transition-all">
                <Zap className="h-4 w-4 fill-amber-500" />
                <span className="text-[10px] font-extrabold uppercase tracking-widest leading-none">Live Network Monitoring</span>
             </div>
           </div>
        </div>

        {/* Transaction Feed */}
        <div className="p-8 overflow-y-auto max-h-[600px] min-h-[400px] custom-scrollbar">
           {isLoading && transactions.length === 0 ? (
              <div className="space-y-4">
                 {Array(5).fill(0).map((_, i) => (
                   <div key={i} className="h-20 bg-accent/10 rounded-2xl animate-pulse"></div>
                 ))}
              </div>
           ) : transactions.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-24 text-center space-y-4">
                 <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center border border-border/40">
                    <Box className="h-6 w-6 text-muted-foreground opacity-40 shrink-0" />
                 </div>
                 <p className="text-sm font-bold text-muted-foreground opacity-60">No recent on-chain activity detected.</p>
              </div>
           ) : (
              <div className="space-y-4">
                 {transactions.map((tx) => (
                   <div 
                      key={tx.id} 
                      onClick={() => onViewDetails(tx)}
                      className="group p-5 rounded-2xl bg-accent/20 hover:bg-accent/40 transition-all border border-transparent hover:border-primary/20 cursor-pointer flex items-center justify-between shadow-sm hover:shadow-xl hover:shadow-primary/5 translate-y-0 hover:-translate-y-1"
                   >
                     <div className="flex items-center gap-5">
                       <div className={cn(
                          "w-12 h-12 rounded-2xl bg-card flex items-center justify-center border border-border/50 shadow-inner transition-transform group-hover:scale-110 duration-500",
                          tx.status === 'Confirmed' ? 'text-primary' : tx.status === 'Failed' ? 'text-rose-500' : 'text-amber-500 animate-pulse'
                       )}>
                          {tx.status === 'Confirmed' ? <CheckCircle2 className="h-6 w-6" /> : tx.status === 'Failed' ? <AlertCircle className="h-6 w-6" /> : <Box className="h-6 w-6" />}
                       </div>
                       <div className="min-w-0">
                         <div className="flex items-center gap-2 mb-1">
                            <p className="text-[10px] font-extrabold text-muted-foreground uppercase tracking-widest leading-none shrink-0 truncate">{tx.type}</p>
                            <span className="h-1 w-1 bg-border/60 rounded-full shrink-0"></span>
                            <p className="text-[10px] text-muted-foreground font-medium shrink-0 italic">{tx.created_at}</p>
                         </div>
                         <p className="text-sm font-bold truncate max-w-[200px] sm:max-w-md lg:max-w-[400px] group-hover:text-primary transition-colors flex items-center gap-2">
                           {tx.hash}
                           <ArrowUpRight className="h-3.5 w-3.5 opacity-0 group-hover:opacity-100 transition-all group-hover:translate-x-1 group-hover:-translate-y-1" />
                         </p>
                       </div>
                     </div>
                     
                     <div className="flex items-center gap-6 shrink-0">
                        <div className="hidden md:flex flex-col items-end">
                           <span className="text-[10px] font-bold text-muted-foreground uppercase leading-none mb-1 shrink-0">Fee Charged</span>
                           <span className="text-xs font-mono font-bold leading-none shrink-0">{tx.fee} <span className="text-[10px] text-muted-foreground">XLM</span></span>
                        </div>
                        <a 
                          href={`https://stellar.expert/explorer/testnet/tx/${tx.hash}`}
                          target="_blank"
                          rel="noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="p-3 text-muted-foreground hover:bg-primary/5 hover:text-primary rounded-xl transition-all border border-transparent hover:border-primary/10 shadow-sm shrink-0"
                          title="View on Explorer"
                        >
                           <ExternalLink className="h-4.5 w-4.5" />
                        </a>
                     </div>
                   </div>
                 ))}
                 
                 <div className="pt-8 border-t border-border/20 flex items-center justify-center">
                    <p className="text-xs text-muted-foreground font-medium italic">
                       Displaying latest entries anchored on the Stellar Distributed Ledger.
                    </p>
                 </div>
              </div>
           )}
        </div>
      </div>
    </div>
  );
}
