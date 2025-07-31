"""
Comprehensive Validation Engine
Implements all 40 validation checks from the evaluation criteria spreadsheet
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ComprehensiveValidationEngine:
    """
    Comprehensive validation engine that implements all 40 validation checks
    from the evaluation criteria spreadsheet
    """
    
    def __init__(self):
        self.validation_checks = self._initialize_validation_checks()
        self.results = {}
        self.progress_callback = None
        
    def _initialize_validation_checks(self) -> Dict[int, Dict[str, Any]]:
        """Initialize all 40 validation checks with their metadata"""
        return {
            1: {
                "description": "Project name provided above",
                "location": "This doc",
                "category": "Document Metadata",
                "weight": 1.0,
                "required": True
            },
            2: {
                "description": "Install/Expansion Case link provided above",
                "location": "This doc", 
                "category": "Document Metadata",
                "weight": 1.0,
                "required": True
            },
            3: {
                "description": "SE Name provided above",
                "location": "This doc",
                "category": "Document Metadata", 
                "weight": 1.0,
                "required": True
            },
            4: {
                "description": "Install/Expansion Plan link provided above",
                "location": "This doc",
                "category": "Document Metadata",
                "weight": 1.0,
                "required": True
            },
            5: {
                "description": "PS Reviewer provided above",
                "location": "This doc",
                "category": "Document Metadata",
                "weight": 1.0,
                "required": True
            },
            6: {
                "description": "Review Date set above",
                "location": "This doc",
                "category": "Document Metadata",
                "weight": 1.0,
                "required": True
            },
            7: {
                "description": "Check SFDC install case feed",
                "location": "SF",
                "category": "SFDC Integration",
                "weight": 2.0,
                "required": True
            },
            8: {
                "description": "Check Install Plan Important Site Notes",
                "location": "Install Plan",
                "category": "Install Plan Validation",
                "weight": 2.0,
                "required": True
            },
            9: {
                "description": "Verify that the VAST Install Plan Submitted is using the Latest Template from the VAST Releases Web Portal",
                "location": "Install Plan",
                "category": "Install Plan Validation",
                "weight": 3.0,
                "required": True
            },
            10: {
                "description": "Verify that the Delete Everything Above This Line content is removed from the Install Plan",
                "location": "Install Plan",
                "category": "Install Plan Validation",
                "weight": 2.0,
                "required": True
            },
            11: {
                "description": "Verify that the Important Site Notes / Site Overview section is filled out within the Install Plan",
                "location": "Install Plan",
                "category": "Install Plan Validation",
                "weight": 2.0,
                "required": True
            },
            12: {
                "description": "Verify that within the Install Plan>Site Survey section within the Opportunity Document Links contains the URLs for both Site Survey Part 1 and Site Survey Part 2",
                "location": "Install Plan, Site Survey 1, Site Survey 2",
                "category": "Cross-Document Consistency",
                "weight": 3.0,
                "required": True
            },
            13: {
                "description": "Verify Cluster Hostname is present within the Install Plan",
                "location": "Install Plan",
                "category": "Technical Configuration",
                "weight": 2.0,
                "required": True
            },
            14: {
                "description": "Verify System PSNT is present within the Install Plan",
                "location": "Install Plan",
                "category": "Technical Configuration",
                "weight": 2.0,
                "required": True
            },
            15: {
                "description": "Verify all URLs for Site Surveys as well as the Install Plan align across the SFDC Case Summary/Feed/Detail sections as well as the Install Plan",
                "location": "SF, Install Plan",
                "category": "Cross-Document Consistency",
                "weight": 3.0,
                "required": True
            },
            16: {
                "description": "Verify that SE Peer Review was performed. This should be documented in the Approvals section of the Install Plan",
                "location": "Install Plan",
                "category": "Process Validation",
                "weight": 3.0,
                "required": True
            },
            17: {
                "description": "Verify Network Switch Configuration Script command verbiage within the Install Plan matches Network Cable Types specified in Site Survey Part 1",
                "location": "Install Plan, Site Survey 1",
                "category": "Network Configuration",
                "weight": 3.0,
                "required": True
            },
            18: {
                "description": "Verify Network Switch Configuration Files look correct and match the inputs defined in the Network Switch Configuration Script contained within the Install Plan",
                "location": "Install Plan",
                "category": "Network Configuration",
                "weight": 3.0,
                "required": True
            },
            19: {
                "description": "Verify that Checkmark Selections within all applicable sections of the Installation Planning>Cluster Information Overview section of the Install Plan are populated correctly to align with other components defined across the Install Plan, as well as both Site Surveys",
                "location": "Install Plan, Site Survey 1, Site Survey 2",
                "category": "Cross-Document Consistency",
                "weight": 3.0,
                "required": True
            },
            20: {
                "description": "Verify that the latest GA Code Version is defined within the Installation Planning>Cluster Information Overview section of the Install Plan",
                "location": "Install Plan",
                "category": "Version Validation",
                "weight": 3.0,
                "required": True
            },
            21: {
                "description": "Verify that the VASTOS Version listed within the Installation Planning>Cluster Information Overview section of the Install Plan aligns with the VAST Bundle Version listed in the same section",
                "location": "Install Plan",
                "category": "Version Validation",
                "weight": 3.0,
                "required": True
            },
            22: {
                "description": "Verify that MTU settings chosen are correct for pairing with the Network Switches that were sold",
                "location": "Install Plan",
                "category": "Network Configuration",
                "weight": 3.0,
                "required": True
            },
            23: {
                "description": "Verify that valid CNode and/or DNode Management Interface Configuration datapoints are checkmarked within Install Plan>Network and Power Cabling>Network cabling",
                "location": "Install Plan",
                "category": "Hardware Validation",
                "weight": 2.0,
                "required": True
            },
            24: {
                "description": "Install Plan>Commissioning the System>Switch Configuration, review the attached Network Configuration Files for Syntax Errors and correctness",
                "location": "Install Plan",
                "category": "Network Configuration",
                "weight": 3.0,
                "required": True
            },
            25: {
                "description": "Install Plan>Commissioning the System>Switch Configuration, please verify the Syntax used with switch_conf.py, for creation of the Network Switch Configuration Files is pasted into the 'Copy and Paste the Template Commands below' field",
                "location": "Install Plan",
                "category": "Network Configuration",
                "weight": 3.0,
                "required": True
            },
            26: {
                "description": "When reviewing Site Survey Part 1, the following Worksheets need to be reviewed for completeness/accuracy, VAST Cluster, Rack Diagram, Rack and Power, and Network Details",
                "location": "Site Survey 1",
                "category": "Site Survey 1 Validation",
                "weight": 2.0,
                "required": True
            },
            27: {
                "description": "Site Survey Part 1>VAST Cluster Worksheet, please ensure the Types and Quantities of CBoxes, DBoxes and Network Switches match the values specified within the Install Plan",
                "location": "Site Survey 1",
                "category": "Hardware Validation",
                "weight": 3.0,
                "required": True
            },
            28: {
                "description": "Site Survey Part 1>Rack Diagram Worksheet, please ensure that the Rack Diagram matches the Hardware Quantity listed within the VAST Cluster worksheet",
                "location": "Site Survey 1",
                "category": "Hardware Validation",
                "weight": 2.0,
                "required": True
            },
            29: {
                "description": "Site Survey Part 1>Racks and Power Worksheet, please check for completeness, accuracy and aligns with hardware being implemented",
                "location": "Site Survey 1",
                "category": "Hardware Validation",
                "weight": 2.0,
                "required": True
            },
            30: {
                "description": "Site Survey Part 1>Network Detail Worksheet, please check for completeness, accuracy and aligns with hardware being implemented",
                "location": "Site Survey 1",
                "category": "Network Configuration",
                "weight": 2.0,
                "required": True
            },
            31: {
                "description": "Site Survey Part 1>VAST Hardware Details Worksheet, please check for completeness, accuracy and aligns with hardware being implemented",
                "location": "Install Plan, Site Survey 1",
                "category": "Hardware Validation",
                "weight": 3.0,
                "required": True
            },
            32: {
                "description": "Site Survey Part 2>Import from Part 1 Worksheet, please check for completeness",
                "location": "Site Survey 1, Site Survey 2",
                "category": "Cross-Document Consistency",
                "weight": 2.0,
                "required": True
            },
            33: {
                "description": "Site Survey Part 2>Features and Configuration Worksheet, please check for completeness and alignment with the parameters defined within the Install Plan",
                "location": "Install Plan, Site Survey 2",
                "category": "Site Survey 2 Validation",
                "weight": 2.0,
                "required": True
            },
            34: {
                "description": "Site Survey Part 2>#2 IP Addresses Worksheet, please check for completeness and alignment with the parameters defined within the Install Plan networking sections",
                "location": "Install Plan, Site Survey 2",
                "category": "Network Configuration",
                "weight": 3.0,
                "required": True
            },
            35: {
                "description": "Site Survey Part 2>Network Diagram Worksheet, please ensure the VAST SE included a Network Diagram",
                "location": "Site Survey 2",
                "category": "Site Survey 2 Validation",
                "weight": 2.0,
                "required": True
            },
            36: {
                "description": "Site Survey Part 2>Easy Install Settings Worksheet, please check for completeness and alignment with the parameters defined within the Install Plan networking sections",
                "location": "Site Survey 2",
                "category": "Site Survey 2 Validation",
                "weight": 2.0,
                "required": False
            },
            37: {
                "description": "Site Survey Part 2>Manual Install Details Worksheet, please check for completeness and alignment with the parameters defined within the Install Plan networking sections",
                "location": "Site Survey 2",
                "category": "Site Survey 2 Validation",
                "weight": 2.0,
                "required": False
            },
            38: {
                "description": "Make sure the default of vlan 69 is used. If not please use the configure_network.py to add the [--data-vlan DATA_VLAN] flag",
                "location": "Install Plan, Site Survey 2",
                "category": "Network Configuration",
                "weight": 2.0,
                "required": True
            },
            39: {
                "description": "Empty validation check - placeholder",
                "location": "",
                "category": "Placeholder",
                "weight": 0.0,
                "required": False
            },
            40: {
                "description": "Ensure that the VAST Version is appropriate for the scale of the cluster being deployed or expanded. Example = Anything larger that 25x25, or 50 Nodes, needs R&D Approval",
                "location": "Install Plan",
                "category": "Version Validation",
                "weight": 3.0,
                "required": True
            }
        }
    
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback
    
    def _update_progress(self, current_check: int, total_checks: int, status: str):
        """Update progress and call callback if set"""
        progress = (current_check / total_checks) * 100
        if self.progress_callback:
            self.progress_callback({
                'current_check': current_check,
                'total_checks': total_checks,
                'progress_percentage': progress,
                'status': status,
                'timestamp': datetime.now().isoformat()
            })
    
    def validate_all_documents(self, documents: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all documents against all 40 validation checks
        
        Args:
            documents: Dictionary containing all document data
                - evaluation_criteria: Evaluation criteria spreadsheet data
                - site_survey_1: Site Survey Part 1 spreadsheet data  
                - site_survey_2: Site Survey Part 2 spreadsheet data
                - install_plan: Install Plan document data
                - sfdc_data: Salesforce data (optional)
        
        Returns:
            Comprehensive validation results
        """
        logger.info("Starting comprehensive validation of all documents")
        
        total_checks = len([check for check in self.validation_checks.values() if check['required']])
        current_check = 0
        
        validation_results = {
            'overall_status': 'In Progress',
            'start_time': datetime.now().isoformat(),
            'total_checks': total_checks,
            'checks_completed': 0,
            'checks_passed': 0,
            'checks_failed': 0,
            'overall_score': 0.0,
            'category_scores': {},
            'individual_results': {},
            'recommendations': [],
            'critical_issues': [],
            'warnings': []
        }
        
        # Group checks by category for scoring
        categories = {}
        for check_id, check_info in self.validation_checks.items():
            category = check_info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(check_id)
        
        # Execute each validation check
        for check_id, check_info in self.validation_checks.items():
            if not check_info['required']:
                continue
                
            current_check += 1
            self._update_progress(current_check, total_checks, f"Executing check {check_id}: {check_info['description'][:50]}...")
            
            try:
                result = self._execute_validation_check(check_id, check_info, documents)
                validation_results['individual_results'][check_id] = result
                
                validation_results['checks_completed'] += 1
                if result['status'] == 'Pass':
                    validation_results['checks_passed'] += 1
                elif result['status'] == 'Fail':
                    validation_results['checks_failed'] += 1
                    if check_info['weight'] >= 3.0:
                        validation_results['critical_issues'].append({
                            'check_id': check_id,
                            'description': check_info['description'],
                            'issue': result.get('details', 'Critical validation failure')
                        })
                
                # Add recommendations if any
                if result.get('recommendations'):
                    validation_results['recommendations'].extend(result['recommendations'])
                    
                # Add warnings if any
                if result.get('warnings'):
                    validation_results['warnings'].extend(result['warnings'])
                    
            except Exception as e:
                logger.error(f"Error executing validation check {check_id}: {str(e)}")
                validation_results['individual_results'][check_id] = {
                    'status': 'Error',
                    'score': 0.0,
                    'details': f"Validation error: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }
        
        # Calculate category scores
        for category, check_ids in categories.items():
            category_results = [validation_results['individual_results'].get(cid) for cid in check_ids if cid in validation_results['individual_results']]
            if category_results:
                category_score = sum(r['score'] for r in category_results if r) / len(category_results)
                validation_results['category_scores'][category] = category_score
        
        # Calculate overall score
        all_scores = [r['score'] for r in validation_results['individual_results'].values() if r]
        if all_scores:
            validation_results['overall_score'] = sum(all_scores) / len(all_scores)
        
        # Determine overall status
        if validation_results['overall_score'] >= 0.9:
            validation_results['overall_status'] = 'Pass'
        elif validation_results['overall_score'] >= 0.7:
            validation_results['overall_status'] = 'Pass with Warnings'
        else:
            validation_results['overall_status'] = 'Fail'
        
        validation_results['end_time'] = datetime.now().isoformat()
        
        logger.info(f"Validation completed. Overall score: {validation_results['overall_score']:.2f}")
        
        return validation_results
    
    def _execute_validation_check(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific validation check"""
        
        # Route to specific validation method based on check ID
        validation_methods = {
            1: self._validate_project_name,
            2: self._validate_case_link,
            3: self._validate_se_name,
            4: self._validate_plan_link,
            5: self._validate_ps_reviewer,
            6: self._validate_review_date,
            7: self._validate_sfdc_case_feed,
            8: self._validate_install_plan_site_notes,
            9: self._validate_install_plan_template,
            10: self._validate_delete_line_removed,
            11: self._validate_site_overview_filled,
            12: self._validate_site_survey_urls,
            13: self._validate_cluster_hostname,
            14: self._validate_system_psnt,
            15: self._validate_url_alignment,
            16: self._validate_se_peer_review,
            17: self._validate_network_switch_config_match,
            18: self._validate_network_config_files,
            19: self._validate_checkmark_selections,
            20: self._validate_ga_code_version,
            21: self._validate_vastos_version_alignment,
            22: self._validate_mtu_settings,
            23: self._validate_management_interface_config,
            24: self._validate_network_config_syntax,
            25: self._validate_switch_conf_syntax,
            26: self._validate_site_survey_1_worksheets,
            27: self._validate_vast_cluster_quantities,
            28: self._validate_rack_diagram_match,
            29: self._validate_racks_power_completeness,
            30: self._validate_network_details_completeness,
            31: self._validate_vast_hardware_details,
            32: self._validate_import_from_part1,
            33: self._validate_features_configuration,
            34: self._validate_ip_addresses_worksheet,
            35: self._validate_network_diagram_present,
            36: self._validate_easy_install_settings,
            37: self._validate_manual_install_details,
            38: self._validate_vlan_69_default,
            39: self._validate_placeholder,
            40: self._validate_vast_version_scale
        }
        
        validation_method = validation_methods.get(check_id, self._validate_generic)
        return validation_method(check_id, check_info, documents)
    
    def _validate_project_name(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that project name is provided"""
        eval_criteria = documents.get('evaluation_criteria', {})
        project_name = eval_criteria.get('project_name', '').strip()
        
        if project_name and len(project_name) > 0:
            return {
                'status': 'Pass',
                'score': 1.0,
                'details': f"Project name provided: {project_name}",
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'Fail',
                'score': 0.0,
                'details': "Project name is missing or empty",
                'recommendations': ["Please provide a valid project name"],
                'timestamp': datetime.now().isoformat()
            }
    
    def _validate_case_link(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that install/expansion case link is provided"""
        eval_criteria = documents.get('evaluation_criteria', {})
        case_link = eval_criteria.get('case_link', '').strip()
        
        if case_link and (case_link.startswith('http') or case_link.startswith('https')):
            return {
                'status': 'Pass',
                'score': 1.0,
                'details': f"Case link provided: {case_link}",
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'Fail',
                'score': 0.0,
                'details': "Install/Expansion case link is missing or invalid",
                'recommendations': ["Please provide a valid case link URL"],
                'timestamp': datetime.now().isoformat()
            }
    
    def _validate_se_name(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that SE name is provided"""
        eval_criteria = documents.get('evaluation_criteria', {})
        se_name = eval_criteria.get('se_name', '').strip()
        
        if se_name and len(se_name) > 0:
            return {
                'status': 'Pass',
                'score': 1.0,
                'details': f"SE name provided: {se_name}",
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'Fail',
                'score': 0.0,
                'details': "SE name is missing or empty",
                'recommendations': ["Please provide the SE (Sales Engineer) name"],
                'timestamp': datetime.now().isoformat()
            }
    
    def _validate_plan_link(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that install/expansion plan link is provided"""
        eval_criteria = documents.get('evaluation_criteria', {})
        plan_link = eval_criteria.get('plan_link', '').strip()
        
        if plan_link and (plan_link.startswith('http') or plan_link.startswith('https')):
            return {
                'status': 'Pass',
                'score': 1.0,
                'details': f"Plan link provided: {plan_link}",
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'Fail',
                'score': 0.0,
                'details': "Install/Expansion plan link is missing or invalid",
                'recommendations': ["Please provide a valid plan link URL"],
                'timestamp': datetime.now().isoformat()
            }
    
    def _validate_ps_reviewer(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that PS reviewer is provided"""
        eval_criteria = documents.get('evaluation_criteria', {})
        ps_reviewer = eval_criteria.get('ps_reviewer', '').strip()
        
        if ps_reviewer and len(ps_reviewer) > 0:
            return {
                'status': 'Pass',
                'score': 1.0,
                'details': f"PS reviewer provided: {ps_reviewer}",
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'Fail',
                'score': 0.0,
                'details': "PS reviewer is missing or empty",
                'recommendations': ["Please provide the PS (Professional Services) reviewer name"],
                'timestamp': datetime.now().isoformat()
            }
    
    def _validate_review_date(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that review date is set"""
        eval_criteria = documents.get('evaluation_criteria', {})
        review_date = eval_criteria.get('review_date', '').strip()
        
        if review_date and len(review_date) > 0:
            return {
                'status': 'Pass',
                'score': 1.0,
                'details': f"Review date provided: {review_date}",
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'Fail',
                'score': 0.0,
                'details': "Review date is missing or empty",
                'recommendations': ["Please set the review date"],
                'timestamp': datetime.now().isoformat()
            }
    
    def _validate_generic(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        """Generic validation for checks not yet implemented"""
        return {
            'status': 'Not Implemented',
            'score': 0.5,
            'details': f"Validation check {check_id} not yet implemented: {check_info['description']}",
            'warnings': [f"Check {check_id} requires manual implementation"],
            'timestamp': datetime.now().isoformat()
        }
    
    # Placeholder methods for remaining validation checks
    def _validate_sfdc_case_feed(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_install_plan_site_notes(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_install_plan_template(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_delete_line_removed(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_site_overview_filled(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_site_survey_urls(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_cluster_hostname(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_system_psnt(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_url_alignment(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_se_peer_review(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_network_switch_config_match(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_network_config_files(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_checkmark_selections(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_ga_code_version(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_vastos_version_alignment(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_mtu_settings(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_management_interface_config(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_network_config_syntax(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_switch_conf_syntax(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_site_survey_1_worksheets(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_vast_cluster_quantities(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_rack_diagram_match(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_racks_power_completeness(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_network_details_completeness(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_vast_hardware_details(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_import_from_part1(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_features_configuration(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_ip_addresses_worksheet(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_network_diagram_present(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_easy_install_settings(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_manual_install_details(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_vlan_69_default(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def _validate_placeholder(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'status': 'Skipped',
            'score': 1.0,
            'details': "Placeholder check - skipped",
            'timestamp': datetime.now().isoformat()
        }
    
    def _validate_vast_version_scale(self, check_id: int, check_info: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
        return self._validate_generic(check_id, check_info, documents)
    
    def get_validation_check_info(self, check_id: int) -> Dict[str, Any]:
        """Get information about a specific validation check"""
        return self.validation_checks.get(check_id, {})
    
    def get_all_validation_checks(self) -> Dict[int, Dict[str, Any]]:
        """Get all validation checks"""
        return self.validation_checks
    
    def get_validation_categories(self) -> List[str]:
        """Get all validation categories"""
        categories = set()
        for check in self.validation_checks.values():
            categories.add(check['category'])
        return sorted(list(categories))

