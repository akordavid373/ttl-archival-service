from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from ..database import get_db
from ..services.tenant_service import TenantService


router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])
tenant_service = TenantService()


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, regex="^[a-z0-9-]+$")
    owner_email: str = Field(
        ..., regex="^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"
    )
    owner_name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict] = None
    custom_branding: Optional[Dict] = None


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict] = None
    custom_branding: Optional[Dict] = None


class TenantResponse(BaseModel):
    id: int
    tenant_id: str
    name: str
    slug: str
    description: Optional[str]
    status: str
    owner_email: str
    owner_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TenantUserCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    role: str = Field("member", regex="^(owner|admin|member|guest)$")
    email: Optional[str] = None
    name: Optional[str] = None


class TenantUserResponse(BaseModel):
    id: int
    tenant_id: str
    user_id: str
    role: str
    email: Optional[str]
    name: Optional[str]
    is_active: bool
    joined_at: datetime

    class Config:
        from_attributes = True


class TenantResourceUpdate(BaseModel):
    quota_limit: Optional[int] = Field(None, ge=0)
    quota_used: Optional[int] = Field(None, ge=0)


class TenantResourceResponse(BaseModel):
    id: int
    tenant_id: str
    resource_type: str
    resource_name: str
    quota_limit: int
    quota_used: int
    quota_unit: Optional[str]
    quota_percentage: float
    is_exceeded: bool

    class Config:
        from_attributes = True


class TenantConfigSet(BaseModel):
    config_key: str = Field(..., min_length=1)
    config_value: Any
    config_type: Optional[str] = None
    is_secret: bool = False


class TenantConfigResponse(BaseModel):
    id: int
    tenant_id: str
    config_key: str
    config_value: Any
    config_type: Optional[str]
    is_secret: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BillingAccountCreate(BaseModel):
    billing_email: str
    billing_name: Optional[str] = None
    subscription_tier: str = Field("free", regex="^(free|basic|pro|enterprise)$")


class BillingAccountUpdate(BaseModel):
    billing_email: Optional[str] = None
    billing_name: Optional[str] = None
    subscription_tier: Optional[str] = None
    payment_method: Optional[Dict] = None
    billing_address: Optional[Dict] = None


class BillingAccountResponse(BaseModel):
    id: int
    tenant_id: str
    billing_email: Optional[str]
    billing_name: Optional[str]
    subscription_tier: str
    subscription_status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("", response_model=TenantResponse)
async def create_tenant(request: TenantCreate, db: Session = Depends(get_db)):
    """Create a new tenant"""
    try:
        tenant = await tenant_service.create_tenant(
            db=db,
            name=request.name,
            slug=request.slug,
            owner_email=request.owner_email,
            owner_name=request.owner_name,
            description=request.description,
            settings=request.settings,
            custom_branding=request.custom_branding,
        )

        return TenantResponse(
            id=tenant.id,
            tenant_id=tenant.tenant_id,
            name=tenant.name,
            slug=tenant.slug,
            description=tenant.description,
            status=tenant.status,
            owner_email=tenant.owner_email,
            owner_name=tenant.owner_name,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[TenantResponse])
