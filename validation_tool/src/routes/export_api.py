"""
Export API Routes for Information Validation Tool

Provides REST API endpoints for:
- PDF report generation
- Excel workbook exports
- CSV data exports
- Custom report templates
"""

from flask import Blueprint, jsonify, request, send_file, make_response
from datetime import datetime
import json
import sqlite3
from typing import Dict, Any
import io

# Import export engine
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export.export_engine import ExportEngine

# Create blueprint
export_bp = Blueprint('export', __name__, url_prefix='/api/export')

# Initialize export engine
export_engine = ExportEngine()

@export_bp.route('/validation/pdf/<validation_id>', methods=['GET'])
def export_validation_pdf(validation_id: str):
    """Export specific validation results as PDF"""
    try:
        # Get validation data from database
        validation_data = get_validation_data(validation_id)
        
        if not validation_data:
            return jsonify({
                'status': 'error',
                'message': f'Validation {validation_id} not found'
            }), 404
        
        # Generate PDF
        pdf_bytes = export_engine.export_validation_results_pdf(validation_data)
        
        # Create response
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=validation_report_{validation_id}.pdf'
        
        return response
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to export PDF: {str(e)}'
        }), 500

@export_bp.route('/validation/excel/<validation_id>', methods=['GET'])
def export_validation_excel(validation_id: str):
    """Export specific validation results as Excel workbook"""
    try:
        # Get validation data from database
        validation_data = get_validation_data(validation_id)
        
        if not validation_data:
            return jsonify({
                'status': 'error',
                'message': f'Validation {validation_id} not found'
            }), 404
        
        # Generate Excel
        excel_bytes = export_engine.export_validation_results_excel(validation_data)
        
        # Create response
        response = make_response(excel_bytes)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=validation_results_{validation_id}.xlsx'
        
        return response
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to export Excel: {str(e)}'
        }), 500

@export_bp.route('/validation/csv/<validation_id>', methods=['GET'])
def export_validation_csv(validation_id: str):
    """Export specific validation results as CSV"""
    try:
        # Get query parameters
        export_type = request.args.get('type', 'summary')  # summary, categories, issues
        
        # Get validation data from database
        validation_data = get_validation_data(validation_id)
        
        if not validation_data:
            return jsonify({
                'status': 'error',
                'message': f'Validation {validation_id} not found'
            }), 404
        
        # Generate CSV
        csv_content = export_engine.export_validation_results_csv(validation_data, export_type)
        
        # Create response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=validation_{export_type}_{validation_id}.csv'
        
        return response
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to export CSV: {str(e)}'
        }), 500

@export_bp.route('/trends/pdf', methods=['GET'])
def export_trends_pdf():
    """Export trends analysis as PDF report"""
    try:
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        # Get trends data (would normally come from analytics engine)
        trends_data = get_trends_data(days)
        
        # Generate PDF
        pdf_bytes = export_engine.create_trends_report_pdf(trends_data)
        
        # Create response
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=trends_report_{days}days.pdf'
        
        return response
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to export trends PDF: {str(e)}'
        }), 500

@export_bp.route('/batch/validations', methods=['POST'])
def export_batch_validations():
    """Export multiple validation results in batch"""
    try:
        data = request.get_json()
        
        if not data or 'validation_ids' not in data:
            return jsonify({
                'status': 'error',
                'message': 'validation_ids required in request body'
            }), 400
        
        validation_ids = data['validation_ids']
        export_format = data.get('format', 'pdf')  # pdf, excel, csv
        
        if not validation_ids:
            return jsonify({
                'status': 'error',
                'message': 'At least one validation_id required'
            }), 400
        
        # Get all validation data
        batch_data = []
        for validation_id in validation_ids:
            validation_data = get_validation_data(validation_id)
            if validation_data:
                batch_data.append(validation_data)
        
        if not batch_data:
            return jsonify({
                'status': 'error',
                'message': 'No valid validation data found'
            }), 404
        
        # Create batch export based on format
        if export_format == 'pdf':
            # Combine all validations into single PDF
            combined_data = combine_validation_data(batch_data)
            export_bytes = export_engine.export_validation_results_pdf(combined_data)
            content_type = 'application/pdf'
            filename = f'batch_validation_report_{len(validation_ids)}_validations.pdf'
            
        elif export_format == 'excel':
            # Create Excel with multiple sheets
            combined_data = combine_validation_data(batch_data)
            export_bytes = export_engine.export_validation_results_excel(combined_data)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'batch_validation_results_{len(validation_ids)}_validations.xlsx'
            
        else:
            return jsonify({
                'status': 'error',
                'message': f'Unsupported export format: {export_format}'
            }), 400
        
        # Create response
        response = make_response(export_bytes)
        response.headers['Content-Type'] = content_type
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to export batch: {str(e)}'
        }), 500

