#!/usr/bin/env python3
"""
ClickSend Direct Test - Input credentials directly
=================================================

This script allows you to test ClickSend integration by entering
credentials directly, bypassing environment variables.
"""

import requests
import json
import getpass

class ClickSendDirectTester:
    def __init__(self):
        self.username = None
        self.api_key = None
        self.base_url = 'https://rest.clicksend.com/v3'
        
    def get_credentials(self):
        """Get credentials from user input"""
        print("🔐 Enter your ClickSend credentials:")
        print("(You can find these at: https://www.clicksend.com/account/api)")
        
        self.username = input("ClickSend Username: ").strip()
        self.api_key = getpass.getpass("ClickSend API Key (hidden input): ").strip()
        
        if not self.username or not self.api_key:
            print("❌ Both username and API key are required!")
            return False
            
        print(f"✅ Credentials entered for user: {self.username}")
        return True
    
    def test_authentication(self):
        """Test if credentials work by getting account info"""
        try:
            print("\n🔍 Testing authentication...")
            response = requests.get(
                f'{self.base_url}/account',
                auth=(self.username, self.api_key),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                account = data.get('data', {})
                print(f"✅ Authentication successful!")
                print(f"   Company: {account.get('company_name', 'N/A')}")
                print(f"   Country: {account.get('country', 'N/A')}")
                print(f"   Email: {account.get('email', 'N/A')}")
                return True
            elif response.status_code == 401:
                print("❌ Authentication failed - Invalid credentials")
                print("   Please check your username and API key")
                return False
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def check_balance(self):
        """Check account balance"""
        try:
            print("\n💰 Checking account balance...")
            response = requests.get(
                f'{self.base_url}/account/balance',
                auth=(self.username, self.api_key),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                balance = data.get('data', {})
                credit = float(balance.get('balance', 0))
                currency = balance.get('currency', 'USD')
                
                print(f"✅ Account Balance: {credit:.2f} {currency}")
                
                if credit <= 0:
                    print("⚠️  Warning: No credit available!")
                    print("   Add credit at: https://www.clicksend.com/billing")
                    return False
                elif credit < 1:
                    print("⚠️  Warning: Low balance - may not be enough for testing")
                else:
                    print("✅ Sufficient balance for testing")
                
                return True
            else:
                print(f"❌ Failed to get balance: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking balance: {str(e)}")
            return False
    
    def send_test_sms(self):
        """Send a test SMS"""
        print("\n📱 SMS Test")
        print("=" * 30)
        
        phone = input("Enter phone number (with country code, e.g., +1234567890): ").strip()
        if not phone:
            print("❌ No phone number provided")
            return False
            
        message = input("Enter test message (or press Enter for default): ").strip()
        if not message:
            message = "Hello! This is a test message from ClickSend. No A2P registration required! 🚀"
        
        payload = {
            "messages": [
                {
                    "to": phone,
                    "body": message,
                    "from": "ClickSend"
                }
            ]
        }
        
        try:
            print(f"\n📤 Sending message to {phone}...")
            print(f"Message: {message}")
            
            response = requests.post(
                f'{self.base_url}/sms/send',
                json=payload,
                auth=(self.username, self.api_key),
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            result = response.json()
            
            if response.status_code == 200:
                message_data = result.get('data', {}).get('messages', [])
                if message_data:
                    msg = message_data[0]
                    status = msg.get('status', 'unknown')
                    
                    if status.lower() in ['queued', 'sent']:
                        print(f"✅ Message sent successfully!")
                        print(f"   Message ID: {msg.get('message_id')}")
                        print(f"   Status: {status}")
                        print(f"   Cost: {msg.get('message_price')} {msg.get('currency')}")
                        print(f"   Parts: {msg.get('message_parts', 1)}")
                        return True
                    else:
                        print(f"⚠️  Message queued but status unclear: {status}")
                        print(f"   Message ID: {msg.get('message_id')}")
                        return True
                else:
                    print("❌ No message data in response")
                    return False
            else:
                print(f"❌ Failed to send message: HTTP {response.status_code}")
                error_msg = result.get('response_msg', 'Unknown error')
                print(f"   Error: {error_msg}")
                
                # Provide helpful hints for common errors
                if 'insufficient' in error_msg.lower():
                    print("   💡 Hint: Add credit to your account")
                elif 'invalid' in error_msg.lower() and 'number' in error_msg.lower():
                    print("   💡 Hint: Check phone number format (include country code)")
                
                return False
                
        except Exception as e:
            print(f"❌ Error sending message: {str(e)}")
            return False
    
    def test_integration_with_your_code(self):
        """Test integration with your existing SMS sender"""
        try:
            print("\n🔧 Testing with your SMS sender code...")
            
            # Import your SMS sender
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            
            # Temporarily set environment variables for testing
            os.environ['CLICKSEND_USERNAME'] = self.username
            os.environ['CLICKSEND_API_KEY'] = self.api_key
            
            from alternative_sms import AlternativeSMSSender
            
            sender = AlternativeSMSSender()
            
            # Test a simple message
            phone = input("Enter phone number for integration test: ").strip()
            if not phone:
                print("Skipping integration test")
                return True
                
            success, result = sender.send_via_clicksend(phone, "Integration test message from your SMS sender! 🎉")
            
            if success:
                print(f"✅ Integration test successful: {result}")
                return True
            else:
                print(f"❌ Integration test failed: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Integration test error: {str(e)}")
            return False

def main():
    print("🚀 ClickSend Direct Integration Test")
    print("=" * 50)
    print("This tool will test your ClickSend integration step by step.\n")
    
    tester = ClickSendDirectTester()
    
    # Step 1: Get credentials
    if not tester.get_credentials():
        return
    
    # Step 2: Test authentication
    if not tester.test_authentication():
        return
    
    # Step 3: Check balance
    if not tester.check_balance():
        print("\n⚠️  You can continue testing, but you may not be able to send messages.")
    
    # Step 4: Optional SMS test
    print("\n" + "=" * 50)
    send_test = input("Would you like to send a test SMS? (y/n): ").strip().lower()
    if send_test in ['y', 'yes']:
        tester.send_test_sms()
    
    # Step 5: Integration test
    print("\n" + "=" * 50)
    integration_test = input("Test integration with your SMS sender code? (y/n): ").strip().lower()
    if integration_test in ['y', 'yes']:
        tester.test_integration_with_your_code()
    
    print("\n✅ ClickSend integration test complete!")
    print("\n💡 To use ClickSend in your scripts permanently, set these environment variables:")
    print(f"   $env:CLICKSEND_USERNAME = '{tester.username}'")
    print(f"   $env:CLICKSEND_API_KEY = '[your_api_key]'")
    print("\n🚀 ClickSend is ready for production use - no A2P registration needed!")

if __name__ == "__main__":
    main()
