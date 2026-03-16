import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.database import get_db, Base, engine
from app.models import ArchivePolicy, ArchiveRecord
from app.schemas import ArchiveStatus, DataType

# Override database for testing
Base.metadata.create_all(bind=engine)

def get_test_db():
    """Test database session"""
    from sqlalchemy.orm import sessionmaker
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = get_test_db

client = TestClient(app)

@pytest.fixture
def test_policy():
    """Create a test policy"""
    with TestClient(app) as client:
        policy_data = {
            "name": "test_policy_api",
            "description": "Test policy for API tests",
            "ttl_days": 30,
            "compression_enabled": True,
            "encryption_enabled": False,
            "auto_cleanup": True
        }
        response = client.post("/api/v1/policies", json=policy_data)
        assert response.status_code == 200
        return response.json()

@pytest.fixture
def sample_policy(test_policy):
    """Return sample policy data"""
    return test_policy

class TestHealthAPI:
    """Test health check endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

class TestPolicyAPI:
    """Test policy management endpoints"""
    
    def test_create_policy(self):
        """Test creating a new policy"""
        policy_data = {
            "name": "test_create_policy",
            "description": "Test policy creation",
            "ttl_days": 60,
            "compression_enabled": False,
            "encryption_enabled": True,
            "auto_cleanup": True
        }
        response = client.post("/api/v1/policies", json=policy_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "test_create_policy"
        assert data["ttl_days"] == 60
        assert data["compression_enabled"] is False
        assert data["encryption_enabled"] is True
        assert "id" in data
        assert "created_at" in data
    
    def test_create_policy_duplicate_name(self):
        """Test creating policy with duplicate name"""
        policy_data = {
            "name": "test_duplicate",
            "description": "First policy",
            "ttl_days": 30
        }
        
        # Create first policy
        response1 = client.post("/api/v1/policies", json=policy_data)
        assert response1.status_code == 200
        
        # Try to create duplicate
        response2 = client.post("/api/v1/policies", json=policy_data)
        assert response2.status_code == 400
    
    def test_list_policies(self, sample_policy):
        """Test listing policies"""
        response = client.get("/api/v1/policies")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that our test policy is in the list
        policy_ids = [policy["id"] for policy in data]
        assert sample_policy["id"] in policy_ids
    
    def test_get_policy(self, sample_policy):
        """Test getting a specific policy"""
        response = client.get(f"/api/v1/policies/{sample_policy['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_policy["id"]
        assert data["name"] == sample_policy["name"]
    
    def test_get_nonexistent_policy(self):
        """Test getting a policy that doesn't exist"""
        response = client.get("/api/v1/policies/99999")
        assert response.status_code == 404