@export_bp.route('/template/custom', methods=['POST'])
def export_custom_template():
    """Export validation results using custom template"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body required'
            }), 400
        
        validation_id = data.get('validation_id')
        template_config = data.get('template_config', {})
        export_format = data.get('format', 'pdf')
        
        if not validation_id:
            return jsonify({
                'status': 'error',
                'message': 'validation_id required'
            }), 400
        
        # Get validation data
        validation_data = get_validation_data(validation_id)
        
        if not validation_data:
            return jsonify({
                'status': 'error',
                'message': f'Validation {validation_id} not found'
            }), 404
        
        # Apply custom template configuration
        customized_data = apply_template_config(validation_data, template_config)
        
        # Generate export based on format
        if export_format == 'pdf':
            export_bytes = export_engine.export_validation_results_pdf(customized_data)
            content_type = 'application/pdf'
            filename = f'custom_validation_report_{validation_id}.pdf'
            
        elif export_format == 'excel':
            export_bytes = export_engine.export_validation_results_excel(customized_data)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'custom_validation_results_{validation_id}.xlsx'
            
        else:
            return jsonify({
                'status': 'error',
                'message': f'Unsupported export format: {export_format}'
            }), 400
        
        # Create response
        response = make_response(export_bytes)
        response.headers['Content-Type'] = content_type
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to export custom template: {str(e)}'
        }), 500

@export_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """Get list of supported export formats"""
    return jsonify({
        'status': 'success',
        'supported_formats': {
            'pdf': {
                'description': 'Portable Document Format with charts and formatting',
                'mime_type': 'application/pdf',
                'features': ['charts', 'formatting', 'images', 'tables']
            },
            'excel': {
                'description': 'Excel workbook with multiple sheets',
                'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'features': ['multiple_sheets', 'charts', 'formatting', 'formulas']
            },
            'csv': {
                'description': 'Comma-separated values for data analysis',
                'mime_type': 'text/csv',
                'features': ['data_export', 'analysis_ready', 'lightweight'],
                'types': ['summary', 'categories', 'issues']
            }
        }
    })

@export_bp.route('/api/health', methods=['GET'])
def export_health():
    """Health check for export service"""
    try:
        # Test export engine
        test_data = {
            'overall_score': 85.0,
            'total_checks': 10,
            'passed_checks': 8,
            'failed_checks': 2
        }
        
        # Test PDF generation
        pdf_test = export_engine.export_validation_results_pdf(test_data)
        
        return jsonify({
            'status': 'healthy',
            'service': 'export',
            'pdf_generation': 'ok' if pdf_test else 'error',
            'excel_generation': 'ok',
            'csv_generation': 'ok',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'export',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Helper functions
def get_validation_data(validation_id: str) -> Dict[str, Any]:
    """Get validation data from database"""
    try:
        conn = sqlite3.connect('src/validation_results.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM validation_results WHERE id = ?
        ''', (validation_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Parse the stored JSON data
            validation_data = json.loads(result[3]) if result[3] else {}
            
            # Add metadata
            validation_data.update({
                'validation_id': result[0],
                'document_urls': json.loads(result[1]) if result[1] else {},
                'configuration': json.loads(result[2]) if result[2] else {},
                'created_at': result[5]
            })
            
            return validation_data
        
        return None
        
    except Exception as e:
        print(f"Error getting validation data: {e}")
        return None

def get_trends_data(days: int) -> Dict[str, Any]:
    """Get trends data for export (placeholder)"""
    # This would normally use the TrendingEngine
    return {
        'period_days': days,
        'overview': {
            'total_validations': 25,
            'average_score': 82.5,
            'score_trend': 'increasing'
        },
        'category_trends': {
            'document_completeness': {
                'average_score': 85.0,
                'pass_rate': 90.0,
                'score_trend': 'stable'
            },
            'technical_validation': {
                'average_score': 78.0,
                'pass_rate': 85.0,
                'score_trend': 'increasing'
            }
        },
        'recommendations': [
            {
                'title': 'Improve Document Completeness',
                'priority': 'high',
                'description': 'Focus on completing all required sections'
            }
        ]
    }

def combine_validation_data(batch_data: list) -> Dict[str, Any]:
    """Combine multiple validation results into single dataset"""
    if not batch_data:
        return {}
    
    # Calculate combined metrics
    total_validations = len(batch_data)
    total_score = sum(data.get('overall_score', 0) for data in batch_data)
    average_score = total_score / total_validations if total_validations > 0 else 0
    
    # Combine all issues
    all_issues = []
    for data in batch_data:
        if 'issues' in data:
            all_issues.extend(data['issues'])
    
    # Combine all recommendations
    all_recommendations = []
    for data in batch_data:
        if 'recommendations' in data:
            all_recommendations.extend(data['recommendations'])
    
    return {
        'overall_score': average_score,
        'total_checks': sum(data.get('total_checks', 0) for data in batch_data),
        'passed_checks': sum(data.get('passed_checks', 0) for data in batch_data),
        'failed_checks': sum(data.get('failed_checks', 0) for data in batch_data),
        'batch_size': total_validations,
        'issues': all_issues,
        'recommendations': all_recommendations,
        'category_results': combine_category_results(batch_data)
    }

def combine_category_results(batch_data: list) -> Dict[str, Any]:
    """Combine category results from multiple validations"""
    combined_categories = {}
    
    for data in batch_data:
        if 'category_results' in data:
            for category, results in data['category_results'].items():
                if category not in combined_categories:
                    combined_categories[category] = {
                        'scores': [],
                        'statuses': [],
                        'issues': []
                    }
                
                combined_categories[category]['scores'].append(results.get('score', 0))
                combined_categories[category]['statuses'].append(results.get('status', 'unknown'))
                combined_categories[category]['issues'].extend(results.get('issues', []))
    
    # Calculate averages
    final_categories = {}
    for category, data in combined_categories.items():
        avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
        pass_count = sum(1 for status in data['statuses'] if status == 'pass')
        pass_rate = (pass_count / len(data['statuses'])) * 100 if data['statuses'] else 0
        
        final_categories[category] = {
            'score': avg_score,
            'pass_rate': pass_rate,
            'status': 'pass' if pass_rate >= 80 else 'fail',
            'issues': data['issues']
        }
    
    return final_categories

def apply_template_config(validation_data: Dict[str, Any], 
                         template_config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply custom template configuration to validation data"""
    customized_data = validation_data.copy()
    
    # Apply filters based on template config
    if 'include_sections' in template_config:
        sections = template_config['include_sections']
        
        # Filter categories
        if 'categories' in sections and 'category_results' in customized_data:
            filtered_categories = {}
            for category in sections['categories']:
                if category in customized_data['category_results']:
                    filtered_categories[category] = customized_data['category_results'][category]
            customized_data['category_results'] = filtered_categories
        
        # Filter issues by severity
        if 'min_severity' in template_config and 'issues' in customized_data:
            severity_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            min_level = severity_order.get(template_config['min_severity'], 1)
            
            filtered_issues = [
                issue for issue in customized_data['issues']
                if severity_order.get(issue.get('severity', 'medium'), 2) >= min_level
            ]
            customized_data['issues'] = filtered_issues
    
    return customized_data

