from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from ..database import get_db
from ..services.retention_service import RetentionService
from ..services.compliance_service import ComplianceService


router = APIRouter(prefix="/api/v1/compliance", tags=["compliance"])
retention_service = RetentionService()
compliance_service = ComplianceService()


class RetentionPolicyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    data_type: str = Field(..., min_length=1, max_length=100)
    classification_level: Optional[str] = None
    retention_days: int = Field(..., gt=0)
    grace_period_days: int = Field(0, ge=0)
    archive_before_delete: bool = True
    archive_location: Optional[str] = None
    archive_after_days: Optional[int] = None
    auto_delete: bool = True
    triggers: Optional[Dict] = None
    compliance_regulations: Optional[List[str]] = None
    priority: int = 0


class RetentionPolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    retention_days: Optional[int] = None
    grace_period_days: Optional[int] = None
    archive_before_delete: Optional[bool] = None
    archive_location: Optional[str] = None
    auto_delete: Optional[bool] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class LegalHoldCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    hold_type: str = Field(..., min_length=1, max_length=50)
    reason: str
    start_date: datetime
    end_date: Optional[datetime] = None
    applies_to_data_types: Optional[List[str]] = None
    applies_to_users: Optional[List[str]] = None
    applies_to_resources: Optional[List[int]] = None
    legal_case_id: Optional[str] = None
    requested_by: Optional[str] = None
    approved_by: Optional[str] = None


class DataSubjectRequestCreate(BaseModel):
    request_type: str = Field(..., regex="^(access|deletion|portability|correction)$")
    subject_id: str = Field(..., min_length=1)
    subject_email: Optional[str] = None
    subject_name: Optional[str] = None
    requested_data_types: Optional[List[str]] = None


class DataClassificationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    classification_level: str
    data_category: str
    description: Optional[str] = None
    required_regulations: Optional[List[str]] = None
    handling_requirements: Optional[Dict] = None
    retention_days: int = Field(365, gt=0)
    encryption_required: bool = False
    masking_required: bool = False


class DataProcessingRecordCreate(BaseModel):
    data_type: str = Field(..., min_length=1, max_length=100)
    classification_level: Optional[str] = None
    processing_purpose: str = Field(..., min_length=1)
    legal_basis: str
    data_source: Optional[str] = None
    data_recipients: Optional[List[str]] = None
    retention_period_days: Optional[int] = None
    is_cross_border: bool = False
    countries: Optional[List[str]] = None
    safeguards: Optional[Dict] = None


class RetentionPolicyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    data_type: str
    classification_level: Optional[str]
    retention_days: int
    grace_period_days: int
    archive_before_delete: bool
    archive_location: Optional[str]
    auto_delete: bool
    is_active: bool
    priority: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class LegalHoldResponse(BaseModel):
    id: int
    name: str
    hold_type: str
    reason: str
    legal_case_id: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    status: str
    applies_to_data_types: List[str]
    applies_to_users: List[str]
    applies_to_resources: List[int]
    created_at: datetime

    class Config:
        from_attributes = True


class DataSubjectRequestResponse(BaseModel):
    id: int
    request_id: str
    request_type: str
    status: str
    subject_id: str
    subject_email: Optional[str]
    subject_name: Optional[str]
    verified: bool
    verified_at: Optional[datetime]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class DataClassificationResponse(BaseModel):
    id: int
    name: str
    classification_level: str
    data_category: str
    description: Optional[str]
    retention_days: int
    encryption_required: bool
    masking_required: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/retention-policies", response_model=RetentionPolicyResponse)
