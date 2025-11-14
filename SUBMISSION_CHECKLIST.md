# Submission Checklist

## ✅ Required Deliverables

### 1. GitHub Repository
- [ ] Forked the repository: https://github.com/maadilrehman/securechat-skeleton
- [ ] All code is pushed to your fork
- [ ] At least 10 meaningful commits
- [ ] Repository is accessible
- [ ] README.md is updated with setup instructions
- [ ] Link to your GitHub repository is available

### 2. Database Files
- [ ] `schema.sql` - Database schema (no data)
- [ ] `sample_records.sql` - Sample user records
- [ ] `database_dump.sql` - Complete database dump (optional)
- [ ] Database schema matches requirements:
  - `users` table with columns: `email`, `username`, `salt`, `pwd_hash`
  - `email` VARCHAR(255) NOT NULL
  - `username` VARCHAR(255) NOT NULL UNIQUE
  - `salt` VARBINARY(16) NOT NULL
  - `pwd_hash` CHAR(64) NOT NULL

### 3. README.md
- [ ] Updated with setup instructions
- [ ] Execution steps documented
- [ ] Configuration requirements documented
- [ ] Sample input/output formats
- [ ] Link to GitHub repository
- [ ] Troubleshooting section

### 4. Report (RollNumber-FullName-Report-A02.docx)
- [ ] Protocol implementation details
- [ ] Security features (CIANR):
  - Confidentiality
  - Integrity
  - Authenticity
  - Non-repudiation
- [ ] Certificate validation process
- [ ] Key exchange process
- [ ] Message encryption and signing
- [ ] Non-repudiation mechanism
- [ ] Certificate inspection results (openssl x509 -text)
- [ ] Screenshots of:
  - Certificate generation
  - Registration/login
  - Chat messages
  - Transcripts
  - Session receipts

### 5. Test Report (RollNumber-FullName-TestReport-A02.docx)
- [ ] Wireshark capture:
  - Encrypted payloads (no plaintext)
  - Display filters used
  - Screenshots of encrypted traffic
- [ ] Invalid certificate test:
  - Self-signed certificate rejection
  - Expired certificate rejection
  - Untrusted certificate rejection
  - Error messages (BAD_CERT)
- [ ] Tamper test:
  - Modified ciphertext
  - Signature verification failure
  - Error messages (SIG_FAIL)
- [ ] Replay test:
  - Duplicate sequence number
  - Replay detection
  - Error messages (REPLAY)
- [ ] Non-repudiation:
  - Transcript export
  - Session receipt generation
  - Offline verification:
    - Verify each message signature
    - Verify transcript hash
    - Verify receipt signature
    - Show that any edit breaks verification

### 6. ZIP File (GitHub Repository)
- [ ] Downloaded ZIP of your GitHub repository
- [ ] Does not include:
  - `.git/` directory
  - `.venv/` directory
  - `__pycache__/` directories
  - `*.pyc` files
  - `certs/` directory (certificates and keys)
  - `transcripts/` directory
  - `.env` file (secrets)
- [ ] Includes:
  - All source code
  - `requirements.txt`
  - `README.md`
  - `.gitignore`
  - `scripts/` directory
  - `app/` directory

## 📋 Submission Format

### On Google Classroom (GCR):
1. **ZIP File**: Downloaded ZIP of your GitHub repository
2. **Database Files**:
   - `schema.sql` - Database schema
   - `sample_records.sql` - Sample records
3. **README.md**: Updated README with setup, usage, and test outputs
4. **Report**: `RollNumber-FullName-Report-A02.docx`
5. **Test Report**: `RollNumber-FullName-TestReport-A02.docx`
6. **GitHub Link**: Link to your GitHub repository

## 🔍 Verification Steps

### Before Submission:
1. **Test the system**:
   - [ ] Generate certificates
   - [ ] Initialize database
   - [ ] Register a user
   - [ ] Login with user
   - [ ] Send chat messages
   - [ ] Verify transcripts
   - [ ] Verify session receipts

2. **Test security features**:
   - [ ] Invalid certificate rejection
   - [ ] Tamper test (signature failure)
   - [ ] Replay test (sequence number)
   - [ ] Wireshark capture (encrypted payloads)
   - [ ] Non-repudiation verification

