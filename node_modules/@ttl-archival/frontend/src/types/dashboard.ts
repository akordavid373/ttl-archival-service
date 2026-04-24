export interface DashboardStats {
  total_records: number;
  active_policies: number;
  storage_usage: number;
  storage_usage_formatted: string;
  blockchain_status: 'Healthy' | 'Degraded' | 'Out of Sync';
  verification_rate: number;
  recent_activities_count: number;
  storage_limit: number;
}

export interface ArchiveEntry {
  id: string;
  filename: string;
  size: number;
  size_formatted: string;
  created_at: string;
  status: 'Archived' | 'Expiring' | 'Verified' | 'Failed';
  checksum: string;
  blockchain_tx_id?: string;
}
