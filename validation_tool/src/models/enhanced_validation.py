from .user import db
from datetime import datetime
import json
import uuid

class EnhancedValidationCriteria(db.Model):
    """Enhanced validation criteria with automation support and cross-document capabilities"""
    __tablename__ = 'enhanced_validation_criteria'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    check_id = db.Column(db.String(50), nullable=False, unique=True)  # e.g., "BPI-001", "CDC-001"
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    pass_criteria = db.Column(db.Text, nullable=False)
    
    # Automation Support Fields
    automation_complexity = db.Column(db.String(20), nullable=False)  # low, medium, high
    document_sources = db.Column(db.Text, nullable=False)  # JSON array of document source mappings
    algorithm_type = db.Column(db.String(50), nullable=False)  # pattern_match, content_analysis, cross_reference
    expected_data_format = db.Column(db.Text)  # JSON format specifications
    confidence_method = db.Column(db.Text)  # JSON confidence scoring method
    
    # Validation Logic
    validation_level = db.Column(db.Integer, nullable=False, default=1)  # 1-4 (structural, content, consistency, quality)
    dependencies = db.Column(db.Text)  # JSON array of dependent check IDs
    conditional_logic = db.Column(db.Text)  # JSON conditional validation rules
    
    # Metadata
    weight = db.Column(db.Float, nullable=False, default=1.0)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    version = db.Column(db.String(20), nullable=False, default='1.0')
    created_by = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EnhancedValidationCriteria {self.check_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'check_id': self.check_id,
            'category': self.category,
            'subcategory': self.subcategory,
            'name': self.name,
            'description': self.description,
            'pass_criteria': self.pass_criteria,
            'automation_complexity': self.automation_complexity,
            'document_sources': json.loads(self.document_sources) if self.document_sources else [],
            'algorithm_type': self.algorithm_type,
            'expected_data_format': json.loads(self.expected_data_format) if self.expected_data_format else {},
            'confidence_method': json.loads(self.confidence_method) if self.confidence_method else {},
            'validation_level': self.validation_level,
            'dependencies': json.loads(self.dependencies) if self.dependencies else [],
            'conditional_logic': json.loads(self.conditional_logic) if self.conditional_logic else {},
            'weight': self.weight,
            'enabled': self.enabled,
            'version': self.version,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DocumentSourceMapping(db.Model):
    """Mapping between validation checks and document sources"""
    __tablename__ = 'document_source_mappings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    criteria_id = db.Column(db.String(36), db.ForeignKey('enhanced_validation_criteria.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # site_survey_part1, site_survey_part2, install_plan_pdf
    worksheet_name = db.Column(db.String(100))  # For Excel documents
    cell_range = db.Column(db.String(50))  # e.g., "A1:Z100"
    content_pattern = db.Column(db.Text)  # Regex or pattern for content extraction
    extraction_method = db.Column(db.String(50), nullable=False)  # direct_cell, pattern_match, table_lookup
    validation_rules = db.Column(db.Text)  # JSON validation rules for extracted content
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DocumentSourceMapping {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'criteria_id': self.criteria_id,
            'document_type': self.document_type,
            'worksheet_name': self.worksheet_name,
            'cell_range': self.cell_range,
            'content_pattern': self.content_pattern,
            'extraction_method': self.extraction_method,
            'validation_rules': json.loads(self.validation_rules) if self.validation_rules else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CrossDocumentValidation(db.Model):
    """Cross-document validation tracking and results"""
    __tablename__ = 'cross_document_validations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(255), nullable=False)
    document_set = db.Column(db.Text, nullable=False)  # JSON array of document IDs/URLs
    validation_type = db.Column(db.String(50), nullable=False)  # consistency, synchronization, completeness
    
    # Results
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, pass, fail, partial
    consistency_score = db.Column(db.Float)  # 0.0 to 1.0
    issues_found = db.Column(db.Text)  # JSON array of consistency issues
    recommendations = db.Column(db.Text)  # JSON array of recommendations
    
    # Execution details
    executed_at = db.Column(db.DateTime)
    execution_time_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CrossDocumentValidation {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'document_set': json.loads(self.document_set) if self.document_set else [],
            'validation_type': self.validation_type,
            'status': self.status,
            'consistency_score': self.consistency_score,
            'issues_found': json.loads(self.issues_found) if self.issues_found else [],
            'recommendations': json.loads(self.recommendations) if self.recommendations else [],
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'execution_time_ms': self.execution_time_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ValidationExecution(db.Model):
    """Enhanced validation execution with detailed results"""
    __tablename__ = 'validation_executions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(255), nullable=False)
    criteria_id = db.Column(db.String(36), db.ForeignKey('enhanced_validation_criteria.id'), nullable=False)
    
    # Execution details
    status = db.Column(db.String(20), nullable=False)  # pass, fail, warning, error, not_applicable
    confidence_score = db.Column(db.Float)  # 0.0 to 1.0
    extracted_content = db.Column(db.Text)  # JSON extracted content
    validation_details = db.Column(db.Text)  # JSON detailed validation results
    
    # Error handling
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    
    # Timing
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    execution_time_ms = db.Column(db.Integer)
    
    # Relationships
    criteria = db.relationship('EnhancedValidationCriteria', backref='executions')
    
    def __repr__(self):
        return f'<ValidationExecution {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'criteria_id': self.criteria_id,
            'status': self.status,
            'confidence_score': self.confidence_score,
            'extracted_content': json.loads(self.extracted_content) if self.extracted_content else {},
            'validation_details': json.loads(self.validation_details) if self.validation_details else {},
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'execution_time_ms': self.execution_time_ms
        }

class ProjectValidationSummary(db.Model):
    """Summary of validation results for a project"""
    __tablename__ = 'project_validation_summaries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(255), nullable=False, unique=True)
    project_name = db.Column(db.String(255))
    
    # Overall results
    overall_status = db.Column(db.String(20), nullable=False)  # pass, fail, partial, in_progress
    overall_score = db.Column(db.Float)  # 0.0 to 1.0
    total_checks = db.Column(db.Integer, nullable=False, default=0)
    passed_checks = db.Column(db.Integer, nullable=False, default=0)
    failed_checks = db.Column(db.Integer, nullable=False, default=0)
    warning_checks = db.Column(db.Integer, nullable=False, default=0)
    
    # Category scores
    category_scores = db.Column(db.Text)  # JSON category-wise scores
    
    # Action plan
    action_plan = db.Column(db.Text)  # JSON action plan
    critical_issues = db.Column(db.Text)  # JSON array of critical issues
    
    # Metadata
    last_validated_at = db.Column(db.DateTime)
    validation_duration_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProjectValidationSummary {self.project_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'overall_status': self.overall_status,
            'overall_score': self.overall_score,
            'total_checks': self.total_checks,
            'passed_checks': self.passed_checks,
            'failed_checks': self.failed_checks,
            'warning_checks': self.warning_checks,
            'category_scores': json.loads(self.category_scores) if self.category_scores else {},
            'action_plan': json.loads(self.action_plan) if self.action_plan else [],
            'critical_issues': json.loads(self.critical_issues) if self.critical_issues else [],
            'last_validated_at': self.last_validated_at.isoformat() if self.last_validated_at else None,
            'validation_duration_ms': self.validation_duration_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ValidationAccuracyMetrics(db.Model):
    """Tracking validation accuracy and continuous improvement"""
    __tablename__ = 'validation_accuracy_metrics'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    criteria_id = db.Column(db.String(36), db.ForeignKey('enhanced_validation_criteria.id'), nullable=False)
    
    # Accuracy tracking
    total_executions = db.Column(db.Integer, nullable=False, default=0)
    correct_predictions = db.Column(db.Integer, nullable=False, default=0)
    false_positives = db.Column(db.Integer, nullable=False, default=0)
    false_negatives = db.Column(db.Integer, nullable=False, default=0)
    accuracy_rate = db.Column(db.Float)  # calculated field
    
    # Performance tracking
    avg_execution_time_ms = db.Column(db.Float)
    avg_confidence_score = db.Column(db.Float)
    
    # Improvement tracking
    last_accuracy_review = db.Column(db.DateTime)
    improvement_suggestions = db.Column(db.Text)  # JSON suggestions
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    criteria = db.relationship('EnhancedValidationCriteria', backref='accuracy_metrics')
    
    def __repr__(self):
        return f'<ValidationAccuracyMetrics {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'criteria_id': self.criteria_id,
            'total_executions': self.total_executions,
            'correct_predictions': self.correct_predictions,
            'false_positives': self.false_positives,
            'false_negatives': self.false_negatives,
            'accuracy_rate': self.accuracy_rate,
            'avg_execution_time_ms': self.avg_execution_time_ms,
            'avg_confidence_score': self.avg_confidence_score,
            'last_accuracy_review': self.last_accuracy_review.isoformat() if self.last_accuracy_review else None,
            'improvement_suggestions': json.loads(self.improvement_suggestions) if self.improvement_suggestions else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

