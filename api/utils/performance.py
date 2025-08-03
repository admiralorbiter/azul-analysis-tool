"""
Performance monitoring utilities for the API.
"""

import psutil
from typing import Dict, Any


def get_process_resources() -> Dict[str, Any]:
    """Get current process resource usage."""
    try:
        process = psutil.Process()
        cpu_percent = process.cpu_percent()
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'memory_used_mb': memory_info.rss / (1024**2),
            'threads': process.num_threads()
        }
    except Exception as e:
        return {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_used_mb': 0.0,
            'threads': 0,
            'error': str(e)
        }


def get_system_resources() -> Dict[str, Any]:
    """Get system-wide resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / (1024**3),
            'memory_total_gb': memory.total / (1024**3),
            'disk_percent': disk.percent,
            'disk_used_gb': disk.used / (1024**3),
            'disk_total_gb': disk.total / (1024**3)
        }
    except Exception as e:
        return {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_used_gb': 0.0,
            'memory_total_gb': 0.0,
            'disk_percent': 0.0,
            'disk_used_gb': 0.0,
            'disk_total_gb': 0.0,
            'error': str(e)
        } 