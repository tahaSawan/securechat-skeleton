"""RSA PKCS#1 v1.5 SHA-256 sign/verify."""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.backends import default_backend
import hashlib


def load_private_key(key_path: str) -> rsa.RSAPrivateKey:
    """Load RSA private key from PEM file."""
    with open(key_path, 'rb') as f:
        return load_pem_private_key(f.read(), password=None, backend=default_backend())


def load_public_key_from_cert(cert) -> rsa.RSAPublicKey:
    """Extract RSA public key from X.509 certificate."""
    public_key = cert.public_key()
    if isinstance(public_key, rsa.RSAPublicKey):
        return public_key
    raise ValueError("Certificate does not contain an RSA public key")


def sign_data(data: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    """
    Sign data using RSA PKCS#1 v1.5 with SHA-256.
    
    The cryptography library will automatically compute SHA-256 hash of the data.
    
    Args:
        data: The data to sign (will be hashed internally)
        private_key: The RSA private key
    
    Returns:
        The signature as bytes
    """
    # Sign using PKCS#1 v1.5 padding with SHA-256
    # The library will compute SHA-256 hash internally
    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    
    return signature


def verify_signature(data: bytes, signature: bytes, public_key: rsa.RSAPublicKey) -> bool:
    """
    Verify RSA signature using PKCS#1 v1.5 with SHA-256.
    
    The cryptography library will automatically compute SHA-256 hash of the data.
    
    Args:
        data: The original data (will be hashed internally)
        signature: The signature to verify
        public_key: The RSA public key
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Verify signature
        # The library will compute SHA-256 hash internally
        public_key.verify(
            signature,
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
