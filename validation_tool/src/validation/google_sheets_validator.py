"""
Google Sheets specific validation module for processing Site Survey documents
and validation criteria from Google Sheets.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Fix imports for standalone execution
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from integrations.google_sheets import GoogleSheetsIntegration

# Try to import enhanced validation criteria, but don't fail if it doesn't exist
try:
    from data.enhanced_validation_criteria import ENHANCED_VALIDATION_CRITERIA
except ImportError:
    # Enhanced validation criteria not available - using default validation
    ENHANCED_VALIDATION_CRITERIA = {}

logger = logging.getLogger(__name__)

class GoogleSheetsValidator:
    """Validator for Google Sheets documents (Site Survey Parts 1 & 2)"""
    
    def __init__(self, sheets_integration: Optional[GoogleSheetsIntegration] = None):
        """
        Initialize Google Sheets validator.
        
        Args:
            sheets_integration: Google Sheets integration instance
        """
        self.sheets_integration = sheets_integration or GoogleSheetsIntegration()
        self.validation_criteria = ENHANCED_VALIDATION_CRITERIA
    
    def validate_site_survey_part1(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Validate Site Survey Part 1 Google Sheets document.
        
        Args:
            spreadsheet_id: Google Sheets document ID
            
        Returns:
            Validation results dictionary
        """
        try:
            # Get sheet metadata
            metadata = self.sheets_integration.get_sheet_metadata(spreadsheet_id)
            
            # Expected worksheets for Site Survey Part 1
            expected_worksheets = [
                'Release Notes',
                'Project Details', 
                'VAST Cluster',
                'Rack Diagram',
                'Racks and Power',
                'Network Details',
                'VAST Hardware Details'
            ]
            
            # Check worksheet structure
            worksheet_validation = self._validate_worksheet_structure(metadata, expected_worksheets)
            
            # Validate specific content areas
            content_validation = self._validate_site_survey_content(spreadsheet_id, 'part1')
            
            # Combine results
            validation_results = {
                'document_type': 'site_survey_part1',
                'spreadsheet_id': spreadsheet_id,
                'title': metadata.get('title', 'Unknown'),
                'validation_time': datetime.now().isoformat(),
                'worksheet_validation': worksheet_validation,
                'content_validation': content_validation,
                'overall_score': self._calculate_overall_score([worksheet_validation, content_validation]),
                'status': 'passed',  # Will be updated based on score
                'issues': [],
                'recommendations': []
            }
            
            # Determine status and collect issues
            validation_results['status'] = self._determine_status(validation_results['overall_score'])
            validation_results['issues'] = self._collect_issues(worksheet_validation, content_validation)
            validation_results['recommendations'] = self._generate_recommendations(validation_results['issues'])
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating Site Survey Part 1: {str(e)}")
            return {
                'document_type': 'site_survey_part1',
                'spreadsheet_id': spreadsheet_id,
                'validation_time': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error',
                'overall_score': 0.0
            }
    
    def validate_site_survey_part2(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Validate Site Survey Part 2 Google Sheets document.
        
        Args:
            spreadsheet_id: Google Sheets document ID
            
        Returns:
            Validation results dictionary
        """
        try:
            # Get sheet metadata
            metadata = self.sheets_integration.get_sheet_metadata(spreadsheet_id)
            
            # Expected worksheets for Site Survey Part 2
            expected_worksheets = [
                'Release Notes',
                'Import from Part 1',
                'Customer Support',
                'Features and Configuration',
                '#2 IP Addresses',
                'Network Diagram'
            ]
            
            # Check worksheet structure
            worksheet_validation = self._validate_worksheet_structure(metadata, expected_worksheets)
            
            # Validate specific content areas
            content_validation = self._validate_site_survey_content(spreadsheet_id, 'part2')
            
            # Combine results
            validation_results = {
                'document_type': 'site_survey_part2',
                'spreadsheet_id': spreadsheet_id,
                'title': metadata.get('title', 'Unknown'),
                'validation_time': datetime.now().isoformat(),
                'worksheet_validation': worksheet_validation,
                'content_validation': content_validation,
                'overall_score': self._calculate_overall_score([worksheet_validation, content_validation]),
                'status': 'passed',  # Will be updated based on score
                'issues': [],
                'recommendations': []
            }
            
            # Determine status and collect issues
            validation_results['status'] = self._determine_status(validation_results['overall_score'])
            validation_results['issues'] = self._collect_issues(worksheet_validation, content_validation)
            validation_results['recommendations'] = self._generate_recommendations(validation_results['issues'])
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating Site Survey Part 2: {str(e)}")
            return {
                'document_type': 'site_survey_part2',
                'spreadsheet_id': spreadsheet_id,
                'validation_time': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error',
                'overall_score': 0.0
            }
    
    def validate_validation_criteria_sheet(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Validate a Google Sheets document containing validation criteria.
        
        Args:
            spreadsheet_id: Google Sheets document ID
            
        Returns:
            Validation results dictionary
        """
        try:
            # Read the validation criteria from the sheet
            requirements = self.sheets_integration.read_requirements(spreadsheet_id)
            
            # Analyze the criteria structure
            criteria_analysis = self._analyze_validation_criteria(requirements)
            
            return {
                'document_type': 'validation_criteria',
                'spreadsheet_id': spreadsheet_id,
                'validation_time': datetime.now().isoformat(),
                'criteria_count': len(requirements),
                'criteria_analysis': criteria_analysis,
                'requirements': requirements,
                'status': 'processed',
                'overall_score': 1.0  # Criteria sheets are informational
            }
            
        except Exception as e:
            logger.error(f"Error validating criteria sheet: {str(e)}")
            return {
                'document_type': 'validation_criteria',
                'spreadsheet_id': spreadsheet_id,
                'validation_time': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error',
                'overall_score': 0.0
            }
    
    def _validate_worksheet_structure(self, metadata: Dict[str, Any], expected_worksheets: List[str]) -> Dict[str, Any]:
        """Validate that expected worksheets are present."""
        actual_worksheets = [sheet['title'] for sheet in metadata.get('sheets', [])]
        
        missing_worksheets = []
        extra_worksheets = []
        
        for expected in expected_worksheets:
            if expected not in actual_worksheets:
                missing_worksheets.append(expected)
        
        for actual in actual_worksheets:
            if actual not in expected_worksheets:
                extra_worksheets.append(actual)
        
        score = (len(expected_worksheets) - len(missing_worksheets)) / len(expected_worksheets)
        
        return {
            'expected_worksheets': expected_worksheets,
            'actual_worksheets': actual_worksheets,
            'missing_worksheets': missing_worksheets,
            'extra_worksheets': extra_worksheets,
            'score': score,
            'passed': len(missing_worksheets) == 0
        }
    
    def _validate_site_survey_content(self, spreadsheet_id: str, part: str) -> Dict[str, Any]:
        """Validate specific content areas of Site Survey documents."""
        validation_results = {
            'project_details': {'score': 0.0, 'issues': []},
            'technical_specs': {'score': 0.0, 'issues': []},
            'network_config': {'score': 0.0, 'issues': []},
            'hardware_details': {'score': 0.0, 'issues': []},
            'approval_status': {'score': 0.0, 'issues': []}
        }
        
        try:
            if part == 'part1':
                # Validate Project Details worksheet
                project_data = self._read_worksheet_data(spreadsheet_id, 'Project Details')
                validation_results['project_details'] = self._validate_project_details(project_data)
                
                # Validate VAST Cluster worksheet
                cluster_data = self._read_worksheet_data(spreadsheet_id, 'VAST Cluster')
                validation_results['technical_specs'] = self._validate_cluster_specs(cluster_data)
                
                # Validate Network Details worksheet
                network_data = self._read_worksheet_data(spreadsheet_id, 'Network Details')
                validation_results['network_config'] = self._validate_network_config(network_data)
                
                # Validate VAST Hardware Details worksheet
                hardware_data = self._read_worksheet_data(spreadsheet_id, 'VAST Hardware Details')
                validation_results['hardware_details'] = self._validate_hardware_details(hardware_data)
                
            elif part == 'part2':
                # Validate Import from Part 1 worksheet
                import_data = self._read_worksheet_data(spreadsheet_id, 'Import from Part 1')
                validation_results['project_details'] = self._validate_imported_project_details(import_data)
                
                # Validate Features and Configuration worksheet
                features_data = self._read_worksheet_data(spreadsheet_id, 'Features and Configuration')
                validation_results['technical_specs'] = self._validate_features_config(features_data)
                
                # Validate IP Addresses worksheet
                ip_data = self._read_worksheet_data(spreadsheet_id, '#2 IP Addresses')
                validation_results['network_config'] = self._validate_ip_addresses(ip_data)
                
        except Exception as e:
            logger.error(f"Error validating content for {part}: {str(e)}")
            for key in validation_results:
                validation_results[key]['issues'].append(f"Error reading {key}: {str(e)}")
        
        return validation_results
    
    def _read_worksheet_data(self, spreadsheet_id: str, worksheet_name: str) -> List[List[str]]:
        """Read data from a specific worksheet."""
        try:
            range_name = f"'{worksheet_name}'!A:Z"
            result = self.sheets_integration.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            return result.get('values', [])
            
        except Exception as e:
            logger.error(f"Error reading worksheet {worksheet_name}: {str(e)}")
            return []
    
    def _validate_project_details(self, data: List[List[str]]) -> Dict[str, Any]:
        """Validate project details from Site Survey Part 1."""
        issues = []
        score = 0.0
        total_checks = 6
        
        if not data:
            return {'score': 0.0, 'issues': ['Project Details worksheet is empty']}
        
        # Check for project name (typically in row 18, column B)
        if len(data) > 17 and len(data[17]) > 1 and data[17][1].strip():
            score += 1/total_checks
        else:
            issues.append('Project name is missing or empty')
        
        # Check for customer name (typically in row 19, column B)
        if len(data) > 18 and len(data[18]) > 1 and data[18][1].strip():
            score += 1/total_checks
        else:
            issues.append('Customer name is missing or empty')
        
        # Check for opportunity ID (typically in row 20, column B)
        if len(data) > 19 and len(data[19]) > 1 and data[19][1].strip():
            score += 1/total_checks
        else:
            issues.append('Opportunity ID is missing or empty')
        
        # Check for SE name (typically in row 21, column B)
        if len(data) > 20 and len(data[20]) > 1 and data[20][1].strip():
            score += 1/total_checks
        else:
            issues.append('SE name is missing or empty')
        
        # Check for install date (typically in row 22, column B)
        if len(data) > 21 and len(data[21]) > 1 and data[21][1].strip():
            score += 1/total_checks
        else:
            issues.append('Install date is missing or empty')
        
        # Check for PS reviewer (typically in row 23, column B)
        if len(data) > 22 and len(data[22]) > 1 and data[22][1].strip():
            score += 1/total_checks
        else:
            issues.append('PS reviewer is missing or empty')
        
        return {'score': score, 'issues': issues}
    
    def _validate_cluster_specs(self, data: List[List[str]]) -> Dict[str, Any]:
        """Validate cluster specifications."""
        issues = []
        score = 0.0
        total_checks = 4
        
        if not data:
            return {'score': 0.0, 'issues': ['VAST Cluster worksheet is empty']}
        
        # Look for cluster size information
        cluster_size_found = False
        for row in data:
            if len(row) > 1 and any('cluster' in str(cell).lower() and 'size' in str(cell).lower() for cell in row):
                cluster_size_found = True
                break
        
        if cluster_size_found:
            score += 1/total_checks
        else:
            issues.append('Cluster size specification not found')
        
        # Look for node count
        node_count_found = False
        for row in data:
            if len(row) > 1 and any('node' in str(cell).lower() for cell in row):
                node_count_found = True
                break
        
        if node_count_found:
            score += 1/total_checks
        else:
            issues.append('Node count specification not found')
        
        # Look for software version
        version_found = False
        for row in data:
            if len(row) > 1 and any(re.search(r'\d+\.\d+', str(cell)) for cell in row):
                version_found = True
                break
        
        if version_found:
            score += 1/total_checks
        else:
            issues.append('Software version not specified')
        
        # Check for installation type
        install_type_found = False
        for row in data:
            if len(row) > 1 and any('install' in str(cell).lower() for cell in row):
                install_type_found = True
                break
        
        if install_type_found:
            score += 1/total_checks
        else:
            issues.append('Installation type not specified')
        
        return {'score': score, 'issues': issues}
    
    def _validate_network_config(self, data: List[List[str]]) -> Dict[str, Any]:
        """Validate network configuration."""
        issues = []
        score = 0.0
        total_checks = 5
        
        if not data:
            return {'score': 0.0, 'issues': ['Network Details worksheet is empty']}
        
        # Look for VLAN configuration
        vlan_found = False
        for row in data:
            if len(row) > 1 and any('vlan' in str(cell).lower() for cell in row):
                vlan_found = True
                break
        
        if vlan_found:
            score += 1/total_checks
        else:
            issues.append('VLAN configuration not found')
        
        # Look for IP addresses
        ip_found = False
        for row in data:
            if len(row) > 1:
                for cell in row:
                    if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', str(cell)):
                        ip_found = True
                        break
                if ip_found:
                    break
        
        if ip_found:
            score += 1/total_checks
        else:
            issues.append('IP addresses not specified')
        
        # Look for switch information
        switch_found = False
        for row in data:
            if len(row) > 1 and any('switch' in str(cell).lower() for cell in row):
                switch_found = True
                break
        
        if switch_found:
            score += 1/total_checks
        else:
            issues.append('Switch configuration not found')
        
        # Look for network topology
        topology_found = False
        for row in data:
            if len(row) > 1 and any('topology' in str(cell).lower() or 'network' in str(cell).lower() for cell in row):
                topology_found = True
                break
        
        if topology_found:
            score += 1/total_checks
        else:
            issues.append('Network topology not documented')
        
        # Look for bandwidth requirements
        bandwidth_found = False
        for row in data:
            if len(row) > 1 and any('bandwidth' in str(cell).lower() or 'gbps' in str(cell).lower() for cell in row):
                bandwidth_found = True
                break
        
        if bandwidth_found:
            score += 1/total_checks
        else:
            issues.append('Bandwidth requirements not specified')
        
        return {'score': score, 'issues': issues}
    
    def _validate_hardware_details(self, data: List[List[str]]) -> Dict[str, Any]:
        """Validate hardware details."""
        issues = []
        score = 0.0
        total_checks = 4
        
        if not data:
            return {'score': 0.0, 'issues': ['VAST Hardware Details worksheet is empty']}
        
        # Look for hardware inventory
        inventory_found = False
        for row in data:
            if len(row) > 1 and any('quantity' in str(cell).lower() or 'qty' in str(cell).lower() for cell in row):
                inventory_found = True
                break
        
        if inventory_found:
            score += 1/total_checks
        else:
            issues.append('Hardware inventory not found')
        
        # Look for part numbers
        part_numbers_found = False
        for row in data:
            if len(row) > 1 and any('part' in str(cell).lower() and 'number' in str(cell).lower() for cell in row):
                part_numbers_found = True
                break
        
        if part_numbers_found:
            score += 1/total_checks
        else:
            issues.append('Part numbers not specified')
        
        # Look for power requirements
        power_found = False
        for row in data:
            if len(row) > 1 and any('power' in str(cell).lower() or 'watt' in str(cell).lower() for cell in row):
                power_found = True
                break
        
        if power_found:
            score += 1/total_checks
        else:
            issues.append('Power requirements not specified')
        
        # Look for rack space requirements
        rack_found = False
        for row in data:
            if len(row) > 1 and any('rack' in str(cell).lower() or 'ru' in str(cell).lower() for cell in row):
                rack_found = True
                break
        
        if rack_found:
            score += 1/total_checks
        else:
            issues.append('Rack space requirements not specified')
        
        return {'score': score, 'issues': issues}
    
    def _validate_imported_project_details(self, data: List[List[str]]) -> Dict[str, Any]:
        """Validate imported project details from Site Survey Part 2."""
        # Similar validation to Part 1 but checking for imported data consistency
        return self._validate_project_details(data)
    
    def _validate_features_config(self, data: List[List[str]]) -> Dict[str, Any]:
        """Validate features and configuration from Site Survey Part 2."""
        issues = []
        score = 0.0
        total_checks = 3
        
        if not data:
            return {'score': 0.0, 'issues': ['Features and Configuration worksheet is empty']}
        
        # Look for feature selections
        features_found = False
        for row in data:
            if len(row) > 1 and any('feature' in str(cell).lower() for cell in row):
                features_found = True
                break
        
        if features_found:
            score += 1/total_checks
        else:
            issues.append('Feature selections not found')
        
        # Look for configuration parameters
        config_found = False
        for row in data:
            if len(row) > 1 and any('config' in str(cell).lower() for cell in row):
                config_found = True
                break
        
        if config_found:
            score += 1/total_checks
        else:
            issues.append('Configuration parameters not specified')
        
        # Look for performance settings
        performance_found = False
        for row in data:
            if len(row) > 1 and any('performance' in str(cell).lower() or 'throughput' in str(cell).lower() for cell in row):
                performance_found = True
                break
        
        if performance_found:
            score += 1/total_checks
        else:
            issues.append('Performance settings not documented')
        
        return {'score': score, 'issues': issues}
    
    def _validate_ip_addresses(self, data: List[List[str]]) -> Dict[str, Any]:
        """Validate IP address configuration from Site Survey Part 2."""
        issues = []
        score = 0.0
        total_checks = 4
        
        if not data:
            return {'score': 0.0, 'issues': ['IP Addresses worksheet is empty']}
        
        # Count valid IP addresses
        ip_count = 0
        for row in data:
            if len(row) > 1:
                for cell in row:
                    if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', str(cell)):
                        ip_count += 1
        
        if ip_count >= 5:  # Expect at least 5 IP addresses for a typical installation
            score += 1/total_checks
        else:
            issues.append(f'Insufficient IP addresses specified (found {ip_count}, expected at least 5)')
        
        # Look for subnet information
        subnet_found = False
        for row in data:
            if len(row) > 1 and any('subnet' in str(cell).lower() or '/24' in str(cell) or '/16' in str(cell) for cell in row):
                subnet_found = True
                break
        
        if subnet_found:
            score += 1/total_checks
        else:
            issues.append('Subnet information not specified')
        
        # Look for gateway information
        gateway_found = False
        for row in data:
            if len(row) > 1 and any('gateway' in str(cell).lower() for cell in row):
                gateway_found = True
                break
        
        if gateway_found:
            score += 1/total_checks
        else:
            issues.append('Gateway information not specified')
        
        # Look for DNS information
        dns_found = False
        for row in data:
            if len(row) > 1 and any('dns' in str(cell).lower() for cell in row):
                dns_found = True
                break
        
        if dns_found:
            score += 1/total_checks
        else:
            issues.append('DNS information not specified')
        
        return {'score': score, 'issues': issues}
    
    def _analyze_validation_criteria(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze validation criteria structure."""
        if not requirements:
            return {'error': 'No requirements found'}
        
        # Analyze the structure of the criteria
        categories = set()
        total_criteria = len(requirements)
        
        for req in requirements:
            if 'category' in req:
                categories.add(req['category'])
        
        return {
            'total_criteria': total_criteria,
            'categories': list(categories),
            'category_count': len(categories),
            'structure_valid': total_criteria > 0 and len(categories) > 0
        }
    
    def _calculate_overall_score(self, validation_results: List[Dict[str, Any]]) -> float:
        """Calculate overall validation score."""
        if not validation_results:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for result in validation_results:
            if isinstance(result, dict):
                if 'score' in result:
                    total_score += result['score']
                    total_weight += 1.0
                else:
                    # Handle nested results
                    for key, value in result.items():
                        if isinstance(value, dict) and 'score' in value:
                            total_score += value['score']
                            total_weight += 1.0
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_status(self, score: float) -> str:
        """Determine validation status based on score."""
        if score >= 0.8:
            return 'passed'
        elif score >= 0.6:
            return 'partial'
        else:
            return 'failed'
    
    def _collect_issues(self, *validation_results) -> List[str]:
        """Collect all issues from validation results."""
        all_issues = []
        
        for result in validation_results:
            if isinstance(result, dict):
                if 'issues' in result:
                    all_issues.extend(result['issues'])
                else:
                    # Handle nested results
                    for key, value in result.items():
                        if isinstance(value, dict) and 'issues' in value:
                            all_issues.extend(value['issues'])
        
        return all_issues
    
    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on identified issues."""
        recommendations = []
        
        for issue in issues:
            if 'missing' in issue.lower():
                recommendations.append(f"Add the missing information: {issue}")
            elif 'empty' in issue.lower():
                recommendations.append(f"Fill in the empty field: {issue}")
            elif 'not found' in issue.lower():
                recommendations.append(f"Include the required information: {issue}")
            elif 'not specified' in issue.lower():
                recommendations.append(f"Specify the required details: {issue}")
            else:
                recommendations.append(f"Address the issue: {issue}")
        
        return recommendations

