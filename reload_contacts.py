import sqlite3
import requests

def clear_and_reload_contacts():
    print("=== CLEARING AND RELOADING CONTACTS TABLE ===")
    
    # Connect to local database
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    
    # Clear the contacts table
    print("1. Clearing local contacts table...")
    cursor.execute("DELETE FROM contacts")
    deleted_count = cursor.rowcount
    print(f"   Deleted {deleted_count} existing contacts")
    
    conn.commit()
    
    print("2. Fetching contacts from Supabase...")
    
    # Supabase configuration
    SUPABASE_URL = "https://yggfiuqxfxsoyesqgpyt.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q"
    
    # Fetch all contacts from Supabase
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/contacts?select=*",
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Supabase API error: {response.status_code} - {response.text}")
        
        supabase_contacts = response.json()
        print(f"   Fetched {len(supabase_contacts)} contacts from Supabase")
        
        if len(supabase_contacts) == 0:
            print("   No contacts found in Supabase")
            conn.close()
            return
        
        print("3. Inserting contacts into local database...")
        
        # Insert contacts into local database
        insert_query = """
            INSERT INTO contacts (
                id, sms, call, email_flag, assignee, assigned_to, sponsor, sponsor_first, sponsor_last,
                user_id, first_name, last_name, email, valid, phone, address, city, state, zip,
                ip_address, date_created, timezone, source, campaign, lead_type, status, notes,
                last_contact, next_followup, priority, tags, custom_fields, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        inserted_count = 0
        for contact in supabase_contacts:
            try:
                cursor.execute(insert_query, (
                    contact.get('id'),
                    contact.get('sms'),
                    contact.get('call'),
                    contact.get('email_flag'),
                    contact.get('assignee'),
                    contact.get('assigned_to'),
                    contact.get('sponsor'),
                    contact.get('sponsor_first'),
                    contact.get('sponsor_last'),
                    contact.get('user_id'),
                    contact.get('first_name'),
                    contact.get('last_name'),
                    contact.get('email'),
                    contact.get('valid'),
                    contact.get('phone'),
                    contact.get('address'),
                    contact.get('city'),
                    contact.get('state'),
                    contact.get('zip'),
                    contact.get('ip_address'),
                    contact.get('date_created'),
                    contact.get('timezone'),
                    contact.get('source'),
                    contact.get('campaign'),
                    contact.get('lead_type'),
                    contact.get('status'),
                    contact.get('notes'),
                    contact.get('last_contact'),
                    contact.get('next_followup'),
                    contact.get('priority'),
                    contact.get('tags'),
                    contact.get('custom_fields'),
                    contact.get('created_at'),
                    contact.get('updated_at')
                ))
                inserted_count += 1
            except Exception as e:
                print(f"   Error inserting contact {contact.get('id', 'unknown')}: {e}")
        
        conn.commit()
        print(f"   Successfully inserted {inserted_count} contacts")
        
        print("4. Verifying data...")
        cursor.execute("SELECT COUNT(*) FROM contacts")
        total_contacts = cursor.fetchone()[0]
        print(f"   Total contacts in local database: {total_contacts}")
        
        # Show assignment distribution
        cursor.execute("""
            SELECT assigned_to, COUNT(*) as count
            FROM contacts 
            WHERE assigned_to IS NOT NULL
            GROUP BY assigned_to
            ORDER BY count DESC
        """)
        assignments = cursor.fetchall()
        
        if assignments:
            print("   Assignment distribution:")
            for assigned_to, count in assignments:
                print(f"     {assigned_to}: {count} contacts")
        
        print("✅ CONTACTS TABLE SUCCESSFULLY RELOADED FROM SUPABASE!")
        
    except Exception as e:
        print(f"❌ Error fetching from Supabase: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    clear_and_reload_contacts()
