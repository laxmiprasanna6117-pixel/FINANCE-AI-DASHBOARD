"""
User Authentication, Registration & Profile Management System
Handles user registration, login, profile persistence, and user-specific datasets.
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
        "prasad@fda.finance": {
            "id": "usr_001",
            "name": "Prasad",
            "email": "prasad@fda.finance",
            "password_hash": hash_password("admin123"),
            "organization": "FDA Global Health & Finance",
            "role": "Chief Financial Officer (CFO)",
            "avatar_color": "#3B82F6",
            "created_at": "2026-01-15T09:00:00",
            "uploaded_files": []
        },
        "analyst@fda.finance": {
            "id": "usr_002",
            "name": "Alex Morgan",
            "email": "analyst@fda.finance",
            "password_hash": hash_password("analyst123"),
            "organization": "FDA Financial Intelligence",
            "role": "Senior Financial Analyst",
            "avatar_color": "#10B981",
            "created_at": "2026-02-01T10:30:00",
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
        return False, f"Account with email '{email_clean}' already exists. Please log in."
        
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

def authenticate_user(email, password):
    users = load_users()
    email_clean = email.strip().lower()
    if email_clean not in users:
        return False, "Account not found. Please register a new account."
    user = users[email_clean]
    if user["password_hash"] == hash_password(password):
        return True, user
    return False, "Incorrect password. Please try again."

def add_user_uploaded_file(email, file_name, file_path, row_count, col_count):
    users = load_users()
    email_clean = email.strip().lower()
    if email_clean in users:
        file_meta = {
            "file_name": file_name,
            "file_path": file_path,
            "uploaded_at": datetime.now().isoformat(),
            "row_count": row_count,
            "col_count": col_count
        }
        # Prepend to list
        users[email_clean]["uploaded_files"].insert(0, file_meta)
        save_users(users)
        return True
    return False

def get_user_workspace_dir(user_id):
    ensure_dirs()
    user_dir = os.path.join(UPLOADS_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir
