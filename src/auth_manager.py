import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "users.db")

class AuthManager:
    """
    User Authentication and Registration Manager.
    Uses SQLite database with secure PBKDF2/scrypt password hashing via Werkzeug.
    Generic and privacy-first (no fictional identities or hardcoded personal profiles).
    """

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes the database schema and creates a default admin user if none exists."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    created_at TEXT NOT NULL,
                    last_login TEXT
                )
            """)
            conn.commit()

            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            if count == 0:
                default_username = "admin"
                default_password = "admin123"
                p_hash = generate_password_hash(default_password)
                now_str = datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, full_name, created_at)
                    VALUES (?, ?, ?, ?)
                """, (default_username, p_hash, "Administrator", now_str))
                conn.commit()
        finally:
            conn.close()

    def register_user(self, username, password, full_name=None):
        """
        Registers a new user account.
        Returns: (success: bool, message: str, user_dict: dict)
        """
        username = str(username).strip().lower()
        if not username:
            return False, "Username is required.", None

        if len(username) < 3:
            return False, "Username must be at least 3 characters long.", None

        if not username.replace("_", "").replace(".", "").isalnum():
            return False, "Username can only contain alphanumeric characters, dots, and underscores.", None

        if not password or len(str(password)) < 6:
            return False, "Password must be at least 6 characters long.", None

        display_name = str(full_name).strip() if full_name else username.capitalize()
        p_hash = generate_password_hash(password)
        now_str = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, created_at, last_login)
                VALUES (?, ?, ?, ?, ?)
            """, (username, p_hash, display_name, now_str, now_str))
            conn.commit()
            user_id = cursor.lastrowid

            return True, "Account registered successfully.", {
                "id": user_id,
                "username": username,
                "full_name": display_name,
                "created_at": now_str
            }
        except sqlite3.IntegrityError:
            return False, f"Username '{username}' is already taken. Please choose another.", None
        except Exception as e:
            return False, f"Database error: {str(e)}", None
        finally:
            conn.close()

    def verify_user(self, username, password):
        """
        Authenticates a user by username and password.
        Returns: (success: bool, message: str, user_dict: dict)
        """
        username = str(username).strip().lower()
        if not username or not password:
            return False, "Username and password are required.", None

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if not user:
                return False, "Invalid username or password.", None

            if not check_password_hash(user["password_hash"], password):
                return False, "Invalid username or password.", None

            now_str = datetime.now().isoformat()
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (now_str, user["id"]))
            conn.commit()

            return True, "Authentication successful.", {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "created_at": user["created_at"],
                "last_login": now_str
            }
        finally:
            conn.close()

    def get_user_by_id(self, user_id):
        """Fetches a user profile by ID without password hash."""
        if not user_id:
            return None

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, full_name, created_at, last_login FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user:
                return dict(user)
            return None
        finally:
            conn.close()
