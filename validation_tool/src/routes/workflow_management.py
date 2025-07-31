"""
API routes for workflow management and re-evaluation
"""
from flask import Blueprint, request, jsonify
import asyncio
import json
from datetime import datetime
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.re_evaluation_engine import ReEvaluationEngine

workflow_management_bp = Blueprint('workflow_management', __name__)

# Initialize re-evaluation engine
re_evaluation_engine = ReEvaluationEngine()

@workflow_management_bp.route('/api/workflow/start-validation', methods=['POST'])
def start_validation_workflow():
    """Start a comprehensive validation workflow"""
    try:
        data = request.get_json()
        
        required_fields = ['document_urls', 'validation_config']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Start the validation workflow
        run_id = asyncio.run(re_evaluation_engine.start_comprehensive_validation(
            document_urls=data['document_urls'],
            validation_config=data['validation_config'],
            user_id=data.get('user_id', 'default'),
            project_name=data.get('project_name', 'Unknown')
        ))
        
        return jsonify({
            'status': 'success',
            'message': 'Validation workflow started',
            'run_id': run_id
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@workflow_management_bp.route('/api/workflow/re-evaluate', methods=['POST'])
def trigger_re_evaluation():
    """Trigger re-evaluation of a previous validation run"""
    try:
        data = request.get_json()
        
        required_fields = ['original_run_id', 'change_reason', 'changed_by']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        new_run_id = re_evaluation_engine.trigger_re_evaluation(
            original_run_id=data['original_run_id'],
            change_reason=data['change_reason'],
            changed_by=data['changed_by'],
            user_id=data.get('user_id', 'default'),
            updated_config=data.get('updated_config')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Re-evaluation triggered successfully',
            'new_run_id': new_run_id,
            'original_run_id': data['original_run_id']
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@workflow_management_bp.route('/api/workflow/status/<run_id>', methods=['GET'])
def get_validation_status(run_id):
    """Get the current status of a validation run"""
    try:
        status = re_evaluation_engine.get_evaluation_status(run_id)
        
        return jsonify({
            'status': 'success',
            'data': status
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@workflow_management_bp.route('/api/workflow/active', methods=['GET'])
def get_active_evaluations():
    """Get all currently active evaluations"""
    try:
        active_evaluations = re_evaluation_engine.get_active_evaluations()
        
        return jsonify({
            'status': 'success',
            'data': active_evaluations,
            'total_active': len(active_evaluations)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@workflow_management_bp.route('/api/workflow/cancel/<run_id>', methods=['POST'])
def cancel_evaluation(run_id):
    """Cancel a running evaluation"""
    try:
        success = re_evaluation_engine.cancel_evaluation(run_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Evaluation {run_id} cancelled successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Evaluation {run_id} not found or not running'
            }), 404
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@workflow_management_bp.route('/api/workflow/progress/<run_id>', methods=['GET'])
def get_validation_progress(run_id):
    """Get detailed progress information for a validation run"""
    try:
        # Get current status
        status = re_evaluation_engine.get_evaluation_status(run_id)
        
        # Get run details if completed
        run_details = None
        if status.get('status') in ['COMPLETED', 'FAILED', 'ERROR', 'CANCELLED']:
            run_details = re_evaluation_engine.results_manager.get_validation_run_details(run_id)
        
        progress_data = {
            'run_id': run_id,
            'status': status,
            'run_details': run_details,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': progress_data
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@workflow_management_bp.route('/api/workflow/history/<project_name>', methods=['GET'])
def get_project_workflow_history(project_name):
    """Get complete workflow history for a project"""
    try:
        timeline = re_evaluation_engine.results_manager.get_project_timeline(project_name)
        
        return jsonify({
            'status': 'success',
            'data': timeline
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@workflow_management_bp.route('/api/workflow/compare-runs', methods=['POST'])
def compare_workflow_runs():
    """Compare two validation runs from workflow perspective"""
    try:
        data = request.get_json()
        
        run_id1 = data.get('run_id1')
        run_id2 = data.get('run_id2')
        
        if not run_id1 or not run_id2:
            return jsonify({
                'status': 'error',
                'message': 'Both run_id1 and run_id2 are required'
            }), 400
        
        comparison = re_evaluation_engine.results_manager.compare_validation_runs(run_id1, run_id2)
        
        # Add workflow-specific comparison data
        workflow_comparison = {
            'basic_comparison': comparison,
            'workflow_analysis': {
                'score_improvement': comparison.get('overall_score_difference', 0) > 0,
                'significant_change': abs(comparison.get('overall_score_difference', 0)) > 5,
                'recommendation': 'improvement' if comparison.get('overall_score_difference', 0) > 0 else 'needs_attention'
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': workflow_comparison
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@workflow_management_bp.route('/api/workflow/batch-re-evaluate', methods=['POST'])
def batch_re_evaluation():
    """Trigger re-evaluation for multiple runs"""
    try:
        data = request.get_json()
        
        run_ids = data.get('run_ids', [])
        change_reason = data.get('change_reason', 'Batch re-evaluation')
        changed_by = data.get('changed_by', 'System')
        
        if not run_ids:
            return jsonify({
                'status': 'error',
                'message': 'run_ids list is required'
            }), 400
        
        results = []
        for run_id in run_ids:
            try:
                new_run_id = re_evaluation_engine.trigger_re_evaluation(
                    original_run_id=run_id,
                    change_reason=change_reason,
                    changed_by=changed_by,
                    user_id=data.get('user_id', 'default')
                )
                
                results.append({
                    'original_run_id': run_id,
                    'new_run_id': new_run_id,
                    'status': 'success'
                })
            
            except Exception as e:
                results.append({
                    'original_run_id': run_id,
                    'new_run_id': None,
                    'status': 'error',
                    'error': str(e)
                })
        
        successful_count = len([r for r in results if r['status'] == 'success'])
        
        return jsonify({
            'status': 'success',
            'message': f'Batch re-evaluation completed: {successful_count}/{len(run_ids)} successful',
            'results': results,
            'summary': {
                'total_requested': len(run_ids),
                'successful': successful_count,
                'failed': len(run_ids) - successful_count
            }
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@workflow_management_bp.route('/api/workflow/analytics', methods=['GET'])
def get_workflow_analytics():
    """Get workflow analytics and performance metrics"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Get basic analytics
        analytics = re_evaluation_engine.results_manager.get_trending_analytics(days=days)
        
        # Add workflow-specific metrics
        active_evaluations = re_evaluation_engine.get_active_evaluations()
        
        workflow_metrics = {
            'basic_analytics': analytics,
            'workflow_metrics': {
                'currently_running': len(active_evaluations),
                'active_evaluations': list(active_evaluations.keys()),
                'system_load': 'normal' if len(active_evaluations) < 5 else 'high',
                'average_execution_time': analytics.get('performance_metrics', {}).get('average_execution_time', 0)
            },
            'recommendations': []
        }
        
        # Add recommendations based on metrics
        if analytics.get('pass_rate', 0) < 70:
            workflow_metrics['recommendations'].append({
                'type': 'quality_improvement',
                'message': 'Pass rate is below 70%. Consider reviewing validation criteria or document quality.',
                'priority': 'high'
            })
        
        if len(active_evaluations) > 3:
            workflow_metrics['recommendations'].append({
                'type': 'performance',
                'message': 'Multiple evaluations running simultaneously. Consider staggering validation runs.',
                'priority': 'medium'
            })
        
        return jsonify({
            'status': 'success',
            'data': workflow_metrics
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

