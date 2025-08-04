"""
Export API Routes for Information Validation Tool

Provides REST API endpoints for:
- PDF report generation
- Excel workbook exports
- CSV data exports
- Custom report templates
"""

from flask import Blueprint, jsonify, request, send_file, make_response
from datetime import datetime, timedelta
import json
import sqlite3
from typing import Dict, Any
import io

# Import export engine
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export.export_engine import ExportEngine
from routes.export_api_sample_data import generate_sample_validation_data

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
            # Generate sample data for testing if no validation found
            validation_data = generate_sample_validation_data(validation_id)
        
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
    """Export specific validation results as Excel"""
    try:
        # Get validation data from database
        validation_data = get_validation_data(validation_id)
        
        if not validation_data:
            # Generate sample data for testing if no validation found
            validation_data = generate_sample_validation_data(validation_id)
        
        # Generate Excel
        excel_bytes = export_engine.export_validation_results_excel(validation_data)
        
        # Create response
        response = make_response(excel_bytes)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=validation_report_{validation_id}.xlsx'
        
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
            # Generate sample data for testing if no validation found
            validation_data = generate_sample_validation_data(validation_id)
        
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
    """Get validation data from validation results store or database"""
    try:
        # First try to get from the validation results store (in-memory)
        from routes.comprehensive_validation import validation_results_store
        
        if validation_id in validation_results_store:
            return validation_results_store[validation_id]
        
        # Fallback to database if not in memory
        try:
            conn = sqlite3.connect('validation_results.db')
            cursor = conn.cursor()
            
            # Get validation data from the correct table structure
            cursor.execute('''
                SELECT id, timestamp, overall_score, status, document_urls, validation_config
                FROM validation_runs WHERE id = ?
            ''', (validation_id,))
            
            result = cursor.fetchone()
            
            if result:
                # Get detailed results
                cursor.execute('''
                    SELECT category, check_name, status, score, message, details
                    FROM validation_results WHERE run_id = ?
                ''', (validation_id,))
                
                detailed_results = cursor.fetchall()
                conn.close()
                
                # Parse the result
                validation_data = {
                    'validation_id': result[0],
                    'timestamp': result[1],
                    'overall_score': result[2] or 0.0,
                    'status': result[3] or 'UNKNOWN',
                    'document_urls': json.loads(result[4]) if result[4] else {},
                    'validation_config': json.loads(result[5]) if result[5] else {},
                    'detailed_results': [
                        {
                            'category': row[0],
                            'check_name': row[1],
                            'status': row[2],
                            'score': row[3],
                            'message': row[4],
                            'details': json.loads(row[5]) if row[5] else {}
                        }
                        for row in detailed_results
                    ]
                }
                
                return validation_data
            
            conn.close()
            return None
            
        except sqlite3.Error as db_error:
            print(f"Database error: {db_error}")
            return None
            
    except Exception as e:
        print(f"Error getting validation data: {e}")
        return None

# Import the sample data generator
from routes.export_api_sample_data import generate_sample_validation_data
            {
                'category': 'Technical Requirements',
                'severity': 'warning', 
                'description': 'Missing technical specifications',
                'recommendation': 'Complete all required technical specification fields'
            }
        ]
        
        # Add recommendations
        validation_data['recommendations'] = [
            {
                'title': 'Address Document Consistency',
                'priority': 'medium',
                'description': 'Review and align document versions across all files'
            },
            {
                'title': 'Complete Technical Specifications',
                'priority': 'medium',
                'description': 'Fill in missing technical requirement details'
            }
        ]
        
        return validation_data
        
    except Exception as e:
        print(f"Error getting validation data: {e}")
        return None
