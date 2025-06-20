"""
Multi-Channel Communication System: SMS + Ringless Voicemail
Combines ClickSend SMS with RVM providers for maximum reach
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from multi_provider_sms import MultiProviderSMSManager
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class RVMProvider:
    def __init__(self, name, cost_per_drop, daily_limit=999999):
        self.name = name
        self.cost_per_drop = cost_per_drop
        self.daily_limit = daily_limit
        self.current_count = 0

class MultiChannelCommunicationManager:
    def __init__(self):
        self.sms_manager = MultiProviderSMSManager()
        self.rvm_providers = self._initialize_rvm_providers()
        
    def _initialize_rvm_providers(self):
        """Initialize RVM providers"""
        providers = []
        
        # Slybroadcast
        if os.getenv('SLYBROADCAST_EMAIL'):
            providers.append(RVMProvider("slybroadcast", 0.09))
        
        # CallFire
        if os.getenv('CALLFIRE_APP_LOGIN'):
            providers.append(RVMProvider("callfire", 0.12))
        
        # DropCowboy
        if os.getenv('DROPCOWBOY_API_KEY'):
            providers.append(RVMProvider("dropcowboy", 0.08))
        
        return providers
    
    def send_rvm_slybroadcast(self, phone, audio_url, message_text=""):
        """Send RVM via Slybroadcast"""
        email = os.getenv('SLYBROADCAST_EMAIL')
        password = os.getenv('SLYBROADCAST_PASSWORD')
        
        if not email or not password:
            return False, "Slybroadcast credentials not configured"
        
        # Slybroadcast API endpoint
        url = "https://www.slybroadcast.com/sbapi/send_campaign.php"
        
        data = {
            'email': email,
            'password': password,
            'mobile_list': phone,
            'audio_url': audio_url,
            'title': 'RVM Campaign'
        }
        
        try:
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.text
                if 'success' in result.lower():
                    return True, f"RVM sent successfully: {result}"
                else:
                    return False, f"RVM failed: {result}"
            else:
                return False, f"HTTP error: {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def send_rvm_callfire(self, phone, message_text):
        """Send RVM via CallFire"""
        app_login = os.getenv('CALLFIRE_APP_LOGIN')
        app_password = os.getenv('CALLFIRE_APP_PASSWORD')
        
        if not app_login or not app_password:
            return False, "CallFire credentials not configured"
        
        url = "https://api.callfire.com/v2/calls"
        
        payload = {
            "recipients": [{"phoneNumber": phone}],
            "answeringMachineConfig": "AM_AND_LIVE",
            "sounds": {
                "liveSoundText": message_text,
                "machineSoundText": message_text
            }
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                auth=(app_login, app_password),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return True, f"CallFire RVM sent: {result.get('id')}"
            else:
                return False, f"CallFire error: {response.text}"
        except Exception as e:
            return False, str(e)
    
    def send_combined_campaign(self, contacts, sms_message, rvm_message, strategy="sms_first"):
        """
        Send combined SMS + RVM campaign
        Strategies:
        - sms_first: Send SMS first, then RVM as follow-up
        - rvm_first: Send RVM first, then SMS as follow-up  
        - both_simultaneously: Send both at the same time
        - sms_only: SMS only
        - rvm_only: RVM only
        """
        
        results = []
        
        for contact in contacts:
            phone = contact.get('phone')
            name = contact.get('name', 'Friend')
            
            # Personalize messages
            personalized_sms = sms_message.replace('{name}', name)
            personalized_rvm = rvm_message.replace('{name}', name)
            
            contact_result = {
                'phone': phone,
                'name': name,
                'sms_sent': False,
                'rvm_sent': False,
                'sms_result': '',
                'rvm_result': '',
                'total_cost': 0
            }
            
            if strategy in ['sms_first', 'both_simultaneously', 'sms_only']:
                # Send SMS
                sms_success, sms_result = self.sms_manager.send_sms(phone, personalized_sms)
                contact_result['sms_sent'] = sms_success
                contact_result['sms_result'] = sms_result
                
                if sms_success:
                    contact_result['total_cost'] += 0.0174  # Assume ClickSend rate
            
            if strategy in ['rvm_first', 'both_simultaneously', 'rvm_only']:
                # Send RVM (using first available provider)
                if self.rvm_providers:
                    provider = self.rvm_providers[0]  # Use first available
                    
                    if provider.name == "slybroadcast":
                        # For Slybroadcast, we'd need to upload audio first
                        # This is a simplified example
                        rvm_success, rvm_result = self.send_rvm_slybroadcast(
                            phone, 
                            "https://your-audio-url.com/message.mp3",
                            personalized_rvm
                        )
                    elif provider.name == "callfire":
                        rvm_success, rvm_result = self.send_rvm_callfire(phone, personalized_rvm)
                    else:
                        rvm_success, rvm_result = False, "Provider not implemented"
                    
                    contact_result['rvm_sent'] = rvm_success
                    contact_result['rvm_result'] = rvm_result
                    
                    if rvm_success:
                        contact_result['total_cost'] += provider.cost_per_drop
            
            results.append(contact_result)
            
            # Add delay between contacts to avoid rate limiting
            import time
            time.sleep(1)
        
        return results
    
    def get_campaign_summary(self, results):
        """Generate campaign summary"""
        total_contacts = len(results)
        sms_sent = sum(1 for r in results if r['sms_sent'])
        rvm_sent = sum(1 for r in results if r['rvm_sent'])
        total_cost = sum(r['total_cost'] for r in results)
        
        return {
            'total_contacts': total_contacts,
            'sms_sent': sms_sent,
            'rvm_sent': rvm_sent,
            'sms_success_rate': f"{(sms_sent/total_contacts)*100:.1f}%" if total_contacts > 0 else "0%",
            'rvm_success_rate': f"{(rvm_sent/total_contacts)*100:.1f}%" if total_contacts > 0 else "0%",
            'total_cost': total_cost,
            'cost_per_contact': total_cost / total_contacts if total_contacts > 0 else 0
        }

# Example usage
def demo_multi_channel_campaign():
    """Demo of multi-channel SMS + RVM campaign"""
    
    manager = MultiChannelCommunicationManager()
    
    # Sample contacts
    contacts = [
        {"phone": "+1234567890", "name": "John Doe"},
        {"phone": "+1987654321", "name": "Jane Smith"},
        {"phone": "+1555123456", "name": "Bob Johnson"}
    ]
    
    # Messages
    sms_message = "Hi {name}, don't miss our special offer! Details: [link]. Reply STOP to opt out."
    rvm_message = "Hi {name}, this is a quick message about our special promotion. Check your texts for details!"
    
    print("🚀 Multi-Channel Campaign: SMS + RVM")
    print("=" * 50)
    
    # Run campaign
    results = manager.send_combined_campaign(
        contacts, 
        sms_message, 
        rvm_message, 
        strategy="both_simultaneously"
    )
    
    # Show results
    for result in results:
        print(f"\n📱 {result['phone']} ({result['name']}):")
        print(f"  SMS: {'✅' if result['sms_sent'] else '❌'} {result['sms_result']}")
        print(f"  RVM: {'✅' if result['rvm_sent'] else '❌'} {result['rvm_result']}")
        print(f"  Cost: ${result['total_cost']:.4f}")
    
    # Summary
    summary = manager.get_campaign_summary(results)
    print(f"\n📊 Campaign Summary:")
    print(f"  Total Contacts: {summary['total_contacts']}")
    print(f"  SMS Success Rate: {summary['sms_success_rate']}")
    print(f"  RVM Success Rate: {summary['rvm_success_rate']}")
    print(f"  Total Cost: ${summary['total_cost']:.2f}")
    print(f"  Cost per Contact: ${summary['cost_per_contact']:.4f}")

if __name__ == "__main__":
    demo_multi_channel_campaign()
