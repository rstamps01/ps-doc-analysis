import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from jinja2 import Template

logger = logging.getLogger(__name__)

class EmailService:
    """Email notification service for validation results."""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587, 
                 username: str = None, password: str = None, use_tls: bool = True):
        """
        Initialize email service.
        
        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            use_tls: Whether to use TLS encryption
        """
        # Use environment variables if not provided
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.username = username or os.getenv('SMTP_USERNAME')
        self.password = password or os.getenv('SMTP_PASSWORD')
        self.use_tls = use_tls
        
        # Default sender
        self.default_sender = self.username or os.getenv('DEFAULT_SENDER_EMAIL')
        
        if not all([self.smtp_server, self.username, self.password]):
            logger.warning("Email service not fully configured. Some features may not work.")
    
    def send_validation_result_notification(self, validation_result: Dict[str, Any], 
                                          recipients: List[str], 
                                          content_info: Dict[str, Any] = None) -> bool:
        """
        Send validation result notification email.
        
        Args:
            validation_result: Validation result data
            recipients: List of recipient email addresses
            content_info: Additional content information
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Generate email content
            subject = self._generate_subject(validation_result, content_info)
            html_body = self._generate_html_body(validation_result, content_info)
            text_body = self._generate_text_body(validation_result, content_info)
            
            # Send email
            return self._send_email(
                recipients=recipients,
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
        except Exception as e:
            logger.error(f"Error sending validation result notification: {e}")
            return False
    
    def send_action_plan_notification(self, validation_result: Dict[str, Any],
                                    action_plan: Dict[str, Any],
                                    recipients: List[str],
                                    content_info: Dict[str, Any] = None) -> bool:
        """
        Send action plan notification email.
        
        Args:
            validation_result: Validation result data
            action_plan: Action plan data
            recipients: List of recipient email addresses
            content_info: Additional content information
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Generate email content
            subject = self._generate_action_plan_subject(validation_result, content_info)
            html_body = self._generate_action_plan_html_body(validation_result, action_plan, content_info)
            text_body = self._generate_action_plan_text_body(validation_result, action_plan, content_info)
            
            # Send email
            return self._send_email(
                recipients=recipients,
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
        except Exception as e:
            logger.error(f"Error sending action plan notification: {e}")
            return False
    
    def _send_email(self, recipients: List[str], subject: str, 
                   html_body: str, text_body: str = None,
                   attachments: List[str] = None) -> bool:
        """
        Send email using SMTP.
        
        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body
            attachments: List of file paths to attach
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.default_sender:
            logger.error("No sender email configured")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.default_sender
            message["To"] = ", ".join(recipients)
            
            # Add text and HTML parts
            if text_body:
                text_part = MIMEText(text_body, "plain")
                message.attach(text_part)
            
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        message.attach(part)
            
            # Create SMTP session
            if self.use_tls:
                context = ssl.create_default_context()
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls(context=context)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            # Login and send email
            if self.username and self.password:
                server.login(self.username, self.password)
            
            server.sendmail(self.default_sender, recipients, message.as_string())
            server.quit()
            
            logger.info(f"Email sent successfully to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def _generate_subject(self, validation_result: Dict[str, Any], 
                         content_info: Dict[str, Any] = None) -> str:
        """Generate email subject for validation result."""
        status = validation_result.get('overall_status', 'unknown')
        content_title = content_info.get('title', 'Content') if content_info else 'Content'
        
        status_text = {
            'pass': 'Validation Passed',
            'fail': 'Validation Failed',
            'partial': 'Validation Partially Passed'
        }.get(status, 'Validation Completed')
        
        return f"{status_text}: {content_title}"
    
    def _generate_html_body(self, validation_result: Dict[str, Any], 
                           content_info: Dict[str, Any] = None) -> str:
        """Generate HTML email body for validation result."""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .status-pass { color: #28a745; font-weight: bold; }
                .status-fail { color: #dc3545; font-weight: bold; }
                .status-partial { color: #ffc107; font-weight: bold; }
                .score { font-size: 18px; margin: 10px 0; }
                .rule-result { margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }
                .rule-pass { border-left-color: #28a745; }
                .rule-fail { border-left-color: #dc3545; }
                .rule-warning { border-left-color: #ffc107; }
                .findings { margin-top: 10px; }
                .finding { margin: 5px 0; padding: 5px; background-color: #f8f9fa; border-radius: 3px; }
                .recommendations { margin-top: 10px; }
                .recommendation { margin: 5px 0; padding: 5px; background-color: #e7f3ff; border-radius: 3px; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Validation Result Notification</h2>
                <p><strong>Content:</strong> {{ content_title }}</p>
                <p><strong>Status:</strong> <span class="status-{{ status_class }}">{{ status_text }}</span></p>
                <p class="score"><strong>Score:</strong> {{ score }}/1.0 ({{ score_percentage }}%)</p>
                <p><strong>Validated At:</strong> {{ validated_at }}</p>
            </div>
            
            <h3>Validation Results</h3>
            {% for rule_result in rule_results %}
            <div class="rule-result rule-{{ rule_result.status }}">
                <h4>{{ rule_result.rule_name }}</h4>
                <p><strong>Status:</strong> {{ rule_result.status|title }}</p>
                <p><strong>Score:</strong> {{ rule_result.score }}/1.0</p>
                <p><strong>Message:</strong> {{ rule_result.message }}</p>
                
                {% if rule_result.findings %}
                <div class="findings">
                    <strong>Findings:</strong>
                    {% for finding in rule_result.findings %}
                    <div class="finding">
                        <strong>{{ finding.type|replace('_', ' ')|title }}:</strong> {{ finding.description }}
                        {% if finding.field_name %}
                        <br><em>Field:</em> {{ finding.field_name }}
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if rule_result.recommendations %}
                <div class="recommendations">
                    <strong>Recommendations:</strong>
                    {% for recommendation in rule_result.recommendations %}
                    <div class="recommendation">{{ recommendation }}</div>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
            
            <div class="footer">
                <p>This is an automated notification from the Information Validation Tool.</p>
                <p>Generated at {{ current_time }}</p>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_str)
        
        # Prepare template variables
        status = validation_result.get('overall_status', 'unknown')
        score = validation_result.get('score', 0)
        
        status_class = status
        status_text = {
            'pass': 'PASSED',
            'fail': 'FAILED', 
            'partial': 'PARTIALLY PASSED'
        }.get(status, 'COMPLETED')
        
        return template.render(
            content_title=content_info.get('title', 'Unknown Content') if content_info else 'Unknown Content',
            status_class=status_class,
            status_text=status_text,
            score=score,
            score_percentage=int(score * 100),
            validated_at=validation_result.get('validated_at', 'Unknown'),
            rule_results=validation_result.get('rule_results', []),
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def _generate_text_body(self, validation_result: Dict[str, Any], 
                           content_info: Dict[str, Any] = None) -> str:
        """Generate plain text email body for validation result."""
        lines = []
        lines.append("VALIDATION RESULT NOTIFICATION")
        lines.append("=" * 40)
        lines.append("")
        
        content_title = content_info.get('title', 'Unknown Content') if content_info else 'Unknown Content'
        status = validation_result.get('overall_status', 'unknown')
        score = validation_result.get('score', 0)
        
        lines.append(f"Content: {content_title}")
        lines.append(f"Status: {status.upper()}")
        lines.append(f"Score: {score}/1.0 ({int(score * 100)}%)")
        lines.append(f"Validated At: {validation_result.get('validated_at', 'Unknown')}")
        lines.append("")
        
        lines.append("VALIDATION RESULTS")
        lines.append("-" * 20)
        
        for rule_result in validation_result.get('rule_results', []):
            lines.append("")
            lines.append(f"Rule: {rule_result.get('rule_name', 'Unknown')}")
            lines.append(f"Status: {rule_result.get('status', 'unknown').upper()}")
            lines.append(f"Score: {rule_result.get('score', 0)}/1.0")
            lines.append(f"Message: {rule_result.get('message', '')}")
            
            findings = rule_result.get('findings', [])
            if findings:
                lines.append("Findings:")
                for finding in findings:
                    lines.append(f"  - {finding.get('description', '')}")
            
            recommendations = rule_result.get('recommendations', [])
            if recommendations:
                lines.append("Recommendations:")
                for recommendation in recommendations:
                    lines.append(f"  - {recommendation}")
        
        lines.append("")
        lines.append("This is an automated notification from the Information Validation Tool.")
        lines.append(f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)
    
    def _generate_action_plan_subject(self, validation_result: Dict[str, Any], 
                                    content_info: Dict[str, Any] = None) -> str:
        """Generate email subject for action plan."""
        content_title = content_info.get('title', 'Content') if content_info else 'Content'
        return f"Action Plan Required: {content_title}"
    
    def _generate_action_plan_html_body(self, validation_result: Dict[str, Any],
                                      action_plan: Dict[str, Any],
                                      content_info: Dict[str, Any] = None) -> str:
        """Generate HTML email body for action plan."""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #fff3cd; padding: 20px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #ffeaa7; }
                .summary { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                .task-section { margin: 20px 0; }
                .task { margin: 10px 0; padding: 15px; border-left: 4px solid #007bff; background-color: #f8f9fa; border-radius: 3px; }
                .task-high { border-left-color: #dc3545; }
                .task-medium { border-left-color: #ffc107; }
                .task-low { border-left-color: #28a745; }
                .effort { color: #666; font-style: italic; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🔧 Action Plan Required</h2>
                <p><strong>Content:</strong> {{ content_title }}</p>
                <p><strong>Validation Status:</strong> {{ status_text }}</p>
                <p><strong>Current Score:</strong> {{ score }}/1.0 ({{ score_percentage }}%)</p>
            </div>
            
            <div class="summary">
                <h3>📋 Summary</h3>
                <p>Your content validation has identified areas that need attention. Please review the action plan below to improve your content and achieve a passing score.</p>
                <p><strong>Total Estimated Effort:</strong> {{ total_effort }} hours</p>
                <p><strong>Priority Tasks:</strong> {{ priority_task_count }}</p>
                <p><strong>Optional Tasks:</strong> {{ optional_task_count }}</p>
            </div>
            
            {% if priority_tasks %}
            <div class="task-section">
                <h3>🚨 Priority Tasks (Required)</h3>
                <p>These tasks must be completed to achieve a passing validation score:</p>
                {% for task in priority_tasks %}
                <div class="task task-{{ task.priority }}">
                    <h4>{{ task.title }}</h4>
                    <p>{{ task.description }}</p>
                    <p class="effort">Estimated effort: {{ task.estimated_effort_hours }} hours</p>
                    {% if task.category %}
                    <p><em>Category: {{ task.category|title }}</em></p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if optional_tasks %}
            <div class="task-section">
                <h3>💡 Optional Improvements</h3>
                <p>These tasks can further improve your content quality:</p>
                {% for task in optional_tasks %}
                <div class="task task-{{ task.priority }}">
                    <h4>{{ task.title }}</h4>
                    <p>{{ task.description }}</p>
                    <p class="effort">Estimated effort: {{ task.estimated_effort_hours }} hours</p>
                    {% if task.category %}
                    <p><em>Category: {{ task.category|title }}</em></p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            <div class="footer">
                <p><strong>Next Steps:</strong></p>
                <ol>
                    <li>Review and complete the priority tasks listed above</li>
                    <li>Update your content accordingly</li>
                    <li>Request a new validation when ready</li>
                </ol>
                <p>This action plan was generated automatically based on your validation results.</p>
                <p>Generated at {{ current_time }}</p>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_str)
        
        # Prepare template variables
        status = validation_result.get('overall_status', 'unknown')
        score = validation_result.get('score', 0)
        
        status_text = {
            'pass': 'PASSED',
            'fail': 'FAILED',
            'partial': 'PARTIALLY PASSED'
        }.get(status, 'COMPLETED')
        
        priority_tasks = action_plan.get('priority_tasks', [])
        optional_tasks = action_plan.get('optional_tasks', [])
        
        return template.render(
            content_title=content_info.get('title', 'Unknown Content') if content_info else 'Unknown Content',
            status_text=status_text,
            score=score,
            score_percentage=int(score * 100),
            total_effort=action_plan.get('estimated_effort_hours', 0),
            priority_task_count=len(priority_tasks),
            optional_task_count=len(optional_tasks),
            priority_tasks=priority_tasks,
            optional_tasks=optional_tasks,
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def _generate_action_plan_text_body(self, validation_result: Dict[str, Any],
                                      action_plan: Dict[str, Any],
                                      content_info: Dict[str, Any] = None) -> str:
        """Generate plain text email body for action plan."""
        lines = []
        lines.append("ACTION PLAN REQUIRED")
        lines.append("=" * 40)
        lines.append("")
        
        content_title = content_info.get('title', 'Unknown Content') if content_info else 'Unknown Content'
        status = validation_result.get('overall_status', 'unknown')
        score = validation_result.get('score', 0)
        
        lines.append(f"Content: {content_title}")
        lines.append(f"Validation Status: {status.upper()}")
        lines.append(f"Current Score: {score}/1.0 ({int(score * 100)}%)")
        lines.append("")
        
        lines.append("SUMMARY")
        lines.append("-" * 20)
        lines.append("Your content validation has identified areas that need attention.")
        lines.append("Please review the action plan below to improve your content.")
        lines.append("")
        lines.append(f"Total Estimated Effort: {action_plan.get('estimated_effort_hours', 0)} hours")
        lines.append(f"Priority Tasks: {len(action_plan.get('priority_tasks', []))}")
        lines.append(f"Optional Tasks: {len(action_plan.get('optional_tasks', []))}")
        lines.append("")
        
        priority_tasks = action_plan.get('priority_tasks', [])
        if priority_tasks:
            lines.append("PRIORITY TASKS (REQUIRED)")
            lines.append("-" * 30)
            lines.append("These tasks must be completed to achieve a passing validation score:")
            lines.append("")
            
            for i, task in enumerate(priority_tasks, 1):
                lines.append(f"{i}. {task.get('title', 'Unknown Task')}")
                lines.append(f"   Description: {task.get('description', '')}")
                lines.append(f"   Estimated effort: {task.get('estimated_effort_hours', 0)} hours")
                if task.get('category'):
                    lines.append(f"   Category: {task['category'].title()}")
                lines.append("")
        
        optional_tasks = action_plan.get('optional_tasks', [])
        if optional_tasks:
            lines.append("OPTIONAL IMPROVEMENTS")
            lines.append("-" * 25)
            lines.append("These tasks can further improve your content quality:")
            lines.append("")
            
            for i, task in enumerate(optional_tasks, 1):
                lines.append(f"{i}. {task.get('title', 'Unknown Task')}")
                lines.append(f"   Description: {task.get('description', '')}")
                lines.append(f"   Estimated effort: {task.get('estimated_effort_hours', 0)} hours")
                if task.get('category'):
                    lines.append(f"   Category: {task['category'].title()}")
                lines.append("")
        
        lines.append("NEXT STEPS")
        lines.append("-" * 15)
        lines.append("1. Review and complete the priority tasks listed above")
        lines.append("2. Update your content accordingly")
        lines.append("3. Request a new validation when ready")
        lines.append("")
        lines.append("This action plan was generated automatically based on your validation results.")
        lines.append(f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)
    
    def test_connection(self) -> bool:
        """
        Test email service connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.use_tls:
                context = ssl.create_default_context()
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls(context=context)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.username and self.password:
                server.login(self.username, self.password)
            
            server.quit()
            logger.info("Email service connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Email service connection test failed: {e}")
            return False

