
# SecureChat – Assignment #2 (CS-3002 Information Security, Fall 2025)

This repository is the **official code skeleton** for your Assignment #2.  
You will build a **console-based, PKI-enabled Secure Chat System** in **Python**, demonstrating how cryptographic primitives combine to achieve:

**Confidentiality, Integrity, Authenticity, and Non-Repudiation (CIANR)**.


## 🧩 Overview

You are provided only with the **project skeleton and file hierarchy**.  
Each file contains docstrings and `TODO` markers describing what to implement.

Your task is to:
- Implement the **application-layer protocol**.
- Integrate cryptographic primitives correctly to satisfy the assignment spec.
- Produce evidence of security properties via Wireshark, replay/tamper tests, and signed session receipts.

## 🏗️ Folder Structure
```
securechat-skeleton/
├─ app/
│  ├─ client.py              # Client workflow (plain TCP, no TLS)
│  ├─ server.py              # Server workflow (plain TCP, no TLS)
│  ├─ crypto/
│  │  ├─ aes.py              # AES-128(ECB)+PKCS#7 (use cryptography lib)
│  │  ├─ dh.py               # Classic DH helpers + key derivation
│  │  ├─ pki.py              # X.509 validation (CA signature, validity, CN)
│  │  └─ sign.py             # RSA SHA-256 sign/verify (PKCS#1 v1.5)
│  ├─ common/
│  │  ├─ protocol.py         # Pydantic message models (hello/login/msg/receipt)
│  │  └─ utils.py            # Helpers (base64, now_ms, sha256_hex)
│  └─ storage/
│     ├─ db.py               # MySQL user store (salted SHA-256 passwords)
│     └─ transcript.py       # Append-only transcript + transcript hash
├─ scripts/
│  ├─ gen_ca.py              # Create Root CA (RSA + self-signed X.509)
│  └─ gen_cert.py            # Issue client/server certs signed by Root CA
├─ tests/manual/NOTES.md     # Manual testing + Wireshark evidence checklist
├─ certs/.keep               # Local certs/keys (gitignored)
├─ transcripts/.keep         # Session logs (gitignored)
├─ .env.example              # Sample configuration (no secrets)
├─ .gitignore                # Ignore secrets, binaries, logs, and certs
├─ requirements.txt          # Minimal dependencies
└─ .github/workflows/ci.yml  # Compile-only sanity check (no execution)
```

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher (or Docker)
- Git

### Step 1: Fork and Clone Repository
1. **Fork this repository** to your own GitHub account (using official NU email).  
   All development and commits must be performed in your fork.

2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/securechat-skeleton.git
   cd securechat-skeleton
   ```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the project root (copy from `.env.example` if available):
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=scuser
DB_PASSWORD=scpass
DB_NAME=securechat

# Server Configuration
SERVER_HOST=localhost
SERVER_PORT=8888

# Certificate Paths (relative to project root)
CA_CERT_PATH=certs/ca_cert.pem
CA_KEY_PATH=certs/ca_key.pem
SERVER_CERT_PATH=certs/server_cert.pem
SERVER_KEY_PATH=certs/server_key.pem
CLIENT_CERT_PATH=certs/client_cert.pem
CLIENT_KEY_PATH=certs/client_key.pem

# Transcript Directory
TRANSCRIPT_DIR=transcripts
```

### Step 4: Set Up MySQL Database

#### Option A: Using Docker (Recommended)
```bash
docker run -d \
  --name securechat-db \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=securechat \
  -e MYSQL_USER=scuser \
  -e MYSQL_PASSWORD=scpass \
  -p 3306:3306 \
  mysql:8
```

