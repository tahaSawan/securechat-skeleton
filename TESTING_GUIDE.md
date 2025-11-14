# Step-by-Step Testing and Submission Guide

## Phase 1: Environment Setup

### Step 1.1: Navigate to Project Directory
```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
```

### Step 1.2: Create Python Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 1.3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 1.4: Create .env File
Create a file named `.env` in the project root with the following content:

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

# Server CN (Common Name)
SERVER_CN=server.local
```

## Phase 2: Database Setup

### Step 2.1: Start MySQL Database

**Option A: Using Docker (Recommended)**
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

**Option B: Using Local MySQL**
1. Make sure MySQL is installed and running
2. Create database and user:
```sql
CREATE DATABASE securechat;
CREATE USER 'scuser'@'localhost' IDENTIFIED BY 'scpass';
GRANT ALL PRIVILEGES ON securechat.* TO 'scuser'@'localhost';
FLUSH PRIVILEGES;
```

### Step 2.2: Initialize Database Tables
```bash
python -m app.storage.db --init
```

Expected output:
```
Database initialized successfully.
```

### Step 2.3: Verify Database Setup
```bash
mysql -u scuser -pscpass securechat -e "SHOW TABLES;"
```

Expected output:
```
+---------------------+
| Tables_in_securechat|
+---------------------+
| users               |
+---------------------+
```

## Phase 3: Certificate Generation

### Step 3.1: Generate Root CA
```bash
python scripts/gen_ca.py --name "FAST-NU Root CA"
```

Expected output:
```
Generating RSA-2048 private key...
Creating self-signed CA certificate: FAST-NU Root CA
CA private key saved to: certs/ca_key.pem
CA certificate saved to: certs/ca_cert.pem

CA Certificate Information:
  Subject: ...
  Issuer: ...
  Serial Number: ...
  Valid From: ...
  Valid To: ...
  Fingerprint (SHA-256): ...

CA generation completed successfully!
```

### Step 3.2: Generate Server Certificate
```bash
python scripts/gen_cert.py --cn server.local --out server --server
```

Expected output:
```
Loading CA certificate from: certs/ca_cert.pem
Loading CA private key from: certs/ca_key.pem
Generating RSA-2048 private key...
Creating certificate: server.local
Private key saved to: certs/server_key.pem
Certificate saved to: certs/server_cert.pem

Certificate Information:
  Subject: ...
  Issuer: ...
  Serial Number: ...
  Valid From: ...
  Valid To: ...
  Fingerprint (SHA-256): ...

Certificate generation completed successfully!
```

### Step 3.3: Generate Client Certificate
```bash
python scripts/gen_cert.py --cn client.local --out client
```

Expected output:
```
Loading CA certificate from: certs/ca_cert.pem
Loading CA private key from: certs/ca_key.pem
Generating RSA-2048 private key...
Creating certificate: client.local
Private key saved to: certs/client_key.pem
Certificate saved to: certs/client_cert.pem

Certificate Information:
  Subject: ...
  Issuer: ...
  Serial Number: ...
  Valid From: ...
  Valid To: ...
  Fingerprint (SHA-256): ...

Certificate generation completed successfully!
```

### Step 3.4: Verify Certificates
```bash
# View CA certificate
openssl x509 -in certs/ca_cert.pem -text -noout | head -30

# Verify server certificate is signed by CA
openssl verify -CAfile certs/ca_cert.pem certs/server_cert.pem

# Verify client certificate is signed by CA
openssl verify -CAfile certs/ca_cert.pem certs/client_cert.pem
```

Expected output:
```
certs/server_cert.pem: OK
certs/client_cert.pem: OK
```

## Phase 4: Testing the System

### Step 4.1: Start the Server
Open a new terminal window and run:
```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
source .venv/bin/activate
python -m app.server
```

Expected output:
```
Database initialized successfully.
Server listening on localhost:8888
```

### Step 4.2: Start the Client
Open another terminal window and run:
```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
source .venv/bin/activate
python -m app.client
```

Expected output:
```
Connected to server at localhost:8888
Server certificate validated: OK
Session key established

=== Authentication ===
Register (r) or Login (l)? 
```

### Step 4.3: Test Registration
In the client terminal:
1. Type `r` and press Enter
2. Enter email: `test@example.com`
3. Enter username: `testuser`
4. Enter password: `testpass123`

Expected output:
```
Registration successful: User registered successfully
```

### Step 4.4: Test Login
Restart the client (or create a new connection):
1. Type `l` and press Enter
2. Enter email: `test@example.com`
3. Enter password: `testpass123`

Expected output:
```
Login successful: Login successful
Session key established

