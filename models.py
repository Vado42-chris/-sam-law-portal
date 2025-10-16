#!/usr/bin/env python3
"""
SAM LAW - Database Models
User authentication and case management models
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    User model for authentication
    
    Attributes:
        id: Primary key
        email: User's email (unique, required)
        password_hash: Bcrypt hashed password
        full_name: User's full name
        role: User role (client, lawyer, admin)
        created_at: Account creation timestamp
        last_login: Last login timestamp
        is_active: Account status
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='client')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    cases_as_client = db.relationship('Case', foreign_keys='Case.client_id', backref='client', lazy=True)
    cases_as_lawyer = db.relationship('Case', foreign_keys='Case.lawyer_id', backref='lawyer', lazy=True)
    
    def set_password(self, password):
        """
        Hash and set user password using bcrypt
        
        Args:
            password: Plain text password
        """
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """
        Verify password against stored hash
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def __repr__(self):
        return f'<User {self.email}>'


class Case(db.Model):
    """
    Legal case model
    
    Attributes:
        id: Primary key
        case_number: Unique case identifier (e.g., SAML-00001)
        case_name: Case title
        case_type: Type of case (e.g., Family Law - Separation)
        status: Current case status
        client_id: Foreign key to User
        lawyer_id: Foreign key to User (optional)
        created_at: Case creation timestamp
        updated_at: Last update timestamp
        description: Case description
        jurisdiction: Court jurisdiction
    """
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    case_name = db.Column(db.String(255), nullable=False)
    case_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Active')
    
    # Foreign keys
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lawyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Case details
    description = db.Column(db.Text)
    jurisdiction = db.Column(db.String(255))
    
    # Relationships
    documents = db.relationship('Document', backref='case', lazy=True, cascade='all, delete-orphan')
    timeline_events = db.relationship('TimelineEvent', backref='case', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='case', lazy=True, cascade='all, delete-orphan')
    
    @property
    def jurisdiction_dict(self):
        """Parse jurisdiction string into dict for template compatibility"""
        import json
        if self.jurisdiction:
            try:
                return json.loads(self.jurisdiction)
            except:
                # Fallback if jurisdiction is plain string
                return {
                    'court': self.jurisdiction,
                    'city': 'Toronto',
                    'province': 'ON'
                }
        return {
            'court': 'Ontario Superior Court',
            'city': 'Toronto',
            'province': 'ON'
        }
    
    @property
    def lawyer_dict(self):
        """Return lawyer info as dict for template compatibility"""
        if self.lawyer:
            return {
                'name': self.lawyer.full_name,
                'specialization': 'Family Law'
            }
        return {
            'name': 'Pending Assignment',
            'specialization': 'N/A'
        }
    
    def __repr__(self):
        return f'<Case {self.case_number}>'


class Document(db.Model):
    """
    Case document model
    
    Attributes:
        id: Primary key
        case_id: Foreign key to Case
        filename: Original filename
        file_path: Storage path
        file_size: File size in bytes
        file_type: MIME type
        uploaded_at: Upload timestamp
        uploaded_by: User ID who uploaded
        category: Document category
        ocr_status: OCR processing status
        ocr_text: Extracted text
    """
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(100))
    
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    category = db.Column(db.String(100))
    ocr_status = db.Column(db.String(50), default='pending')
    ocr_text = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Document {self.filename}>'


class TimelineEvent(db.Model):
    """
    Case timeline event model
    
    Attributes:
        id: Primary key
        case_id: Foreign key to Case
        title: Event title
        event_date: Event date
        event_type: Type of event (milestone, deadline, hearing, etc.)
        description: Event description
        status: Event status (upcoming, completed, missed)
        created_at: Creation timestamp
        created_by: User ID who created
    """
    __tablename__ = 'timeline_events'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.Date, nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='upcoming')
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<TimelineEvent {self.title}>'


class Note(db.Model):
    """
    Case note model
    
    Attributes:
        id: Primary key
        case_id: Foreign key to Case
        title: Note title
        content: Note content
        category: Note category
        created_at: Creation timestamp
        updated_at: Last update timestamp
        created_by: User ID who created
    """
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Note {self.title}>'

