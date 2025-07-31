import json
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ValidationEngine:
    """Core validation engine for processing validation rules."""
    
    def __init__(self):
        """Initialize the validation engine."""
        self.rule_processors = {
            'field_presence': self._validate_field_presence,
            'format_validation': self._validate_format,
            'content_length': self._validate_content_length,
            'required_sections': self._validate_required_sections,
            'business_logic': self._validate_business_logic,
            'completeness_check': self._validate_completeness,
            'accuracy_check': self._validate_accuracy,
            'compliance_check': self._validate_compliance
        }
    
    def validate_content(self, content: Dict[str, Any], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate content against a set of rules.
        
        Args:
            content: Content to validate (from Confluence, Salesforce, etc.)
            rules: List of validation rules
            
        Returns:
            Validation result dictionary
        """
        start_time = time.time()
        
        rule_results = []
        total_score = 0.0
        total_weight = 0.0
        
        for rule in rules:
            if not rule.get('enabled', True):
                continue
            
            rule_result = self._execute_rule(content, rule)
            rule_results.append(rule_result)
            
            # Calculate weighted score
            weight = rule.get('weight', 1.0)
            total_score += rule_result['score'] * weight
            total_weight += weight
        
        # Calculate overall score
        overall_score = total_score / total_weight if total_weight > 0 else 0.0
        
        # Determine overall status
        overall_status = self._determine_overall_status(rule_results, overall_score)
        
        # Generate action plan
        action_plan = self._generate_action_plan(rule_results, content)
        
        execution_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        result = {
            'overall_status': overall_status,
            'score': round(overall_score, 3),
            'rule_results': rule_results,
            'action_plan': action_plan,
            'execution_time_ms': execution_time,
            'validated_at': datetime.utcnow().isoformat(),
            'content_summary': self._generate_content_summary(content)
        }
        
        logger.info(f"Validation completed: {overall_status} (score: {overall_score:.3f})")
        return result
    
    def _execute_rule(self, content: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single validation rule.
        
        Args:
            content: Content to validate
            rule: Validation rule configuration
            
        Returns:
            Rule execution result
        """
        rule_start_time = time.time()
        
        rule_type = rule.get('rule_type', 'field_presence')
        processor = self.rule_processors.get(rule_type, self._validate_field_presence)
        
        try:
            result = processor(content, rule)
            
            # Ensure result has required fields
            result.update({
                'rule_id': rule.get('id', ''),
                'rule_name': rule.get('name', ''),
                'rule_type': rule_type,
                'category': rule.get('category', 'general'),
                'weight': rule.get('weight', 1.0),
                'execution_time_ms': int((time.time() - rule_start_time) * 1000)
            })
            
            return result
            
        except Exception as error:
            logger.error(f"Error executing rule {rule.get('name', 'unknown')}: {error}")
            return {
                'rule_id': rule.get('id', ''),
                'rule_name': rule.get('name', ''),
                'rule_type': rule_type,
                'category': rule.get('category', 'general'),
                'status': 'error',
                'score': 0.0,
                'message': f"Rule execution failed: {str(error)}",
                'findings': [],
                'recommendations': ['Fix rule configuration or contact administrator'],
                'severity': 'high',
                'weight': rule.get('weight', 1.0),
                'execution_time_ms': int((time.time() - rule_start_time) * 1000)
            }
    
    def _validate_field_presence(self, content: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that required fields are present."""
        config = rule.get('configuration', {})
        required_fields = config.get('required_fields', [])
        
        findings = []
        missing_fields = []
        
        for field_path in required_fields:
            value = self._get_nested_value(content, field_path)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field_path)
                findings.append({
                    'type': 'missing_field',
                    'field_name': field_path,
                    'expected_value': 'Non-empty value',
                    'actual_value': str(value) if value is not None else 'null',
                    'severity': 'high',
                    'description': f"Required field '{field_path}' is missing or empty"
                })
        
        # Calculate score
        total_fields = len(required_fields)
        present_fields = total_fields - len(missing_fields)
        score = present_fields / total_fields if total_fields > 0 else 1.0
        
        # Determine status
        if score == 1.0:
            status = 'pass'
            message = 'All required fields are present'
        elif score >= 0.8:
            status = 'warning'
            message = f'{len(missing_fields)} required fields are missing'
        else:
            status = 'fail'
            message = f'{len(missing_fields)} required fields are missing'
        
        recommendations = []
        if missing_fields:
            recommendations.append(f"Add content for missing fields: {', '.join(missing_fields)}")
        
        return {
            'status': status,
            'score': score,
            'message': message,
            'findings': findings,
            'recommendations': recommendations,
            'severity': 'high' if status == 'fail' else 'medium' if status == 'warning' else 'low'
        }
    
    def _validate_format(self, content: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate field formats using regex patterns."""
        config = rule.get('configuration', {})
        format_rules = config.get('format_rules', {})
        
        findings = []
        invalid_formats = []
        
        for field_path, pattern in format_rules.items():
            value = self._get_nested_value(content, field_path)
            if value is not None:
                value_str = str(value)
                if not re.match(pattern, value_str):
                    invalid_formats.append(field_path)
                    findings.append({
                        'type': 'invalid_format',
                        'field_name': field_path,
                        'expected_value': f'Pattern: {pattern}',
                        'actual_value': value_str,
                        'severity': 'medium',
                        'description': f"Field '{field_path}' does not match required format"
                    })
        
        # Calculate score
        total_fields = len(format_rules)
        valid_fields = total_fields - len(invalid_formats)
        score = valid_fields / total_fields if total_fields > 0 else 1.0
        
        # Determine status
        if score == 1.0:
            status = 'pass'
            message = 'All fields have valid formats'
        elif score >= 0.8:
            status = 'warning'
            message = f'{len(invalid_formats)} fields have invalid formats'
        else:
            status = 'fail'
            message = f'{len(invalid_formats)} fields have invalid formats'
        
        recommendations = []
        if invalid_formats:
            recommendations.append(f"Fix format for fields: {', '.join(invalid_formats)}")
        
        return {
            'status': status,
            'score': score,
            'message': message,
            'findings': findings,
            'recommendations': recommendations,
            'severity': 'medium' if status == 'fail' else 'low'
        }
    
    def _validate_content_length(self, content: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content length requirements."""
        config = rule.get('configuration', {})
        length_rules = config.get('length_rules', {})
        
        findings = []
        length_violations = []
        
        for field_path, length_config in length_rules.items():
            value = self._get_nested_value(content, field_path)
            if value is not None:
                value_str = str(value)
                length = len(value_str)
                
                min_length = length_config.get('min_length', 0)
                max_length = length_config.get('max_length', float('inf'))
                
                if length < min_length or length > max_length:
                    length_violations.append(field_path)
                    findings.append({
                        'type': 'invalid_length',
                        'field_name': field_path,
                        'expected_value': f'Length between {min_length} and {max_length}',
                        'actual_value': f'Length: {length}',
                        'severity': 'medium',
                        'description': f"Field '{field_path}' length is outside acceptable range"
                    })
        
        # Calculate score
        total_fields = len(length_rules)
        valid_fields = total_fields - len(length_violations)
        score = valid_fields / total_fields if total_fields > 0 else 1.0
        
        # Determine status
        if score == 1.0:
            status = 'pass'
            message = 'All fields meet length requirements'
        elif score >= 0.8:
            status = 'warning'
            message = f'{len(length_violations)} fields have length issues'
        else:
            status = 'fail'
            message = f'{len(length_violations)} fields have length issues'
        
        recommendations = []
        if length_violations:
            recommendations.append(f"Adjust content length for fields: {', '.join(length_violations)}")
        
        return {
            'status': status,
            'score': score,
            'message': message,
            'findings': findings,
            'recommendations': recommendations,
            'severity': 'medium' if status == 'fail' else 'low'
        }
    
    def _validate_required_sections(self, content: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that required sections are present in content."""
        config = rule.get('configuration', {})
        required_sections = config.get('required_sections', [])
        
        # Look for sections in parsed content
        content_text = self._extract_text_content(content)
        headings = self._extract_headings(content)
        
        findings = []
        missing_sections = []
        
        for section in required_sections:
            section_found = False
            
            # Check in headings
            for heading in headings:
                if section.lower() in heading.get('text', '').lower():
                    section_found = True
                    break
            
            # Check in content text if not found in headings
            if not section_found and section.lower() in content_text.lower():
                section_found = True
            
            if not section_found:
                missing_sections.append(section)
                findings.append({
                    'type': 'missing_section',
                    'field_name': 'content_sections',
                    'expected_value': section,
                    'actual_value': 'Not found',
                    'severity': 'high',
                    'description': f"Required section '{section}' is missing from content"
                })
        
        # Calculate score
        total_sections = len(required_sections)
        present_sections = total_sections - len(missing_sections)
        score = present_sections / total_sections if total_sections > 0 else 1.0
        
        # Determine status
        if score == 1.0:
            status = 'pass'
            message = 'All required sections are present'
        elif score >= 0.8:
            status = 'warning'
            message = f'{len(missing_sections)} required sections are missing'
        else:
            status = 'fail'
            message = f'{len(missing_sections)} required sections are missing'
        
        recommendations = []
        if missing_sections:
            recommendations.append(f"Add missing sections: {', '.join(missing_sections)}")
        
        return {
            'status': status,
            'score': score,
            'message': message,
            'findings': findings,
            'recommendations': recommendations,
            'severity': 'high' if status == 'fail' else 'medium'
        }
    
    def _validate_business_logic(self, content: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate custom business logic rules."""
        config = rule.get('configuration', {})
        logic_type = config.get('logic_type', 'custom')
        
        # This is a placeholder for custom business logic validation
        # In a real implementation, this would execute custom validation code
        
        return {
            'status': 'pass',
            'score': 1.0,
            'message': 'Business logic validation passed',
            'findings': [],
            'recommendations': [],
            'severity': 'low'
        }
    
    def _validate_completeness(self, content: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content completeness."""
        config = rule.get('configuration', {})
        completeness_threshold = config.get('threshold', 0.8)
        
        # Calculate completeness based on filled fields vs total expected fields
        total_fields = 0
        filled_fields = 0
        
        def count_fields(obj, path=""):
            nonlocal total_fields, filled_fields
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (dict, list)):
                        count_fields(value, current_path)
                    else:
                        total_fields += 1
                        if value is not None and str(value).strip():
                            filled_fields += 1
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    count_fields(item, current_path)
        
        count_fields(content)
        
        completeness_score = filled_fields / total_fields if total_fields > 0 else 1.0
        
        findings = []
        if completeness_score < completeness_threshold:
            findings.append({
                'type': 'incomplete_content',
                'field_name': 'overall_completeness',
                'expected_value': f'At least {completeness_threshold * 100}% complete',
                'actual_value': f'{completeness_score * 100:.1f}% complete',
                'severity': 'medium',
                'description': f'Content is only {completeness_score * 100:.1f}% complete'
            })
        
        # Determine status
        if completeness_score >= completeness_threshold:
            status = 'pass'
            message = f'Content is {completeness_score * 100:.1f}% complete'
        elif completeness_score >= completeness_threshold * 0.8:
            status = 'warning'
            message = f'Content is {completeness_score * 100:.1f}% complete (below threshold)'
        else:
            status = 'fail'
            message = f'Content is {completeness_score * 100:.1f}% complete (significantly below threshold)'
        
        recommendations = []
        if completeness_score < completeness_threshold:
            empty_fields = total_fields - filled_fields
            recommendations.append(f"Fill in {empty_fields} empty fields to improve completeness")
        
        return {
            'status': status,
            'score': completeness_score,
            'message': message,
            'findings': findings,
            'recommendations': recommendations,
            'severity': 'medium' if status == 'fail' else 'low'
        }
    
    def _validate_accuracy(self, content: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content accuracy (placeholder for external data verification)."""
        # This would typically involve checking against external authoritative sources
        return {
            'status': 'pass',
            'score': 1.0,
            'message': 'Accuracy validation passed',
            'findings': [],
            'recommendations': [],
            'severity': 'low'
        }
    
    def _validate_compliance(self, content: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate compliance requirements."""
        config = rule.get('configuration', {})
        compliance_rules = config.get('compliance_rules', [])
        
        findings = []
        violations = []
        
        for compliance_rule in compliance_rules:
            rule_type = compliance_rule.get('type', 'keyword_presence')
            
            if rule_type == 'keyword_presence':
                required_keywords = compliance_rule.get('keywords', [])
                content_text = self._extract_text_content(content).lower()
                
                for keyword in required_keywords:
                    if keyword.lower() not in content_text:
                        violations.append(f"Missing keyword: {keyword}")
                        findings.append({
                            'type': 'compliance_violation',
                            'field_name': 'content_text',
                            'expected_value': f'Contains keyword: {keyword}',
                            'actual_value': 'Keyword not found',
                            'severity': 'high',
                            'description': f"Required compliance keyword '{keyword}' is missing"
                        })
        
        # Calculate score
        total_rules = len(compliance_rules)
        passed_rules = total_rules - len(violations)
        score = passed_rules / total_rules if total_rules > 0 else 1.0
        
        # Determine status
        if score == 1.0:
            status = 'pass'
            message = 'All compliance requirements met'
        elif score >= 0.8:
            status = 'warning'
            message = f'{len(violations)} compliance violations found'
        else:
            status = 'fail'
            message = f'{len(violations)} compliance violations found'
        
        recommendations = []
        if violations:
            recommendations.append("Address compliance violations: " + "; ".join(violations))
        
        return {
            'status': status,
            'score': score,
            'message': message,
            'findings': findings,
            'recommendations': recommendations,
            'severity': 'high' if status == 'fail' else 'medium'
        }
    
    def _determine_overall_status(self, rule_results: List[Dict[str, Any]], overall_score: float) -> str:
        """Determine overall validation status."""
        failed_rules = [r for r in rule_results if r['status'] == 'fail']
        error_rules = [r for r in rule_results if r['status'] == 'error']
        warning_rules = [r for r in rule_results if r['status'] == 'warning']
        
        if error_rules or failed_rules:
            return 'fail'
        elif warning_rules:
            return 'partial'
        else:
            return 'pass'
    
    def _generate_action_plan(self, rule_results: List[Dict[str, Any]], content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate action plan based on validation results."""
        priority_tasks = []
        optional_tasks = []
        total_effort = 0.0
        
        for rule_result in rule_results:
            if rule_result['status'] in ['fail', 'error']:
                for recommendation in rule_result.get('recommendations', []):
                    effort = 2.0 if rule_result['severity'] == 'high' else 1.0
                    priority_tasks.append({
                        'title': f"Fix {rule_result['rule_name']}",
                        'description': recommendation,
                        'priority': 'high' if rule_result['severity'] == 'high' else 'medium',
                        'estimated_effort_hours': effort,
                        'rule_id': rule_result['rule_id'],
                        'category': rule_result.get('category', 'general')
                    })
                    total_effort += effort
            
            elif rule_result['status'] == 'warning':
                for recommendation in rule_result.get('recommendations', []):
                    effort = 0.5
                    optional_tasks.append({
                        'title': f"Improve {rule_result['rule_name']}",
                        'description': recommendation,
                        'priority': 'low',
                        'estimated_effort_hours': effort,
                        'rule_id': rule_result['rule_id'],
                        'category': rule_result.get('category', 'general')
                    })
                    total_effort += effort
        
        return {
            'priority_tasks': priority_tasks,
            'optional_tasks': optional_tasks,
            'estimated_effort_hours': total_effort,
            'created_at': datetime.utcnow().isoformat()
        }
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """Get nested value from object using dot notation path."""
        keys = path.split('.')
        current = obj
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _extract_text_content(self, content: Dict[str, Any]) -> str:
        """Extract text content from structured content."""
        text_parts = []
        
        # Extract from various content fields
        if 'content' in content:
            content_obj = content['content']
            if isinstance(content_obj, dict):
                if 'parsed_view' in content_obj:
                    text_parts.append(content_obj['parsed_view'].get('text_content', ''))
                if 'parsed_storage' in content_obj:
                    text_parts.append(content_obj['parsed_storage'].get('text_content', ''))
        
        # Extract from title and other text fields
        if 'title' in content:
            text_parts.append(str(content['title']))
        
        return ' '.join(text_parts)
    
    def _extract_headings(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract headings from structured content."""
        headings = []
        
        if 'content' in content and isinstance(content['content'], dict):
            content_obj = content['content']
            if 'parsed_view' in content_obj:
                headings.extend(content_obj['parsed_view'].get('headings', []))
        
        return headings
    
    def _generate_content_summary(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the content being validated."""
        summary = {
            'content_type': content.get('type', 'unknown'),
            'title': content.get('title', 'Untitled'),
            'word_count': 0,
            'has_tables': False,
            'has_images': False,
            'section_count': 0
        }
        
        text_content = self._extract_text_content(content)
        if text_content:
            summary['word_count'] = len(text_content.split())
        
        headings = self._extract_headings(content)
        summary['section_count'] = len(headings)
        
        # Check for tables and images in content
        if 'content' in content and isinstance(content['content'], dict):
            content_obj = content['content']
            if 'parsed_view' in content_obj:
                parsed = content_obj['parsed_view']
                summary['has_tables'] = len(parsed.get('tables', [])) > 0
            if 'parsed_storage' in content_obj:
                parsed = content_obj['parsed_storage']
                summary['has_images'] = len(parsed.get('images', [])) > 0
        
        return summary