=== Chat Session ===
Type messages to send, or 'quit' to exit.
```

### Step 4.5: Test Chat Messaging
1. Type a message: `Hello, this is a test message!`
2. Press Enter
3. Type another message: `This is message number 2`
4. Press Enter
5. Type `quit` to exit

Expected output (server side):
```
Client (testuser): Hello, this is a test message!
Client (testuser): This is message number 2
```

### Step 4.6: Verify Transcripts
Check if transcript files were created:
```bash
ls -la transcripts/
```

Expected output:
```
-rw-r--r-- 1 user user 1234 Dec 10 10:00 client_testuser_1234567890.txt
-rw-r--r-- 1 user user 1234 Dec 10 10:00 server_testuser_1234567890.txt
```

### Step 4.7: Verify Session Receipts
Check the transcript files for session receipts:
```bash
cat transcripts/client_testuser_*.txt
cat transcripts/server_testuser_*.txt
```

## Phase 5: Security Testing

### Step 5.1: Test Invalid Certificate
1. Generate a self-signed certificate:
```bash
openssl req -x509 -newkey rsa:2048 -keyout certs/invalid_key.pem -out certs/invalid_cert.pem -days 365 -nodes -subj "/CN=invalid.local"
```

2. Modify client to use invalid certificate (temporarily):
```bash
# Edit app/client.py to use invalid_cert.pem instead of client_cert.pem
# Or create a test script
```

3. Verify server rejects with `BAD_CERT` error

### Step 5.2: Test Replay Protection
1. Start server and client
2. Send a message
3. Try to resend the same message with the same sequence number
4. Verify server rejects with `REPLAY` error

### Step 5.3: Test Signature Verification
1. Start server and client
2. Send a message
3. Modify the ciphertext in transit (using a proxy or modified client)
4. Verify server rejects with `SIG_FAIL` error

### Step 5.4: Wireshark Capture
1. Start Wireshark
2. Capture traffic on `localhost` (loopback interface)
3. Start server and client
4. Perform registration/login and send messages
5. Verify all payloads are encrypted (no plaintext visible)

## Phase 6: Database Export

### Step 6.1: Export Database Schema
```bash
mysqldump -u scuser -pscpass securechat --no-data > schema.sql
```

### Step 6.2: Export Sample Records
```bash
mysqldump -u scuser -pscpass securechat users > sample_records.sql
```

### Step 6.3: View Sample Records
```bash
mysql -u scuser -pscpass securechat -e "SELECT email, username, LENGTH(salt) as salt_length, LENGTH(pwd_hash) as hash_length FROM users;"
```

## Phase 7: Prepare Submission Files

### Step 7.1: Create GitHub Repository
1. Fork the repository: https://github.com/maadilrehman/securechat-skeleton
2. Push your changes to your fork
3. Make sure you have at least 10 meaningful commits

### Step 7.2: Create ZIP of Repository
```bash
cd /home/taha/Desktop/Info-Sec-A2
zip -r securechat-assignment.zip securechat-skeleton/ -x "*.git*" -x "*.venv*" -x "*.pyc" -x "__pycache__/*" -x "certs/*" -x "transcripts/*" -x "*.pem" -x "*.key"
```

### Step 7.3: Create Database Dump
```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
mysqldump -u scuser -pscpass securechat > database_dump.sql
```

### Step 7.4: Create Test Evidence
1. Screenshots of:
   - Certificate generation
   - Registration/login
   - Chat messages
   - Transcripts
   - Session receipts
2. Wireshark capture file (.pcap)
3. Test results (invalid cert, replay, tamper tests)

## Phase 8: Required Deliverables

### 8.1: GitHub Repository
- Fork of the repository
- At least 10 meaningful commits
- Complete implementation
- Updated README.md

### 8.2: Database Files
- `schema.sql` - Database schema
- `sample_records.sql` - Sample user records
- `database_dump.sql` - Complete database dump

### 8.3: Documentation
- `README.md` - Updated with setup, usage, and test outputs
- Link to your GitHub repository

### 8.4: Report
- `RollNumber-FullName-Report-A02.docx`
- Should include:
  - Protocol implementation details
  - Security features (CIANR)
  - Certificate validation
  - Key exchange process
  - Message encryption and signing
  - Non-repudiation mechanism
  - Test results

### 8.5: Test Report
- `RollNumber-FullName-TestReport-A02.docx`
- Should include:
  - Wireshark captures (encrypted payloads)
  - Invalid certificate test results
  - Tamper test results
  - Replay test results
  - Non-repudiation verification
  - Screenshots and evidence

## Phase 9: Verification Checklist

- [ ] All code is implemented and tested
- [ ] Certificates are generated correctly
- [ ] Database is set up and working
- [ ] Registration and login work
- [ ] Chat messages are encrypted
- [ ] Signatures are verified
- [ ] Replay protection works
- [ ] Transcripts are generated
- [ ] Session receipts are created
- [ ] Wireshark shows encrypted payloads
- [ ] Invalid certificates are rejected
- [ ] Tamper test fails as expected
- [ ] Replay test fails as expected
- [ ] GitHub repository has 10+ commits
- [ ] README.md is updated
- [ ] Database dumps are created
- [ ] Reports are prepared
- [ ] Test report includes evidence

## Troubleshooting

### Issue: Database Connection Failed
**Solution:**
- Check MySQL is running: `systemctl status mysql` or `docker ps`
- Verify credentials in `.env` file
- Check database exists: `mysql -u scuser -pscpass -e "SHOW DATABASES;"`

### Issue: Certificate Validation Failed
**Solution:**
- Verify CA certificate exists: `ls -la certs/ca_cert.pem`
- Verify server/client certificates are signed by CA
- Check certificate validity period
- Verify Common Name (CN) matches expected value

### Issue: Import Errors
**Solution:**
- Activate virtual environment: `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python3 --version` (should be 3.8+)

### Issue: Port Already in Use
**Solution:**
- Change port in `.env` file
- Kill existing process: `lsof -ti:8888 | xargs kill -9`
- Use different port: `SERVER_PORT=8889`

### Issue: Module Not Found
**Solution:**
- Check you're in the project root directory
- Verify `app` directory exists
- Run from project root: `python -m app.server`
- Check `__init__.py` files exist in `app/` directories

## Next Steps

1. **Test the system thoroughly**
2. **Create test evidence** (screenshots, Wireshark captures)
3. **Prepare reports** (Report and Test Report)
4. **Export database** (schema and sample records)
5. **Create GitHub repository** (fork and push)
6. **Submit on GCR** (Google Classroom)

Good luck with your assignment!

