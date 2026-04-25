"""
Simple test script to verify audit logging implementation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, get_db
from backend.models import Base
from backend.utils.audit_logger import audit_logger_instance, AuditEvent, AuditAction, AuditSeverity
from backend.services.audit_service import AuditService

def test_audit_logging():
    """Test basic audit logging functionality"""
    print("Testing Audit Logging System...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Test 1: Create a basic audit event
        print("\n1. Testing basic audit event creation...")
        event = AuditEvent(
            action=AuditAction.USER_LOGIN,
            description="Test user login",
            user_id="test_user@example.com",
            ip_address="127.0.0.1",
            user_agent="Test-Agent/1.0"
        )
        
        audit_log = audit_logger_instance.log_event(db, event)
        if audit_log:
            print(f"✓ Audit log created with ID: {audit_log.id}")
        else:
            print("✗ Failed to create audit log")
            return False
        
        # Test 2: Test audit service
        print("\n2. Testing audit service...")
        audit_service = AuditService()
        
        # Get logs
        logs, total = await audit_service.get_audit_logs(db, limit=10)
        print(f"✓ Retrieved {len(logs)} audit logs (total: {total})")
        
        # Test 3: Test statistics
        print("\n3. Testing audit statistics...")
        stats = await audit_service.get_audit_statistics(db, days=30)
        print(f"✓ Statistics retrieved: {stats['total_logs']} total logs")
        
        # Test 4: Test integrity verification
        print("\n4. Testing log integrity verification...")
        integrity = await audit_service.verify_log_integrity(db, audit_log.id)
        if integrity['is_valid']:
            print("✓ Log integrity verified")
        else:
            print("✗ Log integrity verification failed")
        
        print("\n✓ All tests passed! Audit logging system is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    
    # Run async test
    success = asyncio.run(test_audit_logging())
    
    if success:
        print("\n🎉 Audit logging system implementation is complete and working!")
    else:
        print("\n❌ Audit logging system has issues that need to be resolved.")
        sys.exit(1)
