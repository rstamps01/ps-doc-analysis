"""
Sample Data Generator for Export API Testing
Provides realistic validation data when no database records exist
"""

import uuid
from datetime import datetime
from typing import Dict, Any

def generate_sample_validation_data(validation_id: str = None) -> Dict[str, Any]:
    """Generate comprehensive sample validation data for testing"""
    
    if validation_id is None:
        validation_id = str(uuid.uuid4())
    
    return {
        'validation_id': validation_id,
        'timestamp': datetime.now().isoformat(),
        'overall_score': 82.5,
        'threshold': 75.0,
        'status': 'PASS',
        'documents': {
            'evaluation_criteria': 'https://docs.google.com/spreadsheets/d/1aQVhSNNmDJ0FXhejoXi84GHxD8iIyuIYuhld9lxTZPY/edit',
            'site_survey_1': 'https://docs.google.com/spreadsheets/d/1aQVhSNNmDJ0FXhejoXi84GHxD8iIyuIYuhld9lxTZPY/edit',
            'site_survey_2': 'https://docs.google.com/spreadsheets/d/1p2X4Pvleis2s0pgQ1FRpf-o2e4LsgfOA0LxlmLVxH_k/edit',
            'install_plan': 'https://drive.google.com/file/d/1ez3eMHrKXKJJBXMgJLnj3RQcENZQZgkm/view'
        },
        'category_results': {
            'Document Metadata': {
                'score': 85.0,
                'status': 'PASS',
                'checks_passed': 17,
                'total_checks': 20,
                'issues': [
                    'Missing project timeline in metadata',
                    'SE contact information incomplete',
                    'Version control information not specified'
                ]
            },
            'Technical Requirements': {
                'score': 78.0,
                'status': 'WARNING',
                'checks_passed': 14,
                'total_checks': 18,
                'issues': [
                    'Network bandwidth requirements not fully specified',
                    'Storage capacity calculations need verification',
                    'Backup strategy details incomplete',
                    'Security requirements partially documented'
                ]
            },
            'Document Completeness': {
                'score': 92.0,
                'status': 'PASS',
                'checks_passed': 11,
                'total_checks': 12,
                'issues': [
                    'Risk assessment section could be more detailed'
                ]
            },
            'SFDC Integration': {
                'score': 95.0,
                'status': 'PASS',
                'checks_passed': 19,
                'total_checks': 20,
                'issues': [
                    'Minor formatting inconsistency in case references'
                ]
            }
        },
        'detailed_issues': [
            {
                'id': 1,
                'category': 'Document Metadata',
                'severity': 'Medium',
                'description': 'Project timeline not specified in document header',
                'location': 'Site Survey Part 1, Header Section',
                'recommendation': 'Add project start and end dates to document metadata'
            },
            {
                'id': 2,
                'category': 'Technical Requirements',
                'severity': 'High',
                'description': 'Network bandwidth requirements incomplete',
                'location': 'Install Plan, Network Section',
                'recommendation': 'Specify minimum and recommended bandwidth for all network segments'
            },
            {
                'id': 3,
                'category': 'Technical Requirements',
                'severity': 'Medium',
                'description': 'Storage capacity calculations need verification',
                'location': 'Site Survey Part 2, Storage Section',
                'recommendation': 'Provide detailed storage calculations with growth projections'
            },
            {
                'id': 4,
                'category': 'Document Completeness',
                'severity': 'Low',
                'description': 'Risk assessment could be more comprehensive',
                'location': 'Install Plan, Risk Section',
                'recommendation': 'Expand risk assessment to include technical and operational risks'
            },
            {
                'id': 5,
                'category': 'SFDC Integration',
                'severity': 'Low',
                'description': 'Case reference formatting inconsistency',
                'location': 'Multiple documents',
                'recommendation': 'Standardize case reference format across all documents'
            }
        ],
        'recommendations': [
            {
                'priority': 'High',
                'category': 'Technical Requirements',
                'action': 'Complete network bandwidth specifications',
                'description': 'Ensure all network segments have clearly defined bandwidth requirements with minimum and recommended values.',
                'estimated_effort': '2-4 hours'
            },
            {
                'priority': 'Medium',
                'category': 'Document Metadata',
                'action': 'Add project timeline information',
                'description': 'Include project start date, key milestones, and expected completion date in document headers.',
                'estimated_effort': '1-2 hours'
            },
            {
                'priority': 'Medium',
                'category': 'Technical Requirements',
                'action': 'Verify storage calculations',
                'description': 'Review and validate all storage capacity calculations, including growth projections and backup requirements.',
                'estimated_effort': '3-5 hours'
            },
            {
                'priority': 'Low',
                'category': 'Document Completeness',
                'action': 'Enhance risk assessment',
                'description': 'Expand risk assessment section to cover technical, operational, and business risks with mitigation strategies.',
                'estimated_effort': '2-3 hours'
            },
            {
                'priority': 'Low',
                'category': 'SFDC Integration',
                'action': 'Standardize formatting',
                'description': 'Apply consistent formatting for case references and SFDC integration points across all documents.',
                'estimated_effort': '1 hour'
            }
        ],
        'summary': {
            'total_checks': 70,
            'checks_passed': 61,
            'checks_failed': 9,
            'pass_rate': 87.1,
            'critical_issues': 0,
            'high_issues': 1,
            'medium_issues': 3,
            'low_issues': 2,
            'processing_time': '2.3 seconds',
            'documents_processed': 4
        }
    }

