import React from "react";
import {
  ShieldCheck,
  Clock,
  Database,
  MoreVertical,
  ArrowUpRight,
  Trash2,
  Edit2,
} from "lucide-react";
import { ArchivalPolicy } from "../../types/policy";
import { cn } from "../../utils/cn";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";

interface PolicyCardProps {
  policy: ArchivalPolicy;
  onEdit: (policy: ArchivalPolicy) => void;
  onDelete: (id: string) => void;
}

export function PolicyCard({ policy, onEdit, onDelete }: PolicyCardProps) {
  const statusColors = {
    Active: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
    Inactive: "bg-rose-500/10 text-rose-500 border-rose-500/20",
    Draft: "bg-muted text-muted-foreground border-border/40",
  };

  return (
    <div className="p-6 rounded-3xl bg-card border border-border/50 hover:border-primary/20 hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300 group cursor-default relative overflow-hidden flex flex-col">
      <div className="absolute top-0 right-0 p-4">
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button className="p-2 rounded-xl hover:bg-accent transition-colors outline-none">
              <MoreVertical className="h-4 w-4 text-muted-foreground opacity-100 group-hover:opacity-100 transition-opacity" />
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="z-50 min-w-[160px] bg-card/95 backdrop-blur-xl border border-border/50 p-2 rounded-2xl shadow-xl animate-in fade-in zoom-in-95"
              sideOffset={5}
            >
              <DropdownMenu.Item
                className="flex items-center gap-2 px-3 py-2 text-sm font-semibold rounded-xl hover:bg-primary/10 hover:text-primary outline-none cursor-pointer"
                onClick={() => onEdit(policy)}
              >
                <Edit2 className="h-4 w-4" />
                Edit Policy
              </DropdownMenu.Item>
              <DropdownMenu.Item
                className="flex items-center gap-2 px-3 py-2 text-sm font-semibold text-rose-500 rounded-xl hover:bg-rose-500/10 outline-none cursor-pointer"
                onClick={() => onDelete(policy.id)}
              >
                <Trash2 className="h-4 w-4" />
                Delete Policy
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div
          className={cn(
            "p-3 rounded-2xl bg-accent bg-opacity-10 group-hover:scale-110 transition-transform shadow-inner",
            policy.status === "Active"
              ? "text-primary"
              : "text-muted-foreground",
          )}
        >
          <ShieldCheck className="h-6 w-6" />
        </div>
        <div>
          <h4 className="font-bold text-sm tracking-tight">{policy.name}</h4>
          <div
            className={cn(
              "px-2 py-0.5 rounded-full text-[10px] font-bold mt-1 inline-block border",
              statusColors[policy.status],
            )}
          >
            {policy.status}
          </div>
        </div>
      </div>

      <div className="space-y-4 flex-1">
        <p className="text-xs text-muted-foreground line-clamp-2 min-h-[32px]">
          {policy.description}
        </p>

        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground font-medium flex items-center gap-2">
            <Clock className="h-3.5 w-3.5" />
            Retention Period
          </span>
          <span className="font-bold">{policy.ttl_days} Days</span>
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground font-medium flex items-center gap-2">
            <Database className="h-3.5 w-3.5" />
            Storage Node
          </span>
          <span className="font-bold">{policy.storage_location}</span>
        </div>

        <div className="flex flex-wrap gap-2 pt-2">
          {policy.compression_enabled && (
            <span className="text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-lg bg-blue-500/10 text-blue-500 border border-blue-500/20">
              lz4-comp
            </span>
          )}
          {policy.encryption_enabled && (
            <span className="text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-lg bg-purple-500/10 text-purple-500 border border-purple-500/20">
              aes-256
            </span>
          )}
          {policy.auto_cleanup && (
            <span className="text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-lg bg-amber-500/10 text-amber-500 border border-amber-500/20">
              auto-flush
            </span>
          )}
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-border/30 flex items-center justify-between">
        <span className="text-[10px] text-muted-foreground font-medium flex items-center gap-1">
          <Database className="h-3 w-3" />
          {policy.archives_count} archives
        </span>
        <button
          onClick={() => onEdit(policy)}
          className="text-xs font-bold text-primary hover:underline flex items-center gap-1"
        >
          Edit Settings
          <ArrowUpRight className="h-3 w-3" />
        </button>
      </div>
    </div>
  );
}
