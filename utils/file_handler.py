"""
SAM Law - File Upload Handler
Built by Samuel Alfred Hallberg
Date: October 14, 2025, 3:42 PM

Handles file uploads, validation, storage, and metadata tracking.
"""

import os
import uuid
import hashlib
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'txt': 'text/plain'
}

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_hash(file_path):
    """Generate SHA256 hash of file for deduplication"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_file_size(file_path):
    """Get file size in bytes"""
    return os.path.getsize(file_path)

def save_uploaded_file(file, case_id='SAML-00001', uploaded_by='Chris Hallberg'):
    """
    Save uploaded file and return metadata
    
    Args:
        file: FileStorage object from Flask
        case_id: Case number
        uploaded_by: User name
        
    Returns:
        dict: File metadata including path, hash, size, etc.
    """
    if not file:
        return {'success': False, 'error': 'No file provided'}
    
    if not allowed_file(file.filename):
        return {'success': False, 'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS.keys())}'}
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    file_ext = original_filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())
    stored_filename = f"{unique_id}.{file_ext}"
    
    # Create case-specific directory
    case_upload_dir = os.path.join(UPLOAD_FOLDER, case_id)
    os.makedirs(case_upload_dir, exist_ok=True)
    
    file_path = os.path.join(case_upload_dir, stored_filename)
    
    # Save file
    try:
        file.save(file_path)
    except Exception as e:
        return {'success': False, 'error': f'Failed to save file: {str(e)}'}
    
    # Get file info
    file_size = get_file_size(file_path)
    file_hash = get_file_hash(file_path)
    
    # Check file size
    if file_size > MAX_FILE_SIZE:
        os.remove(file_path)
        return {'success': False, 'error': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB'}
    
    # Detect MIME type
    mime_type = mimetypes.guess_type(original_filename)[0] or ALLOWED_EXTENSIONS.get(file_ext)
    
    # Build metadata
    metadata = {
        'success': True,
        'document_id': unique_id,
        'original_filename': original_filename,
        'stored_filename': stored_filename,
        'file_path': file_path,
        'file_size': file_size,
        'file_size_mb': round(file_size / (1024*1024), 2),
        'file_hash': file_hash,
        'file_type': file_ext,
        'mime_type': mime_type,
        'case_id': case_id,
        'uploaded_by': uploaded_by,
        'uploaded_at': datetime.now().isoformat(),
        'ocr_status': 'pending',  # Will be processed later
        'tags': [],
        'version': 1
    }
    
    return metadata

def get_file_path(document_id, case_id='SAML-00001'):
    """Get file path from document ID"""
    case_upload_dir = os.path.join(UPLOAD_FOLDER, case_id)
    
    # Search for file with this document ID
    if os.path.exists(case_upload_dir):
        for filename in os.listdir(case_upload_dir):
            if filename.startswith(document_id):
                return os.path.join(case_upload_dir, filename)
    
    return None

def delete_file(document_id, case_id='SAML-00001'):
    """Delete file by document ID"""
    file_path = get_file_path(document_id, case_id)
    
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            return {'success': True, 'message': 'File deleted'}
        except Exception as e:
            return {'success': False, 'error': f'Failed to delete file: {str(e)}'}
    
    return {'success': False, 'error': 'File not found'}

def list_uploaded_files(case_id='SAML-00001'):
    """List all files for a case"""
    case_upload_dir = os.path.join(UPLOAD_FOLDER, case_id)
    
    if not os.path.exists(case_upload_dir):
        return []
    
    files = []
    for filename in os.listdir(case_upload_dir):
        file_path = os.path.join(case_upload_dir, filename)
        if os.path.isfile(file_path):
            files.append({
                'filename': filename,
                'path': file_path,
                'size': get_file_size(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            })
    
    return files

