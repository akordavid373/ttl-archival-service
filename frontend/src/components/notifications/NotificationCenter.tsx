import React, { useState } from "react";
import {
  Bell,
  X,
  CheckCircle,
  AlertCircle,
  AlertTriangle,
  Info,
  Settings,
  Trash2,
  Check,
  Filter,
} from "lucide-react";
import {
  Notification,
  NotificationType,
  NotificationPriority,
} from "../../types/notifications";
import { cn } from "../../utils/cn";

interface NotificationCenterProps {
  notifications: Notification[];
  isOpen: boolean;
  onClose: () => void;
  onMarkAsRead: (id: string) => void;
  onDelete: (id: string) => void;
  onClearAll: () => void;
  onMarkAllAsRead: () => void;
}

const typeConfig = {
  success: { icon: CheckCircle, className: "text-green-500" },
  error: { icon: AlertCircle, className: "text-red-500" },
  warning: { icon: AlertTriangle, className: "text-yellow-500" },
  info: { icon: Info, className: "text-blue-500" },
  system: { icon: Settings, className: "text-gray-500" },
};

const priorityConfig = {
  low: { label: "Low", className: "bg-gray-100 text-gray-700" },
  medium: { label: "Medium", className: "bg-blue-100 text-blue-700" },
  high: { label: "High", className: "bg-orange-100 text-orange-700" },
  urgent: { label: "Urgent", className: "bg-red-100 text-red-700" },
};

export function NotificationCenter({
  notifications,
  isOpen,
  onClose,
  onMarkAsRead,
  onDelete,
  onClearAll,
  onMarkAllAsRead,
}: NotificationCenterProps) {
  const [filter, setFilter] = useState<{
    type?: NotificationType;
    priority?: NotificationPriority;
    readStatus?: "all" | "read" | "unread";
  }>({
    readStatus: "all",
  });

  const unreadCount = notifications.filter((n) => !n.read).length;

  const filteredNotifications = notifications.filter((notification) => {
    if (filter.type && notification.type !== filter.type) return false;
    if (filter.priority && notification.priority !== filter.priority)
      return false;
    if (filter.readStatus === "read" && !notification.read) return false;
    if (filter.readStatus === "unread" && notification.read) return false;
    return true;
  });

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-start justify-end p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            <h2 className="text-lg font-semibold">Notifications</h2>
            {unreadCount > 0 && (
              <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                {unreadCount}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onMarkAllAsRead}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Mark all read
            </button>
            <button
              onClick={onClearAll}
              className="text-sm text-red-600 hover:text-red-800"
            >
              Clear all
            </button>
            <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="p-4 border-b space-y-2">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            <span className="text-sm font-medium">Filters</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            <select
              value={filter.readStatus}
              onChange={(e) =>
                setFilter((prev) => ({
                  ...prev,
                  readStatus: e.target.value as any,
                }))
              }
              className="text-sm border rounded px-2 py-1"
            >
              <option value="all">All</option>
              <option value="unread">Unread</option>
              <option value="read">Read</option>
            </select>
            <select
              value={filter.type || ""}
              onChange={(e) =>
                setFilter((prev) => ({
                  ...prev,
                  type: (e.target.value as NotificationType) || undefined,
                }))
              }
              className="text-sm border rounded px-2 py-1"
            >
              <option value="">All Types</option>
              <option value="success">Success</option>
              <option value="error">Error</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
              <option value="system">System</option>
            </select>
            <select
              value={filter.priority || ""}
              onChange={(e) =>
                setFilter((prev) => ({
                  ...prev,
                  priority:
                    (e.target.value as NotificationPriority) || undefined,
                }))
              }
              className="text-sm border rounded px-2 py-1"
            >
              <option value="">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
        </div>

        {/* Notifications List */}
        <div className="flex-1 overflow-y-auto">
          {filteredNotifications.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Bell className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No notifications</p>
            </div>
          ) : (
            <div className="divide-y">
              {filteredNotifications.map((notification) => {
                const TypeIcon = typeConfig[notification.type].icon;
                const priorityStyle = priorityConfig[notification.priority];

                return (
                  <div
                    key={notification.id}
                    className={cn(
                      "p-4 hover:bg-gray-50 transition-colors",
                      !notification.read && "bg-blue-50",
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <TypeIcon
                        className={cn(
                          "h-5 w-5 mt-0.5",
                          typeConfig[notification.type].className,
                        )}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <h4 className="font-semibold text-sm truncate">
                            {notification.title}
                          </h4>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            <span
                              className={cn(
                                "text-xs px-2 py-1 rounded",
                                priorityStyle.className,
                              )}
                            >
                              {priorityStyle.label}
                            </span>
                            <button
                              onClick={() => onDelete(notification.id)}
                              className="p-1 hover:bg-gray-200 rounded"
                            >
                              <Trash2 className="h-3 w-3" />
                            </button>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-gray-500">
                            {formatTime(notification.timestamp)}
                          </span>
                          {!notification.read && (
                            <button
                              onClick={() => onMarkAsRead(notification.id)}
                              className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1"
                            >
                              <Check className="h-3 w-3" />
                              Mark as read
                            </button>
                          )}
                        </div>
                        {notification.action && (
                          <button
                            onClick={() => {
                              notification.action!.onClick();
                              onMarkAsRead(notification.id);
                            }}
                            className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                          >
                            {notification.action.label}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