#### Option B: Using Local MySQL
1. Install MySQL 8.0 or higher
2. Create database and user:
   ```sql
   CREATE DATABASE securechat;
   CREATE USER 'scuser'@'localhost' IDENTIFIED BY 'scpass';
   GRANT ALL PRIVILEGES ON securechat.* TO 'scuser'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Step 5: Initialize Database Tables
```bash
python -m app.storage.db --init
```

This will create the `users` table with the following schema:
- `email VARCHAR(255) NOT NULL`
- `username VARCHAR(255) NOT NULL UNIQUE`
- `salt VARBINARY(16) NOT NULL`
- `pwd_hash CHAR(64) NOT NULL`

### Step 6: Generate Certificates

#### 6.1: Generate Root CA
```bash
python scripts/gen_ca.py --name "FAST-NU Root CA"
```

This will create:
- `certs/ca_cert.pem` - Root CA certificate
- `certs/ca_key.pem` - Root CA private key

#### 6.2: Generate Server Certificate
```bash
python scripts/gen_cert.py --cn server.local --out server --server
```

This will create:
- `certs/server_cert.pem` - Server certificate (signed by CA)
- `certs/server_key.pem` - Server private key

#### 6.3: Generate Client Certificate
```bash
python scripts/gen_cert.py --cn client.local --out client
```

This will create:
- `certs/client_cert.pem` - Client certificate (signed by CA)
- `certs/client_key.pem` - Client private key

**Note**: The `--server` flag is used for server certificates to set appropriate key usage extensions.

### Step 7: Verify Certificate Generation
You can verify the certificates using OpenSSL:
```bash
# View CA certificate
openssl x509 -in certs/ca_cert.pem -text -noout

# View server certificate
openssl x509 -in certs/server_cert.pem -text -noout

# View client certificate
openssl x509 -in certs/client_cert.pem -text -noout

# Verify server certificate is signed by CA
openssl verify -CAfile certs/ca_cert.pem certs/server_cert.pem

