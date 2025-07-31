"""
Conditional Validation Logic and Automation Support
Implements smart validation adaptation based on project characteristics and conditions
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from ..models.enhanced_validation import EnhancedValidationCriteria
from ..integrations.document_processor import ProcessedDocument

logger = logging.getLogger(__name__)

@dataclass
class ValidationCondition:
    """Represents a validation condition"""
    condition_type: str
    field_path: str
    operator: str
    value: Any
    description: str

@dataclass
class ConditionalRule:
    """Represents a conditional validation rule"""
    rule_id: str
    conditions: List[ValidationCondition]
    logic_operator: str  # 'and', 'or'
    actions: Dict[str, Any]
    description: str

class ConditionalValidator:
    """Handles conditional validation logic and automation support"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.condition_evaluators = {
            'equals': self._evaluate_equals,
            'not_equals': self._evaluate_not_equals,
            'greater_than': self._evaluate_greater_than,
            'less_than': self._evaluate_less_than,
            'contains': self._evaluate_contains,
            'regex_match': self._evaluate_regex_match,
            'in_list': self._evaluate_in_list,
            'range': self._evaluate_range
        }
    
    def evaluate_conditional_logic(
        self, 
        criterion: EnhancedValidationCriteria,
        documents: List[ProcessedDocument],
        project_context: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate conditional logic for a validation criterion
        
        Args:
            criterion: The validation criterion to evaluate
            documents: Available documents for the project
            project_context: Additional project context information
            
        Returns:
            Tuple of (should_execute, evaluation_details)
        """
        try:
            conditional_logic = json.loads(criterion.conditional_logic) if criterion.conditional_logic else {}
            
            if not conditional_logic:
                return True, {'reason': 'No conditional logic defined'}
            
            evaluation_results = []
            
            for condition_key, condition_data in conditional_logic.items():
                result = self._evaluate_condition_group(
                    condition_key, condition_data, documents, project_context
                )
                evaluation_results.append(result)
            
            # Determine overall result
            overall_result = self._combine_condition_results(evaluation_results)
            
            return overall_result['should_execute'], {
                'condition_results': evaluation_results,
                'overall_result': overall_result
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating conditional logic for {criterion.check_id}: {str(e)}")
            return True, {'error': str(e), 'default_action': 'execute'}
    
    def _evaluate_condition_group(
        self,
        condition_key: str,
        condition_data: Dict[str, Any],
        documents: List[ProcessedDocument],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a group of conditions"""
        condition_type = condition_data.get('condition')
        additional_checks = condition_data.get('additional_checks', [])
        
        if condition_type == 'cluster_size':
            return self._evaluate_cluster_size_condition(condition_data, documents, project_context)
        elif condition_type == 'project_type':
            return self._evaluate_project_type_condition(condition_data, documents, project_context)
        elif condition_type == 'document_availability':
            return self._evaluate_document_availability_condition(condition_data, documents)
        elif condition_type == 'approval_status':
            return self._evaluate_approval_status_condition(condition_data, documents, project_context)
        elif condition_type == 'network_complexity':
            return self._evaluate_network_complexity_condition(condition_data, documents, project_context)
        else:
            return self._evaluate_custom_condition(condition_key, condition_data, documents, project_context)
    
    def _evaluate_cluster_size_condition(
        self,
        condition_data: Dict[str, Any],
        documents: List[ProcessedDocument],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate cluster size-based conditions"""
        try:
            # Extract cluster size from documents
            cluster_size = self._extract_cluster_size(documents)
            
            if not cluster_size:
                return {
                    'condition_type': 'cluster_size',
                    'result': False,
                    'reason': 'Cluster size not found in documents',
                    'cluster_size': None
                }
            
            # Parse cluster size (e.g., "10x10" -> 100 nodes)
            total_nodes = self._parse_cluster_size(cluster_size)
            
            # Evaluate condition
            condition = condition_data.get('condition')
            threshold = self._extract_threshold_from_condition(condition)
            
            if 'cluster_nodes > 25' in condition:
                result = total_nodes > 25
                additional_checks = condition_data.get('additional_checks', []) if result else []
            elif 'cluster_nodes >= 50' in condition:
                result = total_nodes >= 50
                additional_checks = condition_data.get('additional_checks', []) if result else []
            elif 'cluster_nodes <= 10' in condition:
                result = total_nodes <= 10
                additional_checks = condition_data.get('additional_checks', []) if result else []
            else:
                result = True
                additional_checks = []
            
            return {
                'condition_type': 'cluster_size',
                'result': result,
                'cluster_size': cluster_size,
                'total_nodes': total_nodes,
                'additional_checks': additional_checks,
                'reason': f'Cluster has {total_nodes} nodes'
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating cluster size condition: {str(e)}")
            return {
                'condition_type': 'cluster_size',
                'result': False,
                'error': str(e)
            }
    
    def _evaluate_project_type_condition(
        self,
        condition_data: Dict[str, Any],
        documents: List[ProcessedDocument],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate project type-based conditions"""
        try:
            # Determine project type from documents and context
            project_type = self._determine_project_type(documents, project_context)
            
            expected_type = condition_data.get('expected_type')
            result = project_type == expected_type if expected_type else True
            
            return {
                'condition_type': 'project_type',
                'result': result,
                'project_type': project_type,
                'expected_type': expected_type,
                'reason': f'Project type is {project_type}'
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating project type condition: {str(e)}")
            return {
                'condition_type': 'project_type',
                'result': False,
                'error': str(e)
            }
    
    def _evaluate_document_availability_condition(
        self,
        condition_data: Dict[str, Any],
        documents: List[ProcessedDocument]
    ) -> Dict[str, Any]:
        """Evaluate document availability conditions"""
        required_docs = condition_data.get('required_documents', [])
        available_docs = [doc.document_type for doc in documents]
        
        missing_docs = [doc for doc in required_docs if doc not in available_docs]
        result = len(missing_docs) == 0
        
        return {
            'condition_type': 'document_availability',
            'result': result,
            'required_documents': required_docs,
            'available_documents': available_docs,
            'missing_documents': missing_docs,
            'reason': 'All required documents available' if result else f'Missing documents: {missing_docs}'
        }
    
    def _evaluate_approval_status_condition(
        self,
        condition_data: Dict[str, Any],
        documents: List[ProcessedDocument],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate approval status conditions"""
        try:
            # Extract approval status from documents
            approval_status = self._extract_approval_status(documents)
            
            required_approvals = condition_data.get('required_approvals', [])
            approved_roles = approval_status.get('approved_roles', [])
            
            missing_approvals = [role for role in required_approvals if role not in approved_roles]
            result = len(missing_approvals) == 0
            
            return {
                'condition_type': 'approval_status',
                'result': result,
                'required_approvals': required_approvals,
                'approved_roles': approved_roles,
                'missing_approvals': missing_approvals,
                'approval_details': approval_status,
                'reason': 'All approvals obtained' if result else f'Missing approvals: {missing_approvals}'
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating approval status condition: {str(e)}")
            return {
                'condition_type': 'approval_status',
                'result': False,
                'error': str(e)
            }
    
    def _evaluate_network_complexity_condition(
        self,
        condition_data: Dict[str, Any],
        documents: List[ProcessedDocument],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate network complexity conditions"""
        try:
            # Analyze network complexity from documents
            network_complexity = self._analyze_network_complexity(documents)
            
            complexity_threshold = condition_data.get('complexity_threshold', 'medium')
            complexity_levels = {'low': 1, 'medium': 2, 'high': 3}
            
            current_level = complexity_levels.get(network_complexity['level'], 2)
            threshold_level = complexity_levels.get(complexity_threshold, 2)
            
            result = current_level >= threshold_level
            
            return {
                'condition_type': 'network_complexity',
                'result': result,
                'complexity_level': network_complexity['level'],
                'complexity_score': network_complexity['score'],
                'complexity_factors': network_complexity['factors'],
                'threshold': complexity_threshold,
                'reason': f'Network complexity is {network_complexity["level"]} (threshold: {complexity_threshold})'
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating network complexity condition: {str(e)}")
            return {
                'condition_type': 'network_complexity',
                'result': False,
                'error': str(e)
            }
    
    def _evaluate_custom_condition(
        self,
        condition_key: str,
        condition_data: Dict[str, Any],
        documents: List[ProcessedDocument],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate custom conditions"""
        try:
            # Parse custom condition
            condition_expr = condition_data.get('condition', '')
            
            # Extract field values from documents and context
            field_values = self._extract_field_values(documents, project_context)
            
            # Evaluate condition expression
            result = self._evaluate_condition_expression(condition_expr, field_values)
            
            return {
                'condition_type': 'custom',
                'condition_key': condition_key,
                'condition_expression': condition_expr,
                'result': result,
                'field_values': field_values,
                'reason': f'Custom condition evaluated to {result}'
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating custom condition {condition_key}: {str(e)}")
            return {
                'condition_type': 'custom',
                'condition_key': condition_key,
                'result': False,
                'error': str(e)
            }
    
    def _combine_condition_results(self, evaluation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple condition results"""
        if not evaluation_results:
            return {'should_execute': True, 'reason': 'No conditions to evaluate'}
        
        # Default logic: AND all conditions (all must be true)
        all_results = [result.get('result', False) for result in evaluation_results]
        should_execute = all(all_results)
        
        passed_conditions = sum(1 for result in all_results if result)
        total_conditions = len(all_results)
        
        return {
            'should_execute': should_execute,
            'passed_conditions': passed_conditions,
            'total_conditions': total_conditions,
            'success_rate': passed_conditions / total_conditions if total_conditions > 0 else 0,
            'reason': f'{passed_conditions}/{total_conditions} conditions passed'
        }
    
    # Helper methods for condition evaluation
    def _extract_cluster_size(self, documents: List[ProcessedDocument]) -> Optional[str]:
        """Extract cluster size from documents"""
        for doc in documents:
            if doc.document_type == 'site_survey_part1':
                # Look in VAST Cluster worksheet
                cluster_content = doc.content.get('VAST Cluster', {})
                cluster_info = cluster_content.get('cluster_info', {})
                
                # Look for cluster size patterns
                for key, value in cluster_info.items():
                    if isinstance(value, str) and re.search(r'\d+x\d+', value):
                        match = re.search(r'(\d+x\d+)', value)
                        if match:
                            return match.group(1)
            
            elif doc.document_type == 'install_plan_pdf':
                # Look in metadata
                cluster_size = doc.metadata.get('cluster_size')
                if cluster_size:
                    return cluster_size
        
        return None
    
    def _parse_cluster_size(self, cluster_size: str) -> int:
        """Parse cluster size string to total nodes"""
        if 'x' in cluster_size:
            parts = cluster_size.split('x')
            if len(parts) == 2:
                try:
                    return int(parts[0]) * int(parts[1])
                except ValueError:
                    pass
        
        # Try to extract number directly
        match = re.search(r'(\d+)', cluster_size)
        if match:
            return int(match.group(1))
        
        return 0
    
    def _extract_threshold_from_condition(self, condition: str) -> Optional[int]:
        """Extract numerical threshold from condition string"""
        match = re.search(r'(\d+)', condition)
        return int(match.group(1)) if match else None
    
    def _determine_project_type(
        self, 
        documents: List[ProcessedDocument], 
        project_context: Dict[str, Any]
    ) -> str:
        """Determine project type from documents and context"""
        # Check cluster size to determine project type
        cluster_size = self._extract_cluster_size(documents)
        if cluster_size:
            total_nodes = self._parse_cluster_size(cluster_size)
            if total_nodes <= 100:
                return 'small'
            elif total_nodes <= 500:
                return 'medium'
            else:
                return 'large'
        
        # Check project context
        project_type = project_context.get('project_type')
        if project_type:
            return project_type
        
        return 'standard'
    
    def _extract_approval_status(self, documents: List[ProcessedDocument]) -> Dict[str, Any]:
        """Extract approval status from documents"""
        approval_status = {
            'approved_roles': [],
            'pending_roles': [],
            'approval_details': []
        }
        
        for doc in documents:
            if doc.document_type in ['site_survey_part1', 'site_survey_part2']:
                release_notes = doc.content.get('Release Notes', {})
                release_info = release_notes.get('release_info', {})
                approvals = release_info.get('approvals', [])
                
                for approval in approvals:
                    # Parse approval information
                    for key, value in approval.items():
                        if value and isinstance(value, str):
                            if 'approved' in value.lower():
                                # Extract role from the approval entry
                                role = self._extract_role_from_approval(approval)
                                if role and role not in approval_status['approved_roles']:
                                    approval_status['approved_roles'].append(role)
                            elif 'pending' in value.lower() or 'no response' in value.lower():
                                role = self._extract_role_from_approval(approval)
                                if role and role not in approval_status['pending_roles']:
                                    approval_status['pending_roles'].append(role)
                    
                    approval_status['approval_details'].append(approval)
        
        return approval_status
    
    def _extract_role_from_approval(self, approval: Dict[str, Any]) -> Optional[str]:
        """Extract role from approval entry"""
        # Look for common role patterns
        role_patterns = {
            'SE': r'\bSE\b|Sales Engineer',
            'PM': r'\bPM\b|Project Manager',
            'Technical Lead': r'Technical Lead|Tech Lead',
            'Manager': r'Manager',
            'Director': r'Director'
        }
        
        approval_text = ' '.join(str(v) for v in approval.values())
        
        for role, pattern in role_patterns.items():
            if re.search(pattern, approval_text, re.IGNORECASE):
                return role
        
        return None
    
    def _analyze_network_complexity(self, documents: List[ProcessedDocument]) -> Dict[str, Any]:
        """Analyze network complexity from documents"""
        complexity_factors = {
            'vlan_count': 0,
            'ip_ranges': 0,
            'network_segments': 0,
            'special_configurations': 0
        }
        
        for doc in documents:
            if doc.document_type == 'site_survey_part2':
                # Analyze IP addresses worksheet
                ip_content = doc.content.get('#2 IP Addresses', {})
                ip_info = ip_content.get('ip_addresses', {})
                
                # Count VLANs
                vlans = ip_info.get('vlans', [])
                complexity_factors['vlan_count'] = len(vlans)
                
                # Count IP ranges
                ip_ranges = ip_info.get('ip_ranges', [])
                complexity_factors['ip_ranges'] = len(ip_ranges)
                
            elif doc.document_type == 'install_plan_pdf':
                # Analyze network section
                sections = doc.content.get('sections', {})
                network_section = sections.get('Network', '')
                
                if network_section:
                    # Count network segments
                    segment_matches = re.findall(r'segment|subnet|network', network_section, re.IGNORECASE)
                    complexity_factors['network_segments'] = len(segment_matches)
                    
                    # Look for special configurations
                    special_configs = re.findall(
                        r'bond|trunk|lag|mtu|jumbo|routing|firewall', 
                        network_section, 
                        re.IGNORECASE
                    )
                    complexity_factors['special_configurations'] = len(special_configs)
        
        # Calculate complexity score
        score = (
            complexity_factors['vlan_count'] * 2 +
            complexity_factors['ip_ranges'] * 1 +
            complexity_factors['network_segments'] * 1 +
            complexity_factors['special_configurations'] * 3
        )
        
        # Determine complexity level
        if score <= 5:
            level = 'low'
        elif score <= 15:
            level = 'medium'
        else:
            level = 'high'
        
        return {
            'level': level,
            'score': score,
            'factors': complexity_factors
        }
    
    def _extract_field_values(
        self, 
        documents: List[ProcessedDocument], 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract field values for condition evaluation"""
        field_values = {}
        
        # Add project context
        field_values.update(project_context)
        
        # Extract values from documents
        for doc in documents:
            doc_prefix = doc.document_type
            
            # Add document metadata
            for key, value in doc.metadata.items():
                field_values[f"{doc_prefix}.{key}"] = value
            
            # Add specific content fields
            if doc.document_type == 'site_survey_part1':
                project_details = doc.content.get('Project Details', {}).get('key_values', {})
                for key, value in project_details.items():
                    field_values[f"project.{key}"] = value
            
            elif doc.document_type == 'site_survey_part2':
                ip_info = doc.content.get('#2 IP Addresses', {}).get('ip_addresses', {})
                field_values['network.vlan_count'] = len(ip_info.get('vlans', []))
                field_values['network.ip_range_count'] = len(ip_info.get('ip_ranges', []))
        
        return field_values
    
    def _evaluate_condition_expression(self, expression: str, field_values: Dict[str, Any]) -> bool:
        """Evaluate a condition expression safely"""
        try:
            # Simple expression evaluation for common patterns
            if '>' in expression:
                parts = expression.split('>')
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    
                    left_value = field_values.get(left, 0)
                    right_value = int(right) if right.isdigit() else field_values.get(right, 0)
                    
                    return float(left_value) > float(right_value)
            
            elif '<' in expression:
                parts = expression.split('<')
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    
                    left_value = field_values.get(left, 0)
                    right_value = int(right) if right.isdigit() else field_values.get(right, 0)
                    
                    return float(left_value) < float(right_value)
            
            elif '==' in expression:
                parts = expression.split('==')
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip('"\'')
                    
                    left_value = str(field_values.get(left, ''))
                    
                    return left_value == right
            
            # Default to True for unrecognized expressions
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition expression '{expression}': {str(e)}")
            return True
    
    # Condition evaluator methods
    def _evaluate_equals(self, field_value: Any, condition_value: Any) -> bool:
        """Evaluate equals condition"""
        return field_value == condition_value
    
    def _evaluate_not_equals(self, field_value: Any, condition_value: Any) -> bool:
        """Evaluate not equals condition"""
        return field_value != condition_value
    
    def _evaluate_greater_than(self, field_value: Any, condition_value: Any) -> bool:
        """Evaluate greater than condition"""
        try:
            return float(field_value) > float(condition_value)
        except (ValueError, TypeError):
            return False
    
    def _evaluate_less_than(self, field_value: Any, condition_value: Any) -> bool:
        """Evaluate less than condition"""
        try:
            return float(field_value) < float(condition_value)
        except (ValueError, TypeError):
            return False
    
    def _evaluate_contains(self, field_value: Any, condition_value: Any) -> bool:
        """Evaluate contains condition"""
        return str(condition_value).lower() in str(field_value).lower()
    
    def _evaluate_regex_match(self, field_value: Any, condition_value: Any) -> bool:
        """Evaluate regex match condition"""
        try:
            return bool(re.search(str(condition_value), str(field_value)))
        except re.error:
            return False
    
    def _evaluate_in_list(self, field_value: Any, condition_value: List[Any]) -> bool:
        """Evaluate in list condition"""
        return field_value in condition_value
    
    def _evaluate_range(self, field_value: Any, condition_value: Dict[str, Any]) -> bool:
        """Evaluate range condition"""
        try:
            value = float(field_value)
            min_val = float(condition_value.get('min', float('-inf')))
            max_val = float(condition_value.get('max', float('inf')))
            return min_val <= value <= max_val
        except (ValueError, TypeError):
            return False

class AutomationOrchestrator:
    """Orchestrates automated validation workflows"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conditional_validator = ConditionalValidator()
    
    def create_validation_workflow(
        self, 
        project_id: str,
        documents: List[ProcessedDocument],
        validation_criteria: List[EnhancedValidationCriteria],
        project_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create an automated validation workflow"""
        if project_context is None:
            project_context = {}
        
        workflow = {
            'project_id': project_id,
            'created_at': datetime.utcnow().isoformat(),
            'total_criteria': len(validation_criteria),
            'workflow_steps': [],
            'conditional_results': {},
            'execution_plan': []
        }
        
        # Evaluate conditional logic for each criterion
        for criterion in validation_criteria:
            should_execute, evaluation_details = self.conditional_validator.evaluate_conditional_logic(
                criterion, documents, project_context
            )
            
            workflow['conditional_results'][criterion.check_id] = {
                'should_execute': should_execute,
                'evaluation_details': evaluation_details
            }
            
            if should_execute:
                workflow['execution_plan'].append({
                    'check_id': criterion.check_id,
                    'name': criterion.name,
                    'category': criterion.category,
                    'validation_level': criterion.validation_level,
                    'automation_complexity': criterion.automation_complexity,
                    'estimated_duration': self._estimate_execution_duration(criterion)
                })
        
        # Sort execution plan by validation level and complexity
        workflow['execution_plan'].sort(
            key=lambda x: (x['validation_level'], x['automation_complexity'])
        )
        
        workflow['executable_criteria'] = len(workflow['execution_plan'])
        workflow['conditional_exclusions'] = workflow['total_criteria'] - workflow['executable_criteria']
        
        return workflow
    
    def _estimate_execution_duration(self, criterion: EnhancedValidationCriteria) -> int:
        """Estimate execution duration in milliseconds"""
        complexity_durations = {
            'low': 100,
            'medium': 500,
            'high': 2000
        }
        
        base_duration = complexity_durations.get(criterion.automation_complexity, 500)
        
        # Adjust based on validation level
        level_multiplier = {1: 1.0, 2: 1.5, 3: 2.0, 4: 3.0}
        multiplier = level_multiplier.get(criterion.validation_level, 1.0)
        
        return int(base_duration * multiplier)

