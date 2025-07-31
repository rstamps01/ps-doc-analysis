from flask import Blueprint, request, jsonify
from src.models.validation import db, ValidationResult, ValidationRequest
from src.notifications.notification_manager import NotificationManager
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__)

# Initialize notification manager
notification_manager = NotificationManager()

@notifications_bp.route('/send', methods=['POST'])
def send_notification():
    """Send a custom notification."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['recipients', 'subject', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Send notification
        success = notification_manager.send_custom_notification(
            recipients=data['recipients'],
            subject=data['subject'],
            message=data['message'],
            notification_type=data.get('type', 'email')
        )
        
        return jsonify({
            'success': success,
            'message': 'Notification sent successfully' if success else 'Failed to send notification'
        }), 200 if success else 500
        
    except Exception as e:
        logger.error(f"Error sending custom notification: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@notifications_bp.route('/send-validation-result', methods=['POST'])
def send_validation_result_notification():
    """Send notification for a specific validation result."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'result_id' not in data:
            return jsonify({'error': 'Missing required field: result_id'}), 400
        
        # Get validation result
        result = ValidationResult.query.get(data['result_id'])
        if not result:
            return jsonify({'error': 'Validation result not found'}), 404
        
        # Get validation request
        request_obj = result.request
        if not request_obj:
            return jsonify({'error': 'Associated validation request not found'}), 404
        
        # Get notification settings
        notification_settings = data.get('settings', {})
        
        # Send notifications
        notification_results = notification_manager.send_validation_notifications(
            validation_result=result,
            validation_request=request_obj,
            notification_settings=notification_settings
        )
        
        return jsonify({
            'success': True,
            'notification_results': notification_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error sending validation result notification: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@notifications_bp.route('/summary-report', methods=['POST'])
def send_summary_report():
    """Send summary report of validation results."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['recipients', 'period']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        period = data['period']  # daily, weekly, monthly
        recipients = data['recipients']
        
        # Calculate date range based on period
        end_date = datetime.now()
        if period == 'daily':
            start_date = end_date - timedelta(days=1)
        elif period == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        elif period == 'monthly':
            start_date = end_date - timedelta(days=30)
        else:
            return jsonify({'error': 'Invalid period. Must be daily, weekly, or monthly'}), 400
        
        # Get validation results for the period
        validation_results = ValidationResult.query.filter(
            ValidationResult.executed_at >= start_date,
            ValidationResult.executed_at <= end_date
        ).order_by(ValidationResult.executed_at.desc()).all()
        
        # Send summary report
        success = notification_manager.send_summary_report(
            validation_results=validation_results,
            recipients=recipients,
            report_period=period
        )
        
        return jsonify({
            'success': success,
            'message': f'Summary report sent successfully for {period} period' if success else 'Failed to send summary report',
            'results_count': len(validation_results),
            'period': period,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }), 200 if success else 500
        
    except Exception as e:
        logger.error(f"Error sending summary report: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@notifications_bp.route('/test', methods=['POST'])
def test_notification_service():
    """Test notification service functionality."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'test_email' not in data:
            return jsonify({'error': 'Missing required field: test_email'}), 400
        
        # Test notification service
        test_results = notification_manager.test_notification_service(data['test_email'])
        
        return jsonify({
            'test_results': test_results,
            'overall_success': all(test_results.values()) if isinstance(test_results, dict) else False
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing notification service: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@notifications_bp.route('/settings', methods=['GET'])
def get_notification_settings():
    """Get default notification settings."""
    try:
        return jsonify({
            'default_settings': notification_manager.default_settings,
            'available_types': ['email'],
            'supported_periods': ['daily', 'weekly', 'monthly']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting notification settings: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@notifications_bp.route('/settings', methods=['POST'])
def update_notification_settings():
    """Update notification settings."""
    try:
        data = request.get_json()
        
        # Update default settings
        if 'default_settings' in data:
            notification_manager.default_settings.update(data['default_settings'])
        
        return jsonify({
            'success': True,
            'message': 'Notification settings updated successfully',
            'current_settings': notification_manager.default_settings
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@notifications_bp.route('/history', methods=['GET'])
def get_notification_history():
    """Get notification history (placeholder for future implementation)."""
    try:
        # This would typically query a notification_logs table
        # For now, return a placeholder response
        
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Placeholder data - in a real implementation, this would come from a database
        history = []
        
        return jsonify({
            'notifications': history,
            'total': len(history),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting notification history: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@notifications_bp.route('/templates', methods=['GET'])
def get_notification_templates():
    """Get available notification templates."""
    try:
        templates = [
            {
                'id': 'validation_result',
                'name': 'Validation Result Notification',
                'description': 'Standard notification sent when validation is completed',
                'type': 'email',
                'variables': ['content_title', 'status', 'score', 'rule_results']
            },
            {
                'id': 'action_plan',
                'name': 'Action Plan Notification',
                'description': 'Notification with action plan for failed or partial validations',
                'type': 'email',
                'variables': ['content_title', 'status', 'priority_tasks', 'optional_tasks']
            },
            {
                'id': 'summary_report',
                'name': 'Summary Report',
                'description': 'Periodic summary of validation results',
                'type': 'email',
                'variables': ['period', 'total_validations', 'pass_rate', 'avg_score']
            }
        ]
        
        return jsonify({
            'templates': templates
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting notification templates: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@notifications_bp.route('/bulk-notify', methods=['POST'])
def bulk_notify_validation_results():
    """Send notifications for multiple validation results."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'result_ids' not in data:
            return jsonify({'error': 'Missing required field: result_ids'}), 400
        
        result_ids = data['result_ids']
        notification_settings = data.get('settings', {})
        
        # Process each validation result
        results = []
        for result_id in result_ids:
            try:
                # Get validation result
                result = ValidationResult.query.get(result_id)
                if not result:
                    results.append({
                        'result_id': result_id,
                        'success': False,
                        'error': 'Validation result not found'
                    })
                    continue
                
                # Get validation request
                request_obj = result.request
                if not request_obj:
                    results.append({
                        'result_id': result_id,
                        'success': False,
                        'error': 'Associated validation request not found'
                    })
                    continue
                
                # Send notifications
                notification_results = notification_manager.send_validation_notifications(
                    validation_result=result,
                    validation_request=request_obj,
                    notification_settings=notification_settings
                )
                
                results.append({
                    'result_id': result_id,
                    'success': True,
                    'notification_results': notification_results
                })
                
            except Exception as e:
                logger.error(f"Error processing result {result_id}: {e}")
                results.append({
                    'result_id': result_id,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate summary
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        return jsonify({
            'success': True,
            'summary': {
                'total_processed': total,
                'successful': successful,
                'failed': total - successful
            },
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error in bulk notification: {e}")
        return jsonify({'error': 'Internal server error'}), 500

