import React, { useState, useEffect, useCallback } from "react";
import {
  Globe,
  Activity,
  Zap,
  ShieldCheck,
  Cpu,
  RefreshCcw,
  BarChart3,
} from "lucide-react";
import { BlockchainVolumeChart } from "../components/charts/BlockchainVolumeChart";
import { WalletConnector } from "../components/Blockchain/WalletConnector";
import { ContractStatus } from "../components/Blockchain/ContractStatus";
import { TransactionHistory } from "../components/Blockchain/TransactionHistory";
import {
  BlockchainStatus,
  TransactionRecord,
  WalletInfo,
  ContractState,
  NetworkType,
} from "../types/blockchain";
import { useNotifications } from "../context/NotificationContext";
import { cn } from "../utils/cn";
import axios from "axios";

const API_BASE_URL = (import.meta as any).env.VITE_API_URL || "/api/v1";

export function Blockchain() {
  const [isLoading, setIsLoading] = useState(true);
  const [isTxLoading, setIsTxLoading] = useState(false);
  const [status, setStatus] = useState<BlockchainStatus | null>(null);
  const [state, setState] = useState<ContractState | null>(null);
  const [transactions, setTransactions] = useState<TransactionRecord[]>([]);
  const [wallet, setWallet] = useState<WalletInfo | null>(null);
  const { addNotification } = useNotifications();

  // Fetch Blockchain & Contract Status
  const fetchStatus = useCallback(async () => {
    try {
      const resp = await axios.get(`${API_BASE_URL}/blockchain/status`);
      setStatus(resp.data.status);
      setState(resp.data.state);
    } catch (err) {
      console.error("Failed to fetch blockchain status:", err);
      if ((import.meta as any).env.DEV) {
        setStatus({
          network: (wallet?.network as any) || "testnet",
          horizon_url: "https://horizon-testnet.stellar.org",
          contract_id:
            "C" + Math.random().toString(36).substr(2, 55).toUpperCase(),
          network_height: 1284591 + Math.floor(Math.random() * 1000),
          last_ledger_closed_at: new Date().toISOString(),
          status: "Healthy",
          avg_close_time: 5.2,
        });
        setState({
          total_archives: 842,
          active_policies: 12,
          admin_address:
            "G" + Math.random().toString(36).substr(2, 55).toUpperCase(),
          version: "1.2.4",
          last_updated: new Date().toISOString(),
        });
      }
    } finally {
      setIsLoading(false);
    }
  }, [wallet?.network]);

  // Fetch Transaction History
  const fetchTransactions = useCallback(async (isSilent = false) => {
    if (!isSilent) setIsTxLoading(true);
    try {
      const resp = await axios.get(`${API_BASE_URL}/blockchain/transactions`);
      setTransactions(resp.data);
    } catch (err) {
      console.error("Failed to fetch transactions:", err);
      if ((import.meta as any).env.DEV) {
        setTransactions([
          {
            id: "1",
            hash: "3e4f...1a2b",
            ledger: 1284501,
            created_at: "2m ago",
            source_account: "GD...",
            type: "Policy Commit",
            status: "Confirmed",
            fee: "0.0001",
          },
          {
            id: "2",
            hash: "9a8b...7c6d",
            ledger: 1284489,
            created_at: "14m ago",
            source_account: "GD...",
            type: "Archive Verification",
            status: "Confirmed",
            fee: "0.0001",
          },
          {
            id: "3",
            hash: "5f4e...9d8c",
            ledger: 1284450,
            created_at: "36m ago",
            source_account: "GD...",
            type: "TTL Update",
            status: "Pending",
            fee: "0.0001",
          },
          {
            id: "4",
            hash: "1b2c...5a6d",
            ledger: 1284421,
            created_at: "1h ago",
            source_account: "GD...",
            type: "Policy Commit",
            status: "Confirmed",
            fee: "0.0001",
          },
        ]);
      }
    } finally {
      setIsTxLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    fetchTransactions();
  }, [fetchStatus, fetchTransactions]);

  // Wallet Actions
  const handleConnectWallet = async () => {
    setIsLoading(true);
    try {
      // freighter-api integration logic (mocked)
      setTimeout(() => {
        const mockWallet: WalletInfo = {
          address:
            "GD" + Math.random().toString(36).substr(2, 54).toUpperCase(),
          connected: true,
          network: "testnet",
          balance: "840.50",
        };
        setWallet(mockWallet);
        addNotification({
          title: "Identity Linked",
          message: "Stellar wallet connected via Freighter successfully.",
          type: "success",
          timestamp: new Date(),
        });
        setIsLoading(false);
      }, 1000);
    } catch (err) {
      addNotification({
        title: "Wallet Error",
        message: "Failed to authorize connection via Freighter API.",
        type: "error",
        timestamp: new Date(),
      });
      setIsLoading(false);
    }
  };

  const handleDisconnectWallet = () => {
    setWallet(null);
    addNotification({
      title: "Identity Removed",
      message: "Secure wallet session has been terminated.",
      type: "info",
      timestamp: new Date(),
    });
  };

  const handleNetworkChange = (network: NetworkType) => {
    setWallet((prev) => (prev ? { ...prev, network } : null));
    addNotification({
      title: "Network Traversal",
      message: `Switched operational context to ${network.toUpperCase()}.`,
      type: "info",
      timestamp: new Date(),
    });
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent italic">
            Ledger Synchronization
          </h2>
          <p className="text-muted-foreground flex items-center gap-2">
            <Globe
              className={cn(
                "h-4 w-4 text-emerald-500",
                !isLoading && "animate-spin-slow",
              )}
            />
            Real-time consensus verification via{" "}
            {status?.network.toUpperCase() || "STALLAR"} node clusters.
          </p>
        </div>
        <button
          onClick={() => {
            fetchStatus();
            fetchTransactions(true);
          }}
          className="p-3 bg-card border border-border/50 rounded-2xl text-muted-foreground hover:bg-accent transition-all active:scale-95 group"
        >
          <RefreshCcw
            className={cn(
              "h-5 w-5",
              (isLoading || isTxLoading) && "animate-spin",
            )}
          />
        </button>
      </header>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          {
            label: "Network Height",
            value: status?.network_height.toLocaleString() || "---",
            icon: Cpu,
            color: "text-blue-500",
          },
          {
            label: "Anchored Archives",
            value: state?.total_archives.toLocaleString() || "---",
            icon: ShieldCheck,
            color: "text-emerald-500",
          },
          {
            label: "Transactions (Recent)",
            value: transactions.length || "0",
            icon: Activity,
            color: "text-purple-500",
          },
        ].map((stat, i) => (
          <div
            key={i}
            className="p-8 rounded-[2rem] bg-card border border-border/50 hover:bg-accent/40 hover:border-primary/20 hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300 group"
          >
            <div className="flex items-center gap-5">
              <div
                className={`p-4 rounded-2xl bg-accent ${stat.color} group-hover:scale-110 shadow-lg shadow-black/5 transition-transform duration-500`}
              >
                <stat.icon className="h-6 w-6" />
              </div>
              <div>
                <p className="text-[10px] font-extrabold text-muted-foreground uppercase tracking-widest mb-1">
                  {stat.label}
                </p>
                <p className="text-2xl font-extrabold tracking-tighter leading-none">
                  {stat.value}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
        {/* Left Side: Stats & Chart */}
        <div className="lg:col-span-8 flex flex-col gap-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-full">
            <WalletConnector
              wallet={wallet}
              isLoading={isLoading}
              onConnect={handleConnectWallet}
              onDisconnect={handleDisconnectWallet}
              onNetworkChange={handleNetworkChange}
            />
            <ContractStatus
              status={status}
              state={state}
              isLoading={isLoading}
            />
          </div>

          <div className="p-10 rounded-[2.5rem] bg-card border border-border/50 shadow-sm relative group overflow-hidden">
            <div className="flex items-center justify-between mb-10">
              <h3 className="font-bold text-2xl flex items-center gap-4">
                <div className="p-3 rounded-2xl bg-amber-500/10 text-amber-500 shadow-xl shadow-amber-500/5">
                  <BarChart3 className="h-6 w-6" />
                </div>
                Ledger Data Propagation
              </h3>
              <div className="hidden sm:flex items-center gap-2 px-6 py-2 bg-primary/5 text-primary rounded-2xl border border-primary/10">
                <Zap className="h-4 w-4 fill-primary" />
                <span className="text-[10px] font-extrabold uppercase tracking-widest">
                  Network Live
                </span>
              </div>
            </div>
            <div className="h-[300px]">
              <BlockchainVolumeChart />
            </div>
          </div>
        </div>

        {/* Right Side: Ledger Feed */}
        <div className="lg:col-span-4 flex flex-col">
          <TransactionHistory
            transactions={transactions}
            isLoading={isTxLoading}
            onRefresh={() => fetchTransactions(true)}
            onViewDetails={(tx) => {
              window.open(
                `https://stellar.expert/explorer/testnet/tx/${tx.hash}`,
                "_blank",
              );
            }}
          />
        </div>
      </div>
    </div>
  );
}
