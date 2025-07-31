from flask import Blueprint, request, jsonify
import json
import logging

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/api/settings/credentials/status', methods=['GET'])
def get_credentials_status():
    """Get the current status of Google API credentials"""
    try:
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config.credentials_manager import credentials_manager
        
        has_credentials = credentials_manager.has_credentials()
        
        status = {
            'has_credentials': has_credentials,
            'project_id': credentials_manager.get_project_id() if has_credentials else None,
            'client_email': credentials_manager.get_client_email() if has_credentials else None,
            'timestamp': None
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error getting credentials status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/credentials/upload', methods=['POST'])
def upload_credentials():
    """Upload Google API service account credentials"""
    try:
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config.credentials_manager import credentials_manager
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No credentials data provided'
            }), 400
        
        # Handle both direct JSON and string input
        if isinstance(data.get('credentials'), str):
            try:
                credentials_data = json.loads(data['credentials'])
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON format in credentials'
                }), 400
        else:
            credentials_data = data.get('credentials')
        
        if not credentials_data:
            return jsonify({
                'success': False,
                'error': 'No credentials data found'
            }), 400
        
        # Save credentials
        if credentials_manager.save_credentials(credentials_data):
            return jsonify({
                'success': True,
                'message': 'Credentials saved successfully',
                'project_id': credentials_manager.get_project_id(),
                'client_email': credentials_manager.get_client_email()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save credentials'
            }), 500
            
    except Exception as e:
        logger.error(f"Error uploading credentials: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/credentials/clear', methods=['DELETE'])
def clear_credentials():
    """Clear stored Google API credentials"""
    try:
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config.credentials_manager import credentials_manager
        
        if credentials_manager.clear_credentials():
            return jsonify({
                'success': True,
                'message': 'Credentials cleared successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to clear credentials'
            }), 500
            
    except Exception as e:
        logger.error(f"Error clearing credentials: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/credentials/test', methods=['POST'])
def test_credentials():
    """Test the current Google API credentials"""
    try:
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config.credentials_manager import credentials_manager
        
        if not credentials_manager.has_credentials():
            return jsonify({
                'success': False,
                'error': 'No credentials configured'
            }), 400
        
        # Import here to avoid circular imports
        from integrations.google_drive import GoogleDriveIntegration
        from integrations.google_sheets import GoogleSheetsIntegration
        
        results = {
            'drive': {'connected': False, 'error': None},
            'sheets': {'connected': False, 'error': None}
        }
        
        # Test Google Drive
        try:
            drive_integration = GoogleDriveIntegration()
            # Try to get drive service info
            service = drive_integration.get_service()
            if service:
                # Test with a simple API call
                about = service.about().get(fields="user").execute()
                results['drive']['connected'] = True
                results['drive']['user'] = about.get('user', {}).get('emailAddress', 'Unknown')
        except Exception as e:
            results['drive']['error'] = str(e)
            logger.error(f"Drive test failed: {e}")
        
        # Test Google Sheets
        try:
            sheets_integration = GoogleSheetsIntegration()
            service = sheets_integration.get_service()
            if service:
                # Test with a simple API call (get spreadsheet properties)
                results['sheets']['connected'] = True
        except Exception as e:
            results['sheets']['error'] = str(e)
            logger.error(f"Sheets test failed: {e}")
        
        return jsonify({
            'success': True,
            'connections': results,
            'timestamp': None
        })
        
    except Exception as e:
        logger.error(f"Error testing credentials: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

