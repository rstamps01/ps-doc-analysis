"""
Comprehensive Validation API Routes
Handles all validation operations with progress monitoring and results storage
"""

import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from validation.comprehensive_engine import ComprehensiveValidationEngine
from integrations.enhanced_google_sheets import EnhancedGoogleSheetsIntegration
from integrations.google_drive import GoogleDriveIntegration
import logging

logger = logging.getLogger(__name__)

comprehensive_validation_bp = Blueprint('comprehensive_validation', __name__)

# Global storage for validation results and progress
validation_results_store = {}
validation_progress_store = {}

@comprehensive_validation_bp.route('/api/validation/comprehensive/start', methods=['POST'])
def start_comprehensive_validation():
    """Start comprehensive validation of all documents"""
    try:
        data = request.get_json()
        
        # Generate unique validation ID
        validation_id = str(uuid.uuid4())
        
        # Extract document URLs from request (support both parameter naming conventions)
        evaluation_criteria_url = data.get('evaluation_criteria_url') or data.get('evaluation_criteria')
        site_survey_1_url = data.get('site_survey_1_url') or data.get('site_survey_part1_url')
        site_survey_2_url = data.get('site_survey_2_url') or data.get('site_survey_part2_url')
        install_plan_url = data.get('install_plan_url')
        
        # If no evaluation criteria URL provided, use default test data
        if not evaluation_criteria_url:
            evaluation_criteria_url = 'https://docs.google.com/spreadsheets/d/1MgJ77VGjvuphf45z_0LJ77zWlAslPEvJWOrTgrgsZb8/edit?usp=sharing'
        
        # Validate required URLs (only need the three main document URLs)
        if not all([site_survey_1_url, site_survey_2_url, install_plan_url]):
            return jsonify({
                'success': False,
                'error': 'Site Survey Part 1, Site Survey Part 2, and Install Plan URLs are required'
            }), 400
        
        # Initialize progress tracking
        validation_progress_store[validation_id] = {
            'status': 'Starting',
            'progress_percentage': 0,
            'current_step': 'Initializing validation',
            'start_time': datetime.now().isoformat(),
            'steps_completed': 0,
            'total_steps': 5  # Document extraction + validation
        }
        
        # Start validation process (this would typically be done asynchronously)
        try:
            result = _execute_comprehensive_validation(
                validation_id,
                evaluation_criteria_url,
                site_survey_1_url,
                site_survey_2_url,
                install_plan_url
            )
            
            # Store results
            validation_results_store[validation_id] = result
            
            return jsonify({
                'success': True,
                'validation_id': validation_id,
                'status': 'Completed',
                'result': result
            })
            
        except Exception as e:
            logger.error(f"Validation execution failed: {str(e)}")
            validation_progress_store[validation_id]['status'] = 'Failed'
            validation_progress_store[validation_id]['error'] = str(e)
            
            return jsonify({
                'success': False,
                'validation_id': validation_id,
                'error': str(e)
            }), 500
        
    except Exception as e:
        logger.error(f"Error starting comprehensive validation: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comprehensive_validation_bp.route('/api/validation/comprehensive/progress/<validation_id>', methods=['GET'])
def get_validation_progress(validation_id):
    """Get validation progress for a specific validation ID"""
    try:
        progress = validation_progress_store.get(validation_id)
        if not progress:
            return jsonify({
                'success': False,
                'error': 'Validation ID not found'
            }), 404
        
        return jsonify({
            'success': True,
            'validation_id': validation_id,
            'progress': progress
        })
        
    except Exception as e:
        logger.error(f"Error getting validation progress: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comprehensive_validation_bp.route('/api/validation/comprehensive/results/<validation_id>', methods=['GET'])
def get_validation_results(validation_id):
    """Get validation results for a specific validation ID"""
    try:
        results = validation_results_store.get(validation_id)
        if not results:
            return jsonify({
                'success': False,
                'error': 'Validation results not found'
            }), 404
        
        return jsonify({
            'success': True,
            'validation_id': validation_id,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error getting validation results: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comprehensive_validation_bp.route('/api/validation/comprehensive/list', methods=['GET'])
def list_validations():
    """List all validation sessions"""
    try:
        validations = []
        
        for validation_id in validation_results_store.keys():
            progress = validation_progress_store.get(validation_id, {})
            results = validation_results_store.get(validation_id, {})
            
            validations.append({
                'validation_id': validation_id,
                'status': progress.get('status', 'Unknown'),
                'start_time': progress.get('start_time'),
                'overall_score': results.get('overall_score', 0),
                'overall_status': results.get('overall_status', 'Unknown'),
                'checks_completed': results.get('checks_completed', 0),
                'total_checks': results.get('total_checks', 0)
            })
        
        return jsonify({
            'success': True,
            'validations': validations
        })
        
    except Exception as e:
        logger.error(f"Error listing validations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comprehensive_validation_bp.route('/api/validation/checks/info', methods=['GET'])
def get_validation_checks_info():
    """Get information about all validation checks"""
    try:
        engine = ComprehensiveValidationEngine()
        checks = engine.get_all_validation_checks()
        categories = engine.get_validation_categories()
        
        return jsonify({
            'success': True,
            'total_checks': len(checks),
            'categories': categories,
            'checks': checks
        })
        
    except Exception as e:
        logger.error(f"Error getting validation checks info: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comprehensive_validation_bp.route('/api/validation/test-data', methods=['POST'])
def validate_with_test_data():
    """Validate using the provided test data URLs"""
    try:
        # Use the provided test data URLs
        test_data = {
            'evaluation_criteria_url': 'https://docs.google.com/spreadsheets/d/1MgJ77VGjvuphf45z_0LJ77zWlAslPEvJWOrTgrgsZb8/edit?usp=sharing',
            'site_survey_1_url': 'https://docs.google.com/spreadsheets/d/1aQVhSNNmDJ0FXhejoXi84GHxD8iIyuIYuhld9lxTZPY/edit?usp=sharing',
            'site_survey_2_url': 'https://docs.google.com/spreadsheets/d/1p2X4Pvleis2s0pgQ1FRpf-o2e4LsgfOA0LxlmLVxH_k/edit?usp=sharing',
            'install_plan_url': 'https://drive.google.com/file/d/1ez3eMHrKXKJJBXMgJLnj3RQcENZQZgkm/view?usp=sharing'
        }
        
        # Generate validation ID
        validation_id = str(uuid.uuid4())
        
        # Execute validation
        result = _execute_comprehensive_validation(
            validation_id,
            test_data['evaluation_criteria_url'],
            test_data['site_survey_1_url'],
            test_data['site_survey_2_url'],
            test_data['install_plan_url']
        )
        
        # Store results
        validation_results_store[validation_id] = result
        
        return jsonify({
            'success': True,
            'validation_id': validation_id,
            'test_data_used': test_data,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error validating with test data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _execute_comprehensive_validation(validation_id, eval_criteria_url, site_survey_1_url, site_survey_2_url, install_plan_url):
    """Execute the comprehensive validation process"""
    
    def update_progress(step, total_steps, message):
        progress = (step / total_steps) * 100
        validation_progress_store[validation_id].update({
            'progress_percentage': progress,
            'current_step': message,
            'steps_completed': step,
            'total_steps': total_steps
        })
    
    try:
        # Initialize integrations
        sheets_integration = EnhancedGoogleSheetsIntegration()
        drive_integration = GoogleDriveIntegration()
        validation_engine = ComprehensiveValidationEngine()
        
        # Set up progress callback for validation engine
        def validation_progress_callback(progress_data):
            validation_progress_store[validation_id].update({
                'validation_progress': progress_data
            })
        
        validation_engine.set_progress_callback(validation_progress_callback)
        
        # Step 1: Extract evaluation criteria
        update_progress(1, 5, "Extracting evaluation criteria from Google Sheets")
        eval_criteria_result = sheets_integration.extract_evaluation_criteria(eval_criteria_url)
        if not eval_criteria_result['success']:
            raise Exception(f"Failed to extract evaluation criteria: {eval_criteria_result['error']}")
        
        # Step 2: Extract Site Survey Part 1
        update_progress(2, 5, "Extracting Site Survey Part 1 data")
        site_survey_1_result = sheets_integration.extract_site_survey_data(site_survey_1_url, 1)
        if not site_survey_1_result['success']:
            raise Exception(f"Failed to extract Site Survey Part 1: {site_survey_1_result['error']}")
        
        # Step 3: Extract Site Survey Part 2
        update_progress(3, 5, "Extracting Site Survey Part 2 data")
        site_survey_2_result = sheets_integration.extract_site_survey_data(site_survey_2_url, 2)
        if not site_survey_2_result['success']:
            raise Exception(f"Failed to extract Site Survey Part 2: {site_survey_2_result['error']}")
        
        # Step 4: Extract Install Plan
        update_progress(4, 5, "Extracting Install Plan document")
        install_plan_result = drive_integration.process_document_from_url(install_plan_url)
        if not install_plan_result['success']:
            raise Exception(f"Failed to extract Install Plan: {install_plan_result['error']}")
        
        # Step 5: Execute comprehensive validation
        update_progress(5, 5, "Executing comprehensive validation")
        
        # Prepare documents for validation
        documents = {
            'evaluation_criteria': eval_criteria_result['data'],
            'site_survey_1': site_survey_1_result['data'],
            'site_survey_2': site_survey_2_result['data'],
            'install_plan': install_plan_result['data']
        }
        
        # Execute validation
        validation_results = validation_engine.validate_all_documents(documents)
        
        # Update final progress
        validation_progress_store[validation_id].update({
            'status': 'Completed',
            'progress_percentage': 100,
            'current_step': 'Validation completed',
            'end_time': datetime.now().isoformat()
        })
        
        # Add document metadata to results
        validation_results['document_metadata'] = {
            'evaluation_criteria': eval_criteria_result.get('metadata', {}),
            'site_survey_1': site_survey_1_result.get('metadata', {}),
            'site_survey_2': site_survey_2_result.get('metadata', {}),
            'install_plan': install_plan_result.get('metadata', {})
        }
        
        return validation_results
        
    except Exception as e:
        validation_progress_store[validation_id].update({
            'status': 'Failed',
            'error': str(e),
            'end_time': datetime.now().isoformat()
        })
        raise

@comprehensive_validation_bp.route('/api/validation/comprehensive/export/<validation_id>', methods=['GET'])
def export_validation_results(validation_id):
    """Export validation results in various formats"""
    try:
        results = validation_results_store.get(validation_id)
        if not results:
            return jsonify({
                'success': False,
                'error': 'Validation results not found'
            }), 404
        
        export_format = request.args.get('format', 'json').lower()
        
        if export_format == 'json':
            return jsonify({
                'success': True,
                'validation_id': validation_id,
                'export_format': 'json',
                'data': results
            })
        elif export_format == 'summary':
            # Create a summary report
            summary = {
                'validation_id': validation_id,
                'overall_status': results.get('overall_status'),
                'overall_score': results.get('overall_score'),
                'total_checks': results.get('total_checks'),
                'checks_passed': results.get('checks_passed'),
                'checks_failed': results.get('checks_failed'),
                'category_scores': results.get('category_scores', {}),
                'critical_issues_count': len(results.get('critical_issues', [])),
                'warnings_count': len(results.get('warnings', [])),
                'recommendations_count': len(results.get('recommendations', []))
            }
            
            return jsonify({
                'success': True,
                'validation_id': validation_id,
                'export_format': 'summary',
                'data': summary
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported export format: {export_format}'
            }), 400
        
    except Exception as e:
        logger.error(f"Error exporting validation results: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

