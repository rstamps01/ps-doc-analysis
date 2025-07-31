from flask import Blueprint, request, jsonify, current_app
from src.models.validation import db, ValidationRequest, ValidationResult, ValidationRule, IntegrationConfig, AuditLog
from src.validation.engine import ValidationEngine
from src.integrations.google_sheets import GoogleSheetsIntegration
from src.integrations.confluence import ConfluenceIntegration
from src.notifications.notification_manager import NotificationManager
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

validation_bp = Blueprint('validation', __name__)

# Initialize validation engine and notification manager
validation_engine = ValidationEngine()
notification_manager = NotificationManager()

@validation_bp.route('/validate', methods=['POST'])
def create_validation_request():
    """Create a new validation request."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['source_sheet_id', 'content_id', 'content_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create validation request
        validation_request = ValidationRequest(
            source_sheet_id=data['source_sheet_id'],
            source_sheet_range=data.get('source_sheet_range', 'A:Z'),
            content_id=data['content_id'],
            content_type=data['content_type'],
            validation_rules=json.dumps(data.get('validation_rules', [])),
            priority=data.get('priority', 'medium'),
            requested_by=data.get('requested_by', 'system'),
            extra_data=json.dumps(data.get('metadata', {}))
        )
        
        db.session.add(validation_request)
        db.session.commit()
        
        # Log the request
        _log_audit_event('validation_request_created', 'validation_request', 
                        validation_request.id, data.get('requested_by', 'system'))
        
        # Process validation asynchronously (for now, process synchronously)
        try:
            result = _process_validation_request(validation_request)
            return jsonify({
                'request_id': validation_request.id,
                'status': 'completed',
                'result': result.to_dict() if result else None
            }), 201
        except Exception as e:
            logger.error(f"Error processing validation request: {e}")
            validation_request.status = 'failed'
            db.session.commit()
            return jsonify({
                'request_id': validation_request.id,
                'status': 'failed',
                'error': str(e)
            }), 500
        
    except Exception as e:
        logger.error(f"Error creating validation request: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@validation_bp.route('/requests', methods=['GET'])
def get_validation_requests():
    """Get validation requests with optional filtering."""
    try:
        # Get query parameters
        status = request.args.get('status')
        content_type = request.args.get('content_type')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = ValidationRequest.query
        
        if status:
            query = query.filter(ValidationRequest.status == status)
        if content_type:
            query = query.filter(ValidationRequest.content_type == content_type)
        
        # Apply pagination
        requests = query.order_by(ValidationRequest.created_at.desc()).offset(offset).limit(limit).all()
        total = query.count()
        
        return jsonify({
            'requests': [req.to_dict() for req in requests],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting validation requests: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@validation_bp.route('/requests/<request_id>', methods=['GET'])
def get_validation_request(request_id):
    """Get a specific validation request."""
    try:
        validation_request = ValidationRequest.query.get(request_id)
        if not validation_request:
            return jsonify({'error': 'Validation request not found'}), 404
        
        # Include results if available
        request_data = validation_request.to_dict()
        if validation_request.results:
            request_data['results'] = [result.to_dict() for result in validation_request.results]
        
        return jsonify(request_data), 200
        
    except Exception as e:
        logger.error(f"Error getting validation request: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@validation_bp.route('/results/<result_id>', methods=['GET'])
def get_validation_result(result_id):
    """Get a specific validation result."""
    try:
        result = ValidationResult.query.get(result_id)
        if not result:
            return jsonify({'error': 'Validation result not found'}), 404
        
        return jsonify(result.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error getting validation result: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@validation_bp.route('/rules', methods=['GET'])
def get_validation_rules():
    """Get validation rules."""
    try:
        category = request.args.get('category')
        enabled_only = request.args.get('enabled', 'true').lower() == 'true'
        
        query = ValidationRule.query
        
        if category:
            query = query.filter(ValidationRule.category == category)
        if enabled_only:
            query = query.filter(ValidationRule.enabled == True)
        
        rules = query.order_by(ValidationRule.name).all()
        
        return jsonify({
            'rules': [rule.to_dict() for rule in rules]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting validation rules: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@validation_bp.route('/rules', methods=['POST'])
def create_validation_rule():
    """Create a new validation rule."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'category', 'rule_type', 'configuration']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create validation rule
        rule = ValidationRule(
            name=data['name'],
            description=data.get('description', ''),
            category=data['category'],
            rule_type=data['rule_type'],
            configuration=json.dumps(data['configuration']),
            weight=data.get('weight', 1.0),
            enabled=data.get('enabled', True),
            created_by=data.get('created_by', 'system')
        )
        
        db.session.add(rule)
        db.session.commit()
        
        # Log the creation
        _log_audit_event('validation_rule_created', 'validation_rule', 
                        rule.id, data.get('created_by', 'system'))
        
        return jsonify(rule.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating validation rule: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@validation_bp.route('/rules/<rule_id>', methods=['PUT'])
def update_validation_rule(rule_id):
    """Update a validation rule."""
    try:
        rule = ValidationRule.query.get(rule_id)
        if not rule:
            return jsonify({'error': 'Validation rule not found'}), 404
        
        data = request.get_json()
        old_values = rule.to_dict()
        
        # Update fields
        if 'name' in data:
            rule.name = data['name']
        if 'description' in data:
            rule.description = data['description']
        if 'category' in data:
            rule.category = data['category']
        if 'rule_type' in data:
            rule.rule_type = data['rule_type']
        if 'configuration' in data:
            rule.configuration = json.dumps(data['configuration'])
        if 'weight' in data:
            rule.weight = data['weight']
        if 'enabled' in data:
            rule.enabled = data['enabled']
        
        db.session.commit()
        
        # Log the update
        _log_audit_event('validation_rule_updated', 'validation_rule', 
                        rule.id, data.get('updated_by', 'system'),
                        old_values=old_values, new_values=rule.to_dict())
        
        return jsonify(rule.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error updating validation rule: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@validation_bp.route('/integrations', methods=['GET'])
def get_integrations():
    """Get integration configurations."""
    try:
        system_type = request.args.get('system_type')
        enabled_only = request.args.get('enabled', 'true').lower() == 'true'
        
        query = IntegrationConfig.query
        
        if system_type:
            query = query.filter(IntegrationConfig.system_type == system_type)
        if enabled_only:
            query = query.filter(IntegrationConfig.enabled == True)
        
        configs = query.order_by(IntegrationConfig.name).all()
        
        # Remove sensitive authentication data from response
        config_data = []
        for config in configs:
            config_dict = config.to_dict()
            # Mask authentication details
            if 'authentication' in config_dict:
                config_dict['authentication'] = {'configured': True}
            config_data.append(config_dict)
        
        return jsonify({
            'integrations': config_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting integrations: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@validation_bp.route('/integrations/test/<integration_id>', methods=['POST'])
def test_integration(integration_id):
    """Test an integration configuration."""
    try:
        config = IntegrationConfig.query.get(integration_id)
        if not config:
            return jsonify({'error': 'Integration configuration not found'}), 404
        
        # Test the integration based on system type
        if config.system_type == 'google_sheets':
            auth_config = json.loads(config.authentication)
            integration = GoogleSheetsIntegration(credentials_json=auth_config)
            success = integration.test_connection()
        elif config.system_type == 'confluence':
            auth_config = json.loads(config.authentication)
            integration = ConfluenceIntegration(
                base_url=config.endpoint_url,
                username=auth_config.get('username'),
                api_token=auth_config.get('api_token'),
                oauth_token=auth_config.get('oauth_token')
            )
            success = integration.test_connection()
        else:
            return jsonify({'error': 'Unsupported integration type'}), 400
        
        return jsonify({
            'integration_id': integration_id,
            'success': success,
            'tested_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@validation_bp.route('/audit-logs', methods=['GET'])
def get_audit_logs():
    """Get audit logs with optional filtering."""
    try:
        event_type = request.args.get('event_type')
        resource_type = request.args.get('resource_type')
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        query = AuditLog.query
        
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
        total = query.count()
        
        return jsonify({
            'logs': [log.to_dict() for log in logs],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def _process_validation_request(validation_request: ValidationRequest) -> ValidationResult:
    """Process a validation request and generate results."""
    try:
        # Update request status
        validation_request.status = 'processing'
        db.session.commit()
        
        # Get validation rules
        rule_ids = json.loads(validation_request.validation_rules)
        if rule_ids:
            rules = ValidationRule.query.filter(
                ValidationRule.id.in_(rule_ids),
                ValidationRule.enabled == True
            ).all()
        else:
            # Use all enabled rules if none specified
            rules = ValidationRule.query.filter(ValidationRule.enabled == True).all()
        
        # Get content based on content type
        if validation_request.content_type == 'confluence_page':
            content = _get_confluence_content(validation_request.content_id)
        elif validation_request.content_type == 'salesforce_record':
            content = _get_salesforce_content(validation_request.content_id)
        else:
            raise ValueError(f"Unsupported content type: {validation_request.content_type}")
        
        # Convert rules to dict format for validation engine
        rule_dicts = [rule.to_dict() for rule in rules]
        
        # Run validation
        validation_result_data = validation_engine.validate_content(content, rule_dicts)
        
        # Create validation result record
        result = ValidationResult(
            request_id=validation_request.id,
            overall_status=validation_result_data['overall_status'],
            score=validation_result_data['score'],
            rule_results=json.dumps(validation_result_data['rule_results']),
            action_plan=json.dumps(validation_result_data['action_plan']),
            execution_time_ms=validation_result_data['execution_time_ms'],
            metadata=json.dumps({
                'content_summary': validation_result_data.get('content_summary', {}),
                'validated_at': validation_result_data.get('validated_at')
            })
        )
        
        db.session.add(result)
        
        # Update request status
        validation_request.status = 'completed'
        db.session.commit()
        
        # Update Google Sheets with results
        _update_sheets_status(validation_request, result)
        
        # Send notifications
        try:
            notification_results = notification_manager.send_validation_notifications(
                validation_result=result,
                validation_request=validation_request
            )
            logger.info(f"Notifications sent for validation {validation_request.id}: {notification_results}")
        except Exception as e:
            logger.error(f"Error sending notifications for validation {validation_request.id}: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing validation request {validation_request.id}: {e}")
        validation_request.status = 'failed'
        db.session.commit()
        raise

def _get_confluence_content(page_id: str) -> Dict[str, Any]:
    """Get content from Confluence."""
    # Get Confluence integration config
    config = IntegrationConfig.query.filter_by(
        system_type='confluence',
        enabled=True
    ).first()
    
    if not config:
        raise ValueError("No Confluence integration configured")
    
    auth_config = json.loads(config.authentication)
    integration = ConfluenceIntegration(
        base_url=config.endpoint_url,
        username=auth_config.get('username'),
        api_token=auth_config.get('api_token'),
        oauth_token=auth_config.get('oauth_token')
    )
    
    # Get page content
    page_content = integration.get_page_content(page_id)
    structured_data = integration.extract_structured_data(page_content)
    
    return structured_data

def _get_salesforce_content(record_id: str) -> Dict[str, Any]:
    """Get content from Salesforce (placeholder)."""
    # This would implement Salesforce integration
    # For now, return a placeholder
    return {
        'id': record_id,
        'type': 'salesforce_record',
        'title': 'Salesforce Record',
        'content': {
            'text_content': 'Placeholder Salesforce content'
        }
    }

def _update_sheets_status(validation_request: ValidationRequest, result: ValidationResult):
    """Update Google Sheets with validation results."""
    try:
        # Get Google Sheets integration config
        config = IntegrationConfig.query.filter_by(
            system_type='google_sheets',
            enabled=True
        ).first()
        
        if not config:
            logger.warning("No Google Sheets integration configured")
            return
        
        auth_config = json.loads(config.authentication)
        integration = GoogleSheetsIntegration(credentials_json=auth_config)
        
        # Determine status value to write
        status_value = "Pass" if result.overall_status == "pass" else "Fail"
        if result.overall_status == "partial":
            status_value = "Partial"
        
        # Get the row number from request extra_data
        extra_data = json.loads(validation_request.extra_data)
        row_number = extra_data.get('row_number')
        
        if row_number:
            # Update status column (assuming column E for status)
            additional_updates = {
                'F': f"Score: {result.score:.2f}",  # Score in column F
                'G': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  # Timestamp in column G
            }
            
            success = integration.update_status(
                validation_request.source_sheet_id,
                row_number,
                'E',  # Status column
                status_value,
                additional_updates
            )
            
            if success:
                logger.info(f"Updated Google Sheets status for request {validation_request.id}")
            else:
                logger.error(f"Failed to update Google Sheets status for request {validation_request.id}")
        
    except Exception as e:
        logger.error(f"Error updating Google Sheets status: {e}")

def _log_audit_event(event_type: str, resource_type: str, resource_id: str, 
                    user_id: str, old_values: Dict = None, new_values: Dict = None):
    """Log an audit event."""
    try:
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=event_type,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error logging audit event: {e}")

