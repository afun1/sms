#!/usr/bin/env python3
"""
Test script for Slybroadcast RVM integration
"""

import os
from dotenv import load_dotenv
from slybroadcast_rvm import SlybroadcastRVM

# Load environment variables
load_dotenv()

def test_slybroadcast_basic():
    """Basic test of Slybroadcast functionality"""
    print("🎙️ Testing Slybroadcast RVM Integration")
    print("=" * 50)
    
    rvm = SlybroadcastRVM()
    
    # Check configuration
    print(f"Email configured: {'✅' if rvm.email else '❌'}")
    print(f"Password configured: {'✅' if rvm.password else '❌'}")
    print(f"Fully configured: {'✅' if rvm.is_configured() else '❌'}")
    
    if not rvm.is_configured():
        print("\n❌ Slybroadcast not configured")
        print("💡 Please set SLYBROADCAST_EMAIL and SLYBROADCAST_PASSWORD in .env")
        print("\nExample .env entries:")
        print("SLYBROADCAST_EMAIL=your_email@example.com")
        print("SLYBROADCAST_PASSWORD=your_password")
        return False
    
    print("✅ Slybroadcast configured")
    
    # Test TTS URL generation
    test_message = "Hello, this is a test message for text-to-speech conversion."
    tts_url = rvm.text_to_speech_url(test_message)
    print(f"\n🎵 TTS URL generated: {tts_url}")
    
    # Test API endpoint construction
    print(f"\n🔗 API Base URL: {rvm.base_url}")
    print(f"Send Endpoint: {rvm.base_url}{rvm.api_endpoints['send']}")
    
    return True

def test_with_dummy_data():
    """Test with dummy data (won't actually send)"""
    rvm = SlybroadcastRVM()
    
    if not rvm.is_configured():
        print("❌ Cannot test - Slybroadcast not configured")
        return
    
    print("\n📞 Testing RVM sending logic (dry run)")
    
    # Use a dummy phone number for testing
    test_phone = "+15551234567"  # Dummy number
    test_message = "This is a test ringless voicemail message."
    
    print(f"Would send to: {test_phone}")
    print(f"Message: {test_message}")
    
    # Generate TTS URL
    audio_url = rvm.text_to_speech_url(test_message)
    print(f"Audio URL: {audio_url}")
    
    print("\n⚠️  To actually send, replace with real phone number and run:")
    print("success, result = rvm.send_text_to_speech_rvm('+1234567890', 'Your message')")

if __name__ == "__main__":
    if test_slybroadcast_basic():
        test_with_dummy_data()
    
    print("\n" + "=" * 50)
    print("Test completed. Ready for real testing with valid credentials.")
