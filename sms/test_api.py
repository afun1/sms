"""
Test script for SMS API endpoints
Run this to test your API before integrating with GoHighLevel
"""

import requests
import json
import time

# API base URL (change this to your actual server URL)
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_single_sms():
    """Test sending a single SMS"""
    print("\n📱 Testing single SMS send...")
    
    payload = {
        "phone": "+1234567890",  # Replace with a real phone number for testing
        "message": "Hello {name}, this is a test message from the SMS API!",
        "name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/sms/send",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_bulk_sms():
    """Test sending bulk SMS"""
    print("\n📱📱 Testing bulk SMS send...")
    
    payload = {
        "contacts": [
            {"phone": "+1234567890", "name": "John Doe"},
            {"phone": "+1987654321", "name": "Jane Smith", "message": "Custom message for Jane!"}
        ],
        "default_message": "Hello {name}, this is a bulk test message!",
        "delay": 1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/sms/bulk",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ghl_webhook():
    """Test GoHighLevel webhook format"""
    print("\n🌐 Testing GHL webhook...")
    
    # Simulate GHL webhook payload
    payload = {
        "contact": {
            "phone": "+1234567890",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com"
        },
        "message": "Hi {firstName}, your appointment is confirmed for tomorrow!",
        "trigger": "appointment_confirmed"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/webhook/ghl",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_csv_format():
    """Test CSV data sending"""
    print("\n📊 Testing CSV format...")
    
    csv_data = """phone_number,name,message
+1234567890,John Doe,
+1987654321,Jane Smith,Special message for Jane!
+1555123456,Bob Johnson,"""
    
    payload = {
        "csv_data": csv_data,
        "default_message": "Hello {name}, this is a CSV test message!",
        "delay": 1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/sms/csv",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_webhook_debug():
    """Test webhook debugging endpoint"""
    print("\n🐛 Testing webhook debug...")
    
    payload = {
        "test": "data",
        "contact": {
            "phone": "+1234567890",
            "name": "Debug Test"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/webhook/test",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Custom-Header": "test-value"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SMS API Test Suite")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Server is running!")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("\n💡 Make sure to start the server first:")
        print("   python sms_api_server.py")
        return
    
    print()
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Webhook Debug", test_webhook_debug),
        ("Single SMS", test_single_sms),
        ("Bulk SMS", test_bulk_sms),
        ("GHL Webhook", test_ghl_webhook),
        ("CSV Format", test_csv_format),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is ready for GoHighLevel integration.")
        print("\n📖 Next steps:")
        print("1. Deploy your API to a public server (ngrok, Heroku, etc.)")
        print("2. Update your GHL webhook URL")
        print("3. Test with real GHL workflows")
    else:
        print("⚠️  Some tests failed. Check your configuration:")
        print("1. Verify Twilio credentials in .env file")
        print("2. Check phone number format (+1234567890)")
        print("3. Review server logs for errors")

if __name__ == "__main__":
    main()
