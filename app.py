#!/usr/bin/env python3
"""
SAM LAW - Legal Case Management Module
Built on S10 Command Center Foundation
For: Chris Hallberg Legal Case (SAML-00001)
Date: October 14, 2025
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from dotenv import load_dotenv
import json
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sam-law-fallback-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///sam_law.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from models import db, User, Case, Document, TimelineEvent, Note
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))

# Data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize data files
CASE_FILE = os.path.join(DATA_DIR, 'case_data.json')
DOCUMENTS_FILE = os.path.join(DATA_DIR, 'documents.json')
TIMELINE_FILE = os.path.join(DATA_DIR, 'timeline.json')
NOTES_FILE = os.path.join(DATA_DIR, 'notes.json')

def init_data():
    """Initialize data files with default data"""
    if not os.path.exists(CASE_FILE):
        case_data = {
            "case_name": "Hallberg Separation",
            "case_number": "SAML-00001",
            "client_name": "Chris Hallberg",
            "case_type": "Family Law - Separation",
            "status": "Preparing for Legal Aid",
            "last_updated": datetime.now().isoformat()
        }
        with open(CASE_FILE, 'w') as f:
            json.dump(case_data, f, indent=2)
    
    if not os.path.exists(DOCUMENTS_FILE):
        documents = []
        with open(DOCUMENTS_FILE, 'w') as f:
            json.dump(documents, f, indent=2)
    
    if not os.path.exists(TIMELINE_FILE):
        timeline = [
            {
                "id": "event-001",
                "title": "Legal Aid Application Deadline",
                "date": "2025-10-25",
                "type": "deadline",
                "description": "Deadline to submit Legal Aid application with all supporting documentation",
                "status": "upcoming"
            },
            {
                "id": "event-002",
                "title": "Separation Date",
                "date": "2024-06-15",
                "type": "milestone",
                "description": "Official separation date - documented",
                "status": "completed"
            }
        ]
        with open(TIMELINE_FILE, 'w') as f:
            json.dump(timeline, f, indent=2)
    
    if not os.path.exists(NOTES_FILE):
        notes = [
            {
                "id": "note-001",
                "title": "Questions for Lawyer",
                "content": "1. Custody arrangements for Joshua\n2. Asset division process\n3. Timeline expectations",
                "created": datetime.now().isoformat(),
                "category": "preparation"
            }
        ]
        with open(NOTES_FILE, 'w') as f:
            json.dump(notes, f, indent=2)

init_data()

# Routes
# =============================================================================
# HEALTH & MONITORING
# =============================================================================

@app.route('/health')
def health():
    """Health check endpoint for Render monitoring"""
    try:
        # Check database connection
        with app.app_context():
            User.query.first()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=bool(remember))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

# =============================================================================
# APPLICATION ROUTES
# =============================================================================

@app.route('/')
@login_required
def dashboard():
    """Main dashboard - case overview"""
    # Get current user's case
    case = Case.query.filter_by(client_id=current_user.id).first()
    
    if not case:
        flash('No case found for your account. Please contact support.', 'error')
        return render_template('dashboard.html',
                             case=None,
                             case_info=None,
                             document_count=0,
                             timeline_count=0,
                             notes_count=0)
    
    # Get related data from database
    documents = Document.query.filter_by(case_id=case.id).all()
    timeline = TimelineEvent.query.filter_by(case_id=case.id).order_by(TimelineEvent.event_date.desc()).all()
    notes = Note.query.filter_by(case_id=case.id).order_by(Note.created_at.desc()).all()
    
    return render_template('dashboard.html',
                         case=case,
                         case_info=case,
                         document_count=len(documents),
                         timeline_count=len([e for e in timeline if e.status == 'upcoming']),
                         notes_count=len(notes))

@app.route('/documents')
@login_required
def documents():
    """Document management page"""
    case = Case.query.filter_by(client_id=current_user.id).first()
    if not case:
        flash('No case found', 'error')
        return redirect(url_for('dashboard'))
    
    docs = Document.query.filter_by(case_id=case.id).order_by(Document.uploaded_at.desc()).all()
    return render_template('documents.html', documents=docs)

@app.route('/timeline')
@login_required
def timeline():
    """Timeline and important dates"""
    case = Case.query.filter_by(client_id=current_user.id).first()
    if not case:
        flash('No case found', 'error')
        return redirect(url_for('dashboard'))
    
    events = TimelineEvent.query.filter_by(case_id=case.id).order_by(TimelineEvent.event_date).all()
    return render_template('timeline.html', events=events)

@app.route('/notes')
@login_required
def notes():
    """Notes and preparation"""
    case = Case.query.filter_by(client_id=current_user.id).first()
    if not case:
        flash('No case found', 'error')
        return redirect(url_for('dashboard'))
    
    all_notes = Note.query.filter_by(case_id=case.id).order_by(Note.created_at.desc()).all()
    return render_template('notes.html', notes=all_notes)

@app.route('/settings')
@login_required
def settings():
    """Settings and preferences"""
    case = Case.query.filter_by(client_id=current_user.id).first()
    return render_template('settings.html', case=case, user=current_user)

# API Endpoints
@app.route('/api/documents/upload', methods=['POST'])
@login_required
def upload_document():
    """Upload a new document"""
    data = request.get_json()
    case = Case.query.filter_by(client_id=current_user.id).first()
    
    if not case:
        return jsonify({"success": False, "error": "No case found"}), 404
    
    new_doc = Document(
        case_id=case.id,
        filename=data.get('name'),
        document_type=data.get('type', 'other'),
        description=data.get('description', ''),
        uploaded_by=current_user.id
    )
    
    db.session.add(new_doc)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "document": {
            "id": new_doc.id,
            "name": new_doc.filename,
            "type": new_doc.document_type,
            "uploaded": new_doc.uploaded_at.isoformat()
        }
    })

@app.route('/api/timeline/add', methods=['POST'])
@login_required
def add_timeline_event():
    """Add a new timeline event"""
    data = request.get_json()
    case = Case.query.filter_by(client_id=current_user.id).first()
    
    if not case:
        return jsonify({"success": False, "error": "No case found"}), 404
    
    from datetime import datetime as dt
    new_event = TimelineEvent(
        case_id=case.id,
        title=data.get('title'),
        event_date=dt.strptime(data.get('date'), '%Y-%m-%d').date(),
        event_type=data.get('type', 'milestone'),
        description=data.get('description', ''),
        status='upcoming',
        created_by=current_user.id
    )
    
    db.session.add(new_event)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "event": {
            "id": new_event.id,
            "title": new_event.title,
            "date": new_event.event_date.isoformat(),
            "status": new_event.status
        }
    })

@app.route('/api/notes/create', methods=['POST'])
@login_required
def create_note():
    """Create a new note"""
    data = request.get_json()
    case = Case.query.filter_by(client_id=current_user.id).first()
    
    if not case:
        return jsonify({"success": False, "error": "No case found"}), 404
    
    new_note = Note(
        case_id=case.id,
        title=data.get('title'),
        content=data.get('content', ''),
        category=data.get('category', 'general'),
        created_by=current_user.id
    )
    
    db.session.add(new_note)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "note": {
            "id": new_note.id,
            "title": new_note.title,
            "created": new_note.created_at.isoformat(),
            "category": new_note.category
        }
    })

# ============================================================
# NEW NAVIGATION PAGES - ADDED ONE AT A TIME, TESTED EACH
# ============================================================

@app.route('/files')
def files():
    """Quick Files - Universal file server"""
    with open(CASE_FILE, 'r') as f:
        case_data = json.load(f)
    return render_template('files.html', case_info=case_data)

@app.route('/email')
def email():
    """Email Inbox"""
    with open(CASE_FILE, 'r') as f:
        case_data = json.load(f)
    return render_template('email.html', case_info=case_data)

@app.route('/notifications')
def notifications():
    """Notifications Center"""
    with open(CASE_FILE, 'r') as f:
        case_data = json.load(f)
    return render_template('notifications.html', case_info=case_data)

@app.route('/direct-messages')
def direct_messages():
    """Direct Messages"""
    with open(CASE_FILE, 'r') as f:
        case_data = json.load(f)
    return render_template('direct_messages.html', case_info=case_data)

@app.route('/messages')
@login_required
def messages():
    """Messages Aggregate View"""
    case = Case.query.first()
    return render_template('messages.html', case_info=case)

@app.route('/calendar')
@login_required
def calendar():
    """Calendar View"""
    case = Case.query.first()
    events = TimelineEvent.query.order_by(TimelineEvent.event_date.desc()).all()
    return render_template('calendar.html', case_info=case, events=events)

@app.route('/help')
@login_required
def help_page():
    """Help & Support"""
    case = Case.query.first()
    return render_template('help.html', case_info=case)

@app.route('/my-lawyers')
@login_required
def my_lawyers():
    """My Lawyers"""
    case = Case.query.first()
    return render_template('my_lawyers.html', case_info=case)

@app.route('/case-studies')
def case_studies():
    """Case Studies"""
    with open(CASE_FILE, 'r') as f:
        case_data = json.load(f)
    return render_template('case_studies.html', case_info=case_data)

@app.route('/billing')
def billing():
    """Billing (all cases)"""
    with open(CASE_FILE, 'r') as f:
        case_data = json.load(f)
    return render_template('billing.html', case_info=case_data)

@app.route('/legal-strategy')
@app.route('/strategy')
@login_required
def legal_strategy():
    """Legal Strategy (case-specific)"""
    with open(CASE_FILE, 'r') as f:
        case_data = json.load(f)
    return render_template('legal_strategy.html', case_info=case_data)

@app.route('/case-billing')
def case_billing():
    """Case Billing (case-specific)"""
    with open(CASE_FILE, 'r') as f:
        case_data = json.load(f)
    return render_template('case_billing.html', case_info=case_data)

@app.route('/case-details')
def case_details():
    """Case Details"""
    with open(CASE_FILE, 'r') as f:
        case_data = json.load(f)
    return render_template('case_details.html', case_info=case_data)

@app.route('/communications')
def communications():
    """Communications"""
    with open(CASE_FILE, 'r') as f:
        case_data = json.load(f)
    return render_template('communications.html', case=case_data)

@app.route('/conversations')
def conversations():
    """AI Legal Counsel"""
    with open(CASE_FILE, 'r') as f:
        case_data = json.load(f)
    return render_template('conversations.html', case_info=case_data)

@app.route('/my-cases')
@login_required
def my_cases():
    """My Cases"""
    case = Case.query.first()
    
    # Calculate days active
    from datetime import datetime
    days_active = (datetime.now() - case.created_at).days if case else 0
    
    # Get upcoming deadlines from timeline
    upcoming_deadlines = TimelineEvent.query.filter(
        TimelineEvent.event_type == 'deadline',
        TimelineEvent.event_date >= datetime.now().date()
    ).order_by(TimelineEvent.event_date.asc()).limit(3).all()
    
    # Format for template
    deadline_list = []
    for event in upcoming_deadlines:
        days_until = (event.event_date - datetime.now().date()).days if event.event_date else 0
        deadline_list.append({
            'title': event.title,
            'date': event.event_date.strftime('%Y-%m-%d') if event.event_date else 'TBD',
            'days_until': days_until
        })
    
    return render_template('my_cases.html', case_info=case, days_active=days_active, upcoming_deadlines=deadline_list)

if __name__ == '__main__':
    print("=" * 60)
    print("SAM LAW - Legal Case Management")
    print("=" * 60)
    print(f"Starting server on http://localhost:5601")
    print(f"For Chris Hallberg - Case: SAML-00001")
    print("=" * 60)
    port = int(os.environ.get('PORT', 5601))
    app.run(host='0.0.0.0', port=port, debug=False)

