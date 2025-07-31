"""
Database schema and management for validation results storage
"""
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

class ValidationDatabase:
    def __init__(self, db_path: str = "validation_results.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Validation runs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS validation_runs (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    document_urls TEXT,
                    validation_config TEXT,
                    overall_score REAL,
                    status TEXT,
                    error_message TEXT,
                    execution_time REAL,
                    user_id TEXT,
                    project_name TEXT,
                    version INTEGER DEFAULT 1
                )
            ''')
            
            # Validation results table (detailed results per category)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS validation_results (
                    id TEXT PRIMARY KEY,
                    run_id TEXT,
                    category TEXT,
                    check_id TEXT,
                    check_name TEXT,
                    status TEXT,
                    score REAL,
                    message TEXT,
                    details TEXT,
                    FOREIGN KEY (run_id) REFERENCES validation_runs (id)
                )
            ''')
            
            # Document versions table (track document changes)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_versions (
                    id TEXT PRIMARY KEY,
                    document_url TEXT,
                    document_hash TEXT,
                    last_modified DATETIME,
                    file_size INTEGER,
                    document_type TEXT,
                    metadata TEXT
                )
            ''')
            
            # Validation history table (track re-evaluations)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS validation_history (
                    id TEXT PRIMARY KEY,
                    original_run_id TEXT,
                    new_run_id TEXT,
                    change_reason TEXT,
                    changed_by TEXT,
                    change_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    comparison_data TEXT,
                    FOREIGN KEY (original_run_id) REFERENCES validation_runs (id),
                    FOREIGN KEY (new_run_id) REFERENCES validation_runs (id)
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id TEXT PRIMARY KEY,
                    run_id TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (run_id) REFERENCES validation_runs (id)
                )
            ''')
            
            conn.commit()
    
    def store_validation_run(self, 
                           document_urls: Dict[str, str],
                           validation_config: Dict[str, Any],
                           overall_score: float,
                           status: str,
                           execution_time: float,
                           user_id: str = "default",
                           project_name: str = "Unknown",
                           error_message: str = None) -> str:
        """Store a validation run and return the run ID"""
        run_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO validation_runs 
                (id, document_urls, validation_config, overall_score, status, 
                 error_message, execution_time, user_id, project_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                run_id,
                json.dumps(document_urls),
                json.dumps(validation_config),
                overall_score,
                status,
                error_message,
                execution_time,
                user_id,
                project_name
            ))
            conn.commit()
        
        return run_id
    
    def store_validation_results(self, run_id: str, results: List[Dict[str, Any]]):
        """Store detailed validation results for a run"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for result in results:
                result_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO validation_results
                    (id, run_id, category, check_id, check_name, status, score, message, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result_id,
                    run_id,
                    result.get('category', ''),
                    result.get('check_id', ''),
                    result.get('check_name', ''),
                    result.get('status', ''),
                    result.get('score', 0.0),
                    result.get('message', ''),
                    json.dumps(result.get('details', {}))
                ))
            
            conn.commit()
    
    def get_validation_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific validation run by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM validation_runs WHERE id = ?', (run_id,))
            run = cursor.fetchone()
            
            if not run:
                return None
            
            # Get detailed results
            cursor.execute('SELECT * FROM validation_results WHERE run_id = ?', (run_id,))
            results = cursor.fetchall()
            
            return {
                'run': dict(run),
                'results': [dict(result) for result in results]
            }
    
    def get_validation_history(self, limit: int = 50, user_id: str = None) -> List[Dict[str, Any]]:
        """Get validation run history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = 'SELECT * FROM validation_runs'
            params = []
            
            if user_id:
                query += ' WHERE user_id = ?'
                params.append(user_id)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            runs = cursor.fetchall()
            
            return [dict(run) for run in runs]
    
    def get_project_history(self, project_name: str) -> List[Dict[str, Any]]:
        """Get validation history for a specific project"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM validation_runs 
                WHERE project_name = ? 
                ORDER BY timestamp DESC
            ''', (project_name,))
            
            runs = cursor.fetchall()
            return [dict(run) for run in runs]
    
    def store_re_evaluation(self, 
                          original_run_id: str,
                          new_run_id: str,
                          change_reason: str,
                          changed_by: str,
                          comparison_data: Dict[str, Any]) -> str:
        """Store re-evaluation information"""
        history_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO validation_history
                (id, original_run_id, new_run_id, change_reason, changed_by, comparison_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                history_id,
                original_run_id,
                new_run_id,
                change_reason,
                changed_by,
                json.dumps(comparison_data)
            ))
            conn.commit()
        
        return history_id
    
    def get_comparison_data(self, run_id1: str, run_id2: str) -> Dict[str, Any]:
        """Compare two validation runs"""
        run1 = self.get_validation_run(run_id1)
        run2 = self.get_validation_run(run_id2)
        
        if not run1 or not run2:
            return {"error": "One or both runs not found"}
        
        # Calculate score differences
        score_diff = run2['run']['overall_score'] - run1['run']['overall_score']
        
        # Compare category scores
        category_comparison = {}
        
        # Group results by category
        run1_categories = {}
        run2_categories = {}
        
        for result in run1['results']:
            category = result['category']
            if category not in run1_categories:
                run1_categories[category] = []
            run1_categories[category].append(result)
        
        for result in run2['results']:
            category = result['category']
            if category not in run2_categories:
                run2_categories[category] = []
            run2_categories[category].append(result)
        
        # Compare categories
        for category in set(list(run1_categories.keys()) + list(run2_categories.keys())):
            cat1_score = sum(r['score'] for r in run1_categories.get(category, [])) / max(len(run1_categories.get(category, [])), 1)
            cat2_score = sum(r['score'] for r in run2_categories.get(category, [])) / max(len(run2_categories.get(category, [])), 1)
            
            category_comparison[category] = {
                'old_score': cat1_score,
                'new_score': cat2_score,
                'difference': cat2_score - cat1_score,
                'improvement': cat2_score > cat1_score
            }
        
        return {
            'run1': run1['run'],
            'run2': run2['run'],
            'overall_score_difference': score_diff,
            'overall_improvement': score_diff > 0,
            'category_comparison': category_comparison,
            'timestamp_comparison': {
                'run1_timestamp': run1['run']['timestamp'],
                'run2_timestamp': run2['run']['timestamp'],
                'time_between_runs': run2['run']['timestamp']  # Would need proper datetime parsing
            }
        }
    
    def get_trending_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get trending metrics for the specified time period"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get runs from the last N days
            cursor.execute('''
                SELECT * FROM validation_runs 
                WHERE timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp
            '''.format(days))
            
            runs = cursor.fetchall()
            
            if not runs:
                return {"message": "No data available for the specified period"}
            
            # Calculate trending metrics
            scores = [run['overall_score'] for run in runs]
            statuses = [run['status'] for run in runs]
            
            pass_rate = len([s for s in statuses if s == 'PASS']) / len(statuses) * 100
            avg_score = sum(scores) / len(scores)
            
            # Score trend (simple linear trend)
            if len(scores) > 1:
                x_vals = list(range(len(scores)))
                y_vals = scores
                n = len(scores)
                sum_x = sum(x_vals)
                sum_y = sum(y_vals)
                sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
                sum_x2 = sum(x * x for x in x_vals)
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                trend = "improving" if slope > 0 else "declining" if slope < 0 else "stable"
            else:
                trend = "insufficient_data"
            
            return {
                'period_days': days,
                'total_runs': len(runs),
                'pass_rate': pass_rate,
                'average_score': avg_score,
                'score_trend': trend,
                'latest_score': scores[-1] if scores else 0,
                'best_score': max(scores) if scores else 0,
                'worst_score': min(scores) if scores else 0
            }
    
    def store_performance_metric(self, run_id: str, metric_name: str, metric_value: float):
        """Store a performance metric for a validation run"""
        metric_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO performance_metrics (id, run_id, metric_name, metric_value)
                VALUES (?, ?, ?, ?)
            ''', (metric_id, run_id, metric_name, metric_value))
            conn.commit()
    
    def cleanup_old_runs(self, days_to_keep: int = 90):
        """Clean up old validation runs (optional maintenance)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get old run IDs
            cursor.execute('''
                SELECT id FROM validation_runs 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days_to_keep))
            
            old_run_ids = [row[0] for row in cursor.fetchall()]
            
            if old_run_ids:
                # Delete related records
                placeholders = ','.join(['?' for _ in old_run_ids])
                
                cursor.execute(f'DELETE FROM validation_results WHERE run_id IN ({placeholders})', old_run_ids)
                cursor.execute(f'DELETE FROM performance_metrics WHERE run_id IN ({placeholders})', old_run_ids)
                cursor.execute(f'DELETE FROM validation_runs WHERE id IN ({placeholders})', old_run_ids)
                
                conn.commit()
                
                return len(old_run_ids)
            
            return 0

