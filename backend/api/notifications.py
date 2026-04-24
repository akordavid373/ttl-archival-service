from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Sample data storage (in production, this would be a database)
notification_preferences = [
    {
        "id": "1",
        "type": "email",
        "category": "system",
        "enabled": True,
        "frequency": "daily",
        "quiet_hours": {"enabled": True, "start": "22:00", "end": "08:00"}
    },
    {
        "id": "2", 
        "type": "push",
        "category": "archive",
        "enabled": True,
        "frequency": "immediate",
        "quiet_hours": {"enabled": True, "start": "22:00", "end": "08:00"}
    },
    {
        "id": "3",
        "type": "in_app",
        "category": "security",
        "enabled": True,
        "frequency": "immediate",
        "quiet_hours": {"enabled": False, "start": "22:00", "end": "08:00"}
    }
]

notification_history = [
    {
        "id": "1",
        "type": "email",
        "category": "system",
        "title": "System Maintenance Scheduled",
        "message": "Scheduled maintenance will occur tonight at 2 AM UTC",
        "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        "read": True,
        "actionTaken": "Acknowledged"
    },
    {
        "id": "2",
        "type": "push",
        "category": "archive", 
        "title": "Archive Process Completed",
        "message": "Your archive #12345 has been successfully processed",
        "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
        "read": False
    },
    {
        "id": "3",
        "type": "in_app",
        "category": "security",
        "title": "New Login Detected",
        "message": "New login from Chrome on Windows",
        "timestamp": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
        "read": False
    }
]

@router.get("/preferences")
async def get_notification_preferences():
    """Get notification preferences"""
    try:
        return notification_preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notification preferences: {str(e)}")

@router.put("/preferences")
async def update_notification_preferences(preferences: List[Dict[str, Any]]):
    """Update notification preferences"""
    try:
        global notification_preferences
        notification_preferences = preferences
        return {"status": "success", "message": "Notification preferences updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update notification preferences: {str(e)}")

@router.get("/history")
async def get_notification_history(
    limit: Optional[int] = 50,
    unread_only: Optional[bool] = False,
    category: Optional[str] = None
):
    """Get notification history"""
    try:
        filtered_history = notification_history
        
        if unread_only:
            filtered_history = [n for n in filtered_history if not n["read"]]
        
        if category:
            filtered_history = [n for n in filtered_history if n["category"] == category]
        
        # Sort by timestamp (most recent first) and limit
        filtered_history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        if limit:
            filtered_history = filtered_history[:limit]
        
        return filtered_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notification history: {str(e)}")

@router.post("/history/{notification_id}/read")
async def mark_notification_as_read(notification_id: str):
    """Mark a notification as read"""
    try:
        global notification_history
        for notification in notification_history:
            if notification["id"] == notification_id:
                notification["read"] = True
                break
        return {"status": "success", "message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")

@router.delete("/history/{notification_id}")
async def delete_notification(notification_id: str):
    """Delete a notification"""
    try:
        global notification_history
        notification_history = [n for n in notification_history if n["id"] != notification_id]
        return {"status": "success", "message": "Notification deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete notification: {str(e)}")

@router.post("/history/mark-all-read")
async def mark_all_notifications_as_read():
    """Mark all notifications as read"""
    try:
        global notification_history
        for notification in notification_history:
            notification["read"] = True
        return {"status": "success", "message": "All notifications marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark all notifications as read: {str(e)}")

@router.delete("/history/clear")
async def clear_notification_history():
    """Clear all notification history"""
    try:
        global notification_history
        notification_history = []
        return {"status": "success", "message": "Notification history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear notification history: {str(e)}")

@router.get("/stats")
async def get_notification_stats():
    """Get notification statistics"""
    try:
        total = len(notification_history)
        unread = len([n for n in notification_history if not n["read"]])
        
        # Count by type
        by_type = {}
        for notification in notification_history:
            notification_type = notification["type"]
            by_type[notification_type] = by_type.get(notification_type, 0) + 1
        
        # Count by category
        by_category = {}
        for notification in notification_history:
            category = notification["category"]
            by_category[category] = by_category.get(category, 0) + 1
        
        return {
            "total": total,
            "unread": unread,
            "read": total - unread,
            "by_type": by_type,
            "by_category": by_category
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notification stats: {str(e)}")

@router.post("/send")
async def send_notification(notification: Dict[str, Any]):
    """Send a new notification"""
    try:
        new_notification = {
            "id": str(int(datetime.utcnow().timestamp())),
            "type": notification.get("type", "in_app"),
            "category": notification.get("category", "system"),
            "title": notification.get("title", ""),
            "message": notification.get("message", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "read": False,
            "actionTaken": None
        }
        
        global notification_history
        notification_history.insert(0, new_notification)
        
        return new_notification
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")
