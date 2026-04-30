// Shared types and utilities for TTL-Aware Automated Archival Service

import { z } from "zod";

// Base types
export const DataType = z.enum([
  "user_data",
  "logs", 
  "backup",
  "temp_files",
  "cache",
  "other"
]);

export const ArchiveStatus = z.enum([
  "archived",
  "expired", 
  "deleted"
]);

export const BlockchainStatus = z.enum([
  "pending",
  "confirmed",
  "failed"
]);

// Policy types
export const ArchivePolicySchema = z.object({
  id: z.number(),
  name: z.string().min(1).max(255),
  description: z.string().optional(),
  ttl_days: z.number().min(1),
  storage_location: z.string().optional(),
  compression_enabled: z.boolean(),
  encryption_enabled: z.boolean(),
  auto_cleanup: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime().optional(),
  blockchain_verified: z.boolean().optional()
});

export const CreateArchivePolicySchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().optional(),
  ttl_days: z.number().min(1),
  storage_location: z.string().optional(),
  compression_enabled: z.boolean(),
  encryption_enabled: z.boolean(),
  auto_cleanup: z.boolean()
});

// Archive record types
export const ArchiveRecordSchema = z.object({
  id: z.number(),
  policy_id: z.number(),
  original_data_id: z.string().min(1).max(255),
  data_type: DataType,
  file_path: z.string().optional(),
  file_size_bytes: z.number().min(0).optional(),
  checksum: z.string().length(64).optional(),
  metadata: z.string().optional(),
  status: ArchiveStatus,
  expires_at: z.string().datetime(),
  archived_at: z.string().datetime(),
  deleted_at: z.string().datetime().optional(),
  days_until_expiry: z.number(),
  is_expired: z.boolean(),
  blockchain_hash: z.string().length(64).optional(),
  blockchain_status: BlockchainStatus.optional(),
  policy: ArchivePolicySchema.optional()
});

export const CreateArchiveRecordSchema = z.object({
  policy_id: z.number(),
  original_data_id: z.string().min(1).max(255),
  data_type: DataType,
  file_path: z.string().optional(),
  file_size_bytes: z.number().min(0).optional(),
  checksum: z.string().length(64).optional(),
  metadata: z.string().optional()
});

// Stellar blockchain types
export const StellarPolicySchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string(),
  ttl_days: z.number(),
  compression_enabled: z.boolean(),
  encryption_enabled: z.boolean(),
  auto_cleanup: z.boolean(),
  created_by: z.string(), // Stellar address
  created_at: z.number(), // Stellar timestamp
  contract_id: z.string().optional()
});

export const StellarArchiveRecordSchema = z.object({
  id: z.string().length(64), // SHA-256 hash
  policy_id: z.number(),
  original_data_hash: z.string().length(64),
  data_type: z.string(),
  file_size: z.number(),
  checksum: z.string().length(64),
  metadata: z.string(),
  status: z.string(),
  expires_at: z.number(),
  archived_at: z.number(),
  created_by: z.string(), // Stellar address
  contract_id: z.string().optional()
});

// API response types
export const ApiResponseSchema = z.object({
  success: z.boolean(),
  data: z.any().optional(),
  error: z.string().optional(),
  message: z.string().optional()
});

export const PaginatedResponseSchema = z.object({
  items: z.array(z.any()),
  total: z.number(),
  page: z.number(),
  limit: z.number(),
  has_next: z.boolean(),
  has_prev: z.boolean()
});

// Statistics types
export const CleanupStatsSchema = z.object({
  total_records: z.number(),
  active_records: z.number(),
  expired_records: z.number(),
  deleted_records: z.number(),
  total_storage_bytes: z.number(),
  policies_count: z.number(),
  blockchain_verified_records: z.number().optional()
});

export const HealthCheckSchema = z.object({
  status: z.string(),
  timestamp: z.string().datetime(),
  database_connected: z.boolean(),
  blockchain_connected: z.boolean().optional(),
  scheduler_running: z.boolean()
});

