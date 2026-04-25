import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc

from ..models.search import SearchQuery, SearchResult, SearchSuggestion, SearchAnalytics
from ..schemas.search import SearchAnalytics as SearchAnalyticsSchema

logger = logging.getLogger(__name__)

class SearchAnalyticsService:
    """Service for managing search analytics and insights"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def get_analytics(
        self,
        db: Session,
        period_type: str = "day",
        periods: int = 7
    ) -> SearchAnalyticsSchema:
        """
        Get comprehensive search analytics for the specified period
        
        Args:
            db: Database session
            period_type: Type of period (hour, day, week, month)
            periods: Number of periods to analyze
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, period_type, periods)
            
            # Get basic metrics
            total_searches = await self._get_total_searches(db, start_date, end_date)
            unique_searches = await self._get_unique_searches(db, start_date, end_date)
            avg_response_time = await self._get_avg_response_time(db, start_date, end_date)
            avg_results_per_search = await self._get_avg_results_per_search(db, start_date, end_date)
            unique_users = await self._get_unique_users(db, start_date, end_date)
            unique_sessions = await self._get_unique_sessions(db, start_date, end_date)
            
            # Get top queries and filters
            top_queries = await self._get_top_queries(db, start_date, end_date, limit=10)
            top_filters = await self._get_top_filters(db, start_date, end_date, limit=10)
            
            # Get performance metrics
            zero_results_rate = await self._get_zero_results_rate(db, start_date, end_date)
            slow_searches_rate = await self._get_slow_searches_rate(db, start_date, end_date)
            error_rate = await self._get_error_rate(db, start_date, end_date)
            
            return SearchAnalyticsSchema(
                total_searches=total_searches,
                unique_searches=unique_searches,
                avg_response_time_ms=avg_response_time,
                avg_results_per_search=avg_results_per_search,
                unique_users=unique_users,
                unique_sessions=unique_sessions,
                top_queries=top_queries,
                top_filters=top_filters,
                zero_results_rate=zero_results_rate,
                slow_searches_rate=slow_searches_rate,
                error_rate=error_rate
            )
            
        except Exception as e:
            self.logger.error(f"Error getting search analytics: {e}")
            return SearchAnalyticsSchema()
    
    async def get_time_series_data(
        self,
        db: Session,
        period_type: str = "day",
        periods: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get time series data for search metrics
        
        Returns data points for each period in the specified range
        """
        try:
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, period_type, periods)
            
            # Group by time period
            time_format = self._get_time_format(period_type)
            
            query = db.query(
                func.date_trunc(time_format, SearchQuery.created_at).label('period'),
                func.count(SearchQuery.id).label('searches'),
                func.count(func.distinct(SearchQuery.query_text)).label('unique_searches'),
                func.avg(SearchQuery.response_time_ms).label('avg_response_time'),
                func.avg(SearchQuery.results_count).label('avg_results'),
                func.count(func.distinct(SearchQuery.user_id)).label('unique_users'),
                func.sum(func.case([(SearchQuery.results_count == 0, 1)], else_=0)).label('zero_results')
            ).filter(
                SearchQuery.created_at >= start_date,
                SearchQuery.created_at <= end_date
            ).group_by(
                func.date_trunc(time_format, SearchQuery.created_at)
            ).order_by(
                func.date_trunc(time_format, SearchQuery.created_at)
            ).all()
            
            result = []
            for row in query:
                result.append({
                    'period': row.period.isoformat(),
                    'searches': row.searches,
                    'unique_searches': row.unique_searches,
                    'avg_response_time_ms': float(row.avg_response_time or 0),
                    'avg_results_per_search': float(row.avg_results or 0),
                    'unique_users': row.unique_users,
                    'zero_results_rate': (row.zero_results / max(1, row.searches)) * 100
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting time series data: {e}")
            return []
    
    async def get_search_funnel(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get search funnel analysis showing user journey through search
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Total searches
            total_searches = db.query(SearchQuery).filter(
                SearchQuery.created_at >= start_date,
                SearchQuery.created_at <= end_date
            ).count()
            
            # Searches with results
            searches_with_results = db.query(SearchQuery).filter(
                SearchQuery.created_at >= start_date,
                SearchQuery.created_at <= end_date,
                SearchQuery.results_count > 0
            ).count()
            
            # Searches with clicks (assuming clicks are tracked in search results)
            searches_with_clicks = db.query(SearchResult).join(SearchQuery).filter(
                SearchQuery.created_at >= start_date,
                SearchQuery.created_at <= end_date
            ).distinct(SearchResult.query_id).count()
            
            # Unique searchers
            unique_searchers = db.query(func.count(func.distinct(SearchQuery.user_id))).filter(
                SearchQuery.created_at >= start_date,
                SearchQuery.created_at <= end_date,
                SearchQuery.user_id.isnot(None)
            ).scalar()
            
            return {
                'total_searches': total_searches,
                'searches_with_results': searches_with_results,
                'searches_with_clicks': searches_with_clicks,
                'unique_searchers': unique_searchers,
                'result_rate': (searches_with_results / max(1, total_searches)) * 100,
                'click_through_rate': (searches_with_clicks / max(1, searches_with_results)) * 100 if searches_with_results > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting search funnel: {e}")
            return {}
    
    async def get_popular_content(
        self,
        db: Session,
        limit: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get most popular archive records based on search results
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get most clicked/searched archive records
            query = db.query(
                SearchResult.archive_record_id,
                func.count(SearchResult.id).label('search_count'),
                func.avg(SearchResult.score).label('avg_score'),
                func.avg(SearchResult.rank).label('avg_rank')
            ).join(SearchQuery).filter(
                SearchQuery.created_at >= start_date,
                SearchQuery.created_at <= end_date
            ).group_by(
                SearchResult.archive_record_id
            ).order_by(
                desc('search_count')
            ).limit(limit).all()
            
            result = []
            for row in query:
                result.append({
                    'archive_record_id': row.archive_record_id,
                    'search_count': row.search_count,
                    'avg_score': float(row.avg_score or 0),
                    'avg_rank': float(row.avg_rank or 0)
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting popular content: {e}")
            return []
    
    async def get_search_performance_metrics(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get detailed search performance metrics
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Response time percentiles
            response_times = db.query(SearchQuery.response_time_ms).filter(
                SearchQuery.created_at >= start_date,
                SearchQuery.created_at <= end_date,
                SearchQuery.response_time_ms.isnot(None)
            ).all()
            
            times = [rt[0] for rt in response_times if rt[0] is not None]
            
            if times:
                times.sort()
                n = len(times)
                p50 = times[n // 2]
                p95 = times[int(n * 0.95)]
                p99 = times[int(n * 0.99)]
            else:
                p50 = p95 = p99 = 0
            
            # Search success metrics
            total_searches = db.query(SearchQuery).filter(
                SearchQuery.created_at >= start_date,
                SearchQuery.created_at <= end_date
            ).count()
            
            successful_searches = db.query(SearchQuery).filter(
                SearchQuery.created_at >= start_date,
                SearchQuery.created_at <= end_date,
                SearchQuery.results_count > 0
            ).count()
            
            # Slow searches (> 2 seconds)
            slow_searches = db.query(SearchQuery).filter(
                SearchQuery.created_at >= start_date,
                SearchQuery.created_at <= end_date,
                SearchQuery.response_time_ms > 2000
            ).count()
            
            return {
                'total_searches': total_searches,
                'successful_searches': successful_searches,
                'success_rate': (successful_searches / max(1, total_searches)) * 100,
                'slow_searches': slow_searches,
                'slow_search_rate': (slow_searches / max(1, total_searches)) * 100,
                'response_time_p50_ms': p50,
                'response_time_p95_ms': p95,
                'response_time_p99_ms': p99,
                'avg_response_time_ms': sum(times) / max(1, len(times)) if times else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def generate_analytics_report(
        self,
        db: Session,
        period_type: str = "day",
        periods: int = 7
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report
        """
        try:
            # Get basic analytics
            analytics = await self.get_analytics(db, period_type, periods)
            
            # Get time series data
            time_series = await self.get_time_series_data(db, period_type, periods)
            
            # Get search funnel
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, period_type, periods)
            funnel = await self.get_search_funnel(db, start_date, end_date)
            
            # Get popular content
            popular_content = await self.get_popular_content(db, limit=10, start_date=start_date, end_date=end_date)
            
            # Get performance metrics
            performance = await self.get_search_performance_metrics(db, start_date, end_date)
            
            return {
                'summary': analytics.dict(),
                'time_series': time_series,
                'funnel': funnel,
                'popular_content': popular_content,
                'performance': performance,
                'period_info': {
                    'period_type': period_type,
                    'periods': periods,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating analytics report: {e}")
            return {}
    
    def _calculate_start_date(self, end_date: datetime, period_type: str, periods: int) -> datetime:
        """Calculate start date based on period type and number of periods"""
        if period_type == "hour":
            return end_date - timedelta(hours=periods)
        elif period_type == "day":
            return end_date - timedelta(days=periods)
        elif period_type == "week":
            return end_date - timedelta(weeks=periods)
        elif period_type == "month":
            return end_date - timedelta(days=periods * 30)
        else:
            return end_date - timedelta(days=periods)
    
    def _get_time_format(self, period_type: str) -> str:
        """Get PostgreSQL date_trunc format for period type"""
        formats = {
            "hour": "hour",
            "day": "day",
            "week": "week",
            "month": "month"
        }
        return formats.get(period_type, "day")
    
    async def _get_total_searches(self, db: Session, start_date: datetime, end_date: datetime) -> int:
        """Get total number of searches"""
        return db.query(SearchQuery).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date
        ).count()
    
    async def _get_unique_searches(self, db: Session, start_date: datetime, end_date: datetime) -> int:
        """Get number of unique searches"""
        return db.query(func.count(func.distinct(SearchQuery.query_text))).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date,
            SearchQuery.query_text.isnot(None),
            SearchQuery.query_text != ""
        ).scalar()
    
    async def _get_avg_response_time(self, db: Session, start_date: datetime, end_date: datetime) -> float:
        """Get average response time in milliseconds"""
        result = db.query(func.avg(SearchQuery.response_time_ms)).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date,
            SearchQuery.response_time_ms.isnot(None)
        ).scalar()
        return float(result or 0)
    
    async def _get_avg_results_per_search(self, db: Session, start_date: datetime, end_date: datetime) -> float:
        """Get average number of results per search"""
        result = db.query(func.avg(SearchQuery.results_count)).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date
        ).scalar()
        return float(result or 0)
    
    async def _get_unique_users(self, db: Session, start_date: datetime, end_date: datetime) -> int:
        """Get number of unique users"""
        return db.query(func.count(func.distinct(SearchQuery.user_id))).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date,
            SearchQuery.user_id.isnot(None)
        ).scalar()
    
    async def _get_unique_sessions(self, db: Session, start_date: datetime, end_date: datetime) -> int:
        """Get number of unique sessions"""
        return db.query(func.count(func.distinct(SearchQuery.session_id))).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date,
            SearchQuery.session_id.isnot(None)
        ).scalar()
    
    async def _get_top_queries(self, db: Session, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top search queries"""
        query = db.query(
            SearchQuery.query_text,
            func.count(SearchQuery.id).label('count'),
            func.avg(SearchQuery.results_count).label('avg_results'),
            func.avg(SearchQuery.response_time_ms).label('avg_response_time')
        ).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date,
            SearchQuery.query_text.isnot(None),
            SearchQuery.query_text != ""
        ).group_by(
            SearchQuery.query_text
        ).order_by(
            desc('count')
        ).limit(limit).all()
        
        return [
            {
                'query': row.query_text,
                'count': row.count,
                'avg_results': float(row.avg_results or 0),
                'avg_response_time_ms': float(row.avg_response_time or 0)
            }
            for row in query
        ]
    
    async def _get_top_filters(self, db: Session, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top search filters"""
        # This is a simplified version - in practice you'd parse the JSON filters
        query = db.query(SearchQuery).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date,
            SearchQuery.filters.isnot(None)
        ).all()
        
        filter_counts = {}
        for search_query in query:
            if search_query.filters:
                for filter_item in search_query.filters:
                    field = filter_item.get('field', 'unknown')
                    filter_counts[field] = filter_counts.get(field, 0) + 1
        
        # Sort and limit
        sorted_filters = sorted(filter_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            {'filter': field, 'count': count}
            for field, count in sorted_filters
        ]
    
    async def _get_zero_results_rate(self, db: Session, start_date: datetime, end_date: datetime) -> float:
        """Get percentage of searches with zero results"""
        total_searches = db.query(SearchQuery).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date
        ).count()
        
        zero_results = db.query(SearchQuery).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date,
            SearchQuery.results_count == 0
        ).count()
        
        return (zero_results / max(1, total_searches)) * 100
    
    async def _get_slow_searches_rate(self, db: Session, start_date: datetime, end_date: datetime) -> float:
        """Get percentage of slow searches (> 2 seconds)"""
        total_searches = db.query(SearchQuery).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date
        ).count()
        
        slow_searches = db.query(SearchQuery).filter(
            SearchQuery.created_at >= start_date,
            SearchQuery.created_at <= end_date,
            SearchQuery.response_time_ms > 2000
        ).count()
        
        return (slow_searches / max(1, total_searches)) * 100
    
    async def _get_error_rate(self, db: Session, start_date: datetime, end_date: datetime) -> float:
        """Get search error rate (placeholder - would track actual errors)"""
        # This would be implemented based on how you track search errors
        # For now, return 0 as a placeholder
        return 0.0

# Global analytics service instance
analytics_service = SearchAnalyticsService()
