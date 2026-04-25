from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class SearchType(str, Enum):
    FULL_TEXT = "full_text"
    FACETED = "faceted"
    AUTOCOMPLETE = "autocomplete"
    SUGGEST = "suggest"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SortField(str, Enum):
    RELEVANCE = "_score"
    CREATED_AT = "created_at"
    ARCHIVED_AT = "archived_at"
    EXPIRES_AT = "expires_at"
    FILE_SIZE = "file_size_bytes"
    ORIGINAL_DATA_ID = "original_data_id"

class SearchFilter(BaseModel):
    """Base model for search filters"""
    field: str
    operator: str = Field(..., regex="^(eq|ne|gt|gte|lt|lte|in|nin|contains|startswith|endswith)$")
    value: Union[str, int, float, List[Union[str, int, float]]]

class DateRangeFilter(BaseModel):
    """Date range filter for datetime fields"""
    field: str
    gte: Optional[datetime] = None
    lte: Optional[datetime] = None

class NumericRangeFilter(BaseModel):
    """Numeric range filter"""
    field: str
    gte: Optional[float] = None
    lte: Optional[float] = None

class SearchQueryBase(BaseModel):
    """Base model for search queries"""
    query: Optional[str] = None
    search_type: SearchType = SearchType.FULL_TEXT
    filters: Optional[List[Dict[str, Any]]] = []
    sort_by: SortField = SortField.RELEVANCE
    sort_order: SortOrder = SortOrder.DESC
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)
    
    @validator('query')
    def validate_query(cls, v, values):
        if not v and values.get('search_type') == SearchType.FULL_TEXT:
            raise ValueError('Query is required for full-text search')
        return v

class SearchRequest(SearchQueryBase):
    """Search request model"""
    highlight: bool = True
    include_aggregations: bool = False
    aggregation_fields: Optional[List[str]] = []
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0)

class AutocompleteRequest(BaseModel):
    """Autocomplete request model"""
    prefix: str = Field(..., min_length=1, max_length=100)
    field: str = "original_data_id"
    size: int = Field(10, ge=1, le=50)
    suggest_type: str = "completion"  # completion, prefix, fuzzy

class SuggestionRequest(BaseModel):
    """Search suggestion request model"""
    query: str = Field(..., min_length=1, max_length=100)
    size: int = Field(5, ge=1, le=20)
    category: Optional[str] = None

class SearchHit(BaseModel):
    """Individual search result"""
    id: int
    score: float
    title: Optional[str] = None
    description: Optional[str] = None
    highlights: Optional[Dict[str, List[str]]] = {}
    
    # Archive record fields
    policy_id: int
    original_data_id: str
    data_type: str
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    status: str
    expires_at: datetime
    archived_at: datetime
    deleted_at: Optional[datetime] = None
    
    # Policy information
    policy_name: Optional[str] = None
    policy_ttl_days: Optional[int] = None
    
    class Config:
        from_attributes = True

class SearchAggregation(BaseModel):
    """Search aggregation result"""
    name: str
    buckets: List[Dict[str, Any]]

class SearchResponse(BaseModel):
    """Search response model"""
    hits: List[SearchHit]
    total: int
    max_score: Optional[float] = None
    took: int  # Time in milliseconds
    timed_out: bool
    
    # Pagination
    page: int
    size: int
    total_pages: int
    
    # Aggregations
    aggregations: Optional[List[SearchAggregation]] = []
    
    # Search metadata
    query: Optional[str] = None
    search_type: SearchType
    filters: List[Dict[str, Any]] = []

class AutocompleteSuggestion(BaseModel):
    """Autocomplete suggestion"""
    text: str
    score: float
    type: str
    source: Optional[str] = None

class AutocompleteResponse(BaseModel):
    """Autocomplete response"""
    suggestions: List[AutocompleteSuggestion]
    took: int
    query: str

class SuggestionResponse(BaseModel):
    """Search suggestion response"""
    suggestions: List[str]
    took: int
    query: str

class SearchAnalytics(BaseModel):
    """Search analytics data"""
    total_searches: int
    unique_searches: int
    avg_response_time_ms: float
    avg_results_per_search: float
    unique_users: int
    unique_sessions: int
    top_queries: List[Dict[str, Any]]
    top_filters: List[Dict[str, Any]]
    zero_results_rate: float
    slow_searches_rate: float
    error_rate: float

class SearchIndexConfig(BaseModel):
    """Search index configuration"""
    index_name: str
    mapping: Dict[str, Any]
    settings: Dict[str, Any]
    auto_reindex: bool = False
    reindex_interval_hours: int = 24

class SearchIndexStatus(BaseModel):
    """Search index status"""
    index_name: str
    status: str
    document_count: int
    size_bytes: int
    health: str  # green, yellow, red
    created_at: datetime
    updated_at: datetime
    last_reindexed_at: Optional[datetime] = None

class BulkIndexRequest(BaseModel):
    """Bulk indexing request"""
    documents: List[Dict[str, Any]]
    index_name: str
    refresh: bool = False

class BulkIndexResponse(BaseModel):
    """Bulk indexing response"""
    indexed: int
    errors: List[Dict[str, Any]]
    took: int

class SearchStats(BaseModel):
    """Search statistics"""
    total_documents: int
    total_indices: int
    total_size_bytes: int
    avg_document_size_bytes: float
    search_queries_last_24h: int
    avg_response_time_ms: float
    popular_queries: List[Dict[str, Any]]
    index_health: Dict[str, str]

# Request/Response models for API documentation
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

class SuccessResponse(BaseModel):
    """Success response model"""
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime

# Filter validation models
class ArchiveFilter(BaseModel):
    """Archive-specific filters"""
    policy_id: Optional[List[int]] = None
    data_type: Optional[List[str]] = None
    status: Optional[List[str]] = None
    file_size_min: Optional[int] = None
    file_size_max: Optional[int] = None
    archived_after: Optional[datetime] = None
    archived_before: Optional[datetime] = None
    expires_after: Optional[datetime] = None
    expires_before: Optional[datetime] = None

class AdvancedSearchRequest(SearchRequest):
    """Advanced search request with archive-specific filters"""
    archive_filters: Optional[ArchiveFilter] = None
    include_deleted: bool = False
    include_expired: bool = True