3. **Verify code quality**:
   - [ ] No hardcoded secrets
   - [ ] Proper error handling
   - [ ] Code is well-documented
   - [ ] Follows assignment requirements
   - [ ] No use of TLS/SSL

4. **Verify documentation**:
   - [ ] README.md is complete
   - [ ] Reports are comprehensive
   - [ ] Test evidence is included
   - [ ] Screenshots are clear

## 📝 Quick Commands Reference

### Setup:
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env  # Or create manually

# Start MySQL (Docker)
docker run -d --name securechat-db -e MYSQL_ROOT_PASSWORD=rootpass -e MYSQL_DATABASE=securechat -e MYSQL_USER=scuser -e MYSQL_PASSWORD=scpass -p 3306:3306 mysql:8

# Initialize database
python -m app.storage.db --init

# Generate certificates
python scripts/gen_ca.py --name "FAST-NU Root CA"
python scripts/gen_cert.py --cn server.local --out server --server
python scripts/gen_cert.py --cn client.local --out client
```

### Testing:
```bash
# Start server
python -m app.server

# Start client (in another terminal)
python -m app.client
```

### Database Export:
```bash
# Export schema
mysqldump -u scuser -pscpass securechat --no-data > schema.sql

# Export sample records
mysqldump -u scuser -pscpass securechat users > sample_records.sql

# View users
mysql -u scuser -pscpass securechat -e "SELECT email, username FROM users;"
```

### Certificate Verification:
```bash
# View CA certificate
openssl x509 -in certs/ca_cert.pem -text -noout

# Verify server certificate
openssl verify -CAfile certs/ca_cert.pem certs/server_cert.pem

# Verify client certificate
openssl verify -CAfile certs/ca_cert.pem certs/client_cert.pem
```

### Create ZIP:
```bash
# Create ZIP (excluding secrets)
cd /home/taha/Desktop/Info-Sec-A2
zip -r securechat-assignment.zip securechat-skeleton/ \
  -x "*.git*" \
  -x "*.venv*" \
  -x "*.pyc" \
  -x "__pycache__/*" \
  -x "certs/*" \
  -x "transcripts/*" \
  -x "*.pem" \
  -x "*.key" \
  -x ".env"
```

## ⚠️ Important Notes

1. **Do not commit secrets**:
   - Certificates and keys (in `certs/` directory)
   - Database passwords (in `.env` file)
   - Transcripts (in `transcripts/` directory)

2. **Ensure .gitignore is correct**:
   - `*.pem`
   - `*.key`
   - `certs/`
   - `transcripts/`
   - `.env`
   - `__pycache__/`
   - `*.pyc`

3. **Test all features**:
   - Registration
   - Login
   - Chat messaging
   - Certificate validation
   - Replay protection
   - Signature verification
   - Non-repudiation

4. **Document everything**:
   - Setup instructions
   - Test results
   - Screenshots
   - Wireshark captures
   - Error messages

5. **Submit on time**:
   - Check submission deadline
   - Allow time for testing
   - Double-check all files
   - Verify all requirements are met

## 🎯 Grading Rubric Reference

### GitHub Workflow (20%):
- Fork accessible; ≥10 clear commits
- Proper README
- No secrets committed
- Sensible .gitignore

### PKI Setup & Certificates (20%):
- Root CA works
- Server & client certs issued
- Mutual verification
- Expiry/hostname checks
- Invalid/self-signed/expired certs rejected

### Registration & Login Security (20%):
- Per-user random salt ≥16B
- Store hex(sha256(salt||pwd))
- Credentials sent only after cert checks
- Under encryption
- No plaintext passwords in files/logs
- Constant-time compare

### Encrypted Chat (20%):
- DH after login
- K = Trunc16(SHA256(Ks))
- AES-128 used correctly with PKCS#7 padding
- Clean send/receive path
- Clear error handling

### Integrity, Authenticity & Non-Repudiation (10%):
- For each message: compute h = SHA256(seqno∥ts∥ct)
- RSA-sign h
- Verify every message
- Strict replay defense on seqno
- Append-only transcript
- SessionReceipt (signed transcript hash) produced
- Offline verification documented

### Testing & Evidence (10%):
- PCAP/screens show encrypted payloads
- Filters included
- Invalid/expired cert rejection
- Tamper + replay tests shown
- Steps reproducible by TA

Good luck with your submission!

