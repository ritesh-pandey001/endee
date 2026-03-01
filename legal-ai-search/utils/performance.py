"""
Performance monitoring and logging utilities.
"""

import time
import functools
from typing import Callable, Any, Dict
from datetime import datetime
import json
from pathlib import Path

from app.core.config import settings
from app.core.logging_config import logger


class PerformanceTracker:
    """
    Track and log performance metrics for API endpoints and operations.
    """
    
    def __init__(self):
        """Initialize performance tracker."""
        self.metrics = {}
        self.metrics_file = Path("./data/performance_metrics.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_metrics()
    
    def _load_metrics(self):
        """Load existing metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    self.metrics = json.load(f)
                logger.info("Loaded performance metrics from file")
            except Exception as e:
                logger.error(f"Error loading metrics: {e}")
                self.metrics = {}
    
    def _save_metrics(self):
        """Save metrics to file."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def track_operation(self, operation_name: str, duration_ms: float, 
                       success: bool = True, metadata: Dict[str, Any] = None):
        """
        Track an operation's performance.
        
        Args:
            operation_name: Name of the operation
            duration_ms: Duration in milliseconds
            success: Whether operation succeeded
            metadata: Additional metadata
        """
        if not settings.enable_performance_logging:
            return
        
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                "count": 0,
                "total_time_ms": 0,
                "min_time_ms": float('inf'),
                "max_time_ms": 0,
                "successes": 0,
                "failures": 0,
                "last_updated": None
            }
        
        metric = self.metrics[operation_name]
        metric["count"] += 1
        metric["total_time_ms"] += duration_ms
        metric["min_time_ms"] = min(metric["min_time_ms"], duration_ms)
        metric["max_time_ms"] = max(metric["max_time_ms"], duration_ms)
        
        if success:
            metric["successes"] += 1
        else:
            metric["failures"] += 1
        
        metric["last_updated"] = datetime.utcnow().isoformat()
        
        # Save periodically
        if metric["count"] % 10 == 0:
            self._save_metrics()
        
        # Log slow operations
        if duration_ms > 5000:  # > 5 seconds
            logger.warning(f"Slow operation detected: {operation_name} took {duration_ms:.2f}ms")
    
    def get_metrics(self, operation_name: str = None) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Args:
            operation_name: Optional - get metrics for specific operation
            
        Returns:
            Metrics dictionary
        """
        if operation_name:
            metric = self.metrics.get(operation_name, {})
            if metric and metric.get("count", 0) > 0:
                return {
                    "operation": operation_name,
                    "total_requests": metric["count"],
                    "avg_response_time_ms": metric["total_time_ms"] / metric["count"],
                    "min_response_time_ms": metric["min_time_ms"],
                    "max_response_time_ms": metric["max_time_ms"],
                    "success_rate": metric["successes"] / metric["count"] if metric["count"] > 0 else 0,
                    "last_updated": metric.get("last_updated")
                }
            return {}
        else:
            # Return all metrics
            result = {}
            for name, metric in self.metrics.items():
                if metric.get("count", 0) > 0:
                    result[name] = {
                        "total_requests": metric["count"],
                        "avg_response_time_ms": metric["total_time_ms"] / metric["count"],
                        "min_response_time_ms": metric["min_time_ms"],
                        "max_response_time_ms": metric["max_time_ms"],
                        "success_rate": metric["successes"] / metric["count"],
                        "last_updated": metric.get("last_updated")
                    }
            return result
    
    def reset_metrics(self, operation_name: str = None):
        """
        Reset performance metrics.
        
        Args:
            operation_name: Optional - reset only specific operation
        """
        if operation_name:
            if operation_name in self.metrics:
                del self.metrics[operation_name]
                logger.info(f"Reset metrics for {operation_name}")
        else:
            self.metrics = {}
            logger.info("Reset all metrics")
        
        self._save_metrics()


# Global performance tracker
performance_tracker = PerformanceTracker()


def track_performance(operation_name: str = None):
    """
    Decorator to track function performance.
    
    Args:
        operation_name: Optional custom name (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            start_time = time.time()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                performance_tracker.track_operation(op_name, duration_ms, success)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                performance_tracker.track_operation(op_name, duration_ms, success)
        
        # Return appropriate wrapper based on function type
        if functools.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class RequestTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str):
        """
        Initialize timer.
        
        Args:
            operation_name: Name of operation being timed
        """
        self.operation_name = operation_name
        self.start_time = None
        self.duration_ms = None
    
    def __enter__(self):
        """Start timer."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer and log performance."""
        self.duration_ms = (time.time() - self.start_time) * 1000
        success = exc_type is None
        performance_tracker.track_operation(self.operation_name, self.duration_ms, success)
        
        if settings.enable_performance_logging:
            status = "succeeded" if success else "failed"
            logger.info(f"{self.operation_name} {status} in {self.duration_ms:.2f}ms")
