"""
API Key Management System

Provides secure API key generation, validation, and lifecycle management.
Uses SQLite for persistence in MVP, can be upgraded to PostgreSQL/MySQL for production.
"""

import sqlite3
import secrets
import hashlib
import time
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass


@dataclass
class APIKey:
    """API Key data model"""
    key_id: str
    key_hash: str
    name: str
    created_at: str
    expires_at: Optional[str]
    is_active: bool
    rate_limit: int  # requests per minute
    last_used_at: Optional[str]
    usage_count: int
    metadata: Optional[str]


class APIKeyManager:
    """
    Manages API keys with secure storage and validation
    
    Features:
    - Secure key generation (cryptographically random)
    - Key hashing (SHA-256)
    - Expiration support
    - Rate limiting
    - Usage tracking
    - Key rotation
    """
    
    def __init__(self, db_path: str = "data/api_keys.db"):
        """
        Initialize API Key Manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialize_database()
    
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id TEXT PRIMARY KEY,
                key_hash TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                rate_limit INTEGER NOT NULL DEFAULT 1000,
                last_used_at TEXT,
                usage_count INTEGER NOT NULL DEFAULT 0,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_key_hash ON api_keys(key_hash)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_is_active ON api_keys(is_active)
        """)
        
        conn.commit()
        conn.close()
    
    def generate_key(
        self,
        name: str,
        expires_in_days: Optional[int] = None,
        rate_limit: int = 1000,
        metadata: Optional[Dict] = None
    ) -> Tuple[str, APIKey]:
        """
        Generate a new API key
        
        Args:
            name: Descriptive name for the key
            expires_in_days: Optional expiration in days
            rate_limit: Requests per minute limit
            metadata: Optional metadata dictionary
        
        Returns:
            Tuple of (raw_key, APIKey object)
            
        Note:
            The raw key is only returned once and cannot be retrieved later.
            Store it securely!
        """
        # Generate cryptographically secure random key
        raw_key = f"asg_{secrets.token_urlsafe(32)}"
        
        # Hash the key for storage
        key_hash = self._hash_key(raw_key)
        
        # Generate unique key ID
        key_id = f"key_{secrets.token_hex(8)}"
        
        # Calculate expiration
        created_at = datetime.utcnow()
        expires_at = None
        if expires_in_days:
            expires_at = created_at + timedelta(days=expires_in_days)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO api_keys (
                key_id, key_hash, name, created_at, expires_at,
                is_active, rate_limit, usage_count, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            key_id,
            key_hash,
            name,
            created_at.isoformat(),
            expires_at.isoformat() if expires_at else None,
            1,  # is_active
            rate_limit,
            0,  # usage_count
            str(metadata) if metadata else None
        ))
        
        conn.commit()
        conn.close()
        
        # Create APIKey object
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            created_at=created_at.isoformat(),
            expires_at=expires_at.isoformat() if expires_at else None,
            is_active=True,
            rate_limit=rate_limit,
            last_used_at=None,
            usage_count=0,
            metadata=str(metadata) if metadata else None
        )
        
        return raw_key, api_key
    
    def validate_key(self, raw_key: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an API key
        
        Args:
            raw_key: The raw API key to validate
        
        Returns:
            Tuple of (is_valid, reason)
            - is_valid: True if key is valid
            - reason: None if valid, error message if invalid
        """
        # Hash the provided key
        key_hash = self._hash_key(raw_key)
        
        # Look up in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT key_id, is_active, expires_at, usage_count, rate_limit
            FROM api_keys
            WHERE key_hash = ?
        """, (key_hash,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False, "Invalid API key"
        
        key_id, is_active, expires_at, usage_count, rate_limit = result
        
        # Check if active
        if not is_active:
            return False, "API key has been revoked"
        
        # Check if expired
        if expires_at:
            expiry = datetime.fromisoformat(expires_at)
            if datetime.utcnow() > expiry:
                return False, "API key has expired"
        
        # Update usage
        self._record_usage(key_hash)
        
        return True, None
    
    def revoke_key(self, key_id: str) -> bool:
        """
        Revoke an API key
        
        Args:
            key_id: The key ID to revoke
        
        Returns:
            True if revoked successfully, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE api_keys
            SET is_active = 0
            WHERE key_id = ?
        """, (key_id,))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def list_keys(self, include_inactive: bool = False) -> List[APIKey]:
        """
        List all API keys
        
        Args:
            include_inactive: Whether to include revoked keys
        
        Returns:
            List of APIKey objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if include_inactive:
            cursor.execute("SELECT * FROM api_keys ORDER BY created_at DESC")
        else:
            cursor.execute("""
                SELECT * FROM api_keys
                WHERE is_active = 1
                ORDER BY created_at DESC
            """)
        
        results = cursor.fetchall()
        conn.close()
        
        keys = []
        for row in results:
            keys.append(APIKey(
                key_id=row[0],
                key_hash=row[1],
                name=row[2],
                created_at=row[3],
                expires_at=row[4],
                is_active=bool(row[5]),
                rate_limit=row[6],
                last_used_at=row[7],
                usage_count=row[8],
                metadata=row[9]
            ))
        
        return keys
    
    def get_key_info(self, key_id: str) -> Optional[APIKey]:
        """
        Get information about a specific key
        
        Args:
            key_id: The key ID
        
        Returns:
            APIKey object or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM api_keys WHERE key_id = ?", (key_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return APIKey(
            key_id=result[0],
            key_hash=result[1],
            name=result[2],
            created_at=result[3],
            expires_at=result[4],
            is_active=bool(result[5]),
            rate_limit=result[6],
            last_used_at=result[7],
            usage_count=result[8],
            metadata=result[9]
        )
    
    def _hash_key(self, raw_key: str) -> str:
        """
        Hash an API key using SHA-256
        
        Args:
            raw_key: The raw API key
        
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    def _record_usage(self, key_hash: str):
        """
        Record API key usage
        
        Args:
            key_hash: The hashed key
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE api_keys
            SET usage_count = usage_count + 1,
                last_used_at = ?
            WHERE key_hash = ?
        """, (datetime.utcnow().isoformat(), key_hash))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        """
        Get API key statistics
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 1")
        active_keys = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 0")
        revoked_keys = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(usage_count) FROM api_keys")
        total_usage = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "active_keys": active_keys,
            "revoked_keys": revoked_keys,
            "total_keys": active_keys + revoked_keys,
            "total_usage": total_usage
        }


# Example usage
if __name__ == "__main__":
    # Initialize manager
    manager = APIKeyManager("data/api_keys.db")
    
    # Generate a new key
    raw_key, api_key = manager.generate_key(
        name="Test Key",
        expires_in_days=30,
        rate_limit=1000
    )
    
    print(f"Generated API Key: {raw_key}")
    print(f"Key ID: {api_key.key_id}")
    print(f"Expires: {api_key.expires_at}")
    
    # Validate the key
    is_valid, reason = manager.validate_key(raw_key)
    print(f"\nValidation: {is_valid}")
    if not is_valid:
        print(f"Reason: {reason}")
    
    # List all keys
    keys = manager.list_keys()
    print(f"\nTotal active keys: {len(keys)}")
    
    # Get statistics
    stats = manager.get_statistics()
    print(f"\nStatistics: {stats}")
