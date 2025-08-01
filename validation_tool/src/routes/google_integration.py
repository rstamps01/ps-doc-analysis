"""
Google integration routes for enhanced document processing capabilities.
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

google_integration = Blueprint('google_integration', __name__)
logger = logging.getLogger(__name__)

# Fix imports for standalone execution
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from integrations.google_drive import GoogleDriveIntegration
    from integrations.google_sheets import GoogleSheetsIntegration
    from validation.google_sheets_validator import GoogleSheetsValidator
except ImportError as e:
    # Fallback for missing modules
    logger.warning(f"Import error: {e}. Some Google integration features may not work.")
    
    class GoogleDriveIntegration:
        def __init__(self): pass
        def test_connection(self): return False
    
    class GoogleSheetsIntegration:
        def __init__(self): pass
        def test_connection(self): return False
        def get_sheet_metadata(self, spreadsheet_id): return {}
        def detect_schema(self, spreadsheet_id): return {}
    
    class GoogleSheetsValidator:
        def __init__(self): pass
        def validate_site_survey_part1(self, spreadsheet_id): return {'status': 'error', 'message': 'Module not available'}
        def validate_site_survey_part2(self, spreadsheet_id): return {'status': 'error', 'message': 'Module not available'}

@google_integration.route('/api/google/test-connection', methods=['GET'])
def test_google_connections():
    """Test Google Drive and Sheets API connections"""
    try:
        results = {
            'google_drive': {'connected': False, 'error': None},
            'google_sheets': {'connected': False, 'error': None}
        }
        
        # Test Google Drive connection
        try:
            drive_integration = GoogleDriveIntegration()
            results['google_drive']['connected'] = drive_integration.test_connection()
        except Exception as e:
            results['google_drive']['error'] = str(e)
        
        # Test Google Sheets connection
        try:
            sheets_integration = GoogleSheetsIntegration()
            results['google_sheets']['connected'] = sheets_integration.test_connection()
        except Exception as e:
            results['google_sheets']['error'] = str(e)
        
        overall_success = results['google_drive']['connected'] and results['google_sheets']['connected']
        
        return jsonify({
            'success': overall_success,
            'connections': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Connection test failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@google_integration.route('/api/google/drive/info/<file_id>', methods=['GET'])
def get_drive_file_info(file_id):
    """Get information about a Google Drive file"""
    try:
        drive_integration = GoogleDriveIntegration()
        if not drive_integration.service:
            return jsonify({'error': 'Google Drive integration not configured'}), 500
        
        permissions = drive_integration.check_file_permissions(file_id)
        
        return jsonify({
            'success': permissions.get('accessible', False),
            'file_info': permissions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting file info: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@google_integration.route('/api/google/sheets/info/<spreadsheet_id>', methods=['GET'])
def get_sheets_info(spreadsheet_id):
    """Get information about a Google Sheets document"""
    try:
        sheets_integration = GoogleSheetsIntegration()
        if not sheets_integration.service:
            return jsonify({'error': 'Google Sheets integration not configured'}), 500
        
        metadata = sheets_integration.get_sheet_metadata(spreadsheet_id)
        schema = sheets_integration.detect_schema(spreadsheet_id)
        
        return jsonify({
            'success': True,
            'metadata': metadata,
            'schema': schema,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting sheets info: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@google_integration.route('/api/google/sheets/validate-site-survey', methods=['POST'])
def validate_site_survey():
    """Validate Site Survey Google Sheets documents"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        spreadsheet_id = data.get('spreadsheet_id')
        document_type = data.get('document_type', 'part1')  # 'part1' or 'part2'
        
        if not spreadsheet_id:
            return jsonify({'error': 'Spreadsheet ID is required'}), 400
        
        # Initialize validator
        sheets_validator = GoogleSheetsValidator()
        
        # Validate based on document type
        if document_type == 'part1':
            validation_results = sheets_validator.validate_site_survey_part1(spreadsheet_id)
        elif document_type == 'part2':
            validation_results = sheets_validator.validate_site_survey_part2(spreadsheet_id)
        else:
            return jsonify({'error': 'Invalid document type. Use "part1" or "part2"'}), 400
        
        return jsonify({
            'success': True,
            'validation_results': validation_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Site Survey validation failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@google_integration.route('/api/google/sheets/cross-validate', methods=['POST'])
def cross_validate_documents():
    """Cross-validate multiple Google Sheets documents for consistency"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        part1_id = data.get('part1_spreadsheet_id')
        part2_id = data.get('part2_spreadsheet_id')
        
        if not part1_id or not part2_id:
            return jsonify({'error': 'Both Part 1 and Part 2 spreadsheet IDs are required'}), 400
        
        # Initialize validator
        sheets_validator = GoogleSheetsValidator()
        
        # Validate both documents
        part1_results = sheets_validator.validate_site_survey_part1(part1_id)
        part2_results = sheets_validator.validate_site_survey_part2(part2_id)
        
        # Perform cross-document validation
        cross_validation = _perform_cross_validation(part1_results, part2_results)
        
        return jsonify({
            'success': True,
            'part1_validation': part1_results,
            'part2_validation': part2_results,
            'cross_validation': cross_validation,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Cross-validation failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@google_integration.route('/api/google/extract-file-id', methods=['POST'])
def extract_file_id():
    """Extract file ID from Google Drive or Sheets URL"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400
        
        # Determine if it's Drive or Sheets
        if 'drive.google.com' in url:
            drive_integration = GoogleDriveIntegration()
            file_id = drive_integration.extract_file_id(url)
            service_type = 'drive'
        elif 'docs.google.com/spreadsheets' in url:
            import re
            match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
            file_id = match.group(1) if match else None
            service_type = 'sheets'
        else:
            return jsonify({'error': 'URL is not a valid Google Drive or Sheets URL'}), 400
        
        if not file_id:
            return jsonify({'error': 'Could not extract file ID from URL'}), 400
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'service_type': service_type,
            'original_url': url,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'File ID extraction failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

def _perform_cross_validation(part1_results: dict, part2_results: dict) -> dict:
    """Perform cross-validation between Site Survey Part 1 and Part 2"""
    cross_validation = {
        'consistency_score': 0.0,
        'consistency_issues': [],
        'data_sync_status': 'unknown',
        'recommendations': []
    }
    
    try:
        # Check if both validations were successful
        if part1_results.get('status') == 'error' or part2_results.get('status') == 'error':
            cross_validation['consistency_issues'].append('One or both documents could not be validated')
            return cross_validation
        
        # Compare project details consistency
        part1_score = part1_results.get('content_validation', {}).get('project_details', {}).get('score', 0)
        part2_score = part2_results.get('content_validation', {}).get('project_details', {}).get('score', 0)
        
        if abs(part1_score - part2_score) > 0.2:
            cross_validation['consistency_issues'].append('Project details consistency between Part 1 and Part 2 is low')
        
        # Check for data synchronization (Part 2 should import from Part 1)
        if 'Import from Part 1' in part2_results.get('title', ''):
            cross_validation['data_sync_status'] = 'synchronized'
        else:
            cross_validation['data_sync_status'] = 'not_synchronized'
            cross_validation['consistency_issues'].append('Part 2 may not be properly synchronized with Part 1')
        
        # Calculate overall consistency score
        consistency_factors = []
        
        # Factor 1: Both documents have good scores
        if part1_results.get('overall_score', 0) > 0.7 and part2_results.get('overall_score', 0) > 0.7:
            consistency_factors.append(0.4)
        
        # Factor 2: Data sync status
        if cross_validation['data_sync_status'] == 'synchronized':
            consistency_factors.append(0.3)
        
        # Factor 3: Similar project details scores
        if abs(part1_score - part2_score) <= 0.2:
            consistency_factors.append(0.3)
        
        cross_validation['consistency_score'] = sum(consistency_factors)
        
        # Generate recommendations
        if cross_validation['consistency_score'] < 0.7:
            cross_validation['recommendations'].append('Review and synchronize data between Part 1 and Part 2')
        
        if cross_validation['data_sync_status'] != 'synchronized':
            cross_validation['recommendations'].append('Ensure Part 2 properly imports data from Part 1')
        
        if len(cross_validation['consistency_issues']) == 0:
            cross_validation['recommendations'].append('Documents are well synchronized and consistent')
        
    except Exception as e:
        logger.error(f"Error in cross-validation: {str(e)}")
        cross_validation['consistency_issues'].append(f'Cross-validation error: {str(e)}')
    
    return cross_validation


@google_integration.route('/api/google/credentials/status', methods=['GET'])
def get_credentials_status():
    """Get the status of Google API credentials"""
    try:
        # Check if credentials file exists
        import os
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', './credentials/google-service-account.json')
        
        status = {
            'credentials_configured': False,
            'credentials_path': credentials_path,
            'file_exists': False,
            'google_drive_accessible': False,
            'google_sheets_accessible': False,
            'project_id': None,
            'client_email': None
        }
        
        # Check if credentials file exists
        if os.path.exists(credentials_path):
            status['file_exists'] = True
            
            # Try to read credentials info
            try:
                import json
                with open(credentials_path, 'r') as f:
                    creds_data = json.load(f)
                    status['project_id'] = creds_data.get('project_id')
                    status['client_email'] = creds_data.get('client_email')
                    status['credentials_configured'] = True
            except Exception as e:
                logger.warning(f"Could not read credentials file: {e}")
        
        # Test actual API connections
        try:
            drive_integration = GoogleDriveIntegration()
            status['google_drive_accessible'] = drive_integration.test_connection()
        except Exception as e:
            logger.warning(f"Google Drive test failed: {e}")
        
        try:
            sheets_integration = GoogleSheetsIntegration()
            status['google_sheets_accessible'] = sheets_integration.test_connection()
        except Exception as e:
            logger.warning(f"Google Sheets test failed: {e}")
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error checking credentials status: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@google_integration.route('/api/google/credentials/upload', methods=['POST', 'OPTIONS'])
def upload_credentials():
    """Upload Google API service account credentials"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
    
    try:
        # Check if file was uploaded
        if 'credentials' not in request.files:
            return jsonify({'error': 'No credentials file uploaded'}), 400
        
        file = request.files['credentials']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file is JSON
        if not file.filename.endswith('.json'):
            return jsonify({'error': 'Credentials file must be a JSON file'}), 400
        
        # Read and validate JSON content
        try:
            import json
            file_content = file.read().decode('utf-8')
            credentials_data = json.loads(file_content)
            
            # Validate required fields
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
            missing_fields = [field for field in required_fields if field not in credentials_data]
            
            if missing_fields:
                return jsonify({
                    'error': f'Invalid credentials file. Missing fields: {", ".join(missing_fields)}'
                }), 400
            
            if credentials_data.get('type') != 'service_account':
                return jsonify({'error': 'Credentials file must be for a service account'}), 400
            
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON file'}), 400
        except Exception as e:
            return jsonify({'error': f'Error reading file: {str(e)}'}), 400
        
        # Save credentials file
        import os
        credentials_dir = './credentials'
        os.makedirs(credentials_dir, exist_ok=True)
        
        credentials_path = os.path.join(credentials_dir, 'google-service-account.json')
        
        with open(credentials_path, 'w') as f:
            f.write(file_content)
        
        # Update environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # Test the new credentials
        test_results = {
            'google_drive': False,
            'google_sheets': False
        }
        
        try:
            drive_integration = GoogleDriveIntegration()
            test_results['google_drive'] = drive_integration.test_connection()
        except Exception as e:
            logger.warning(f"Google Drive test failed with new credentials: {e}")
        
        try:
            sheets_integration = GoogleSheetsIntegration()
            test_results['google_sheets'] = sheets_integration.test_connection()
        except Exception as e:
            logger.warning(f"Google Sheets test failed with new credentials: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Credentials uploaded successfully',
            'project_id': credentials_data.get('project_id'),
            'client_email': credentials_data.get('client_email'),
            'test_results': test_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error uploading credentials: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

