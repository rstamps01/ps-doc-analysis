"""
API routes for validation results storage and management
"""
from flask import Blueprint, request, jsonify
import json
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import from storage
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.results_manager import ValidationResultsManager

results_storage_bp = Blueprint('results_storage', __name__)

# Initialize results manager
results_manager = ValidationResultsManager()

@results_storage_bp.route('/api/results/history', methods=['GET'])
def get_validation_history():
    """Get validation run history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        user_id = request.args.get('user_id')
        
        history = results_manager.get_validation_history(limit=limit, user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'data': history,
            'total': len(history)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@results_storage_bp.route('/api/results/run/<run_id>', methods=['GET'])
def get_validation_run_details(run_id):
    """Get detailed results for a specific validation run"""
    try:
        run_details = results_manager.get_validation_run_details(run_id)
        
        if not run_details:
            return jsonify({
                'status': 'error',
                'message': f'Validation run {run_id} not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': run_details
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@results_storage_bp.route('/api/results/compare', methods=['POST'])
def compare_validation_runs():
    """Compare two validation runs"""
    try:
        data = request.get_json()
        run_id1 = data.get('run_id1')
        run_id2 = data.get('run_id2')
        
        if not run_id1 or not run_id2:
            return jsonify({
                'status': 'error',
                'message': 'Both run_id1 and run_id2 are required'
            }), 400
        
        comparison = results_manager.compare_validation_runs(run_id1, run_id2)
        
        return jsonify({
            'status': 'success',
            'data': comparison
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@results_storage_bp.route('/api/results/project/<project_name>/timeline', methods=['GET'])
def get_project_timeline(project_name):
    """Get complete timeline for a project"""
    try:
        timeline = results_manager.get_project_timeline(project_name)
        
        return jsonify({
            'status': 'success',
            'data': timeline
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@results_storage_bp.route('/api/results/re-evaluate', methods=['POST'])
def trigger_re_evaluation():
    """Trigger re-evaluation of documents"""
    try:
        data = request.get_json()
        
        required_fields = ['original_run_id', 'document_urls', 'change_reason', 'changed_by']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        new_run_id = results_manager.trigger_re_evaluation(
            original_run_id=data['original_run_id'],
            document_urls=data['document_urls'],
            validation_config=data.get('validation_config', {}),
            change_reason=data['change_reason'],
            changed_by=data['changed_by'],
            user_id=data.get('user_id', 'default')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Re-evaluation triggered successfully',
            'new_run_id': new_run_id
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@results_storage_bp.route('/api/results/analytics', methods=['GET'])
def get_trending_analytics():
    """Get trending analytics and metrics"""
    try:
        days = request.args.get('days', 30, type=int)
        
        analytics = results_manager.get_trending_analytics(days=days)
        
        return jsonify({
            'status': 'success',
            'data': analytics
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@results_storage_bp.route('/api/results/export', methods=['POST'])
def export_validation_data():
    """Export validation data"""
    try:
        data = request.get_json() or {}
        
        run_ids = data.get('run_ids')
        format_type = data.get('format', 'json')
        
        export_data = results_manager.export_validation_data(
            run_ids=run_ids,
            format=format_type
        )
        
        return jsonify({
            'status': 'success',
            'data': export_data
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@results_storage_bp.route('/api/results/start-run', methods=['POST'])
def start_validation_run():
    """Start a new validation run"""
    try:
        data = request.get_json()
        
        required_fields = ['document_urls', 'validation_config']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        run_id = results_manager.start_validation_run(
            document_urls=data['document_urls'],
            validation_config=data['validation_config'],
            user_id=data.get('user_id', 'default'),
            project_name=data.get('project_name', 'Unknown')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Validation run started',
            'run_id': run_id
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@results_storage_bp.route('/api/results/complete-run', methods=['POST'])
def complete_validation_run():
    """Complete a validation run with results"""
    try:
        data = request.get_json()
        
        required_fields = ['run_id', 'overall_score', 'status', 'results']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        results_manager.complete_validation_run(
            run_id=data['run_id'],
            overall_score=data['overall_score'],
            status=data['status'],
            results=data['results'],
            error_message=data.get('error_message')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Validation run completed successfully'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@results_storage_bp.route('/api/results/summary', methods=['GET'])
def get_results_summary():
    """Get summary of all validation results"""
    try:
        # Get recent history
        recent_runs = results_manager.get_validation_history(limit=10)
        
        # Get analytics
        analytics = results_manager.get_trending_analytics(days=30)
        
        # Calculate summary statistics
        total_runs = len(recent_runs)
        if total_runs > 0:
            avg_score = sum(run['overall_score'] for run in recent_runs if run['overall_score']) / total_runs
            latest_run = recent_runs[0] if recent_runs else None
            
            pass_count = len([run for run in recent_runs if run['status'] == 'PASS'])
            pass_rate = (pass_count / total_runs * 100) if total_runs > 0 else 0
        else:
            avg_score = 0
            latest_run = None
            pass_rate = 0
        
        summary = {
            'total_runs': total_runs,
            'average_score': avg_score,
            'pass_rate': pass_rate,
            'latest_run': latest_run,
            'analytics': analytics,
            'recent_runs': recent_runs[:5]  # Last 5 runs
        }
        
        return jsonify({
            'status': 'success',
            'data': summary
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

