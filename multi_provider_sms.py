"""
Multi-Provider SMS System for Higher Daily Limits
Rotates between multiple SMS providers to increase capacity without A2P registration
"""

import os
import json
from datetime import datetime, date
from dotenv import load_dotenv
from twilio.rest import Client
import requests
import time
from dataclasses import dataclass
from typing import List, Optional
import logging

load_dotenv()

@dataclass
class SMSProvider:
    name: str
    daily_limit: int
    cost_per_message: float
    current_count: int = 0
    last_reset: str = ""
    enabled: bool = True

class MultiProviderSMSManager:
    def __init__(self):
        self.providers = self._initialize_providers()
        self.usage_file = "sms_usage.json"
        self.load_usage_data()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _initialize_providers(self):
        """Initialize all SMS providers"""
        providers = []
        
        # Twilio
        if os.getenv('TWILIO_ACCOUNT_SID'):
            providers.append(SMSProvider("twilio", 200, 0.0075, enabled=True))
        
        # TextBelt
        providers.append(SMSProvider("textbelt_free", 1, 0.0, enabled=True))
          # ClickSend (updated 2025 pricing)
        if os.getenv('CLICKSEND_USERNAME'):
            providers.append(SMSProvider("clicksend", 999999, 0.0243, enabled=True))  # Starts at $0.0243, no daily limit
        
        # Add more providers as needed
        providers.append(SMSProvider("textbelt_paid", 1000, 0.0063, enabled=False))
        
        # Vonage (if configured)
        if os.getenv('VONAGE_API_KEY'):
            providers.append(SMSProvider("vonage", 1000, 0.008, enabled=False))
        
        return providers
    
    def load_usage_data(self):
        """Load usage data from file"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                
                today = str(date.today())
                
                for provider in self.providers:
                    if provider.name in data:
                        provider_data = data[provider.name]
                        if provider_data.get('date') == today:
                            provider.current_count = provider_data.get('count', 0)
                        else:
                            provider.current_count = 0
                        provider.last_reset = provider_data.get('date', today)
            except Exception as e:
                self.logger.error(f"Error loading usage data: {e}")
    
    def save_usage_data(self):
        """Save usage data to file"""
        data = {}
        today = str(date.today())
        
        for provider in self.providers:
            data[provider.name] = {
                'count': provider.current_count,
                'date': today,
                'limit': provider.daily_limit
            }
        
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving usage data: {e}")
    
    def get_available_capacity(self):
        """Get total available capacity across all providers"""
        total_capacity = 0
        available_providers = []
        
        for provider in self.providers:
            if provider.enabled and provider.current_count < provider.daily_limit:
                remaining = provider.daily_limit - provider.current_count
                total_capacity += remaining
                available_providers.append({
                    'name': provider.name,
                    'remaining': remaining,
                    'cost': provider.cost_per_message
                })
        
        return total_capacity, available_providers
    
    def get_best_provider(self):
        """Get the best available provider (cheapest with capacity)"""
        available = [p for p in self.providers 
                    if p.enabled and p.current_count < p.daily_limit]
        
        if not available:
            return None
        
        # Sort by cost (cheapest first)
        available.sort(key=lambda x: x.cost_per_message)
        return available[0]
    
    def send_via_twilio(self, phone, message):
        """Send SMS via Twilio"""
        try:
            client = Client(
                os.getenv('TWILIO_ACCOUNT_SID'),
                os.getenv('TWILIO_AUTH_TOKEN')
            )
            
            message_instance = client.messages.create(
                body=message,
                from_=os.getenv('TWILIO_PHONE_NUMBER'),
                to=phone
            )
            
            return True, f"Twilio SID: {message_instance.sid}"
        except Exception as e:
            return False, str(e)
    
    def send_via_textbelt(self, phone, message, use_paid=False):
        """Send SMS via TextBelt"""
        url = 'https://textbelt.com/text'
        
        api_key = 'textbelt' if not use_paid else os.getenv('TEXTBELT_API_KEY')
        
        data = {
            'phone': phone,
            'message': message,
            'key': api_key
        }
        
        try:
            response = requests.post(url, data=data)
            result = response.json()
            
            if result.get('success'):
                return True, f"TextBelt ID: {result.get('textId')}"
            else:
                return False, result.get('error', 'Unknown error')
        except Exception as e:
            return False, str(e)
    
    def send_via_clicksend(self, phone, message):
        """Send SMS via ClickSend"""
        username = os.getenv('CLICKSEND_USERNAME')
        api_key = os.getenv('CLICKSEND_API_KEY')
        
        if not username or not api_key:
            return False, "ClickSend credentials not configured"
        
        url = 'https://rest.clicksend.com/v3/sms/send'
        
        payload = {
            "messages": [
                {
                    "to": phone,
                    "body": message,
                    "from": os.getenv('SENDER_ID', 'SMS')
                }
            ]
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                auth=(username, api_key),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return True, "ClickSend: Message sent successfully"
            else:
                return False, f"ClickSend error: {response.text}"
        except Exception as e:
            return False, str(e)
    
    def send_sms(self, phone, message, preferred_provider=None):
        """Send SMS using the best available provider"""
        
        # Use preferred provider if specified and available
        if preferred_provider:
            provider = next((p for p in self.providers 
                           if p.name == preferred_provider and p.enabled 
                           and p.current_count < p.daily_limit), None)
        else:
            provider = self.get_best_provider()
        
        if not provider:
            return False, "No providers available (daily limits reached)"
        
        self.logger.info(f"Sending SMS via {provider.name} to {phone}")
        
        # Send via the selected provider
        success = False
        result = ""
        
        if provider.name == "twilio":
            success, result = self.send_via_twilio(phone, message)
        elif provider.name == "textbelt_free":
            success, result = self.send_via_textbelt(phone, message, use_paid=False)
        elif provider.name == "textbelt_paid":
            success, result = self.send_via_textbelt(phone, message, use_paid=True)
        elif provider.name == "clicksend":
            success, result = self.send_via_clicksend(phone, message)
          # Update usage count if successful
        if success:
            provider.current_count += 1
            self.save_usage_data()
            
            cost = provider.cost_per_message
            remaining = provider.daily_limit - provider.current_count
            
            self.logger.info(f"✅ SMS sent! Provider: {provider.name}, "
                           f"Cost: ${cost:.4f}, Remaining today: {remaining}")
        else:
            self.logger.error(f"❌ SMS failed via {provider.name}: {result}")
            cost = 0
        
        return success, f"{provider.name}: {result}", cost, provider.name
    
    def get_usage_report(self):
        """Get detailed usage report"""
        report = {
            'date': str(date.today()),
            'providers': [],
            'total_sent': 0,
            'total_cost': 0,
            'remaining_capacity': 0
        }
        
        for provider in self.providers:
            if not provider.enabled:
                continue
                
            sent = provider.current_count
            remaining = provider.daily_limit - sent
            cost = sent * provider.cost_per_message
            
            report['providers'].append({
                'name': provider.name,
                'sent': sent,
                'limit': provider.daily_limit,
                'remaining': remaining,
                'cost_per_message': provider.cost_per_message,
                'total_cost': cost,
                'utilization': f"{(sent/provider.daily_limit)*100:.1f}%"
            })
            
            report['total_sent'] += sent
            report['total_cost'] += cost
            report['remaining_capacity'] += remaining
        
        return report

def main():
    """Demo usage of multi-provider SMS manager"""
    manager = MultiProviderSMSManager()
    
    print("📊 Multi-Provider SMS Manager")
    print("=" * 50)
    
    # Show current usage
    report = manager.get_usage_report()
    print(f"📅 Date: {report['date']}")
    print(f"📱 Total sent today: {report['total_sent']}")
    print(f"💰 Total cost today: ${report['total_cost']:.4f}")
    print(f"📈 Remaining capacity: {report['remaining_capacity']}")
    print()
    
    print("Provider Status:")
    for provider_info in report['providers']:
        name = provider_info['name']
        sent = provider_info['sent']
        limit = provider_info['limit']
        remaining = provider_info['remaining']
        util = provider_info['utilization']
        
        print(f"  {name:<15} {sent:>4}/{limit:<4} ({remaining:>4} left) {util}")
    
    print()
    
    # Example send
    phone = "+1234567890"  # Replace with real number for testing
    message = "Test message from multi-provider SMS system!"
    
    print(f"📱 Sending test SMS to {phone}...")
    success, result = manager.send_sms(phone, message)
    
    if success:
        print(f"✅ {result}")
    else:
        print(f"❌ {result}")
    
    # Show updated usage
    print("\n📊 Updated Usage:")
    report = manager.get_usage_report()
    print(f"Total sent: {report['total_sent']}")
    print(f"Remaining capacity: {report['remaining_capacity']}")

if __name__ == "__main__":
    main()
