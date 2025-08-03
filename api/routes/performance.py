"""
Performance Monitoring API Routes

This module contains all performance monitoring endpoints for the Azul Solver & Analysis Toolkit.
"""

import json
import time
import psutil
import os
from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from ..auth import require_session
from ..models.performance import PerformanceStatsRequest, SystemHealthRequest

# Create Flask blueprint for performance endpoints
performance_bp = Blueprint('performance', __name__)


@performance_bp.route('/performance/stats', methods=['GET'])
@require_session
def get_performance_stats():
    """Get system performance statistics."""
    try:
        # Get system resources
        system_resources = get_system_resources()
        
        # Get process resources
        process_resources = get_process_resources()
        
        # Get database stats if available
        db_stats = {}
        if hasattr(current_app, 'database') and current_app.database:
            try:
                db_stats = current_app.database.get_stats()
            except Exception as e:
                current_app.logger.warning(f"Failed to get database stats: {e}")
        
        # Get cache stats if available
        cache_stats = {}
        if hasattr(current_app, 'cache') and current_app.cache:
            try:
                cache_stats = current_app.cache.get_stats()
            except Exception as e:
                current_app.logger.warning(f"Failed to get cache stats: {e}")
        
        return jsonify({
            'system': system_resources,
            'process': process_resources,
            'database': db_stats,
            'cache': cache_stats,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting performance stats: {e}")
        return jsonify({'error': 'Failed to get performance stats', 'message': str(e)}), 500


@performance_bp.route('/performance/health', methods=['GET'])
@require_session
def get_system_health():
    """Get system health status."""
    try:
        # Check system resources
        system_resources = get_system_resources()
        
        # Check process resources
        process_resources = get_process_resources()
        
        # Determine overall health
        health_status = 'healthy'
        warnings = []
        
        # Check memory usage
        if system_resources['memory']['percent'] > 90:
            health_status = 'warning'
            warnings.append('High memory usage')
        elif system_resources['memory']['percent'] > 80:
            warnings.append('Elevated memory usage')
        
        # Check CPU usage
        if system_resources['cpu']['percent'] > 90:
            health_status = 'warning'
            warnings.append('High CPU usage')
        elif system_resources['cpu']['percent'] > 80:
            warnings.append('Elevated CPU usage')
        
        # Check disk usage
        if system_resources['disk']['percent'] > 90:
            health_status = 'critical'
            warnings.append('Critical disk usage')
        elif system_resources['disk']['percent'] > 80:
            health_status = 'warning'
            warnings.append('High disk usage')
        
        # Check database connectivity
        db_healthy = True
        if hasattr(current_app, 'database') and current_app.database:
            try:
                current_app.database.test_connection()
            except Exception as e:
                db_healthy = False
                health_status = 'critical'
                warnings.append(f'Database connection failed: {str(e)}')
        
        return jsonify({
            'status': health_status,
            'warnings': warnings,
            'system': system_resources,
            'process': process_resources,
            'database_healthy': db_healthy,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting system health: {e}")
        return jsonify({'error': 'Failed to get system health', 'message': str(e)}), 500


@performance_bp.route('/performance/optimize', methods=['POST'])
@require_session
def optimize_database():
    """Optimize database performance."""
    try:
        if not hasattr(current_app, 'database') or not current_app.database:
            return jsonify({'error': 'Database not available'}), 503
        
        # Get optimization parameters
        data = request.get_json() or {}
        vacuum = data.get('vacuum', True)
        analyze = data.get('analyze', True)
        reindex = data.get('reindex', False)
        
        # Perform optimizations
        results = {}
        
        if vacuum:
            try:
                current_app.database.vacuum()
                results['vacuum'] = 'completed'
            except Exception as e:
                results['vacuum'] = f'failed: {str(e)}'
        
        if analyze:
            try:
                current_app.database.analyze()
                results['analyze'] = 'completed'
            except Exception as e:
                results['analyze'] = f'failed: {str(e)}'
        
        if reindex:
            try:
                current_app.database.reindex()
                results['reindex'] = 'completed'
            except Exception as e:
                results['reindex'] = f'failed: {str(e)}'
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error optimizing database: {e}")
        return jsonify({'error': 'Failed to optimize database', 'message': str(e)}), 500


@performance_bp.route('/performance/analytics', methods=['GET'])
@require_session
def get_cache_analytics():
    """Get cache analytics and performance metrics."""
    try:
        if not hasattr(current_app, 'database') or not current_app.database:
            return jsonify({'error': 'Database not available'}), 503
        
        # Get cache statistics
        cache_stats = current_app.database.get_cache_stats()
        
        # Get hit rate analytics
        hit_rate_data = current_app.database.get_hit_rate_analytics()
        
        # Get size analytics
        size_data = current_app.database.get_size_analytics()
        
        # Get performance metrics
        performance_metrics = current_app.database.get_performance_metrics()
        
        return jsonify({
            'cache_stats': cache_stats,
            'hit_rate_analytics': hit_rate_data,
            'size_analytics': size_data,
            'performance_metrics': performance_metrics,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting cache analytics: {e}")
        return jsonify({'error': 'Failed to get cache analytics', 'message': str(e)}), 500


@performance_bp.route('/performance/monitoring', methods=['GET'])
@require_session
def get_monitoring_data():
    """Get real-time monitoring data."""
    try:
        # Get current system state
        system_resources = get_system_resources()
        process_resources = get_process_resources()
        
        # Get database monitoring data
        db_monitoring = {}
        if hasattr(current_app, 'database') and current_app.database:
            try:
                db_monitoring = current_app.database.get_monitoring_data()
            except Exception as e:
                current_app.logger.warning(f"Failed to get database monitoring data: {e}")
        
        # Get cache monitoring data
        cache_monitoring = {}
        if hasattr(current_app, 'cache') and current_app.cache:
            try:
                cache_monitoring = current_app.cache.get_monitoring_data()
            except Exception as e:
                current_app.logger.warning(f"Failed to get cache monitoring data: {e}")
        
        return jsonify({
            'system': system_resources,
            'process': process_resources,
            'database': db_monitoring,
            'cache': cache_monitoring,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting monitoring data: {e}")
        return jsonify({'error': 'Failed to get monitoring data', 'message': str(e)}), 500


def get_system_resources():
    """Get system resource usage."""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Network I/O
        network = psutil.net_io_counters()
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
        }
    except Exception as e:
        return {
            'error': f'Failed to get system resources: {str(e)}',
            'cpu': {'percent': 0, 'count': 0},
            'memory': {'total': 0, 'available': 0, 'used': 0, 'percent': 0},
            'disk': {'total': 0, 'used': 0, 'free': 0, 'percent': 0},
            'network': {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0}
        }


def get_process_resources():
    """Get current process resource usage."""
    try:
        process = psutil.Process()
        
        # Memory info
        memory_info = process.memory_info()
        
        # CPU info
        cpu_percent = process.cpu_percent()
        cpu_times = process.cpu_times()
        
        # Open files
        open_files = len(process.open_files())
        
        # Threads
        num_threads = process.num_threads()
        
        # Connections
        connections = len(process.connections())
        
        return {
            'memory': {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': process.memory_percent()
            },
            'cpu': {
                'percent': cpu_percent,
                'user': cpu_times.user,
                'system': cpu_times.system
            },
            'files': open_files,
            'threads': num_threads,
            'connections': connections,
            'create_time': process.create_time()
        }
    except Exception as e:
        return {
            'error': f'Failed to get process resources: {str(e)}',
            'memory': {'rss': 0, 'vms': 0, 'percent': 0},
            'cpu': {'percent': 0, 'user': 0, 'system': 0},
            'files': 0,
            'threads': 0,
            'connections': 0,
            'create_time': 0
        } 