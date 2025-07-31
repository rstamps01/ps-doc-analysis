"""
Analytics API Routes for Information Validation Tool

Provides REST API endpoints for:
- Trending analytics
- Performance metrics
- Advanced reporting
- Data visualization support
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import json
from typing import Dict, Any

# Import analytics engine
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.trending_engine import TrendingEngine

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Initialize trending engine
trending_engine = TrendingEngine()

@analytics_bp.route('/trends', methods=['GET'])
def get_validation_trends():
    """Get validation trends for specified time period"""
    try:
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        # Validate days parameter
        if days < 1 or days > 365:
            return jsonify({
                'error': 'Days parameter must be between 1 and 365'
            }), 400
        
        # Get trends analysis
        trends = trending_engine.analyze_validation_trends(days)
        
        return jsonify({
            'status': 'success',
            'data': trends,
            'metadata': {
                'analysis_period_days': days,
                'generated_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to analyze trends: {str(e)}'
        }), 500

@analytics_bp.route('/report', methods=['GET'])
def generate_analytics_report():
    """Generate comprehensive analytics report"""
    try:
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        format_type = request.args.get('format', 'json')
        
        # Generate report
        report = trending_engine.generate_analytics_report(days)
        
        if format_type == 'json':
            return jsonify({
                'status': 'success',
                'report': report
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Unsupported format: {format_type}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate report: {str(e)}'
        }), 500

@analytics_bp.route('/metrics/overview', methods=['GET'])
def get_overview_metrics():
    """Get high-level overview metrics"""
    try:
        days = request.args.get('days', 7, type=int)
        trends = trending_engine.analyze_validation_trends(days)
        
        overview = trends.get('overview', {})
        
        metrics = {
            'total_validations': overview.get('total_validations', 0),
            'average_score': round(overview.get('average_score', 0), 1),
            'score_trend': overview.get('score_trend', 'stable'),
            'average_processing_time': round(overview.get('average_processing_time', 0), 2),
            'score_distribution': overview.get('score_distribution', {}),
            'period_days': days
        }
        
        return jsonify({
            'status': 'success',
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get overview metrics: {str(e)}'
        }), 500

@analytics_bp.route('/metrics/categories', methods=['GET'])
def get_category_metrics():
    """Get metrics by validation category"""
    try:
        days = request.args.get('days', 30, type=int)
        trends = trending_engine.analyze_validation_trends(days)
        
        category_trends = trends.get('category_trends', {})
        
        return jsonify({
            'status': 'success',
            'category_metrics': category_trends,
            'period_days': days
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get category metrics: {str(e)}'
        }), 500

@analytics_bp.route('/metrics/failures', methods=['GET'])
def get_failure_patterns():
    """Get failure pattern analysis"""
    try:
        days = request.args.get('days', 30, type=int)
        trends = trending_engine.analyze_validation_trends(days)
        
        failure_patterns = trends.get('failure_patterns', {})
        
        return jsonify({
            'status': 'success',
            'failure_patterns': failure_patterns,
            'period_days': days
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get failure patterns: {str(e)}'
        }), 500

@analytics_bp.route('/metrics/performance', methods=['GET'])
def get_performance_metrics():
    """Get system performance metrics"""
    try:
        days = request.args.get('days', 30, type=int)
        trends = trending_engine.analyze_validation_trends(days)
        
        performance = trends.get('performance_metrics', {})
        
        return jsonify({
            'status': 'success',
            'performance_metrics': performance,
            'period_days': days
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get performance metrics: {str(e)}'
        }), 500

@analytics_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get actionable recommendations based on trends"""
    try:
        days = request.args.get('days', 30, type=int)
        priority = request.args.get('priority', None)
        
        trends = trending_engine.analyze_validation_trends(days)
        recommendations = trends.get('recommendations', [])
        
        # Filter by priority if specified
        if priority:
            recommendations = [
                rec for rec in recommendations 
                if rec.get('priority') == priority
            ]
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations,
            'total_count': len(recommendations)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get recommendations: {str(e)}'
        }), 500

@analytics_bp.route('/dashboard/data', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard data for visualization"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Get comprehensive trends
        trends = trending_engine.analyze_validation_trends(days)
        
        # Prepare dashboard data
        dashboard_data = {
            'summary_cards': {
                'total_validations': trends.get('overview', {}).get('total_validations', 0),
                'average_score': round(trends.get('overview', {}).get('average_score', 0), 1),
                'success_rate': round(trends.get('performance_metrics', {}).get('success_rate', 0), 1),
                'avg_processing_time': round(trends.get('performance_metrics', {}).get('average_processing_time', 0), 2)
            },
            'charts': {
                'score_distribution': trends.get('overview', {}).get('score_distribution', {}),
                'category_performance': trends.get('category_trends', {}),
                'failure_patterns': trends.get('failure_patterns', {}).get('most_common_failures', [])[:5],
                'daily_counts': trends.get('overview', {}).get('daily_validation_counts', {})
            },
            'trends': {
                'score_trend': trends.get('overview', {}).get('score_trend', 'stable'),
                'processing_time_trend': trends.get('performance_metrics', {}).get('processing_time_trend', 'stable'),
                'improvement_trends': trends.get('improvement_trends', {})
            },
            'recommendations': trends.get('recommendations', [])[:3]  # Top 3 recommendations
        }
        
        return jsonify({
            'status': 'success',
            'dashboard_data': dashboard_data,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get dashboard data: {str(e)}'
        }), 500

@analytics_bp.route('/export/trends', methods=['GET'])
def export_trends_data():
    """Export trends data for external analysis"""
    try:
        days = request.args.get('days', 30, type=int)
        format_type = request.args.get('format', 'json')
        
        trends = trending_engine.analyze_validation_trends(days)
        
        if format_type == 'json':
            return jsonify({
                'status': 'success',
                'export_data': trends,
                'export_metadata': {
                    'format': 'json',
                    'period_days': days,
                    'exported_at': datetime.now().isoformat()
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Export format {format_type} not yet supported'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to export trends data: {str(e)}'
        }), 500

@analytics_bp.route('/health', methods=['GET'])
def analytics_health():
    """Health check for analytics service"""
    try:
        # Test database connection
        test_trends = trending_engine.analyze_validation_trends(1)
        
        return jsonify({
            'status': 'healthy',
            'service': 'analytics',
            'database_connection': 'ok',
            'trending_engine': 'operational',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'analytics',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Error handlers
@analytics_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Analytics endpoint not found'
    }), 404

@analytics_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal analytics service error'
    }), 500

