"""Client skeleton — plain TCP; no TLS. See assignment spec."""

import socket
import json
import os
import secrets
import sys
import threading
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
from app.storage.transcript import Transcript


# Load environment variables
load_dotenv()


class SecureChatClient:
    """Secure chat client implementing CIANR protocol."""
    
    def __init__(self, host: str = "localhost", port: int = 8888):
        """
        Initialize secure chat client.
        
        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self.socket = None
        
        # Certificate and key paths
        self.ca_cert_path = os.getenv("CA_CERT_PATH", "certs/ca_cert.pem")
        self.client_cert_path = os.getenv("CLIENT_CERT_PATH", "certs/client_cert.pem")
        self.client_key_path = os.getenv("CLIENT_KEY_PATH", "certs/client_key.pem")
        
        # Load CA certificate
        self.ca_cert = load_ca_cert(self.ca_cert_path)
        
        # Load client certificate
        self.client_cert = load_certificate_from_file(self.client_cert_path)
        
        # Load client private key
        self.client_private_key = load_private_key(self.client_key_path)
        
        # Client certificate PEM for transmission
        with open(self.client_cert_path, 'rb') as f:
            self.client_cert_pem = f.read().decode('utf-8')
        
        # Transcript directory
        self.transcript_dir = os.getenv("TRANSCRIPT_DIR", "transcripts")
        os.makedirs(self.transcript_dir, exist_ok=True)
        
        # Sequence number for messages
        self.seqno = 1
    
    def connect(self):
        """Connect to the server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")
    
    def start(self):
        """Start the client."""
        try:
            # Connect to server
            self.connect()
            
            # Phase 1: Control Plane (Negotiation and Authentication)
            server_cert, temp_aes_key = self.control_plane()
            if not server_cert:
                return
            
            # Phase 2: Registration/Login
            username = self.authentication(temp_aes_key)
            if not username:
                return
            
            # Phase 3: Key Agreement (Session Key)
            session_key = self.key_agreement()
            if not session_key:
                return
            
            # Phase 4: Data Plane (Encrypted Chat)
            transcript = self.data_plane(server_cert, session_key, username)
            
            # Phase 5: Non-Repudiation (Session Receipt)
            self.non_repudiation(server_cert, transcript, username)
            
        except Exception as e:
            print(f"Error in client: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.socket:
                self.socket.close()
    
    def control_plane(self) -> Tuple[Optional[object], Optional[bytes]]:
        """
        Control plane: certificate exchange and temporary DH key agreement.
        
        Returns:
            (server_cert, temp_aes_key) or (None, None) on failure
        """
        try:
            # Generate client nonce
            client_nonce = secrets.token_bytes(32)
            
            # Send client hello
            hello = HelloMessage(
                client_cert=self.client_cert_pem,
                nonce=b64e(client_nonce)
            )
            self.send_message(self.socket, hello.model_dump_json())
            
            # Receive server hello
            data = self.receive_message(self.socket)
            server_hello = ServerHelloMessage(**json.loads(data))
            
            # Load server certificate
            server_cert = load_certificate_from_file(server_hello.server_cert) if os.path.exists(server_hello.server_cert) else None
            if not server_cert:
                # Try to load from PEM string
                from app.crypto.pki import load_cert_from_pem
                server_cert = load_cert_from_pem(server_hello.server_cert)
            
            # Validate server certificate
            # Get expected CN from environment or use default
            expected_cn = os.getenv("SERVER_CN", "server.local")
            is_valid, error_msg = validate_certificate(server_cert, self.ca_cert, expected_cn=expected_cn)
            if not is_valid:
                print(f"Server certificate validation failed: {error_msg}")
                return None, None
            
            print(f"Server certificate validated: {error_msg}")
            
            # Perform temporary DH key exchange for credential encryption
            temp_aes_key = self.temporary_dh_exchange()
            if not temp_aes_key:
                return None, None
            
            return server_cert, temp_aes_key
            
        except Exception as e:
            print(f"Error in control plane: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def temporary_dh_exchange(self) -> Optional[bytes]:
        """
        Perform temporary DH key exchange for credential encryption.
        
        Returns:
            Temporary AES key or None on failure
        """
        try:
            # Generate DH parameters
            p, g = generate_dh_parameters()
            
            # Generate client private key
            client_private_key = generate_private_key()
            
            # Compute client public value
            client_public_value = compute_public_value(client_private_key, p, g)
            
            # Send client DH message
            dh_client = DHClientMessage(g=g, p=p, A=client_public_value)
            self.send_message(self.socket, dh_client.model_dump_json())
            
            # Receive server DH message
            data = self.receive_message(self.socket)
            dh_server = DHServerMessage(**json.loads(data))
            
            # Compute shared secret
            shared_secret = compute_shared_secret(client_private_key, dh_server.B, p)
            
            # Derive AES key
            aes_key = derive_session_key(shared_secret)
            
            return aes_key
            
        except Exception as e:
            print(f"Error in temporary DH exchange: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def authentication(self, temp_aes_key: bytes) -> Optional[str]:
        """
        Handle authentication: registration or login.
        
        Returns:
            Username if successful, None otherwise
        """
        try:
            # Prompt user for registration or login
            print("\n=== Authentication ===")
            action = input("Register (r) or Login (l)? ").strip().lower()
            
            if action == 'r':
                # Registration
                email = input("Email: ").strip()
                username = input("Username: ").strip()
                password = input("Password: ").strip()
                
                # Create registration message
                register_data = {
                    "type": "register",
                    "email": email,
                    "username": username,
                    "pwd": password  # Plaintext password (will be encrypted)
                }
                
                # Encrypt registration message
                register_json = json.dumps(register_data)
                encrypted_data = encrypt_aes128(register_json.encode('utf-8'), temp_aes_key)
                
                # Send encrypted registration message
                self.send_message(self.socket, b64e(encrypted_data))
                
                # Receive response
                data = self.receive_message(self.socket)
                response = json.loads(data)
                
                if response.get('status') == 'success':
                    print(f"Registration successful: {response.get('message')}")
                    return username
                else:
                    print(f"Registration failed: {response.get('message')}")
                    return None
                    
            elif action == 'l':
                # Login
                email = input("Email: ").strip()
                password = input("Password: ").strip()
                
                # Create login message
                login_data = {
                    "type": "login",
                    "email": email,
                    "pwd": password,  # Plaintext password (will be encrypted)
                    "nonce": b64e(secrets.token_bytes(32))
                }
                
                # Encrypt login message
                login_json = json.dumps(login_data)
                encrypted_data = encrypt_aes128(login_json.encode('utf-8'), temp_aes_key)
                
                # Send encrypted login message
                self.send_message(self.socket, b64e(encrypted_data))
                
                # Receive response
                data = self.receive_message(self.socket)
                response = json.loads(data)
                
                if response.get('status') == 'success':
                    print(f"Login successful: {response.get('message')}")
                    username = response.get('username')
                    return username
                else:
                    print(f"Login failed: {response.get('message')}")
                    return None
            else:
                print("Invalid action. Please choose 'r' for register or 'l' for login.")
                return None
                
        except Exception as e:
            print(f"Error in authentication: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def key_agreement(self) -> Optional[bytes]:
        """
        Perform session key agreement using DH.
        
        Returns:
            Session AES key or None on failure
        """
        try:
            # Generate DH parameters
            p, g = generate_dh_parameters()
            
            # Generate client private key
            client_private_key = generate_private_key()
            
            # Compute client public value
            client_public_value = compute_public_value(client_private_key, p, g)
            
            # Send client DH message
            dh_client = DHClientMessage(g=g, p=p, A=client_public_value)
            self.send_message(self.socket, dh_client.model_dump_json())
            
            # Receive server DH message
            data = self.receive_message(self.socket)
            dh_server = DHServerMessage(**json.loads(data))
            
            # Compute shared secret
            shared_secret = compute_shared_secret(client_private_key, dh_server.B, p)
            
            # Derive session AES key
            session_key = derive_session_key(shared_secret)
            
            print("Session key established")
            return session_key
            
        except Exception as e:
            print(f"Error in key agreement: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def data_plane(self, server_cert: object, session_key: bytes, username: str) -> Transcript:
        """
        Handle encrypted chat messages.
        
        Returns:
            Transcript object
        """
        # Initialize transcript
        transcript_file = os.path.join(self.transcript_dir, f"client_{username}_{now_ms()}.txt")
        transcript = Transcript(transcript_file)
        
        # Get server certificate fingerprint
        server_cert_fingerprint = get_cert_fingerprint(server_cert)
        
        # Get server public key
        server_public_key = load_public_key_from_cert(server_cert)
        
        # Reset sequence number
        self.seqno = 1
        
        print("\n=== Chat Session ===")
        print("Type messages to send, or 'quit' to exit.")
        
        # Start a thread to receive messages
        receive_thread = threading.Thread(target=self.receive_messages, args=(session_key, server_public_key, transcript, server_cert_fingerprint), daemon=True)
        receive_thread.start()
        
        try:
            while True:
                # Get user input
                message = input().strip()
                
                if message.lower() == 'quit':
                    # Send quit message
                    self.send_message(self.socket, json.dumps({"type": "quit"}))
                    break
                
                if message:
                    # Send message
                    self.send_chat_message(message, session_key, transcript, server_cert_fingerprint)
                    
        except KeyboardInterrupt:
            print("\nChat session interrupted")
        except Exception as e:
            print(f"Error in data plane: {e}")
            import traceback
            traceback.print_exc()
        
        return transcript
    
    def send_chat_message(self, plaintext: str, session_key: bytes, transcript: Transcript, peer_cert_fingerprint: str):
        """
        Send an encrypted chat message.
        
        Args:
            plaintext: Plaintext message
            session_key: AES session key
            transcript: Transcript object
            peer_cert_fingerprint: Peer certificate fingerprint
        """
        try:
            # Encrypt message
            plaintext_bytes = plaintext.encode('utf-8')
            ciphertext = encrypt_aes128(plaintext_bytes, session_key)
            
            # Get timestamp
            timestamp = now_ms()
            
            # Compute hash: SHA256(seqno || timestamp || ciphertext)
            seqno_bytes = self.seqno.to_bytes(8, byteorder='big')
            ts_bytes = timestamp.to_bytes(8, byteorder='big')
            hash_data = seqno_bytes + ts_bytes + ciphertext
            
            # Sign hash
            signature = sign_data(hash_data, self.client_private_key)
            
            # Create chat message
            chat_message = ChatMessage(
                seqno=self.seqno,
                ts=timestamp,
                ct=b64e(ciphertext),
                sig=b64e(signature)
            )
            
            # Send message
            self.send_message(self.socket, chat_message.model_dump_json())
            
            # Add to transcript
            transcript.append_message(
                self.seqno,
                timestamp,
                b64e(ciphertext),
                b64e(signature),
                peer_cert_fingerprint
            )
            
            # Increment sequence number
            self.seqno += 1
            
        except Exception as e:
            print(f"Error sending message: {e}")
            import traceback
            traceback.print_exc()
    
    def receive_messages(self, session_key: bytes, server_public_key, transcript: Transcript, server_cert_fingerprint: str):
        """
        Receive and process messages from server.
        
        Args:
            session_key: AES session key
            server_public_key: Server public key
            transcript: Transcript object
            server_cert_fingerprint: Server certificate fingerprint
        """
        try:
            while True:
                # Receive message
                data = self.receive_message(self.socket, timeout=1.0)
                if not data:
                    continue
                
                try:
                    msg_data = json.loads(data)
                    
                    if msg_data.get('type') == 'msg':
                        # Handle chat message from server
                        msg = ChatMessage(**msg_data)
                        
                        # Verify signature
                        seqno_bytes = msg.seqno.to_bytes(8, byteorder='big')
                        ts_bytes = msg.ts.to_bytes(8, byteorder='big')
                        ct_bytes = b64d(msg.ct)
                        hash_data = seqno_bytes + ts_bytes + ct_bytes
                        signature = b64d(msg.sig)
                        
                        if verify_signature(hash_data, signature, server_public_key):
                            # Decrypt message
                            plaintext = decrypt_aes128(ct_bytes, session_key)
                            print(f"Server: {plaintext.decode('utf-8')}")
                            
                            # Add to transcript
                            transcript.append_message(
                                msg.seqno,
                                msg.ts,
                                msg.ct,
                                msg.sig,
                                server_cert_fingerprint
                            )
                        else:
                            print("SIG_FAIL: Signature verification failed")
                            
                    elif msg_data.get('type') == 'receipt':
                        # Handle session receipt
                        receipt = SessionReceipt(**msg_data)
                        print(f"Received session receipt from server")
                        break
                    elif msg_data.get('status') == 'ack':
                        # Acknowledgment
                        pass
                    elif msg_data.get('status') == 'error':
                        print(f"Error: {msg_data.get('message')}")
                        
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error processing message: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error receiving messages: {e}")
            import traceback
            traceback.print_exc()
    
    def non_repudiation(self, server_cert: object, transcript: Transcript, username: str):
        """
        Generate and send session receipt for non-repudiation.
        """
        try:
            # Compute transcript hash
            transcript_hash = transcript.compute_transcript_hash()
            
            # Sign transcript hash
            hash_bytes = bytes.fromhex(transcript_hash)
            signature = sign_data(hash_bytes, self.client_private_key)
            
            # Create session receipt
            receipt = SessionReceipt(
                peer="client",
                first_seq=transcript.get_first_seq() or 0,
                last_seq=transcript.get_last_seq() or 0,
                transcript_sha256=transcript_hash,
                sig=b64e(signature)
            )
            
            # Send receipt
            self.send_message(self.socket, receipt.model_dump_json())
            
            print(f"Session receipt sent. Transcript hash: {transcript_hash}")
            
        except Exception as e:
            print(f"Error generating session receipt: {e}")
            import traceback
            traceback.print_exc()
    
    def receive_message(self, sock: socket.socket, timeout: Optional[float] = None) -> str:
        """
        Receive a message from the server.
        
        Args:
            sock: Socket
            timeout: Socket timeout in seconds
        
        Returns:
            Message string
        """
        if timeout:
            sock.settimeout(timeout)
        
        try:
            # Receive message length (first 4 bytes)
            length_data = sock.recv(4)
            if not length_data:
                return ""
            
            message_length = int.from_bytes(length_data, byteorder='big')
            
            # Receive message data
            message_data = b""
            while len(message_data) < message_length:
                chunk = sock.recv(message_length - len(message_data))
                if not chunk:
                    break
                message_data += chunk
            
            return message_data.decode('utf-8')
        except socket.timeout:
            return ""
        except Exception as e:
            print(f"Error receiving message: {e}")
            return ""
    
    def send_message(self, sock: socket.socket, message: str):
        """
        Send a message to the server.
        
        Args:
            sock: Socket
            message: Message string
        """
        message_bytes = message.encode('utf-8')
        message_length = len(message_bytes)
        
        # Send message length (4 bytes)
        sock.sendall(message_length.to_bytes(4, byteorder='big'))
        
        # Send message data
        sock.sendall(message_bytes)


def main():
    """Main client entry point."""
    # Create and start client
    host = os.getenv("SERVER_HOST", "localhost")
    port = int(os.getenv("SERVER_PORT", 8888))
    
    client = SecureChatClient(host, port)
    client.start()


if __name__ == "__main__":
    main()
