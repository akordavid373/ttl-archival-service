import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError, RequestError
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from ..models.search import SearchIndex
from ..database import get_db

logger = logging.getLogger(__name__)

class IndexManager:
    """Manages Elasticsearch indices for the archival service"""
    
    def __init__(self, elasticsearch_url: str = "http://localhost:9200"):
        self.es = Elasticsearch([elasticsearch_url])
        self.logger = logging.getLogger(__name__)
        
        # Default mapping for archive records
        self.default_mapping = {
            "properties": {
                "id": {"type": "integer"},
                "policy_id": {"type": "integer"},
                "original_data_id": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {"type": "keyword"},
                        "suggest": {
                            "type": "completion",
                            "analyzer": "simple"
                        }
                    }
                },
                "data_type": {
                    "type": "keyword",
                    "fields": {
                        "text": {"type": "text"}
                    }
                },
                "file_path": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "file_size_bytes": {"type": "long"},
                "checksum": {"type": "keyword"},
                "metadata": {"type": "object", "dynamic": True},
                "status": {"type": "keyword"},
                "expires_at": {"type": "date"},
                "archived_at": {"type": "date"},
                "deleted_at": {"type": "date"},
                "policy_name": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "policy_ttl_days": {"type": "integer"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"}
            }
        }
        
        # Default settings
        self.default_settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "archive_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "stop",
                            "snowball"
                        ]
                    }
                }
            }
        }
    
    async def test_connection(self) -> bool:
        """Test Elasticsearch connection"""
        try:
            info = await asyncio.get_event_loop().run_in_executor(
                None, self.es.info
            )
            self.logger.info(f"Connected to Elasticsearch: {info['version']['number']}")
            return True
        except ConnectionError as e:
            self.logger.error(f"Failed to connect to Elasticsearch: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to Elasticsearch: {e}")
            return False
    
    async def create_index(
        self, 
        index_name: str, 
        mapping: Optional[Dict] = None,
        settings: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> bool:
        """Create a new Elasticsearch index"""
        try:
            # Check if index already exists
            if await self.index_exists(index_name):
                self.logger.warning(f"Index {index_name} already exists")
                return False
            
            # Use defaults if not provided
            index_mapping = mapping or self.default_mapping
            index_settings = settings or self.default_settings
            
            # Create index body
            body = {
                "settings": index_settings,
                "mappings": index_mapping
            }
            
            # Create index
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.indices.create(index=index_name, body=body)
            )
            
            self.logger.info(f"Created index: {index_name}")
            
            # Record in database if session provided
            if db:
                search_index = SearchIndex(
                    index_name=index_name,
                    mapping=index_mapping,
                    settings=index_settings,
                    status="active",
                    document_count=0,
                    size_bytes=0
                )
                db.add(search_index)
                db.commit()
            
            return True
            
        except RequestError as e:
            self.logger.error(f"Failed to create index {index_name}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating index {index_name}: {e}")
            return False
    
    async def index_exists(self, index_name: str) -> bool:
        """Check if an index exists"""
        try:
            return await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.indices.exists(index=index_name)
            )
        except Exception as e:
            self.logger.error(f"Error checking if index {index_name} exists: {e}")
            return False
    
    async def delete_index(self, index_name: str, db: Optional[Session] = None) -> bool:
        """Delete an Elasticsearch index"""
        try:
            if not await self.index_exists(index_name):
                self.logger.warning(f"Index {index_name} does not exist")
                return False
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.indices.delete(index=index_name)
            )
            
            self.logger.info(f"Deleted index: {index_name}")
            
            # Update database record if session provided
            if db:
                search_index = db.query(SearchIndex).filter(
                    SearchIndex.index_name == index_name
                ).first()
                if search_index:
                    search_index.status = "deleted"
                    db.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting index {index_name}: {e}")
            return False
    
    async def get_index_stats(self, index_name: str) -> Optional[Dict[str, Any]]:
        """Get index statistics"""
        try:
            if not await self.index_exists(index_name):
                return None
            
            stats = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.indices.stats(index=index_name)
            )
            
            index_stats = stats['indices'][index_name]
            return {
                "document_count": index_stats['total']['docs']['count'],
                "size_bytes": index_stats['total']['store']['size_in_bytes'],
                "health": "green",  # Would need cluster health call for accurate status
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting stats for index {index_name}: {e}")
            return None
    
    async def reindex(
        self, 
        source_index: str, 
        dest_index: str,
        db: Optional[Session] = None
    ) -> bool:
        """Reindex from source to destination index"""
        try:
            if not await self.index_exists(source_index):
                self.logger.error(f"Source index {source_index} does not exist")
                return False
            
            # Create destination index with same mapping
            source_mapping = await self.get_mapping(source_index)
            if not await self.create_index(dest_index, source_mapping, db=db):
                return False
            
            # Perform reindexing
            body = {
                "source": {"index": source_index},
                "dest": {"index": dest_index}
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.reindex(body=body, wait_for_completion=True)
            )
            
            self.logger.info(f"Reindexed from {source_index} to {dest_index}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error reindexing from {source_index} to {dest_index}: {e}")
            return False
    
    async def get_mapping(self, index_name: str) -> Optional[Dict[str, Any]]:
        """Get index mapping"""
        try:
            if not await self.index_exists(index_name):
                return None
            
            mapping = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.indices.get_mapping(index=index_name)
            )
            
            return mapping[index_name]['mappings']
            
        except Exception as e:
            self.logger.error(f"Error getting mapping for index {index_name}: {e}")
            return None
    
    async def update_mapping(
        self, 
        index_name: str, 
        new_mapping: Dict[str, Any],
        db: Optional[Session] = None
    ) -> bool:
        """Update index mapping (only for adding new fields)"""
        try:
            if not await self.index_exists(index_name):
                return False
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.indices.put_mapping(
                    index=index_name,
                    body=new_mapping
                )
            )
            
            self.logger.info(f"Updated mapping for index: {index_name}")
            
            # Update database record if session provided
            if db:
                search_index = db.query(SearchIndex).filter(
                    SearchIndex.index_name == index_name
                ).first()
                if search_index:
                    current_mapping = search_index.mapping or {}
                    current_mapping.update(new_mapping)
                    search_index.mapping = current_mapping
                    search_index.updated_at = datetime.utcnow()
                    db.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating mapping for index {index_name}: {e}")
            return False
    
    async def refresh_index(self, index_name: str) -> bool:
        """Refresh an index to make changes visible"""
        try:
            if not await self.index_exists(index_name):
                return False
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.indices.refresh(index=index_name)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error refreshing index {index_name}: {e}")
            return False
    
    async def optimize_index(self, index_name: str) -> bool:
        """Optimize index for better performance"""
        try:
            if not await self.index_exists(index_name):
                return False
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.indices.forcemerge(
                    index=index_name,
                    max_num_segments=1
                )
            )
            
            self.logger.info(f"Optimized index: {index_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing index {index_name}: {e}")
            return False
    
    async def list_indices(self) -> List[str]:
        """List all indices"""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.cat.indices(format="json")
            )
            
            return [index['index'] for index in result]
            
        except Exception as e:
            self.logger.error(f"Error listing indices: {e}")
            return []
    
    async def get_cluster_health(self) -> Dict[str, Any]:
        """Get cluster health information"""
        try:
            health = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.es.cluster.health()
            )
            
            return {
                "status": health['status'],
                "number_of_nodes": health['number_of_nodes'],
                "active_primary_shards": health['active_primary_shards'],
                "active_shards": health['active_shards'],
                "relocating_shards": health['relocating_shards'],
                "initializing_shards": health['initializing_shards'],
                "unassigned_shards": health['unassigned_shards']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cluster health: {e}")
            return {}
    
    async def create_time_based_index(
        self, 
        base_name: str, 
        date_pattern: str = "%Y.%m",
        db: Optional[Session] = None
    ) -> str:
        """Create a time-based index (e.g., archives-2024.01)"""
        index_name = f"{base_name}-{datetime.now().strftime(date_pattern)}"
        
        if not await self.index_exists(index_name):
            await self.create_index(index_name, db=db)
        
        return index_name
    
    async def cleanup_old_indices(
        self, 
        base_name: str, 
        retention_days: int = 90,
        db: Optional[Session] = None
    ) -> int:
        """Delete indices older than retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            indices = await self.list_indices()
            
            deleted_count = 0
            for index in indices:
                if index.startswith(base_name + "-"):
                    # Extract date from index name
                    try:
                        date_part = index.split("-")[-1]
                        index_date = datetime.strptime(date_part, "%Y.%m")
                        
                        if index_date < cutoff_date:
                            if await self.delete_index(index, db):
                                deleted_count += 1
                    except ValueError:
                        # Skip if date format is invalid
                        continue
            
            self.logger.info(f"Cleaned up {deleted_count} old indices")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old indices: {e}")
            return 0

# Global index manager instance
index_manager = IndexManager()

@asynccontextmanager
async def get_index_manager():
    """Context manager for index manager"""
    try:
        await index_manager.test_connection()
        yield index_manager
    except Exception as e:
        logger.error(f"Index manager error: {e}")
        raise
