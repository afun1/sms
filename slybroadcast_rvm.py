"""
Slybroadcast RVM Integration Module
Handles Ringless Voicemail sending via Slybroadcast API
"""

import requests
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from io import BytesIO
import tempfile
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class SlybroadcastRVM:
    def __init__(self):
        self.email = os.getenv('SLYBROADCAST_EMAIL')
        self.password = os.getenv('SLYBROADCAST_PASSWORD')        # Updated API endpoints based on Slybroadcast documentation
        self.base_url = "https://www.slybroadcast.com"
        self.api_endpoints = {
            'send': '/sbapi/send_drop.php',  # Try singular form
            'upload': '/sbapi/upload_audio.php',
            'balance': '/sbapi/get_balance.php'
        }
        
        if not self.email or not self.password:
            logger.warning("Slybroadcast credentials not configured")
    
    def is_configured(self):
        """Check if Slybroadcast is properly configured"""
        return bool(self.email and self.password)
    
    def text_to_speech_url(self, text, voice="female1"):
        """
        Convert text to speech using a TTS service and return URL
        For production, you'd use a service like AWS Polly, Google TTS, etc.
        This is a placeholder implementation.
        """
        # This is a simplified example - you'd integrate with a real TTS service
        # For now, return a placeholder URL
        tts_services = {
            'responsivevoice': f"https://responsivevoice.org/responsivevoice/getvoice.php?t={text}&tl=en&sv=g1",
            # Add other TTS services as needed
        }
        
        # For demo purposes, we'll use ResponsiveVoice (free tier)
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        return f"https://responsivevoice.org/responsivevoice/getvoice.php?t={encoded_text}&tl=en&sv=g1"
    
    def upload_audio_file(self, audio_url_or_path):
        """
        Upload audio file to Slybroadcast or return URL if already hosted
        """
        if audio_url_or_path.startswith('http'):
            # Already a URL, return as-is
            return audio_url_or_path
        else:
            # Local file - would need to upload to a hosting service
            # For production, upload to AWS S3, Google Cloud Storage, etc.
            logger.warning("Local file upload not implemented - use hosted URLs")
            return audio_url_or_path
    
    def send_rvm(self, phone_number, audio_url, title="RVM Campaign"):
        """
        Send ringless voicemail via Slybroadcast
        
        Args:
            phone_number (str): Phone number with country code (+1234567890)
            audio_url (str): URL to hosted audio file
            title (str): Campaign title
        
        Returns:
            tuple: (success: bool, result: str)
        """
        if not self.is_configured():
            return False, "Slybroadcast credentials not configured"
        
        # Clean phone number (remove +1 if present)
        clean_phone = phone_number.replace('+1', '').replace('+', '').replace('-', '').replace(' ', '')        # Slybroadcast API endpoint - updated to correct path
        url = f"{self.base_url}/sbapi/send_drop.php"
          # Prepare data for Slybroadcast API
        data = {
            'email': self.email,
            'password': self.password,
            'phone_numbers': clean_phone,  # Updated parameter name
            'audio_url': audio_url,
            'campaign_name': title,  # Updated parameter name
            'caller_id': '0000000000'  # Default caller ID
        }
        
        try:
            logger.info(f"Sending RVM to {phone_number} via Slybroadcast")
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                result_text = response.text.strip()
                
                # Parse Slybroadcast response
                if 'success' in result_text.lower() or 'campaign sent' in result_text.lower():
                    logger.info(f"✅ RVM sent successfully to {phone_number}")
                    return True, f"RVM sent successfully: {result_text}"
                else:
                    logger.error(f"❌ RVM failed for {phone_number}: {result_text}")
                    return False, f"RVM failed: {result_text}"
            else:
                error_msg = f"HTTP error {response.status_code}: {response.text}"
                logger.error(f"❌ RVM HTTP error for {phone_number}: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Request timeout - Slybroadcast may be slow"
            logger.error(f"❌ RVM timeout for {phone_number}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"❌ RVM error for {phone_number}: {error_msg}")
            return False, error_msg
    
    def send_text_to_speech_rvm(self, phone_number, message_text, voice="female1", title="RVM Campaign"):
        """
        Send RVM using text-to-speech conversion
        
        Args:
            phone_number (str): Phone number
            message_text (str): Text to convert to speech
            voice (str): Voice type
            title (str): Campaign title
        """
        try:
            # Convert text to speech URL
            audio_url = self.text_to_speech_url(message_text, voice)
            
            # Send RVM
            return self.send_rvm(phone_number, audio_url, title)
            
        except Exception as e:
            return False, f"TTS conversion failed: {str(e)}"
    
    def send_bulk_rvm(self, contacts, message_text_or_audio_url, use_tts=True, delay=2):
        """
        Send bulk RVM campaigns
        
        Args:
            contacts (list): List of contact dicts with 'phone' and optional 'name'
            message_text_or_audio_url (str): Either text for TTS or audio URL
            use_tts (bool): Whether to use text-to-speech
            delay (int): Delay between sends in seconds
        """
        results = []
        
        for contact in contacts:
            phone = contact.get('phone', contact.get('phone_number', ''))
            name = contact.get('name', 'Friend')
            
            # Personalize message if using TTS
            if use_tts:
                personalized_message = message_text_or_audio_url.replace('{name}', name)
                success, result = self.send_text_to_speech_rvm(
                    phone, 
                    personalized_message,
                    title=f"RVM for {name}"
                )
            else:
                success, result = self.send_rvm(
                    phone,
                    message_text_or_audio_url,
                    title=f"RVM for {name}"
                )
            
            results.append({
                'phone': phone,
                'name': name,
                'success': success,
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'cost': 0.09 if success else 0  # Slybroadcast cost per drop
            })
            
            logger.info(f"RVM to {phone}: {'✅' if success else '❌'} {result}")
            
            # Delay between sends
            if delay > 0:
                time.sleep(delay)
        
        return results
    
    def get_account_balance(self):
        """
        Get Slybroadcast account balance
        Note: This might require a different API endpoint
        """
        # This is a placeholder - Slybroadcast may have a different endpoint for balance
        url = f"{self.base_url}/get_balance.php"
        
        data = {
            'email': self.email,
            'password': self.password
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                return True, response.text
            else:
                return False, f"HTTP error: {response.status_code}"
                
        except Exception as e:
            return False, f"Error getting balance: {str(e)}"

# Example usage and testing
def test_slybroadcast_integration():
    """Test Slybroadcast integration"""
    
    print("🎙️ Testing Slybroadcast RVM Integration")
    print("=" * 50)
    
    rvm = SlybroadcastRVM()
    
    # Check configuration
    if not rvm.is_configured():
        print("❌ Slybroadcast not configured")
        print("💡 Please set SLYBROADCAST_EMAIL and SLYBROADCAST_PASSWORD in .env")
        return
    
    print("✅ Slybroadcast configured")
    
    # Test single RVM
    test_phone = "+1234567890"  # Replace with real number for testing
    test_message = "Hi there! This is a test ringless voicemail from your automated system. Have a great day!"
    
    print(f"\n📞 Sending test RVM to {test_phone}...")
    success, result = rvm.send_text_to_speech_rvm(test_phone, test_message)
    
    if success:
        print(f"✅ {result}")
    else:
        print(f"❌ {result}")
    
    # Test bulk RVM
    test_contacts = [
        {"phone": "+1234567890", "name": "John Doe"},
        {"phone": "+1987654321", "name": "Jane Smith"}
    ]
    
    bulk_message = "Hi {name}, this is a bulk test message from our RVM system!"
    
    print(f"\n📞 Sending bulk RVM to {len(test_contacts)} contacts...")
    bulk_results = rvm.send_bulk_rvm(test_contacts, bulk_message, use_tts=True, delay=1)
    
    # Show results
    successful = sum(1 for r in bulk_results if r['success'])
    total_cost = sum(r['cost'] for r in bulk_results)
    
    print(f"\n📊 Bulk RVM Results:")
    print(f"  Total Sent: {len(bulk_results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {len(bulk_results) - successful}")
    print(f"  Total Cost: ${total_cost:.2f}")
    
    for result in bulk_results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['phone']} ({result['name']}): {result['result']}")

if __name__ == "__main__":
    test_slybroadcast_integration()
