from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from ...database import get_db
from ...services.search_service import search_service
from ...utils.audit_logger import audit_logger_instance, AuditAction

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced schemas for v2
class SearchRequestV2(BaseModel):
    """Enhanced search request for v2"""
    query: str = Field(..., description="Search query")
    search_type: str = Field("fulltext", regex="^(fulltext|fuzzy|regex|semantic)$")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    highlighting: bool = Field(True, description="Enable result highlighting")
    facets: Optional[List[str]] = Field(None, description="Fields to facet on")
    sort: Optional[List[Dict[str, str]]] = Field(None, description="Sort configuration")
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)
    include_metadata: bool = Field(True, description="Include result metadata")

class SearchResultV2(BaseModel):
    """Enhanced search result for v2"""
    id: int
    title: str
    content: str
    highlights: Optional[Dict[str, List[str]]]
    score: float
    metadata: Optional[Dict[str, Any]]
    archive_id: Optional[int]
    policy_id: Optional[int]
    created_at: datetime
    tags: List[str]

class SearchResponseV2(BaseModel):
    """Enhanced search response for v2"""
    query: str
    results: List[SearchResultV2]
    total: int
    took: float
    facets: Optional[Dict[str, Dict[str, int]]]
    suggestions: Optional[List[str]]
    aggregations: Optional[Dict[str, Any]]

class SearchSuggestion(BaseModel):
    """Search suggestion"""
    text: str
    score: float
    type: str

class SearchAnalytics(BaseModel):
    """Search analytics"""
    popular_queries: List[Dict[str, Any]]
    search_volume: Dict[str, int]
    avg_response_time: float
    zero_result_queries: List[str]

# Initialize search service
search_service = search_service

