from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import uuid
import hashlib

from ..models.data_classification import (
    DataSubjectRequest,
    DataProcessingRecord,
    ComplianceReport,
    DataClassification,
    LegalHold,
)
from ..models import ArchiveRecord


class ComplianceService:
    """Service class for compliance features"""

    async def create_data_subject_request(
        self,
        db: Session,
        request_type: str,
        subject_id: str,
        subject_email: Optional[str] = None,
        subject_name: Optional[str] = None,
        requested_data_types: Optional[List[str]] = None,
    ) -> DataSubjectRequest:
        """Create a new data subject request"""
        request_id = self._generate_request_id()

        request = DataSubjectRequest(
            request_id=request_id,
            request_type=request_type,
            subject_id=subject_id,
            subject_email=subject_email,
            subject_name=subject_name,
            requested_data_types=requested_data_types or [],
            status="pending",
        )

        db.add(request)
        db.commit()
        db.refresh(request)

        return request

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        return f"DSR-{timestamp}-{unique_id.upper()}"

    async def get_data_subject_requests(
        self,
        db: Session,
        subject_id: Optional[str] = None,
        status: Optional[str] = None,
        request_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[DataSubjectRequest], int]:
        """Get data subject requests with filtering"""
        query = db.query(DataSubjectRequest)
        count_query = db.query(func.count(DataSubjectRequest.id))

        if subject_id:
            query = query.filter(DataSubjectRequest.subject_id == subject_id)
            count_query = count_query.filter(
                DataSubjectRequest.subject_id == subject_id
            )

        if status:
            query = query.filter(DataSubjectRequest.status == status)
            count_query = count_query.filter(DataSubjectRequest.status == status)

        if request_type:
            query = query.filter(DataSubjectRequest.request_type == request_type)
            count_query = count_query.filter(
                DataSubjectRequest.request_type == request_type
            )

        total = count_query.scalar()

        requests = (
            query.order_by(desc(DataSubjectRequest.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return requests, total

    async def get_request_by_id(
        self, db: Session, request_id: str
    ) -> Optional[DataSubjectRequest]:
        """Get a data subject request by ID"""
        return (
            db.query(DataSubjectRequest)
            .filter(DataSubjectRequest.request_id == request_id)
            .first()
        )

    async def verify_request(
        self, db: Session, request_id: str
    ) -> Optional[DataSubjectRequest]:
        """Verify a data subject request"""
        request = await self.get_request_by_id(db, request_id)
        if not request:
            return None

        request.verified = True
        request.verified_at = datetime.utcnow()

        db.commit()
        db.refresh(request)

        return request

    async def process_access_request(
        self, db: Session, request_id: str
    ) -> Dict[str, Any]:
        """Process a data access request"""
        request = await self.get_request_by_id(db, request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")

        if request.status != "pending":
            return {"status": "skipped", "reason": f"Request is {request.status}"}

        if not request.verified:
            request.status = "pending_verification"
            db.commit()
            return {"status": "pending_verification"}

        data_records = (
            db.query(ArchiveRecord)
            .filter(ArchiveRecord.data_type.in_(request.requested_data_types or ["*"]))
            .all()
        )

        data_export = {
            "request_id": request.request_id,
            "subject_id": request.subject_id,
            "generated_at": datetime.utcnow().isoformat(),
            "records": [
                {
                    "id": str(r.id),
                    "data_type": r.data_type,
                    "original_data_id": r.original_data_id,
                    "archived_at": r.archived_at.isoformat() if r.archived_at else None,
                    "metadata": r.metadata,
                }
                for r in data_records
            ],
        }

        request.response_data = data_export
        request.response_date = datetime.utcnow()
        request.status = "completed"
        request.completed_at = datetime.utcnow()

        db.commit()

        return {
            "status": "completed",
            "request_id": request_id,
            "records_exported": len(data_records),
        }

    async def process_deletion_request(
        self, db: Session, request_id: str, anonymize: bool = True
    ) -> Dict[str, Any]:
        """Process a data deletion request"""
        request = await self.get_request_by_id(db, request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")

        if not request.verified:
            request.status = "pending_verification"
            db.commit()
            return {"status": "pending_verification"}

        legal_holds = db.query(LegalHold).filter(LegalHold.status == "active").all()

        on_hold = []
        for hold in legal_holds:
            if request.subject_id in (hold.applies_to_users or []):
                on_hold.append(hold.name)

        if on_hold:
            request.status = "denied"
            request.denial_reason = f"Data on legal hold: {', '.join(on_hold)}"
            request.denial_date = datetime.utcnow()
            db.commit()

            return {
                "status": "denied",
                "reason": "Data subject to legal hold",
                "holds": on_hold,
            }

        deleted_count = 0

        if anonymize:
            records = (
                db.query(ArchiveRecord)
                .filter(
                    ArchiveRecord.data_type.in_(request.requested_data_types or ["*"])
                )
                .all()
            )

            for record in records:
                record.metadata = self._anonymize_data(record.metadata)
                deleted_count += 1
        else:
            result = (
                db.query(ArchiveRecord)
                .filter(
                    ArchiveRecord.data_type.in_(request.requested_data_types or ["*"])
                )
                .delete()
            )
            deleted_count = result

        request.status = "completed"
        request.completed_at = datetime.utcnow()

        db.commit()

        return {
            "status": "completed",
            "request_id": request_id,
            "records_processed": deleted_count,
            "anonymized": anonymize,
        }

    def _anonymize_data(self, data: Optional[str]) -> str:
        """Anonymize data for GDPR deletion"""
        return {
            "anonymized": True,
            "anonymized_at": datetime.utcnow().isoformat(),
            "original_data_hash": hashlib.sha256((data or "").encode()).hexdigest()[
                :16
            ],
        }

    async def process_portability_request(
        self, db: Session, request_id: str, format: str = "json"
    ) -> Dict[str, Any]:
        """Process a data portability request"""
        request = await self.get_request_by_id(db, request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")

        data_records = (
            db.query(ArchiveRecord)
            .filter(ArchiveRecord.data_type.in_(request.requested_data_types or ["*"]))
            .all()
        )

        export_data = {
            "request_id": request.request_id,
            "subject": {
                "id": request.subject_id,
                "email": request.subject_email,
                "name": request.subject_name,
            },
            "export_format": format,
            "generated_at": datetime.utcnow().isoformat(),
            "data": [
                {
                    "type": r.data_type,
                    "created": r.archived_at.isoformat() if r.archived_at else None,
                    "content": r.metadata,
                }
                for r in data_records
            ],
        }

        request.response_data = export_data
        request.response_date = datetime.utcnow()
        request.status = "completed"
        request.completed_at = datetime.utcnow()

        db.commit()

        return {
            "status": "completed",
            "request_id": request_id,
            "format": format,
            "data": export_data,
        }

    async def create_data_processing_record(
        self,
        db: Session,
        data_type: str,
        processing_purpose: str,
        legal_basis: str,
        data_source: Optional[str] = None,
        data_recipients: Optional[List[str]] = None,
        retention_period_days: Optional[int] = None,
        is_cross_border: bool = False,
        countries: Optional[List[str]] = None,
        classification_level: Optional[str] = None,
        safeguards: Optional[Dict] = None,
    ) -> DataProcessingRecord:
        """Create a data processing record"""
        record = DataProcessingRecord(
            data_type=data_type,
            classification_level=classification_level,
            processing_purpose=processing_purpose,
            legal_basis=legal_basis,
            data_source=data_source,
            data_recipients=data_recipients or [],
            retention_period_days=retention_period_days,
            is_cross_border=is_cross_border,
            countries=countries or [],
            safeguards=safeguards or {},
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    async def get_processing_records(
        self, db: Session, data_type: Optional[str] = None
    ) -> List[DataProcessingRecord]:
        """Get data processing records"""
        query = db.query(DataProcessingRecord)

        if data_type:
            query = query.filter(DataProcessingRecord.data_type == data_type)

        return query.order_by(desc(DataProcessingRecord.created_at)).all()

    async def generate_compliance_report(
        self,
        db: Session,
        report_type: str,
        regulation: str,
        period_start: datetime,
        period_end: datetime,
        generated_by: Optional[str] = None,
    ) -> ComplianceReport:
        """Generate a compliance report"""
        report_id = self._generate_report_id()

        report = ComplianceReport(
            report_id=report_id,
            report_type=report_type,
            regulation=regulation,
            period_start=period_start,
            period_end=period_end,
            generated_by=generated_by,
            status="generating",
        )

        db.add(report)
        db.commit()

        summary, findings, recommendations = await self._calculate_report_data(
            db, report_type, regulation, period_start, period_end
        )

        report.summary = summary
        report.findings = findings
        report.recommendations = recommendations
        report.status = "completed"
        report.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(report)

        return report

    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique = str(uuid.uuid4())[:4].upper()
        return f"CR-{timestamp}-{unique}"

    async def _calculate_report_data(
        self,
        db: Session,
        report_type: str,
        regulation: str,
        period_start: datetime,
        period_end: datetime,
    ) -> Tuple[Dict, List[Dict], List[Dict]]:
        """Calculate data for compliance report"""
        summary = {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
            },
            "regulation": regulation,
            "report_type": report_type,
        }

        findings = []
        recommendations = []

        if regulation.upper() == "GDPR":
            dsr_stats = (
                db.query(
                    DataSubjectRequest.request_type,
                    DataSubjectRequest.status,
                    func.count(DataSubjectRequest.id).label("count"),
                )
                .filter(
                    and_(
                        DataSubjectRequest.created_at >= period_start,
                        DataSubjectRequest.created_at <= period_end,
                    )
                )
                .group_by(DataSubjectRequest.request_type, DataSubjectRequest.status)
                .all()
            )

            summary["data_subject_requests"] = {
                "total": sum(s.count for s in dsr_stats),
                "by_type_and_status": [
                    {"type": s.request_type, "status": s.status, "count": s.count}
                    for s in dsr_stats
                ],
            }

            processing_records = db.query(func.count(DataProcessingRecord.id)).scalar()
            summary["processing_records"] = processing_records

            if processing_records == 0:
                findings.append(
                    {
                        "severity": "high",
                        "category": "Records of Processing",
                        "description": "No records of processing found",
                    }
                )
                recommendations.append(
                    {
                        "category": "Records of Processing",
                        "action": "Create and maintain records of all processing activities",
                    }
                )

        elif regulation.upper() == "CCPA":
            data_classifications = (
                db.query(DataClassification)
                .filter(
                    DataClassification.classification_level.in_(
                        ["sensitive", "restricted"]
                    )
                )
                .count()
            )

            summary["sensitive_data_classifications"] = data_classifications

        return summary, findings, recommendations

    async def get_compliance_reports(
        self,
        db: Session,
        regulation: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[ComplianceReport]:
        """Get compliance reports"""
        query = db.query(ComplianceReport)

        if regulation:
            query = query.filter(ComplianceReport.regulation == regulation)

        if status:
            query = query.filter(ComplianceReport.status == status)

        return query.order_by(desc(ComplianceReport.created_at)).all()

    async def check_compliance_status(
        self, db: Session, regulation: str
    ) -> Dict[str, Any]:
        """Check compliance status for a regulation"""
        status = {
            "regulation": regulation,
            "checked_at": datetime.utcnow().isoformat(),
            "checks": [],
        }

        if regulation.upper() == "GDPR":
            pending_requests = (
                db.query(func.count(DataSubjectRequest.id))
                .filter(DataSubjectRequest.status == "pending")
                .scalar()
            )

            status["checks"].append(
                {
                    "check": "Pending Data Subject Requests",
                    "status": "pass" if pending_requests == 0 else "warning",
                    "details": f"{pending_requests} pending requests",
                }
            )

            processing_records = db.query(func.count(DataProcessingRecord.id)).scalar()
            status["checks"].append(
                {
                    "check": "Records of Processing",
                    "status": "pass" if processing_records > 0 else "fail",
                    "details": f"{processing_records} processing records found",
                }
            )

            active_holds = (
                db.query(func.count(LegalHold.id))
                .filter(LegalHold.status == "active")
                .scalar()
            )

            status["checks"].append(
                {
                    "check": "Legal Holds",
                    "status": "pass",
                    "details": f"{active_holds} active legal holds",
                }
            )

        return status
