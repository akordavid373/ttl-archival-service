import React, { useState, useEffect, useMemo } from "react";
import {
  Plus,
  Search,
  Filter,
  ShieldAlert,
  Archive,
  AlertCircle,
} from "lucide-react";
import { PolicyMetricsChart } from "../components/charts/PolicyMetricsChart";
import { ArchivalPolicy, PolicyFormData } from "../types/policy";
import { PolicyList } from "../components/Policies/PolicyList";
import { PolicyForm } from "../components/Policies/PolicyForm";
import { useNotifications } from "../context/NotificationContext";
import axios from "axios";

const API_BASE_URL = (import.meta as any).env.VITE_API_URL || "/api/v1";

export function Policies() {
  const [policies, setPolicies] = useState<ArchivalPolicy[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState<
    ArchivalPolicy | undefined
  >();
  const { addNotification } = useNotifications();

  const fetchPolicies = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/policies`);
      setPolicies(response.data);
    } catch (error) {
      console.error("Failed to fetch policies:", error);
      // Mock data for development
      if ((import.meta as any).env.DEV) {
        const mockPolicies: ArchivalPolicy[] = [
          {
            id: "1",
            name: "User Data TTL",
            description:
              "Automated archival for user profile data and activity logs.",
            ttl_days: 30,
            status: "Active",
            storage_location: "S3 Standard",
            archives_count: 124,
            compression_enabled: true,
            encryption_enabled: true,
            auto_cleanup: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: "2",
            name: "System Logs",
            description: "Archival for system performance and error logs.",
            ttl_days: 7,
            status: "Active",
            storage_location: "Glacier Deep",
            archives_count: 850,
            compression_enabled: true,
            encryption_enabled: false,
            auto_cleanup: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: "3",
            name: "Marketing Assets",
            description:
              "Long term retention for promotional media and assets.",
            ttl_days: 365,
            status: "Inactive",
            storage_location: "Google Archive",
            archives_count: 54,
            compression_enabled: false,
            encryption_enabled: true,
            auto_cleanup: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ];
        setPolicies(mockPolicies);
      } else {
        addNotification({
          title: "Fetch Failed",
          message: "Could not load archival policies. Please try again later.",
          type: "error",
          duration: 5000,
          timestamp: new Date(),
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const filteredPolicies = useMemo(() => {
    return policies.filter((p: ArchivalPolicy) => {
      const matchesSearch =
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus = statusFilter === "All" || p.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [policies, searchQuery, statusFilter]);

  const handleCreateOrUpdate = async (data: PolicyFormData) => {
    try {
      if (editingPolicy) {
        await axios.put(`${API_BASE_URL}/policies/${editingPolicy.id}`, data);
        setPolicies((prev: ArchivalPolicy[]) =>
          prev.map((p: ArchivalPolicy) =>
            p.id === editingPolicy.id
              ? { ...p, ...data, updated_at: new Date().toISOString() }
              : p,
          ),
        );
        addNotification({
          title: "Policy Updated",
          message: `Policy "${data.name}" has been successfully updated.`,
          type: "success",
          timestamp: new Date(),
        });
      } else {
        const response = await axios.post(`${API_BASE_URL}/policies`, data);
        const newPolicy = response.data || {
          ...data,
          id: Math.random().toString(36).substr(2, 9),
          archives_count: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        setPolicies((prev: ArchivalPolicy[]) => [newPolicy, ...prev]);
        addNotification({
          title: "Policy Created",
          message: `New policy "${data.name}" has been established.`,
          type: "success",
          timestamp: new Date(),
        });
      }
      setIsFormOpen(false);
      setEditingPolicy(undefined);
    } catch (error) {
      console.error("Operation failed:", error);
      // Optimistic update for dev
      if ((import.meta as any).env.DEV) {
        if (editingPolicy) {
          setPolicies((prev: ArchivalPolicy[]) =>
            prev.map((p: ArchivalPolicy) =>
              p.id === editingPolicy.id ? { ...p, ...data } : p,
            ),
          );
        } else {
          setPolicies((prev: ArchivalPolicy[]) => [
            {
              ...data,
              id: Date.now().toString(),
              archives_count: 0,
              created_at: "",
              updated_at: "",
            } as ArchivalPolicy,
            ...prev,
          ]);
        }
        setIsFormOpen(false);
        setEditingPolicy(undefined);
      } else {
        addNotification({
          title: "Operation Failed",
          message:
            "An error occurred while saving the policy. Please verify your data.",
          type: "error",
          timestamp: new Date(),
        });
      }
    }
  };

  const handleDelete = async (id: string) => {
    if (
      !window.confirm(
        "Are you sure you want to permanently delete this policy? This action cannot be undone.",
      )
    )
      return;

    try {
      await axios.delete(`${API_BASE_URL}/policies/${id}`);
      setPolicies((prev: ArchivalPolicy[]) =>
        prev.filter((p: ArchivalPolicy) => p.id !== id),
      );
      addNotification({
        title: "Policy Deleted",
        message: "The policy has been successfully removed from the system.",
        type: "info",
        timestamp: new Date(),
      });
    } catch (error) {
      console.error("Delete failed:", error);
      if ((import.meta as any).env.DEV) {
        setPolicies((prev: ArchivalPolicy[]) =>
          prev.filter((p: ArchivalPolicy) => p.id !== id),
        );
      } else {
        addNotification({
          title: "Deletion Failed",
          message: "The policy could not be deleted at this time.",
          type: "error",
          timestamp: new Date(),
        });
      }
    }
  };

  const openEditForm = (policy: ArchivalPolicy) => {
    setEditingPolicy(policy);
    setIsFormOpen(true);
  };

  const openCreateForm = () => {
    setEditingPolicy(undefined);
    setIsFormOpen(true);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <header className="flex flex-col sm:flex-row sm:items-end justify-between gap-6">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            Archival Policies
          </h2>
          <p className="text-muted-foreground flex items-center gap-2">
            <Archive className="h-4 w-4 text-primary" />
            Manage rules, TTL settings, and automated archival workflows for all
            data nodes.
          </p>
        </div>
        <button
          onClick={openCreateForm}
          className="flex items-center gap-2 px-6 py-4 bg-primary text-primary-foreground font-bold text-sm rounded-2xl shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 group whitespace-nowrap"
        >
          <Plus className="h-5 w-5 group-hover:rotate-90 transition-transform duration-300" />
          Establish New Policy
        </button>
      </header>

      <div className="flex flex-col md:flex-row items-stretch md:items-center gap-4 bg-card/40 backdrop-blur-md p-4 rounded-[2rem] border border-border/50 shadow-sm">
        <div className="flex-1 relative group">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
          <input
            value={searchQuery}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setSearchQuery(e.target.value)
            }
            className="w-full pl-12 pr-4 py-3 bg-transparent text-sm font-medium focus:outline-none placeholder:text-muted-foreground/60"
            placeholder="Search by name or description..."
          />
        </div>
        <div className="hidden md:block h-8 w-px bg-border/40"></div>
        <div className="flex items-center gap-3 px-4">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={statusFilter}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
              setStatusFilter(e.target.value)
            }
            className="bg-transparent text-xs font-bold px-2 py-2 cursor-pointer focus:outline-none rounded-xl"
          >
            <option value="All">All Statuses</option>
            <option value="Active">Active</option>
            <option value="Inactive">Inactive</option>
            <option value="Draft">Draft</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <div className="p-8 rounded-[2rem] bg-card border border-border/50 shadow-sm relative group overflow-hidden">
            <div className="flex items-center justify-between mb-8">
              <h3 className="font-bold text-lg flex items-center gap-3">
                <ShieldAlert className="h-5 w-5 text-indigo-500" />
                Effectiveness
              </h3>
              <span className="text-[10px] font-bold px-2 py-1 bg-indigo-500/10 text-indigo-500 rounded-full border border-indigo-500/20">
                Live Audit
              </span>
            </div>
            <PolicyMetricsChart />
            <div className="mt-8 pt-8 border-t border-border/20 space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground font-medium">
                    Compliance Coverage
                  </span>
                  <span className="font-bold">98.2%</span>
                </div>
                <div className="w-full bg-accent/30 h-1.5 rounded-full overflow-hidden">
                  <div className="w-[98.2%] bg-indigo-500 h-full rounded-full transition-all duration-1000"></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground font-medium">
                    Auto-Archival Precision
                  </span>
                  <span className="font-bold">94.5%</span>
                </div>
                <div className="w-full bg-accent/30 h-1.5 rounded-full overflow-hidden">
                  <div className="w-[94.5%] bg-emerald-500 h-full rounded-full transition-all duration-1000"></div>
                </div>
              </div>
            </div>
          </div>

          <div className="p-6 bg-primary/5 rounded-[2rem] border border-primary/10">
            <div className="flex gap-4">
              <div className="p-3 rounded-2xl bg-primary/10 text-primary h-fit">
                <AlertCircle className="h-5 w-5" />
              </div>
              <div className="space-y-1">
                <h4 className="font-bold text-sm tracking-tight text-primary">
                  Optimization Tip
                </h4>
                <p className="text-[11px] leading-relaxed text-muted-foreground">
                  Policies with TTL &lt; 7 days are processed in prioritized
                  cleanup cycles to maximize storage efficiency.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-3">
          <PolicyList
            policies={filteredPolicies}
            isLoading={isLoading}
            onEdit={openEditForm}
            onDelete={handleDelete}
            onCreateNew={openCreateForm}
          />
        </div>
      </div>

      {isFormOpen && (
        <PolicyForm
          policy={editingPolicy}
          onSubmit={handleCreateOrUpdate}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingPolicy(undefined);
          }}
        />
      )}
    </div>
  );
}
