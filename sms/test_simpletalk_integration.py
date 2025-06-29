#!/usr/bin/env python3
"""
Test script for SimpleTalk.ai integration with Sparky Messaging
Tests all AI endpoints to ensure proper functionality
"""

import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, method="GET", payload=None):
    """Test an API endpoint and return the result"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        
        print(f"\n{'='*60}")
        print(f"Testing: {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    print("🤖 Testing SimpleTalk.ai Integration with Sparky Messaging")
    print("=" * 60)
    
    # Test 1: Check AI status
    print("\n1. Testing AI Status")
    test_endpoint("/api/ai/status")
    
    # Test 2: Generate SMS (this will fail without API key, but tests the endpoint)
    print("\n2. Testing SMS Generation")
    sms_payload = {
        "context": "Follow up on meeting about marketing automation",
        "contact_info": {
            "name": "John Smith", 
            "company": "ABC Corp"
        },
        "tone": "professional",
        "max_length": 160
    }
    test_endpoint("/api/ai/generate/sms", "POST", sms_payload)
    
    # Test 3: Generate RVM script
    print("\n3. Testing RVM Generation")
    rvm_payload = {
        "context": "Introduction to new service offering",
        "contact_info": {
            "name": "Jane Doe",
            "company": "XYZ Inc"
        },
        "tone": "conversational",
        "duration": "30 seconds"
    }
    test_endpoint("/api/ai/generate/rvm", "POST", rvm_payload)
    
    # Test 4: Optimize message
    print("\n4. Testing Message Optimization")
    optimize_payload = {
        "original_message": "Hey there! We have a new product that might interest you. Give us a call!",
        "optimization_goal": "engagement"
    }
    test_endpoint("/api/ai/optimize", "POST", optimize_payload)
    
    # Test 5: Create conversation flow
    print("\n5. Testing Conversation Flow Creation")
    flow_payload = {
        "campaign_goal": "Generate leads for consulting services",
        "audience_info": "Small business owners in tech industry",
        "num_steps": 3
    }
    test_endpoint("/api/ai/conversation-flow", "POST", flow_payload)
    
    # Test 6: Get AI usage
    print("\n6. Testing AI Usage Stats")
    test_endpoint("/api/ai/usage")
    
    print("\n" + "="*60)
    print("🎯 SimpleTalk.ai Integration Test Complete!")
    print("💡 To enable AI features, configure SIMPLETALK_API_KEY in .env")
    print("📖 Access the dashboard at: http://localhost:5000/")

if __name__ == "__main__":
    main()