// Utility types
export type ArchivePolicy = z.infer<typeof ArchivePolicySchema>;
export type CreateArchivePolicy = z.infer<typeof CreateArchivePolicySchema>;
export type ArchiveRecord = z.infer<typeof ArchiveRecordSchema>;
export type CreateArchiveRecord = z.infer<typeof CreateArchiveRecordSchema>;
export type StellarPolicy = z.infer<typeof StellarPolicySchema>;
export type StellarArchiveRecord = z.infer<typeof StellarArchiveRecordSchema>;
export type ApiResponse = z.infer<typeof ApiResponseSchema>;
export type PaginatedResponse = z.infer<typeof PaginatedResponseSchema>;
export type CleanupStats = z.infer<typeof CleanupStatsSchema>;
export type HealthCheck = z.infer<typeof HealthCheckSchema>;
export type DataTypeType = z.infer<typeof DataType>;
export type ArchiveStatusType = z.infer<typeof ArchiveStatus>;
export type BlockchainStatusType = z.infer<typeof BlockchainStatus>;

// Utility functions
export const calculateExpiryDate = (ttlDays: number): Date => {
  const now = new Date();
  return new Date(now.getTime() + ttlDays * 24 * 60 * 60 * 1000);
};

export const calculateDaysUntilExpiry = (expiresAt: string): number => {
  const now = new Date();
  const expiry = new Date(expiresAt);
  const diffTime = expiry.getTime() - now.getTime();
  return Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const generateStellarHash = (data: string): string => {
  // This would be implemented with actual Stellar SDK
  // For now, return a placeholder using a browser-compatible hex encoding
  let hex = "";
  for (let i = 0; i < data.length; i++) {
    hex += data.charCodeAt(i).toString(16).padStart(2, "0");
  }
  return hex.padEnd(64, "0").substring(0, 64);
};

// Validation helpers
export const validateStellarAddress = (address: string): boolean => {
  // Basic Stellar address validation (starts with 'G' and 56 characters)
  return /^G[A-Z0-9]{55}$/.test(address);
};

export const validateHash = (hash: string): boolean => {
  // SHA-256 hash validation (64 hex characters)
  return /^[a-f0-9]{64}$/i.test(hash);
};

// Error types
export class ValidationError extends Error {
  constructor(message: string, public field?: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class BlockchainError extends Error {
  constructor(message: string, public transactionId?: string) {
    super(message);
    this.name = 'BlockchainError';
  }
}

export class ArchiveError extends Error {
  constructor(message: string, public code?: string) {
    super(message);
    this.name = "ArchiveError";
  }
}

// Synchronization types
export const SyncType = z.enum(["FULL", "INCREMENTAL", "REAL_TIME"]);
export const SyncStatus = z.enum([
  "PENDING",
  "RUNNING",
  "COMPLETED",
  "FAILED",
  "PAUSED",
]);
export const ConflictStrategy = z.enum([
  "LAST_WRITE_WINS",
  "SOURCE_WINS",
  "TARGET_WINS",
  "MANUAL",
]);
export const RecordSyncStatus = z.enum([
  "SYNCED",
  "CONFLICT",
  "FAILED",
  "SKIPPED",
]);

export const SyncJobSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  source_system: z.string(),
  target_system: z.string(),
  sync_type: SyncType,
  status: SyncStatus,
  conflict_strategy: ConflictStrategy,
  last_sync_at: z.string().datetime().nullable(),
  next_sync_at: z.string().datetime().nullable(),
  records_synced: z.number(),
  records_failed: z.number(),
  error_message: z.string().nullable(),
  retry_count: z.number(),
  max_retries: z.number(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const SyncRecordSchema = z.object({
  id: z.string().uuid(),
  sync_job_id: z.string().uuid(),
  record_id: z.string(),
  record_type: z.string(),
  source_checksum: z.string().nullable(),
  target_checksum: z.string().nullable(),
  status: RecordSyncStatus,
  conflict_details: z.any().optional(),
  synced_at: z.string().datetime().nullable(),
  created_at: z.string().datetime(),
});

export const SyncConflictSchema = z.object({
  id: z.string().uuid(),
  sync_job_id: z.string().uuid(),
  sync_record_id: z.string().uuid(),
  source_data: z.any(),
  target_data: z.any(),
  resolution: z.string().nullable(),
  resolved_at: z.string().datetime().nullable(),
  resolved_by: z.string().nullable(),
  created_at: z.string().datetime(),
});

export type SyncJob = z.infer<typeof SyncJobSchema>;
export type SyncRecord = z.infer<typeof SyncRecordSchema>;
export type SyncConflict = z.infer<typeof SyncConflictSchema>;
export type SyncTypeType = z.infer<typeof SyncType>;
export type SyncStatusType = z.infer<typeof SyncStatus>;
export type ConflictStrategyType = z.infer<typeof ConflictStrategy>;
export type RecordSyncStatusType = z.infer<typeof RecordSyncStatus>;
