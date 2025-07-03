#!/usr/bin/env python3
"""
Database migration script to add role-based assignment features
"""

import sqlite3
import uuid

DB_FILE = 'contacts.db'

def migrate_database():
    """Add new tables and columns for role-based assignments"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        print("🔄 Starting database migration...")
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("📋 Creating users table...")
            cursor.execute('''
                CREATE TABLE users (
                    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                    email TEXT UNIQUE NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    role TEXT CHECK(role IN ('user', 'manager', 'supervisor', 'admin')) DEFAULT 'user',
                    manager_id TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (manager_id) REFERENCES users (id)
                )
            ''')
            
            # Create indexes for users table
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_manager ON users(manager_id)')
            
            print("✅ Users table created")
        else:
            print("✅ Users table already exists")
        
        # Check if assigned_to column exists in contacts table
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'assigned_to' not in columns:
            print("📋 Adding assigned_to column to contacts table...")
            cursor.execute('ALTER TABLE contacts ADD COLUMN assigned_to TEXT')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_assigned_to ON contacts(assigned_to)')
            print("✅ Added assigned_to column")
        else:
            print("✅ assigned_to column already exists")
        
        # Create default admin user if none exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("📋 Creating default admin user...")
            admin_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO users (id, email, first_name, last_name, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (admin_id, 'admin@sparky.com', 'Admin', 'User', 'admin', 1))
            print("✅ Created default admin user: admin@sparky.com")
        else:
            print("✅ Admin user already exists")
        
        conn.commit()
        print("🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
