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
    GOOGLE_INTEGRATIONS_AVAILABLE = True
except ImportError as e:
    # Log the error but don't create fallback classes
    logger.error(f"Critical import error: {e}. Google integration features will not work.")
    GOOGLE_INTEGRATIONS_AVAILABLE = False

@google_integration.route('/api/google/test-connection', methods=['GET'])
def test_google_connections():
    """Test Google Drive and Sheets API connections"""
    if not GOOGLE_INTEGRATIONS_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Google integrations not available due to import errors',
            'connections': {
                'google_drive': {'connected': False, 'error': 'Import error'},
                'google_sheets': {'connected': False, 'error': 'Import error'}
            }
        }), 500
    
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
    """Get the current status of Google API credentials"""
    try:
        # Use the same path as upload function
        credentials_path = "/src/credentials/google-service-account.json"
        
        # Check if file exists
        file_exists = os.path.exists(credentials_path)
        
        status = {
            'credentials_configured': file_exists,
            'credentials_path': credentials_path,
            'file_exists': file_exists,
            'google_drive_accessible': False,
            'google_sheets_accessible': False,
            'client_email': None,
            'project_id': None
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
        
        # Test actual API connections with detailed error reporting
        drive_error = None
        sheets_error = None
        
        try:
            from integrations.google_drive import GoogleDriveIntegration
            # Pass the credentials path explicitly
            drive_integration = GoogleDriveIntegration(credentials_path=credentials_path)
            status['google_drive_accessible'] = drive_integration.test_connection()
            if not status['google_drive_accessible']:
                drive_error = "Google Drive API test failed - check if API is enabled"
        except Exception as e:
            logger.warning(f"Google Drive test failed: {e}")
            status['google_drive_accessible'] = False
            drive_error = str(e)
        
        try:
            from integrations.google_sheets import GoogleSheetsIntegration
            # Pass the credentials path explicitly
            sheets_integration = GoogleSheetsIntegration(credentials_path=credentials_path)
            status['google_sheets_accessible'] = sheets_integration.test_connection()
            if not status['google_sheets_accessible']:
                sheets_error = "Google Sheets API test failed - check if API is enabled"
        except Exception as e:
            logger.warning(f"Google Sheets test failed: {e}")
            status['google_sheets_accessible'] = False
            sheets_error = str(e)
        
        # Add error details to status
        if drive_error:
            status['google_drive_error'] = drive_error
        if sheets_error:
            status['google_sheets_error'] = sheets_error
        
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
        logger.info("=== CREDENTIALS UPLOAD DEBUG START ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request files keys: {list(request.files.keys())}")
        logger.info(f"Request form keys: {list(request.form.keys())}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # Check if file was uploaded
        if 'credentials' not in request.files:
            logger.error("No 'credentials' key found in request.files")
            logger.error(f"Available file keys: {list(request.files.keys())}")
            return jsonify({'error': 'No credentials file uploaded'}), 400
        
        file = request.files['credentials']
        logger.info(f"File received: filename='{file.filename}', content_type='{file.content_type}'")
        
        if file.filename == '':
            logger.error("File filename is empty")
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file is JSON
        if not file.filename.endswith('.json'):
            logger.error(f"File does not end with .json: {file.filename}")
            return jsonify({'error': 'Credentials file must be a JSON file'}), 400
        
        # Read and validate JSON content
        try:
            import json
            logger.info("Reading file content...")
            file_content = file.read().decode('utf-8')
            logger.info(f"File content length: {len(file_content)} characters")
            logger.info(f"File content preview: {file_content[:200]}...")
            
            logger.info("Parsing JSON content...")
            credentials_data = json.loads(file_content)
            logger.info(f"JSON parsed successfully. Keys: {list(credentials_data.keys())}")
            
            # Validate required fields
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
            missing_fields = [field for field in required_fields if field not in credentials_data]
            
            if missing_fields:
                logger.error(f"Missing required fields: {missing_fields}")
                return jsonify({
                    'error': f'Invalid credentials file. Missing fields: {", ".join(missing_fields)}'
                }), 400
            
            if credentials_data.get('type') != 'service_account':
                logger.error(f"Invalid type: {credentials_data.get('type')}")
                return jsonify({'error': 'Credentials file must be for a service account'}), 400
            
            logger.info("JSON validation passed")
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return jsonify({'error': 'Invalid JSON file'}), 400
        except Exception as e:
            logger.error(f"Error reading/parsing file: {str(e)}")
            return jsonify({'error': f'Error reading file: {str(e)}'}), 400
        
        # Save credentials file
        import os
        try:
            logger.info("Starting file save process...")
            # Use absolute path that matches the status check
            credentials_dir = '/src/credentials'
            logger.info(f"Credentials directory: {credentials_dir}")
            
            # Ensure directory exists
            if not os.path.exists(credentials_dir):
                logger.info(f"Creating credentials directory: {credentials_dir}")
                os.makedirs(credentials_dir, exist_ok=True)
            else:
                logger.info("Credentials directory already exists")
            
            # Check directory permissions
            if not os.access(credentials_dir, os.W_OK):
                logger.error(f"No write permission to directory: {credentials_dir}")
                return jsonify({'error': 'Cannot write to credentials directory'}), 500
            
            credentials_path = os.path.join(credentials_dir, 'google-service-account.json')
            logger.info(f"Saving credentials to: {credentials_path}")
            
            # Write the file
            with open(credentials_path, 'w') as f:
                json.dump(credentials_data, f, indent=2)
            
            # Set readable permissions for deployed environments
            os.chmod(credentials_path, 0o644)
            logger.info("Credentials file saved successfully with restricted permissions")
            
            # Verify file was written
            if os.path.exists(credentials_path):
                file_size = os.path.getsize(credentials_path)
                logger.info(f"File verification: exists=True, size={file_size} bytes")
                
                # Reload credentials manager to recognize the new file
                try:
                    from config.credentials_manager import credentials_manager
                    reload_success = credentials_manager.reload_credentials()
                    logger.info(f"Credentials manager reloaded: {reload_success}")
                except Exception as e:
                    logger.warning(f"Failed to reload credentials manager: {e}")
            else:
                logger.error("File verification failed: file does not exist after writing")
                return jsonify({'error': 'Failed to save credentials file'}), 500
            
        except PermissionError as e:
            logger.error(f"Permission error saving file: {str(e)}")
            return jsonify({'error': 'Permission denied when saving credentials'}), 500
        except Exception as e:
            logger.error(f"Error saving credentials file: {str(e)}")
            return jsonify({'error': f'Failed to save credentials: {str(e)}'}), 500
        
        # Test the credentials
        logger.info("Testing credentials with Google APIs...")
        test_results = {}
        
        try:
            from integrations.google_drive import GoogleDriveIntegration
            drive_integration = GoogleDriveIntegration(credentials_path=credentials_path)
            test_results['google_drive'] = drive_integration.test_connection()
            logger.info("Google Drive test completed")
        except Exception as e:
            logger.warning(f"Google Drive test failed with new credentials: {e}")
            test_results['google_drive'] = {'success': False, 'error': str(e)}
        
        try:
            from integrations.google_sheets import GoogleSheetsIntegration
            sheets_integration = GoogleSheetsIntegration(credentials_path=credentials_path)
            test_results['google_sheets'] = sheets_integration.test_connection()
            logger.info("Google Sheets test completed")
        except Exception as e:
            logger.warning(f"Google Sheets test failed with new credentials: {e}")
            test_results['google_sheets'] = {'success': False, 'error': str(e)}
        
        logger.info("=== CREDENTIALS UPLOAD DEBUG END ===")
        logger.info("Credentials upload successful!")
        
        response = jsonify({
            'message': 'Credentials uploaded successfully',
            'project_id': credentials_data.get('project_id'),
            'client_email': credentials_data.get('client_email'),
            'test_results': test_results
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"=== CREDENTIALS UPLOAD FAILED ===")
        logger.error(f"Unexpected error in upload_credentials: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        response = jsonify({'error': f'Upload failed: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

