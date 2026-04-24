from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..database import get_db
from ..schemas.search import (
    SearchRequest, SearchResponse, AdvancedSearchRequest,
    AutocompleteRequest, AutocompleteResponse,
    SuggestionRequest, SuggestionResponse,
    SearchAnalytics, SearchStats, ErrorResponse, SuccessResponse
)
from ..services.search_service import search_service
from ..utils.index_manager import index_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/search", tags=["search"])

@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Perform a search across archive records
    
    - **query**: Search query text (optional for filtered searches)
    - **search_type**: Type of search (full_text, faceted, autocomplete)
    - **filters**: List of filters to apply
    - **sort_by**: Field to sort by (relevance, created_at, etc.)
    - **sort_order**: Sort order (asc, desc)
    - **page**: Page number for pagination
    - **size**: Number of results per page
    - **highlight**: Whether to return highlighted snippets
    - **include_aggregations**: Whether to include aggregation results
    """
    try:
        # Extract request metadata
        user_id = http_request.headers.get("x-user-id")
        session_id = http_request.headers.get("x-session-id")
        ip_address = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent", "unknown")
        
        # Perform search
        result = await search_service.search(
            request=request,
            db=db,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/advanced", response_model=SearchResponse)
async def advanced_search(
    request: AdvancedSearchRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Perform advanced search with archive-specific filters
    
    - **query**: Search query text
    - **archive_filters**: Archive-specific filters (policy, data_type, etc.)
    - **include_deleted**: Whether to include deleted records
    - **include_expired**: Whether to include expired records
    """
    try:
        # Convert archive filters to standard filters
        filters = request.filters or []
        
        if request.archive_filters:
            af = request.archive_filters
            
            if af.policy_id:
                filters.append({
                    "field": "policy_id",
                    "operator": "in",
                    "value": af.policy_id
                })
            
            if af.data_type:
                filters.append({
                    "field": "data_type",
                    "operator": "in",
                    "value": af.data_type
                })
            
            if af.status:
                filters.append({
                    "field": "status",
                    "operator": "in",
                    "value": af.status
                })
            
            if af.file_size_min is not None or af.file_size_max is not None:
                range_filter = {"field": "file_size_bytes"}
                if af.file_size_min is not None:
                    range_filter["gte"] = af.file_size_min
                if af.file_size_max is not None:
                    range_filter["lte"] = af.file_size_max
                filters.append(range_filter)
            
            if af.archived_after or af.archived_before:
                range_filter = {"field": "archived_at"}
                if af.archived_after:
                    range_filter["gte"] = af.archived_after.isoformat()
                if af.archived_before:
                    range_filter["lte"] = af.archived_before.isoformat()
                filters.append(range_filter)
            
            if af.expires_after or af.expires_before:
                range_filter = {"field": "expires_at"}
                if af.expires_after:
                    range_filter["gte"] = af.expires_after.isoformat()
                if af.expires_before:
                    range_filter["lte"] = af.expires_before.isoformat()
                filters.append(range_filter)
        
        # Add status filters for deleted/expired
        if not request.include_deleted:
            filters.append({
                "field": "status",
                "operator": "nin",
                "value": ["deleted"]
            })
        
        if not request.include_expired:
            filters.append({
                "field": "status",
                "operator": "nin",
                "value": ["expired"]
            })
        
        # Create search request with converted filters
        search_request = SearchRequest(
            query=request.query,
            search_type=request.search_type,
            filters=filters,
            sort_by=request.sort_by,
            sort_order=request.sort_order,
            page=request.page,
            size=request.size,
            highlight=request.highlight,
            include_aggregations=request.include_aggregations,
            aggregation_fields=request.aggregation_fields,
            min_score=request.min_score
        )
        
        # Extract request metadata
        user_id = http_request.headers.get("x-user-id")
        session_id = http_request.headers.get("x-session-id")
        ip_address = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent", "unknown")
        
        # Perform search
        result = await search_service.search(
            request=search_request,
            db=db,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=SearchResponse)
