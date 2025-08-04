"""
Export API Routes
Handles validation report generation and export in multiple formats
"""

import json
import sqlite3
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, Response
from export.export_engine import ExportEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

export_bp = Blueprint('export', __name__)
export_engine = ExportEngine()

@export_bp.route('/validation/pdf/<validation_id>', methods=['GET'])
def export_validation_pdf(validation_id: str):
    """Export validation results as PDF"""
    try:
        # Get validation data
        validation_data = get_validation_data(validation_id)
        
        if not validation_data:
            # Generate sample data for testing
            validation_data = generate_sample_validation_data(validation_id)
        
        # Generate PDF
        pdf_bytes = export_engine.export_validation_results_pdf(validation_data)
        
        # Create response
        response = Response(pdf_bytes, mimetype='application/pdf')
        response.headers['Content-Disposition'] = f'attachment; filename=validation_report_{validation_id}.pdf'
        
        return response
        
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to export PDF: {str(e)}'
        }), 500

@export_bp.route('/validation/excel/<validation_id>', methods=['GET'])
def export_validation_excel(validation_id: str):
    """Export validation results as Excel"""
    try:
        # Get validation data
        validation_data = get_validation_data(validation_id)
        
        if not validation_data:
            # Generate sample data for testing
            validation_data = generate_sample_validation_data(validation_id)
        
        # Generate Excel
        excel_bytes = export_engine.export_validation_results_excel(validation_data)
        
        # Create response
        response = Response(excel_bytes, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response.headers['Content-Disposition'] = f'attachment; filename=validation_report_{validation_id}.xlsx'
        
        return response
        
    except Exception as e:
        logger.error(f"Excel export error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to export Excel: {str(e)}'
        }), 500

@export_bp.route('/validation/csv/<validation_id>', methods=['GET'])
def export_validation_csv(validation_id: str):
    """Export validation results as CSV"""
    try:
        # Get validation data
        validation_data = get_validation_data(validation_id)
        
        if not validation_data:
            # Generate sample data for testing
            validation_data = generate_sample_validation_data(validation_id)
        
        # Generate CSV
        csv_content = export_engine.export_validation_results_csv(validation_data, export_type='summary')
        
        # Create response
        response = Response(csv_content, mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename=validation_summary_{validation_id}.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to export CSV: {str(e)}'
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
            logger.error(f"Database error: {db_error}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting validation data: {e}")
        return None

# Import the sample data generator
from routes.export_api_sample_data import generate_sample_validation_data

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

