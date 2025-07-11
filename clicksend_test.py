#!/usr/bin/env python3
"""
ClickSend Test Script - No A2P Required
=======================================

This script demonstrates how to use ClickSend without A2P registration.
ClickSend is perfect for getting started quickly without the complexity 
of A2P registration processes.

Setup Instructions:
1. Sign up at https://www.clicksend.com/
2. Get your API credentials from Account Settings
3. Set environment variables:
   - CLICKSEND_USERNAME=your_username
   - CLICKSEND_API_KEY=your_api_key
4. Add credit to your account
5. Start sending!

Benefits:
- ✅ No A2P registration required
- ✅ No daily limits (unlike Twilio's 200/day)
- ✅ Instant setup (no weeks of waiting)
- ✅ Global reach (190+ countries)
- ✅ 99.95% uptime
"""

import os
import requests
import json

class ClickSendTester:
    def __init__(self):
        self.username = os.getenv('CLICKSEND_USERNAME')
        self.api_key = os.getenv('CLICKSEND_API_KEY')
        self.base_url = 'https://rest.clicksend.com/v3'
        
    def check_credentials(self):
        """Check if ClickSend credentials are configured"""
        if not self.username or not self.api_key:
            print("❌ ClickSend credentials not found!")
            print("\nTo set up ClickSend:")
            print("1. Sign up at: https://www.clicksend.com/")
            print("2. Get your API credentials from Account Settings")
            print("3. Set environment variables:")
            print("   set CLICKSEND_USERNAME=your_username")
            print("   set CLICKSEND_API_KEY=your_api_key")
            return False
        
        print("✅ ClickSend credentials found!")
        print(f"Username: {self.username}")
        print(f"API Key: {self.api_key[:8]}..." if len(self.api_key) > 8 else "API Key: [short]")
        return True
    
    def get_account_info(self):
        """Get account information and balance"""
        try:
            response = requests.get(
                f'{self.base_url}/account',
                auth=(self.username, self.api_key)
            )
            
            if response.status_code == 200:
                data = response.json()
                account = data.get('data', {})
                print(f"\n✅ Account Info:")
                print(f"   Company: {account.get('company_name', 'N/A')}")
                print(f"   Country: {account.get('country', 'N/A')}")
                print(f"   Currency: {account.get('currency', 'N/A')}")
                return True
            else:
                print(f"❌ Failed to get account info: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting account info: {str(e)}")
            return False
    
    def get_balance(self):
        """Check account balance"""
        try:
            response = requests.get(
                f'{self.base_url}/account/balance',
                auth=(self.username, self.api_key)
            )
            
            if response.status_code == 200:
                data = response.json()
                balance = data.get('data', {})
                credit = balance.get('balance', 0)
                currency = balance.get('currency', 'USD')
                
                print(f"\n💰 Account Balance: {credit} {currency}")
                
                if credit <= 0:
                    print("⚠️  Warning: Low balance! Add credit to your account.")
                    print("   Go to: https://www.clicksend.com/billing")
                else:
                    print("✅ Sufficient balance for testing")
                
                return True
            else:
                print(f"❌ Failed to get balance: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting balance: {str(e)}")
            return False
    
    def send_test_message(self, phone_number, message="Hello from ClickSend! This is a test message. No A2P registration required! 🚀"):
        """Send a test SMS message"""
        if not phone_number:
            print("❌ No phone number provided for test")
            return False
            
        payload = {
            "messages": [
                {
                    "to": phone_number,
                    "body": message,
                    "from": "ClickSend"
                }
            ]
        }
        
        try:
            print(f"\n📱 Sending test message to {phone_number}...")
            print(f"Message: {message}")
            
            response = requests.post(
                f'{self.base_url}/sms/send',
                json=payload,
                auth=(self.username, self.api_key),
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if response.status_code == 200:
                message_data = result.get('data', {}).get('messages', [])
                if message_data:
                    msg = message_data[0]
                    print(f"✅ Message sent successfully!")
                    print(f"   Message ID: {msg.get('message_id')}")
                    print(f"   Status: {msg.get('status')}")
                    print(f"   Cost: {msg.get('message_price')} {msg.get('currency')}")
                return True
            else:
                print(f"❌ Failed to send message: {response.status_code}")
                print(f"Response: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending message: {str(e)}")
            return False

def main():
    print("🚀 ClickSend Test - No A2P Required!")
    print("=" * 50)
    
    tester = ClickSendTester()
    
    # Check credentials
    if not tester.check_credentials():
        return
    
    # Get account info
    print("\n📊 Checking Account Status...")
    tester.get_account_info()
    tester.get_balance()
    
    # Ask for test phone number
    print("\n" + "=" * 50)
    print("📱 SMS Test (Optional)")
    print("=" * 50)
    
    phone = input("Enter a phone number to test (with country code, e.g., +1234567890): ").strip()
    
    if phone:
        custom_message = input("Enter custom message (or press Enter for default): ").strip()
        if custom_message:
            tester.send_test_message(phone, custom_message)
        else:
            tester.send_test_message(phone)
    else:
        print("⏭️  Skipping SMS test")
    
    print("\n✅ ClickSend setup complete!")
    print("\n💡 Tips for using ClickSend:")
    print("   • No A2P registration needed - start sending immediately")
    print("   • No daily limits (unlike Twilio's 200/day limit)")
    print("   • Global reach in 190+ countries")
    print("   • Monitor usage at: https://www.clicksend.com/dashboard")
    print("   • Set up webhooks for delivery reports")

if __name__ == "__main__":
    main()
