"""
Alternative SMS sending script using different providers
that don't require A2P registration
"""

import pandas as pd
import requests
import time
from dotenv import load_dotenv
import os

class AlternativeSMSSender:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('SMS_API_KEY')
        self.sender_id = os.getenv('SENDER_ID', 'SMS')
    
    def send_via_textbelt(self, phone, message):
        """
        Send SMS using TextBelt (free tier available)
        Sign up at: https://textbelt.com/
        """
        url = 'https://textbelt.com/text'
        data = {
            'phone': phone,
            'message': message,
            'key': self.api_key if self.api_key else 'textbelt'  # 'textbelt' for free tier (1 msg/day)
        }
        
        try:
            response = requests.post(url, data=data)
            result = response.json()
            
            if result.get('success'):
                return True, f"Success - ID: {result.get('textId')}"
            else:
                return False, result.get('error', 'Unknown error')
        except Exception as e:
            return False, str(e)
    
    def send_via_clicksend(self, phone, message):
        """
        Send SMS using ClickSend API
        Sign up at: https://www.clicksend.com/
        """
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
                    "from": self.sender_id
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
            
            result = response.json()
            
            if response.status_code == 200:
                return True, "Message sent successfully"
            else:
                return False, result.get('response_msg', 'Unknown error')
        except Exception as e:
            return False, str(e)
    
    def send_bulk_sms(self, csv_file, default_message, provider='textbelt', delay=2):
        """
        Send bulk SMS from CSV file
        """
        try:
            df = pd.read_csv(csv_file)
            
            if 'phone_number' not in df.columns:
                print("Error: CSV must contain 'phone_number' column")
                return
            
            total = len(df)
            successful = 0
            failed = 0
            
            print(f"Starting to send {total} messages using {provider}...")
            
            for idx, row in df.iterrows():
                # Handle phone number safely
                phone_raw = row['phone_number']
                if pd.isna(phone_raw):
                    print(f"Skipping row {idx + 1}: No phone number")
                    continue
                phone = str(phone_raw).strip()
                
                # Handle name safely
                name_raw = row.get('name', 'Friend')
                name = str(name_raw) if not pd.isna(name_raw) else 'Friend'
                
                # Handle custom message safely
                custom_msg_raw = row.get('message', '')
                custom_msg = str(custom_msg_raw) if not pd.isna(custom_msg_raw) else ''
                
                # Prepare message
                message = custom_msg if custom_msg and custom_msg.strip() else default_message
                message = message.replace('{name}', name)
                
                print(f"Sending to {phone}...")
                
                # Send message based on provider
                if provider == 'textbelt':
                    success, result = self.send_via_textbelt(phone, message)
                elif provider == 'clicksend':
                    success, result = self.send_via_clicksend(phone, message)
                else:
                    print(f"Unknown provider: {provider}")
                    break
                
                if success:
                    print(f"✓ Success: {result}")
                    successful += 1
                else:
                    print(f"✗ Failed: {result}")
                    failed += 1
                
                # Progress
                print(f"Progress: {idx + 1}/{total}")
                
                # Delay between messages
                if idx < total - 1:
                    time.sleep(delay)
            
            print(f"\nCompleted! Success: {successful}, Failed: {failed}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def test_clicksend_connection(self):
        """
        Test ClickSend connection and credentials
        """
        username = os.getenv('CLICKSEND_USERNAME')
        api_key = os.getenv('CLICKSEND_API_KEY')
        
        print("🚀 Testing ClickSend Connection...")
        print("=" * 40)
        
        if not username or not api_key:
            print("❌ ClickSend credentials not found in environment")
            print("Make sure to set:")
            print("  CLICKSEND_USERNAME=your_username")
            print("  CLICKSEND_API_KEY=your_api_key")
            return False
        
        print(f"✅ Found credentials for user: {username}")
        
        # Test account connection
        try:
            response = requests.get(
                'https://rest.clicksend.com/v3/account',
                auth=(username, api_key)
            )
            
            if response.status_code == 200:
                data = response.json()
                account = data.get('data', {})
                print(f"✅ Account connected successfully!")
                print(f"   Company: {account.get('company_name', 'N/A')}")
                print(f"   Country: {account.get('country', 'N/A')}")
                
                # Check balance
                balance_response = requests.get(
                    'https://rest.clicksend.com/v3/account/balance',
                    auth=(username, api_key)
                )
                
                if balance_response.status_code == 200:
                    balance_data = balance_response.json()
                    balance = balance_data.get('data', {})
                    credit = balance.get('balance', 0)
                    currency = balance.get('currency', 'USD')
                    print(f"💰 Balance: {credit} {currency}")
                    
                    if credit > 0:
                        print("✅ Ready to send messages!")
                        return True
                    else:
                        print("⚠️  Low balance - add credit to send messages")
                        return True
                else:
                    print("⚠️  Could not check balance")
                    return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False

def main():
    sender = AlternativeSMSSender()
    
    # Test ClickSend connection first
    print("Testing ClickSend integration...")
    if sender.test_clicksend_connection():
        print("\n" + "="*50)
        print("🎉 ClickSend is ready to use!")
        print("Advantages of ClickSend (No A2P required):")
        print("✅ Unlimited daily messages (no 200/day limit)")
        print("✅ Instant setup (no weeks of approval)")
        print("✅ Global reach (190+ countries)")
        print("✅ No monthly fees")
        print("="*50)
        
        # Ask if user wants to test sending
        test_send = input("\nWould you like to test sending a message? (y/n): ").strip().lower()
        if test_send == 'y':
            phone = input("Enter phone number (with country code, e.g., +1234567890): ").strip()
            if phone:
                success, result = sender.send_via_clicksend(phone, "Test message from ClickSend - No A2P required! 🚀")
                if success:
                    print(f"✅ Test message sent: {result}")
                else:
                    print(f"❌ Test failed: {result}")
    else:
        print("\n❌ ClickSend setup needs attention")
    
    # Uncomment below to run bulk SMS
    # csv_file = 'sample_contacts.csv'
    # default_message = "Hello {name}, this is a test message from our system!"
    # provider = 'clicksend'
    # sender.send_bulk_sms(csv_file, default_message, provider)

if __name__ == "__main__":
    main()
