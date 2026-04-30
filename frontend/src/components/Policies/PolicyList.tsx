import React from "react";
import { ShieldCheck, Search, PlusCircle } from "lucide-react";
import { ArchivalPolicy } from "../../types/policy";
import { PolicyCard } from "./PolicyCard";

interface PolicyListProps {
  policies: ArchivalPolicy[];
  isLoading: boolean;
  onEdit: (policy: ArchivalPolicy) => void;
  onDelete: (id: string) => void;
  onCreateNew: () => void;
}

export function PolicyList({
  policies,
  isLoading,
  onEdit,
  onDelete,
  onCreateNew,
}: PolicyListProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-80 rounded-3xl bg-accent/20 animate-pulse border border-border/50"
          />
        ))}
      </div>
    );
  }

  if (policies.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 bg-card/40 backdrop-blur-md rounded-3xl border border-dashed border-border/60">
        <ShieldCheck className="h-16 w-16 mb-6 text-muted-foreground opacity-20" />
        <h3 className="text-xl font-bold mb-2">No Policies Found</h3>
        <p className="text-muted-foreground mb-8 max-w-sm text-center">
          Define your archival rules to automate the lifecycle of your data and
          logs.
        </p>
        <button
          onClick={onCreateNew}
          className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-bold rounded-2xl shadow-lg hover:scale-105 transition-all"
        >
          <PlusCircle className="h-5 w-5" />
          Create First Policy
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      {policies.map((policy) => (
        <PolicyCard
          key={policy.id}
          policy={policy}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
