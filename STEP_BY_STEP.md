# Step-by-Step Instructions

## 🚀 Quick Start (Automated)

### Option 1: Use the Quick Start Script
```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
./QUICK_START.sh
```

This will automatically:
1. Create virtual environment
2. Install dependencies
3. Create .env file
4. Generate certificates
5. Initialize database

### Option 2: Manual Setup (Step by Step)

## 📋 Manual Setup Steps

### Step 1: Set Up Environment
```bash
# Navigate to project directory
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Create .env File
Create a file named `.env` in the project root:
```bash
cat > .env << 'EOF'
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=scuser
DB_PASSWORD=scpass
DB_NAME=securechat

# Server Configuration
SERVER_HOST=localhost
SERVER_PORT=8888

# Certificate Paths
CA_CERT_PATH=certs/ca_cert.pem
CA_KEY_PATH=certs/ca_key.pem
SERVER_CERT_PATH=certs/server_cert.pem
SERVER_KEY_PATH=certs/server_key.pem
CLIENT_CERT_PATH=certs/client_cert.pem
CLIENT_KEY_PATH=certs/client_key.pem

# Transcript Directory
TRANSCRIPT_DIR=transcripts

# Server CN
SERVER_CN=server.local
EOF
```

### Step 3: Set Up MySQL Database

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
```bash
# Start MySQL
sudo systemctl start mysql

# Create database and user
mysql -u root -p << 'EOF'
CREATE DATABASE securechat;
CREATE USER 'scuser'@'localhost' IDENTIFIED BY 'scpass';
GRANT ALL PRIVILEGES ON securechat.* TO 'scuser'@'localhost';
FLUSH PRIVILEGES;
EOF
```

### Step 4: Initialize Database
```bash
python -m app.storage.db --init
```

Expected output:
```
Database initialized successfully.
```

### Step 5: Generate Certificates
```bash
# Generate Root CA
python scripts/gen_ca.py --name "FAST-NU Root CA"

# Generate Server Certificate
python scripts/gen_cert.py --cn server.local --out server --server

# Generate Client Certificate
python scripts/gen_cert.py --cn client.local --out client
```

### Step 6: Verify Certificates
```bash
# Verify server certificate
openssl verify -CAfile certs/ca_cert.pem certs/server_cert.pem

# Verify client certificate
openssl verify -CAfile certs/ca_cert.pem certs/client_cert.pem
```

Both should output: `OK`

## 🧪 Testing the System

### Step 7: Start the Server
Open Terminal 1:
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

### Step 8: Start the Client
Open Terminal 2:
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

### Step 9: Test Registration
In Terminal 2 (client):
1. Type `r` and press Enter
2. Enter email: `test@example.com`
3. Enter username: `testuser`
4. Enter password: `testpass123`

Expected output:
```
Registration successful: User registered successfully
```

### Step 10: Test Login
Restart the client (Ctrl+C and run again):
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

### Step 11: Test Chat Messaging
In Terminal 2 (client):
1. Type: `Hello, this is a test message!`
2. Press Enter
3. Type: `This is message number 2`
4. Press Enter
5. Type: `quit` to exit

Check Terminal 1 (server) - you should see:
```
Client (testuser): Hello, this is a test message!
Client (testuser): This is message number 2
```

### Step 12: Verify Transcripts
```bash
ls -la transcripts/
```

You should see transcript files:
```
client_testuser_*.txt
server_testuser_*.txt
```

### Step 13: View Transcripts
```bash
cat transcripts/client_testuser_*.txt
cat transcripts/server_testuser_*.txt
```

## 🔒 Security Testing

### Step 14: Test Invalid Certificate
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:2048 \
  -keyout certs/invalid_key.pem \
  -out certs/invalid_cert.pem \
  -days 365 -nodes \
  -subj "/CN=invalid.local"

# Temporarily modify client to use invalid certificate
# (Edit app/client.py to use invalid_cert.pem)
# Server should reject with BAD_CERT error
```

### Step 15: Test Replay Protection
1. Start server and client
2. Send a message
3. Try to resend the same message with the same sequence number
4. Server should reject with `REPLAY` error

### Step 16: Test Signature Verification
1. Start server and client
2. Send a message
3. Modify the ciphertext in transit
4. Server should reject with `SIG_FAIL` error

