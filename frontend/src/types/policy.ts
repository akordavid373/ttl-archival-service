export type PolicyStatus = "Active" | "Inactive" | "Draft";

export interface ArchivalPolicy {
  id: string;
  name: string;
  description: string;
  ttl_days: number;
  storage_location:
    | "S3 Standard"
    | "Glacier Deep"
    | "Google Archive"
    | "Azure Blob";
  compression_enabled: boolean;
  encryption_enabled: boolean;
  auto_cleanup: boolean;
  status: PolicyStatus;
  archives_count: number;
  created_at: string;
  updated_at: string;
}

export interface PolicyFormData {
  name: string;
  description: string;
  ttl_days: number;
  storage_location: string;
  compression_enabled: boolean;
  encryption_enabled: boolean;
  auto_cleanup: boolean;
  status: PolicyStatus;
}
