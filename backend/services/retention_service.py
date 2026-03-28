from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from ..models.data_classification import (
    RetentionPolicy,
    LegalHold,
    DataClassification,
    DataSubjectRequest,
)
from ..models import ArchiveRecord


class RetentionService:
    """Service class for data retention policies and enforcement"""

    async def create_retention_policy(
        self,
        db: Session,
        name: str,
        data_type: str,
        retention_days: int,
        description: Optional[str] = None,
        classification_level: Optional[str] = None,
        grace_period_days: int = 0,
        archive_before_delete: bool = True,
        archive_location: Optional[str] = None,
        archive_after_days: Optional[int] = None,
        auto_delete: bool = True,
        triggers: Optional[Dict] = None,
        compliance_regulations: Optional[List[str]] = None,
        priority: int = 0,
    ) -> RetentionPolicy:
        """Create a new retention policy"""
        policy = RetentionPolicy(
            name=name,
            description=description,
            data_type=data_type,
            classification_level=classification_level,
            retention_days=retention_days,
            grace_period_days=grace_period_days,
            archive_before_delete=archive_before_delete,
            archive_location=archive_location,
            archive_after_days=archive_after_days,
            auto_delete=auto_delete,
            triggers=triggers or {},
            compliance_regulations=compliance_regulations or [],
            priority=priority,
        )

        db.add(policy)
        db.commit()
        db.refresh(policy)

        return policy

    async def get_retention_policies(
        self,
        db: Session,
        data_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        classification_level: Optional[str] = None,
    ) -> List[RetentionPolicy]:
        """Get retention policies with optional filtering"""
        query = db.query(RetentionPolicy)

        if data_type:
            query = query.filter(RetentionPolicy.data_type == data_type)

        if is_active is not None:
            query = query.filter(RetentionPolicy.is_active == is_active)

        if classification_level:
            query = query.filter(
                RetentionPolicy.classification_level == classification_level
            )

        return query.order_by(desc(RetentionPolicy.priority)).all()

    async def get_retention_policy_by_id(
        self, db: Session, policy_id: int
    ) -> Optional[RetentionPolicy]:
        """Get a retention policy by ID"""
        return db.query(RetentionPolicy).filter(RetentionPolicy.id == policy_id).first()

    async def update_retention_policy(
        self, db: Session, policy_id: int, **kwargs
    ) -> Optional[RetentionPolicy]:
        """Update a retention policy"""
        policy = await self.get_retention_policy_by_id(db, policy_id)
        if not policy:
            return None

        for key, value in kwargs.items():
            if hasattr(policy, key):
                setattr(policy, key, value)

        db.commit()
        db.refresh(policy)

        return policy

    async def apply_retention_policy(
        self, db: Session, policy_id: int
    ) -> Dict[str, Any]:
        """Apply a retention policy to enforce data lifecycle"""
        policy = await self.get_retention_policy_by_id(db, policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")

        cutoff_date = datetime.utcnow() - timedelta(
            days=policy.retention_days + policy.grace_period_days
        )

        legal_holds = self._get_active_legal_holds(db)

        query = db.query(ArchiveRecord).filter(
            and_(
                ArchiveRecord.policy_id == policy_id,
                ArchiveRecord.status == "archived",
                ArchiveRecord.archived_at < cutoff_date,
            )
        )

        excluded_ids = []
        for hold in legal_holds:
            if hold.applies_to_resources:
                excluded_ids.extend(hold.applies_to_resources)

        if excluded_ids:
            query = query.filter(~ArchiveRecord.id.in_(excluded_ids))

        records_to_process = query.all()

        archived_count = 0
        deleted_count = 0
        errors = []

        for record in records_to_process:
            try:
                if policy.archive_before_delete and policy.archive_location:
                    record.status = "archived"
                    archived_count += 1
                else:
                    db.delete(record)
                    deleted_count += 1

                record.deleted_at = datetime.utcnow()

            except Exception as e:
                errors.append(f"Error processing record {record.id}: {str(e)}")

        db.commit()

        return {
            "policy_id": policy_id,
            "policy_name": policy.name,
            "processed_records": len(records_to_process),
            "archived": archived_count,
            "deleted": deleted_count,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def apply_all_policies(self, db: Session) -> Dict[str, Any]:
        """Apply all active retention policies"""
        policies = await self.get_retention_policies(db, is_active=True)

        results = []
        total_archived = 0
        total_deleted = 0
        total_errors = 0

        for policy in policies:
            result = await self.apply_retention_policy(db, policy.id)
            results.append(result)
            total_archived += result["archived"]
            total_deleted += result["deleted"]
            total_errors += len(result["errors"])

        return {
            "policies_processed": len(policies),
            "total_archived": total_archived,
            "total_deleted": total_deleted,
            "total_errors": total_errors,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def create_legal_hold(
        self,
        db: Session,
        name: str,
        hold_type: str,
        reason: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        applies_to_data_types: Optional[List[str]] = None,
        applies_to_users: Optional[List[str]] = None,
        applies_to_resources: Optional[List[int]] = None,
        legal_case_id: Optional[str] = None,
        requested_by: Optional[str] = None,
        approved_by: Optional[str] = None,
    ) -> LegalHold:
        """Create a new legal hold"""
        hold = LegalHold(
            name=name,
            hold_type=hold_type,
            reason=reason,
            start_date=start_date,
            end_date=end_date,
            applies_to_data_types=applies_to_data_types or [],
            applies_to_users=applies_to_users or [],
            applies_to_resources=applies_to_resources or [],
            legal_case_id=legal_case_id,
            requested_by=requested_by,
            approved_by=approved_by,
            status="active",
        )

        db.add(hold)
        db.commit()
        db.refresh(hold)

        return hold

    async def get_legal_holds(
        self, db: Session, status: Optional[str] = None
    ) -> List[LegalHold]:
        """Get legal holds"""
        query = db.query(LegalHold)

        if status:
            query = query.filter(LegalHold.status == status)

        return query.order_by(desc(LegalHold.created_at)).all()

    async def release_legal_hold(
        self, db: Session, hold_id: int, released_by: Optional[str] = None
    ) -> Optional[LegalHold]:
        """Release a legal hold"""
        hold = db.query(LegalHold).filter(LegalHold.id == hold_id).first()
        if not hold:
            return None

        hold.status = "released"
        hold.released_at = datetime.utcnow()

        db.commit()
        db.refresh(hold)

        return hold

    def _get_active_legal_holds(self, db: Session) -> List[LegalHold]:
        """Get all active legal holds"""
        now = datetime.utcnow()
        return (
            db.query(LegalHold)
            .filter(
                and_(
                    LegalHold.status == "active",
                    or_(LegalHold.end_date.is_(None), LegalHold.end_date > now),
                    LegalHold.start_date <= now,
                )
            )
            .all()
        )

    async def check_data_expiry(
        self, db: Session, data_id: str, data_type: str
    ) -> Dict[str, Any]:
        """Check if data should be deleted based on retention policies"""
        policy = (
            db.query(RetentionPolicy)
            .filter(
                and_(
                    RetentionPolicy.data_type == data_type,
                    RetentionPolicy.is_active == True,
                )
            )
            .order_by(desc(RetentionPolicy.priority))
            .first()
        )

        if not policy:
            return {
                "data_id": data_id,
                "data_type": data_type,
                "has_policy": False,
                "should_expire": False,
            }

        legal_holds = self._get_active_legal_holds(db)
        is_on_hold = False

        for hold in legal_holds:
            if data_type in (hold.applies_to_data_types or []):
                is_on_hold = True
                break

        retention_date = datetime.utcnow() - timedelta(days=policy.retention_days)

        return {
            "data_id": data_id,
            "data_type": data_type,
            "has_policy": True,
            "policy_id": policy.id,
            "policy_name": policy.name,
            "retention_days": policy.retention_days,
            "on_legal_hold": is_on_hold,
            "should_expire": not is_on_hold,
            "retention_date": retention_date.isoformat(),
        }

    async def get_retention_schedule(
        self, db: Session, days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Get upcoming retention events"""
        policies = await self.get_retention_policies(db, is_active=True)

        schedule = []

        for policy in policies:
            next_run = datetime.utcnow() + timedelta(days=1)

            for _ in range(days_ahead):
                if next_run.weekday() == 0:
                    break
                next_run += timedelta(days=1)

            affected_records = (
                db.query(func.count(ArchiveRecord.id))
                .filter(
                    and_(
                        ArchiveRecord.policy_id == policy.id,
                        ArchiveRecord.status == "archived",
                    )
                )
                .scalar()
            )

            schedule.append(
                {
                    "policy_id": policy.id,
                    "policy_name": policy.name,
                    "data_type": policy.data_type,
                    "retention_days": policy.retention_days,
                    "next_scheduled_run": next_run.isoformat(),
                    "affected_records": affected_records,
                }
            )

        return schedule

    async def create_data_classification(
        self,
        db: Session,
        name: str,
        classification_level: str,
        data_category: str,
        description: Optional[str] = None,
        required_regulations: Optional[List[str]] = None,
        handling_requirements: Optional[Dict] = None,
        retention_days: int = 365,
        encryption_required: bool = False,
        masking_required: bool = False,
    ) -> DataClassification:
        """Create a new data classification"""
        classification = DataClassification(
            name=name,
            description=description,
            classification_level=classification_level,
            data_category=data_category,
            required_regulations=required_regulations or [],
            handling_requirements=handling_requirements or {},
            retention_days=retention_days,
            encryption_required=encryption_required,
            masking_required=masking_required,
        )

        db.add(classification)
        db.commit()
        db.refresh(classification)

        return classification

    async def get_data_classifications(
        self,
        db: Session,
        classification_level: Optional[str] = None,
        data_category: Optional[str] = None,
    ) -> List[DataClassification]:
        """Get data classifications"""
        query = db.query(DataClassification)

        if classification_level:
            query = query.filter(
                DataClassification.classification_level == classification_level
            )

        if data_category:
            query = query.filter(DataClassification.data_category == data_category)

        return query.order_by(DataClassification.classification_level).all()