async def create_retention_policy(
    request: RetentionPolicyCreate, db: Session = Depends(get_db)
):
    """Create a new retention policy"""
    try:
        policy = await retention_service.create_retention_policy(
            db=db,
            name=request.name,
            data_type=request.data_type,
            retention_days=request.retention_days,
            description=request.description,
            classification_level=request.classification_level,
            grace_period_days=request.grace_period_days,
            archive_before_delete=request.archive_before_delete,
            archive_location=request.archive_location,
            archive_after_days=request.archive_after_days,
            auto_delete=request.auto_delete,
            triggers=request.triggers,
            compliance_regulations=request.compliance_regulations,
            priority=request.priority,
        )

        return RetentionPolicyResponse(
            id=policy.id,
            name=policy.name,
            description=policy.description,
            data_type=policy.data_type,
            classification_level=policy.classification_level,
            retention_days=policy.retention_days,
            grace_period_days=policy.grace_period_days,
            archive_before_delete=policy.archive_before_delete,
            archive_location=policy.archive_location,
            auto_delete=policy.auto_delete,
            is_active=policy.is_active,
            priority=policy.priority,
            created_at=policy.created_at,
            updated_at=policy.updated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/retention-policies")
async def get_retention_policies(
    data_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    classification_level: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get retention policies"""
    try:
        policies = await retention_service.get_retention_policies(
            db=db,
            data_type=data_type,
            is_active=is_active,
            classification_level=classification_level,
        )

        return [
            RetentionPolicyResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                data_type=p.data_type,
                classification_level=p.classification_level,
                retention_days=p.retention_days,
                grace_period_days=p.grace_period_days,
                archive_before_delete=p.archive_before_delete,
                archive_location=p.archive_location,
                auto_delete=p.auto_delete,
                is_active=p.is_active,
                priority=p.priority,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in policies
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/retention-policies/{policy_id}")
async def update_retention_policy(
    policy_id: int, request: RetentionPolicyUpdate, db: Session = Depends(get_db)
):
    """Update a retention policy"""
    try:
        update_data = request.model_dump(exclude_unset=True)
        policy = await retention_service.update_retention_policy(
            db=db, policy_id=policy_id, **update_data
        )

        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")

        return RetentionPolicyResponse(
            id=policy.id,
            name=policy.name,
            description=policy.description,
            data_type=policy.data_type,
            classification_level=policy.classification_level,
            retention_days=policy.retention_days,
            grace_period_days=policy.grace_period_days,
            archive_before_delete=policy.archive_before_delete,
            archive_location=policy.archive_location,
            auto_delete=policy.auto_delete,
            is_active=policy.is_active,
            priority=policy.priority,
            created_at=policy.created_at,
            updated_at=policy.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retention-policies/{policy_id}/apply")
async def apply_retention_policy(policy_id: int, db: Session = Depends(get_db)):
    """Apply a retention policy to enforce data lifecycle"""
    try:
        result = await retention_service.apply_retention_policy(db, policy_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retention-policies/apply-all")
async def apply_all_retention_policies(db: Session = Depends(get_db)):
    """Apply all active retention policies"""
    try:
        result = await retention_service.apply_all_policies(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/retention-schedule")
async def get_retention_schedule(
    days_ahead: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)
):
    """Get upcoming retention events"""
    try:
        schedule = await retention_service.get_retention_schedule(db, days_ahead)
        return {"schedule": schedule}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/legal-holds", response_model=LegalHoldResponse)
async def create_legal_hold(request: LegalHoldCreate, db: Session = Depends(get_db)):
    """Create a new legal hold"""
    try:
        hold = await retention_service.create_legal_hold(
            db=db,
            name=request.name,
            hold_type=request.hold_type,
            reason=request.reason,
            start_date=request.start_date,
            end_date=request.end_date,
            applies_to_data_types=request.applies_to_data_types,
            applies_to_users=request.applies_to_users,
            applies_to_resources=request.applies_to_resources,
            legal_case_id=request.legal_case_id,
            requested_by=request.requested_by,
            approved_by=request.approved_by,
        )

        return LegalHoldResponse(
            id=hold.id,
            name=hold.name,
            hold_type=hold.hold_type,
            reason=hold.reason,
            legal_case_id=hold.legal_case_id,
            start_date=hold.start_date,
            end_date=hold.end_date,
            status=hold.status,
            applies_to_data_types=hold.applies_to_data_types or [],
            applies_to_users=hold.applies_to_users or [],
            applies_to_resources=hold.applies_to_resources or [],
            created_at=hold.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/legal-holds")
async def get_legal_holds(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Get legal holds"""
    try:
        holds = await retention_service.get_legal_holds(db, status)

        return [
            LegalHoldResponse(
                id=h.id,
                name=h.name,
                hold_type=h.hold_type,
                reason=h.reason,
                legal_case_id=h.legal_case_id,
                start_date=h.start_date,
                end_date=h.end_date,
                status=h.status,
                applies_to_data_types=h.applies_to_data_types or [],
                applies_to_users=h.applies_to_users or [],
                applies_to_resources=h.applies_to_resources or [],
                created_at=h.created_at,
            )
            for h in holds
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/legal-holds/{hold_id}/release")
async def release_legal_hold(
    hold_id: int, released_by: Optional[str] = None, db: Session = Depends(get_db)
):
    """Release a legal hold"""
    try:
        hold = await retention_service.release_legal_hold(db, hold_id, released_by)

        if not hold:
            raise HTTPException(status_code=404, detail="Legal hold not found")

        return {
            "status": "released",
            "hold_id": hold_id,
            "released_at": hold.released_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-subject-requests", response_model=DataSubjectRequestResponse)
async def create_data_subject_request(
    request: DataSubjectRequestCreate, db: Session = Depends(get_db)
):
    """Create a new data subject request (GDPR/CCPA)"""
    try:
        dsr = await compliance_service.create_data_subject_request(
            db=db,
            request_type=request.request_type,
            subject_id=request.subject_id,
            subject_email=request.subject_email,
            subject_name=request.subject_name,
            requested_data_types=request.requested_data_types,
        )

        return DataSubjectRequestResponse(
            id=dsr.id,
            request_id=dsr.request_id,
            request_type=dsr.request_type,
            status=dsr.status,
            subject_id=dsr.subject_id,
            subject_email=dsr.subject_email,
            subject_name=dsr.subject_name,
            verified=dsr.verified,
            verified_at=dsr.verified_at,
            created_at=dsr.created_at,
            completed_at=dsr.completed_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-subject-requests")
async def get_data_subject_requests(
    subject_id: Optional[str] = None,
    status: Optional[str] = None,
    request_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get data subject requests"""
    try:
        skip = (page - 1) * size

        requests, total = await compliance_service.get_data_subject_requests(
            db=db,
            subject_id=subject_id,
            status=status,
            request_type=request_type,
            skip=skip,
            limit=size,
        )

        return {
            "items": [
                DataSubjectRequestResponse(
                    id=r.id,
                    request_id=r.request_id,
                    request_type=r.request_type,
                    status=r.status,
                    subject_id=r.subject_id,
                    subject_email=r.subject_email,
                    subject_name=r.subject_name,
                    verified=r.verified,
                    verified_at=r.verified_at,
                    created_at=r.created_at,
                    completed_at=r.completed_at,
                )
                for r in requests
            ],
            "total": total,
            "page": page,
            "size": size,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-subject-requests/{request_id}/verify")
async def verify_data_subject_request(request_id: str, db: Session = Depends(get_db)):
    """Verify a data subject request"""
    try:
        request = await compliance_service.verify_request(db, request_id)

        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        return {
            "status": "verified",
            "request_id": request_id,
            "verified_at": request.verified_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-subject-requests/{request_id}/process")
async def process_data_subject_request(
    request_id: str,
    anonymize: bool = Query(True, description="Anonymize data instead of hard delete"),
    db: Session = Depends(get_db),
):
    """Process a data subject request"""
    try:
        request = await compliance_service.get_request_by_id(db, request_id)

        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        if request.request_type == "access":
            result = await compliance_service.process_access_request(db, request_id)
        elif request.request_type == "deletion":
            result = await compliance_service.process_deletion_request(
                db, request_id, anonymize
            )
        elif request.request_type == "portability":
            result = await compliance_service.process_portability_request(
                db, request_id
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid request type")

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-classifications", response_model=DataClassificationResponse)
async def create_data_classification(
    request: DataClassificationCreate, db: Session = Depends(get_db)
):
    """Create a new data classification"""
    try:
        classification = await retention_service.create_data_classification(
            db=db,
            name=request.name,
            classification_level=request.classification_level,
            data_category=request.data_category,
            description=request.description,
            required_regulations=request.required_regulations,
            handling_requirements=request.handling_requirements,
            retention_days=request.retention_days,
            encryption_required=request.encryption_required,
            masking_required=request.masking_required,
        )

        return DataClassificationResponse(
            id=classification.id,
            name=classification.name,
            classification_level=classification.classification_level,
            data_category=classification.data_category,
            description=classification.description,
            retention_days=classification.retention_days,
            encryption_required=classification.encryption_required,
            masking_required=classification.masking_required,
            created_at=classification.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-classifications")
async def get_data_classifications(
    classification_level: Optional[str] = None,
    data_category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get data classifications"""
    try:
        classifications = await retention_service.get_data_classifications(
            db=db,
            classification_level=classification_level,
            data_category=data_category,
        )

        return [
            DataClassificationResponse(
                id=c.id,
                name=c.name,
                classification_level=c.classification_level,
                data_category=c.data_category,
                description=c.description,
                retention_days=c.retention_days,
                encryption_required=c.encryption_required,
                masking_required=c.masking_required,
                created_at=c.created_at,
            )
            for c in classifications
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance-status/{regulation}")
async def check_compliance_status(regulation: str, db: Session = Depends(get_db)):
    """Check compliance status for a regulation"""
    try:
        status = await compliance_service.check_compliance_status(db, regulation)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
