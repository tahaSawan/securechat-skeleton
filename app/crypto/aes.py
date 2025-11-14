"""AES-128(ECB)+PKCS#7 helpers (use library)."""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os


def encrypt_aes128(plaintext: bytes, key: bytes) -> bytes:
    """
    Encrypt plaintext using AES-128 in ECB mode with PKCS#7 padding.
    
    Args:
        plaintext: The plaintext to encrypt
        key: The 16-byte AES key
    
    Returns:
        The ciphertext (no IV prefix since ECB mode)
    """
    if len(key) != 16:
        raise ValueError("AES key must be 16 bytes (128 bits)")
    
    # Add PKCS#7 padding
    padder = padding.PKCS7(128).padder()  # 128 bits = 16 bytes block size
    padded_data = padder.update(plaintext) + padder.finalize()
    
    # Create cipher in ECB mode
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Encrypt
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return ciphertext


def decrypt_aes128(ciphertext: bytes, key: bytes) -> bytes:
    """
    Decrypt ciphertext using AES-128 in ECB mode and remove PKCS#7 padding.
    
    Args:
        ciphertext: The ciphertext to decrypt
        key: The 16-byte AES key
    
    Returns:
        The decrypted plaintext with padding removed
    """
    if len(key) != 16:
        raise ValueError("AES key must be 16 bytes (128 bits)")
    
    # Create cipher in ECB mode
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    
    # Decrypt
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove PKCS#7 padding
    unpadder = padding.PKCS7(128).unpadder()  # 128 bits = 16 bytes block size
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    return plaintext
