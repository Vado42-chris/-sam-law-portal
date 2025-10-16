#!/usr/bin/env python3
"""
SAM LAW - Database Initialization Script
Creates all tables and initializes database schema
"""

from app import app
from models import db, User, Case, Document, TimelineEvent, Note
from datetime import datetime, date

def init_database():
    """Initialize database with tables"""
    with app.app_context():
        print("=" * 60)
        print("SAM LAW - Database Initialization")
        print("=" * 60)
        
        # Drop all tables (fresh start)
        print("\n1. Dropping existing tables...")
        db.drop_all()
        print("   ✅ All tables dropped")
        
        # Create all tables
        print("\n2. Creating new tables...")
        db.create_all()
        print("   ✅ Users table created")
        print("   ✅ Cases table created")
        print("   ✅ Documents table created")
        print("   ✅ Timeline Events table created")
        print("   ✅ Notes table created")
        
        print("\n" + "=" * 60)
        print("Database initialization complete!")
        print("=" * 60)
        
        return True

if __name__ == '__main__':
    try:
        init_database()
        print("\n✅ SUCCESS: Database ready for use")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise

