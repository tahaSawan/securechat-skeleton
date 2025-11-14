"""MySQL users table + salted hashing (no chat storage)."""

import pymysql
import os
import secrets
import hashlib
import sys
from typing import Optional, Tuple


def get_db_connection():
    """Get MySQL database connection."""
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'scuser'),
        password=os.getenv('DB_PASSWORD', 'scpass'),
        database=os.getenv('DB_NAME', 'securechat'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def init_database():
    """Initialize database and create users table."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email VARCHAR(255) NOT NULL,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    salt VARBINARY(16) NOT NULL,
                    pwd_hash CHAR(64) NOT NULL,
                    PRIMARY KEY (username),
                    INDEX idx_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()


def generate_salt() -> bytes:
    """Generate a random 16-byte salt."""
    return secrets.token_bytes(16)


def compute_password_hash(password: str, salt: bytes) -> str:
    """
    Compute salted password hash.
    pwd_hash = hex(SHA256(salt || password))
    """
    # Concatenate salt and password
    salted_password = salt + password.encode('utf-8')
    # Compute SHA-256 hash
    hash_value = hashlib.sha256(salted_password).digest()
    # Return as hexadecimal string (64 characters)
    return hash_value.hex()


def register_user(email: str, username: str, password: str) -> Tuple[bool, str]:
    """
    Register a new user with salted password hash.
    
    Args:
        email: User email
        username: Username (must be unique)
        password: Plain text password
    
    Returns:
        (success, error_message)
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check if username or email already exists
            cursor.execute(
                "SELECT username, email FROM users WHERE username = %s OR email = %s",
                (username, email)
            )
            existing = cursor.fetchone()
            if existing:
                if existing['username'] == username:
                    return False, "Username already exists"
                if existing['email'] == email:
                    return False, "Email already exists"
            
            # Generate salt
            salt = generate_salt()
            
            # Compute password hash
            pwd_hash = compute_password_hash(password, salt)
            
            # Insert user
            cursor.execute(
                "INSERT INTO users (email, username, salt, pwd_hash) VALUES (%s, %s, %s, %s)",
                (email, username, salt, pwd_hash)
            )
            conn.commit()
            return True, "User registered successfully"
    except Exception as e:
        conn.rollback()
        return False, f"Registration failed: {str(e)}"
    finally:
        conn.close()


def verify_user(email: str, password: str, salt: bytes) -> bool:
    """
    Verify user password using stored salt.
    
    Args:
        email: User email
        password: Plain text password
        salt: Salt bytes from database
    
    Returns:
        True if password matches, False otherwise
    """
    # Compute password hash with provided salt
    computed_hash = compute_password_hash(password, salt)
    return computed_hash


def get_user_by_email(email: str) -> Optional[dict]:
    """
    Get user by email.
    
    Args:
        email: User email
    
    Returns:
        User record with salt and pwd_hash, or None if not found
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT email, username, salt, pwd_hash FROM users WHERE email = %s",
                (email,)
            )
            return cursor.fetchone()
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> Tuple[bool, Optional[str]]:
    """
    Authenticate user by email and password.
    
    Args:
        email: User email
        password: Plain text password
    
    Returns:
        (is_authenticated, username_or_error_message)
    """
    user = get_user_by_email(email)
    if not user:
        return False, "User not found"
    
    # Get salt from database
    salt = user['salt']
    
    # Compute password hash
    computed_hash = compute_password_hash(password, salt)
    
    # Compare with stored hash (constant-time comparison to prevent timing attacks)
    stored_hash = user['pwd_hash']
    if constant_time_compare(computed_hash, stored_hash):
        return True, user['username']
    else:
        return False, "Invalid password"


def constant_time_compare(a: str, b: str) -> bool:
    """
    Constant-time string comparison to prevent timing attacks.
    
    Args:
        a: First string
        b: Second string
    
    Returns:
        True if strings are equal, False otherwise
    """
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


if __name__ == '__main__':
    # Allow initialization via command line
    if '--init' in sys.argv:
        init_database()
    else:
        print("Usage: python -m app.storage.db --init")
