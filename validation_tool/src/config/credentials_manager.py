import os
import json
import tempfile
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CredentialsManager:
    """Manages Google API credentials for the validation tool"""
    
    def __init__(self):
        # Try the deployed path first, then fall back to local development path
        self.credentials_file = '/src/credentials/google-service-account.json'
        if not os.path.exists(self.credentials_file):
            # Fall back to local development path
            local_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'google-service-account.json')
            if os.path.exists(local_path):
                self.credentials_file = local_path
            else:
                # Fall back to temp directory
                self.credentials_file = os.path.join(tempfile.gettempdir(), 'google_credentials.json')
        
        self.credentials = None
        self.load_credentials()
    
    def load_credentials(self) -> Optional[Dict[str, Any]]:
        """Load credentials from file if they exist"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r') as f:
                    credentials_data = json.load(f)
                
                # Validate credentials before setting
                if self._validate_credentials(credentials_data):
                    self.credentials = credentials_data
                    logger.info(f"Google credentials loaded successfully from {self.credentials_file}")
                    return self.credentials
                else:
                    logger.error("Invalid credentials format in file")
                    self.credentials = None
                    return None
            else:
                logger.info(f"No credentials file found at {self.credentials_file}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in credentials file: {e}")
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
        
        self.credentials = None
        return None
    
    def save_credentials(self, credentials_data: Dict[str, Any]) -> bool:
        """Save Google API credentials to secure storage"""
        try:
            # Validate the credentials structure
            if not self._validate_credentials(credentials_data):
                raise ValueError("Invalid credentials format")
            
            # Save to temporary file
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials_data, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(self.credentials_file, 0o600)
            
            self.credentials = credentials_data
            logger.info("Google credentials saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            return False
    
    def _validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate Google service account credentials format"""
        required_fields = [
            'type', 'project_id', 'private_key_id', 'private_key',
            'client_email', 'client_id', 'auth_uri', 'token_uri'
        ]
        
        if not isinstance(credentials, dict):
            return False
        
        for field in required_fields:
            if field not in credentials:
                logger.error(f"Missing required field: {field}")
                return False
        
        if credentials.get('type') != 'service_account':
            logger.error("Credentials must be for a service account")
            return False
        
        return True
    
    def get_credentials(self) -> Optional[Dict[str, Any]]:
        """Get current credentials"""
        return self.credentials
    
    def has_credentials(self) -> bool:
        """Check if valid credentials are available"""
        return self.credentials is not None
    
    def clear_credentials(self) -> bool:
        """Clear stored credentials"""
        try:
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)
            self.credentials = None
            logger.info("Credentials cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to clear credentials: {e}")
            return False
    
    def get_credentials_file_path(self) -> str:
        """Get the path to the credentials file for Google API clients"""
        if self.has_credentials():
            return self.credentials_file
        return None
    
    def get_project_id(self) -> Optional[str]:
        """Get the Google Cloud project ID from credentials"""
        if self.credentials:
            return self.credentials.get('project_id')
        return None
    
    def get_client_email(self) -> Optional[str]:
        """Get the service account email from credentials"""
        if self.credentials:
            return self.credentials.get('client_email')
        return None

# Global instance
credentials_manager = CredentialsManager()