class TestArchiveAPI:
    """Test archive management endpoints"""
    
    def test_create_archive_record(self, sample_policy):
        """Test creating an archive record"""
        record_data = {
            "policy_id": sample_policy["id"],
            "original_data_id": "test_data_123",
            "data_type": "user_data",
            "metadata": '{"key": "value"}'
        }
        response = client.post("/api/v1/archives", json=record_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["policy_id"] == sample_policy["id"]
        assert data["original_data_id"] == "test_data_123"
        assert data["data_type"] == "user_data"
        assert data["status"] == ArchiveStatus.ARCHIVED
        assert data["is_expired"] is False
        assert data["days_until_expiry"] > 0
        assert "expires_at" in data
        assert "archived_at" in data
    
    def test_create_archive_record_invalid_policy(self):
        """Test creating archive record with invalid policy"""
        record_data = {
            "policy_id": 99999,
            "original_data_id": "test_invalid_policy",
            "data_type": "logs"
        }
        response = client.post("/api/v1/archives", json=record_data)
        assert response.status_code == 400
    
    def test_list_archives(self, sample_policy):
        """Test listing archive records"""
        # Create a few records first
        for i in range(3):
            record_data = {
                "policy_id": sample_policy["id"],
                "original_data_id": f"test_list_{i}",
                "data_type": "cache"
            }
            client.post("/api/v1/archives", json=record_data)
        
        # List records
        response = client.get("/api/v1/archives")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
    
    def test_list_archives_with_filters(self, sample_policy):
        """Test listing archives with filters"""
        # Create records with different data types
        record_types = ["user_data", "logs", "backup"]
        for i, data_type in enumerate(record_types):
            record_data = {
                "policy_id": sample_policy["id"],
                "original_data_id": f"test_filter_{i}",
                "data_type": data_type
            }
            client.post("/api/v1/archives", json=record_data)
        
        # Filter by policy
        response = client.get(f"/api/v1/archives?policy_id={sample_policy['id']}")
        assert response.status_code == 200
        data = response.json()
        for record in data:
            assert record["policy_id"] == sample_policy["id"]
        
        # Filter by status
        response = client.get("/api/v1/archives?status=archived")
        assert response.status_code == 200
        data = response.json()
        for record in data:
            assert record["status"] == ArchiveStatus.ARCHIVED
    
    def test_get_archive_record(self, sample_policy):
        """Test getting a specific archive record"""
        # Create a record first
        record_data = {
            "policy_id": sample_policy["id"],
            "original_data_id": "test_get_specific",
            "data_type": "temp_files"
        }
        create_response = client.post("/api/v1/archives", json=record_data)
        created_record = create_response.json()
        
        # Get the record
        response = client.get(f"/api/v1/archives/{created_record['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == created_record["id"]
        assert data["original_data_id"] == "test_get_specific"
    
    def test_get_nonexistent_archive_record(self):
        """Test getting a record that doesn't exist"""
        response = client.get("/api/v1/archives/99999")
        assert response.status_code == 404
    
    def test_delete_archive_record(self, sample_policy):
        """Test deleting an archive record"""
        # Create a record first
        record_data = {
            "policy_id": sample_policy["id"],
            "original_data_id": "test_delete_me",
            "data_type": "other"
        }
        create_response = client.post("/api/v1/archives", json=record_data)
        created_record = create_response.json()
        
        # Delete the record
        response = client.delete(f"/api/v1/archives/{created_record['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        
        # Verify it's marked as deleted
        get_response = client.get(f"/api/v1/archives/{created_record['id']}")
        deleted_record = get_response.json()
        assert deleted_record["status"] == ArchiveStatus.DELETED
    
    def test_delete_nonexistent_archive_record(self):
        """Test deleting a record that doesn't exist"""
        response = client.delete("/api/v1/archives/99999")
        assert response.status_code == 404

class TestCleanupAPI:
    """Test cleanup endpoints"""
    
    def test_trigger_cleanup(self, sample_policy):
        """Test triggering manual cleanup"""
        # Create a record that will expire soon
        record_data = {
            "policy_id": sample_policy["id"],
            "original_data_id": "test_cleanup",
            "data_type": "user_data"
        }
        client.post("/api/v1/archives", json=record_data)
        
        # Trigger cleanup
        response = client.post("/api/v1/archives/cleanup")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "deleted_count" in data or "Cleaned up" in data["message"]
    
    def test_trigger_cleanup_with_policy(self, sample_policy):
        """Test triggering cleanup for specific policy"""
        response = client.post(f"/api/v1/archives/cleanup?policy_id={sample_policy['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data

class TestStatsAPI:
    """Test statistics endpoints"""
    
    def test_get_stats(self):
        """Test getting service statistics"""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_records" in data
        assert "active_records" in data
        assert "expired_records" in data
        assert "deleted_records" in data
        assert "total_storage_bytes" in data
        assert "policies_count" in data
        
        # Validate data types
        assert isinstance(data["total_records"], int)
        assert isinstance(data["active_records"], int)
        assert isinstance(data["expired_records"], int)
        assert isinstance(data["deleted_records"], int)
        assert isinstance(data["total_storage_bytes"], int)
        assert isinstance(data["policies_count"], int)

class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_endpoint(self):
        """Test accessing invalid endpoint"""
        response = client.get("/api/v1/invalid")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """Test using invalid HTTP method"""
        response = client.put("/api/v1/health")
        assert response.status_code == 405
    
    def test_invalid_json(self):
        """Test sending invalid JSON"""
        response = client.post(
            "/api/v1/policies",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__])
