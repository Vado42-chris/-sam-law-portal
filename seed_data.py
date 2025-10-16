#!/usr/bin/env python3
"""
SAM LAW - Seed Data Script
Populates database with Chris Hallberg's case data
"""

from app import app
from models import db, User, Case, Document, TimelineEvent, Note
from datetime import datetime, date

def seed_database():
    """Seed database with Chris Hallberg's case"""
    with app.app_context():
        print("=" * 60)
        print("SAM LAW - Seeding Database with Real Case Data")
        print("=" * 60)
        
        # Create Chris Hallberg (client)
        print("\n1. Creating client user...")
        chris = User(
            email='chris@xibalba.io',
            full_name='Chris Hallberg',
            role='client',
            is_active=True
        )
        chris.set_password('secure123')  # Will be changed to real auth
        db.session.add(chris)
        db.session.flush()  # Get chris.id
        print(f"   ✅ Created client: {chris.full_name} (ID: {chris.id})")
        
        # Create Emma Rodriguez (lawyer)
        print("\n2. Creating lawyer user...")
        emma = User(
            email='emma.rodriguez@samlaw.io',
            full_name='Emma Rodriguez',
            role='lawyer',
            is_active=True
        )
        emma.set_password('lawyer123')
        db.session.add(emma)
        db.session.flush()  # Get emma.id
        print(f"   ✅ Created lawyer: {emma.full_name} (ID: {emma.id})")
        
        # Create Chris's case
        print("\n3. Creating legal case...")
        case = Case(
            case_number='SAML-00001',
            case_name='Hallberg Separation',
            case_type='Family Law - Separation',
            status='Preparing for Legal Aid',
            client_id=chris.id,
            lawyer_id=emma.id,
            description='Separation case requiring Legal Aid application. Separated June 15, 2024.',
            jurisdiction='Ontario Superior Court, Toronto, ON'
        )
        db.session.add(case)
        db.session.flush()  # Get case.id
        print(f"   ✅ Created case: {case.case_number} - {case.case_name}")
        
        # Create timeline events
        print("\n4. Creating timeline events...")
        events = [
            TimelineEvent(
                case_id=case.id,
                title='Legal Aid Application Deadline',
                event_date=date(2025, 10, 25),
                event_type='deadline',
                description='Deadline to submit Legal Aid application with all supporting documentation',
                status='upcoming',
                created_by=chris.id
            ),
            TimelineEvent(
                case_id=case.id,
                title='Separation Date',
                event_date=date(2024, 6, 15),
                event_type='milestone',
                description='Official separation date - documented',
                status='completed',
                created_by=chris.id
            ),
            TimelineEvent(
                case_id=case.id,
                title='Initial Consultation with Emma',
                event_date=date(2025, 10, 1),
                event_type='meeting',
                description='First meeting with lawyer to discuss case strategy',
                status='completed',
                created_by=emma.id
            )
        ]
        for event in events:
            db.session.add(event)
        print(f"   ✅ Created {len(events)} timeline events")
        
        # Create notes
        print("\n5. Creating case notes...")
        notes = [
            Note(
                case_id=case.id,
                title='Questions for Lawyer',
                content='1. Custody arrangements for Joshua\n2. Asset division process\n3. Timeline expectations\n4. Legal Aid application requirements',
                category='preparation',
                created_by=chris.id
            ),
            Note(
                case_id=case.id,
                title='Legal Aid Requirements',
                content='Need to gather:\n- Proof of income (last 3 months)\n- Bank statements\n- Documentation of separation\n- List of assets and debts',
                category='legal-aid',
                created_by=chris.id
            ),
            Note(
                case_id=case.id,
                title='Case Strategy Notes',
                content='Focus on:\n1. Documenting separation timeline\n2. Establishing custody arrangements\n3. Fair asset division\n4. Maintaining communication for Joshua',
                category='strategy',
                created_by=emma.id
            )
        ]
        for note in notes:
            db.session.add(note)
        print(f"   ✅ Created {len(notes)} case notes")
        
        # Commit all changes
        print("\n6. Committing all data to database...")
        db.session.commit()
        print("   ✅ All data committed successfully")
        
        print("\n" + "=" * 60)
        print("Database seeding complete!")
        print("=" * 60)
        print(f"\nCreated:")
        print(f"  - 2 users (1 client, 1 lawyer)")
        print(f"  - 1 legal case (SAML-00001)")
        print(f"  - {len(events)} timeline events")
        print(f"  - {len(notes)} case notes")
        print(f"\nLogin Credentials:")
        print(f"  Client: chris@xibalba.io / secure123")
        print(f"  Lawyer: emma.rodriguez@samlaw.io / lawyer123")
        
        return True

if __name__ == '__main__':
    try:
        seed_database()
        print("\n✅ SUCCESS: Database seeded with real case data")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise

