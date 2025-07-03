import sqlite3

conn = sqlite3.connect('contacts.db')
cursor = conn.cursor()

# Check current setup
print("Current manager-user relationships:")
cursor.execute("SELECT id, email, first_name, last_name, role, manager_id FROM users WHERE role IN ('user', 'manager')")
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]} | {row[2]} {row[3]} | Role: {row[4]} | Manager: {row[5]}")

# Set John User to report to John Manager
cursor.execute("""
    UPDATE users 
    SET manager_id = 'user-manager-example-com' 
    WHERE id = 'user-john+2-tpnlife-com'
""")

print(f"\nUpdated {cursor.rowcount} user(s)")

# Verify the relationship
print("\nAfter update:")
cursor.execute("SELECT id, email, first_name, last_name, role, manager_id FROM users WHERE role IN ('user', 'manager')")
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]} | {row[2]} {row[3]} | Role: {row[4]} | Manager: {row[5]}")

conn.commit()
conn.close()
