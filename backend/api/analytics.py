from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime
import json

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Sample data storage (in production, this would be a database)
share_analytics = {
    "twitter": 145,
    "facebook": 89,
    "linkedin": 67,
    "email": 23,
    "copy": 156
}

share_events = []

@router.post("/share")
async def track_share_event(event: Dict[str, Any]):
    """Track a social media share event"""
    try:
        share_data = {
            "platform": event.get("platform", "unknown"),
            "url": event.get("url", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "user_agent": event.get("user_agent", ""),
            "ip_address": event.get("ip_address", "")
        }
        
        # Store the event
        share_events.append(share_data)
        
        # Update platform counts
        platform = event.get("platform")
        if platform in share_analytics:
            share_analytics[platform] += 1
        
        return {"status": "success", "message": "Share event tracked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track share event: {str(e)}")

@router.get("/shares")
async def get_share_analytics():
    """Get share analytics data"""
    try:
        total_shares = sum(share_analytics.values())
        
        # Calculate percentages
        share_percentages = {}
        for platform, count in share_analytics.items():
            share_percentages[platform] = (count / total_shares * 100) if total_shares > 0 else 0
        
        # Get recent events
        recent_events = sorted(share_events, key=lambda x: x["timestamp"], reverse=True)[:10]
        
        return {
            "total_shares": total_shares,
            "by_platform": share_analytics,
            "percentages": share_percentages,
            "recent_events": recent_events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get share analytics: {str(e)}")

@router.get("/shares/platform/{platform}")
async def get_platform_shares(platform: str):
    """Get shares for a specific platform"""
    try:
        platform_events = [event for event in share_events if event["platform"] == platform]
        
        return {
            "platform": platform,
            "total_count": share_analytics.get(platform, 0),
            "recent_events": sorted(platform_events, key=lambda x: x["timestamp"], reverse=True)[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get platform shares: {str(e)}")

@router.get("/shares/trends")
async def get_share_trends(days: int = 30):
    """Get share trends over time"""
    try:
        # In a real implementation, this would query database for historical data
        # For now, return sample trend data
        from datetime import timedelta
        
        trends = []
        base_date = datetime.utcnow() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            # Generate sample data for each platform
            daily_data = {
                "date": date.strftime("%Y-%m-%d"),
                "twitter": max(0, share_analytics["twitter"] // days + (i % 5) - 2),
                "facebook": max(0, share_analytics["facebook"] // days + (i % 3) - 1),
                "linkedin": max(0, share_analytics["linkedin"] // days + (i % 4) - 2),
                "email": max(0, share_analytics["email"] // days + (i % 2)),
                "copy": max(0, share_analytics["copy"] // days + (i % 6) - 3)
            }
            trends.append(daily_data)
        
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get share trends: {str(e)}")

@router.get("/shares/popular-urls")
async def get_popular_urls(limit: int = 10):
    """Get most shared URLs"""
    try:
        # Count shares by URL
        url_counts = {}
        for event in share_events:
            url = event.get("url", "")
            if url:
                url_counts[url] = url_counts.get(url, 0) + 1
        
        # Sort by count and return top URLs
        popular_urls = sorted(url_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            {"url": url, "share_count": count} 
            for url, count in popular_urls
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get popular URLs: {str(e)}")
