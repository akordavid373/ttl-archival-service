import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from ..models import ArchiveRecord, ArchivePolicy
from ..models.search import SearchQuery, SearchResult, SearchSuggestion, SearchAnalytics
from ..schemas.search import (
    SearchRequest, SearchResponse, SearchHit, SearchAggregation,
    AutocompleteRequest, AutocompleteResponse, AutocompleteSuggestion,
    SuggestionRequest, SuggestionResponse, SearchAnalytics as SearchAnalyticsSchema,
    AdvancedSearchRequest, SortField, SortOrder, SearchType
)
from ..services.search_analytics_service import analytics_service
from ..utils.index_manager import index_manager

logger = logging.getLogger(__name__)

class SearchService:
    """Service for handling search operations with Elasticsearch"""
    
    def __init__(self, elasticsearch_url: str = "http://localhost:9200"):
        self.es = Elasticsearch([elasticsearch_url])
        self.logger = logging.getLogger(__name__)
        self.default_index = "archive_records"
    
    async def initialize_search(self, db: Session) -> bool:
        """Initialize search indices and ensure they exist"""
        try:
            # Test Elasticsearch connection
            if not await index_manager.test_connection():
                self.logger.error("Failed to connect to Elasticsearch")
                return False
            
            # Create default index if it doesn't exist
            if not await index_manager.index_exists(self.default_index):
                await index_manager.create_index(self.default_index, db=db)
            
            # Index existing archive records
            await self.reindex_all_records(db)
            
            self.logger.info("Search service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing search service: {e}")
            return False
    
    async def search(
        self, 
        request: SearchRequest,
        db: Session,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> SearchResponse:
        """Perform search with analytics tracking"""
        start_time = datetime.now()
        
        try:
            # Build Elasticsearch query
            es_query = await self._build_search_query(request)
            
            # Execute search
            es_result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.search(
                    index=self.default_index,
                    body=es_query,
                    size=request.size,
                    from_=(request.page - 1) * request.size
                )
            )
            
            # Process results
            hits = await self._process_search_hits(es_result['hits']['hits'])
            
            # Process aggregations if requested
            aggregations = []
            if request.include_aggregations and request.aggregation_fields:
                aggregations = await self._process_aggregations(
                    es_result.get('aggregations', {})
                )
            
            # Create response
            response = SearchResponse(
                hits=hits,
                total=es_result['hits']['total']['value'],
                max_score=es_result['hits'].get('max_score'),
                took=es_result['took'],
                timed_out=es_result['timed_out'],
                page=request.page,
                size=request.size,
                total_pages=(es_result['hits']['total']['value'] + request.size - 1) // request.size,
                aggregations=aggregations,
                query=request.query,
                search_type=request.search_type,
                filters=request.filters or []
            )
            
            # Log search analytics
            await self._log_search_analytics(
                db=db,
                request=request,
                response=response,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                start_time=start_time
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error performing search: {e}")
            raise
    
    async def autocomplete(self, request: AutocompleteRequest) -> AutocompleteResponse:
        """Get autocomplete suggestions"""
        try:
            # Build autocomplete query
            es_query = {
                "suggest": {
                    "text": request.prefix,
                    "simple_phrase": {
                        "phrase": {
                            "field": f"{request.field}.suggest",
                            "size": request.size,
                            "gram_size": 10,
                            "direct_generator": [{
                                "field": f"{request.field}.suggest",
                                "suggest_mode": "missing"
                            }],
                            "highlight": {
                                "pre_tag": "<em>",
                                "post_tag": "</em>"
                            }
                        }
                    }
                }
            }
            
            # Execute autocomplete query
            es_result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.search(
                    index=self.default_index,
                    body=es_query
                )
            )
            
            # Process suggestions
            suggestions = []
            options = es_result['suggest']['simple_phrase'][0]['options']
            
            for option in options:
                suggestions.append(AutocompleteSuggestion(
                    text=option['text'],
                    score=option['_score'],
                    type="completion",
                    source=request.field
                ))
            
            return AutocompleteResponse(
                suggestions=suggestions,
                took=es_result['took'],
                query=request.prefix
            )
            
        except Exception as e:
            self.logger.error(f"Error getting autocomplete suggestions: {e}")
            return AutocompleteResponse(
                suggestions=[],
                took=0,
                query=request.prefix
            )
    
    async def get_suggestions(self, request: SuggestionRequest, db: Session) -> SuggestionResponse:
        """Get search suggestions based on historical queries"""
        try:
            # Get suggestions from database
            query = db.query(SearchSuggestion).filter(
                SearchSuggestion.suggestion_text.ilike(f"%{request.query}%")
            )
            
            if request.category:
                query = query.filter(SearchSuggestion.category == request.category)
            
            suggestions = query.order_by(desc(SearchSuggestion.frequency)).limit(request.size).all()
            
            return SuggestionResponse(
                suggestions=[s.suggestion_text for s in suggestions],
                took=0,
                query=request.query
            )
            
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {e}")
            return SuggestionResponse(
                suggestions=[],
                took=0,
                query=request.query
            )
    
    async def index_document(self, document: Dict[str, Any], db: Session) -> bool:
        """Index a single document"""
        try:
            # Ensure index exists
            if not await index_manager.index_exists(self.default_index):
                await index_manager.create_index(self.default_index, db=db)
            
            # Index document
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.index(
                    index=self.default_index,
                    id=document['id'],
                    body=document,
                    refresh=False
                )
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error indexing document {document.get('id')}: {e}")
            return False
    
    async def bulk_index(self, documents: List[Dict[str, Any]], db: Session) -> Dict[str, Any]:
        """Bulk index multiple documents"""
        try:
            # Ensure index exists
            if not await index_manager.index_exists(self.default_index):
                await index_manager.create_index(self.default_index, db=db)
            
            # Build bulk body
            body = []
            errors = []
            
            for doc in documents:
                body.append({"index": {"_index": self.default_index, "_id": doc['id']}})
                body.append(doc)
            
            # Execute bulk request
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.bulk(body=body, refresh=False)
            )
            
            # Process results
            indexed_count = 0
            for item in result['items']:
                if 'index' in item:
                    if item['index'].get('status') in [200, 201]:
                        indexed_count += 1
                    else:
                        errors.append(item['index'])
            
            return {
                "indexed": indexed_count,
                "errors": errors,
                "took": result['took']
            }
            
        except Exception as e:
            self.logger.error(f"Error in bulk indexing: {e}")
            return {"indexed": 0, "errors": [str(e)], "took": 0}
    
    async def reindex_all_records(self, db: Session) -> int:
        """Reindex all archive records from database"""
        try:
            # Get all archive records with policy information
            records = db.query(ArchiveRecord).join(ArchivePolicy).all()
            
            documents = []
            for record in records:
                doc = await self._prepare_document_for_indexing(record)
                documents.append(doc)
            
            # Bulk index
            result = await self.bulk_index(documents, db)
            
            # Refresh index
            await index_manager.refresh_index(self.default_index)
            
            self.logger.info(f"Reindexed {result['indexed']} archive records")
            return result['indexed']
            
        except Exception as e:
            self.logger.error(f"Error reindexing records: {e}")
            return 0
    
    async def update_document(self, document_id: int, updates: Dict[str, Any]) -> bool:
        """Update an indexed document"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.update(
                    index=self.default_index,
                    id=document_id,
                    body={"doc": updates}
                )
            )
            return True
            
        except NotFoundError:
            self.logger.warning(f"Document {document_id} not found in index")
            return False
        except Exception as e:
            self.logger.error(f"Error updating document {document_id}: {e}")
            return False
    
    async def delete_document(self, document_id: int) -> bool:
        """Delete a document from index"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.delete(
                    index=self.default_index,
                    id=document_id
                )
            )
            return True
            
        except NotFoundError:
            self.logger.warning(f"Document {document_id} not found in index")
            return False
        except Exception as e:
            self.logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def get_search_analytics(
        self, 
        period_type: str = "day",
        periods: int = 7
    ) -> SearchAnalyticsSchema:
        """Get search analytics for the specified period"""
        try:
            # Get database session
            from ..database import get_db
            db = next(get_db())
            
            try:
                analytics = await analytics_service.get_analytics(db, period_type, periods)
                return analytics
            finally:
                db.close()
                
        except Exception as e:
            self.logger.error(f"Error getting search analytics: {e}")
            return SearchAnalyticsSchema()
    
    async def _build_search_query(self, request: SearchRequest) -> Dict[str, Any]:
        """Build Elasticsearch query from search request"""
        query = {"bool": {"must": [], "filter": []}}
        
        # Add text query
        if request.query:
            if request.search_type == SearchType.FULL_TEXT:
                query["bool"]["must"].append({
                    "multi_match": {
                        "query": request.query,
                        "fields": [
                            "original_data_id^3",
                            "policy_name^2",
                            "data_type",
                            "metadata.*"
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })
            elif request.search_type == SearchType.AUTOCOMPLETE:
                query["bool"]["must"].append({
                    "prefix": {
                        "original_data_id.suggest": request.query
                    }
                })
        
        # Add filters
        if request.filters:
            for filter_item in request.filters:
                field = filter_item.get("field")
                operator = filter_item.get("operator")
                value = filter_item.get("value")
                
                if operator == "eq":
                    query["bool"]["filter"].append({"term": {field: value}})
                elif operator == "in":
                    query["bool"]["filter"].append({"terms": {field: value}})
                elif operator == "range":
                    query["bool"]["filter"].append({"range": {field: value}})
        
        # Add aggregations if requested
        body = {"query": query}
        
        if request.include_aggregations and request.aggregation_fields:
            body["aggs"] = {}
            for field in request.aggregation_fields:
                body["aggs"][field] = {"terms": {"field": field}}
        
        # Add sorting
        if request.sort_by == SortField.RELEVANCE:
            body["sort"] = [{"_score": {"order": request.sort_order.value}}]
        else:
            body["sort"] = [{request.sort_by.value: {"order": request.sort_order.value}}]
        
        # Add minimum score if specified
        if request.min_score:
            body["min_score"] = request.min_score
        
        return body
    
    async def _process_search_hits(self, hits: List[Dict]) -> List[SearchHit]:
        """Process Elasticsearch hits into SearchHit objects"""
        search_hits = []
        
        for hit in hits:
            source = hit['_source']
            highlights = hit.get('highlight', {})
            
            search_hit = SearchHit(
                id=source['id'],
                score=hit['_score'],
                title=source.get('original_data_id'),
                description=source.get('metadata', {}).get('description'),
                highlights=highlights,
                policy_id=source['policy_id'],
                original_data_id=source['original_data_id'],
                data_type=source['data_type'],
                file_path=source.get('file_path'),
                file_size_bytes=source.get('file_size_bytes'),
                checksum=source.get('checksum'),
                metadata=source.get('metadata', {}),
                status=source['status'],
                expires_at=source['expires_at'],
                archived_at=source['archived_at'],
                deleted_at=source.get('deleted_at'),
                policy_name=source.get('policy_name'),
                policy_ttl_days=source.get('policy_ttl_days')
            )
            
            search_hits.append(search_hit)
        
        return search_hits
    
    async def _process_aggregations(self, aggregations: Dict[str, Any]) -> List[SearchAggregation]:
        """Process Elasticsearch aggregations"""
        result = []
        
        for name, agg_data in aggregations.items():
            if 'buckets' in agg_data:
                buckets = []
                for bucket in agg_data['buckets']:
                    buckets.append({
                        'key': bucket['key'],
                        'doc_count': bucket['doc_count']
                    })
                
                result.append(SearchAggregation(
                    name=name,
                    buckets=buckets
                ))
        
        return result
    
    async def _prepare_document_for_indexing(self, record: ArchiveRecord) -> Dict[str, Any]:
        """Prepare archive record for Elasticsearch indexing"""
        document = {
            "id": record.id,
            "policy_id": record.policy_id,
            "original_data_id": record.original_data_id,
            "data_type": record.data_type,
            "file_path": record.file_path,
            "file_size_bytes": record.file_size_bytes,
            "checksum": record.checksum,
            "metadata": record.metadata or {},
            "status": record.status,
            "expires_at": record.expires_at,
            "archived_at": record.archived_at,
            "deleted_at": record.deleted_at,
            "created_at": record.archived_at,
            "updated_at": record.archived_at
        }
        
        # Add policy information if available
        if record.policy:
            document["policy_name"] = record.policy.name
            document["policy_ttl_days"] = record.policy.ttl_days
        
        return document
    
    async def _log_search_analytics(
        self,
        db: Session,
        request: SearchRequest,
        response: SearchResponse,
        user_id: Optional[str],
        session_id: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str],
        start_time: datetime
    ):
        """Log search analytics to database"""
        try:
            # Calculate response time
            response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Create search query record
            search_query = SearchQuery(
                query_text=request.query or "",
                filters=request.filters or [],
                results_count=response.total,
                response_time_ms=response_time_ms,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                index_name=self.default_index,
                search_type=request.search_type.value,
                sort_by=request.sort_by.value,
                sort_order=request.sort_order.value
            )
            
            db.add(search_query)
            db.commit()
            
            # Log individual results (first 10 for performance)
            for i, hit in enumerate(response.hits[:10]):
                search_result = SearchResult(
                    query_id=search_query.id,
                    archive_record_id=hit.id,
                    score=hit.score,
                    rank=i + 1,
                    title=hit.title,
                    description=hit.description,
                    highlights=hit.highlights
                )
                db.add(search_result)
            
            db.commit()
            
            # Update suggestions
            if request.query:
                await self._update_suggestions(db, request.query)
            
        except Exception as e:
            self.logger.error(f"Error logging search analytics: {e}")
    
    async def _update_suggestions(self, db: Session, query: str):
        """Update search suggestions based on query"""
        try:
            # Get or create suggestion
            suggestion = db.query(SearchSuggestion).filter(
                SearchSuggestion.suggestion_text == query.lower()
            ).first()
            
            if suggestion:
                suggestion.frequency += 1
                suggestion.updated_at = datetime.now()
            else:
                suggestion = SearchSuggestion(
                    suggestion_text=query.lower(),
                    frequency=1
                )
                db.add(suggestion)
            
            db.commit()
            
        except Exception as e:
            self.logger.error(f"Error updating suggestions: {e}")

# Global search service instance
search_service = SearchService()