@router.post("/", response_model=SearchResponseV2)
async def search(
    request: SearchRequestV2,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Enhanced search with multiple search types and advanced features"""
    try:
        start_time = datetime.now()
        
        # Perform search based on type
        if request.search_type == "semantic":
            results = await _semantic_search(db, request)
        elif request.search_type == "fuzzy":
            results = await _fuzzy_search(db, request)
        elif request.search_type == "regex":
            results = await _regex_search(db, request)
        else:  # fulltext
            results = await _fulltext_search(db, request)
        
        # Calculate search time
        search_time = (datetime.now() - start_time).total_seconds()
        
        # Log search query for analytics
        background_tasks.add_task(
            _log_search_analytics,
            request.query,
            len(results.get('results', [])),
            search_time
        )
        
        return SearchResponseV2(
            query=request.query,
            results=results.get('results', []),
            total=results.get('total', 0),
            took=search_time,
            facets=results.get('facets'),
            suggestions=results.get('suggestions'),
            aggregations=results.get('aggregations')
        )
        
    except Exception as e:
        logger.error(f"Error performing search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggest", response_model=List[SearchSuggestion])
async def get_search_suggestions(
    query: str = Query(..., description="Partial query for suggestions"),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get search suggestions as user types"""
    try:
        suggestions = await _get_suggestions(db, query, limit)
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics", response_model=SearchAnalytics)
async def get_search_analytics(
    period_days: int = Query(30, description="Period in days for analytics"),
    db: Session = Depends(get_db)
):
    """Get search analytics and insights"""
    try:
        analytics = await _get_search_analytics(db, period_days)
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting search analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index/rebuild")
async def rebuild_search_index(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Rebuild the search index"""
    try:
        # Add background task for index rebuilding
        background_tasks.add_task(_rebuild_search_index, db)
        
        return {
            "message": "Search index rebuild initiated",
            "status": "processing",
            "estimated_time": "5-10 minutes"
        }
        
    except Exception as e:
        logger.error(f"Error rebuilding search index: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index/status")
async def get_index_status(db: Session = Depends(get_db)):
    """Get search index status"""
    try:
        status = await _get_index_status(db)
        return status
        
    except Exception as e:
        logger.error(f"Error getting index status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index/optimize")
async def optimize_search_index(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Optimize the search index for better performance"""
    try:
        background_tasks.add_task(_optimize_search_index, db)
        
        return {
            "message": "Search index optimization initiated",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error optimizing search index: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/facets")
async def get_search_facets(
    field: str = Query(..., description="Field to get facets for"),
    query: Optional[str] = Query(None, description="Query to filter facets"),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get facet values for a specific field"""
    try:
        facets = await _get_facets(db, field, query, size)
        return facets
        
    except Exception as e:
        logger.error(f"Error getting facets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
async def save_search(
    name: str = Field(..., description="Name for saved search"),
    query: str = Field(..., description="Search query"),
    filters: Optional[Dict[str, Any]] = Field(None),
    user_id: str = Field(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Save a search for later use"""
    try:
        # This would implement saved search logic
        return {
            "message": "Search saved successfully",
            "search_id": f"saved_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "name": name
        }
        
    except Exception as e:
        logger.error(f"Error saving search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/saved")
async def get_saved_searches(
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Get saved searches for a user"""
    try:
        # This would implement saved searches retrieval
        return {
            "saved_searches": [],
            "total": 0
        }
        
    except Exception as e:
        logger.error(f"Error getting saved searches: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/saved/{search_id}")
async def delete_saved_search(
    search_id: str,
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Delete a saved search"""
    try:
        # This would implement saved search deletion
        return {
            "message": "Saved search deleted successfully",
            "search_id": search_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting saved search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def _fulltext_search(db: Session, request: SearchRequestV2) -> Dict[str, Any]:
    """Perform fulltext search"""
    # This would implement actual fulltext search
    return {
        "results": [],
        "total": 0,
        "facets": {},
        "suggestions": [],
        "aggregations": {}
    }

async def _semantic_search(db: Session, request: SearchRequestV2) -> Dict[str, Any]:
    """Perform semantic search using embeddings"""
    # This would implement semantic search
    return {
        "results": [],
        "total": 0,
        "facets": {},
        "suggestions": [],
        "aggregations": {}
    }

async def _fuzzy_search(db: Session, request: SearchRequestV2) -> Dict[str, Any]:
    """Perform fuzzy search"""
    # This would implement fuzzy search
    return {
        "results": [],
        "total": 0,
        "facets": {},
        "suggestions": [],
        "aggregations": {}
    }

async def _regex_search(db: Session, request: SearchRequestV2) -> Dict[str, Any]:
    """Perform regex search"""
    # This would implement regex search
    return {
        "results": [],
        "total": 0,
        "facets": {},
        "suggestions": [],
        "aggregations": {}
    }

async def _get_suggestions(db: Session, query: str, limit: int) -> List[SearchSuggestion]:
    """Get search suggestions"""
    # This would implement suggestion logic
    return []

async def _get_search_analytics(db: Session, period_days: int) -> SearchAnalytics:
    """Get search analytics"""
    # This would implement analytics calculation
    return SearchAnalytics(
        popular_queries=[],
        search_volume={},
        avg_response_time=0.0,
        zero_result_queries=[]
    )

async def _log_search_analytics(query: str, result_count: int, search_time: float):
    """Log search analytics"""
    logger.info(f"Search query: '{query}', results: {result_count}, time: {search_time:.3f}s")

async def _rebuild_search_index(db: Session):
    """Rebuild search index in background"""
    logger.info("Rebuilding search index...")
    # This would implement index rebuilding

async def _get_index_status(db: Session) -> Dict[str, Any]:
    """Get search index status"""
    return {
        "status": "healthy",
        "document_count": 0,
        "index_size": "0 MB",
        "last_updated": datetime.now(),
        "optimization_score": 100
    }

async def _optimize_search_index(db: Session):
    """Optimize search index in background"""
    logger.info("Optimizing search index...")
    # This would implement index optimization

async def _get_facets(db: Session, field: str, query: Optional[str], size: int) -> Dict[str, int]:
    """Get facet values"""
    # This would implement faceting
    return {}
