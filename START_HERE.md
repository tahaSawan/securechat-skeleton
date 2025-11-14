# 🚀 START HERE - Quick Commands

## What to Do Right Now

### 1. Run the Quick Start Script (Easiest Way)
```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
./QUICK_START.sh
```

This will set up everything automatically!

### 2. Or Follow These Manual Steps

#### Step 1: Setup Environment
```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Step 2: Create .env File
```bash
cat > .env << 'EOF'
DB_HOST=localhost
DB_PORT=3306
DB_USER=scuser
DB_PASSWORD=scpass
DB_NAME=securechat
SERVER_HOST=localhost
SERVER_PORT=8888
CA_CERT_PATH=certs/ca_cert.pem
CA_KEY_PATH=certs/ca_key.pem
SERVER_CERT_PATH=certs/server_cert.pem
SERVER_KEY_PATH=certs/server_key.pem
CLIENT_CERT_PATH=certs/client_cert.pem
CLIENT_KEY_PATH=certs/client_key.pem
TRANSCRIPT_DIR=transcripts
SERVER_CN=server.local
EOF
```

#### Step 3: Start MySQL (Choose One)

**Option A: Docker (Recommended)**
```bash
docker run -d --name securechat-db -e MYSQL_ROOT_PASSWORD=rootpass -e MYSQL_DATABASE=securechat -e MYSQL_USER=scuser -e MYSQL_PASSWORD=scpass -p 3306:3306 mysql:8
```

**Option B: Local MySQL**
```bash
sudo systemctl start mysql
mysql -u root -p << 'EOF'
CREATE DATABASE securechat;
CREATE USER 'scuser'@'localhost' IDENTIFIED BY 'scpass';
GRANT ALL PRIVILEGES ON securechat.* TO 'scuser'@'localhost';
FLUSH PRIVILEGES;
EOF
```

#### Step 4: Initialize Database
```bash
python -m app.storage.db --init
```

#### Step 5: Generate Certificates
```bash
python scripts/gen_ca.py --name "FAST-NU Root CA"
python scripts/gen_cert.py --cn server.local --out server --server
python scripts/gen_cert.py --cn client.local --out client
```

#### Step 6: Test the System

**Terminal 1 - Start Server:**
```bash
python -m app.server
```

**Terminal 2 - Start Client:**
```bash
python -m app.client
```

In Terminal 2:
1. Type `r` for register
2. Enter email: `test@example.com`
3. Enter username: `testuser`
4. Enter password: `testpass123`
5. Restart client and login with same credentials
6. Send some messages
7. Type `quit` to exit

## 📋 What to Submit

### On Google Classroom (GCR):

1. **ZIP File**: Downloaded ZIP of your GitHub repository
   ```bash
   cd /home/taha/Desktop/Info-Sec-A2
   zip -r securechat-assignment.zip securechat-skeleton/ -x "*.git*" -x "*.venv*" -x "*.pyc" -x "__pycache__/*" -x "certs/*" -x "transcripts/*" -x "*.pem" -x "*.key" -x ".env"
   ```

2. **Database Files**:
   ```bash
   mysqldump -u scuser -pscpass securechat --no-data > schema.sql
   mysqldump -u scuser -pscpass securechat users > sample_records.sql
   ```

3. **README.md**: Already updated with setup instructions

4. **Report**: `RollNumber-FullName-Report-A02.docx`
   - Protocol implementation
   - Security features (CIANR)
   - Screenshots

5. **Test Report**: `RollNumber-FullName-TestReport-A02.docx`
   - Wireshark captures
   - Invalid certificate test
   - Tamper test
   - Replay test
   - Non-repudiation verification

6. **GitHub Link**: Link to your forked repository

## 📚 More Information

- **Detailed Instructions**: See `STEP_BY_STEP.md`
- **Testing Guide**: See `TESTING_GUIDE.md`
- **Submission Checklist**: See `SUBMISSION_CHECKLIST.md`
- **Full README**: See `README.md`

## 🎯 Quick Checklist

- [ ] Environment setup complete
- [ ] Database initialized
- [ ] Certificates generated
- [ ] Server starts successfully
- [ ] Client connects successfully
- [ ] Registration works
- [ ] Login works
- [ ] Chat messages work
- [ ] Transcripts are generated
- [ ] Session receipts are created
- [ ] GitHub repository created
- [ ] Reports prepared
- [ ] Ready to submit

## 🆘 Need Help?

1. Check error messages carefully
2. Verify MySQL is running
3. Verify certificates are generated
4. Check `.env` file exists
5. Make sure virtual environment is activated
6. Review troubleshooting section in README.md

Good luck! 🎉

