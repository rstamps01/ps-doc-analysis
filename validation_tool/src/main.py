#!/usr/bin/env python3
"""
Information Validation Tool - API Only Backend
Enhanced validation system for Site Survey and Install Plan documents
"""

import os
import sys
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app - API only, no static files
app = Flask(__name__)

# Enable CORS for all routes with comprehensive configuration
CORS(app, 
     origins=['*'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'Accept'],
     supports_credentials=False)

# Root API endpoint with description and status
@app.route('/', methods=['GET'])
def api_root():
    """Root API endpoint with description and status"""
    from datetime import datetime
    return jsonify({
        'service': 'Enhanced Information Validation Tool API',
        'description': 'REST API for automated validation of Site Survey and Install Plan documents',
        'version': '2.0.1',
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'health': '/api/health',
            'validation': '/api/validation/comprehensive/start',
            'google_integration': '/api/google/credentials/status',
            'analytics': '/api/analytics/dashboard/data',
            'export': '/api/export/validation/pdf/<validation_id>'
        },
        'documentation': 'https://github.com/rstamps01/ps-doc-analysis',
        'support': 'Enhanced validation system for VAST Data deployment documentation'
    })

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return jsonify({
        'service': 'Information Validation Tool Enhanced',
        'status': 'healthy',
        'version': '2.0.1',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'operational'
    })

# Register blueprints with error handling
try:
    from routes.comprehensive_validation import comprehensive_validation_bp
    app.register_blueprint(comprehensive_validation_bp)
    logger.info("Real comprehensive validation blueprint registered")
except ImportError as e:
    logger.error(f"Could not import comprehensive validation blueprint: {e}")
    logger.error("Comprehensive validation functionality will not be available")

try:
    from routes.google_integration import google_integration
    from routes.api_key_validation import api_key_validation_bp
    app.register_blueprint(google_integration)
    app.register_blueprint(api_key_validation_bp)
    logger.info("Google integration and API key validation blueprints registered")
except ImportError as e:
    logger.warning(f"Could not import google integration blueprints: {e}")

try:
    from routes.settings import settings_bp
    app.register_blueprint(settings_bp)
    logger.info("Settings blueprint registered")
except ImportError as e:
    logger.warning(f"Could not import settings blueprint: {e}")

try:
    from routes.results_storage import results_storage_bp
    app.register_blueprint(results_storage_bp)
    logger.info("Results storage blueprint registered")
except ImportError as e:
    logger.warning(f"Could not import results storage blueprint: {e}")

try:
    from routes.workflow_management import workflow_management_bp
    app.register_blueprint(workflow_management_bp)
    logger.info("Workflow management blueprint registered")
except ImportError as e:
    logger.warning(f"Could not import workflow management blueprint: {e}")

# Register analytics blueprint
try:
    from routes.analytics_api import analytics_bp
    app.register_blueprint(analytics_bp)
    logger.info("Analytics API blueprint registered")
except ImportError as e:
    logger.warning(f"Could not import analytics blueprint: {e}")

# Register export blueprint
try:
    from routes.export_api import export_bp
    app.register_blueprint(export_bp)
    logger.info("Export API blueprint registered")
except ImportError as e:
    logger.warning(f"Could not import export blueprint: {e}")

# Register real data blueprint
try:
    from routes.real_data_api import real_data_bp
    app.register_blueprint(real_data_bp)
    logger.info("Real data API blueprint registered")
except ImportError as e:
    logger.warning(f"Could not import real data blueprint: {e}")

# Register metrics collector blueprint
try:
    from routes.metrics_collector import metrics_collector_bp
    app.register_blueprint(metrics_collector_bp)
    logger.info("Metrics collector blueprint registered")
except ImportError as e:
    logger.warning(f"Could not import metrics collector blueprint: {e}")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Information Validation Tool API Server...")
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)

