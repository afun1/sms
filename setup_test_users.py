#!/usr/bin/env python3
"""
Script to set up test users and contact assignments for role-based access testing
"""

import sqlite3
import uuid
from datetime import datetime

def setup_test_users_and_assignments():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # Create a test user (mapped from Supabase user with role 'user')
    test_user_id = 'user-john-example-com'  # This matches the mapping pattern
    cursor.execute('''
        INSERT OR REPLACE INTO users (id, email, first_name, last_name, role, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        test_user_id,
        'john@example.com',
        'John',
        'User',
        'user',
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))
    
    # Create a manager user
    manager_user_id = 'user-manager-example-com'
    cursor.execute('''
        INSERT OR REPLACE INTO users (id, email, first_name, last_name, role, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        manager_user_id,
        'manager@example.com',
        'Manager',
        'User',
        'manager',
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))
    
    # Get first 10 contacts for the regular user
    cursor.execute('SELECT id FROM contacts LIMIT 10')
    user_contacts = cursor.fetchall()
    
    # Get next 20 contacts for the manager
    cursor.execute('SELECT id FROM contacts LIMIT 20 OFFSET 10')
    manager_contacts = cursor.fetchall()
    
    # Assign first 10 contacts to the test user
    for contact in user_contacts:
        cursor.execute('''
            UPDATE contacts 
            SET assigned_to = ?, updated_at = ?
            WHERE id = ?
        ''', (test_user_id, datetime.now().isoformat(), contact[0]))
    
    # Assign next 20 contacts to the manager
    for contact in manager_contacts:
        cursor.execute('''
            UPDATE contacts 
            SET assigned_to = ?, updated_at = ?
            WHERE id = ?
        ''', (manager_user_id, datetime.now().isoformat(), contact[0]))
    
    # Set the manager as the test user's manager
    cursor.execute('''
        UPDATE users 
        SET manager_id = ?
        WHERE id = ?
    ''', (manager_user_id, test_user_id))
    
    conn.commit()
    
    # Print summary
    cursor.execute('SELECT COUNT(*) FROM contacts WHERE assigned_to = ?', (test_user_id,))
    user_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM contacts WHERE assigned_to = ?', (manager_user_id,))
    manager_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM contacts WHERE assigned_to IS NULL')
    unassigned_count = cursor.fetchone()[0]
    
    print(f"✅ Test setup complete!")
    print(f"📊 Contact assignments:")
    print(f"   - Regular user ({test_user_id}): {user_count} contacts")
    print(f"   - Manager user ({manager_user_id}): {manager_count} contacts")
    print(f"   - Unassigned contacts: {unassigned_count}")
    print(f"   - Admin user can see all contacts")
    print()
    print(f"🔗 User hierarchy:")
    print(f"   - John User (user role) reports to Manager User")
    print(f"   - Manager User can see their own contacts + John's contacts")
    print(f"   - Admin can see all contacts")
    
    conn.close()

if __name__ == '__main__':
    setup_test_users_and_assignments()
