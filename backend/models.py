from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from .database import Base

class ArchivePolicy(Base):
    __tablename__ = "archive_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    ttl_days = Column(Integer, nullable=False)  # Time to live in days
    storage_location = Column(String(500))  # Where to store archived data
    compression_enabled = Column(Boolean, default=True)
    encryption_enabled = Column(Boolean, default=False)
    auto_cleanup = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    archive_records = relationship("ArchiveRecord", back_populates="policy")
    
    def __repr__(self):
        return f"<ArchivePolicy(id={self.id}, name='{self.name}', ttl_days={self.ttl_days})>"

class ArchiveRecord(Base):
    __tablename__ = "archive_records"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("archive_policies.id"), nullable=False, index=True)
    original_data_id = Column(String(255), nullable=False, index=True)  # ID of original data
    data_type = Column(String(100), nullable=False)  # Type of data (e.g., "user_data", "logs")
    file_path = Column(String(500))  # Path to archived file
    file_size_bytes = Column(Integer)
    checksum = Column(String(64))  # SHA-256 checksum for integrity verification
    metadata = Column(Text)  # JSON metadata about the archived data
    status = Column(String(50), default="archived", index=True)  # archived, expired, deleted
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    archived_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    deleted_at = Column(DateTime(timezone=True))
    
    # Relationships
    policy = relationship("ArchivePolicy", back_populates="archive_records")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_policy_expires', 'policy_id', 'expires_at'),
        Index('idx_status_expires', 'status', 'expires_at'),
        Index('idx_original_data', 'original_data_id', 'data_type'),
    )
    
    def __repr__(self):
        return f"<ArchiveRecord(id={self.id}, policy_id={self.policy_id}, expires_at={self.expires_at})>"
    
    @property
    def is_expired(self):
        """Check if the record has expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def days_until_expiry(self):
        """Calculate days until expiry"""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)
