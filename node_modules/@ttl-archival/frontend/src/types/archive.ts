import { ArchiveEntry } from './dashboard';

export type ArchiveStatus = 'Archived' | 'Expiring' | 'Verified' | 'Failed' | 'Sycning';

export interface ArchiveFilters {
  policy_id?: string;
  status?: ArchiveStatus[];
  date_from?: string;
  date_to?: string;
  search?: string;
  min_size?: number;
  max_size?: number;
}

export interface ArchiveSort {
  field: 'created_at' | 'size' | 'filename' | 'status' | 'policy_name';
  order: 'asc' | 'desc';
}

export interface DetailedArchiveEntry extends ArchiveEntry {
  policy_id: string;
  policy_name: string;
  storage_location: string;
  compression_method?: string;
  encryption_algorithm?: string;
  original_data_id: string;
  blockchain_network: 'Stellar' | 'IPFS' | 'Internal';
  verification_date?: string;
  expiry_date?: string;
  metadata: Record<string, string | number | boolean>;
}

export interface PaginatedArchives {
  items: DetailedArchiveEntry[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}
