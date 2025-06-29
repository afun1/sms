"""
Multi-Provider Email Manager for Sparky Messaging
Supports multiple email providers with automatic failover and cost optimization
"""

import smtplib
import ssl
import requests
import json
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

@dataclass
class EmailProvider:
    """Email provider configuration"""
    name: str
    enabled: bool
    priority: int
    cost_per_email: float
    daily_limit: int
    sent_today: int
    last_reset: str
    config: Dict
    provider_type: str  # 'smtp', 'api'

class MultiProviderEmailManager:
    """Manages multiple email providers with automatic failover"""
    
    def __init__(self):
        self.providers = []
        self.usage_stats = {
            'total_sent': 0,
            'total_failed': 0,
            'cost_saved': 0,
            'last_reset': datetime.now().strftime('%Y-%m-%d')
        }
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured email providers"""
        
        # Gmail SMTP Provider
        if os.getenv('GMAIL_EMAIL') and os.getenv('GMAIL_APP_PASSWORD'):
            self.providers.append(EmailProvider(
                name="Gmail",
                enabled=True,
                priority=1,
                cost_per_email=0.0,  # Free tier
                daily_limit=500,  # Gmail's daily limit
                sent_today=0,
                last_reset=datetime.now().strftime('%Y-%m-%d'),
                config={
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'email': os.getenv('GMAIL_EMAIL'),
                    'password': os.getenv('GMAIL_APP_PASSWORD'),
                    'use_tls': True
                },
                provider_type='smtp'
            ))
        
        # SendGrid API Provider
        if os.getenv('SENDGRID_API_KEY'):
            self.providers.append(EmailProvider(
                name="SendGrid",
                enabled=True,
                priority=2,
                cost_per_email=0.0000295,  # $0.295 per 10k emails
                daily_limit=100000,
                sent_today=0,
                last_reset=datetime.now().strftime('%Y-%m-%d'),
                config={
                    'api_key': os.getenv('SENDGRID_API_KEY'),
                    'api_url': 'https://api.sendgrid.com/v3/mail/send'
                },
                provider_type='api'
            ))
        
        # Mailgun API Provider
        if os.getenv('MAILGUN_API_KEY') and os.getenv('MAILGUN_DOMAIN'):
            self.providers.append(EmailProvider(
                name="Mailgun",
                enabled=True,
                priority=3,
                cost_per_email=0.0008,  # $0.80 per 1k emails
                daily_limit=10000,
                sent_today=0,
                last_reset=datetime.now().strftime('%Y-%m-%d'),
                config={
                    'api_key': os.getenv('MAILGUN_API_KEY'),
                    'domain': os.getenv('MAILGUN_DOMAIN'),
                    'api_url': f"https://api.mailgun.net/v3/{os.getenv('MAILGUN_DOMAIN')}/messages"
                },
                provider_type='api'
            ))
        
        # Amazon SES SMTP Provider
        if os.getenv('AWS_SES_SMTP_USERNAME') and os.getenv('AWS_SES_SMTP_PASSWORD'):
            self.providers.append(EmailProvider(
                name="Amazon SES",
                enabled=True,
                priority=4,
                cost_per_email=0.0001,  # $0.10 per 1k emails
                daily_limit=200,  # Sandbox limit, increases with verification
                sent_today=0,
                last_reset=datetime.now().strftime('%Y-%m-%d'),
                config={
                    'smtp_server': f"email-smtp.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com",
                    'smtp_port': 587,
                    'username': os.getenv('AWS_SES_SMTP_USERNAME'),
                    'password': os.getenv('AWS_SES_SMTP_PASSWORD'),
                    'use_tls': True
                },
                provider_type='smtp'
            ))
        
        # ClickSend Email API Provider
        if os.getenv('CLICKSEND_USERNAME') and os.getenv('CLICKSEND_API_KEY'):
            self.providers.append(EmailProvider(
                name="ClickSend",
                enabled=True,
                priority=5,
                cost_per_email=0.0009,  # $0.90 per 1k emails (competitive international rates)
                daily_limit=50000,  # High daily limit
                sent_today=0,
                last_reset=datetime.now().strftime('%Y-%m-%d'),
                config={
                    'username': os.getenv('CLICKSEND_USERNAME'),
                    'api_key': os.getenv('CLICKSEND_API_KEY'),
                    'api_url': 'https://rest.clicksend.com/v3/email/send'
                },
                provider_type='api'
            ))
        
        # Sort providers by priority
        self.providers.sort(key=lambda x: x.priority)
        
        if self.providers:
            logger.info(f"Initialized {len(self.providers)} email providers")
        else:
            logger.warning("No email providers configured!")
    
    def get_best_provider(self) -> Optional[EmailProvider]:
        """Get the best available provider based on priority and limits"""
        self._reset_daily_counts()
        
        for provider in self.providers:
            if provider.enabled and provider.sent_today < provider.daily_limit:
                return provider
        
        return None
    
    def _reset_daily_counts(self):
        """Reset daily counts if it's a new day"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        for provider in self.providers:
            if provider.last_reset != today:
                provider.sent_today = 0
                provider.last_reset = today
        
        if self.usage_stats['last_reset'] != today:
            self.usage_stats['last_reset'] = today
    
    def send_email(self, to_email: str, subject: str, content: str, 
                   from_name: str = "Sparky Messaging", 
                   content_type: str = "html",
                   attachments: List[Dict] = None) -> Dict:
        """
        Send email using the best available provider
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            content: Email content (HTML or plain text)
            from_name: Sender display name
            content_type: 'html' or 'text'
            attachments: List of attachment dicts with 'filename' and 'content' keys
        
        Returns:
            Dict with success status, provider used, cost, and message
        """
        
        provider = self.get_best_provider()
        if not provider:
            return {
                'success': False,
                'error': 'No email providers available',
                'provider': None,
                'cost': 0
            }
        
        try:
            if provider.provider_type == 'smtp':
                result = self._send_smtp_email(provider, to_email, subject, content, 
                                             from_name, content_type, attachments)
            else:
                result = self._send_api_email(provider, to_email, subject, content, 
                                            from_name, content_type, attachments)
            
            if result['success']:
                provider.sent_today += 1
                self.usage_stats['total_sent'] += 1
                result['cost'] = provider.cost_per_email
                result['provider'] = provider.name
                
                logger.info(f"Email sent successfully via {provider.name} to {to_email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send email via {provider.name}: {str(e)}")
            return {
                'success': False,
                'error': f'{provider.name} error: {str(e)}',
                'provider': provider.name,
                'cost': 0
            }
    
    def _send_smtp_email(self, provider: EmailProvider, to_email: str, subject: str, 
                        content: str, from_name: str, content_type: str, 
                        attachments: List[Dict] = None) -> Dict:
        """Send email via SMTP"""
        
        config = provider.config
        from_email = config['email']
        
        # Create message
        if attachments:
            msg = MIMEMultipart()
        else:
            msg = MIMEText(content, content_type)
            msg['Subject'] = subject
            msg['From'] = formataddr((from_name, from_email))
            msg['To'] = to_email
            
            # Send via SMTP
            context = ssl.create_default_context()
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                if config.get('use_tls'):
                    server.starttls(context=context)
                server.login(config['email'], config['password'])
                server.send_message(msg)
            
            return {'success': True, 'message_id': f"smtp-{int(time.time())}"}
        
        # Handle multipart message with attachments
        msg['Subject'] = subject
        msg['From'] = formataddr((from_name, from_email))
        msg['To'] = to_email
        
        # Add body
        msg.attach(MIMEText(content, content_type))
        
        # Add attachments
        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment['content'])
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment["filename"]}'
                )
                msg.attach(part)
        
        # Send via SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            if config.get('use_tls'):
                server.starttls(context=context)
            server.login(config['email'], config['password'])
            server.send_message(msg)
        
        return {'success': True, 'message_id': f"smtp-{int(time.time())}"}
    
    def _send_api_email(self, provider: EmailProvider, to_email: str, subject: str, 
                       content: str, from_name: str, content_type: str, 
                       attachments: List[Dict] = None) -> Dict:
        """Send email via API (SendGrid, Mailgun, etc.)"""
        
        if provider.name == "SendGrid":
            return self._send_sendgrid_email(provider, to_email, subject, content, 
                                           from_name, content_type, attachments)
        elif provider.name == "Mailgun":
            return self._send_mailgun_email(provider, to_email, subject, content, 
                                          from_name, content_type, attachments)
        elif provider.name == "ClickSend":
            return self._send_clicksend_email(provider, to_email, subject, content, 
                                            from_name, content_type, attachments)
        
        return {'success': False, 'error': f'API provider {provider.name} not implemented'}
    
    def _send_sendgrid_email(self, provider: EmailProvider, to_email: str, subject: str, 
                           content: str, from_name: str, content_type: str, 
                           attachments: List[Dict] = None) -> Dict:
        """Send email via SendGrid API"""
        
        config = provider.config
        from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@sparkymessaging.com')
        
        payload = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": subject
            }],
            "from": {
                "email": from_email,
                "name": from_name
            },
            "content": [{
                "type": f"text/{content_type}",
                "value": content
            }]
        }
        
        # Add attachments if any
        if attachments:
            payload["attachments"] = []
            for attachment in attachments:
                payload["attachments"].append({
                    "content": attachment['content'],
                    "filename": attachment['filename'],
                    "type": "application/octet-stream",
                    "disposition": "attachment"
                })
        
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(config['api_url'], 
                               headers=headers, 
                               data=json.dumps(payload))
        
        if response.status_code == 202:
            return {'success': True, 'message_id': response.headers.get('X-Message-Id')}
        else:
            return {'success': False, 'error': f'SendGrid error: {response.text}'}
    
    def _send_mailgun_email(self, provider: EmailProvider, to_email: str, subject: str, 
                          content: str, from_name: str, content_type: str, 
                          attachments: List[Dict] = None) -> Dict:
        """Send email via Mailgun API"""
        
        config = provider.config
        from_email = f"{from_name} <noreply@{config['domain']}>"
        
        data = {
            'from': from_email,
            'to': to_email,
            'subject': subject,
            f'{content_type}': content
        }
        
        files = []
        if attachments:
            for attachment in attachments:
                files.append(('attachment', (attachment['filename'], attachment['content'])))
        
        response = requests.post(
            config['api_url'],
            auth=('api', config['api_key']),
            data=data,
            files=files if files else None
        )
        
        if response.status_code == 200:
            result = response.json()
            return {'success': True, 'message_id': result.get('id')}
        else:
            return {'success': False, 'error': f'Mailgun error: {response.text}'}
    
    def _send_clicksend_email(self, provider: EmailProvider, to_email: str, subject: str, 
                            content: str, from_name: str, content_type: str, 
                            attachments: List[Dict] = None) -> Dict:
        """Send email via ClickSend API"""
        
        config = provider.config
        from_email = os.getenv('CLICKSEND_FROM_EMAIL', 'noreply@sparkymessaging.com')
        
        # Create authentication header
        auth_string = f"{config['username']}:{config['api_key']}"
        auth_header = base64.b64encode(auth_string.encode()).decode()
        
        # Prepare email data for ClickSend API
        email_data = {
            "from": {
                "email_address": from_email,
                "name": from_name
            },
            "to": [
                {
                    "email_address": to_email,
                    "name": ""
                }
            ],
            "subject": subject,
            "body": content,
            "body_type": "html" if content_type == "html" else "txt"
        }
        
        # Add attachments if any
        if attachments:
            email_data["attachments"] = []
            for attachment in attachments:
                # ClickSend expects base64 encoded attachments
                if isinstance(attachment['content'], str):
                    # If content is already base64 encoded
                    encoded_content = attachment['content']
                else:
                    # If content is bytes, encode it
                    encoded_content = base64.b64encode(attachment['content']).decode()
                
                email_data["attachments"].append({
                    "filename": attachment['filename'],
                    "content": encoded_content,
                    "type": "application/octet-stream"
                })
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                config['api_url'],
                headers=headers,
                data=json.dumps(email_data),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('http_code') == 200 and result.get('response_code') == 'SUCCESS':
                    message_id = result.get('data', {}).get('message_id', f"clicksend-{int(time.time())}")
                    return {'success': True, 'message_id': message_id}
                else:
                    error_msg = result.get('response_msg', 'Unknown ClickSend error')
                    return {'success': False, 'error': f'ClickSend error: {error_msg}'}
            else:
                return {'success': False, 'error': f'ClickSend HTTP error: {response.status_code} - {response.text}'}
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'ClickSend request timeout'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'ClickSend request error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'ClickSend unexpected error: {str(e)}'}
    
    def send_bulk_email(self, recipients: List[str], subject: str, content: str,
                       from_name: str = "Sparky Messaging", 
                       content_type: str = "html") -> Dict:
        """Send bulk emails to multiple recipients"""
        
        results = {
            'total_sent': 0,
            'total_failed': 0,
            'total_cost': 0,
            'provider_usage': {},
            'failed_emails': [],
            'details': []
        }
        
        for email in recipients:
            result = self.send_email(email, subject, content, from_name, content_type)
            
            if result['success']:
                results['total_sent'] += 1
                results['total_cost'] += result.get('cost', 0)
                
                provider = result.get('provider')
                if provider:
                    results['provider_usage'][provider] = results['provider_usage'].get(provider, 0) + 1
            else:
                results['total_failed'] += 1
                results['failed_emails'].append({
                    'email': email,
                    'error': result.get('error')
                })
            
            results['details'].append({
                'email': email,
                'success': result['success'],
                'provider': result.get('provider'),
                'cost': result.get('cost', 0),
                'error': result.get('error') if not result['success'] else None
            })
        
        return results
    
    def get_capacity(self) -> Dict:
        """Get remaining email capacity across all providers"""
        self._reset_daily_counts()
        
        capacity_info = {
            'total_remaining': 0,
            'total_limit': 0,
            'providers': []
        }
        
        for provider in self.providers:
            if provider.enabled:
                remaining = provider.daily_limit - provider.sent_today
                capacity_info['total_remaining'] += remaining
                capacity_info['total_limit'] += provider.daily_limit
                
                capacity_info['providers'].append({
                    'name': provider.name,
                    'remaining': remaining,
                    'limit': provider.daily_limit,
                    'cost_per_email': provider.cost_per_email,
                    'sent_today': provider.sent_today
                })
        
        return capacity_info
    
    def get_usage_stats(self) -> Dict:
        """Get email usage statistics"""
        capacity = self.get_capacity()
        
        return {
            'usage_stats': self.usage_stats,
            'capacity': capacity,
            'providers_configured': len([p for p in self.providers if p.enabled]),
            'cheapest_provider': min(self.providers, key=lambda x: x.cost_per_email).name if self.providers else None
        }
    
    def get_cost_estimate(self, email_count: int) -> Dict:
        """Get cost estimate for sending emails"""
        if not self.providers:
            return {'error': 'No providers configured'}
        
        # Use cheapest available provider for estimate
        cheapest = min([p for p in self.providers if p.enabled], 
                      key=lambda x: x.cost_per_email, default=None)
        
        if not cheapest:
            return {'error': 'No providers available'}
        
        total_cost = email_count * cheapest.cost_per_email
        
        return {
            'email_count': email_count,
            'cost_per_email': cheapest.cost_per_email,
            'total_cost': round(total_cost, 4),
            'provider': cheapest.name,
            'currency': 'USD'
        }

# Create global instance
email_manager = MultiProviderEmailManager()
