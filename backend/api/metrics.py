from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from ..database import get_db
from ..services.metrics_service import MetricsService
from ..models.metric import MetricType, MetricCategory


router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])
metrics_service = MetricsService()


class MetricRecordRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    metric_type: str = Field(
        ...,
        description="business, technical, user_behavior, performance, system_health",
    )
    category: str = Field(
        ..., description="usage, performance, error, engagement, health"
    )
    value: float
    unit: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    metadata: Optional[Dict] = None
    tags: Optional[Dict] = None


class MetricRecordBatchRequest(BaseModel):
    metrics: List[MetricRecordRequest]


class DashboardCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    layout: Optional[Dict] = None
    widgets: Optional[List[Dict]] = None
    filters: Optional[Dict] = None
    refresh_interval: int = Field(60, ge=10, le=3600)
    is_shared: bool = False


class ThresholdCreateRequest(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=255)
    threshold_value: float
    comparison_operator: str = Field(..., regex="^(gt|gte|lt|lte|eq)$")
    severity: str = Field("warning", regex="^(info|warning|critical)$")
    notification_enabled: bool = True
    notification_channels: Optional[List[str]] = None


class MetricResponse(BaseModel):
    id: int
    name: str
    metric_type: str
    category: str
    value: float
    unit: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class MetricListResponse(BaseModel):
    items: List[MetricResponse]
    total: int
    page: int
    size: int


class DashboardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    user_id: str
    is_shared: bool
    layout: Dict
    widgets: List[Dict]
    filters: Dict
    refresh_interval: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ThresholdResponse(BaseModel):
    id: int
    metric_name: str
    threshold_value: float
    comparison_operator: str
    severity: str
    notification_enabled: bool
    notification_channels: Optional[List[str]]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/record", response_model=MetricResponse)
