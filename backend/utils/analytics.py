from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class AnalyticsEngine:
    """Analytics engine for processing and analyzing metrics"""

    @staticmethod
    def calculate_growth_rate(current_value: float, previous_value: float) -> float:
        """Calculate growth rate percentage"""
        if previous_value == 0:
            return 100.0 if current_value > 0 else 0.0
        return ((current_value - previous_value) / previous_value) * 100

    @staticmethod
    def calculate_moving_average(values: List[float], window_size: int) -> List[float]:
        """Calculate simple moving average"""
        if len(values) < window_size:
            return values

        result = []
        for i in range(len(values) - window_size + 1):
            window = values[i : i + window_size]
            result.append(sum(window) / window_size)

        return result

    @staticmethod
    def detect_anomalies(
        values: List[float], threshold_std: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using standard deviation"""
        if len(values) < 3:
            return []

        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        anomalies = []
        for i, value in enumerate(values):
            z_score = abs((value - mean) / stdev) if stdev > 0 else 0
            if z_score > threshold_std:
                anomalies.append(
                    {
                        "index": i,
                        "value": value,
                        "z_score": z_score,
                        "is_high": value > mean,
                    }
                )

        return anomalies

    @staticmethod
    def calculate_percentiles(
        values: List[float], percentiles: List[int] = [50, 75, 90, 95, 99]
    ) -> Dict[str, float]:
        """Calculate percentiles for a list of values"""
        if not values:
            return {f"p{p}": 0 for p in percentiles}

        sorted_values = sorted(values)
        result = {}

        for p in percentiles:
            index = int(len(sorted_values) * p / 100)
            result[f"p{p}"] = sorted_values[min(index, len(sorted_values) - 1)]

        return result

    @staticmethod
    def aggregate_by_time_period(
        data: List[Dict[str, Any]],
        timestamp_field: str,
        value_field: str,
        period: str = "day",
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Aggregate data by time period"""
        aggregated = defaultdict(list)

        for item in data:
            timestamp = item.get(timestamp_field)
            if not timestamp:
                continue

            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            if period == "hour":
                key = timestamp.strftime("%Y-%m-%d %H:00")
            elif period == "day":
                key = timestamp.strftime("%Y-%m-%d")
            elif period == "week":
                key = timestamp.strftime("%Y-W%U")
            elif period == "month":
                key = timestamp.strftime("%Y-%m")
            else:
                key = timestamp.strftime("%Y-%m-%d")

            aggregated[key].append(item.get(value_field))

        result = {}
        for key, values in aggregated.items():
            result[key] = {
                "count": len(values),
                "sum": sum(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            }

        return result

    @staticmethod
    def calculate_retention(
        initial_value: float, values_over_time: List[float], period: str = "day"
    ) -> List[Dict[str, Any]]:
        """Calculate retention metrics"""
        if not values_over_time:
            return []

        retention_data = []
        current_value = initial_value

        for i, value in enumerate(values_over_time):
            retention_rate = (value / initial_value) * 100 if initial_value > 0 else 0
            churn_rate = 100 - retention_rate

            retention_data.append(
                {
                    "period_index": i,
                    "period": period,
                    "value": value,
                    "retention_rate": round(retention_rate, 2),
                    "churn_rate": round(churn_rate, 2),
                    "absolute_change": value - current_value,
                    "relative_change": ((value - current_value) / current_value * 100)
                    if current_value > 0
                    else 0,
                }
            )

            current_value = value

        return retention_data

    @staticmethod
    def calculate_cohort_retention(
        cohorts: Dict[str, List[float]],
    ) -> List[Dict[str, Any]]:
        """Calculate cohort-based retention"""
        result = []

        for cohort_name, values in cohorts.items():
            initial_value = values[0] if values else 0

            retention_periods = []
            for i, value in enumerate(values):
                retention_rate = (
                    (value / initial_value * 100) if initial_value > 0 else 0
                )
                retention_periods.append(round(retention_rate, 1))

            result.append(
                {
                    "cohort": cohort_name,
                    "initial_size": initial_value,
                    "retention_by_period": retention_periods,
                }
            )

        return result

    @staticmethod
    def generate_trend_analysis(
        values: List[float], timestamps: List[datetime]
    ) -> Dict[str, Any]:
        """Generate trend analysis for a time series"""
        if len(values) < 2:
            return {"trend": "insufficient_data"}

        n = len(values)

        x_mean = sum(range(n)) / n
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        y_intercept = y_mean - slope * x_mean

        if abs(slope) < 0.01:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        predicted_next = slope * n + y_intercept

        return {
            "trend": trend,
            "slope": round(slope, 4),
            "y_intercept": round(y_intercept, 4),
            "predicted_next_value": round(predicted_next, 4),
            "direction": "up" if slope > 0 else "down",
            "strength": "strong" if abs(slope) > 0.1 else "weak",
        }


class RealTimeAnalytics:
    """Real-time analytics processor"""

    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._timers: Dict[str, List[float]] = defaultdict(list)
        self._last_updated: Dict[str, datetime] = {}

    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter metric"""
        self._counters[name] += value
        self._last_updated[name] = datetime.utcnow()

    def set_gauge(self, name: str, value: float):
        """Set a gauge metric"""
        self._gauges[name] = value
        self._last_updated[name] = datetime.utcnow()

    def record_timing(self, name: str, duration_ms: float):
        """Record a timing metric"""
        self._timers[name].append(duration_ms)
        if len(self._timers[name]) > 1000:
            self._timers[name] = self._timers[name][-1000:]
        self._last_updated[name] = datetime.utcnow()

    def get_counter(self, name: str) -> int:
        """Get current counter value"""
        return self._counters.get(name, 0)

    def get_gauge(self, name: str) -> Optional[float]:
        """Get current gauge value"""
        return self._gauges.get(name)

    def get_timing_stats(self, name: str) -> Dict[str, float]:
        """Get timing statistics"""
        values = self._timers.get(name, [])
        if not values:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}

        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "p50": AnalyticsEngine._percentile_single(values, 50),
            "p95": AnalyticsEngine._percentile_single(values, 95),
            "p99": AnalyticsEngine._percentile_single(values, 99),
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "timers": {
                name: self.get_timing_stats(name) for name in self._timers.keys()
            },
            "last_updated": {k: v.isoformat() for k, v in self._last_updated.items()},
        }

    def reset(self):
        """Reset all metrics"""
        self._counters.clear()
        self._gauges.clear()
        self._timers.clear()
        self._last_updated.clear()


class DashboardGenerator:
    """Generate dashboard configurations"""

    @staticmethod
    def generate_metrics_dashboard(
        title: str, metrics: List[str], time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Generate a metrics dashboard configuration"""
        widgets = []

        for i, metric in enumerate(metrics[:6]):
            row = i // 3
            col = i % 3

            widget = {
                "id": f"widget_{i}",
                "type": "metric_chart",
                "metric": metric,
                "position": {"row": row, "col": col, "width": 1, "height": 1},
                "chart_config": {
                    "type": "line",
                    "show_legend": True,
                    "show_grid": True,
                },
            }
            widgets.append(widget)

        return {
            "title": title,
            "time_range": time_range,
            "widgets": widgets,
            "layout": {"type": "grid", "columns": 3, "rows": 2},
        }

    @staticmethod
    def generate_summary_dashboard(
        title: str, metrics: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Generate a summary dashboard with metric cards"""
        widgets = []

        for i, metric in enumerate(metrics[:4]):
            widget = {
                "id": f"card_{i}",
                "type": "metric_card",
                "metric": metric.get("name"),
                "label": metric.get("label", metric.get("name")),
                "unit": metric.get("unit", ""),
                "position": {"row": 0, "col": i, "width": 1, "height": 1},
                "display": {
                    "show_trend": True,
                    "show_comparison": True,
                    "color_scheme": metric.get("color", "blue"),
                },
            }
            widgets.append(widget)

        return {
            "title": title,
            "widgets": widgets,
            "layout": {"type": "flex", "direction": "row"},
        }


real_time_analytics = RealTimeAnalytics()
