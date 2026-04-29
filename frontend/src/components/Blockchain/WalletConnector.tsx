import React from "react";
import {
  Wallet,
  LogOut,
  ShieldCheck,
  Globe,
  Link2,
  AlertCircle,
} from "lucide-react";
import { WalletInfo, NetworkType } from "../../types/blockchain";
import { cn } from "../../utils/cn";

interface WalletConnectorProps {
  wallet: WalletInfo | null;
  isLoading: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
  onNetworkChange: (network: NetworkType) => void;
}

export function WalletConnector({
  wallet,
  isLoading,
  onConnect,
  onDisconnect,
  onNetworkChange,
}: WalletConnectorProps) {
  return (
    <div className="p-8 rounded-[2.5rem] bg-card border border-border/50 shadow-sm relative overflow-hidden group">
      {/* Background Decorative Elements */}
      <div className="absolute -top-12 -right-12 w-48 h-48 bg-primary/5 rounded-full blur-3xl group-hover:scale-125 transition-transform duration-700"></div>

      <div className="flex flex-col h-full relative z-10">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div
              className={cn(
                "p-4 rounded-2xl shadow-lg transition-all duration-500",
                wallet?.connected
                  ? "bg-emerald-500/10 text-emerald-500 shadow-emerald-500/10"
                  : "bg-primary/10 text-primary shadow-primary/10",
              )}
            >
              <Wallet className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold tracking-tight">
                Identity Provider
              </h3>
              <p className="text-[10px] text-muted-foreground uppercase font-extrabold tracking-widest mt-1">
                Freighter Wallet Connection
              </p>
            </div>
          </div>

          {wallet?.connected && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 text-emerald-500 rounded-full border border-emerald-500/20 shadow-sm">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="text-[10px] font-bold uppercase tracking-wider">
                Connected
              </span>
            </div>
          )}
        </div>

        {!wallet?.connected ? (
          <div className="space-y-6">
            <p className="text-sm text-muted-foreground leading-relaxed">
              Connect your Stellar wallet to authorize archival operations and
              manage on-chain storage policies securely.
            </p>
            <button
              onClick={onConnect}
              disabled={isLoading}
              className="w-full py-4 bg-primary text-primary-foreground font-extrabold text-sm rounded-2xl shadow-xl shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-3 disabled:opacity-50"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></div>
              ) : (
                <>
                  <Link2 className="h-5 w-5" />
                  Connect Freighter Wallet
                </>
              )}
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="p-5 rounded-2xl bg-accent/20 border border-border/40 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest leading-none">
                  Wallet Address
                </span>
                <span className="text-[10px] font-bold text-primary hover:underline cursor-pointer">
                  Explore →
                </span>
              </div>
              <p className="text-xs font-mono font-bold break-all leading-relaxed text-foreground/80">
                {wallet.address}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-accent/10 border border-border/20">
                <p className="text-[10px] font-bold text-muted-foreground uppercase opacity-60 mb-1">
                  Network
                </p>
                <p className="text-xs font-extrabold uppercase tracking-widest text-primary">
                  {wallet.network}
                </p>
              </div>
              <div className="p-4 rounded-2xl bg-accent/10 border border-border/20">
                <p className="text-[10px] font-bold text-muted-foreground uppercase opacity-60 mb-1">
                  Status
                </p>
                <p className="text-xs font-extrabold text-emerald-500">
                  Authenticated
                </p>
              </div>
            </div>

            <div className="pt-2 flex gap-3">
              <button
                onClick={() =>
                  onNetworkChange(
                    wallet.network === "testnet" ? "public" : "testnet",
                  )
                }
                className="flex-1 py-4 bg-secondary text-secondary-foreground font-bold text-xs rounded-2xl border border-border/50 hover:bg-accent transition-all flex items-center justify-center gap-2"
              >
                <Globe className="h-4 w-4" />
                Switch Network
              </button>
              <button
                onClick={onDisconnect}
                className="p-4 text-rose-500 border border-rose-500/20 rounded-2xl hover:bg-rose-500/10 transition-all flex items-center justify-center"
                title="Disconnect Wallet"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}

        <div className="mt-8 pt-8 border-t border-border/20">
          <div className="flex items-start gap-3 p-4 rounded-2xl bg-amber-500/5 border border-amber-500/10">
            <AlertCircle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
            <p className="text-[10px] font-bold text-amber-600/80 leading-relaxed uppercase tracking-tight">
              All on-chain operations incur a network fee in XLM. Ensure your
              wallet is funded.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
