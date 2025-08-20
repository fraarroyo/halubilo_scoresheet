#!/usr/bin/env python3
"""
Database Migration Script for Scoresheet Halubilo
Adds activity_id field to User model for activity-based user assignments
"""

import sqlite3
import os

def migrate_database():
    """Migrate the database to add activity_id field to users table"""
    
    db_path = 'scoresheet.db'
    
    if not os.path.exists(db_path):
        print("Database not found. Please run the main application first to create it.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if activity_id column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'activity_id' not in columns:
            print("Adding activity_id column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN activity_id INTEGER REFERENCES activity(id)")
            print("✅ Successfully added activity_id column")
        else:
            print("✅ activity_id column already exists")
        
        # Commit changes
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    migrate_database()
    print("✨ Migration script completed!")

