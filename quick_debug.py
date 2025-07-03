#!/usr/bin/env python3
import sqlite3
import requests
import json

def check_database():
    print("=== DATABASE CHECK ===")
    try:
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        
        # Check if manager user exists
        cursor.execute("SELECT * FROM users WHERE id = 'user-manager-example-com'")
        manager = cursor.fetchone()
        print(f"Manager user exists: {manager is not None}")
        if manager:
            print(f"Manager data: {manager}")
        
        # Check contacts assigned to manager
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE assigned_to = 'user-manager-example-com'")
        manager_contacts = cursor.fetchone()[0]
        print(f"Contacts assigned to manager: {manager_contacts}")
        
        # Check contacts assigned to manager's direct reports
        cursor.execute("""
            SELECT COUNT(*) FROM contacts c
            JOIN users u ON c.assigned_to = u.id
            WHERE u.manager_id = 'user-manager-example-com'
        """)
        reports_contacts = cursor.fetchone()[0]
        print(f"Contacts assigned to manager's reports: {reports_contacts}")
        
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

def check_api():
    print("\n=== API CHECK ===")
    try:
        # Test health
        response = requests.get("http://localhost:3000/api/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test contacts for manager
        response = requests.get(
            "http://localhost:3000/api/contacts",
            params={
                "current_user_id": "user-manager-example-com",
                "per_page": "5"
            },
            timeout=10
        )
        print(f"Contacts API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Manager can see {len(data.get('contacts', []))} contacts")
            print(f"User role detected: {data.get('user_role')}")
        else:
            print(f"API Error: {response.text}")
            
    except Exception as e:
        print(f"API error: {e}")

if __name__ == "__main__":
    check_database()
    check_api()
