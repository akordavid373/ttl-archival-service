from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from collections import defaultdict

from ..models.metric import (
    Metric,
    MetricAggregation,
    Dashboard,
    MetricThreshold,
    MetricType,
    MetricCategory,
)


class MetricsService:
    """Service class for metrics collection and analytics"""

    async def record_metric(
        self,
        db: Session,
        name: str,
        metric_type: str,
        category: str,
        value: float,
        unit: Optional[str] = None,
        description: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[Dict] = None,
        timestamp: Optional[datetime] = None,
    ) -> Metric:
        """Record a new metric"""
        metric = Metric(
            name=name,
            metric_type=metric_type,
            category=category,
            value=value,
            unit=unit,
            description=description,
            user_id=user_id,
            session_id=session_id,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
            tags=tags,
            timestamp=timestamp or datetime.utcnow(),
        )

        db.add(metric)
        db.commit()
        db.refresh(metric)

        return metric

    async def record_metrics_batch(
        self, db: Session, metrics: List[Dict[str, Any]]
    ) -> List[Metric]:
        """Record multiple metrics in batch"""
        metric_objects = []

        for metric_data in metrics:
            metric = Metric(
                name=metric_data.get("name"),
                metric_type=metric_data.get("metric_type"),
                category=metric_data.get("category"),
                value=metric_data.get("value"),
                unit=metric_data.get("unit"),
                description=metric_data.get("description"),
                user_id=metric_data.get("user_id"),
                session_id=metric_data.get("session_id"),
                resource_type=metric_data.get("resource_type"),
                resource_id=metric_data.get("resource_id"),
                metadata=metric_data.get("metadata"),
                tags=metric_data.get("tags"),
                timestamp=metric_data.get("timestamp") or datetime.utcnow(),
            )
            metric_objects.append(metric)

        db.bulk_save_objects(metric_objects)
        db.commit()

        return metric_objects

    async def get_metrics(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        metric_name: Optional[str] = None,
        metric_type: Optional[str] = None,
        category: Optional[str] = None,
        user_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_field: str = "timestamp",
        sort_order: str = "desc",
    ) -> Tuple[List[Metric], int]:
        """Get metrics with filtering and pagination"""
        query = db.query(Metric)
        count_query = db.query(func.count(Metric.id))

        if metric_name:
            query = query.filter(Metric.name == metric_name)
            count_query = count_query.filter(Metric.name == metric_name)

        if metric_type:
            query = query.filter(Metric.metric_type == metric_type)
            count_query = count_query.filter(Metric.metric_type == metric_type)

        if category:
            query = query.filter(Metric.category == category)
            count_query = count_query.filter(Metric.category == category)

        if user_id:
            query = query.filter(Metric.user_id == user_id)
            count_query = count_query.filter(Metric.user_id == user_id)

        if date_from:
            query = query.filter(Metric.timestamp >= date_from)
            count_query = count_query.filter(Metric.timestamp >= date_from)

        if date_to:
            query = query.filter(Metric.timestamp <= date_to)
            count_query = count_query.filter(Metric.timestamp <= date_to)

        total = count_query.scalar()

        sort_column = getattr(Metric, sort_field, Metric.timestamp)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        metrics = query.offset(skip).limit(limit).all()

        return metrics, total

    async def get_metric_statistics(
        self,
        db: Session,
        metric_name: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        interval: str = "hour",
    ) -> Dict[str, Any]:
        """Get aggregated statistics for a metric"""
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=7)
        if not date_to:
            date_to = datetime.utcnow()

        query = db.query(Metric).filter(
            and_(
                Metric.name == metric_name,
                Metric.timestamp >= date_from,
                Metric.timestamp <= date_to,
            )
        )

        total_count = query.count()
        total_sum = (
            db.query(func.sum(Metric.value))
            .filter(
                and_(
                    Metric.name == metric_name,
                    Metric.timestamp >= date_from,
                    Metric.timestamp <= date_to,
                )
            )
            .scalar()
            or 0
        )

        total_avg = (
            db.query(func.avg(Metric.value))
            .filter(
                and_(
                    Metric.name == metric_name,
                    Metric.timestamp >= date_from,
                    Metric.timestamp <= date_to,
                )
            )
            .scalar()
            or 0
        )

        min_value = (
            db.query(func.min(Metric.value))
            .filter(
                and_(
                    Metric.name == metric_name,
                    Metric.timestamp >= date_from,
                    Metric.timestamp <= date_to,
                )
            )
            .scalar()
        )

        max_value = (
            db.query(func.max(Metric.value))
            .filter(
                and_(
                    Metric.name == metric_name,
                    Metric.timestamp >= date_from,
                    Metric.timestamp <= date_to,
                )
            )
            .scalar()
        )

        time_buckets = self._get_time_buckets(date_from, date_to, interval)
        time_series = []

        for bucket_start, bucket_end in time_buckets:
            bucket_data = query.filter(
                and_(Metric.timestamp >= bucket_start, Metric.timestamp < bucket_end)
            ).all()

            if bucket_data:
                avg_val = sum(m.value for m in bucket_data) / len(bucket_data)
                min_val = min(m.value for m in bucket_data)
                max_val = max(m.value for m in bucket_data)
            else:
                avg_val = min_val = max_val = 0

            time_series.append(
                {
                    "timestamp": bucket_start.isoformat(),
                    "avg": avg_val,
                    "min": min_val,
                    "max": max_val,
                    "count": len(bucket_data),
                }
            )

        return {
            "metric_name": metric_name,
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat(),
                "interval": interval,
            },
            "statistics": {
                "count": total_count,
                "sum": total_sum,
                "avg": round(total_avg, 2),
                "min": min_value,
                "max": max_value,
            },
            "time_series": time_series,
        }

    def _get_time_buckets(
        self, start: datetime, end: datetime, interval: str
    ) -> List[Tuple[datetime, datetime]]:
        """Generate time buckets for aggregation"""
        buckets = []
        current = start

        if interval == "minute":
            delta = timedelta(minutes=1)
        elif interval == "hour":
            delta = timedelta(hours=1)
        elif interval == "day":
            delta = timedelta(days=1)
        elif interval == "week":
            delta = timedelta(weeks=1)
        else:
            delta = timedelta(hours=1)

        while current < end:
            bucket_end = min(current + delta, end)
            buckets.append((current, bucket_end))
            current = bucket_end

        return buckets

    async def aggregate_metrics(
        self, db: Session, period_type: str = "hour"
    ) -> List[MetricAggregation]:
        """Aggregate metrics for the specified period"""
        now = datetime.utcnow()

        if period_type == "hour":
            period_start = now.replace(minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(hours=1)
        elif period_type == "day":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        else:
            period_start = now.replace(minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(hours=1)

        metrics = (
            db.query(Metric)
            .filter(
                and_(Metric.timestamp >= period_start, Metric.timestamp < period_end)
            )
            .all()
        )

        aggregated = defaultdict(lambda: {"values": [], "dimensions": {}})

        for metric in metrics:
            key = (metric.name, metric.metric_type)
            aggregated[key]["values"].append(metric.value)

            if metric.metadata:
                aggregated[key]["dimensions"].update(metric.metadata)

        aggregations = []
        for (name, metric_type), data in aggregated.items():
            values = data["values"]

            agg = MetricAggregation(
                metric_name=name,
                metric_type=metric_type,
                period_start=period_start,
                period_end=period_end,
                period_type=period_type,
                count=len(values),
                sum=sum(values),
                avg=sum(values) / len(values) if values else 0,
                min=min(values) if values else None,
                max=max(values) if values else None,
                dimensions=data["dimensions"] if data["dimensions"] else None,
            )
            aggregations.append(agg)
            db.add(agg)

        db.commit()

        return aggregations

    async def create_dashboard(
        self,
        db: Session,
        name: str,
        user_id: str,
        description: Optional[str] = None,
        layout: Optional[Dict] = None,
        widgets: Optional[List[Dict]] = None,
        filters: Optional[Dict] = None,
        refresh_interval: int = 60,
        is_shared: bool = False,
    ) -> Dashboard:
        """Create a new dashboard"""
        dashboard = Dashboard(
            name=name,
            description=description,
            user_id=user_id,
            layout=layout or {"type": "grid"},
            widgets=widgets or [],
            filters=filters or {},
            refresh_interval=refresh_interval,
            is_shared=is_shared,
        )

        db.add(dashboard)
        db.commit()
        db.refresh(dashboard)

        return dashboard

    async def get_dashboards(
        self, db: Session, user_id: Optional[str] = None, include_shared: bool = True
    ) -> List[Dashboard]:
        """Get dashboards for a user"""
        query = db.query(Dashboard)

        if user_id:
            if include_shared:
                query = query.filter(
                    or_(Dashboard.user_id == user_id, Dashboard.is_shared == True)
                )
            else:
                query = query.filter(Dashboard.user_id == user_id)
        elif not include_shared:
            query = query.filter(Dashboard.is_shared == True)

        return query.order_by(desc(Dashboard.created_at)).all()

    async def create_threshold(
        self,
        db: Session,
        metric_name: str,
        threshold_value: float,
        comparison_operator: str,
        severity: str = "warning",
        notification_enabled: bool = True,
        notification_channels: Optional[List[str]] = None,
    ) -> MetricThreshold:
        """Create a metric threshold for alerting"""
        threshold = MetricThreshold(
            metric_name=metric_name,
            threshold_value=threshold_value,
            comparison_operator=comparison_operator,
            severity=severity,
            notification_enabled=notification_enabled,
            notification_channels=notification_channels or ["log"],
        )

        db.add(threshold)
        db.commit()
        db.refresh(threshold)

        return threshold

    async def check_thresholds(
        self, db: Session, metric_name: str, current_value: float
    ) -> List[Dict[str, Any]]:
        """Check if a metric value exceeds any thresholds"""
        thresholds = (
            db.query(MetricThreshold)
            .filter(
                and_(
                    MetricThreshold.metric_name == metric_name,
                    MetricThreshold.is_active == True,
                )
            )
            .all()
        )

        violations = []

        for threshold in thresholds:
            is_violation = False

            if (
                threshold.comparison_operator == "gt"
                and current_value > threshold.threshold_value
            ):
                is_violation = True
            elif (
                threshold.comparison_operator == "gte"
                and current_value >= threshold.threshold_value
            ):
                is_violation = True
            elif (
                threshold.comparison_operator == "lt"
                and current_value < threshold.threshold_value
            ):
                is_violation = True
            elif (
                threshold.comparison_operator == "lte"
                and current_value <= threshold.threshold_value
            ):
                is_violation = True
            elif (
                threshold.comparison_operator == "eq"
                and current_value == threshold.threshold_value
            ):
                is_violation = True

            if is_violation:
                violations.append(
                    {
                        "threshold_id": threshold.id,
                        "metric_name": metric_name,
                        "threshold_value": threshold.threshold_value,
                        "current_value": current_value,
                        "operator": threshold.comparison_operator,
                        "severity": threshold.severity,
                        "notification_enabled": threshold.notification_enabled,
                        "channels": threshold.notification_channels,
                    }
                )

        return violations

    async def get_business_metrics(
        self,
        db: Session,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get business-related metrics summary"""
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()

        business_metrics = (
            db.query(Metric)
            .filter(
                and_(
                    Metric.metric_type == MetricType.BUSINESS.value,
                    Metric.timestamp >= date_from,
                    Metric.timestamp <= date_to,
                )
            )
            .all()
        )

        metrics_by_name = defaultdict(list)
        for m in business_metrics:
            metrics_by_name[m.name].append(m.value)

        summary = {}
        for name, values in metrics_by_name.items():
            summary[name] = {
                "count": len(values),
                "total": sum(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            }

        return {
            "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
            "metrics": summary,
        }

    async def get_performance_metrics(
        self,
        db: Session,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get performance-related metrics summary"""
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=1)
        if not date_to:
            date_to = datetime.utcnow()

        perf_metrics = (
            db.query(Metric)
            .filter(
                and_(
                    Metric.metric_type == MetricType.PERFORMANCE.value,
                    Metric.timestamp >= date_from,
                    Metric.timestamp <= date_to,
                )
            )
            .all()
        )

        metrics_by_name = defaultdict(list)
        for m in perf_metrics:
            metrics_by_name[m.name].append(m.value)

        summary = {}
        for name, values in metrics_by_name.items():
            summary[name] = {
                "count": len(values),
                "avg": sum(values) / len(values),
                "p95": self._percentile(values, 95),
                "p99": self._percentile(values, 99),
                "max": max(values),
            }

        return {
            "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
            "metrics": summary,
        }

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of a list of values"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