async def record_metric(request: MetricRecordRequest, db: Session = Depends(get_db)):
    """Record a new metric"""
    try:
        metric = await metrics_service.record_metric(
            db=db,
            name=request.name,
            metric_type=request.metric_type,
            category=request.category,
            value=request.value,
            unit=request.unit,
            description=request.description,
            user_id=request.user_id,
            session_id=request.session_id,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            metadata=request.metadata,
            tags=request.tags,
        )

        return MetricResponse(
            id=metric.id,
            name=metric.name,
            metric_type=metric.metric_type,
            category=metric.category,
            value=metric.value,
            unit=metric.unit,
            description=metric.description,
            user_id=metric.user_id,
            timestamp=metric.timestamp,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record/batch")
async def record_metrics_batch(
    request: MetricRecordBatchRequest, db: Session = Depends(get_db)
):
    """Record multiple metrics in batch"""
    try:
        metrics_data = [m.model_dump() for m in request.metrics]
        metrics = await metrics_service.record_metrics_batch(db, metrics_data)

        return {"recorded": len(metrics), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=MetricListResponse)
async def get_metrics(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    metric_name: Optional[str] = Query(None, description="Filter by metric name"),
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    sort_field: str = Query("timestamp", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
):
    """Get metrics with filtering and pagination"""
    try:
        skip = (page - 1) * size

        metrics, total = await metrics_service.get_metrics(
            db=db,
            skip=skip,
            limit=size,
            metric_name=metric_name,
            metric_type=metric_type,
            category=category,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            sort_field=sort_field,
            sort_order=sort_order,
        )

        return MetricListResponse(
            items=[
                MetricResponse(
                    id=m.id,
                    name=m.name,
                    metric_type=m.metric_type,
                    category=m.category,
                    value=m.value,
                    unit=m.unit,
                    description=m.description,
                    user_id=m.user_id,
                    timestamp=m.timestamp,
                )
                for m in metrics
            ],
            total=total,
            page=page,
            size=size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/{metric_name}")
async def get_metric_statistics(
    metric_name: str,
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    interval: str = Query(
        "hour", regex="^(minute|hour|day|week)$", description="Time interval"
    ),
    db: Session = Depends(get_db),
):
    """Get aggregated statistics for a specific metric"""
    try:
        stats = await metrics_service.get_metric_statistics(
            db=db,
            metric_name=metric_name,
            date_from=date_from,
            date_to=date_to,
            interval=interval,
        )

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/business")
async def get_business_metrics(
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db),
):
    """Get business metrics summary"""
    try:
        metrics = await metrics_service.get_business_metrics(
            db=db, date_from=date_from, date_to=date_to
        )

        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance_metrics(
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db),
):
    """Get performance metrics summary"""
    try:
        metrics = await metrics_service.get_performance_metrics(
            db=db, date_from=date_from, date_to=date_to
        )

        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/aggregate")
async def aggregate_metrics(
    period_type: str = Query("hour", regex="^(minute|hour|day)$"),
    db: Session = Depends(get_db),
):
    """Aggregate metrics for the specified period"""
    try:
        aggregations = await metrics_service.aggregate_metrics(db, period_type)

        return {
            "period_type": period_type,
            "aggregated": len(aggregations),
            "status": "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboards", response_model=DashboardResponse)
async def create_dashboard(
    request: DashboardCreateRequest,
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db),
):
    """Create a new dashboard"""
    try:
        dashboard = await metrics_service.create_dashboard(
            db=db,
            name=request.name,
            user_id=user_id,
            description=request.description,
            layout=request.layout,
            widgets=request.widgets,
            filters=request.filters,
            refresh_interval=request.refresh_interval,
            is_shared=request.is_shared,
        )

        return DashboardResponse(
            id=dashboard.id,
            name=dashboard.name,
            description=dashboard.description,
            user_id=dashboard.user_id,
            is_shared=dashboard.is_shared,
            layout=dashboard.layout,
            widgets=dashboard.widgets,
            filters=dashboard.filters,
            refresh_interval=dashboard.refresh_interval,
            created_at=dashboard.created_at,
            updated_at=dashboard.updated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboards")
async def get_dashboards(
    user_id: Optional[str] = Query(None, description="User ID"),
    include_shared: bool = Query(True, description="Include shared dashboards"),
    db: Session = Depends(get_db),
):
    """Get dashboards"""
    try:
        dashboards = await metrics_service.get_dashboards(
            db=db, user_id=user_id, include_shared=include_shared
        )

        return [
            DashboardResponse(
                id=d.id,
                name=d.name,
                description=d.description,
                user_id=d.user_id,
                is_shared=d.is_shared,
                layout=d.layout,
                widgets=d.widgets,
                filters=d.filters,
                refresh_interval=d.refresh_interval,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in dashboards
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/thresholds", response_model=ThresholdResponse)
async def create_threshold(
    request: ThresholdCreateRequest, db: Session = Depends(get_db)
):
    """Create a metric threshold for alerting"""
    try:
        threshold = await metrics_service.create_threshold(
            db=db,
            metric_name=request.metric_name,
            threshold_value=request.threshold_value,
            comparison_operator=request.comparison_operator,
            severity=request.severity,
            notification_enabled=request.notification_enabled,
            notification_channels=request.notification_channels,
        )

        return ThresholdResponse(
            id=threshold.id,
            metric_name=threshold.metric_name,
            threshold_value=threshold.threshold_value,
            comparison_operator=threshold.comparison_operator,
            severity=threshold.severity,
            notification_enabled=threshold.notification_enabled,
            notification_channels=threshold.notification_channels,
            is_active=threshold.is_active,
            created_at=threshold.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thresholds/{metric_name}/check")
async def check_threshold(
    metric_name: str,
    value: float = Query(..., description="Current metric value"),
    db: Session = Depends(get_db),
):
    """Check if a metric value exceeds thresholds"""
    try:
        violations = await metrics_service.check_thresholds(
            db=db, metric_name=metric_name, current_value=value
        )

        return {
            "metric_name": metric_name,
            "current_value": value,
            "violations": violations,
            "has_violations": len(violations) > 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