# Error handlers
@export_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Export endpoint not found'
    }), 404

@export_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal export service error'
    }), 500


@export_bp.route('/validation/pdf/demo', methods=['GET'])
def export_demo_pdf():
    """Export demo validation results as PDF for testing"""
    try:
        # Create demo validation data
        demo_data = {
            'validation_id': 'demo',
            'overall_score': 85.2,
            'total_checks': 50,
            'passed_checks': 43,
            'failed_checks': 3,
            'warning_checks': 4,
            'document_urls': {
                'site_survey': 'https://docs.google.com/spreadsheets/d/demo_site_survey',
                'install_plan': 'https://docs.google.com/spreadsheets/d/demo_install_plan'
            },
            'configuration': {
                'pass_threshold': 80,
                'warning_threshold': 60
            },
            'category_results': {
                'document_completeness': {
                    'score': 90.0,
                    'status': 'pass',
                    'issues': []
                },
                'technical_validation': {
                    'score': 85.0,
                    'status': 'pass',
                    'issues': ['Minor formatting inconsistency in section 3']
                },
                'data_consistency': {
                    'score': 78.0,
                    'status': 'warning',
                    'issues': ['Some cross-references need verification']
                },
                'compliance_check': {
                    'score': 88.0,
                    'status': 'pass',
                    'issues': []
                }
            },
            'issues': [
                {
                    'category': 'technical_validation',
                    'severity': 'minor',
                    'description': 'Minor formatting inconsistency in section 3',
                    'recommendation': 'Review and standardize formatting'
                },
                {
                    'category': 'data_consistency',
                    'severity': 'warning',
                    'description': 'Some cross-references need verification',
                    'recommendation': 'Verify all cross-document references'
                }
            ],
            'recommendations': [
                {
                    'title': 'Improve Data Consistency',
                    'priority': 'medium',
                    'description': 'Review cross-document references for accuracy'
                },
                {
                    'title': 'Standardize Formatting',
                    'priority': 'low',
                    'description': 'Apply consistent formatting across all sections'
                }
            ],
            'created_at': datetime.now().isoformat(),
            'processing_time': 2.3
        }
        
        # Generate PDF
        pdf_bytes = export_engine.export_validation_results_pdf(demo_data)
        
        # Create response
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=demo_validation_report.pdf'
        
        return response
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to export demo PDF: {str(e)}'
        }), 500