async def search_get(
    q: Optional[str] = Query(None, description="Search query"),
    type: str = Query("full_text", description="Search type"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Results per page"),
    sort_by: str = Query("relevance", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    policy_id: Optional[List[int]] = Query(None, description="Filter by policy IDs"),
    data_type: Optional[List[str]] = Query(None, description="Filter by data types"),
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    http_request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Simple search using query parameters
    
    - **q**: Search query
    - **type**: Search type (full_text, faceted, autocomplete)
    - **page**: Page number
    - **size**: Results per page
    - **sort_by**: Sort field
    - **sort_order**: Sort order
    - **policy_id**: Filter by policy IDs
    - **data_type**: Filter by data types
    - **status**: Filter by status
    """
    try:
        # Build filters from query parameters
        filters = []
        
        if policy_id:
            filters.append({
                "field": "policy_id",
                "operator": "in",
                "value": policy_id
            })
        
        if data_type:
            filters.append({
                "field": "data_type",
                "operator": "in",
                "value": data_type
            })
        
        if status:
            filters.append({
                "field": "status",
                "operator": "in",
                "value": status
            })
        
        # Create search request
        request = SearchRequest(
            query=q,
            search_type=type,
            filters=filters,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Extract request metadata
        user_id = http_request.headers.get("x-user-id")
        session_id = http_request.headers.get("x-session-id")
        ip_address = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent", "unknown")
        
        # Perform search
        result = await search_service.search(
            request=request,
            db=db,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return result
        
    except Exception as e:
        logger.error(f"GET search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(request: AutocompleteRequest):
    """
    Get autocomplete suggestions for search queries
    
    - **prefix**: Text prefix to autocomplete
    - **field**: Field to search in (default: original_data_id)
    - **size**: Number of suggestions to return
    - **suggest_type**: Type of suggestion (completion, prefix, fuzzy)
    """
    try:
        result = await search_service.autocomplete(request)
        return result
        
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_get(
    prefix: str = Query(..., description="Text prefix to autocomplete"),
    field: str = Query("original_data_id", description="Field to search in"),
    size: int = Query(10, ge=1, le=50, description="Number of suggestions")
):
    """
    Get autocomplete suggestions using query parameters
    """
    try:
        request = AutocompleteRequest(
            prefix=prefix,
            field=field,
            size=size
        )
        
        result = await search_service.autocomplete(request)
        return result
        
    except Exception as e:
        logger.error(f"GET autocomplete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggestions", response_model=SuggestionResponse)
async def suggestions(
    request: SuggestionRequest,
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on historical queries
    
    - **query**: Query to get suggestions for
    - **size**: Number of suggestions to return
    - **category**: Optional category filter
    """
    try:
        result = await search_service.get_suggestions(request, db)
        return result
        
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions", response_model=SuggestionResponse)
async def suggestions_get(
    q: str = Query(..., description="Query to get suggestions for"),
    size: int = Query(5, ge=1, le=20, description="Number of suggestions"),
    category: Optional[str] = Query(None, description="Category filter"),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions using query parameters
    """
    try:
        request = SuggestionRequest(
            query=q,
            size=size,
            category=category
        )
        
        result = await search_service.get_suggestions(request, db)
        return result
        
    except Exception as e:
        logger.error(f"GET suggestions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics", response_model=SearchAnalytics)
async def get_analytics(
    period_type: str = Query("day", description="Period type (hour, day, week, month)"),
    periods: int = Query(7, ge=1, le=365, description="Number of periods"),
    db: Session = Depends(get_db)
):
    """
    Get search analytics for the specified period
    
    - **period_type**: Type of period (hour, day, week, month)
    - **periods**: Number of periods to analyze
    """
    try:
        analytics = await search_service.get_search_analytics(period_type, periods)
        return analytics
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=SearchStats)
async def get_search_stats(db: Session = Depends(get_db)):
    """
    Get search system statistics
    
    Returns information about:
    - Total documents indexed
    - Index health and size
    - Recent search activity
    - Popular queries
    """
    try:
        # Get index stats
        index_stats = await index_manager.get_index_stats("archive_records")
        
        # Get cluster health
        cluster_health = await index_manager.get_cluster_health()
        
        # Get basic analytics
        analytics = await search_service.get_search_analytics("day", 1)
        
        stats = SearchStats(
            total_documents=index_stats.get("document_count", 0) if index_stats else 0,
            total_indices=len(await index_manager.list_indices()),
            total_size_bytes=index_stats.get("size_bytes", 0) if index_stats else 0,
            avg_document_size_bytes=(
                index_stats.get("size_bytes", 0) / max(1, index_stats.get("document_count", 1))
                if index_stats else 0
            ),
            search_queries_last_24h=analytics.total_searches,
            avg_response_time_ms=analytics.avg_response_time_ms,
            popular_queries=analytics.top_queries,
            index_health={"archive_records": cluster_health.get("status", "unknown")}
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Search stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reindex", response_model=SuccessResponse)
async def reindex(db: Session = Depends(get_db)):
    """
    Reindex all archive records from the database
    
    This operation can take a while for large datasets.
    It will recreate the search index with all current records.
    """
    try:
        # Reindex all records
        indexed_count = await search_service.reindex_all_records(db)
        
        return SuccessResponse(
            message=f"Successfully reindexed {indexed_count} archive records",
            data={"indexed_count": indexed_count},
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Reindex error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index/refresh", response_model=SuccessResponse)
async def refresh_index():
    """
    Refresh the search index to make changes visible
    
    This makes recent indexing changes available for search.
    """
    try:
        success = await index_manager.refresh_index("archive_records")
        
        if success:
            return SuccessResponse(
                message="Search index refreshed successfully",
                timestamp=datetime.utcnow()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to refresh index")
        
    except Exception as e:
        logger.error(f"Refresh index error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def search_health():
    """
    Check the health of the search system
    
    Returns:
    - Elasticsearch connection status
    - Index existence and health
    - Overall system status
    """
    try:
        # Test Elasticsearch connection
        es_connected = await index_manager.test_connection()
        
        # Check if main index exists
        index_exists = await index_manager.index_exists("archive_records")
        
        # Get cluster health
        cluster_health = await index_manager.get_cluster_health()
        
        health_status = {
            "elasticsearch_connected": es_connected,
            "main_index_exists": index_exists,
            "cluster_status": cluster_health.get("status", "unknown"),
            "overall_status": "healthy" if es_connected and index_exists else "unhealthy",
            "timestamp": datetime.utcnow()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Search health check error: {e}")
        return {
            "elasticsearch_connected": False,
            "main_index_exists": False,
            "cluster_status": "error",
            "overall_status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }
