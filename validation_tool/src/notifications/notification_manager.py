import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.notifications.email_service import EmailService
from src.models.validation import db, ValidationResult, ValidationRequest

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manages notifications for validation results and action plans."""
    
    def __init__(self):
        """Initialize notification manager."""
        self.email_service = EmailService()
        
        # Default notification settings
        self.default_settings = {
            'send_on_pass': True,
            'send_on_fail': True,
            'send_on_partial': True,
            'include_action_plan': True,
            'send_to_author': True,
            'send_to_admin': False
        }
    
    def send_validation_notifications(self, validation_result: ValidationResult,
                                    validation_request: ValidationRequest,
                                    notification_settings: Dict[str, Any] = None) -> Dict[str, bool]:
        """
        Send notifications for validation results.
        
        Args:
            validation_result: ValidationResult object
            validation_request: ValidationRequest object
            notification_settings: Custom notification settings
            
        Returns:
            Dictionary with notification results
        """
        settings = {**self.default_settings, **(notification_settings or {})}
        results = {}
        
        try:
            # Check if notifications should be sent based on status
            status = validation_result.overall_status
            should_send = (
                (status == 'pass' and settings.get('send_on_pass', True)) or
                (status == 'fail' and settings.get('send_on_fail', True)) or
                (status == 'partial' and settings.get('send_on_partial', True))
            )
            
            if not should_send:
                logger.info(f"Notifications disabled for status: {status}")
                return {'skipped': True, 'reason': f'Notifications disabled for {status}'}
            
            # Get recipients
            recipients = self._get_recipients(validation_request, settings)
            if not recipients:
                logger.warning("No recipients found for notifications")
                return {'error': 'No recipients found'}
            
            # Get content information
            content_info = self._get_content_info(validation_request)
            
            # Prepare validation result data
            result_data = validation_result.to_dict()
            
            # Send basic validation result notification
            email_sent = self.email_service.send_validation_result_notification(
                validation_result=result_data,
                recipients=recipients,
                content_info=content_info
            )
            results['email_notification'] = email_sent
            
            # Send action plan notification if needed
            if (settings.get('include_action_plan', True) and 
                status in ['fail', 'partial'] and 
                result_data.get('action_plan')):
                
                action_plan_sent = self.email_service.send_action_plan_notification(
                    validation_result=result_data,
                    action_plan=result_data['action_plan'],
                    recipients=recipients,
                    content_info=content_info
                )
                results['action_plan_notification'] = action_plan_sent
            
            # Log notification attempt
            self._log_notification_attempt(validation_result, recipients, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error sending validation notifications: {e}")
            return {'error': str(e)}
    
    def send_custom_notification(self, recipients: List[str], subject: str,
                               message: str, notification_type: str = 'email') -> bool:
        """
        Send custom notification.
        
        Args:
            recipients: List of recipient addresses
            subject: Notification subject
            message: Notification message
            notification_type: Type of notification (email, slack, etc.)
            
        Returns:
            True if notification sent successfully
        """
        try:
            if notification_type == 'email':
                # Create simple HTML message
                html_message = f"""
                <html>
                <body>
                    <h3>{subject}</h3>
                    <p>{message}</p>
                    <hr>
                    <p><em>This is an automated notification from the Information Validation Tool.</em></p>
                    <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </body>
                </html>
                """
                
                return self.email_service._send_email(
                    recipients=recipients,
                    subject=subject,
                    html_body=html_message,
                    text_body=message
                )
            else:
                logger.warning(f"Unsupported notification type: {notification_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending custom notification: {e}")
            return False
    
    def send_summary_report(self, validation_results: List[ValidationResult],
                          recipients: List[str], 
                          report_period: str = "daily") -> bool:
        """
        Send summary report of validation results.
        
        Args:
            validation_results: List of ValidationResult objects
            recipients: List of recipient email addresses
            report_period: Report period (daily, weekly, monthly)
            
        Returns:
            True if report sent successfully
        """
        try:
            if not validation_results:
                logger.info("No validation results to report")
                return True
            
            # Generate summary statistics
            total_validations = len(validation_results)
            passed = sum(1 for r in validation_results if r.overall_status == 'pass')
            failed = sum(1 for r in validation_results if r.overall_status == 'fail')
            partial = sum(1 for r in validation_results if r.overall_status == 'partial')
            
            avg_score = sum(r.score for r in validation_results) / total_validations
            avg_execution_time = sum(r.execution_time_ms for r in validation_results) / total_validations
            
            # Generate report content
            subject = f"Validation Summary Report - {report_period.title()}"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                    .stat {{ text-align: center; padding: 15px; background-color: #e9ecef; border-radius: 5px; }}
                    .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                    .results-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    .results-table th {{ background-color: #f2f2f2; }}
                    .status-pass {{ color: #28a745; font-weight: bold; }}
                    .status-fail {{ color: #dc3545; font-weight: bold; }}
                    .status-partial {{ color: #ffc107; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>📊 Validation Summary Report</h2>
                    <p><strong>Period:</strong> {report_period.title()}</p>
                    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{total_validations}</div>
                        <div>Total Validations</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{passed}</div>
                        <div>Passed</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{failed}</div>
                        <div>Failed</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{partial}</div>
                        <div>Partial</div>
                    </div>
                </div>
                
                <h3>📈 Key Metrics</h3>
                <ul>
                    <li><strong>Average Score:</strong> {avg_score:.3f}/1.0 ({avg_score*100:.1f}%)</li>
                    <li><strong>Pass Rate:</strong> {(passed/total_validations)*100:.1f}%</li>
                    <li><strong>Average Execution Time:</strong> {avg_execution_time:.0f}ms</li>
                </ul>
                
                <h3>📋 Recent Validations</h3>
                <table class="results-table">
                    <tr>
                        <th>Content ID</th>
                        <th>Status</th>
                        <th>Score</th>
                        <th>Execution Time</th>
                        <th>Date</th>
                    </tr>
            """
            
            # Add recent validation results
            for result in validation_results[-10:]:  # Show last 10 results
                status_class = f"status-{result.overall_status}"
                html_content += f"""
                    <tr>
                        <td>{result.request.content_id if result.request else 'Unknown'}</td>
                        <td><span class="{status_class}">{result.overall_status.upper()}</span></td>
                        <td>{result.score:.3f}</td>
                        <td>{result.execution_time_ms}ms</td>
                        <td>{result.executed_at.strftime('%Y-%m-%d %H:%M') if result.executed_at else 'Unknown'}</td>
                    </tr>
                """
            
            html_content += """
                </table>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
                    <p>This is an automated summary report from the Information Validation Tool.</p>
                </div>
            </body>
            </html>
            """
            
            # Generate text version
            text_content = f"""
VALIDATION SUMMARY REPORT - {report_period.upper()}
{'=' * 50}

SUMMARY STATISTICS
Total Validations: {total_validations}
Passed: {passed}
Failed: {failed}
Partial: {partial}

KEY METRICS
Average Score: {avg_score:.3f}/1.0 ({avg_score*100:.1f}%)
Pass Rate: {(passed/total_validations)*100:.1f}%
Average Execution Time: {avg_execution_time:.0f}ms

This is an automated summary report from the Information Validation Tool.
Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            # Send report
            return self.email_service._send_email(
                recipients=recipients,
                subject=subject,
                html_body=html_content,
                text_body=text_content
            )
            
        except Exception as e:
            logger.error(f"Error sending summary report: {e}")
            return False
    
    def _get_recipients(self, validation_request: ValidationRequest,
                       settings: Dict[str, Any]) -> List[str]:
        """Get notification recipients based on settings."""
        recipients = []
        
        try:
            # Get author email from request metadata
            extra_data = json.loads(validation_request.extra_data or '{}')
            author_email = extra_data.get('author_email')
            
            if settings.get('send_to_author', True) and author_email:
                recipients.append(author_email)
            
            # Add admin recipients if configured
            if settings.get('send_to_admin', False):
                admin_emails = settings.get('admin_emails', [])
                recipients.extend(admin_emails)
            
            # Add custom recipients
            custom_recipients = settings.get('custom_recipients', [])
            recipients.extend(custom_recipients)
            
            # Remove duplicates
            recipients = list(set(recipients))
            
        except Exception as e:
            logger.error(f"Error getting recipients: {e}")
        
        return recipients
    
    def _get_content_info(self, validation_request: ValidationRequest) -> Dict[str, Any]:
        """Get content information for notifications."""
        try:
            extra_data = json.loads(validation_request.extra_data or '{}')
            
            return {
                'title': extra_data.get('content_title', f"Content {validation_request.content_id}"),
                'type': validation_request.content_type,
                'id': validation_request.content_id,
                'author': extra_data.get('author_name', 'Unknown'),
                'url': extra_data.get('content_url', '')
            }
            
        except Exception as e:
            logger.error(f"Error getting content info: {e}")
            return {
                'title': f"Content {validation_request.content_id}",
                'type': validation_request.content_type,
                'id': validation_request.content_id,
                'author': 'Unknown',
                'url': ''
            }
    
    def _log_notification_attempt(self, validation_result: ValidationResult,
                                recipients: List[str], results: Dict[str, bool]):
        """Log notification attempt for audit purposes."""
        try:
            log_data = {
                'validation_result_id': validation_result.id,
                'recipients': recipients,
                'notification_results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Notification attempt logged: {json.dumps(log_data)}")
            
        except Exception as e:
            logger.error(f"Error logging notification attempt: {e}")
    
    def test_notification_service(self, test_email: str) -> Dict[str, bool]:
        """
        Test notification services.
        
        Args:
            test_email: Email address to send test notification
            
        Returns:
            Dictionary with test results
        """
        results = {}
        
        try:
            # Test email service
            email_test = self.email_service.test_connection()
            results['email_connection'] = email_test
            
            if email_test:
                # Send test email
                test_sent = self.send_custom_notification(
                    recipients=[test_email],
                    subject="Test Notification - Information Validation Tool",
                    message="This is a test notification to verify the email service is working correctly."
                )
                results['test_email_sent'] = test_sent
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing notification service: {e}")
            return {'error': str(e)}

