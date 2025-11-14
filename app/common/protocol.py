"""Pydantic models: hello, server_hello, register, login, dh_client, dh_server, msg, receipt."""

from pydantic import BaseModel
from typing import Optional


class HelloMessage(BaseModel):
    """Client hello message with certificate and nonce."""
    type: str = "hello"
    client_cert: str  # PEM encoded certificate
    nonce: str  # base64 encoded nonce


class ServerHelloMessage(BaseModel):
    """Server hello message with certificate and nonce."""
    type: str = "server_hello"
    server_cert: str  # PEM encoded certificate
    nonce: str  # base64 encoded nonce


class RegisterMessage(BaseModel):
    """Registration message with encrypted credentials."""
    type: str = "register"
    email: str
    username: str
    pwd: str  # plaintext password (encrypted with AES for transmission)


class LoginMessage(BaseModel):
    """Login message with encrypted credentials."""
    type: str = "login"
    email: str
    pwd: str  # base64(sha256(salt||pwd))
    nonce: str  # base64 encoded nonce


class DHClientMessage(BaseModel):
    """Diffie-Hellman client message with public parameters."""
    type: str = "dh_client"
    g: int  # generator
    p: int  # prime modulus
    A: int  # public value g^a mod p


class DHServerMessage(BaseModel):
    """Diffie-Hellman server message with public value."""
    type: str = "dh_server"
    B: int  # public value g^b mod p


class ChatMessage(BaseModel):
    """Encrypted chat message with signature."""
    type: str = "msg"
    seqno: int  # sequence number
    ts: int  # timestamp in milliseconds
    ct: str  # base64 encoded ciphertext
    sig: str  # base64 encoded RSA signature


class SessionReceipt(BaseModel):
    """Session receipt for non-repudiation."""
    type: str = "receipt"
    peer: str  # "client" or "server"
    first_seq: int  # first sequence number
    last_seq: int  # last sequence number
    transcript_sha256: str  # hexadecimal SHA-256 hash of transcript
    sig: str  # base64 encoded RSA signature
