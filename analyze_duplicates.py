#!/usr/bin/env python3
import sqlite3

def analyze_duplicates():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    
    print("=== DUPLICATE ANALYSIS ===")
    
    # Check for exact email duplicates
    cursor.execute("""
        SELECT email, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM contacts 
        WHERE email IS NOT NULL AND email != ''
        GROUP BY LOWER(email)
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 10
    """)
    email_dupes = cursor.fetchall()
    print(f"\nEmail duplicates: {len(email_dupes)} groups")
    for email, count, ids in email_dupes:
        print(f"  {email}: {count} copies (IDs: {ids[:50]}...)")
    
    # Check for name + phone duplicates
    cursor.execute("""
        SELECT first_name, last_name, phone, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM contacts 
        WHERE first_name IS NOT NULL AND last_name IS NOT NULL 
              AND phone IS NOT NULL AND phone != ''
        GROUP BY LOWER(first_name), LOWER(last_name), phone
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 10
    """)
    name_phone_dupes = cursor.fetchall()
    print(f"\nName + Phone duplicates: {len(name_phone_dupes)} groups")
    for fname, lname, phone, count, ids in name_phone_dupes:
        print(f"  {fname} {lname} {phone}: {count} copies")
    
    # Total contact count
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]
    print(f"\nTotal contacts: {total}")
    
    # Potential duplicate removal impact
    total_email_dupes = sum(count - 1 for _, count, _ in email_dupes)
    total_name_phone_dupes = sum(count - 1 for _, _, _, count, _ in name_phone_dupes)
    
    print(f"Potential removals:")
    print(f"  Email duplicates: {total_email_dupes}")
    print(f"  Name+Phone duplicates: {total_name_phone_dupes}")
    print(f"  Estimated final count: {total - max(total_email_dupes, total_name_phone_dupes)}")
    
    conn.close()

if __name__ == "__main__":
    analyze_duplicates()
