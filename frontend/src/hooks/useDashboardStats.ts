import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { DashboardStats, ArchiveEntry } from "../types/dashboard";

interface UseDashboardData {
  stats: DashboardStats | null;
  recentArchives: ArchiveEntry[];
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

const API_BASE_URL = (import.meta as any).env.VITE_API_URL || "/api/v1";

export function useDashboardStats(): UseDashboardData {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentArchives, setRecentArchives] = useState<ArchiveEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (refreshing = false) => {
    if (refreshing) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    setError(null);

    try {
      // Mocked for testing/development if API is not ready
      // In a real scenario, these would be separate calls or Promise.all
      const [statsRes, archivesRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/stats`),
        axios.get(`${API_BASE_URL}/archives?limit=10`),
      ]);

      setStats(statsRes.data);
      setRecentArchives(archivesRes.data);
    } catch (err: any) {
      console.error("Failed to fetch dashboard data:", err);
      // For development, provide mock data if the API fails
      if (process.env.NODE_ENV === "development") {
        const mockStats: DashboardStats = {
          total_records: 1284,
          active_policies: 24,
          storage_usage: 1450000000,
          storage_usage_formatted: "1.45 GB",
          blockchain_status: "Healthy",
          verification_rate: 99.9,
          recent_activities_count: 14,
          storage_limit: 5368709120, // 5GB
        };
        const mockArchives: ArchiveEntry[] = [
          {
            id: "1",
            filename: "user_logs_2024_03_21.sql",
            size: 14200000,
            size_formatted: "14.2 MB",
            created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
            status: "Verified",
            checksum: "abc...",
          },
          {
            id: "2",
            filename: "audit_trail_march.json",
            size: 2100000,
            size_formatted: "2.1 MB",
            created_at: new Date(Date.now() - 3600000 * 5).toISOString(),
            status: "Archived",
            checksum: "def...",
          },
          {
            id: "3",
            filename: "system_metrics_daily.csv",
            size: 850000,
            size_formatted: "850 KB",
            created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
            status: "Verified",
            checksum: "ghi...",
          },
          {
            id: "4",
            filename: "error_logs_q1.zip",
            size: 45000000,
            size_formatted: "45.0 MB",
            created_at: new Date(Date.now() - 3600000 * 48).toISOString(),
            status: "Expiring",
            checksum: "jkl...",
          },
        ];
        setStats(mockStats);
        setRecentArchives(mockArchives);
      } else {
        setError(
          err.message ||
            "An unexpected error occurred while fetching dashboard data.",
        );
      }
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refresh = async () => {
    await fetchData(true);
  };

  return { stats, recentArchives, isLoading, isRefreshing, error, refresh };
}
