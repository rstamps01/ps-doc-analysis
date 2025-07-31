from .user import db
from datetime import datetime
import json
import uuid

class ValidationRequest(db.Model):
    __tablename__ = 'validation_requests'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_sheet_id = db.Column(db.String(255), nullable=False)
    source_sheet_range = db.Column(db.String(100), nullable=False, default='A:Z')
    content_id = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # confluence_page, salesforce_record
    validation_rules = db.Column(db.Text, nullable=False)  # JSON array of rule IDs
    priority = db.Column(db.String(20), nullable=False, default='medium')
    requested_by = db.Column(db.String(255), nullable=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='pending')
    extra_data = db.Column(db.Text, default='{}')  # JSON metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to validation results
    results = db.relationship('ValidationResult', backref='request', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ValidationRequest {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_sheet_id': self.source_sheet_id,
            'source_sheet_range': self.source_sheet_range,
            'content_id': self.content_id,
            'content_type': self.content_type,
            'validation_rules': json.loads(self.validation_rules) if self.validation_rules else [],
            'priority': self.priority,
            'requested_by': self.requested_by,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'status': self.status,
            'metadata': json.loads(self.extra_data) if self.extra_data else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ValidationResult(db.Model):
    __tablename__ = 'validation_results'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = db.Column(db.String(36), db.ForeignKey('validation_requests.id'), nullable=False)
    overall_status = db.Column(db.String(20), nullable=False)  # pass, fail, partial
    score = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    rule_results = db.Column(db.Text, nullable=False)  # JSON array of rule results
    action_plan = db.Column(db.Text)  # JSON action plan
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    execution_time_ms = db.Column(db.Integer, nullable=False)
    extra_data = db.Column(db.Text, default='{}')  # JSON metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ValidationResult {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'overall_status': self.overall_status,
            'score': self.score,
            'rule_results': json.loads(self.rule_results) if self.rule_results else [],
            'action_plan': json.loads(self.action_plan) if self.action_plan else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'execution_time_ms': self.execution_time_ms,
            'metadata': json.loads(self.extra_data) if self.extra_data else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ValidationRule(db.Model):
    __tablename__ = 'validation_rules'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # completeness, accuracy, compliance, quality
    rule_type = db.Column(db.String(50), nullable=False)  # field_presence, format_validation, business_logic
    configuration = db.Column(db.Text, nullable=False)  # JSON configuration
    weight = db.Column(db.Float, nullable=False, default=1.0)  # 0.0 to 1.0
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ValidationRule {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'rule_type': self.rule_type,
            'configuration': json.loads(self.configuration) if self.configuration else {},
            'weight': self.weight,
            'enabled': self.enabled,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class IntegrationConfig(db.Model):
    __tablename__ = 'integration_configs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    system_type = db.Column(db.String(50), nullable=False)  # google_sheets, confluence, salesforce
    name = db.Column(db.String(255), nullable=False)
    endpoint_url = db.Column(db.String(500), nullable=False)
    authentication = db.Column(db.Text, nullable=False)  # JSON auth config (encrypted)
    rate_limits = db.Column(db.Text)  # JSON rate limit config
    field_mappings = db.Column(db.Text)  # JSON field mappings
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<IntegrationConfig {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'system_type': self.system_type,
            'name': self.name,
            'endpoint_url': self.endpoint_url,
            'authentication': json.loads(self.authentication) if self.authentication else {},
            'rate_limits': json.loads(self.rate_limits) if self.rate_limits else {},
            'field_mappings': json.loads(self.field_mappings) if self.field_mappings else {},
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = db.Column(db.String(50), nullable=False)  # user_action, system_event, data_change
    user_id = db.Column(db.String(255))
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.String(255), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    old_values = db.Column(db.Text)  # JSON old values
    new_values = db.Column(db.Text)  # JSON new values
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    extra_data = db.Column(db.Text, default='{}')  # JSON metadata
    
    def __repr__(self):
        return f'<AuditLog {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'user_id': self.user_id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'action': self.action,
            'old_values': json.loads(self.old_values) if self.old_values else None,
            'new_values': json.loads(self.new_values) if self.new_values else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metadata': json.loads(self.extra_data) if self.extra_data else {}
        }

