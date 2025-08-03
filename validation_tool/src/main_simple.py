#!/usr/bin/env python3
import os
import sys
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.validation import validation_bp
from src.routes.notifications import notifications_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for all routes
CORS(app)

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(validation_bp)
app.register_blueprint(notifications_bp)

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Information Validation Tool Enhanced',
        'version': '2.0'
    })

# Enhanced validation criteria endpoint (simplified)
@app.route('/api/v2/validation/criteria')
def get_enhanced_criteria():
    return jsonify({
        'success': True,
        'total_criteria': 65,
        'categories': [
            'Basic Project Information',
            'SFDC & Documentation Integration', 
            'Template & Documentation Standards',
            'Installation Plan Content Validation',
            'Network Configuration & Technical',
            'Site Survey Documentation',
            'Cross-Document Consistency'
        ],
        'enhanced_features': [
            'Conditional Logic Processing',
            'Cross-Document Validation',
            'Automation Complexity Classification',
            'Confidence Scoring',
            'Real-Time Accuracy Monitoring'
        ]
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# Create all database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

