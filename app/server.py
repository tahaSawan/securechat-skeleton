"""Server skeleton — plain TCP; no TLS. See assignment spec."""

import socket
import json
import os
import secrets
import sys
from typing import Optional, Tuple
from dotenv import load_dotenv

from app.crypto.pki import load_ca_cert, load_certificate_from_file, validate_certificate, get_cert_fingerprint
from app.crypto.dh import generate_private_key, compute_public_value, compute_shared_secret, derive_session_key, generate_dh_parameters
from app.crypto.aes import encrypt_aes128, decrypt_aes128
from app.crypto.sign import load_private_key, load_public_key_from_cert, sign_data, verify_signature
from app.common.protocol import (
    HelloMessage, ServerHelloMessage, RegisterMessage, LoginMessage,
    DHClientMessage, DHServerMessage, ChatMessage, SessionReceipt
)
from app.common.utils import now_ms, b64e, b64d, sha256_hex
from app.storage.db import register_user, authenticate_user, init_database
from app.storage.transcript import Transcript


# Load environment variables
load_dotenv()


class SecureChatServer:
    """Secure chat server implementing CIANR protocol."""
    
    def __init__(self, host: str = "localhost", port: int = 8888):
        """
        Initialize secure chat server.
        
        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self.socket = None
        
        # Certificate and key paths
        self.ca_cert_path = os.getenv("CA_CERT_PATH", "certs/ca_cert.pem")
        self.server_cert_path = os.getenv("SERVER_CERT_PATH", "certs/server_cert.pem")
        self.server_key_path = os.getenv("SERVER_KEY_PATH", "certs/server_key.pem")
        
        # Load CA certificate
        self.ca_cert = load_ca_cert(self.ca_cert_path)
        
        # Load server certificate
        self.server_cert = load_certificate_from_file(self.server_cert_path)
        
        # Load server private key
        self.server_private_key = load_private_key(self.server_key_path)
        
        # Server certificate PEM for transmission
        with open(self.server_cert_path, 'rb') as f:
            self.server_cert_pem = f.read().decode('utf-8')
        
        # Transcript directory
        self.transcript_dir = os.getenv("TRANSCRIPT_DIR", "transcripts")
        os.makedirs(self.transcript_dir, exist_ok=True)
    
    def start(self):
        """Start the server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")
        
        while True:
            try:
                client_socket, client_address = self.socket.accept()
                print(f"Client connected from {client_address}")
                self.handle_client(client_socket, client_address)
            except KeyboardInterrupt:
                print("\nServer shutting down...")
                break
            except Exception as e:
                print(f"Error handling client: {e}")
                continue
            finally:
                if client_socket:
                    client_socket.close()
    
    def handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        """Handle a client connection."""
        try:
            # Phase 1: Control Plane (Negotiation and Authentication)
            client_cert, temp_aes_key = self.control_plane(client_socket)
            if not client_cert:
                return
            
            # Phase 2: Registration/Login
            username = self.authentication(client_socket, client_cert, temp_aes_key)
            if not username:
                return
            
            # Phase 3: Key Agreement (Session Key)
            session_key = self.key_agreement(client_socket, client_cert)
            if not session_key:
                return
            
            # Phase 4: Data Plane (Encrypted Chat)
            transcript = self.data_plane(client_socket, client_cert, session_key, username, client_address)
            
            # Phase 5: Non-Repudiation (Session Receipt)
            self.non_repudiation(client_socket, client_cert, transcript, username)
            
        except Exception as e:
            print(f"Error in client handler: {e}")
            import traceback
            traceback.print_exc()
        finally:
            client_socket.close()
    
    def control_plane(self, client_socket: socket.socket) -> Tuple[Optional[object], Optional[bytes]]:
        """
        Control plane: certificate exchange and temporary DH key agreement.
        
        Returns:
            (client_cert, temp_aes_key) or (None, None) on failure
        """
        try:
            # Receive client hello
            data = self.receive_message(client_socket)
            hello = HelloMessage(**json.loads(data))
            
            # Load client certificate
            client_cert = load_certificate_from_file(hello.client_cert) if os.path.exists(hello.client_cert) else None
            if not client_cert:
                # Try to load from PEM string
                from app.crypto.pki import load_cert_from_pem
                client_cert = load_cert_from_pem(hello.client_cert)
            
            # Validate client certificate
            is_valid, error_msg = validate_certificate(client_cert, self.ca_cert)
            if not is_valid:
                self.send_error(client_socket, error_msg)
                return None, None
            
            print(f"Client certificate validated: {error_msg}")
            
            # Generate server nonce
            server_nonce = secrets.token_bytes(32)
            
            # Send server hello
            server_hello = ServerHelloMessage(
                server_cert=self.server_cert_pem,
                nonce=b64e(server_nonce)
            )
            self.send_message(client_socket, server_hello.model_dump_json())
            
            # Perform temporary DH key exchange for credential encryption
            temp_aes_key = self.temporary_dh_exchange(client_socket)
            if not temp_aes_key:
                return None, None
            
            return client_cert, temp_aes_key
            
        except Exception as e:
            print(f"Error in control plane: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def temporary_dh_exchange(self, client_socket: socket.socket) -> Optional[bytes]:
        """
        Perform temporary DH key exchange for credential encryption.
        
        Returns:
            Temporary AES key or None on failure
        """
        try:
            # Receive client DH message (client sends p, g, A)
            data = self.receive_message(client_socket)
            dh_client = DHClientMessage(**json.loads(data))
            
            # Use client's DH parameters (p, g)
            p = dh_client.p
            g = dh_client.g
            
            # Generate server private key
            server_private_key = generate_private_key()
            
            # Compute server public value
            server_public_value = compute_public_value(server_private_key, p, g)
            
            # Compute shared secret
            shared_secret = compute_shared_secret(server_private_key, dh_client.A, p)
            
            # Derive AES key
            aes_key = derive_session_key(shared_secret)
            
            # Send server DH message (server responds with B)
            dh_server = DHServerMessage(B=server_public_value)
            self.send_message(client_socket, dh_server.model_dump_json())
            
            return aes_key
            
        except Exception as e:
            print(f"Error in temporary DH exchange: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def authentication(self, client_socket: socket.socket, client_cert: object, temp_aes_key: bytes) -> Optional[str]:
        """
        Handle authentication: registration or login.
        
        Returns:
            Username if successful, None otherwise
        """
        try:
            # Receive encrypted authentication message
            encrypted_data = self.receive_message(client_socket)
            encrypted_bytes = b64d(encrypted_data)
            
            # Decrypt authentication message
            decrypted_data = decrypt_aes128(encrypted_bytes, temp_aes_key)
            auth_data = json.loads(decrypted_data.decode('utf-8'))
            
            if auth_data.get('type') == 'register':
                # Handle registration
                # For registration, password is sent as plaintext (encrypted with AES)
                # The server will generate salt and compute hash
                email = auth_data.get('email')
                username = auth_data.get('username')
                password = auth_data.get('pwd')  # Plaintext password
                
                # Register user (server generates salt and computes hash)
                success, message = register_user(email, username, password)
                if success:
                    self.send_message(client_socket, json.dumps({"status": "success", "message": "Registration successful"}))
                    return username
                else:
                    self.send_message(client_socket, json.dumps({"status": "error", "message": message}))
                    return None
                    
            elif auth_data.get('type') == 'login':
                # Handle login
                # For login, password is sent as plaintext (encrypted with AES)
                # The server retrieves salt from database and verifies
                email = auth_data.get('email')
                password = auth_data.get('pwd')  # Plaintext password
                
                # Authenticate user (server retrieves salt and verifies)
                is_authenticated, result = authenticate_user(email, password)
                if is_authenticated:
                    self.send_message(client_socket, json.dumps({"status": "success", "message": "Login successful", "username": result}))
                    return result
                else:
                    self.send_message(client_socket, json.dumps({"status": "error", "message": result}))
                    return None
            else:
                self.send_message(client_socket, json.dumps({"status": "error", "message": "Invalid authentication type"}))
                return None
                
        except Exception as e:
            print(f"Error in authentication: {e}")
            import traceback
            traceback.print_exc()
            self.send_message(client_socket, json.dumps({"status": "error", "message": str(e)}))
            return None
    
    def key_agreement(self, client_socket: socket.socket, client_cert: object) -> Optional[bytes]:
        """
        Perform session key agreement using DH.
        
        Returns:
            Session AES key or None on failure
        """
        try:
            # Receive client DH message (client sends p, g, A)
            data = self.receive_message(client_socket)
            dh_client = DHClientMessage(**json.loads(data))
            
            # Use client's DH parameters (p, g)
            p = dh_client.p
            g = dh_client.g
            
            # Generate server private key
            server_private_key = generate_private_key()
            
            # Compute server public value
            server_public_value = compute_public_value(server_private_key, p, g)
            
            # Compute shared secret
            shared_secret = compute_shared_secret(server_private_key, dh_client.A, p)
            
            # Derive session AES key
            session_key = derive_session_key(shared_secret)
            
            # Send server DH message (server responds with B)
            dh_server = DHServerMessage(B=server_public_value)
            self.send_message(client_socket, dh_server.model_dump_json())
            
            print("Session key established")
            return session_key
            
        except Exception as e:
            print(f"Error in key agreement: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def data_plane(self, client_socket: socket.socket, client_cert: object, session_key: bytes, username: str, client_address: Tuple[str, int]) -> Transcript:
        """
        Handle encrypted chat messages.
        
        Returns:
            Transcript object
        """
        # Initialize transcript
        transcript_file = os.path.join(self.transcript_dir, f"server_{username}_{now_ms()}.txt")
        transcript = Transcript(transcript_file)
        
        # Get client certificate fingerprint
        client_cert_fingerprint = get_cert_fingerprint(client_cert)
        
        # Get client public key
        client_public_key = load_public_key_from_cert(client_cert)
        
        # Sequence number tracking
        expected_seqno = 1
        
        print("Entering data plane. Type messages to send, or 'quit' to exit.")
        
        try:
            while True:
                # Receive message
                try:
                    data = self.receive_message(client_socket, timeout=1.0)
                    if data:
                        msg_data = json.loads(data)
                        
                        if msg_data.get('type') == 'msg':
                            # Handle chat message
                            msg = ChatMessage(**msg_data)
                            
                            # Verify sequence number (replay protection)
                            if msg.seqno != expected_seqno:
                                self.send_error(client_socket, f"REPLAY: Expected seqno {expected_seqno}, got {msg.seqno}")
                                continue
                            
                            # Verify timestamp (freshness)
                            current_time = now_ms()
                            if abs(current_time - msg.ts) > 300000:  # 5 minutes tolerance
                                self.send_error(client_socket, "STALE: Message timestamp is too old")
                                continue
                            
                            # Verify signature
                            # Compute hash: SHA256(seqno || timestamp || ciphertext)
                            # Concatenate as bytes: seqno (8 bytes) || timestamp (8 bytes) || ciphertext (bytes)
                            seqno_bytes = msg.seqno.to_bytes(8, byteorder='big')
                            ts_bytes = msg.ts.to_bytes(8, byteorder='big')
                            ct_bytes = b64d(msg.ct)
                            hash_data = seqno_bytes + ts_bytes + ct_bytes
                            signature = b64d(msg.sig)
                            
                            if not verify_signature(hash_data, signature, client_public_key):
                                self.send_error(client_socket, "SIG_FAIL: Signature verification failed")
                                continue
                            
                            # Decrypt message
                            ciphertext = b64d(msg.ct)
                            plaintext = decrypt_aes128(ciphertext, session_key)
                            
                            print(f"Client ({username}): {plaintext.decode('utf-8')}")
                            
                            # Add to transcript
                            transcript.append_message(
                                msg.seqno,
                                msg.ts,
                                msg.ct,
                                msg.sig,
                                client_cert_fingerprint
                            )
                            
                            expected_seqno += 1
                            
                            # Send acknowledgment
                            self.send_message(client_socket, json.dumps({"status": "ack", "seqno": msg.seqno}))
                            
                        elif msg_data.get('type') == 'receipt':
                            # Handle session receipt
                            receipt = SessionReceipt(**msg_data)
                            print(f"Received session receipt from client")
                            break
                        elif msg_data.get('type') == 'quit':
                            break
                            
                except socket.timeout:
                    # No message received, continue
                    pass
                except Exception as e:
                    print(f"Error receiving message: {e}")
                    break
                
                # Check for user input (non-blocking)
                # In a real implementation, you might want to use threading or select
                # For now, we'll just receive messages
                
        except KeyboardInterrupt:
            print("\nChat session interrupted")
        except Exception as e:
            print(f"Error in data plane: {e}")
            import traceback
            traceback.print_exc()
        
        return transcript
    
    def non_repudiation(self, client_socket: socket.socket, client_cert: object, transcript: Transcript, username: str):
        """
        Generate and send session receipt for non-repudiation.
        """
        try:
            # Compute transcript hash
            transcript_hash = transcript.compute_transcript_hash()
            
            # Sign transcript hash
            hash_bytes = bytes.fromhex(transcript_hash)
            signature = sign_data(hash_bytes, self.server_private_key)
            
            # Create session receipt
            receipt = SessionReceipt(
                peer="server",
                first_seq=transcript.get_first_seq() or 0,
                last_seq=transcript.get_last_seq() or 0,
                transcript_sha256=transcript_hash,
                sig=b64e(signature)
            )
            
            # Send receipt
            self.send_message(client_socket, receipt.model_dump_json())
            
            print(f"Session receipt sent. Transcript hash: {transcript_hash}")
            
        except Exception as e:
            print(f"Error generating session receipt: {e}")
            import traceback
            traceback.print_exc()
    
    def receive_message(self, client_socket: socket.socket, timeout: Optional[float] = None) -> str:
        """
        Receive a message from the client.
        
        Args:
            client_socket: Client socket
            timeout: Socket timeout in seconds
        
        Returns:
            Message string
        """
        if timeout:
            client_socket.settimeout(timeout)
        
        # Receive message length (first 4 bytes)
        length_data = client_socket.recv(4)
        if not length_data:
            return ""
        
        message_length = int.from_bytes(length_data, byteorder='big')
        
        # Receive message data
        message_data = b""
        while len(message_data) < message_length:
            chunk = client_socket.recv(message_length - len(message_data))
            if not chunk:
                break
            message_data += chunk
        
        return message_data.decode('utf-8')
    
    def send_message(self, client_socket: socket.socket, message: str):
        """
        Send a message to the client.
        
        Args:
            client_socket: Client socket
            message: Message string
        """
        message_bytes = message.encode('utf-8')
        message_length = len(message_bytes)
        
        # Send message length (4 bytes)
        client_socket.sendall(message_length.to_bytes(4, byteorder='big'))
        
        # Send message data
        client_socket.sendall(message_bytes)
    
    def send_error(self, client_socket: socket.socket, error_message: str):
        """Send an error message to the client."""
        error_response = json.dumps({"status": "error", "message": error_message})
        self.send_message(client_socket, error_response)


def main():
    """Main server entry point."""
    # Initialize database
    try:
        init_database()
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("Continuing anyway...")
    
    # Create and start server
    host = os.getenv("SERVER_HOST", "localhost")
    port = int(os.getenv("SERVER_PORT", 8888))
    
    server = SecureChatServer(host, port)
    server.start()


if __name__ == "__main__":
    main()
