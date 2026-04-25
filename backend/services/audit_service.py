import json
import csv
import io
import hashlib
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, extract
from fastapi import HTTPException

from ..models.audit_log import AuditLog, AuditAction, AuditSeverity, AuditRetentionPolicy
from ..utils.audit_logger import audit_logger_instance, AuditEvent

class AuditService:
    """
    Service class for audit log operations, reporting, and compliance
    """
    
    def __init__(self):
        self.logger = audit_logger_instance
    
    async def create_audit_log(
        self, 
        db: Session, 
        event: AuditEvent
    ) -> Optional[AuditLog]:
        """Create a new audit log entry"""
        return self.logger.log_event(db, event)
    
    async def get_audit_logs(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        action: Optional[AuditAction] = None,
        severity: Optional[AuditSeverity] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: Optional[bool] = None,
        compliance_category: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        search: Optional[str] = None,
        sort_field: str = "timestamp",
        sort_order: str = "desc"
    ) -> Tuple[List[AuditLog], int]:
        """
        Get audit logs with advanced filtering and pagination
        
        Returns:
            Tuple of (audit_logs, total_count)
        """
        query = db.query(AuditLog)
        count_query = db.query(func.count(AuditLog.id))
        
        # Apply filters
        if action:
            query = query.filter(AuditLog.action == action)
            count_query = count_query.filter(AuditLog.action == action)
        
        if severity:
            query = query.filter(AuditLog.severity == severity)
            count_query = count_query.filter(AuditLog.severity == severity)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
            count_query = count_query.filter(AuditLog.user_id == user_id)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
            count_query = count_query.filter(AuditLog.resource_type == resource_type)
        
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
            count_query = count_query.filter(AuditLog.resource_id == resource_id)
        
        if success is not None:
            query = query.filter(AuditLog.success == success)
            count_query = count_query.filter(AuditLog.success == success)
        
        if compliance_category:
            query = query.filter(AuditLog.compliance_category == compliance_category)
            count_query = count_query.filter(AuditLog.compliance_category == compliance_category)
        
        if date_from:
            query = query.filter(AuditLog.timestamp >= date_from)
            count_query = count_query.filter(AuditLog.timestamp >= date_from)
        
        if date_to:
            query = query.filter(AuditLog.timestamp <= date_to)
            count_query = count_query.filter(AuditLog.timestamp <= date_to)
        
        if ip_address:
            query = query.filter(AuditLog.ip_address == ip_address)
            count_query = count_query.filter(AuditLog.ip_address == ip_address)
        
        if session_id:
            query = query.filter(AuditLog.session_id == session_id)
            count_query = count_query.filter(AuditLog.session_id == session_id)
        
        if search:
            search_filter = or_(
                AuditLog.description.ilike(f"%{search}%"),
                AuditLog.resource_name.ilike(f"%{search}%"),
                AuditLog.user_id.ilike(f"%{search}%"),
                AuditLog.details.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
            count_query = count_query.filter(search_filter)
        
        # Get total count
        total = count_query.scalar()
        
        # Apply sorting
        sort_column = getattr(AuditLog, sort_field, AuditLog.timestamp)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        audit_logs = query.offset(skip).limit(limit).all()
        
        return audit_logs, total
    
    async def get_audit_log_by_id(self, db: Session, log_id: int) -> Optional[AuditLog]:
        """Get a specific audit log by ID"""
        return db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    async def get_user_activity(
        self,
        db: Session,
        user_id: str,
        days: int = 30,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get recent activity for a specific user"""
        date_from = datetime.utcnow() - timedelta(days=days)
        
        return db.query(AuditLog)\
            .filter(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.timestamp >= date_from
                )
            )\
            .order_by(desc(AuditLog.timestamp))\
            .limit(limit)\
            .all()
    
    async def get_resource_history(
        self,
        db: Session,
        resource_type: str,
        resource_id: str,
        limit: int = 50
    ) -> List[AuditLog]:
        """Get audit history for a specific resource"""
        return db.query(AuditLog)\
            .filter(
                and_(
                    AuditLog.resource_type == resource_type,
                    AuditLog.resource_id == resource_id
                )
            )\
            .order_by(desc(AuditLog.timestamp))\
            .limit(limit)\
            .all()
    
    async def get_compliance_report(
        self,
        db: Session,
        compliance_category: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate compliance report for audit logs
        
        Args:
            db: Database session
            compliance_category: Specific compliance category to report on
            date_from: Start date for report
            date_to: End date for report
            format: Output format (json, csv)
            
        Returns:
            Compliance report data
        """
        # Default to last 90 days if no dates provided
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=90)
        if not date_to:
            date_to = datetime.utcnow()
        
        # Base query
        query = db.query(AuditLog).filter(
            and_(
                AuditLog.timestamp >= date_from,
                AuditLog.timestamp <= date_to
            )
        )
        
        if compliance_category:
            query = query.filter(AuditLog.compliance_category == compliance_category)
        
        # Get summary statistics
        total_logs = query.count()
        success_count = query.filter(AuditLog.success == True).count()
        failure_count = total_logs - success_count
        
        # Action breakdown
        action_stats = db.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).filter(
            and_(
                AuditLog.timestamp >= date_from,
                AuditLog.timestamp <= date_to
            )
        )
        
        if compliance_category:
            action_stats = action_stats.filter(AuditLog.compliance_category == compliance_category)
        
        action_stats = action_stats.group_by(AuditLog.action).all()
        
        # Severity breakdown
        severity_stats = db.query(
            AuditLog.severity,
            func.count(AuditLog.id).label('count')
        ).filter(
            and_(
                AuditLog.timestamp >= date_from,
                AuditLog.timestamp <= date_to
            )
        )
        
        if compliance_category:
            severity_stats = severity_stats.filter(AuditLog.compliance_category == compliance_category)
        
        severity_stats = severity_stats.group_by(AuditLog.severity).all()
        
        # User activity breakdown
        user_stats = db.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label('count')
        ).filter(
            and_(
                AuditLog.timestamp >= date_from,
                AuditLog.timestamp <= date_to,
                AuditLog.user_id.isnot(None)
            )
        )
        
        if compliance_category:
            user_stats = user_stats.filter(AuditLog.compliance_category == compliance_category)
        
        user_stats = user_stats.group_by(AuditLog.user_id)\
            .order_by(desc(func.count(AuditLog.id)))\
            .limit(10).all()
        
        # Daily activity trend
        daily_stats = db.query(
            func.date(AuditLog.timestamp).label('date'),
            func.count(AuditLog.id).label('count')
        ).filter(
            and_(
                AuditLog.timestamp >= date_from,
                AuditLog.timestamp <= date_to
            )
        )
        
        if compliance_category:
            daily_stats = daily_stats.filter(AuditLog.compliance_category == compliance_category)
        
        daily_stats = daily_stats.group_by(func.date(AuditLog.timestamp))\
            .order_by(func.date(AuditLog.timestamp)).all()
        
        # Compile report
        report = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "date_from": date_from.isoformat(),
                "date_to": date_to.isoformat(),
                "compliance_category": compliance_category,
                "format": format
            },
            "summary": {
                "total_logs": total_logs,
                "successful_operations": success_count,
                "failed_operations": failure_count,
                "success_rate": round((success_count / total_logs * 100) if total_logs > 0 else 0, 2)
            },
            "action_breakdown": [
                {"action": action.value, "count": count} 
                for action, count in action_stats
            ],
            "severity_breakdown": [
                {"severity": severity.value, "count": count} 
                for severity, count in severity_stats
            ],
            "top_users": [
                {"user_id": user_id, "action_count": count} 
                for user_id, count in user_stats
            ],
            "daily_activity": [
                {"date": date.isoformat(), "count": count} 
                for date, count in daily_stats
            ]
        }
        
        if format == "csv":
            return self._convert_to_csv(report)
        
        return report
    
    async def apply_retention_policies(self, db: Session) -> Dict[str, Any]:
        """
        Apply retention policies to clean up old audit logs
        
        Returns:
            Dictionary with cleanup results
        """
        # Get all active retention policies
        policies = db.query(AuditRetentionPolicy)\
            .filter(AuditRetentionPolicy.is_active == True)\
            .order_by(desc(AuditRetentionPolicy.priority))\
            .all()
        
        deleted_count = 0
        archived_count = 0
        errors = []
        
        for policy in policies:
            try:
                # Calculate cutoff date
                cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_days)
                
                # Build query based on policy criteria
                query = db.query(AuditLog).filter(
                    and_(
                        AuditLog.timestamp < cutoff_date,
                        AuditLog.legal_hold == False  # Never delete logs on legal hold
                    )
                )
                
                # Apply policy filters
                if policy.action_types:
                    action_types = json.loads(policy.action_types)
                    query = query.filter(AuditLog.action.in_(action_types))
                
                if policy.severity_levels:
                    severity_levels = json.loads(policy.severity_levels)
                    query = query.filter(AuditLog.severity.in_(severity_levels))
                
                if policy.compliance_categories:
                    compliance_categories = json.loads(policy.compliance_categories)
                    query = query.filter(AuditLog.compliance_category.in_(compliance_categories))
                
                # Get logs to process
                logs_to_process = query.all()
                
                if policy.auto_archive and policy.archive_location:
                    # Archive logs instead of deleting
                    archived_count += len(logs_to_process)
                    # Implementation would move logs to archive storage
                    # For now, we'll just mark them as archived
                    for log in logs_to_process:
                        log.details = json.dumps({
                            "archived": True,
                            "archive_date": datetime.utcnow().isoformat(),
                            "archive_location": policy.archive_location,
                            "original_details": log.details
                        })
                else:
                    # Delete logs
                    for log in logs_to_process:
                        db.delete(log)
                    deleted_count += len(logs_to_process)
                
                db.commit()
                
            except Exception as e:
                errors.append(f"Error applying policy {policy.name}: {str(e)}")
                db.rollback()
        
        return {
            "processed_policies": len(policies),
            "deleted_logs": deleted_count,
            "archived_logs": archived_count,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def create_retention_policy(
        self,
        db: Session,
        name: str,
        description: str,
        retention_days: int,
        action_types: Optional[List[str]] = None,
        severity_levels: Optional[List[str]] = None,
        compliance_categories: Optional[List[str]] = None,
        auto_archive: bool = False,
        archive_location: Optional[str] = None,
        legal_hold_enabled: bool = False,
        priority: int = 0
    ) -> AuditRetentionPolicy:
        """Create a new audit retention policy"""
        policy = AuditRetentionPolicy(
            name=name,
            description=description,
            retention_days=retention_days,
            action_types=json.dumps(action_types) if action_types else None,
            severity_levels=json.dumps(severity_levels) if severity_levels else None,
            compliance_categories=json.dumps(compliance_categories) if compliance_categories else None,
            auto_archive=auto_archive,
            archive_location=archive_location,
            legal_hold_enabled=legal_hold_enabled,
            priority=priority
        )
        
        db.add(policy)
        db.commit()
        db.refresh(policy)
        
        return policy
    
    async def get_retention_policies(self, db: Session) -> List[AuditRetentionPolicy]:
        """Get all retention policies"""
        return db.query(AuditRetentionPolicy)\
            .order_by(desc(AuditRetentionPolicy.priority))\
            .all()
    
    async def get_audit_statistics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Get audit log statistics for the specified period"""
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Basic counts
        total_logs = db.query(func.count(AuditLog.id))\
            .filter(AuditLog.timestamp >= date_from).scalar()
        
        # Success/failure rates
        success_count = db.query(func.count(AuditLog.id))\
            .filter(
                and_(
                    AuditLog.timestamp >= date_from,
                    AuditLog.success == True
                )
            ).scalar()
        
        # Top actions
        top_actions = db.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).filter(AuditLog.timestamp >= date_from)\
            .group_by(AuditLog.action)\
            .order_by(desc(func.count(AuditLog.id)))\
            .limit(10).all()
        
        # Top users
        top_users = db.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label('count')
        ).filter(
            and_(
                AuditLog.timestamp >= date_from,
                AuditLog.user_id.isnot(None)
            )
        ).group_by(AuditLog.user_id)\
            .order_by(desc(func.count(AuditLog.id)))\
            .limit(10).all()
        
        # Security events
        security_events = db.query(func.count(AuditLog.id))\
            .filter(
                and_(
                    AuditLog.timestamp >= date_from,
                    AuditLog.action == AuditAction.SECURITY_EVENT
                )
            ).scalar()
        
        return {
            "period_days": days,
            "total_logs": total_logs,
            "successful_operations": success_count,
            "failed_operations": total_logs - success_count,
            "success_rate": round((success_count / total_logs * 100) if total_logs > 0 else 0, 2),
            "top_actions": [
                {"action": action.value, "count": count} 
                for action, count in top_actions
            ],
            "top_users": [
                {"user_id": user_id, "action_count": count} 
                for user_id, count in top_users
            ],
            "security_events": security_events
        }
    
    def _convert_to_csv(self, report_data: Dict[str, Any]) -> str:
        """Convert report data to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Report Section", "Key", "Value"])
        
        # Write summary
        for key, value in report_data["summary"].items():
            writer.writerow(["Summary", key, value])
        
        # Write action breakdown
        for item in report_data["action_breakdown"]:
            writer.writerow(["Actions", item["action"], item["count"]])
        
        # Write severity breakdown
        for item in report_data["severity_breakdown"]:
            writer.writerow(["Severity", item["severity"], item["count"]])
        
        # Write top users
        for item in report_data["top_users"]:
            writer.writerow(["Users", item["user_id"], item["action_count"]])
        
        return output.getvalue()
    
    async def verify_log_integrity(self, db: Session, log_id: int) -> Dict[str, Any]:
        """Verify the integrity of an audit log using its hash"""
        log = await self.get_audit_log_by_id(db, log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Audit log not found")
        
        # Recalculate hash
        hash_data = {
            'action': log.action.value,
            'description': log.description,
            'user_id': log.user_id,
            'timestamp': log.timestamp.isoformat(),
            'resource_type': log.resource_type,
            'resource_id': log.resource_id,
            'success': log.success
        }
        
        calculated_hash = hashlib.sha256(
            json.dumps(hash_data, sort_keys=True).encode()
        ).hexdigest()
        
        is_valid = calculated_hash == log.event_hash
        
        return {
            "log_id": log_id,
            "is_valid": is_valid,
            "stored_hash": log.event_hash,
            "calculated_hash": calculated_hash,
            "timestamp": datetime.utcnow().isoformat()
        }
