#!/usr/bin/env python3
"""
Test API endpoints for SMS and RVM functionality
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_capacity_endpoint():
    """Test the capacity endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/capacity")
        print(f"Capacity check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Capacity check failed: {e}")
        return False

def test_rvm_send_endpoint():
    """Test the RVM send endpoint"""
    test_data = {
        "phone_number": "+15551234567",  # Test number
        "message": "This is a test RVM message from the API",
        "voice": "female1"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/rvm/send", json=test_data)
        print(f"RVM Send: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code in [200, 400]  # 400 expected for test number
    except Exception as e:
        print(f"RVM send test failed: {e}")
        return False

def test_multi_send_endpoint():
    """Test the multi-channel send endpoint"""
    test_data = {
        "phone_number": "+15551234567",
        "sms_message": "This is an SMS test",
        "rvm_message": "This is an RVM test",
        "send_sms": True,
        "send_rvm": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/multi/send", json=test_data)
        print(f"Multi Send: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code in [200, 400]  # 400 expected for test number
    except Exception as e:
        print(f"Multi send test failed: {e}")
        return False

def test_ghl_webhook():
    """Test the GoHighLevel webhook endpoint"""
    # Sample GHL webhook data
    ghl_data = {
        "contact": {
            "phone": "+15551234567",
            "firstName": "John",
            "lastName": "Doe"
        },
        "workflow": {
            "name": "Test Workflow"
        },
        "customFields": {
            "sms_message": "Hello from GHL workflow!",
            "rvm_message": "This is a voicemail from your GHL automation",
            "send_both": "true"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/webhook/ghl", json=ghl_data)
        print(f"GHL Webhook: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code in [200, 400]
    except Exception as e:
        print(f"GHL webhook test failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Testing SMS/RVM API Endpoints")
    print("=" * 50)
    
    # Wait for server to be ready
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Capacity Check", test_capacity_endpoint),
        ("RVM Send", test_rvm_send_endpoint),
        ("Multi-Channel Send", test_multi_send_endpoint),
        ("GHL Webhook", test_ghl_webhook)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"{'✅' if success else '❌'} {test_name}")
        except Exception as e:
            print(f"❌ {test_name} - Error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    for test_name, success in results:
        print(f"  {'✅' if success else '❌'} {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTests passed: {passed}/{total}")

if __name__ == "__main__":
    main()
