"""
Metrics Collector - Tracks real system performance and usage metrics
Replaces mock data with actual system measurements
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import sqlite3
import os
import time
import psutil
import threading
from typing import Dict, List, Any

metrics_collector_bp = Blueprint('metrics_collector', __name__)

# Database path
DB_PATH = '/home/ubuntu/validation_tool/data/validation_results.db'

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
        self.validation_count = 0
        self.successful_validations = 0
        self.failed_validations = 0
        self.total_processing_time = 0.0
        
    def record_validation_start(self, validation_id: str):
        """Record when a validation starts"""
        self.validation_count += 1
        return time.time()
    
    def record_validation_complete(self, validation_id: str, start_time: float, success: bool, score: float):
        """Record when a validation completes"""
        processing_time = time.time() - start_time
        self.total_processing_time += processing_time
        
        if success:
            self.successful_validations += 1
        else:
            self.failed_validations += 1
            
        # Store in database
        self._store_validation_metrics(validation_id, processing_time, success, score)
    
    def _store_validation_metrics(self, validation_id: str, processing_time: float, success: bool, score: float):
        """Store validation metrics in database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            
            # Update validation run with actual metrics
            conn.execute('''
                UPDATE validation_runs 
                SET execution_time = ?, status = ?
                WHERE validation_id = ?
            ''', (processing_time, 'completed' if success else 'failed', validation_id))
            
            # Insert system metrics
            now = datetime.now().isoformat()
            
            # Calculate current success rate
            success_rate = (self.successful_validations / self.validation_count * 100) if self.validation_count > 0 else 0
            avg_processing_time = (self.total_processing_time / self.validation_count) if self.validation_count > 0 else 0
            
            metrics = [
                ('total_validations', self.validation_count, 'count'),
                ('success_rate', success_rate, 'percentage'),
                ('avg_processing_time', avg_processing_time, 'seconds'),
                ('last_validation_score', score, 'percentage'),
                ('last_validation_time', processing_time, 'seconds')
            ]
            
            for metric_name, value, unit in metrics:
                conn.execute('''
                    INSERT INTO system_metrics (timestamp, metric_name, metric_value, metric_unit)
                    VALUES (?, ?, ?, ?)
                ''', (now, metric_name, value, unit))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing metrics: {e}")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        uptime_hours = (time.time() - self.start_time) / 3600
        
        # Get system resource usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'uptime_hours': uptime_hours,
            'total_validations': self.validation_count,
            'successful_validations': self.successful_validations,
            'failed_validations': self.failed_validations,
            'success_rate': (self.successful_validations / self.validation_count * 100) if self.validation_count > 0 else 0,
            'avg_processing_time': (self.total_processing_time / self.validation_count) if self.validation_count > 0 else 0,
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'disk_usage': disk.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_free_gb': disk.free / (1024**3)
        }

# Global metrics collector instance
metrics_collector = MetricsCollector()

@metrics_collector_bp.route('/api/metrics/system', methods=['GET'])
def get_system_metrics():
    """Get real-time system metrics"""
    try:
        metrics = metrics_collector.get_system_metrics()
        
        # Get additional metrics from database
        conn = sqlite3.connect(DB_PATH)
        
        # Get latest validation metrics
        latest_metrics = conn.execute('''
            SELECT metric_name, metric_value, metric_unit, timestamp
            FROM system_metrics
            WHERE timestamp >= datetime('now', '-1 hour')
            ORDER BY timestamp DESC
        ''').fetchall()
        
        db_metrics = {}
        for row in latest_metrics:
            if row[0] not in db_metrics:  # Get most recent value for each metric
                db_metrics[row[0]] = {
                    'value': row[1],
                    'unit': row[2],
                    'timestamp': row[3]
                }
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'real_time_metrics': metrics,
                'stored_metrics': db_metrics,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@metrics_collector_bp.route('/api/metrics/performance', methods=['GET'])
