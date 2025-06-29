"""
Quick start script for SMS API with GoHighLevel integration
"""

import os
import sys
import subprocess
import time

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("📝 Please create .env file with your Twilio credentials")
        return False
    
    # Check for required variables
    with open('.env', 'r') as f:
        content = f.read()
        
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
    missing_vars = []
    
    for var in required_vars:
        if f"{var}=your_" in content or var not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Please update these variables in your .env file:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    return True

def start_api_server():
    """Start the Flask API server"""
    print("🚀 Starting SMS API Server...")
    print("📡 GoHighLevel webhook endpoint will be available at:")
    print("   http://localhost:5000/api/webhook/ghl")
    print()
    print("💡 To make it accessible from GHL:")
    print("   1. Use ngrok: ngrok http 5000")
    print("   2. Or deploy to cloud (Heroku, Render, etc.)")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, 'sms_api_server.py'])
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")

def run_tests():
    """Run API tests"""
    print("🧪 Running API tests...")
    print("Make sure the API server is running in another terminal!")
    print()
    
    try:
        subprocess.run([sys.executable, 'test_api.py'])
    except KeyboardInterrupt:
        print("\n👋 Tests stopped!")

def main():
    print("🚀 SMS API for GoHighLevel Integration")
    print("=" * 50)
    
    # Check environment
    if not check_env_file():
        print("\n🔧 Setup your .env file first, then run this script again.")
        return
    
    print("✅ Environment configured!")
    print()
    
    print("Choose an option:")
    print("1. Start API Server (for GHL integration)")
    print("2. Run API Tests")
    print("3. View GHL Integration Guide")
    print("4. Exit")
    print()
    
    try:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            start_api_server()
        elif choice == '2':
            run_tests()
        elif choice == '3':
            print("\n📖 Opening GHL Integration Guide...")
            if os.path.exists('GHL_INTEGRATION_GUIDE.md'):
                with open('GHL_INTEGRATION_GUIDE.md', 'r') as f:
                    print(f.read())
            else:
                print("Guide not found!")
        elif choice == '4':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
