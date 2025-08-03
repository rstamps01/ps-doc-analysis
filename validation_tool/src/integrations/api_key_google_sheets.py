"""
API Key-based Google Sheets Integration
Uses Google API key for accessing public spreadsheets
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)

class APIKeyGoogleSheetsIntegration:
    """Google Sheets integration using API key for public spreadsheets"""
    
    def __init__(self, api_key: str = None):
        import os
        self.api_key = api_key or os.environ.get('GOOGLE_SHEETS_API_KEY')
        if not self.api_key:
            raise ValueError("Google Sheets API key is required. Set GOOGLE_SHEETS_API_KEY environment variable or pass api_key parameter.")
        self.base_url = "https://sheets.googleapis.com/v4/spreadsheets"
        
    def test_connection(self) -> Dict[str, Any]:
        """Test Google Sheets API connection with API key"""
        try:
            # Test with a known public spreadsheet
            test_spreadsheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            url = f"{self.base_url}/{test_spreadsheet_id}?key={self.api_key}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return {
                    'connected': True,
                    'api_key_valid': True,
                    'message': 'API key connection successful'
                }
            else:
                return {
                    'connected': False,
                    'api_key_valid': False,
                    'error': f"API request failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Google Sheets API key connection test failed: {str(e)}")
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
            url = f"{self.base_url}/{spreadsheet_id}?key={self.api_key}"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
            data = response.json()
            
            sheets = []
            for sheet in data.get('sheets', []):
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
                'title': data.get('properties', {}).get('title', ''),
                'locale': data.get('properties', {}).get('locale', ''),
                'sheets': sheets,
                'total_sheets': len(sheets)
            }
            
        except Exception as e:
            logger.error(f"Error getting spreadsheet metadata: {str(e)}")
            raise
    
    def extract_sheet_data(self, spreadsheet_id: str, sheet_name: str, range_name: str = None) -> Dict[str, Any]:
        """Extract data from a specific sheet"""
        try:
            # If no range specified, get all data from the sheet
            if range_name is None:
                range_name = sheet_name
            else:
                range_name = f"{sheet_name}!{range_name}"
            
            # URL encode the range
            encoded_range = quote(range_name)
            url = f"{self.base_url}/{spreadsheet_id}/values/{encoded_range}?key={self.api_key}&valueRenderOption=UNFORMATTED_VALUE&dateTimeRenderOption=FORMATTED_STRING"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
            data = response.json()
            values = data.get('values', [])
            
            # Process the data into a more structured format
            processed_data = self._process_sheet_data(values, sheet_name)
            
            return {
                'sheet_name': sheet_name,
                'range': data.get('range', ''),
                'major_dimension': data.get('majorDimension', 'ROWS'),
                'values': values,
                'processed_data': processed_data,
                'row_count': len(values),
                'column_count': max(len(row) for row in values) if values else 0
            }
            
        except Exception as e:
            logger.error(f"Error extracting sheet data: {str(e)}")
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
    
    def _process_sheet_data(self, values: List[List[Any]], sheet_name: str) -> Dict[str, Any]:
        """Process raw sheet data into structured format"""
        if not values:
            return {'type': 'empty', 'data': {}}
        
        # Determine the type of data based on sheet name and content
        sheet_name_lower = sheet_name.lower()
        
        if 'checks' in sheet_name_lower or 'criteria' in sheet_name_lower or 'project name' in sheet_name_lower:
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
        
        # Extract project metadata from the top rows
        project_data = {}
        checks = []
        
        # Look for project metadata in the first rows
        for i, row in enumerate(values[:10]):
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
        
        # Look for the header row with Check #, Check, Check Location, Status, etc.
        header_row_idx = None
        for i, row in enumerate(values):
            if len(row) > 0 and str(row[0]).strip().lower() in ['check #', 'check']:
                header_row_idx = i
                break
        
        if header_row_idx is not None:
            headers = [str(cell).strip() for cell in values[header_row_idx]]
            
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
                'project_metadata': project_data,
                'headers': headers if header_row_idx is not None else [],
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
                    criteria_data = sheet_data['processed_data']['data']
                    evaluation_criteria['validation_checks'] = criteria_data
                    # Also extract project metadata if available
                    if 'project_metadata' in criteria_data:
                        evaluation_criteria.update(criteria_data['project_metadata'])
            
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