def get_performance_metrics():
    """Get performance metrics over time"""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Get validation performance over time
        performance_data = conn.execute('''
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_validations,
                AVG(overall_score) as avg_score,
                AVG(execution_time) as avg_time,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful
            FROM validation_runs
            WHERE timestamp >= datetime('now', '-30 days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        ''').fetchall()
        
        performance_trends = []
        for row in performance_data:
            performance_trends.append({
                'date': row[0],
                'total_validations': row[1],
                'avg_score': row[2] or 0,
                'avg_processing_time': row[3] or 0,
                'successful_validations': row[4],
                'success_rate': (row[4] / row[1] * 100) if row[1] > 0 else 0
            })
        
        # Get hourly metrics for today
        hourly_data = conn.execute('''
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as validations,
                AVG(overall_score) as avg_score
            FROM validation_runs
            WHERE DATE(timestamp) = DATE('now')
            GROUP BY strftime('%H', timestamp)
            ORDER BY hour
        ''').fetchall()
        
        hourly_trends = []
        for row in hourly_data:
            hourly_trends.append({
                'hour': int(row[0]),
                'validations': row[1],
                'avg_score': row[2] or 0
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'daily_trends': performance_trends,
                'hourly_trends': hourly_trends,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@metrics_collector_bp.route('/api/metrics/validation-stats', methods=['GET'])
def get_validation_stats():
    """Get detailed validation statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Get overall statistics
        overall_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_runs,
                AVG(overall_score) as avg_score,
                MIN(overall_score) as min_score,
                MAX(overall_score) as max_score,
                AVG(execution_time) as avg_time,
                MIN(execution_time) as min_time,
                MAX(execution_time) as max_time,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_runs
            FROM validation_runs
        ''').fetchone()
        
        # Get category statistics
        category_stats = conn.execute('''
            SELECT 
                category_name,
                COUNT(*) as total_checks,
                AVG(score) as avg_score,
                MIN(score) as min_score,
                MAX(score) as max_score,
                SUM(CASE WHEN status = 'pass' THEN 1 ELSE 0 END) as passed_checks
            FROM validation_categories
            GROUP BY category_name
            ORDER BY avg_score DESC
        ''').fetchall()
        
        # Get issue statistics
        issue_stats = conn.execute('''
            SELECT 
                severity,
                category,
                COUNT(*) as frequency,
                issue_description
            FROM validation_issues
            GROUP BY severity, category, issue_description
            ORDER BY frequency DESC, severity DESC
        ''').fetchall()
        
        conn.close()
        
        # Format results
        stats = {
            'overall': {
                'total_runs': overall_stats[0] or 0,
                'avg_score': overall_stats[1] or 0,
                'min_score': overall_stats[2] or 0,
                'max_score': overall_stats[3] or 0,
                'avg_processing_time': overall_stats[4] or 0,
                'min_processing_time': overall_stats[5] or 0,
                'max_processing_time': overall_stats[6] or 0,
                'successful_runs': overall_stats[7] or 0,
                'success_rate': (overall_stats[7] / overall_stats[0] * 100) if overall_stats[0] > 0 else 0
            },
            'categories': [
                {
                    'name': row[0],
                    'total_checks': row[1],
                    'avg_score': row[2] or 0,
                    'min_score': row[3] or 0,
                    'max_score': row[4] or 0,
                    'passed_checks': row[5] or 0,
                    'pass_rate': (row[5] / row[1] * 100) if row[1] > 0 else 0
                }
                for row in category_stats
            ],
            'issues': [
                {
                    'severity': row[0],
                    'category': row[1],
                    'frequency': row[2],
                    'description': row[3]
                }
                for row in issue_stats
            ]
        }
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Function to be called by validation endpoints
def record_validation_start(validation_id: str):
    """Record validation start - to be called by validation endpoints"""
    return metrics_collector.record_validation_start(validation_id)

def record_validation_complete(validation_id: str, start_time: float, success: bool, score: float):
    """Record validation completion - to be called by validation endpoints"""
    return metrics_collector.record_validation_complete(validation_id, start_time, success, score)