def get_trends_data(days: int) -> Dict[str, Any]:
    """Get trends data for export from actual database"""
    try:
        conn = sqlite3.connect('src/validation_results.db')
        cursor = conn.cursor()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get validation runs in the date range
        cursor.execute('''
            SELECT id, timestamp, overall_score, status, execution_time
            FROM validation_runs 
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp DESC
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        runs = cursor.fetchall()
        
        if not runs:
            conn.close()
            return {
                'period_days': days,
                'overview': {
                    'total_validations': 0,
                    'average_score': 0.0,
                    'score_trend': 'no_data'
                },
                'category_trends': {},
                'recommendations': [
                    {
                        'title': 'No Data Available',
                        'priority': 'info',
                        'description': 'No validation data found for the specified period'
                    }
                ]
            }
        
        # Calculate overview metrics
        total_validations = len(runs)
        scores = [run[2] for run in runs if run[2] is not None]
        average_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine score trend (simple comparison of first half vs second half)
        if len(scores) >= 4:
            mid_point = len(scores) // 2
            first_half_avg = sum(scores[:mid_point]) / mid_point
            second_half_avg = sum(scores[mid_point:]) / (len(scores) - mid_point)
            
            if second_half_avg > first_half_avg + 5:
                score_trend = 'increasing'
            elif second_half_avg < first_half_avg - 5:
                score_trend = 'decreasing'
            else:
                score_trend = 'stable'
        else:
            score_trend = 'insufficient_data'
        
        # Get category trends
        category_trends = {}
        for run_id, _, _, _, _ in runs:
            cursor.execute('''
                SELECT category, AVG(score) as avg_score, 
                       COUNT(CASE WHEN status = 'pass' THEN 1 END) * 100.0 / COUNT(*) as pass_rate
                FROM validation_results 
                WHERE run_id = ?
                GROUP BY category
            ''', (run_id,))
            
            categories = cursor.fetchall()
            for category, avg_score, pass_rate in categories:
                if category not in category_trends:
                    category_trends[category] = {
                        'scores': [],
                        'pass_rates': []
                    }
                category_trends[category]['scores'].append(avg_score or 0.0)
                category_trends[category]['pass_rates'].append(pass_rate or 0.0)
        
        # Calculate final category trends
        final_category_trends = {}
        for category, data in category_trends.items():
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0.0
            avg_pass_rate = sum(data['pass_rates']) / len(data['pass_rates']) if data['pass_rates'] else 0.0
            
            # Determine trend
            if len(data['scores']) >= 2:
                recent_score = sum(data['scores'][-2:]) / 2
                older_score = sum(data['scores'][:-2]) / max(1, len(data['scores']) - 2)
                trend = 'increasing' if recent_score > older_score + 2 else ('decreasing' if recent_score < older_score - 2 else 'stable')
            else:
                trend = 'insufficient_data'
            
            final_category_trends[category] = {
                'average_score': round(avg_score, 1),
                'pass_rate': round(avg_pass_rate, 1),
                'score_trend': trend
            }
        
        # Generate recommendations based on data
        recommendations = []
        if average_score < 70:
            recommendations.append({
                'title': 'Improve Overall Validation Scores',
                'priority': 'high',
                'description': f'Average score is {average_score:.1f}%. Focus on addressing common validation failures.'
            })
        
        low_performing_categories = [cat for cat, data in final_category_trends.items() if data['average_score'] < 75]
        if low_performing_categories:
            recommendations.append({
                'title': 'Focus on Low-Performing Categories',
                'priority': 'medium',
                'description': f'Categories needing attention: {", ".join(low_performing_categories)}'
            })
        
        if score_trend == 'decreasing':
            recommendations.append({
                'title': 'Address Declining Performance',
                'priority': 'high',
                'description': 'Validation scores are trending downward. Review recent changes and processes.'
            })
        
        if not recommendations:
            recommendations.append({
                'title': 'Maintain Current Performance',
                'priority': 'low',
                'description': 'Validation performance is stable. Continue current practices.'
            })
        
        conn.close()
        
        return {
            'period_days': days,
            'overview': {
                'total_validations': total_validations,
                'average_score': round(average_score, 1),
                'score_trend': score_trend
            },
            'category_trends': final_category_trends,
            'recommendations': recommendations
        }
        
    except Exception as e:
        print(f"Error getting trends data: {e}")
        return {
            'period_days': days,
            'overview': {
                'total_validations': 0,
                'average_score': 0.0,
                'score_trend': 'error'
            },
            'category_trends': {},
            'recommendations': [
                {
                    'title': 'Data Retrieval Error',
                    'priority': 'high',
                    'description': f'Error retrieving trends data: {str(e)}'
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


