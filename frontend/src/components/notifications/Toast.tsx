import React, { useEffect, useState } from "react";
import {
  X,
  CheckCircle,
  AlertCircle,
  AlertTriangle,
  Info,
  Settings,
} from "lucide-react";
import { Notification } from "../../types/notifications";
import { cn } from "../../utils/cn";

interface ToastProps {
  notification: Notification;
  onClose: (id: string) => void;
  onAction?: (notification: Notification) => void;
}

const typeConfig = {
  success: {
    icon: CheckCircle,
    className: "bg-green-50 border-green-200 text-green-800",
    iconClassName: "text-green-500",
  },
  error: {
    icon: AlertCircle,
    className: "bg-red-50 border-red-200 text-red-800",
    iconClassName: "text-red-500",
  },
  warning: {
    icon: AlertTriangle,
    className: "bg-yellow-50 border-yellow-200 text-yellow-800",
    iconClassName: "text-yellow-500",
  },
  info: {
    icon: Info,
    className: "bg-blue-50 border-blue-200 text-blue-800",
    iconClassName: "text-blue-500",
  },
  system: {
    icon: Settings,
    className: "bg-gray-50 border-gray-200 text-gray-800",
    iconClassName: "text-gray-500",
  },
};

const priorityConfig = {
  low: { borderStyle: "border-l-2" },
  medium: { borderStyle: "border-l-4" },
  high: { borderStyle: "border-l-4 shadow-lg" },
  urgent: { borderStyle: "border-l-8 shadow-xl animate-pulse" },
};

export function Toast({ notification, onClose, onAction }: ToastProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [progress, setProgress] = useState(100);

  const config = typeConfig[notification.type];
  const priorityConfigStyle = priorityConfig[notification.priority];
  const Icon = config.icon;

  useEffect(() => {
    // Trigger entrance animation
    setIsVisible(true);

    // Auto-dismiss logic
    if (notification.autoDismiss && notification.dismissTimeout) {
      const startTime = Date.now();
      const interval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const remaining = Math.max(
          0,
          100 - (elapsed / notification.dismissTimeout!) * 100,
        );
        setProgress(remaining);

        if (remaining === 0) {
          handleClose();
        }
      }, 50);

      return () => clearInterval(interval);
    }
  }, [notification.autoDismiss, notification.dismissTimeout]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => onClose(notification.id), 300);
  };

  const handleAction = () => {
    if (notification.action) {
      notification.action.onClick();
    }
    if (onAction) {
      onAction(notification);
    }
    handleClose();
  };

  return (
    <div
      className={cn(
        "relative flex items-start gap-3 p-4 rounded-lg border shadow-sm transition-all duration-300 max-w-md w-full",
        config.className,
        priorityConfigStyle.borderStyle,
        isVisible ? "translate-x-0 opacity-100" : "translate-x-full opacity-0",
      )}
    >
      <Icon
        className={cn("h-5 w-5 flex-shrink-0 mt-0.5", config.iconClassName)}
      />

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <h4 className="font-semibold text-sm truncate">
            {notification.title}
          </h4>
          <button
            onClick={handleClose}
            className="flex-shrink-0 p-1 rounded-md hover:bg-black/5 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <p className="text-sm mt-1 opacity-90 break-words">
          {notification.message}
        </p>

        {notification.action && (
          <button
            onClick={handleAction}
            className="mt-2 text-sm font-medium underline hover:no-underline"
          >
            {notification.action.label}
          </button>
        )}

        {notification.autoDismiss && notification.dismissTimeout && (
          <div
            className="absolute bottom-0 left-0 h-1 bg-current opacity-20 rounded-b-lg transition-all duration-100"
            style={{ width: `${progress}%` }}
          />
        )}
      </div>
    </div>
  );
}