# Verify client certificate is signed by CA
openssl verify -CAfile certs/ca_cert.pem certs/client_cert.pem
```

### Step 8: Run the System

#### 8.1: Start the Server
```bash
python -m app.server
```

The server will:
- Load CA and server certificates
- Initialize database connection
- Listen on `localhost:8888` (configurable via `.env`)
- Accept client connections and handle secure chat sessions

#### 8.2: Start the Client (in another terminal)
```bash
python -m app.client
```

The client will:
- Load CA and client certificates
- Connect to the server
- Exchange certificates (mutual authentication)
- Perform Diffie-Hellman key exchange for credential encryption
- Prompt for registration or login
- Establish session key for chat
- Enable encrypted chat messaging

### Step 9: Usage Example

1. **Start the server**:
   ```bash
   python -m app.server
   ```

2. **Start the client** (in another terminal):
   ```bash
   python -m app.client
   ```

3. **Register a new user**:
   - When prompted, choose `r` for register
   - Enter email, username, and password
   - Server will create the user account

4. **Login**:
   - When prompted, choose `l` for login
   - Enter email and password
   - Server will authenticate the user

5. **Chat**:
   - After successful authentication, you can send messages
   - Messages are encrypted with AES-128 and signed with RSA
   - Type messages and press Enter to send
   - Type `quit` to exit the chat session

6. **Session Receipt**:
   - At the end of the session, a session receipt is generated
   - The receipt contains the transcript hash and signature
   - Transcripts are saved in the `transcripts/` directory

## 🚫 Important Rules

- **Do not use TLS/SSL or any secure-channel abstraction**  
  (e.g., `ssl`, HTTPS, WSS, OpenSSL socket wrappers).  
  All crypto operations must occur **explicitly** at the application layer.

- You are **not required** to implement AES, RSA, or DH math, Use any of the available libraries.
- Do **not commit secrets** (certs, private keys, salts, `.env` values).
- Your commits must reflect progressive development — at least **10 meaningful commits**.

## 🧾 Deliverables

When submitting on Google Classroom (GCR):

1. A ZIP of your **GitHub fork** (repository).
2. MySQL schema dump and a few sample records.
3. Updated **README.md** explaining setup, usage, and test outputs.
4. `RollNumber-FullName-Report-A02.docx`
5. `RollNumber-FullName-TestReport-A02.docx`

## 🔐 Protocol Implementation

### Control Plane (Negotiation and Authentication)
1. **Certificate Exchange**:
   - Client sends hello message with client certificate and nonce
   - Server sends server hello message with server certificate and nonce
   - Both parties validate each other's certificates:
     - Check issuer matches CA subject
     - Check validity period (not expired, not yet valid)
     - Check Common Name (CN) match (for server certificate)

2. **Temporary DH Key Exchange**:
   - Client sends DH parameters (p, g) and public value A
   - Server responds with public value B
   - Both compute shared secret: Ks = A^b mod p = B^a mod p
   - Derive temporary AES key: K = Trunc16(SHA256(big-endian(Ks)))

3. **Authentication**:
   - Client encrypts registration/login credentials with temporary AES key
   - Server decrypts and processes authentication
   - For registration: Server generates salt and computes password hash
   - For login: Server retrieves salt from database and verifies password

### Key Agreement (Session Key Establishment)
1. **DH Key Exchange**:
   - Client sends DH parameters (p, g) and public value A
   - Server responds with public value B
   - Both compute shared secret: Ks = A^b mod p = B^a mod p
   - Derive session AES key: K = Trunc16(SHA256(big-endian(Ks)))

### Data Plane (Encrypted Message Exchange)
1. **Message Encryption**:
   - Plaintext is padded using PKCS#7
   - Encrypted using AES-128 in ECB mode
   - Ciphertext is base64 encoded

2. **Message Signing**:
   - Compute hash: h = SHA256(seqno || timestamp || ciphertext)
   - Sign hash with RSA private key: sig = RSA_SIGN(h)
   - Signature is base64 encoded

3. **Message Format**:
   ```json
   {
     "type": "msg",
     "seqno": 1,
     "ts": 1234567890,
     "ct": "base64_encoded_ciphertext",
     "sig": "base64_encoded_signature"
   }
   ```

4. **Message Verification**:
   - Check sequence number (replay protection)
   - Check timestamp (freshness)
   - Verify signature using sender's public key
   - Decrypt ciphertext using AES-128
   - Remove PKCS#7 padding

### Non-Repudiation (Session Evidence)
1. **Transcript Management**:
   - Each message is appended to transcript file
   - Transcript format: `seqno|timestamp|ciphertext|signature|peer_cert_fingerprint`
   - Transcript is append-only

2. **Session Receipt**:
   - Compute transcript hash: TranscriptHash = SHA256(concatenation of transcript lines)
   - Sign transcript hash with RSA private key
   - Generate session receipt:
     ```json
     {
       "type": "receipt",
       "peer": "client|server",
       "first_seq": 1,
       "last_seq": 10,
       "transcript_sha256": "hex_hash",
       "sig": "base64_encoded_signature"
     }
     ```

## 🔒 Security Features

### Confidentiality
- **AES-128 Encryption**: All messages are encrypted with AES-128
- **Session Key**: Unique session key for each chat session
- **Temporary Key**: Separate temporary key for credential encryption

### Integrity
- **SHA-256 Hashing**: Message integrity verified using SHA-256
- **RSA Signatures**: Digital signatures ensure message authenticity
- **PKCS#7 Padding**: Proper padding for block cipher encryption

### Authenticity
- **X.509 Certificates**: Mutual authentication using CA-signed certificates
- **Certificate Validation**: Issuer, validity period, and CN checks
- **Digital Signatures**: RSA signatures on all messages

### Non-Repudiation
- **Transcript Management**: Append-only transcript of all messages
- **Session Receipt**: Signed transcript hash provides cryptographic proof
- **Offline Verification**: Transcripts can be verified offline

### Replay Protection
- **Sequence Numbers**: Strictly increasing sequence numbers
- **Timestamp Validation**: Messages with old timestamps are rejected
- **Replay Detection**: Duplicate sequence numbers are detected and rejected

## 🧪 Testing Instructions

### Test 1: Wireshark Capture
1. Start Wireshark and capture traffic on `localhost` (loopback interface)
2. Start server and client
3. Perform registration/login and send messages
4. Verify that all payloads are encrypted (no plaintext visible)

### Test 2: Invalid Certificate Test
1. Generate a self-signed certificate:
   ```bash
   openssl req -x509 -newkey rsa:2048 -keyout certs/invalid_key.pem -out certs/invalid_cert.pem -days 365 -nodes
   ```
2. Modify client to use invalid certificate
3. Verify server rejects connection with `BAD_CERT` error

### Test 3: Tamper Test
1. Start server and client
2. Send a message
3. Intercept and modify the ciphertext in transit (using a proxy or modified client)
4. Verify server rejects message with `SIG_FAIL` error

### Test 4: Replay Test
1. Start server and client
2. Send a message
3. Resend the same message with the same sequence number
4. Verify server rejects message with `REPLAY` error

### Test 5: Non-Repudiation Test
1. Start server and client
2. Send several messages
3. End chat session
4. Verify session receipt is generated
5. Verify transcript file is created
6. Verify transcript hash matches receipt
7. Verify receipt signature using certificate

### Test 6: Offline Verification
1. Export transcript and session receipt
2. Verify transcript hash:
   ```python
   from app.storage.transcript import Transcript
   transcript = Transcript("transcripts/client_username_timestamp.txt")
   hash_value = transcript.compute_transcript_hash()
   print(f"Transcript hash: {hash_value}")
   ```
3. Verify receipt signature:
   ```python
   from app.crypto.sign import verify_signature, load_public_key_from_cert
   from app.crypto.pki import load_certificate_from_file
   from app.common.utils import b64d
   import json
   
   # Load receipt
   with open("receipt.json") as f:
       receipt = json.load(f)
   
   # Load certificate
   cert = load_certificate_from_file("certs/client_cert.pem")
   public_key = load_public_key_from_cert(cert)
   
   # Verify signature
   hash_bytes = bytes.fromhex(receipt["transcript_sha256"])
   signature = b64d(receipt["sig"])
   is_valid = verify_signature(hash_bytes, signature, public_key)
   print(f"Signature valid: {is_valid}")
   ```

## 🧪 Test Evidence Checklist

✔ Wireshark capture (encrypted payloads only)  
✔ Invalid/self-signed cert rejected (`BAD_CERT`)  
✔ Tamper test → signature verification fails (`SIG_FAIL`)  
✔ Replay test → rejected by seqno (`REPLAY`)  
✔ Non-repudiation → exported transcript + signed SessionReceipt verified offline

## 🐛 Troubleshooting

### Common Issues

1. **Certificate Validation Failed**:
   - Verify CA certificate is in `certs/ca_cert.pem`
   - Verify server/client certificates are signed by CA
   - Check certificate validity period
   - Verify Common Name (CN) matches expected value

2. **Database Connection Failed**:
   - Verify MySQL is running
   - Check database credentials in `.env` file
   - Verify database and user exist
   - Check network connectivity

3. **Authentication Failed**:
   - Verify user exists in database
   - Check password is correct
   - Verify salt and password hash are stored correctly

4. **Message Encryption/Decryption Failed**:
   - Verify session key is derived correctly
   - Check AES key is 16 bytes (128 bits)
   - Verify PKCS#7 padding is applied correctly

5. **Signature Verification Failed**:
   - Verify certificate contains RSA public key
   - Check signature algorithm matches (RSA PKCS#1 v1.5 with SHA-256)
   - Verify hash computation is correct

## 📝 Notes

- All cryptographic operations are performed at the application layer (no TLS/SSL)
- Certificates and private keys are stored in `certs/` directory (gitignored)
- Transcripts are stored in `transcripts/` directory (gitignored)
- Database stores only user credentials, not chat messages
- Session keys are derived from Diffie-Hellman shared secrets
- Messages are encrypted with AES-128 and signed with RSA
- Sequence numbers and timestamps provide replay protection
- Transcripts provide non-repudiation evidence  
