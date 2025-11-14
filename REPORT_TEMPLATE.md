# Report Template: RollNumber-FullName-Report-A02

## Instructions
Replace `RollNumber` with your roll number and `FullName` with your full name.

## Report Structure

### 1. Introduction
- Overview of the assignment
- Objective: Implement a secure chat system with CIANR (Confidentiality, Integrity, Authenticity, Non-Repudiation)
- Technologies used: Python, MySQL, Cryptography library

### 2. Protocol Implementation

#### 2.1 Control Plane (Negotiation and Authentication)
- Certificate exchange process
- Temporary Diffie-Hellman key exchange
- Registration and login process
- Screenshot: Certificate generation
- Screenshot: Registration/login

#### 2.2 Key Agreement (Session Key Establishment)
- Diffie-Hellman key exchange
- Key derivation: K = Trunc16(SHA256(big-endian(Ks)))
- Session key establishment
- Screenshot: Key exchange process

#### 2.3 Data Plane (Encrypted Message Exchange)
- Message encryption (AES-128)
- Message signing (RSA PKCS#1 v1.5 SHA-256)
- Message format: {seqno, ts, ct, sig}
- Screenshot: Encrypted messages

#### 2.4 Non-Repudiation (Session Evidence)
- Transcript management
- Session receipt generation
- Offline verification
- Screenshot: Transcript files
- Screenshot: Session receipts

### 3. Security Features (CIANR)

#### 3.1 Confidentiality
- AES-128 encryption
- Session key establishment
- Temporary key for credentials
- Screenshot: Encrypted payloads

#### 3.2 Integrity
- SHA-256 hashing
- RSA signatures
- PKCS#7 padding
- Screenshot: Signature verification

#### 3.3 Authenticity
- X.509 certificates
- Certificate validation
- Digital signatures
- Screenshot: Certificate validation

#### 3.4 Non-Repudiation
- Transcript management
- Session receipts
- Offline verification
- Screenshot: Offline verification

### 4. Certificate Validation

#### 4.1 Certificate Generation
- Root CA generation
- Server certificate generation
- Client certificate generation
- Screenshot: Certificate generation output

#### 4.2 Certificate Validation
- Issuer validation
- Validity period check
- Common Name (CN) check
- Invalid certificate rejection
- Screenshot: Certificate validation output

#### 4.3 Certificate Inspection
```bash
# CA Certificate
openssl x509 -in certs/ca_cert.pem -text -noout

# Server Certificate
openssl x509 -in certs/server_cert.pem -text -noout

# Client Certificate
openssl x509 -in certs/client_cert.pem -text -noout
```

Screenshot: Certificate inspection output

### 5. Key Exchange Process

#### 5.1 Diffie-Hellman Key Exchange
- Public parameter exchange (p, g)
- Public value exchange (A, B)
- Shared secret computation: Ks = A^b mod p = B^a mod p
- Key derivation: K = Trunc16(SHA256(big-endian(Ks)))

#### 5.2 Session Key Establishment
- Temporary key for credentials
- Session key for chat messages
- Key rotation (per session)

### 6. Message Encryption and Signing

#### 6.1 Message Encryption
- Plaintext padding (PKCS#7)
- AES-128 encryption (ECB mode)
- Ciphertext encoding (base64)

#### 6.2 Message Signing
- Hash computation: h = SHA256(seqno || timestamp || ciphertext)
- RSA signing: sig = RSA_SIGN(h)
- Signature encoding (base64)

#### 6.3 Message Verification
- Sequence number validation
- Timestamp validation
- Signature verification
- Ciphertext decryption

### 7. Non-Repudiation Mechanism

#### 7.1 Transcript Management
- Append-only transcript
- Transcript format: seqno|timestamp|ciphertext|signature|peer_cert_fingerprint
- Transcript hash: SHA256(concatenation of transcript lines)

#### 7.2 Session Receipt
- Receipt format: {type, peer, first_seq, last_seq, transcript_sha256, sig}
- Receipt signing: RSA_SIGN(transcript_sha256)
- Receipt verification

#### 7.3 Offline Verification
- Transcript hash verification
- Receipt signature verification
- Message signature verification
- Screenshot: Offline verification

### 8. Implementation Details

#### 8.1 Database Schema
```sql
CREATE TABLE users (
    email VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    salt VARBINARY(16) NOT NULL,
    pwd_hash CHAR(64) NOT NULL,
    PRIMARY KEY (username),
    INDEX idx_email (email)
);
```

#### 8.2 Password Security
- Salt generation: 16-byte random salt
- Password hashing: hex(SHA256(salt || password))
- Constant-time comparison

#### 8.3 Replay Protection
- Sequence number validation
- Timestamp validation
- Duplicate message rejection

### 9. Testing

#### 9.1 Functional Testing
- Registration test
- Login test
- Chat message test
- Screenshot: Functional tests

#### 9.2 Security Testing
- Invalid certificate test
- Tamper detection test
- Replay protection test
- Screenshot: Security tests

### 10. Conclusion
- Summary of implementation
- Security features achieved
- Challenges faced
- Future improvements

## Screenshots Required

1. Certificate generation output
2. Registration/login process
3. Chat messages
4. Transcript files
5. Session receipts
6. Certificate validation output
7. Certificate inspection output
8. Offline verification output
9. Security test results
10. Wireshark capture (encrypted payloads)

## Appendix

### A. Certificate Inspection Output
```bash
openssl x509 -in certs/ca_cert.pem -text -noout
openssl x509 -in certs/server_cert.pem -text -noout
openssl x509 -in certs/client_cert.pem -text -noout
```

### B. Database Schema
```sql
-- See schema.sql for complete schema
```

### C. Sample Records
```sql
-- See sample_records.sql for sample records
```

### D. GitHub Repository
Link: https://github.com/YOUR_USERNAME/securechat-skeleton

### E. Code Structure
```
securechat-skeleton/
├── app/
│   ├── client.py
│   ├── server.py
│   ├── crypto/
│   │   ├── aes.py
│   │   ├── dh.py
│   │   ├── pki.py
│   │   └── sign.py
│   ├── common/
│   │   ├── protocol.py
│   │   └── utils.py
│   └── storage/
│       ├── db.py
│       └── transcript.py
├── scripts/
│   ├── gen_ca.py
│   └── gen_cert.py
└── tests/
    ├── test_invalid_cert.py
    ├── test_tamper.py
    ├── test_replay.py
    └── test_non_repudiation.py
```

