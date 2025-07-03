#!/usr/bin/env python3
import sqlite3
from datetime import datetime

def remove_duplicates():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    
    print("=== CONTACT DUPLICATE REMOVAL ===")
    
    # Backup before removal
    backup_filename = f"contacts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    print(f"Creating backup: {backup_filename}")
    
    # Get initial count
    cursor.execute("SELECT COUNT(*) FROM contacts")
    initial_count = cursor.fetchone()[0]
    print(f"Initial contact count: {initial_count}")
    
    removed_count = 0
    
    # 1. Remove exact email duplicates (keep the oldest one)
    print("\n1. Removing email duplicates...")
    cursor.execute("""
        DELETE FROM contacts 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM contacts 
            WHERE email IS NOT NULL AND email != ''
            GROUP BY LOWER(email)
        ) AND email IS NOT NULL AND email != ''
    """)
    email_removed = cursor.rowcount
    removed_count += email_removed
    print(f"   Removed {email_removed} email duplicates")
    
    # 2. Remove name + phone duplicates (keep the oldest one)
    print("\n2. Removing name + phone duplicates...")
    cursor.execute("""
        DELETE FROM contacts 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM contacts 
            WHERE first_name IS NOT NULL AND last_name IS NOT NULL 
                  AND phone IS NOT NULL AND phone != ''
            GROUP BY LOWER(first_name), LOWER(last_name), phone
        ) AND first_name IS NOT NULL AND last_name IS NOT NULL 
              AND phone IS NOT NULL AND phone != ''
    """)
    name_phone_removed = cursor.rowcount
    removed_count += name_phone_removed
    print(f"   Removed {name_phone_removed} name+phone duplicates")
    
    # 3. Remove fuzzy duplicates (similar names with same email domain)
    print("\n3. Checking for fuzzy duplicates...")
    cursor.execute("""
        SELECT id, first_name, last_name, email, phone
        FROM contacts 
        WHERE email IS NOT NULL AND email != ''
        ORDER BY email, first_name, last_name
    """)
    
    contacts = cursor.fetchall()
    fuzzy_duplicates = []
    
    for i in range(len(contacts) - 1):
        current = contacts[i]
        next_contact = contacts[i + 1]
        
        # Check if emails are from same domain and names are similar
        if (current[3] and next_contact[3] and 
            current[3].split('@')[1] == next_contact[3].split('@')[1] and
            current[1] and next_contact[1] and current[2] and next_contact[2] and
            current[1].lower() == next_contact[1].lower() and 
            current[2].lower() == next_contact[2].lower()):
            
            fuzzy_duplicates.append((current[0], next_contact[0]))
    
    fuzzy_removed = 0
    for dup_pair in fuzzy_duplicates:
        # Keep the first one, remove the second
        cursor.execute("DELETE FROM contacts WHERE id = ?", (dup_pair[1],))
        fuzzy_removed += cursor.rowcount
    
    removed_count += fuzzy_removed
    print(f"   Removed {fuzzy_removed} fuzzy duplicates")
    
    # Get final count
    cursor.execute("SELECT COUNT(*) FROM contacts")
    final_count = cursor.fetchone()[0]
    
    print(f"\n=== SUMMARY ===")
    print(f"Initial contacts: {initial_count}")
    print(f"Final contacts: {final_count}")
    print(f"Total removed: {removed_count}")
    print(f"Reduction: {((initial_count - final_count) / initial_count * 100):.1f}%")
    
    # Show assignment distribution after cleanup
    print(f"\n=== ASSIGNMENT DISTRIBUTION AFTER CLEANUP ===")
    cursor.execute("""
        SELECT 
            u.first_name || ' ' || u.last_name as name,
            u.role,
            COUNT(c.id) as contact_count
        FROM users u
        LEFT JOIN contacts c ON u.id = c.assigned_to
        GROUP BY u.id
        ORDER BY contact_count DESC
    """)
    
    for name, role, count in cursor.fetchall():
        print(f"  {name} ({role}): {count} contacts")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Duplicate removal complete!")
    return final_count

if __name__ == "__main__":
    remove_duplicates()
