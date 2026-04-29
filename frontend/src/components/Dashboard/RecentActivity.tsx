import React from "react";
import {
  Clock,
  AlertTriangle,
  FileText,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { ArchiveEntry } from "../../types/dashboard";
import { cn } from "../../utils/cn";

interface RecentActivityProps {
  activities: ArchiveEntry[];
  loading?: boolean;
}

const statusConfig = {
  Archived: { icon: FileText, color: "text-blue-500", bg: "bg-blue-500/10" },
  Expiring: {
    icon: AlertTriangle,
    color: "text-amber-500",
    bg: "bg-amber-500/10",
  },
  Verified: {
    icon: CheckCircle2,
    color: "text-emerald-500",
    bg: "bg-emerald-500/10",
  },
  Failed: { icon: XCircle, color: "text-rose-500", bg: "bg-rose-500/10" },
};

export function RecentActivity({ activities, loading }: RecentActivityProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="flex items-center gap-4 p-3 rounded-xl bg-accent/20 animate-pulse"
          >
            <div className="w-10 h-10 rounded-lg bg-accent shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-accent rounded w-1/3" />
              <div className="h-3 bg-accent rounded w-1/4" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
        <Clock className="h-12 w-12 mb-4 opacity-20" />
        <p className="text-sm font-medium">No recent activity detected.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 relative z-10">
      {activities.map((activity) => {
        const config = statusConfig[activity.status] || statusConfig.Archived;
        const StatusIcon = config.icon;

        return (
          <div
            key={activity.id}
            className="group flex items-center gap-4 p-3 rounded-xl hover:bg-accent/50 transition-colors cursor-pointer border border-transparent hover:border-border/40"
          >
            <div
              className={cn(
                "w-10 h-10 rounded-lg flex items-center justify-center shrink-0 transition-transform group-hover:scale-110",
                config.bg,
                config.color,
              )}
            >
              <StatusIcon className="h-5 w-5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate group-hover:text-primary transition-colors">
                {activity.filename}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <p className="text-[10px] text-muted-foreground flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {formatDistanceToNow(new Date(activity.created_at), {
                    addSuffix: true,
                  })}
                </p>
                <span className="text-[10px] text-muted-foreground">·</span>
                <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight">
                  {activity.size_formatted}
                </p>
                <span className="text-[10px] text-muted-foreground">·</span>
                <span
                  className={cn(
                    "text-[10px] font-bold px-2 py-0.5 rounded-full uppercase",
                    config.bg,
                    config.color,
                  )}
                >
                  {activity.status}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
