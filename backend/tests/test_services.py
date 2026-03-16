import pytest
import tempfile
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models import ArchivePolicy, ArchiveRecord
from app.services import ArchiveService, PolicyService
from app.schemas import ArchivePolicyCreate, ArchiveRecordCreate, DataType

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def archive_service():
    """Create archive service instance"""
    return ArchiveService()

@pytest.fixture
def policy_service():
    """Create policy service instance"""
    return PolicyService()

@pytest.fixture
def sample_policy(db):
    """Create a sample archive policy"""
    policy = ArchivePolicy(
        name="test_policy",
        description="Test policy for unit tests",
        ttl_days=30,
        compression_enabled=True,
        encryption_enabled=False,
        auto_cleanup=True
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy

@pytest.fixture
def temp_file():
    """Create a temporary file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("This is test content for archival")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

class TestPolicyService:
    """Test cases for PolicyService"""
    
    def test_create_policy(self, db, policy_service):
        """Test creating a new policy"""
        policy_data = ArchivePolicyCreate(
            name="test_policy",
            description="Test policy",
            ttl_days=60,
            compression_enabled=False
        )
        
        policy = policy_service.create_policy(db, policy_data)
        
        assert policy.id is not None
        assert policy.name == "test_policy"
        assert policy.ttl_days == 60
        assert policy.compression_enabled is False
    
    def test_get_policy(self, db, policy_service, sample_policy):
        """Test retrieving a policy"""
        policy = policy_service.get_policy(db, sample_policy.id)
        
        assert policy is not None
        assert policy.id == sample_policy.id
        assert policy.name == sample_policy.name
    
    def test_list_policies(self, db, policy_service, sample_policy):
        """Test listing policies"""
        policies = policy_service.list_policies(db)
        
        assert len(policies) >= 1
        assert sample_policy.id in [p.id for p in policies]
    
    def test_update_policy(self, db, policy_service, sample_policy):
        """Test updating a policy"""
        updated_policy = policy_service.update_policy(
            db, 
            sample_policy.id, 
            {"ttl_days": 90, "description": "Updated description"}
        )
        
        assert updated_policy is not None
        assert updated_policy.ttl_days == 90
        assert updated_policy.description == "Updated description"

class TestArchiveService:
    """Test cases for ArchiveService"""
    
    def test_create_record(self, db, archive_service, sample_policy):
        """Test creating an archive record"""
        record_data = ArchiveRecordCreate(
            policy_id=sample_policy.id,
            original_data_id="test_data_123",
            data_type=DataType.USER_DATA,
            metadata="{'key': 'value'}"
        )
        
        record = archive_service.create_record(db, record_data)
        
        assert record.id is not None
        assert record.policy_id == sample_policy.id
        assert record.original_data_id == "test_data_123"
        assert record.data_type == DataType.USER_DATA
        assert record.status == "archived"
        assert record.expires_at > datetime.utcnow()
    
    def test_create_record_with_file(self, db, archive_service, sample_policy, temp_file):
        """Test creating an archive record with a file"""
        record_data = ArchiveRecordCreate(
            policy_id=sample_policy.id,
            original_data_id="test_file_123",
            data_type=DataType.LOGS,
            file_path=temp_file
        )
        
        record = archive_service.create_record(db, record_data)
        
        assert record.id is not None
        assert record.file_path is not None
        assert record.file_size_bytes > 0
        assert record.checksum is not None
        assert os.path.exists(record.file_path)
    
    def test_get_record(self, db, archive_service, sample_policy):
        """Test retrieving an archive record"""
        # Create a record first
        record_data = ArchiveRecordCreate(
            policy_id=sample_policy.id,
            original_data_id="test_get_123",
            data_type=DataType.BACKUP
        )
        created_record = archive_service.create_record(db, record_data)
        
        # Retrieve the record
        retrieved_record = archive_service.get_record(db, created_record.id)
        
        assert retrieved_record is not None
        assert retrieved_record.id == created_record.id
        assert retrieved_record.original_data_id == "test_get_123"
    
    def test_list_records(self, db, archive_service, sample_policy):
        """Test listing archive records"""
        # Create multiple records
        for i in range(3):
            record_data = ArchiveRecordCreate(
                policy_id=sample_policy.id,
                original_data_id=f"test_list_{i}",
                data_type=DataType.CACHE
            )
            archive_service.create_record(db, record_data)
        
        # List records
        records = archive_service.list_records(db)
        
        assert len(records) >= 3
    
    def test_delete_record(self, db, archive_service, sample_policy):
        """Test deleting an archive record"""
        # Create a record first
        record_data = ArchiveRecordCreate(
            policy_id=sample_policy.id,
            original_data_id="test_delete_123",
            data_type=DataType.TEMP_FILES
        )
        created_record = archive_service.create_record(db, record_data)
        
        # Delete the record
        success = archive_service.delete_record(db, created_record.id)
        
        assert success is True
        
        # Check that record is marked as deleted
        deleted_record = archive_service.get_record(db, created_record.id)
        assert deleted_record.status == "deleted"
        assert deleted_record.deleted_at is not None
    
    def test_cleanup_expired_records(self, db, archive_service, sample_policy):
        """Test cleanup of expired records"""
        # Create a record with expiry in the past
        record_data = ArchiveRecordCreate(
            policy_id=sample_policy.id,
            original_data_id="test_expired_123",
            data_type=DataType.OTHER
        )
        
        # Manually set expiry to past
        record = archive_service.create_record(db, record_data)
        record.expires_at = datetime.utcnow() - timedelta(days=1)
        db.commit()
        
        # Run cleanup
        deleted_count = archive_service.cleanup_expired_records(db)
        
        assert deleted_count >= 1
        
        # Check that record is marked as deleted
        cleaned_record = archive_service.get_record(db, record.id)
        assert cleaned_record.status == "deleted"
    
    def test_get_stats(self, db, archive_service, sample_policy):
        """Test getting archival statistics"""
        # Create some records
        for i in range(2):
            record_data = ArchiveRecordCreate(
                policy_id=sample_policy.id,
                original_data_id=f"test_stats_{i}",
                data_type=DataType.USER_DATA
            )
            archive_service.create_record(db, record_data)
        
        # Get stats
        stats = archive_service.get_stats(db)
        
        assert stats.total_records >= 2
        assert stats.active_records >= 2
        assert stats.policies_count >= 1
        assert stats.total_storage_bytes >= 0

if __name__ == "__main__":
    pytest.main([__file__])
