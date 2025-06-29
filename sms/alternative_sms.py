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
                phone = str(row['phone_number']).strip()
                name = row.get('name', 'Friend')
                custom_msg = row.get('message', '')
                
                # Prepare message
                message = custom_msg if custom_msg and str(custom_msg).strip() else default_message
                message = message.replace('{name}', name if name else 'Friend')
                
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

def main():
    sender = AlternativeSMSSender()
    
    # Example usage
    csv_file = 'sample_contacts.csv'
    default_message = "Hello {name}, this is a test message from our system!"
    
    # Choose provider: 'textbelt' or 'clicksend'
    provider = 'textbelt'
    
    sender.send_bulk_sms(csv_file, default_message, provider)

if __name__ == "__main__":
    main()
