import React from "react";
import { Bell } from "lucide-react";
import { useNotifications } from "../../context/NotificationContext";

export function NotificationBell() {
  const { unreadCount, openNotificationCenter, requestDesktopPermission } =
    useNotifications();

  const handleClick = async () => {
    // Request desktop permission on first interaction
    if ("Notification" in window && Notification.permission === "default") {
      await requestDesktopPermission();
    }
    openNotificationCenter();
  };

  return (
    <button
      onClick={handleClick}
      className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
      aria-label={`Notifications ${unreadCount > 0 ? `(${unreadCount} unread)` : ""}`}
    >
      <Bell className="h-5 w-5" />
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center animate-pulse">
          {unreadCount > 99 ? "99+" : unreadCount}
        </span>
      )}
    </button>
  );
}
