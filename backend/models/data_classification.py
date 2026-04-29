from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from ..database import Base


class DataClassificationLevel(str, Enum):
    """Data classification levels"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SENSITIVE = "sensitive"


class DataCategory(str, Enum):
    """Data categories"""

    PERSONAL = "personal"
    FINANCIAL = "financial"
    HEALTH = "health"
    EDUCATIONAL = "educational"
    COMMERCIAL = "commercial"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"


class ComplianceRegulation(str, Enum):
    """Compliance regulations"""

    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    FERPA = "ferpa"
    COPPA = "coppa"


class DataClassification(Base):
    """Model for data classification"""

    __tablename__ = "data_classifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)

    classification_level = Column(String(50), nullable=False, index=True)
    data_category = Column(String(50), nullable=False, index=True)

    required_regulations = Column(JSON)
    handling_requirements = Column(JSON)

    retention_days = Column(Integer, default=365)
    encryption_required = Column(Boolean, default=False)
    masking_required = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_class_level_cat", "classification_level", "data_category"),
    )

    def __repr__(self):
        return f"<DataClassification(id={self.id}, name='{self.name}', level='{self.classification_level}')>"


class LegalHold(Base):
    """Model for legal holds"""

    __tablename__ = "legal_holds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)

    hold_type = Column(String(50), nullable=False)
    reason = Column(Text)
    legal_case_id = Column(String(255))

    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))

    applies_to_data_types = Column(JSON)
    applies_to_users = Column(JSON)
    applies_to_resources = Column(JSON)

    status = Column(String(50), default="active", index=True)

    requested_by = Column(String(255))
    approved_by = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    released_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<LegalHold(id={self.id}, name='{self.name}', status='{self.status}')>"


class RetentionPolicy(Base):
    """Model for data retention policies"""

    __tablename__ = "retention_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)

    data_type = Column(String(100), nullable=False, index=True)
    classification_level = Column(String(50))

    retention_days = Column(Integer, nullable=False)
    grace_period_days = Column(Integer, default=0)

    archive_before_delete = Column(Boolean, default=True)
    archive_location = Column(String(500))
    archive_after_days = Column(Integer)

    auto_delete = Column(Boolean, default=True)

    triggers = Column(JSON)

    compliance_regulations = Column(JSON)

    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_policy_type_active", "data_type", "is_active"),
        Index("idx_policy_priority", "priority", "is_active"),
    )

    def __repr__(self):
        return f"<RetentionPolicy(id={self.id}, name='{self.name}', data_type='{self.data_type}')>"


class DataSubjectRequest(Base):
    """Model for data subject requests (GDPR/CCPA)"""

    __tablename__ = "data_subject_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(255), unique=True, nullable=False, index=True)

    request_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default="pending", index=True)

    subject_id = Column(String(255), nullable=False, index=True)
    subject_email = Column(String(255))
    subject_name = Column(String(255))

    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True))

    requested_data_types = Column(JSON)

    response_data = Column(JSON)
    response_date = Column(DateTime(timezone=True))

    denial_reason = Column(Text)
    denial_date = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_request_status_type", "status", "request_type"),
        Index("idx_subject_status", "subject_id", "status"),
    )

    def __repr__(self):
        return f"<DataSubjectRequest(id={self.id}, request_id='{self.request_id}', type='{self.request_type}')>"


class DataProcessingRecord(Base):
    """Model for data processing records"""

    __tablename__ = "data_processing_records"

    id = Column(Integer, primary_key=True, index=True)

    data_type = Column(String(100), nullable=False, index=True)
    classification_level = Column(String(50), index=True)

    processing_purpose = Column(String(255), nullable=False)
    legal_basis = Column(String(100))

    data_source = Column(String(255))
    data_recipients = Column(JSON)

    retention_period_days = Column(Integer)

    is_cross_border = Column(Boolean, default=False)
    countries = Column(JSON)

    safeguards = Column(JSON)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<DataProcessingRecord(id={self.id}, data_type='{self.data_type}', purpose='{self.processing_purpose}')>"


class ComplianceReport(Base):
    """Model for compliance reports"""

    __tablename__ = "compliance_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(255), unique=True, nullable=False, index=True)

    report_type = Column(String(50), nullable=False, index=True)
    regulation = Column(String(50), nullable=False, index=True)

    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    status = Column(String(50), default="generating", index=True)

    summary = Column(JSON)
    findings = Column(JSON)
    recommendations = Column(JSON)

    generated_by = Column(String(255))
    approved_by = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<ComplianceReport(id={self.id}, report_id='{self.report_id}', type='{self.report_type}')>"