async def get_tenants(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all tenants"""
    try:
        skip = (page - 1) * size
        tenants, total = await tenant_service.get_tenants(
            db=db, status=status, skip=skip, limit=size
        )

        return [
            TenantResponse(
                id=t.id,
                tenant_id=t.tenant_id,
                name=t.name,
                slug=t.slug,
                description=t.description,
                status=t.status,
                owner_email=t.owner_email,
                owner_name=t.owner_name,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in tenants
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """Get a specific tenant"""
    try:
        tenant = await tenant_service.get_tenant(db, tenant_id=tenant_id)

        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        return TenantResponse(
            id=tenant.id,
            tenant_id=tenant.tenant_id,
            name=tenant.name,
            slug=tenant.slug,
            description=tenant.description,
            status=tenant.status,
            owner_email=tenant.owner_email,
            owner_name=tenant.owner_name,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{tenant_id}")
async def update_tenant(
    tenant_id: str, request: TenantUpdate, db: Session = Depends(get_db)
):
    """Update a tenant"""
    try:
        update_data = request.model_dump(exclude_unset=True)
        tenant = await tenant_service.update_tenant(db, tenant_id, **update_data)

        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        return TenantResponse(
            id=tenant.id,
            tenant_id=tenant.tenant_id,
            name=tenant.name,
            slug=tenant.slug,
            description=tenant.description,
            status=tenant.status,
            owner_email=tenant.owner_email,
            owner_name=tenant.owner_name,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{tenant_id}/activate")
async def activate_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """Activate a tenant"""
    try:
        tenant = await tenant_service.activate_tenant(db, tenant_id)

        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        return {"status": "activated", "tenant_id": tenant_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{tenant_id}/suspend")
async def suspend_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """Suspend a tenant"""
    try:
        tenant = await tenant_service.suspend_tenant(db, tenant_id)

        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        return {"status": "suspended", "tenant_id": tenant_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{tenant_id}/users", response_model=TenantUserResponse)
async def add_user_to_tenant(
    tenant_id: str, request: TenantUserCreate, db: Session = Depends(get_db)
):
    """Add a user to a tenant"""
    try:
        has_quota, error = await tenant_service.check_resource_quota(
            db, tenant_id, "users"
        )

        if not has_quota:
            raise HTTPException(status_code=402, detail="User quota exceeded")

        user = await tenant_service.add_user_to_tenant(
            db=db,
            tenant_id=tenant_id,
            user_id=request.user_id,
            role=request.role,
            email=request.email,
            name=request.name,
        )

        return TenantUserResponse(
            id=user.id,
            tenant_id=user.tenant_id,
            user_id=user.user_id,
            role=user.role,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            joined_at=user.joined_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tenant_id}/users")
async def get_tenant_users(
    tenant_id: str, role: Optional[str] = Query(None), db: Session = Depends(get_db)
):
    """Get users belonging to a tenant"""
    try:
        users = await tenant_service.get_tenant_users(db, tenant_id, role)

        return [
            TenantUserResponse(
                id=u.id,
                tenant_id=u.tenant_id,
                user_id=u.user_id,
                role=u.role,
                email=u.email,
                name=u.name,
                is_active=u.is_active,
                joined_at=u.joined_at,
            )
            for u in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{tenant_id}/users/{user_id}")
async def remove_user_from_tenant(
    tenant_id: str, user_id: str, db: Session = Depends(get_db)
):
    """Remove a user from a tenant"""
    try:
        success = await tenant_service.remove_user_from_tenant(db, tenant_id, user_id)

        if not success:
            raise HTTPException(status_code=404, detail="User not found in tenant")

        return {"status": "removed", "tenant_id": tenant_id, "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tenant_id}/resources")
async def get_tenant_resources(tenant_id: str, db: Session = Depends(get_db)):
    """Get resource quotas for a tenant"""
    try:
        resources = await tenant_service.get_tenant_resources(db, tenant_id)

        return [
            TenantResourceResponse(
                id=r.id,
                tenant_id=r.tenant_id,
                resource_type=r.resource_type,
                resource_name=r.resource_name,
                quota_limit=r.quota_limit,
                quota_used=r.quota_used,
                quota_unit=r.quota_unit,
                quota_percentage=r.quota_percentage,
                is_exceeded=r.is_exceeded,
            )
            for r in resources
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{tenant_id}/resources/{resource_type}")
async def update_tenant_resource(
    tenant_id: str,
    resource_type: str,
    request: TenantResourceUpdate,
    db: Session = Depends(get_db),
):
    """Update a tenant resource quota"""
    try:
        update_data = request.model_dump(exclude_unset=True)
        resource = await tenant_service.update_resource(
            db, tenant_id, resource_type, **update_data
        )

        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        return TenantResourceResponse(
            id=resource.id,
            tenant_id=resource.tenant_id,
            resource_type=resource.resource_type,
            resource_name=resource.resource_name,
            quota_limit=resource.quota_limit,
            quota_used=resource.quota_used,
            quota_unit=resource.quota_unit,
            quota_percentage=resource.quota_percentage,
            is_exceeded=resource.is_exceeded,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{tenant_id}/configs", response_model=TenantConfigResponse)
async def set_tenant_config(
    tenant_id: str, request: TenantConfigSet, db: Session = Depends(get_db)
):
    """Set a tenant configuration value"""
    try:
        config = await tenant_service.set_tenant_config(
            db=db,
            tenant_id=tenant_id,
            config_key=request.config_key,
            config_value=request.config_value,
            config_type=request.config_type,
            is_secret=request.is_secret,
        )

        return TenantConfigResponse(
            id=config.id,
            tenant_id=config.tenant_id,
            config_key=config.config_key,
            config_value=config.config_value,
            config_type=config.config_type,
            is_secret=config.is_secret,
            created_at=config.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tenant_id}/configs")
async def get_tenant_configs(
    tenant_id: str, include_secrets: bool = Query(False), db: Session = Depends(get_db)
):
    """Get all configurations for a tenant"""
    try:
        configs = await tenant_service.get_tenant_configs(
            db, tenant_id, include_secrets
        )

        return [
            TenantConfigResponse(
                id=c.id,
                tenant_id=c.tenant_id,
                config_key=c.config_key,
                config_value=c.config_value
                if not c.is_secret or include_secrets
                else "***",
                config_type=c.config_type,
                is_secret=c.is_secret,
                created_at=c.created_at,
            )
            for c in configs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{tenant_id}/billing", response_model=BillingAccountResponse)
async def create_billing_account(
    tenant_id: str, request: BillingAccountCreate, db: Session = Depends(get_db)
):
    """Create a billing account for a tenant"""
    try:
        account = await tenant_service.create_billing_account(
            db=db,
            tenant_id=tenant_id,
            billing_email=request.billing_email,
            billing_name=request.billing_name,
            subscription_tier=request.subscription_tier,
        )

        return BillingAccountResponse(
            id=account.id,
            tenant_id=account.tenant_id,
            billing_email=account.billing_email,
            billing_name=account.billing_name,
            subscription_tier=account.subscription_tier,
            subscription_status=account.subscription_status,
            current_period_start=account.current_period_start,
            current_period_end=account.current_period_end,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tenant_id}/billing", response_model=BillingAccountResponse)
async def get_billing_account(tenant_id: str, db: Session = Depends(get_db)):
    """Get billing account for a tenant"""
    try:
        account = await tenant_service.get_billing_account(db, tenant_id)

        if not account:
            raise HTTPException(status_code=404, detail="Billing account not found")

        return BillingAccountResponse(
            id=account.id,
            tenant_id=account.tenant_id,
            billing_email=account.billing_email,
            billing_name=account.billing_name,
            subscription_tier=account.subscription_tier,
            subscription_status=account.subscription_status,
            current_period_start=account.current_period_start,
            current_period_end=account.current_period_end,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{tenant_id}/billing")
async def update_billing_account(
    tenant_id: str, request: BillingAccountUpdate, db: Session = Depends(get_db)
):
    """Update billing account"""
    try:
        update_data = request.model_dump(exclude_unset=True)
        account = await tenant_service.update_billing_account(
            db, tenant_id, **update_data
        )

        if not account:
            raise HTTPException(status_code=404, detail="Billing account not found")

        return BillingAccountResponse(
            id=account.id,
            tenant_id=account.tenant_id,
            billing_email=account.billing_email,
            billing_name=account.billing_name,
            subscription_tier=account.subscription_tier,
            subscription_status=account.subscription_status,
            current_period_start=account.current_period_start,
            current_period_end=account.current_period_end,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
