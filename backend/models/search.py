from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class SearchQuery(Base):
    """Model for storing search queries and analytics"""
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String(500), nullable=False, index=True)
    filters = Column(JSON)  # Store applied filters as JSON
    results_count = Column(Integer, default=0)
    response_time_ms = Column(Float)
    user_id = Column(String(255), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    
    # Search metadata
    index_name = Column(String(100), nullable=False)
    search_type = Column(String(50), default="full_text")  # full_text, faceted, autocomplete
    sort_by = Column(String(100))
    sort_order = Column(String(10), default="desc")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    search_results = relationship("SearchResult", back_populates="query")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_query_time', 'user_id', 'created_at'),
        Index('idx_session_time', 'session_id', 'created_at'),
        Index('idx_query_type_time', 'search_type', 'created_at'),
    )
    
    def __repr__(self):
        return f"<SearchQuery(id={self.id}, query='{self.query_text[:50]}...', results={self.results_count})>"

class SearchResult(Base):
    """Model for storing individual search results"""
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("search_queries.id"), nullable=False, index=True)
    archive_record_id = Column(Integer, ForeignKey("archive_records.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    
    # Result metadata
    title = Column(String(500))
    description = Column(Text)
    highlights = Column(JSON)  # Search highlights as JSON
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    query = relationship("SearchQuery", back_populates="search_results")
    archive_record = relationship("ArchiveRecord")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_query_rank', 'query_id', 'rank'),
        Index('idx_record_score', 'archive_record_id', 'score'),
    )
    
    def __repr__(self):
        return f"<SearchResult(id={self.id}, query_id={self.query_id}, rank={self.rank}, score={self.score})>"

class SearchSuggestion(Base):
    """Model for storing search suggestions and autocomplete"""
    __tablename__ = "search_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    suggestion_text = Column(String(500), nullable=False, unique=True, index=True)
    frequency = Column(Integer, default=1)
    category = Column(String(100), nullable=True, index=True)
    context = Column(JSON)  # Additional context for suggestions
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SearchSuggestion(id={self.id}, text='{self.suggestion_text}', frequency={self.frequency})>"

class SearchIndex(Base):
    """Model for managing search indices"""
    __tablename__ = "search_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    index_name = Column(String(100), unique=True, nullable=False, index=True)
    index_pattern = Column(String(100))  # For time-based indices (e.g., "archives-YYYY.MM")
    
    # Index configuration
    mapping = Column(JSON)  # Elasticsearch mapping configuration
    settings = Column(JSON)  # Elasticsearch settings
    
    # Index status
    status = Column(String(50), default="creating")  # creating, active, updating, deleting, error
    document_count = Column(Integer, default=0)
    size_bytes = Column(Integer, default=0)
    
    # Index lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_reindexed_at = Column(DateTime(timezone=True))
    
    # Auto-reindexing settings
    auto_reindex = Column(Boolean, default=False)
    reindex_interval_hours = Column(Integer, default=24)
    
    def __repr__(self):
        return f"<SearchIndex(id={self.id}, name='{self.index_name}', status='{self.status}', docs={self.document_count})>"

class SearchAnalytics(Base):
    """Model for aggregated search analytics"""
    __tablename__ = "search_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Time period for aggregation
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String(20), default="hour")  # hour, day, week, month
    
    # Search metrics
    total_searches = Column(Integer, default=0)
    unique_searches = Column(Integer, default=0)
    avg_response_time_ms = Column(Float, default=0.0)
    avg_results_per_search = Column(Float, default=0.0)
    
    # User metrics
    unique_users = Column(Integer, default=0)
    unique_sessions = Column(Integer, default=0)
    
    # Popular queries
    top_queries = Column(JSON)  # List of popular queries with counts
    top_filters = Column(JSON)  # List of popular filters with counts
    
    # Zero results metrics
    zero_results_searches = Column(Integer, default=0)
    zero_results_rate = Column(Float, default=0.0)
    
    # Performance metrics
    slow_searches = Column(Integer, default=0)  # Searches > 2 seconds
    error_searches = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_period_type_start', 'period_type', 'period_start'),
        Index('idx_period_start_end', 'period_start', 'period_end'),
    )
    
    def __repr__(self):
        return f"<SearchAnalytics(id={self.id}, period='{self.period_type}', searches={self.total_searches})>"
