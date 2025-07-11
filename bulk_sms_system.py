"""
Comprehensive Bulk SMS System
Supports CSV import, API integration, and multiple providers
"""

import pandas as pd
import requests
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bulk_sms.log'),
        logging.StreamHandler()
    ]
)

class SMSProvider(Enum):
    CLICKSEND = "clicksend"
    TWILIO = "twilio"
    PLIVO = "plivo"
    TEXTMAGIC = "textmagic"
    BULKSMS = "bulksms"
    MESSAGEBIRD = "messagebird"

@dataclass
class SMSMessage:
    to: str
    message: str
    from_: str = "SMS"
    name: str = ""
    custom_fields: Dict = None

@dataclass
class SMSResult:
    success: bool
    message_id: str = ""
    error: str = ""
    cost: float = 0.0
    provider: str = ""

class BulkSMSSystem:
    def __init__(self):
        self.providers = {
            SMSProvider.CLICKSEND: ClickSendProvider(),
            SMSProvider.TWILIO: TwilioProvider(),
            SMSProvider.PLIVO: PlivoProvider(),
            SMSProvider.TEXTMAGIC: TextMagicProvider(),
            SMSProvider.BULKSMS: BulkSMSProvider(),
            SMSProvider.MESSAGEBIRD: MessageBirdProvider(),
        }
        self.results = []
        
    def load_contacts_from_csv(self, csv_file: str) -> List[Dict]:
        """Load contacts from CSV file with validation"""
        try:
            df = pd.read_csv(csv_file)
            
            # Validate required columns
            required_columns = ['phone_number']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Clean and validate phone numbers
            df['phone_number'] = df['phone_number'].astype(str).str.strip()
            df = df[df['phone_number'].str.len() > 0]  # Remove empty phone numbers
            
            # Add optional columns if they don't exist
            optional_columns = ['name', 'email', 'message', 'first_name', 'last_name']
            for col in optional_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Convert to list of dictionaries
            contacts = df.to_dict('records')
            
            logging.info(f"Loaded {len(contacts)} contacts from {csv_file}")
            return contacts
            
        except Exception as e:
            logging.error(f"Error loading CSV: {str(e)}")
            raise
    
    def prepare_messages(self, contacts: List[Dict], template: str, from_number: str = "SMS") -> List[SMSMessage]:
        """Prepare SMS messages from contacts and template"""
        messages = []
        
        for contact in contacts:
            # Handle phone number
            phone = str(contact.get('phone_number', '')).strip()
            if not phone:
                continue
                
            # Handle name (try different variations)
            name = (
                contact.get('name', '') or 
                f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip() or 
                'Friend'
            )
            
            # Handle custom message
            message = contact.get('message', '').strip() or template
            
            # Replace placeholders
            message = self._replace_placeholders(message, contact)
            
            messages.append(SMSMessage(
                to=phone,
                message=message,
                from_=from_number,
                name=name,
                custom_fields=contact
            ))
        
        logging.info(f"Prepared {len(messages)} SMS messages")
        return messages
    
    def _replace_placeholders(self, message: str, contact: Dict) -> str:
        """Replace placeholders in message template"""
        replacements = {
            '{name}': contact.get('name', 'Friend'),
            '{first_name}': contact.get('first_name', ''),
            '{lastName}': contact.get('last_name', ''),
            '{email}': contact.get('email', ''),
            '{phone}': contact.get('phone_number', ''),
            '{company}': contact.get('company', ''),
        }
        
        for placeholder, value in replacements.items():
            message = message.replace(placeholder, str(value))
        
        return message
    
    async def send_bulk_async(self, messages: List[SMSMessage], provider: SMSProvider, 
                            delay: float = 1.0, batch_size: int = 50) -> List[SMSResult]:
        """Send bulk SMS asynchronously with rate limiting"""
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not supported")
        
        provider_instance = self.providers[provider]
        results = []
        
        # Process in batches
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            batch_results = await self._send_batch_async(batch, provider_instance, delay)
            results.extend(batch_results)
            
            # Log progress
            logging.info(f"Processed batch {i//batch_size + 1}/{(len(messages)-1)//batch_size + 1}")
        
        self.results = results
        return results
    
    async def _send_batch_async(self, batch: List[SMSMessage], provider, delay: float) -> List[SMSResult]:
        """Send a batch of messages asynchronously"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for message in batch:
                task = asyncio.create_task(self._send_single_async(message, provider, session))
                tasks.append(task)
                
                # Add delay between requests
                if delay > 0:
                    await asyncio.sleep(delay)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append(SMSResult(
                        success=False,
                        error=str(result),
                        provider=provider.__class__.__name__
                    ))
                else:
                    processed_results.append(result)
            
            return processed_results
    
    async def _send_single_async(self, message: SMSMessage, provider, session) -> SMSResult:
        """Send a single SMS message asynchronously"""
        try:
            return await provider.send_async(message, session)
        except Exception as e:
            return SMSResult(
                success=False,
                error=str(e),
                provider=provider.__class__.__name__
            )
    
    def send_bulk_sync(self, messages: List[SMSMessage], provider: SMSProvider, 
                      delay: float = 1.0) -> List[SMSResult]:
        """Send bulk SMS synchronously (fallback method)"""
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not supported")
        
        provider_instance = self.providers[provider]
        results = []
        
        for i, message in enumerate(messages):
            try:
                result = provider_instance.send_sync(message)
                results.append(result)
                
                logging.info(f"Sent {i+1}/{len(messages)} - Success: {result.success}")
                
                # Rate limiting
                if delay > 0 and i < len(messages) - 1:
                    time.sleep(delay)
                    
            except Exception as e:
                result = SMSResult(
                    success=False,
                    error=str(e),
                    provider=provider_instance.__class__.__name__
                )
                results.append(result)
                logging.error(f"Failed to send message {i+1}: {str(e)}")
        
        self.results = results
        return results
    
    def get_summary(self) -> Dict:
        """Get summary of sending results"""
        if not self.results:
            return {"total": 0, "successful": 0, "failed": 0, "success_rate": 0.0}
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(success_rate, 2),
            "total_cost": sum(r.cost for r in self.results),
            "errors": [r.error for r in self.results if not r.success and r.error]
        }
    
    def export_results(self, filename: str = None) -> str:
        """Export results to CSV"""
        if not self.results:
            raise ValueError("No results to export")
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sms_results_{timestamp}.csv"
        
        # Convert results to DataFrame
        data = []
        for i, result in enumerate(self.results):
            data.append({
                'index': i + 1,
                'success': result.success,
                'message_id': result.message_id,
                'error': result.error,
                'cost': result.cost,
                'provider': result.provider
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        
        logging.info(f"Results exported to {filename}")
        return filename

# Provider implementations
class BaseProvider:
    def __init__(self):
        self.name = self.__class__.__name__
    
    def send_sync(self, message: SMSMessage) -> SMSResult:
        raise NotImplementedError
    
    async def send_async(self, message: SMSMessage, session) -> SMSResult:
        raise NotImplementedError

class ClickSendProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self.username = os.getenv('CLICKSEND_USERNAME')
        self.api_key = os.getenv('CLICKSEND_API_KEY')
        self.base_url = 'https://rest.clicksend.com/v3'
    
    def send_sync(self, message: SMSMessage) -> SMSResult:
        if not self.username or not self.api_key:
            return SMSResult(success=False, error="ClickSend credentials not configured")
        
        url = f"{self.base_url}/sms/send"
        payload = {
            "messages": [{
                "to": message.to,
                "body": message.message,
                "from": message.from_
            }]
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                auth=(self.username, self.api_key),
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if response.status_code == 200:
                message_data = result['data']['messages'][0]
                return SMSResult(
                    success=True,
                    message_id=message_data.get('message_id', ''),
                    cost=float(message_data.get('message_price', 0)),
                    provider=self.name
                )
            else:
                return SMSResult(
                    success=False,
                    error=result.get('response_msg', 'Unknown error'),
                    provider=self.name
                )
        except Exception as e:
            return SMSResult(success=False, error=str(e), provider=self.name)
    
    async def send_async(self, message: SMSMessage, session) -> SMSResult:
        if not self.username or not self.api_key:
            return SMSResult(success=False, error="ClickSend credentials not configured")
        
        url = f"{self.base_url}/sms/send"
        payload = {
            "messages": [{
                "to": message.to,
                "body": message.message,
                "from": message.from_
            }]
        }
        
        auth = aiohttp.BasicAuth(self.username, self.api_key)
        
        try:
            async with session.post(url, json=payload, auth=auth) as response:
                result = await response.json()
                
                if response.status == 200:
                    message_data = result['data']['messages'][0]
                    return SMSResult(
                        success=True,
                        message_id=message_data.get('message_id', ''),
                        cost=float(message_data.get('message_price', 0)),
                        provider=self.name
                    )
                else:
                    return SMSResult(
                        success=False,
                        error=result.get('response_msg', 'Unknown error'),
                        provider=self.name
                    )
        except Exception as e:
            return SMSResult(success=False, error=str(e), provider=self.name)

class TwilioProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    def send_sync(self, message: SMSMessage) -> SMSResult:
        # Placeholder - implement Twilio API calls
        return SMSResult(success=False, error="Twilio implementation pending", provider=self.name)
    
    async def send_async(self, message: SMSMessage, session) -> SMSResult:
        return SMSResult(success=False, error="Twilio async implementation pending", provider=self.name)

class PlivoProvider(BaseProvider):
    def send_sync(self, message: SMSMessage) -> SMSResult:
        return SMSResult(success=False, error="Plivo implementation pending", provider=self.name)
    
    async def send_async(self, message: SMSMessage, session) -> SMSResult:
        return SMSResult(success=False, error="Plivo async implementation pending", provider=self.name)

class TextMagicProvider(BaseProvider):
    def send_sync(self, message: SMSMessage) -> SMSResult:
        return SMSResult(success=False, error="TextMagic implementation pending", provider=self.name)
    
    async def send_async(self, message: SMSMessage, session) -> SMSResult:
        return SMSResult(success=False, error="TextMagic async implementation pending", provider=self.name)

class BulkSMSProvider(BaseProvider):
    def send_sync(self, message: SMSMessage) -> SMSResult:
        return SMSResult(success=False, error="BulkSMS implementation pending", provider=self.name)
    
    async def send_async(self, message: SMSMessage, session) -> SMSResult:
        return SMSResult(success=False, error="BulkSMS async implementation pending", provider=self.name)

class MessageBirdProvider(BaseProvider):
    def send_sync(self, message: SMSMessage) -> SMSResult:
        return SMSResult(success=False, error="MessageBird implementation pending", provider=self.name)
    
    async def send_async(self, message: SMSMessage, session) -> SMSResult:
        return SMSResult(success=False, error="MessageBird async implementation pending", provider=self.name)

# Main execution functions
async def main_async():
    """Example usage - async version"""
    system = BulkSMSSystem()
    
    # Load contacts from CSV
    contacts = system.load_contacts_from_csv('contacts.csv')
    
    # Prepare messages
    template = "Hi {name}, this is a test message from our system!"
    messages = system.prepare_messages(contacts, template, "YourBusiness")
    
    # Send messages
    results = await system.send_bulk_async(
        messages, 
        SMSProvider.CLICKSEND, 
        delay=1.0,  # 1 second between messages
        batch_size=50
    )
    
    # Get summary
    summary = system.get_summary()
    print(f"Campaign Summary: {summary}")
    
    # Export results
    filename = system.export_results()
    print(f"Results exported to: {filename}")

def main_sync():
    """Example usage - sync version"""
    system = BulkSMSSystem()
    
    # Load contacts from CSV
    contacts = system.load_contacts_from_csv('contacts.csv')
    
    # Prepare messages
    template = "Hi {name}, this is a test message from our system!"
    messages = system.prepare_messages(contacts, template, "YourBusiness")
    
    # Send messages
    results = system.send_bulk_sync(
        messages, 
        SMSProvider.CLICKSEND, 
        delay=1.0  # 1 second between messages
    )
    
    # Get summary
    summary = system.get_summary()
    print(f"Campaign Summary: {summary}")
    
    # Export results
    filename = system.export_results()
    print(f"Results exported to: {filename}")

if __name__ == "__main__":
    # Choose async or sync execution
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'async':
        asyncio.run(main_async())
    else:
        main_sync()
