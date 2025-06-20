#!/usr/bin/env python3
"""
Quick start script for SMS Sender Application
"""

import os
import sys

def main():
    print("🚀 SMS Sender Application")
    print("=" * 40)
    print()
    
    # Check if required files exist
    required_files = [
        'sms_sender.py',
        'requirements.txt',
        'sample_contacts.csv'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return
    
    print("✅ All required files found")
    print()
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠️  No .env file found")
        print("📝 Please create a .env file with your credentials:")
        print()
        print("TWILIO_ACCOUNT_SID=your_account_sid_here")
        print("TWILIO_AUTH_TOKEN=your_auth_token_here")
        print("TWILIO_PHONE_NUMBER=your_twilio_phone_number_here")
        print()
        print("You can copy .env.example to .env and edit it.")
        print()
    else:
        print("✅ .env file found")
        print()
    
    # Show options
    print("Choose an option:")
    print("1. Run GUI SMS Sender (Recommended)")
    print("2. Run command-line alternative")
    print("3. View sample CSV format")
    print("4. Exit")
    print()
    
    try:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            print("\n🚀 Starting GUI SMS Sender...")
            os.system('python sms_sender.py')
        elif choice == '2':
            print("\n🚀 Starting command-line SMS sender...")
            os.system('python alternative_sms.py')
        elif choice == '3':
            print("\n📋 Sample CSV format:")
            print("-" * 30)
            if os.path.exists('sample_contacts.csv'):
                with open('sample_contacts.csv', 'r') as f:
                    print(f.read())
            else:
                print("phone_number,name,message")
                print("+1234567890,John Doe,")
                print("+1987654321,Jane Smith,Custom message here")
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
