export type NetworkType = 'testnet' | 'public';

export interface BlockchainStatus {
  network: NetworkType;
  horizon_url: string;
  contract_id: string;
  network_height: number;
  last_ledger_closed_at: string;
  status: 'Healthy' | 'Degraded' | 'Out of Sync';
  avg_close_time: number;
}

export interface TransactionRecord {
  id: string;
  hash: string;
  ledger: number;
  created_at: string;
  source_account: string;
  memo?: string;
  type: string;
  status: 'Confirmed' | 'Failed' | 'Pending';
  fee: string;
  result_code?: string;
}

export interface WalletInfo {
  address: string;
  connected: boolean;
  network: NetworkType;
  balance?: string;
}

export interface ContractState {
  total_archives: number;
  active_policies: number;
  admin_address: string;
  version: string;
  last_updated: string;
}
