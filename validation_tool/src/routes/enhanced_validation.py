"""
Enhanced Validation API Endpoints
Provides comprehensive API access to enhanced validation capabilities
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest, NotFound

from ..models.enhanced_validation import (
    EnhancedValidationCriteria, DocumentSourceMapping, CrossDocumentValidation,
    ValidationExecution, ProjectValidationSummary, ValidationAccuracyMetrics
)
from ..models.user import db
from ..validation.enhanced_engine import EnhancedValidationEngine, DocumentContent
from ..automation.conditional_validator import ConditionalValidator, AutomationOrchestrator
from ..integrations.document_processor import DocumentProcessor, ProcessedDocument

logger = logging.getLogger(__name__)

enhanced_validation_bp = Blueprint('enhanced_validation', __name__, url_prefix='/api/v2/validation')

# Initialize components
validation_engine = EnhancedValidationEngine()
conditional_validator = ConditionalValidator()
automation_orchestrator = AutomationOrchestrator()
document_processor = DocumentProcessor()

@enhanced_validation_bp.route('/criteria', methods=['GET'])
def get_enhanced_criteria():
    """Get all enhanced validation criteria with filtering options"""
    try:
        # Parse query parameters
        category = request.args.get('category')
        complexity = request.args.get('complexity')
        validation_level = request.args.get('validation_level', type=int)
        enabled_only = request.args.get('enabled_only', 'true').lower() == 'true'
        
        # Build query
        query = EnhancedValidationCriteria.query
        
        if category:
            query = query.filter(EnhancedValidationCriteria.category == category)
        
        if complexity:
            query = query.filter(EnhancedValidationCriteria.automation_complexity == complexity)
        
        if validation_level:
            query = query.filter(EnhancedValidationCriteria.validation_level == validation_level)
        
        if enabled_only:
            query = query.filter(EnhancedValidationCriteria.enabled == True)
        
        criteria = query.all()
        
        # Group by category for better organization
        criteria_by_category = {}
        for criterion in criteria:
            category_name = criterion.category
            if category_name not in criteria_by_category:
                criteria_by_category[category_name] = []
            criteria_by_category[category_name].append(criterion.to_dict())
        
        return jsonify({
            'success': True,
            'total_criteria': len(criteria),
            'criteria_by_category': criteria_by_category,
            'categories': list(criteria_by_category.keys())
        })
        
    except Exception as e:
        logger.error(f"Error retrieving enhanced criteria: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_validation_bp.route('/criteria/<check_id>', methods=['GET'])
def get_criterion_details(check_id):
    """Get detailed information about a specific validation criterion"""
    try:
        criterion = EnhancedValidationCriteria.query.filter_by(check_id=check_id).first()
        
        if not criterion:
            return jsonify({
                'success': False,
                'error': f'Criterion {check_id} not found'
            }), 404
        
        # Get document source mappings
        mappings = DocumentSourceMapping.query.filter_by(criteria_id=criterion.id).all()
        
        # Get recent executions
        recent_executions = ValidationExecution.query.filter_by(
            criteria_id=criterion.id
        ).order_by(ValidationExecution.executed_at.desc()).limit(10).all()
        
        # Get accuracy metrics
        accuracy_metrics = ValidationAccuracyMetrics.query.filter_by(
            criteria_id=criterion.id
        ).first()
        
        return jsonify({
            'success': True,
            'criterion': criterion.to_dict(),
            'document_mappings': [mapping.to_dict() for mapping in mappings],
            'recent_executions': [execution.to_dict() for execution in recent_executions],
            'accuracy_metrics': accuracy_metrics.to_dict() if accuracy_metrics else None
        })
        
    except Exception as e:
        logger.error(f"Error retrieving criterion details for {check_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_validation_bp.route('/projects/<project_id>/validate', methods=['POST'])
def validate_project_enhanced(project_id):
    """Execute enhanced validation for a project with multiple documents"""
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("Request body is required")
        
        # Parse request data
        documents_data = data.get('documents', [])
        project_context = data.get('project_context', {})
        validation_options = data.get('validation_options', {})
        
        if not documents_data:
            raise BadRequest("At least one document is required")
        
        # Process documents
        processed_documents = []
        for doc_data in documents_data:
            doc_type = doc_data.get('document_type')
            source_url = doc_data.get('source_url', '')
            content = doc_data.get('content', {})
            metadata = doc_data.get('metadata', {})
            
            if not doc_type:
                raise BadRequest("document_type is required for each document")
            
            # Create DocumentContent object
            document_content = DocumentContent(
                document_type=doc_type,
                content=content,
                metadata=metadata
            )
            processed_documents.append(document_content)
        
        # Execute enhanced validation
        validation_results = validation_engine.validate_project(
            project_id, processed_documents
        )
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'validation_results': validation_results
        })
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error validating project {project_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_validation_bp.route('/projects/<project_id>/workflow', methods=['POST'])
def create_validation_workflow(project_id):
    """Create an automated validation workflow for a project"""
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("Request body is required")
        
        # Parse request data
        documents_data = data.get('documents', [])
        project_context = data.get('project_context', {})
        
        # Process documents
        processed_documents = []
        for doc_data in documents_data:
            processed_doc = ProcessedDocument(
                document_type=doc_data.get('document_type'),
                source_url=doc_data.get('source_url', ''),
                content=doc_data.get('content', {}),
                metadata=doc_data.get('metadata', {}),
                processing_errors=doc_data.get('processing_errors', [])
            )
            processed_documents.append(processed_doc)
        
        # Get validation criteria
        criteria = EnhancedValidationCriteria.query.filter_by(enabled=True).all()
        
        # Create workflow
        workflow = automation_orchestrator.create_validation_workflow(
            project_id, processed_documents, criteria, project_context
        )
        
        return jsonify({
            'success': True,
            'workflow': workflow
        })
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating validation workflow for {project_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_validation_bp.route('/projects/<project_id>/summary', methods=['GET'])
def get_project_validation_summary(project_id):
    """Get validation summary for a project"""
    try:
        summary = ProjectValidationSummary.query.filter_by(project_id=project_id).first()
        
        if not summary:
            return jsonify({
                'success': False,
                'error': f'No validation summary found for project {project_id}'
            }), 404
        
        # Get recent validation executions
        recent_executions = ValidationExecution.query.filter_by(
            project_id=project_id
        ).order_by(ValidationExecution.executed_at.desc()).limit(20).all()
        
        # Get cross-document validations
        cross_validations = CrossDocumentValidation.query.filter_by(
            project_id=project_id
        ).order_by(CrossDocumentValidation.executed_at.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'summary': summary.to_dict(),
            'recent_executions': [execution.to_dict() for execution in recent_executions],
            'cross_document_validations': [cv.to_dict() for cv in cross_validations]
        })
        
    except Exception as e:
        logger.error(f"Error retrieving project summary for {project_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_validation_bp.route('/projects/<project_id>/executions', methods=['GET'])
def get_project_validation_executions(project_id):
    """Get validation executions for a project with filtering"""
    try:
        # Parse query parameters
        status = request.args.get('status')
        category = request.args.get('category')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = ValidationExecution.query.filter_by(project_id=project_id)
        
        if status:
            query = query.filter(ValidationExecution.status == status)
        
        if category:
            # Join with criteria to filter by category
            query = query.join(EnhancedValidationCriteria).filter(
                EnhancedValidationCriteria.category == category
            )
        
        # Apply pagination
        executions = query.order_by(
            ValidationExecution.executed_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Get total count
        total_count = query.count()
        
        return jsonify({
            'success': True,
            'executions': [execution.to_dict() for execution in executions],
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Error retrieving executions for project {project_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_validation_bp.route('/cross-document/validate', methods=['POST'])
def validate_cross_document():
    """Execute cross-document validation"""
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("Request body is required")
        
        project_id = data.get('project_id')
        documents_data = data.get('documents', [])
        validation_types = data.get('validation_types', ['consistency', 'synchronization'])
        
        if not project_id:
            raise BadRequest("project_id is required")
        
        if not documents_data:
            raise BadRequest("documents are required")
        
        # Process documents
        processed_documents = []
        for doc_data in documents_data:
            processed_doc = ProcessedDocument(
                document_type=doc_data.get('document_type'),
                source_url=doc_data.get('source_url', ''),
                content=doc_data.get('content', {}),
                metadata=doc_data.get('metadata', {}),
                processing_errors=doc_data.get('processing_errors', [])
            )
            processed_documents.append(processed_doc)
        
        # Execute cross-document validation
        cross_validation_results = validation_engine._perform_cross_document_validation(
            project_id, processed_documents
        )
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'cross_validation_results': cross_validation_results
        })
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error executing cross-document validation: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_validation_bp.route('/conditional/evaluate', methods=['POST'])
def evaluate_conditional_logic():
    """Evaluate conditional logic for validation criteria"""
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("Request body is required")
        
        check_id = data.get('check_id')
        documents_data = data.get('documents', [])
        project_context = data.get('project_context', {})
        
        if not check_id:
            raise BadRequest("check_id is required")
        
        # Get criterion
        criterion = EnhancedValidationCriteria.query.filter_by(check_id=check_id).first()
        if not criterion:
            raise NotFound(f"Criterion {check_id} not found")
        
        # Process documents
        processed_documents = []
        for doc_data in documents_data:
            processed_doc = ProcessedDocument(
                document_type=doc_data.get('document_type'),
                source_url=doc_data.get('source_url', ''),
                content=doc_data.get('content', {}),
                metadata=doc_data.get('metadata', {}),
                processing_errors=doc_data.get('processing_errors', [])
            )
            processed_documents.append(processed_doc)
        
        # Evaluate conditional logic
        should_execute, evaluation_details = conditional_validator.evaluate_conditional_logic(
            criterion, processed_documents, project_context
        )
        
        return jsonify({
            'success': True,
            'check_id': check_id,
            'should_execute': should_execute,
            'evaluation_details': evaluation_details
        })
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except NotFound as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error evaluating conditional logic: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_validation_bp.route('/accuracy/metrics', methods=['GET'])
def get_accuracy_metrics():
    """Get validation accuracy metrics"""
    try:
        # Parse query parameters
        check_id = request.args.get('check_id')
        category = request.args.get('category')
        
        # Build query
        query = ValidationAccuracyMetrics.query
        
        if check_id:
            criterion = EnhancedValidationCriteria.query.filter_by(check_id=check_id).first()
            if criterion:
                query = query.filter(ValidationAccuracyMetrics.criteria_id == criterion.id)
            else:
                return jsonify({
                    'success': False,
                    'error': f'Criterion {check_id} not found'
                }), 404
        
        if category:
            # Join with criteria to filter by category
            query = query.join(EnhancedValidationCriteria).filter(
                EnhancedValidationCriteria.category == category
            )
        
        metrics = query.all()
        
        # Calculate summary statistics
        if metrics:
            total_executions = sum(m.total_executions for m in metrics)
            total_correct = sum(m.correct_predictions for m in metrics)
            overall_accuracy = total_correct / total_executions if total_executions > 0 else 0.0
            
            avg_execution_time = sum(m.avg_execution_time_ms for m in metrics if m.avg_execution_time_ms) / len(metrics)
            avg_confidence = sum(m.avg_confidence_score for m in metrics if m.avg_confidence_score) / len(metrics)
        else:
            overall_accuracy = 0.0
            avg_execution_time = 0.0
            avg_confidence = 0.0
        
        return jsonify({
            'success': True,
            'metrics': [metric.to_dict() for metric in metrics],
            'summary': {
                'total_criteria': len(metrics),
                'overall_accuracy': overall_accuracy,
                'avg_execution_time_ms': avg_execution_time,
                'avg_confidence_score': avg_confidence
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving accuracy metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_validation_bp.route('/documents/process', methods=['POST'])
def process_document():
    """Process a document for validation"""
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("Request body is required")
        
        document_type = data.get('document_type')
        source_url = data.get('source_url')
        content_data = data.get('content_data')  # Base64 encoded or raw content
        
        if not document_type:
            raise BadRequest("document_type is required")
        
        if not source_url:
            raise BadRequest("source_url is required")
        
        if not content_data:
            raise BadRequest("content_data is required")
        
        # Convert content data to bytes if needed
        if isinstance(content_data, str):
            import base64
            try:
                content_bytes = base64.b64decode(content_data)
            except Exception:
                content_bytes = content_data.encode('utf-8')
        else:
            content_bytes = content_data
        
        # Process document
        processed_doc = document_processor.process_document(
            document_type, source_url, content_bytes
        )
        
        return jsonify({
            'success': True,
            'processed_document': {
                'document_type': processed_doc.document_type,
                'source_url': processed_doc.source_url,
                'content': processed_doc.content,
                'metadata': processed_doc.metadata,
                'processing_errors': processed_doc.processing_errors
            }
        })
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_validation_bp.route('/analytics/dashboard', methods=['GET'])
def get_validation_analytics():
    """Get validation analytics for dashboard"""
    try:
        # Get summary statistics
        total_criteria = EnhancedValidationCriteria.query.filter_by(enabled=True).count()
        total_projects = db.session.query(ProjectValidationSummary.project_id).distinct().count()
        
        # Get recent validation activity
        recent_executions = ValidationExecution.query.order_by(
            ValidationExecution.executed_at.desc()
        ).limit(100).all()
        
        # Calculate success rates by category
        category_stats = {}
        for execution in recent_executions:
            if execution.criteria and execution.criteria.category:
                category = execution.criteria.category
                if category not in category_stats:
                    category_stats[category] = {'total': 0, 'passed': 0}
                
                category_stats[category]['total'] += 1
                if execution.status == 'pass':
                    category_stats[category]['passed'] += 1
        
        # Calculate success rates
        for category in category_stats:
            stats = category_stats[category]
            stats['success_rate'] = stats['passed'] / stats['total'] if stats['total'] > 0 else 0.0
        
        # Get project status distribution
        project_summaries = ProjectValidationSummary.query.all()
        status_distribution = {}
        for summary in project_summaries:
            status = summary.overall_status
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Get recent cross-document validations
        recent_cross_validations = CrossDocumentValidation.query.order_by(
            CrossDocumentValidation.executed_at.desc()
        ).limit(20).all()
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_criteria': total_criteria,
                'total_projects': total_projects,
                'category_stats': category_stats,
                'status_distribution': status_distribution,
                'recent_activity': {
                    'executions': [execution.to_dict() for execution in recent_executions[:10]],
                    'cross_validations': [cv.to_dict() for cv in recent_cross_validations[:5]]
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving validation analytics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@enhanced_validation_bp.errorhandler(400)
def handle_bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'message': str(error)
    }), 400

@enhanced_validation_bp.errorhandler(404)
def handle_not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': str(error)
    }), 404

@enhanced_validation_bp.errorhandler(500)
def handle_internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error)
    }), 500

