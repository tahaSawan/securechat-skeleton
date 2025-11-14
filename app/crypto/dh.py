"""Classic DH helpers + Trunc16(SHA256(Ks)) derivation."""

import secrets
import hashlib
from typing import Tuple


# Standard DH parameters (RFC 5114)
# Using a 2048-bit prime for security
# Note: In production, use well-known safe primes or generate them securely
DH_P = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AAAC42DAD33170D04507A33A85521ABDF1CBA64ECFB850458DBEF0A8AEA71575D060C7DB3970F85A6E1E4C7ABF5AE8CDB0933D71E8C94E04A25619DCEE3D2261AD2EE6BF12FFA06D98A0864D87602733EC86A64521F2B18177B200CBBE117577A615D6C770988C0BAD946E208E24FA074E5AB3143DB5BFCE0FD108E4B82D120A93AD2CAFFFFFFFFFFFFFFFF
DH_G = 2


def generate_private_key() -> int:
    """Generate a random private key for DH."""
    # Generate a random private key (at least 256 bits)
    return secrets.randbits(256)


def compute_public_value(private_key: int, p: int, g: int) -> int:
    """Compute public value: A = g^a mod p (or B = g^b mod p)."""
    return pow(g, private_key, p)


def compute_shared_secret(private_key: int, peer_public_value: int, p: int) -> int:
    """Compute shared secret: Ks = peer_public_value^private_key mod p."""
    return pow(peer_public_value, private_key, p)


def derive_session_key(shared_secret: int) -> bytes:
    """
    Derive AES-128 session key from shared secret.
    K = Trunc16(SHA256(big-endian(Ks)))
    """
    # Convert shared secret to big-endian bytes
    # Calculate the number of bytes needed
    secret_bytes = shared_secret.to_bytes((shared_secret.bit_length() + 7) // 8, byteorder='big')
    
    # Compute SHA-256 hash
    hash_value = hashlib.sha256(secret_bytes).digest()
    
    # Truncate to 16 bytes (128 bits) for AES-128
    return hash_value[:16]


def generate_dh_parameters() -> Tuple[int, int]:
    """Generate or return standard DH parameters (p, g)."""
    return (DH_P, DH_G)
