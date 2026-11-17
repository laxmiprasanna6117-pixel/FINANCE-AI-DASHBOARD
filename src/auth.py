"""
User Authentication, Registration & Profile Management System
Handles secure user registration, password verification, profile persistence, and data isolation.
"""

import os
import json
import hashlib
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
UPLOADS_DIR = os.path.join(DATA_DIR, "user_uploads")

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_default_users():
    return {
        "analyst@fda.finance": {
            "id": "usr_002",
            "name": "Alex Morgan",
            "email": "analyst@fda.finance",
            "password_hash": hash_password("analyst123"),
            "organization": "FDA Financial Intelligence",
            "role": "Senior Financial Analyst",
            "avatar_color": "#10A37F",
            "created_at": "2026-02-01T10:30:00",
            "uploaded_files": []
        },
        "executive@fda.finance": {
            "id": "usr_004",
            "name": "Jordan Hayes",
            "email": "executive@fda.finance",
            "password_hash": hash_password("admin123"),
            "organization": "FDA Global Health & Finance",
            "role": "VP of Finance & Strategy",
            "avatar_color": "#06B6D4",
            "created_at": "2026-02-15T09:00:00",
            "uploaded_files": []
        }
    }

def load_users():
    ensure_dirs()
    if not os.path.exists(USERS_FILE):
        users = get_default_users()
        save_users(users)
        return users
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        users = get_default_users()
        save_users(users)
        return users

def save_users(users):
    ensure_dirs()
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def register_user(name, email, password, organization, role="Financial Analyst"):
    ensure_dirs()
    users = load_users()
    email_clean = email.strip().lower()
    
    if not name.strip():
        return False, "Full Name is required."
    if not email_clean or "@" not in email_clean:
        return False, "A valid email address is required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters long."
    if email_clean in users:
        return False, f"An account with email '{email_clean}' already exists. Please log in with your password."
        
    colors = ["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#06B6D4"]
    avatar_color = colors[len(users) % len(colors)]
    user_id = f"usr_{len(users)+1:03d}"
    
    user_profile = {
        "id": user_id,
        "name": name.strip(),
        "email": email_clean,
        "password_hash": hash_password(password),
        "organization": organization.strip() if organization.strip() else "Enterprise Organization",
        "role": role,
        "avatar_color": avatar_color,
        "created_at": datetime.now().isoformat(),
        "uploaded_files": []
    }
    
    users[email_clean] = user_profile
    save_users(users)
    return True, user_profile

def authenticate_user(identifier, password):
    """
    Authenticate user by email or full name, and verify password hash.
    """
    if not identifier or not identifier.strip():
        return False, "Please enter your Email or Username."
    if not password:
        return False, "Please enter your Password."
        
    users = load_users()
    ident_clean = identifier.strip().lower()
    target_user = None
    
    for email, user in users.items():
        if email.lower() == ident_clean or user.get("name", "").strip().lower() == ident_clean:
            target_user = user
            break
            
    if not target_user:
        return False, "Account not found. Please check your email/username or register a new account."
        
    if target_user["password_hash"] == hash_password(password):
        return True, target_user
        
    return False, "Incorrect password. Please verify and try again."

def add_user_uploaded_file(email, file_name, file_path, row_count, col_count):
    """
    Registers an uploaded file metadata exclusively to the specific user's account.
    """
    users = load_users()
    email_clean = email.strip().lower()
    if email_clean in users:
        file_meta = {
            "file_name": file_name,
            "file_path": file_path,
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "row_count": row_count,
            "col_count": col_count
        }
        # Prepend to user's private list (avoid duplicates with same name)
        user_files = [f for f in users[email_clean].get("uploaded_files", []) if f["file_name"] != file_name]
        user_files.insert(0, file_meta)
        users[email_clean]["uploaded_files"] = user_files
        save_users(users)
        return True
    return False

def get_user_workspace_dir(user_id):
    """
    Returns the isolated filesystem directory path for a specific user's files.
    """
    ensure_dirs()
    user_dir = os.path.join(UPLOADS_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir
