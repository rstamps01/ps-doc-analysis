"""
Enhanced Google Sheets Integration
Comprehensive data extraction from all spreadsheet tabs
"""

import json
import logging
from typing import Dict, List, Any, Optional
from googleapiclient.discovery import build
from google.oauth2 import service_account
from config.credentials_manager import CredentialsManager

logger = logging.getLogger(__name__)

class EnhancedGoogleSheetsIntegration:
    """Enhanced Google Sheets integration for comprehensive data extraction"""
    
    def __init__(self):
        self.credentials_manager = CredentialsManager()
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Sheets service with credentials"""
        try:
            credentials_data = self.credentials_manager.get_credentials()
            if not credentials_data:
                logger.warning("No Google credentials found")
                return
            
            credentials = service_account.Credentials.from_service_account_info(
                credentials_data,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Google Sheets service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {str(e)}")
            self.service = None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Google Sheets API connection"""
        try:
            if not self.service:
                return {
                    'connected': False,
                    'error': 'Google Sheets service not initialized'
                }
            
            # Test with a simple API call
            response = self.service.spreadsheets().get(
                spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'  # Public test sheet
            ).execute()
            
            return {
                'connected': True,
                'service_account_email': self.credentials_manager.get_service_account_email()
            }
            
        except Exception as e:
            logger.error(f"Google Sheets connection test failed: {str(e)}")
            return {
                'connected': False,
                'error': str(e)
            }
    
    def extract_spreadsheet_id(self, url: str) -> Optional[str]:
        """Extract spreadsheet ID from Google Sheets URL"""
        try:
            if '/spreadsheets/d/' in url:
                start = url.find('/spreadsheets/d/') + len('/spreadsheets/d/')
                end = url.find('/', start)
                if end == -1:
                    end = url.find('#', start)
                if end == -1:
                    end = url.find('?', start)
                if end == -1:
                    end = len(url)
                return url[start:end]
            return None
        except Exception as e:
            logger.error(f"Error extracting spreadsheet ID: {str(e)}")
            return None
    
    def get_spreadsheet_metadata(self, spreadsheet_id: str) -> Dict[str, Any]:
        """Get spreadsheet metadata including all sheet names"""
        try:
            if not self.service:
                raise Exception("Google Sheets service not initialized")
            
            response = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets = []
            for sheet in response.get('sheets', []):
                sheet_properties = sheet.get('properties', {})
                sheets.append({
                    'sheet_id': sheet_properties.get('sheetId'),
                    'title': sheet_properties.get('title'),
                    'index': sheet_properties.get('index'),
                    'sheet_type': sheet_properties.get('sheetType', 'GRID'),
                    'grid_properties': sheet_properties.get('gridProperties', {})
                })
            
            return {
                'spreadsheet_id': spreadsheet_id,
                'title': response.get('properties', {}).get('title', ''),
                'locale': response.get('properties', {}).get('locale', ''),
                'sheets': sheets,
                'total_sheets': len(sheets)
            }
            
        except Exception as e:
            logger.error(f"Error getting spreadsheet metadata: {str(e)}")
            raise
    
    def extract_all_sheet_data(self, spreadsheet_id: str) -> Dict[str, Any]:
        """Extract data from all sheets in the spreadsheet"""
        try:
            metadata = self.get_spreadsheet_metadata(spreadsheet_id)
            all_data = {
                'metadata': metadata,
                'sheets_data': {}
            }
            
            for sheet in metadata['sheets']:
                sheet_title = sheet['title']
                logger.info(f"Extracting data from sheet: {sheet_title}")
                
                try:
                    sheet_data = self.extract_sheet_data(spreadsheet_id, sheet_title)
                    all_data['sheets_data'][sheet_title] = sheet_data
                except Exception as e:
                    logger.error(f"Error extracting data from sheet {sheet_title}: {str(e)}")
                    all_data['sheets_data'][sheet_title] = {
                        'error': str(e),
                        'values': []
                    }
            
            return all_data
            
        except Exception as e:
            logger.error(f"Error extracting all sheet data: {str(e)}")
            raise
    
    def extract_sheet_data(self, spreadsheet_id: str, sheet_name: str, range_name: str = None) -> Dict[str, Any]:
        """Extract data from a specific sheet"""
        try:
            if not self.service:
                raise Exception("Google Sheets service not initialized")
            
            # If no range specified, get all data from the sheet
            if range_name is None:
                range_name = sheet_name
            else:
                range_name = f"{sheet_name}!{range_name}"
            
            response = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueRenderOption='UNFORMATTED_VALUE',
                dateTimeRenderOption='FORMATTED_STRING'
            ).execute()
            
            values = response.get('values', [])
            
            # Process the data into a more structured format
            processed_data = self._process_sheet_data(values, sheet_name)
            
            return {
                'sheet_name': sheet_name,
                'range': response.get('range', ''),
                'major_dimension': response.get('majorDimension', 'ROWS'),
                'values': values,
                'processed_data': processed_data,
                'row_count': len(values),
                'column_count': max(len(row) for row in values) if values else 0
            }
            
        except Exception as e:
            logger.error(f"Error extracting sheet data: {str(e)}")
            raise
    
    def _process_sheet_data(self, values: List[List[Any]], sheet_name: str) -> Dict[str, Any]:
        """Process raw sheet data into structured format"""
        if not values:
            return {'type': 'empty', 'data': {}}
        
        # Determine the type of data based on sheet name and content
        sheet_name_lower = sheet_name.lower()
        
        if 'checks' in sheet_name_lower or 'criteria' in sheet_name_lower:
            return self._process_validation_criteria(values)
        elif 'project' in sheet_name_lower and 'details' in sheet_name_lower:
            return self._process_project_details(values)
        elif 'vast cluster' in sheet_name_lower:
            return self._process_vast_cluster_data(values)
        elif 'rack diagram' in sheet_name_lower:
            return self._process_rack_diagram_data(values)
        elif 'network' in sheet_name_lower:
            return self._process_network_data(values)
        elif 'ip addresses' in sheet_name_lower:
            return self._process_ip_addresses_data(values)
        elif 'features' in sheet_name_lower and 'configuration' in sheet_name_lower:
            return self._process_features_configuration_data(values)
        else:
            return self._process_generic_data(values)
    
    def _process_validation_criteria(self, values: List[List[Any]]) -> Dict[str, Any]:
        """Process validation criteria data"""
        if len(values) < 2:
            return {'type': 'validation_criteria', 'data': {}}
        
        # Look for the header row with Check #, Check, Check Location, Status, etc.
        header_row_idx = None
        for i, row in enumerate(values):
            if len(row) > 0 and str(row[0]).strip().lower() in ['check #', 'check']:
                header_row_idx = i
                break
        
        if header_row_idx is None:
            return {'type': 'validation_criteria', 'data': {'raw_values': values}}
        
        headers = [str(cell).strip() for cell in values[header_row_idx]]
        checks = []
        
        for row in values[header_row_idx + 1:]:
            if len(row) == 0 or not str(row[0]).strip():
                continue
            
            check_data = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    check_data[header.lower().replace(' ', '_').replace('#', 'number')] = str(row[i]).strip()
            
            if check_data.get('check_number'):
                checks.append(check_data)
        
        return {
            'type': 'validation_criteria',
            'data': {
                'headers': headers,
                'checks': checks,
                'total_checks': len(checks)
            }
        }
    
    def _process_project_details(self, values: List[List[Any]]) -> Dict[str, Any]:
        """Process project details data"""
        project_data = {}
        
        # Look for key-value pairs in the first few rows
        for row in values[:20]:  # Check first 20 rows for project metadata
            if len(row) >= 2:
                key = str(row[0]).strip().lower()
                value = str(row[1]).strip() if len(row) > 1 else ''
                
                if 'project name' in key:
                    project_data['project_name'] = value
                elif 'case link' in key:
                    project_data['case_link'] = value
                elif 'se name' in key:
                    project_data['se_name'] = value
                elif 'plan link' in key:
                    project_data['plan_link'] = value
                elif 'reviewer' in key:
                    project_data['ps_reviewer'] = value
                elif 'review date' in key:
                    project_data['review_date'] = value
                elif 'status' in key:
                    project_data['overall_status'] = value
        
        return {
            'type': 'project_details',
            'data': project_data
        }
    
    def _process_vast_cluster_data(self, values: List[List[Any]]) -> Dict[str, Any]:
        """Process VAST cluster hardware data"""
        cluster_data = {
            'cboxes': [],
            'dboxes': [],
            'switches': [],
            'other_hardware': []
        }
        
        # Look for hardware specifications
        for row in values:
            if len(row) >= 2:
                item_name = str(row[0]).strip().lower()
                quantity = str(row[1]).strip() if len(row) > 1 else '0'
                
                if 'cbox' in item_name or 'cnode' in item_name:
                    cluster_data['cboxes'].append({
                        'name': str(row[0]).strip(),
                        'quantity': quantity,
                        'details': row[2:] if len(row) > 2 else []
                    })
                elif 'dbox' in item_name or 'dnode' in item_name:
                    cluster_data['dboxes'].append({
                        'name': str(row[0]).strip(),
                        'quantity': quantity,
                        'details': row[2:] if len(row) > 2 else []
                    })
                elif 'switch' in item_name:
                    cluster_data['switches'].append({
                        'name': str(row[0]).strip(),
                        'quantity': quantity,
                        'details': row[2:] if len(row) > 2 else []
                    })
        
        return {
            'type': 'vast_cluster',
            'data': cluster_data
        }
    
    def _process_rack_diagram_data(self, values: List[List[Any]]) -> Dict[str, Any]:
        """Process rack diagram data"""
        return {
            'type': 'rack_diagram',
            'data': {
                'raw_values': values,
                'has_diagram': len(values) > 5  # Simple check for content
            }
        }
    
    def _process_network_data(self, values: List[List[Any]]) -> Dict[str, Any]:
        """Process network configuration data"""
        network_data = {
            'network_settings': {},
            'cable_specifications': [],
            'switch_configurations': []
        }
        
        # Extract network configuration details
        for row in values:
            if len(row) >= 2:
                key = str(row[0]).strip().lower()
                value = str(row[1]).strip() if len(row) > 1 else ''
                
                if 'mtu' in key:
                    network_data['network_settings']['mtu'] = value
                elif 'vlan' in key:
                    network_data['network_settings']['vlan'] = value
                elif 'cable' in key:
                    network_data['cable_specifications'].append({
                        'type': str(row[0]).strip(),
                        'specification': value,
                        'details': row[2:] if len(row) > 2 else []
                    })
        
        return {
            'type': 'network_data',
            'data': network_data
        }
    
    def _process_ip_addresses_data(self, values: List[List[Any]]) -> Dict[str, Any]:
        """Process IP addresses worksheet data"""
        ip_data = {
            'management_ips': [],
            'data_ips': [],
            'network_ranges': {}
        }
        
        # Extract IP addressing information
        for row in values:
            if len(row) >= 2:
                key = str(row[0]).strip().lower()
                value = str(row[1]).strip() if len(row) > 1 else ''
                
                if 'management' in key and ('ip' in key or 'address' in key):
                    ip_data['management_ips'].append({
                        'description': str(row[0]).strip(),
                        'address': value,
                        'details': row[2:] if len(row) > 2 else []
                    })
                elif 'data' in key and ('ip' in key or 'address' in key):
                    ip_data['data_ips'].append({
                        'description': str(row[0]).strip(),
                        'address': value,
                        'details': row[2:] if len(row) > 2 else []
                    })
                elif 'subnet' in key or 'range' in key:
                    ip_data['network_ranges'][key] = value
        
        return {
            'type': 'ip_addresses',
            'data': ip_data
        }
    
    def _process_features_configuration_data(self, values: List[List[Any]]) -> Dict[str, Any]:
        """Process features and configuration data"""
        features_data = {
            'enabled_features': [],
            'configuration_settings': {},
            'installation_type': None
        }
        
        # Extract feature and configuration information
        for row in values:
            if len(row) >= 2:
                key = str(row[0]).strip().lower()
                value = str(row[1]).strip() if len(row) > 1 else ''
                
                if 'install' in key and ('easy' in key or 'manual' in key):
                    features_data['installation_type'] = value
                elif value.lower() in ['yes', 'enabled', 'true', 'on']:
                    features_data['enabled_features'].append(str(row[0]).strip())
                else:
                    features_data['configuration_settings'][key] = value
        
        return {
            'type': 'features_configuration',
            'data': features_data
        }
    
    def _process_generic_data(self, values: List[List[Any]]) -> Dict[str, Any]:
        """Process generic sheet data"""
        return {
            'type': 'generic',
            'data': {
                'raw_values': values,
                'row_count': len(values),
                'column_count': max(len(row) for row in values) if values else 0
            }
        }
    
    def extract_evaluation_criteria(self, url: str) -> Dict[str, Any]:
        """Extract evaluation criteria from the spreadsheet"""
        try:
            spreadsheet_id = self.extract_spreadsheet_id(url)
            if not spreadsheet_id:
                raise Exception("Invalid Google Sheets URL")
            
            all_data = self.extract_all_sheet_data(spreadsheet_id)
            
            # Extract evaluation criteria specifically
            evaluation_criteria = {}
            
            for sheet_name, sheet_data in all_data['sheets_data'].items():
                if sheet_data.get('processed_data', {}).get('type') == 'validation_criteria':
                    evaluation_criteria['validation_checks'] = sheet_data['processed_data']['data']
                elif sheet_data.get('processed_data', {}).get('type') == 'project_details':
                    evaluation_criteria.update(sheet_data['processed_data']['data'])
            
            return {
                'success': True,
                'data': evaluation_criteria,
                'metadata': all_data['metadata']
            }
            
        except Exception as e:
            logger.error(f"Error extracting evaluation criteria: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_site_survey_data(self, url: str, survey_part: int) -> Dict[str, Any]:
        """Extract site survey data (Part 1 or Part 2)"""
        try:
            spreadsheet_id = self.extract_spreadsheet_id(url)
            if not spreadsheet_id:
                raise Exception("Invalid Google Sheets URL")
            
            all_data = self.extract_all_sheet_data(spreadsheet_id)
            
            # Process site survey data
            site_survey_data = {
                'survey_part': survey_part,
                'sheets': {}
            }
            
            for sheet_name, sheet_data in all_data['sheets_data'].items():
                processed_data = sheet_data.get('processed_data', {})
                site_survey_data['sheets'][sheet_name] = processed_data.get('data', {})
            
            return {
                'success': True,
                'data': site_survey_data,
                'metadata': all_data['metadata']
            }
            
        except Exception as e:
            logger.error(f"Error extracting site survey data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

