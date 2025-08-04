import io
import json
import os
import re
import time
from typing import Dict, Any, Optional, Tuple, List
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import logging

logger = logging.getLogger(__name__)

class GoogleDriveIntegration:
    """Google Drive API integration for downloading and processing documents."""
    
    def __init__(self, credentials_path: Optional[str] = None, credentials_json: Optional[Dict] = None):
        """
        Initialize Google Drive integration.
        
        Args:
            credentials_path: Path to service account JSON file
            credentials_json: Service account credentials as dictionary
        """
        self.scopes = [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.file'
        ]
        self.service = None
        self.rate_limit_delay = 1.0  # Delay between requests to respect rate limits
        
        # Try to use provided credentials first
        if credentials_json:
            self.credentials = Credentials.from_service_account_info(
                credentials_json, scopes=self.scopes
            )
        elif credentials_path and os.path.exists(credentials_path):
            self.credentials = Credentials.from_service_account_file(
                credentials_path, scopes=self.scopes
            )
        else:
            # Try to use credentials manager
            try:
                from config.credentials_manager import credentials_manager
                
                if credentials_manager.has_credentials():
                    credentials_file = credentials_manager.get_credentials_file_path()
                    if credentials_file:
                        self.credentials = Credentials.from_service_account_file(
                            credentials_file, scopes=self.scopes
                        )
                        logger.info("Using credentials from credentials manager")
                    else:
                        logger.warning("Credentials manager has credentials but no file path")
                        self.credentials = None
                else:
                    logger.warning("No credentials available in credentials manager")
                    self.credentials = None
            except Exception as e:
                logger.error(f"Failed to load credentials from manager: {e}")
                # Fallback to environment variables
                creds_env = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
                if creds_env:
                    credentials_json = json.loads(creds_env)
                    self.credentials = Credentials.from_service_account_info(
                        credentials_json, scopes=self.scopes
                    )
                else:
                    logger.warning("No Google Drive credentials available")
                    self.credentials = None
        
        if self.credentials:
            self.service = build('drive', 'v3', credentials=self.credentials)
    
    def _rate_limit_delay(self):
        """Apply rate limiting delay."""
        time.sleep(self.rate_limit_delay)
    
    def extract_file_id(self, url: str) -> Optional[str]:
        """
        Extract Google Drive file ID from various URL formats.
        
        Args:
            url: Google Drive URL
            
        Returns:
            File ID if found, None otherwise
        """
        # Common Google Drive URL patterns
        patterns = [
            r'/file/d/([a-zA-Z0-9-_]+)',  # Standard sharing URL
            r'id=([a-zA-Z0-9-_]+)',       # Direct file ID parameter
            r'/d/([a-zA-Z0-9-_]+)',       # Short format
            r'drive\.google\.com.*?/([a-zA-Z0-9-_]{25,})'  # Generic pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                file_id = match.group(1)
                logger.info(f"Extracted file ID: {file_id} from URL: {url}")
                return file_id
        
        # If no pattern matches, check if the URL itself is a file ID
        if re.match(r'^[a-zA-Z0-9-_]{25,}$', url.strip()):
            logger.info(f"URL appears to be a direct file ID: {url}")
            return url.strip()
        
        logger.warning(f"Could not extract file ID from URL: {url}")
        return None
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get metadata for a Google Drive file.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            File metadata dictionary
        """
        if not self.service:
            raise ValueError("Google Drive service not initialized")
        
        try:
            self._rate_limit_delay()
            
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields='id,name,mimeType,size,createdTime,modifiedTime,owners,permissions'
            ).execute()
            
            logger.info(f"Retrieved metadata for file: {file_metadata.get('name', 'Unknown')}")
            return file_metadata
            
        except HttpError as error:
            if error.resp.status == 404:
                logger.error(f"File not found: {file_id}")
                raise ValueError(f"File not found or not accessible: {file_id}")
            elif error.resp.status == 403:
                logger.error(f"Access denied to file: {file_id}")
                raise ValueError(f"Access denied to file: {file_id}")
            else:
                logger.error(f"Google Drive API error: {error}")
                raise
        except Exception as error:
            logger.error(f"Error getting file metadata: {error}")
            raise
    
    def download_file(self, file_id: str, local_path: str) -> Tuple[bool, str]:
        """
        Download a file from Google Drive to local storage.
        
        Args:
            file_id: Google Drive file ID
            local_path: Local path to save the file
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.service:
            raise ValueError("Google Drive service not initialized")
        
        try:
            # Get file metadata first
            metadata = self.get_file_metadata(file_id)
            mime_type = metadata.get('mimeType', '')
            file_name = metadata.get('name', 'unknown_file')
            
            self._rate_limit_delay()
            
            # Handle Google Workspace documents (need to export)
            if mime_type.startswith('application/vnd.google-apps'):
                success, message = self._export_google_doc(file_id, local_path, mime_type, file_name)
            else:
                # Regular file download
                success, message = self._download_regular_file(file_id, local_path, file_name)
            
            if success:
                logger.info(f"Successfully downloaded file: {file_name} to {local_path}")
            else:
                logger.error(f"Failed to download file: {file_name} - {message}")
            
            return success, message
            
        except Exception as error:
            error_msg = f"Error downloading file {file_id}: {str(error)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _download_regular_file(self, file_id: str, local_path: str, file_name: str) -> Tuple[bool, str]:
        """Download a regular file (PDF, XLSX, etc.)."""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    logger.debug(f"Download progress: {int(status.progress() * 100)}%")
            
            # Write to local file
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(file_io.getvalue())
            
            return True, f"Successfully downloaded {file_name}"
            
        except Exception as error:
            return False, f"Error downloading regular file: {str(error)}"
    
    def _export_google_doc(self, file_id: str, local_path: str, mime_type: str, file_name: str) -> Tuple[bool, str]:
        """Export a Google Workspace document to a downloadable format."""
        try:
            # Determine export format based on Google Workspace type
            export_formats = {
                'application/vnd.google-apps.document': 'application/pdf',  # Google Docs -> PDF
                'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # Sheets -> XLSX
                'application/vnd.google-apps.presentation': 'application/pdf',  # Slides -> PDF
            }
            
            export_mime_type = export_formats.get(mime_type)
            if not export_mime_type:
                return False, f"Unsupported Google Workspace document type: {mime_type}"
            
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType=export_mime_type
            )
            
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    logger.debug(f"Export progress: {int(status.progress() * 100)}%")
            
            # Adjust file extension based on export format
            if export_mime_type == 'application/pdf' and not local_path.endswith('.pdf'):
                local_path = local_path.rsplit('.', 1)[0] + '.pdf'
            elif export_mime_type.endswith('spreadsheetml.sheet') and not local_path.endswith('.xlsx'):
                local_path = local_path.rsplit('.', 1)[0] + '.xlsx'
            
            # Write to local file
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(file_io.getvalue())
            
            return True, f"Successfully exported {file_name} as {os.path.basename(local_path)}"
            
        except Exception as error:
            return False, f"Error exporting Google document: {str(error)}"
    
    def check_file_permissions(self, file_id: str) -> Dict[str, Any]:
        """
        Check if the service account has access to the file.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            Dictionary with permission information
        """
        # Check if Google Drive service is initialized
        if not self.service:
            return {
                'accessible': False,
                'error': 'Google Drive service not initialized - credentials may be missing or invalid'
            }
        
        try:
            metadata = self.get_file_metadata(file_id)
            
            permissions_info = {
                'accessible': True,
                'file_name': metadata.get('name', 'Unknown'),
                'mime_type': metadata.get('mimeType', 'Unknown'),
                'size': metadata.get('size', 'Unknown'),
                'owners': [owner.get('displayName', 'Unknown') for owner in metadata.get('owners', [])],
                'created_time': metadata.get('createdTime'),
                'modified_time': metadata.get('modifiedTime')
            }
            
            return permissions_info
            
        except ValueError as error:
            return {
                'accessible': False,
                'error': str(error),
                'file_id': file_id
            }
        except Exception as error:
            return {
                'accessible': False,
                'error': f"Unexpected error: {str(error)}",
                'file_id': file_id
            }
    
    def process_google_drive_url(self, url: str, download_dir: str = '/tmp/validation_downloads') -> Dict[str, Any]:
        """
        Process a Google Drive URL: extract file ID, check permissions, and download.
        
        Args:
            url: Google Drive URL
            download_dir: Directory to download files to
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'success': False,
            'url': url,
            'file_id': None,
            'local_path': None,
            'metadata': {},
            'error': None
        }
        
        # Check if Google Drive service is initialized
        if not self.service:
            result['error'] = "Google Drive service not initialized - credentials may be missing or invalid"
            logger.error("Google Drive service not initialized")
            return result
        
        try:
            # Extract file ID
            file_id = self.extract_file_id(url)
            if not file_id:
                result['error'] = "Could not extract file ID from URL"
                return result
            
            result['file_id'] = file_id
            
            # Check permissions
            permissions = self.check_file_permissions(file_id)
            if not permissions.get('accessible', False):
                result['error'] = permissions.get('error', 'File not accessible')
                return result
            
            result['metadata'] = permissions
            
            # Generate local file path
            file_name = permissions.get('file_name', f'file_{file_id}')
            # Sanitize filename
            safe_filename = re.sub(r'[^\w\-_\.]', '_', file_name)
            local_path = os.path.join(download_dir, safe_filename)
            
            # Download file
            download_success, download_message = self.download_file(file_id, local_path)
            
            if download_success:
                result['success'] = True
                result['local_path'] = local_path
                result['message'] = download_message
            else:
                result['error'] = download_message
            
            return result
            
        except Exception as error:
            result['error'] = f"Error processing Google Drive URL: {str(error)}"
            logger.error(result['error'])
            return result
    
    def test_connection(self) -> bool:
        """
        Test the connection to Google Drive API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        if not self.service:
            return False
        
        try:
            # Try to list files (with limit 1) to test connection
            self._rate_limit_delay()
            result = self.service.files().list(pageSize=1).execute()
            logger.info("Google Drive connection test successful")
            return True
        except Exception as error:
            logger.error(f"Google Drive connection test failed: {error}")
            return False
    
    def list_recent_files(self, max_files: int = 10) -> List[Dict[str, Any]]:
        """
        List recent files accessible to the service account.
        
        Args:
            max_files: Maximum number of files to return
            
        Returns:
            List of file metadata dictionaries
        """
        if not self.service:
            raise ValueError("Google Drive service not initialized")
        
        try:
            self._rate_limit_delay()
            
            results = self.service.files().list(
                pageSize=max_files,
                orderBy='modifiedTime desc',
                fields='files(id,name,mimeType,size,modifiedTime)'
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Retrieved {len(files)} recent files")
            
            return files
            
        except Exception as error:
            logger.error(f"Error listing recent files: {error}")
            return []


    def process_document_from_url(self, url: str) -> Dict[str, Any]:
        """
        Process a document from a Google Drive URL.
        
        Args:
            url: Google Drive URL to process
            
        Returns:
            Dict containing success status, data, and metadata
        """
        try:
            # Use the existing process_google_drive_url method
            result = self.process_google_drive_url(url)
            
            if result['success']:
                return {
                    'success': True,
                    'data': result.get('content', ''),
                    'metadata': {
                        'file_id': result.get('file_id'),
                        'file_name': result.get('file_name'),
                        'mime_type': result.get('mime_type'),
                        'size': result.get('size'),
                        'modified_time': result.get('modified_time'),
                        'url': url
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error processing document'),
                    'data': None,
                    'metadata': None
                }
                
        except Exception as e:
            logger.error(f"Error processing document from URL {url}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': None,
                'metadata': None
            }

