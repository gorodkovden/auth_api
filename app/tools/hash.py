"""
Password Hashing Utilities.

This module provides secure password hashing using bcrypt.
"""

import bcrypt

# Salt rounds: higher values are more secure but slower
# 12 rounds is a good balance for most applications
SALT_ROUNDS = 12
salt = bcrypt.gensalt(rounds=SALT_ROUNDS)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: Bcrypt-hashed password
        
    Notes:
        - Uses randomly generated salt
        - Salt is embedded in the hash output
    """
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt-hashed password to check against
        
    Returns:
        bool: True if password matches, False otherwise
        
    Notes:
        - Uses constant-time comparison to prevent timing attacks
        - Extracts salt from stored hash automatically
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
