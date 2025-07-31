"""
Results manager for handling validation results storage and retrieval
"""
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from .database import ValidationDatabase

class ValidationResultsManager:
    def __init__(self, db_path: str = "validation_results.db"):
        """Initialize the results manager with database connection"""
        self.db = ValidationDatabase(db_path)
    
    def start_validation_run(self, 
                           document_urls: Dict[str, str],
                           validation_config: Dict[str, Any],
                           user_id: str = "default",
                           project_name: str = "Unknown") -> str:
        """Start a new validation run and return the run ID"""
        run_id = self.db.store_validation_run(
            document_urls=document_urls,
            validation_config=validation_config,
            overall_score=0.0,  # Will be updated when complete
            status="RUNNING",
            execution_time=0.0,  # Will be updated when complete
            user_id=user_id,
            project_name=project_name
        )
        
        # Store start time for performance tracking
        self.db.store_performance_metric(run_id, "start_time", time.time())
        
        return run_id
    
    def complete_validation_run(self,
                              run_id: str,
                              overall_score: float,
                              status: str,
                              results: List[Dict[str, Any]],
                              error_message: str = None):
        """Complete a validation run with results"""
        start_time_result = None
        
        # Calculate execution time
        with self.db.db_path as db_path:
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT metric_value FROM performance_metrics 
                    WHERE run_id = ? AND metric_name = 'start_time'
                ''', (run_id,))
                start_time_result = cursor.fetchone()
        
        execution_time = 0.0
        if start_time_result:
            execution_time = time.time() - start_time_result['metric_value']
        
        # Update the validation run
        with self.db.db_path as db_path:
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE validation_runs 
                    SET overall_score = ?, status = ?, error_message = ?, execution_time = ?
                    WHERE id = ?
                ''', (overall_score, status, error_message, execution_time, run_id))
                conn.commit()
        
        # Store detailed results
        if results:
            self.db.store_validation_results(run_id, results)
        
        # Store completion metrics
        self.db.store_performance_metric(run_id, "completion_time", time.time())
        self.db.store_performance_metric(run_id, "execution_duration", execution_time)
        self.db.store_performance_metric(run_id, "total_checks", len(results) if results else 0)
        
        return run_id
    
    def get_validation_run_details(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get complete details for a validation run"""
        run_data = self.db.get_validation_run(run_id)
        
        if not run_data:
            return None
        
        # Parse JSON fields
        run_data['run']['document_urls'] = eval(run_data['run']['document_urls']) if run_data['run']['document_urls'] else {}
        run_data['run']['validation_config'] = eval(run_data['run']['validation_config']) if run_data['run']['validation_config'] else {}
        
        # Parse result details
        for result in run_data['results']:
            if result['details']:
                try:
                    result['details'] = eval(result['details'])
                except:
                    result['details'] = {}
        
        # Add summary statistics
        if run_data['results']:
            total_checks = len(run_data['results'])
            passed_checks = len([r for r in run_data['results'] if r['status'] == 'PASS'])
            failed_checks = len([r for r in run_data['results'] if r['status'] == 'FAIL'])
            warning_checks = len([r for r in run_data['results'] if r['status'] == 'WARNING'])
            
            run_data['summary'] = {
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': failed_checks,
                'warning_checks': warning_checks,
                'pass_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
            }
            
            # Group results by category
            categories = {}
            for result in run_data['results']:
                category = result['category']
                if category not in categories:
                    categories[category] = {
                        'total': 0,
                        'passed': 0,
                        'failed': 0,
                        'warnings': 0,
                        'average_score': 0,
                        'results': []
                    }
                
                categories[category]['total'] += 1
                categories[category]['results'].append(result)
                
                if result['status'] == 'PASS':
                    categories[category]['passed'] += 1
                elif result['status'] == 'FAIL':
                    categories[category]['failed'] += 1
                elif result['status'] == 'WARNING':
                    categories[category]['warnings'] += 1
            
            # Calculate category averages
            for category, data in categories.items():
                if data['total'] > 0:
                    data['average_score'] = sum(r['score'] for r in data['results']) / data['total']
                    data['pass_rate'] = (data['passed'] / data['total'] * 100)
            
            run_data['categories'] = categories
        
        return run_data
    
    def get_validation_history(self, limit: int = 50, user_id: str = None) -> List[Dict[str, Any]]:
        """Get validation run history with summary information"""
        runs = self.db.get_validation_history(limit, user_id)
        
        # Parse JSON fields and add summary info
        for run in runs:
            if run['document_urls']:
                try:
                    run['document_urls'] = eval(run['document_urls'])
                except:
                    run['document_urls'] = {}
            
            if run['validation_config']:
                try:
                    run['validation_config'] = eval(run['validation_config'])
                except:
                    run['validation_config'] = {}
        
        return runs
    
    def trigger_re_evaluation(self,
                            original_run_id: str,
                            document_urls: Dict[str, str],
                            validation_config: Dict[str, Any],
                            change_reason: str,
                            changed_by: str,
                            user_id: str = "default") -> str:
        """Trigger a re-evaluation of documents and track the relationship"""
        
        # Get original run for project name
        original_run = self.db.get_validation_run(original_run_id)
        if not original_run:
            raise ValueError(f"Original run {original_run_id} not found")
        
        project_name = original_run['run']['project_name']
        
        # Start new validation run
        new_run_id = self.start_validation_run(
            document_urls=document_urls,
            validation_config=validation_config,
            user_id=user_id,
            project_name=project_name
        )
        
        # Store re-evaluation relationship (will be completed after validation finishes)
        comparison_data = {
            'trigger_reason': change_reason,
            'triggered_by': changed_by,
            'original_run_timestamp': original_run['run']['timestamp'],
            'new_run_timestamp': datetime.now().isoformat()
        }
        
        self.db.store_re_evaluation(
            original_run_id=original_run_id,
            new_run_id=new_run_id,
            change_reason=change_reason,
            changed_by=changed_by,
            comparison_data=comparison_data
        )
        
        return new_run_id
    
    def compare_validation_runs(self, run_id1: str, run_id2: str) -> Dict[str, Any]:
        """Compare two validation runs and return detailed comparison"""
        return self.db.get_comparison_data(run_id1, run_id2)
    
    def get_project_timeline(self, project_name: str) -> Dict[str, Any]:
        """Get complete timeline for a project including all runs and re-evaluations"""
        project_runs = self.db.get_project_history(project_name)
        
        if not project_runs:
            return {"message": f"No validation history found for project: {project_name}"}
        
        # Get re-evaluation relationships
        timeline = []
        
        for run in project_runs:
            run_details = self.get_validation_run_details(run['id'])
            if run_details:
                timeline_entry = {
                    'run_id': run['id'],
                    'timestamp': run['timestamp'],
                    'overall_score': run['overall_score'],
                    'status': run['status'],
                    'execution_time': run['execution_time'],
                    'summary': run_details.get('summary', {}),
                    'is_re_evaluation': False,
                    're_evaluation_info': None
                }
                
                # Check if this is a re-evaluation
                with self.db.db_path as db_path:
                    import sqlite3
                    with sqlite3.connect(db_path) as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT * FROM validation_history 
                            WHERE new_run_id = ?
                        ''', (run['id'],))
                        re_eval = cursor.fetchone()
                        
                        if re_eval:
                            timeline_entry['is_re_evaluation'] = True
                            timeline_entry['re_evaluation_info'] = {
                                'original_run_id': re_eval['original_run_id'],
                                'change_reason': re_eval['change_reason'],
                                'changed_by': re_eval['changed_by']
                            }
                
                timeline.append(timeline_entry)
        
        # Calculate project statistics
        scores = [run['overall_score'] for run in project_runs if run['overall_score'] is not None]
        
        project_stats = {
            'total_runs': len(project_runs),
            'total_re_evaluations': len([t for t in timeline if t['is_re_evaluation']]),
            'average_score': sum(scores) / len(scores) if scores else 0,
            'best_score': max(scores) if scores else 0,
            'latest_score': scores[0] if scores else 0,  # First in list (most recent)
            'score_improvement': scores[0] - scores[-1] if len(scores) > 1 else 0
        }
        
        return {
            'project_name': project_name,
            'timeline': timeline,
            'statistics': project_stats
        }
    
    def get_trending_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive trending analytics"""
        base_metrics = self.db.get_trending_metrics(days)
        
        # Add additional analytics
        runs = self.db.get_validation_history(limit=1000)  # Get more data for analytics
        
        if not runs:
            return base_metrics
        
        # Calculate additional metrics
        recent_runs = [r for r in runs if r['timestamp']]  # Filter valid timestamps
        
        # Most common failure categories (would need to query detailed results)
        failure_analysis = {
            'most_common_failures': [],
            'improvement_areas': [],
            'success_patterns': []
        }
        
        # Performance metrics
        execution_times = [r['execution_time'] for r in recent_runs if r['execution_time']]
        performance_metrics = {
            'average_execution_time': sum(execution_times) / len(execution_times) if execution_times else 0,
            'fastest_execution': min(execution_times) if execution_times else 0,
            'slowest_execution': max(execution_times) if execution_times else 0
        }
        
        # Combine all metrics
        analytics = {
            **base_metrics,
            'failure_analysis': failure_analysis,
            'performance_metrics': performance_metrics,
            'data_quality': {
                'total_runs_analyzed': len(recent_runs),
                'runs_with_execution_time': len(execution_times),
                'data_completeness': len(execution_times) / len(recent_runs) * 100 if recent_runs else 0
            }
        }
        
        return analytics
    
    def export_validation_data(self, run_ids: List[str] = None, format: str = "json") -> Dict[str, Any]:
        """Export validation data for reporting or backup"""
        if run_ids:
            # Export specific runs
            export_data = []
            for run_id in run_ids:
                run_data = self.get_validation_run_details(run_id)
                if run_data:
                    export_data.append(run_data)
        else:
            # Export all recent runs
            runs = self.get_validation_history(limit=100)
            export_data = []
            for run in runs:
                run_data = self.get_validation_run_details(run['id'])
                if run_data:
                    export_data.append(run_data)
        
        export_package = {
            'export_timestamp': datetime.now().isoformat(),
            'export_format': format,
            'total_runs': len(export_data),
            'data': export_data
        }
        
        return export_package

