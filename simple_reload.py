import sqlite3
import requests

def simple_reload():
    print("=== SIMPLE CONTACT RELOAD ===")
    
    # Connect to database
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    
    # Get actual table schema
    cursor.execute('PRAGMA table_info(contacts)')
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"Local table has {len(column_names)} columns: {column_names[:10]}...")
    
    # Clear existing data
    cursor.execute("DELETE FROM contacts")
    print(f"Cleared {cursor.rowcount} existing contacts")
    
    # Fetch from Supabase
    SUPABASE_URL = "https://yggfiuqxfxsoyesqgpyt.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q"
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{SUPABASE_URL}/rest/v1/contacts?select=*", headers=headers)
    contacts = response.json()
    print(f"Fetched {len(contacts)} contacts from Supabase")
    
    if not contacts:
        print("No contacts to import")
        conn.close()
        return
    
    # Check what fields the first contact has
    sample_contact = contacts[0]
    print(f"Sample contact fields: {list(sample_contact.keys())[:10]}...")
    
    # Only map fields that exist in BOTH local table AND Supabase data
    common_fields = []
    for field in sample_contact.keys():
        if field in column_names:
            common_fields.append(field)
    
    print(f"Common fields to map: {common_fields}")
    
    # Build dynamic INSERT query
    placeholders = ', '.join(['?' for _ in common_fields])
    query = f"INSERT INTO contacts ({', '.join(common_fields)}) VALUES ({placeholders})"
    
    # Insert contacts
    inserted = 0
    for contact in contacts:
        try:
            values = [contact.get(field) for field in common_fields]
            cursor.execute(query, values)
            inserted += 1
        except Exception as e:
            print(f"Error inserting contact: {e}")
            break
    
    conn.commit()
    print(f"Successfully inserted {inserted} contacts")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]
    print(f"Total contacts in database: {total}")
    
    conn.close()
    print("✅ DONE!")

if __name__ == "__main__":
    simple_reload()
