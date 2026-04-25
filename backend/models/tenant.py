from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from .database import Base


class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class Tenant(Base):
    """Model for tenant management"""

    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)

    status = Column(String(50), default=TenantStatus.PENDING.value, index=True)

    owner_email = Column(String(255), nullable=False, index=True)
    owner_name = Column(String(255))

    settings = Column(JSON)
    custom_branding = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    suspended_at = Column(DateTime(timezone=True))

    __table_args__ = (Index("idx_tenant_status", "status"),)

    def __repr__(self):
        return (
            f"<Tenant(id={self.id}, tenant_id='{self.tenant_id}', name='{self.name}')>"
        )


class TenantResource(Base):
    """Model for tenant resource quotas and allocation"""

    __tablename__ = "tenant_resources"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(
        String(255), ForeignKey("tenants.tenant_id"), nullable=False, index=True
    )

    resource_type = Column(String(100), nullable=False)
    resource_name = Column(String(255), nullable=False)

    quota_limit = Column(Integer, nullable=False)
    quota_used = Column(Integer, default=0)
    quota_unit = Column(String(50))

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (Index("idx_resource_tenant_type", "tenant_id", "resource_type"),)

    def __repr__(self):
        return f"<TenantResource(id={self.id}, tenant_id='{self.tenant_id}', type='{self.resource_type}')>"

    @property
    def quota_percentage(self) -> float:
        if self.quota_limit == 0:
            return 100.0
        return (self.quota_used / self.quota_limit) * 100

    @property
    def is_exceeded(self) -> bool:
        return self.quota_used >= self.quota_limit


class TenantConfig(Base):
    """Model for tenant-specific configuration"""

    __tablename__ = "tenant_configs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(
        String(255), ForeignKey("tenants.tenant_id"), nullable=False, index=True
    )

    config_key = Column(String(255), nullable=False)
    config_value = Column(JSON)
    config_type = Column(String(50))

    is_overridable = Column(Boolean, default=True)
    is_secret = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (Index("idx_config_tenant_key", "tenant_id", "config_key"),)

    def __repr__(self):
        return f"<TenantConfig(id={self.id}, tenant_id='{self.tenant_id}', key='{self.config_key}')>"


class TenantUser(Base):
    """Model for tenant users (users belonging to tenants)"""

    __tablename__ = "tenant_users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(
        String(255), ForeignKey("tenants.tenant_id"), nullable=False, index=True
    )
    user_id = Column(String(255), nullable=False, index=True)

    role = Column(String(50), default="member")
    email = Column(String(255))
    name = Column(String(255))

    is_active = Column(Boolean, default=True)

    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_tenant_user_unique", "tenant_id", "user_id", unique=True),
    )

    def __repr__(self):
        return f"<TenantUser(id={self.id}, tenant_id='{self.tenant_id}', user_id='{self.user_id}')>"


class BillingAccount(Base):
    """Model for tenant billing accounts"""

    __tablename__ = "billing_accounts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(
        String(255),
        ForeignKey("tenants.tenant_id"),
        nullable=False,
        unique=True,
        index=True,
    )

    billing_email = Column(String(255))
    billing_name = Column(String(255))

    subscription_tier = Column(String(50), default="free")
    subscription_status = Column(String(50), default="active")

    payment_method = Column(JSON)
    billing_address = Column(JSON)

    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<BillingAccount(id={self.id}, tenant_id='{self.tenant_id}', tier='{self.subscription_tier}')>"