### Step 17: Wireshark Capture
1. Start Wireshark
2. Capture traffic on `localhost` (loopback interface)
3. Start server and client
4. Perform registration/login and send messages
5. Verify all payloads are encrypted (no plaintext visible)
6. Save capture as `securechat.pcap`

## 📦 Preparing Submission

### Step 18: Export Database
```bash
# Export schema
mysqldump -u scuser -pscpass securechat --no-data > schema.sql

# Export sample records
mysqldump -u scuser -pscpass securechat users > sample_records.sql

# View users
mysql -u scuser -pscpass securechat -e "SELECT email, username FROM users;"
```

### Step 19: Create GitHub Repository
1. Fork the repository: https://github.com/maadilrehman/securechat-skeleton
2. Push your changes to your fork
3. Make sure you have at least 10 meaningful commits
4. Get the link to your repository

### Step 20: Create ZIP File
```bash
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

### Step 21: Prepare Reports
1. **Report** (`RollNumber-FullName-Report-A02.docx`):
   - Protocol implementation details
   - Security features (CIANR)
   - Certificate validation
   - Key exchange process
   - Message encryption and signing
   - Non-repudiation mechanism
   - Screenshots

2. **Test Report** (`RollNumber-FullName-TestReport-A02.docx`):
   - Wireshark captures
   - Invalid certificate test
   - Tamper test
   - Replay test
   - Non-repudiation verification
   - Screenshots and evidence

## 📤 Submission Checklist

### Files to Submit on GCR:
- [ ] ZIP file of GitHub repository
- [ ] `schema.sql` - Database schema
- [ ] `sample_records.sql` - Sample records
- [ ] `README.md` - Updated README
- [ ] `RollNumber-FullName-Report-A02.docx` - Report
- [ ] `RollNumber-FullName-TestReport-A02.docx` - Test Report
- [ ] GitHub repository link

### Before Submission:
- [ ] All code is tested and working
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
- [ ] Reports are prepared
- [ ] Test evidence is included

## 🎯 Quick Command Reference

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Database
docker run -d --name securechat-db -e MYSQL_ROOT_PASSWORD=rootpass -e MYSQL_DATABASE=securechat -e MYSQL_USER=scuser -e MYSQL_PASSWORD=scpass -p 3306:3306 mysql:8
python -m app.storage.db --init

# Certificates
python scripts/gen_ca.py --name "FAST-NU Root CA"
python scripts/gen_cert.py --cn server.local --out server --server
python scripts/gen_cert.py --cn client.local --out client

# Testing
python -m app.server  # Terminal 1
python -m app.client  # Terminal 2

# Database Export
mysqldump -u scuser -pscpass securechat --no-data > schema.sql
mysqldump -u scuser -pscpass securechat users > sample_records.sql

# Create ZIP
zip -r securechat-assignment.zip securechat-skeleton/ -x "*.git*" -x "*.venv*" -x "*.pyc" -x "__pycache__/*" -x "certs/*" -x "transcripts/*" -x "*.pem" -x "*.key" -x ".env"
```

## 🆘 Troubleshooting

### Issue: Database Connection Failed
```bash
# Check MySQL is running
systemctl status mysql
# or
docker ps

# Test connection
mysql -u scuser -pscpass securechat -e "SELECT 1;"
```

### Issue: Certificate Validation Failed
```bash
# Verify certificates exist
ls -la certs/

# Verify certificates are signed by CA
openssl verify -CAfile certs/ca_cert.pem certs/server_cert.pem
openssl verify -CAfile certs/ca_cert.pem certs/client_cert.pem
```

### Issue: Port Already in Use
```bash
# Kill process on port 8888
lsof -ti:8888 | xargs kill -9

# Or change port in .env file
SERVER_PORT=8889
```

### Issue: Module Not Found
```bash
# Make sure you're in the project root
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton

# Activate virtual environment
source .venv/bin/activate

# Run from project root
python -m app.server
```

## 📞 Need Help?

1. Check `TESTING_GUIDE.md` for detailed instructions
2. Check `SUBMISSION_CHECKLIST.md` for submission requirements
3. Check `README.md` for setup and usage instructions
4. Review error messages and check troubleshooting section

Good luck with your assignment! 🎉