@export_bp.route('/validation/excel/demo', methods=['GET'])
def export_demo_excel():
    """Export demo validation results as Excel for testing"""
    try:
        # Use the same demo data as PDF
        demo_data = {
            'validation_id': 'demo',
            'overall_score': 85.2,
            'total_checks': 50,
            'passed_checks': 43,
            'failed_checks': 3,
            'warning_checks': 4,
            'category_results': {
                'document_completeness': {'score': 90.0, 'status': 'pass'},
                'technical_validation': {'score': 85.0, 'status': 'pass'},
                'data_consistency': {'score': 78.0, 'status': 'warning'},
                'compliance_check': {'score': 88.0, 'status': 'pass'}
            },
            'created_at': datetime.now().isoformat()
        }
        
        # Generate Excel
        excel_bytes = export_engine.export_validation_results_excel(demo_data)
        
        # Create response
        response = make_response(excel_bytes)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=demo_validation_results.xlsx'
        
        return response
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to export demo Excel: {str(e)}'
        }), 500

@export_bp.route('/validation/csv/demo', methods=['GET'])
def export_demo_csv():
    """Export demo validation results as CSV for testing"""
    try:
        # Get export type from query parameters
        export_type = request.args.get('type', 'summary')
        
        # Create demo data
        demo_data = {
            'validation_id': 'demo',
            'overall_score': 85.2,
            'total_checks': 50,
            'passed_checks': 43,
            'failed_checks': 3,
            'warning_checks': 4,
            'category_results': {
                'document_completeness': {'score': 90.0, 'status': 'pass'},
                'technical_validation': {'score': 85.0, 'status': 'pass'},
                'data_consistency': {'score': 78.0, 'status': 'warning'},
                'compliance_check': {'score': 88.0, 'status': 'pass'}
            }
        }
        
        # Generate CSV
        csv_content = export_engine.export_validation_results_csv(demo_data, export_type)
        
        # Create response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=demo_validation_{export_type}.csv'
        
        return response
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to export demo CSV: {str(e)}'
        }), 500

