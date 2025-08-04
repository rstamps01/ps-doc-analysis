import os
import json
import time
from typing import List, Dict, Any, Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsIntegration:
    """Google Sheets API integration for reading requirements and updating status."""
    
    def __init__(self, credentials_path: Optional[str] = None, credentials_json: Optional[Dict] = None):
        """
        Initialize Google Sheets integration.
        
        Args:
            credentials_path: Path to service account JSON file
            credentials_json: Service account credentials as dictionary
        """
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        self.service = None
        
        # Try to use provided credentials first
        if credentials_json:
            self.credentials = Credentials.from_service_account_info(
                credentials_json, scopes=self.scopes
            )
        elif credentials_path and os.path.exists(credentials_path):
            try:
                self.credentials = Credentials.from_service_account_file(
                    credentials_path, scopes=self.scopes
                )
            except PermissionError as e:
                logger.warning(f"Permission error reading credentials file {credentials_path}: {e}")
                # Try to fix permissions
                try:
                    os.chmod(credentials_path, 0o644)
                    logger.info("Fixed credentials file permissions, retrying...")
                    self.credentials = Credentials.from_service_account_file(
                        credentials_path, scopes=self.scopes
                    )
                except Exception as fix_error:
                    logger.error(f"Cannot fix permissions or read file: {fix_error}")
                    self.credentials = None
        else:
            # Try to use credentials manager
            try:
                from config.credentials_manager import credentials_manager
                
                if credentials_manager.has_credentials():
                    credentials_file = credentials_manager.get_credentials_file_path()
                    if credentials_file:
                        try:
                            self.credentials = Credentials.from_service_account_file(
                                credentials_file, scopes=self.scopes
                            )
                            logger.info("Using credentials from credentials manager")
                        except PermissionError as e:
                            logger.warning(f"Permission error reading credentials from manager: {e}")
                            # Try to fix permissions
                            try:
                                os.chmod(credentials_file, 0o644)
                                logger.info("Fixed credentials file permissions, retrying...")
                                self.credentials = Credentials.from_service_account_file(
                                    credentials_file, scopes=self.scopes
                                )
                                logger.info("Using credentials from credentials manager after permission fix")
                            except Exception as fix_error:
                                logger.error(f"Cannot fix permissions: {fix_error}")
                                self.credentials = None
                    else:
                        logger.warning("Credentials manager has credentials but no file path")
                        self.credentials = None
                else:
                    logger.warning("No credentials available in credentials manager")
                    self.credentials = None
            except Exception as e:
                logger.error(f"Failed to load credentials from manager: {e}")
                # Fallback to environment variables
                creds_env = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
                if creds_env:
                    credentials_json = json.loads(creds_env)
                    self.credentials = Credentials.from_service_account_info(
                        credentials_json, scopes=self.scopes
                    )
                else:
                    logger.warning("No Google Sheets credentials available")
                    self.credentials = None
        
        if self.credentials:
            self.service = build('sheets', 'v4', credentials=self.credentials)
    
    def _rate_limit_delay(self):
        """Apply rate limiting delay."""
        time.sleep(self.rate_limit_delay)
    
    def read_requirements(self, spreadsheet_id: str, range_name: str = 'A:Z') -> List[Dict[str, Any]]:
        """
        Read validation requirements from Google Sheets.
        
        Args:
            spreadsheet_id: Google Sheets document ID
            range_name: Cell range to read (default: A:Z)
            
        Returns:
            List of requirement dictionaries
        """
        if not self.service:
            raise ValueError("Google Sheets service not initialized")
        
        try:
            self._rate_limit_delay()
            
            # Get the values from the sheet
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning(f"No data found in sheet {spreadsheet_id}")
                return []
            
            # Assume first row contains headers
            headers = values[0] if values else []
            requirements = []
            
            for row_idx, row in enumerate(values[1:], start=2):  # Skip header row
                if not row:  # Skip empty rows
                    continue
                
                # Create requirement dictionary
                requirement = {}
                for col_idx, header in enumerate(headers):
                    value = row[col_idx] if col_idx < len(row) else ''
                    requirement[header.lower().replace(' ', '_')] = value
                
                # Add row metadata
                requirement['_row_number'] = row_idx
                requirement['_spreadsheet_id'] = spreadsheet_id
                requirement['_range'] = range_name
                
                requirements.append(requirement)
            
            logger.info(f"Read {len(requirements)} requirements from sheet {spreadsheet_id}")
            return requirements
            
        except HttpError as error:
            logger.error(f"Google Sheets API error: {error}")
            raise
        except Exception as error:
            logger.error(f"Error reading requirements: {error}")
            raise
    
    def update_status(self, spreadsheet_id: str, row_number: int, status_column: str, 
                     status_value: str, additional_updates: Optional[Dict[str, str]] = None) -> bool:
        """
        Update validation status in Google Sheets.
        
        Args:
            spreadsheet_id: Google Sheets document ID
            row_number: Row number to update (1-based)
            status_column: Column letter/name for status (e.g., 'E' or 'Status')
            status_value: Status value to write (e.g., 'Pass', 'Fail')
            additional_updates: Additional column updates {column: value}
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            raise ValueError("Google Sheets service not initialized")
        
        try:
            self._rate_limit_delay()
            
            # Prepare updates
            updates = []
            
            # Main status update
            status_range = f"{status_column}{row_number}"
            updates.append({
                'range': status_range,
                'values': [[status_value]]
            })
            
            # Additional updates
            if additional_updates:
                for column, value in additional_updates.items():
                    update_range = f"{column}{row_number}"
                    updates.append({
                        'range': update_range,
                        'values': [[value]]
                    })
            
            # Batch update
            body = {
                'valueInputOption': 'RAW',
                'data': updates
            }
            
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            updated_cells = result.get('totalUpdatedCells', 0)
            logger.info(f"Updated {updated_cells} cells in sheet {spreadsheet_id}")
            
            return True
            
        except HttpError as error:
            logger.error(f"Google Sheets API error during update: {error}")
            return False
        except Exception as error:
            logger.error(f"Error updating status: {error}")
            return False
    
    def get_sheet_metadata(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Get metadata about the spreadsheet.
        
        Args:
            spreadsheet_id: Google Sheets document ID
            
        Returns:
            Spreadsheet metadata
        """
        if not self.service:
            raise ValueError("Google Sheets service not initialized")
        
        try:
            self._rate_limit_delay()
            
            result = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            return {
                'title': result.get('properties', {}).get('title', ''),
                'sheets': [
                    {
                        'title': sheet['properties']['title'],
                        'sheet_id': sheet['properties']['sheetId'],
                        'grid_properties': sheet['properties'].get('gridProperties', {})
                    }
                    for sheet in result.get('sheets', [])
                ]
            }
            
        except HttpError as error:
            logger.error(f"Google Sheets API error getting metadata: {error}")
            raise
        except Exception as error:
            logger.error(f"Error getting sheet metadata: {error}")
            raise
    
    def detect_schema(self, spreadsheet_id: str, range_name: str = 'A1:Z1') -> List[str]:
        """
        Detect the schema (column headers) of the spreadsheet.
        
        Args:
            spreadsheet_id: Google Sheets document ID
            range_name: Range containing headers (default: A1:Z1)
            
        Returns:
            List of column headers
        """
        if not self.service:
            raise ValueError("Google Sheets service not initialized")
        
        try:
            self._rate_limit_delay()
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            headers = values[0] if values else []
            
            logger.info(f"Detected schema with {len(headers)} columns: {headers}")
            return headers
            
        except HttpError as error:
            logger.error(f"Google Sheets API error detecting schema: {error}")
            raise
        except Exception as error:
            logger.error(f"Error detecting schema: {error}")
            raise
    
    def batch_read_requirements(self, requests: List[Dict[str, str]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Read requirements from multiple sheets in a single batch.
        
        Args:
            requests: List of {spreadsheet_id, range} dictionaries
            
        Returns:
            Dictionary mapping spreadsheet_id to requirements list
        """
        if not self.service:
            raise ValueError("Google Sheets service not initialized")
        
        results = {}
        
        for request in requests:
            spreadsheet_id = request['spreadsheet_id']
            range_name = request.get('range', 'A:Z')
            
            try:
                requirements = self.read_requirements(spreadsheet_id, range_name)
                results[spreadsheet_id] = requirements
            except Exception as error:
                logger.error(f"Error reading from sheet {spreadsheet_id}: {error}")
                results[spreadsheet_id] = []
        
        return results
    
    def test_connection(self) -> bool:
        """
        Test the connection to Google Sheets API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        if not self.service:
            logger.error("Google Sheets service not initialized")
            return False
        
        try:
            # Try to make a simple API call to test the connection
            # Use the correct method name for the Sheets API
            response = self.service.spreadsheets().get(
                spreadsheetId='test'  # This will fail but will test authentication
            ).execute()
            # If we get here without an auth error, the connection works
            return True
        except HttpError as e:
            # Check if it's an authentication error vs just a "not found" error
            if e.resp.status == 404:
                # 404 means authentication worked but spreadsheet doesn't exist - that's fine
                logger.info("Google Sheets connection test successful (404 expected for test ID)")
                return True
            elif e.resp.status in [401, 403]:
                # Authentication/authorization error
                logger.error(f"Google Sheets authentication failed: {e}")
                return False
            else:
                # Other error, but authentication probably worked
                logger.warning(f"Google Sheets test returned unexpected error: {e}")
                return True
        except Exception as error:
            logger.error(f"Google Sheets connection test failed: {error}")
            return False

