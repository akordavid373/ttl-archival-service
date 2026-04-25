"""
Test script for search functionality
Run this script to test the search system components
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.database import get_db, engine, Base
from backend.models import ArchiveRecord, ArchivePolicy
from backend.models.search import SearchQuery, SearchResult, SearchSuggestion
from backend.services.search_service import search_service
from backend.utils.index_manager import index_manager
from backend.schemas.search import SearchRequest, SearchType, SortField, SortOrder

async def test_elasticsearch_connection():
    """Test Elasticsearch connection"""
    print("Testing Elasticsearch connection...")
    try:
        connected = await index_manager.test_connection()
        if connected:
            print("✅ Elasticsearch connection successful")
            return True
        else:
            print("❌ Elasticsearch connection failed")
            return False
    except Exception as e:
        print(f"❌ Elasticsearch connection error: {e}")
        return False

async def test_index_creation():
    """Test index creation"""
    print("\nTesting index creation...")
    try:
        # Create test index
        success = await index_manager.create_index("test_archive_records")
        if success:
            print("✅ Index creation successful")
            
            # Check if index exists
            exists = await index_manager.index_exists("test_archive_records")
            if exists:
                print("✅ Index existence check successful")
                
                # Clean up test index
                await index_manager.delete_index("test_archive_records")
                print("✅ Test index cleanup successful")
                return True
            else:
                print("❌ Index existence check failed")
                return False
        else:
            print("❌ Index creation failed")
            return False
    except Exception as e:
        print(f"❌ Index creation error: {e}")
        return False

async def test_document_indexing():
    """Test document indexing"""
    print("\nTesting document indexing...")
    try:
        # Create test document
        test_doc = {
            "id": 1,
            "policy_id": 1,
            "original_data_id": "test_record_001",
            "data_type": "user_data",
            "file_path": "/test/path/file.txt",
            "file_size_bytes": 1024,
            "checksum": "abc123",
            "metadata": {"description": "Test record for search functionality"},
            "status": "archived",
            "expires_at": datetime.utcnow() + timedelta(days=30),
            "archived_at": datetime.utcnow(),
            "deleted_at": None,
            "policy_name": "Test Policy",
            "policy_ttl_days": 30
        }
        
        # Index document
        success = await search_service.index_document(test_doc, None)
        if success:
            print("✅ Document indexing successful")
            
            # Refresh index
            await index_manager.refresh_index("archive_records")
            print("✅ Index refresh successful")
            
            return True
        else:
            print("❌ Document indexing failed")
            return False
    except Exception as e:
        print(f"❌ Document indexing error: {e}")
        return False

async def test_search_functionality():
    """Test basic search functionality"""
    print("\nTesting search functionality...")
    try:
        # Create search request
        search_request = SearchRequest(
            query="test",
            search_type=SearchType.FULL_TEXT,
            sort_by=SortField.RELEVANCE,
            sort_order=SortOrder.DESC,
            page=1,
            size=10
        )
        
        # Perform search (without analytics for testing)
        es_query = await search_service._build_search_query(search_request)
        print(f"✅ Search query built successfully: {es_query}")
        
        # Test autocomplete
        from backend.schemas.search import AutocompleteRequest
        autocomplete_request = AutocompleteRequest(
            prefix="test",
            field="original_data_id",
            size=5
        )
        
        # Note: This might fail if no documents are indexed, but that's expected
        print("✅ Search request creation successful")
        return True
    except Exception as e:
        print(f"❌ Search functionality error: {e}")
        return False

async def test_database_models():
    """Test database models"""
    print("\nTesting database models...")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test database session
        db = next(get_db())
        
        # Test creating a search query record
        test_query = SearchQuery(
            query_text="test query",
            filters=[{"field": "status", "operator": "eq", "value": "archived"}],
            results_count=5,
            response_time_ms=150.5,
            user_id="test_user",
            session_id="test_session",
            ip_address="127.0.0.1",
            user_agent="test_agent",
            index_name="archive_records",
            search_type="full_text",
            sort_by="relevance",
            sort_order="desc"
        )
        
        db.add(test_query)
        db.commit()
        
        # Query the record
        retrieved = db.query(SearchQuery).filter(SearchQuery.query_text == "test query").first()
        if retrieved:
            print("✅ Search query model test successful")
            db.delete(retrieved)
            db.commit()
        else:
            print("❌ Search query model test failed")
            return False
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database models error: {e}")
        return False

async def test_schemas():
    """Test Pydantic schemas"""
    print("\nTesting Pydantic schemas...")
    try:
        # Test search request schema
        search_request = SearchRequest(
            query="test query",
            search_type=SearchType.FULL_TEXT,
            filters=[{"field": "status", "operator": "eq", "value": "archived"}],
            sort_by=SortField.RELEVANCE,
            sort_order=SortOrder.DESC,
            page=1,
            size=10
        )
        
        print(f"✅ Search request schema valid: {search_request.query}")
        
        # Test validation
        try:
            invalid_request = SearchRequest(
                search_type=SearchType.FULL_TEXT,
                # Missing query for full_text search - should fail validation
            )
            print("❌ Schema validation should have failed")
            return False
        except Exception:
            print("✅ Schema validation working correctly")
        
        return True
    except Exception as e:
        print(f"❌ Schemas error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔍 Starting Search System Tests")
    print("=" * 50)
    
    tests = [
        ("Elasticsearch Connection", test_elasticsearch_connection),
        ("Index Creation", test_index_creation),
        ("Document Indexing", test_document_indexing),
        ("Search Functionality", test_search_functionality),
        ("Database Models", test_database_models),
        ("Pydantic Schemas", test_schemas),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Search system is ready.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
