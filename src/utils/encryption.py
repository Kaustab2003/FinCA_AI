"""
Encryption utility for sensitive data (salary, PAN, etc.)
Uses Fernet (AES-128-CBC + HMAC) for symmetric encryption
"""
from cryptography.fernet import Fernet
from src.config.settings import settings
import structlog
from typing import Optional
from dotenv import load_dotenv
import os

# Load .env before anything else
load_dotenv()

logger = structlog.get_logger()

class SalaryEncryption:
    """Handle encryption/decryption of salary data"""
    
    def __init__(self):
        """Initialize encryption with key from environment"""
        # Try direct environment variable first
        key = os.getenv('ENCRYPTION_KEY')
        
        if not key:
            logger.warning("⚠️ No ENCRYPTION_KEY found in .env")
            raise ValueError("ENCRYPTION_KEY must be set in .env file")
        
        try:
            self.cipher = Fernet(key.encode())
            logger.info("Encryption initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    def encrypt_salary(self, salary: int) -> str:
        """
        Encrypt salary amount
        
        Args:
            salary: Monthly salary amount (integer)
        
        Returns:
            Encrypted string
        """
        try:
            salary_bytes = str(salary).encode()
            encrypted = self.cipher.encrypt(salary_bytes)
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_salary(self, encrypted_salary: str) -> int:
        """
        Decrypt salary amount
        
        Args:
            encrypted_salary: Encrypted salary string
        
        Returns:
            Original salary amount (integer)
        """
        try:
            # Handle unencrypted data (legacy support)
            if not encrypted_salary or encrypted_salary.isdigit():
                logger.info("Found unencrypted salary data, returning as-is")
                return int(encrypted_salary) if encrypted_salary else 0
            
            decrypted = self.cipher.decrypt(encrypted_salary.encode())
            return int(decrypted.decode())
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            # Try to return as integer if it's actually unencrypted
            try:
                return int(encrypted_salary)
            except:
                return 0

# Global instance
_encryption_instance: Optional[SalaryEncryption] = None

def get_encryption() -> SalaryEncryption:
    """Get or create encryption instance"""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = SalaryEncryption()
    return _encryption_instance

# Convenience functions
def encrypt_salary(salary: int) -> str:
    """Encrypt salary - convenience wrapper"""
    return get_encryption().encrypt_salary(salary)

def decrypt_salary(encrypted_salary: str) -> int:
    """Decrypt salary - convenience wrapper"""
    return get_encryption().decrypt_salary(encrypted_salary)
