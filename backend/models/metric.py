from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    Float,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from .database import Base


class MetricType(str, Enum):
    """Types of metrics"""

    BUSINESS = "business"
    TECHNICAL = "technical"
    USER_BEHAVIOR = "user_behavior"
    PERFORMANCE = "performance"
    SYSTEM_HEALTH = "system_health"


class MetricCategory(str, Enum):
    """Metric categories"""

    USAGE = "usage"
    PERFORMANCE = "performance"
    ERROR = "error"
    ENGAGEMENT = "engagement"
    HEALTH = "health"


class Metric(Base):
    """Model for storing application metrics"""

    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    description = Column(Text)

    user_id = Column(String(255), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(255), nullable=True)

    metadata = Column(JSON)
    tags = Column(JSON)

    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_metric_name_time", "name", "timestamp"),
        Index("idx_metric_type_time", "metric_type", "timestamp"),
        Index("idx_user_metric_time", "user_id", "timestamp"),
        Index("idx_category_time", "category", "timestamp"),
    )

    def __repr__(self):
        return f"<Metric(id={self.id}, name='{self.name}', value={self.value}, timestamp={self.timestamp})>"


class MetricAggregation(Base):
    """Model for aggregated metrics"""

    __tablename__ = "metric_aggregations"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False, index=True)

    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String(20), default="hour")

    count = Column(Integer, default=0)
    sum = Column(Float, default=0.0)
    avg = Column(Float, default=0.0)
    min = Column(Float, nullable=True)
    max = Column(Float, nullable=True)

    dimensions = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_agg_metric_period", "metric_name", "period_start", "period_end"),
        Index("idx_agg_period_type", "period_type", "period_start"),
    )

    def __repr__(self):
        return f"<MetricAggregation(id={self.id}, metric_name='{self.metric_name}', period='{self.period_type}', avg={self.avg})>"


class Dashboard(Base):
    """Model for custom dashboards"""

    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)

    user_id = Column(String(255), nullable=True, index=True)
    is_shared = Column(Boolean, default=False)

    layout = Column(JSON)
    widgets = Column(JSON)

    filters = Column(JSON)

    refresh_interval = Column(Integer, default=60)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return (
            f"<Dashboard(id={self.id}, name='{self.name}', user_id='{self.user_id}')>"
        )


class MetricThreshold(Base):
    """Model for metric thresholds and alerts"""

    __tablename__ = "metric_thresholds"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(255), nullable=False, index=True)

    threshold_value = Column(Float, nullable=False)
    comparison_operator = Column(String(10), nullable=False)

    severity = Column(String(20), default="warning")

    notification_enabled = Column(Boolean, default=True)
    notification_channels = Column(JSON)

    is_active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<MetricThreshold(id={self.id}, metric_name='{self.metric_name}', threshold={self.threshold_value})>"
