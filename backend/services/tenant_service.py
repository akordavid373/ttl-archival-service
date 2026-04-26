from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import uuid

from ..models.tenant import (
    Tenant,
    TenantStatus,
    TenantResource,
    TenantConfig,
    TenantUser,
    BillingAccount,
)


class TenantService:
    """Service class for multi-tenant operations"""

    async def create_tenant(
        self,
        db: Session,
        name: str,
        slug: str,
        owner_email: str,
        owner_name: Optional[str] = None,
        description: Optional[str] = None,
        settings: Optional[Dict] = None,
        custom_branding: Optional[Dict] = None,
    ) -> Tenant:
        """Create a new tenant"""
        tenant_id = f"tenant_{uuid.uuid4().hex[:12]}"

        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            slug=slug,
            description=description,
            owner_email=owner_email,
            owner_name=owner_name,
            settings=settings or {},
            custom_branding=custom_branding,
            status=TenantStatus.PENDING.value,
        )

        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        await self._create_default_resources(db, tenant_id)
        await self._create_default_configs(db, tenant_id)

        return tenant

    async def _create_default_resources(self, db: Session, tenant_id: str):
        """Create default resource quotas for a tenant"""
        default_resources = [
            {
                "resource_type": "storage",
                "resource_name": "Storage",
                "quota_limit": 1073741824,
                "quota_unit": "bytes",
            },
            {
                "resource_type": "api_calls",
                "resource_name": "API Calls",
                "quota_limit": 10000,
                "quota_unit": "requests",
            },
            {
                "resource_type": "users",
                "resource_name": "Users",
                "quota_limit": 10,
                "quota_unit": "users",
            },
            {
                "resource_type": "policies",
                "resource_name": "Policies",
                "quota_limit": 100,
                "quota_unit": "policies",
            },
        ]

        for resource in default_resources:
            tenant_resource = TenantResource(tenant_id=tenant_id, **resource)
            db.add(tenant_resource)

        db.commit()

    async def _create_default_configs(self, db: Session, tenant_id: str):
        """Create default configuration for a tenant"""
        default_configs = [
            {"config_key": "timezone", "config_value": "UTC", "config_type": "string"},
            {"config_key": "language", "config_value": "en", "config_type": "string"},
            {
                "config_key": "date_format",
                "config_value": "YYYY-MM-DD",
                "config_type": "string",
            },
        ]

        for config in default_configs:
            tenant_config = TenantConfig(tenant_id=tenant_id, **config)
            db.add(tenant_config)

        db.commit()

    async def get_tenant(
        self, db: Session, tenant_id: Optional[str] = None, slug: Optional[str] = None
    ) -> Optional[Tenant]:
        """Get a tenant by ID or slug"""
        query = db.query(Tenant)

        if tenant_id:
            return query.filter(Tenant.tenant_id == tenant_id).first()
        elif slug:
            return query.filter(Tenant.slug == slug).first()

        return None

    async def get_tenants(
        self, db: Session, status: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Tenant], int]:
        """Get tenants with optional filtering"""
        query = db.query(Tenant)
        count_query = db.query(func.count(Tenant.id))

        if status:
            query = query.filter(Tenant.status == status)
            count_query = count_query.filter(Tenant.status == status)

        total = count_query.scalar()
        tenants = (
            query.order_by(desc(Tenant.created_at)).offset(skip).limit(limit).all()
        )

        return tenants, total

    async def update_tenant(
        self, db: Session, tenant_id: str, **kwargs
    ) -> Optional[Tenant]:
        """Update a tenant"""
        tenant = await self.get_tenant(db, tenant_id=tenant_id)
        if not tenant:
            return None

        for key, value in kwargs.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)

        db.commit()
        db.refresh(tenant)

        return tenant

    async def activate_tenant(self, db: Session, tenant_id: str) -> Optional[Tenant]:
        """Activate a tenant"""
        return await self.update_tenant(db, tenant_id, status=TenantStatus.ACTIVE.value)

    async def suspend_tenant(self, db: Session, tenant_id: str) -> Optional[Tenant]:
        """Suspend a tenant"""
        tenant = await self.get_tenant(db, tenant_id=tenant_id)
        if tenant:
            tenant.status = TenantStatus.SUSPENDED.value
            tenant.suspended_at = datetime.utcnow()
            db.commit()
            db.refresh(tenant)
        return tenant

    async def delete_tenant(self, db: Session, tenant_id: str) -> bool:
        """Soft delete a tenant"""
        tenant = await self.get_tenant(db, tenant_id=tenant_id)
        if not tenant:
            return False

        tenant.status = TenantStatus.DELETED.value
        db.commit()

        return True

    async def add_user_to_tenant(
        self,
        db: Session,
        tenant_id: str,
        user_id: str,
        role: str = "member",
        email: Optional[str] = None,
        name: Optional[str] = None,
    ) -> TenantUser:
        """Add a user to a tenant"""
        existing = (
            db.query(TenantUser)
            .filter(
                and_(TenantUser.tenant_id == tenant_id, TenantUser.user_id == user_id)
            )
            .first()
        )

        if existing:
            return existing

        tenant_user = TenantUser(
            tenant_id=tenant_id, user_id=user_id, role=role, email=email, name=name
        )

        await self.increment_resource(db, tenant_id, "users")

        db.add(tenant_user)
        db.commit()
        db.refresh(tenant_user)

        return tenant_user

    async def remove_user_from_tenant(
        self, db: Session, tenant_id: str, user_id: str
    ) -> bool:
        """Remove a user from a tenant"""
        tenant_user = (
            db.query(TenantUser)
            .filter(
                and_(TenantUser.tenant_id == tenant_id, TenantUser.user_id == user_id)
            )
            .first()
        )

        if not tenant_user:
            return False

        db.delete(tenant_user)
        await self.decrement_resource(db, tenant_id, "users")
        db.commit()

        return True

    async def get_tenant_users(
        self, db: Session, tenant_id: str, role: Optional[str] = None
    ) -> List[TenantUser]:
        """Get users belonging to a tenant"""
        query = db.query(TenantUser).filter(TenantUser.tenant_id == tenant_id)

        if role:
            query = query.filter(TenantUser.role == role)

        return query.order_by(TenantUser.joined_at).all()

    async def get_user_tenants(self, db: Session, user_id: str) -> List[Tenant]:
        """Get all tenants a user belongs to"""
        tenant_users = (
            db.query(TenantUser)
            .filter(and_(TenantUser.user_id == user_id, TenantUser.is_active == True))
            .all()
        )

        tenant_ids = [tu.tenant_id for tu in tenant_users]

        if not tenant_ids:
            return []

        return db.query(Tenant).filter(Tenant.tenant_id.in_(tenant_ids)).all()

    async def update_resource(
        self,
        db: Session,
        tenant_id: str,
        resource_type: str,
        quota_limit: Optional[int] = None,
        quota_used: Optional[int] = None,
    ) -> Optional[TenantResource]:
        """Update a tenant resource quota"""
        resource = (
            db.query(TenantResource)
            .filter(
                and_(
                    TenantResource.tenant_id == tenant_id,
                    TenantResource.resource_type == resource_type,
                )
            )
            .first()
        )

        if not resource:
            return None

        if quota_limit is not None:
            resource.quota_limit = quota_limit
        if quota_used is not None:
            resource.quota_used = quota_used

        db.commit()
        db.refresh(resource)

        return resource

    async def increment_resource(
        self, db: Session, tenant_id: str, resource_type: str, amount: int = 1
    ) -> Optional[TenantResource]:
        """Increment a resource usage"""
        resource = (
            db.query(TenantResource)
            .filter(
                and_(
                    TenantResource.tenant_id == tenant_id,
                    TenantResource.resource_type == resource_type,
                )
            )
            .first()
        )

        if resource:
            resource.quota_used += amount
            db.commit()
            db.refresh(resource)

        return resource

    async def decrement_resource(
        self, db: Session, tenant_id: str, resource_type: str, amount: int = 1
    ) -> Optional[TenantResource]:
        """Decrement a resource usage"""
        return await self.increment_resource(db, tenant_id, resource_type, -amount)

    async def check_resource_quota(
        self, db: Session, tenant_id: str, resource_type: str, required: int = 1
    ) -> Tuple[bool, Optional[TenantResource]]:
        """Check if tenant has enough resource quota"""
        resource = (
            db.query(TenantResource)
            .filter(
                and_(
                    TenantResource.tenant_id == tenant_id,
                    TenantResource.resource_type == resource_type,
                )
            )
            .first()
        )

        if not resource:
            return False, None

        available = resource.quota_limit - resource.quota_used
        return available >= required, resource

    async def get_tenant_resources(
        self, db: Session, tenant_id: str
    ) -> List[TenantResource]:
        """Get all resources for a tenant"""
        return (
            db.query(TenantResource).filter(TenantResource.tenant_id == tenant_id).all()
        )

    async def set_tenant_config(
        self,
        db: Session,
        tenant_id: str,
        config_key: str,
        config_value: Any,
        config_type: Optional[str] = None,
        is_secret: bool = False,
    ) -> TenantConfig:
        """Set a tenant configuration value"""
        existing = (
            db.query(TenantConfig)
            .filter(
                and_(
                    TenantConfig.tenant_id == tenant_id,
                    TenantConfig.config_key == config_key,
                )
            )
            .first()
        )

        if existing:
            existing.config_value = config_value
            if config_type:
                existing.config_type = config_type
            db.commit()
            db.refresh(existing)
            return existing

        config = TenantConfig(
            tenant_id=tenant_id,
            config_key=config_key,
            config_value=config_value,
            config_type=config_type,
            is_secret=is_secret,
        )

        db.add(config)
        db.commit()
        db.refresh(config)

        return config

    async def get_tenant_config(
        self, db: Session, tenant_id: str, config_key: str
    ) -> Optional[TenantConfig]:
        """Get a tenant configuration value"""
        return (
            db.query(TenantConfig)
            .filter(
                and_(
                    TenantConfig.tenant_id == tenant_id,
                    TenantConfig.config_key == config_key,
                )
            )
            .first()
        )

    async def get_tenant_configs(
        self, db: Session, tenant_id: str, include_secrets: bool = False
    ) -> List[TenantConfig]:
        """Get all configurations for a tenant"""
        query = db.query(TenantConfig).filter(TenantConfig.tenant_id == tenant_id)

        if not include_secrets:
            query = query.filter(TenantConfig.is_secret == False)

        return query.order_by(TenantConfig.config_key).all()

    async def create_billing_account(
        self,
        db: Session,
        tenant_id: str,
        billing_email: str,
        billing_name: Optional[str] = None,
        subscription_tier: str = "free",
    ) -> BillingAccount:
        """Create a billing account for a tenant"""
        existing = (
            db.query(BillingAccount)
            .filter(BillingAccount.tenant_id == tenant_id)
            .first()
        )

        if existing:
            return existing

        account = BillingAccount(
            tenant_id=tenant_id,
            billing_email=billing_email,
            billing_name=billing_name,
            subscription_tier=subscription_tier,
        )

        db.add(account)
        db.commit()
        db.refresh(account)

        return account

    async def get_billing_account(
        self, db: Session, tenant_id: str
    ) -> Optional[BillingAccount]:
        """Get billing account for a tenant"""
        return (
            db.query(BillingAccount)
            .filter(BillingAccount.tenant_id == tenant_id)
            .first()
        )

    async def update_billing_account(
        self, db: Session, tenant_id: str, **kwargs
    ) -> Optional[BillingAccount]:
        """Update billing account"""
        account = await self.get_billing_account(db, tenant_id)
        if not account:
            return None

        for key, value in kwargs.items():
            if hasattr(account, key):
                setattr(account, key, value)

        db.commit()
        db.refresh(account)

        return account

    async def is_tenant_active(self, db: Session, tenant_id: str) -> bool:
        """Check if a tenant is active"""
        tenant = await self.get_tenant(db, tenant_id=tenant_id)
        return tenant is not None and tenant.status == TenantStatus.ACTIVE.value
