# Next Steps After Running QUICK_START.sh

## ✅ What's Already Done:
- ✓ Virtual environment created (`.venv`)
- ✓ .env file created
- ✓ Certificates generated (CA, server, client)

## 🔧 What You Need to Do Now:

### Step 1: Set Up MySQL Database

**Option A: Using Docker (Easiest - Recommended)**
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
```bash
# Install MySQL (if not installed)
sudo apt update
sudo apt install mysql-server

# Start MySQL
sudo systemctl start mysql

# Create database and user
sudo mysql << 'EOF'
CREATE DATABASE securechat;
CREATE USER 'scuser'@'localhost' IDENTIFIED BY 'scpass';
GRANT ALL PRIVILEGES ON securechat.* TO 'scuser'@'localhost';
FLUSH PRIVILEGES;
EOF
```

### Step 2: Initialize Database

```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
source .venv/bin/activate
python3 -m app.storage.db --init
```

Expected output:
```
Database initialized successfully.
```

### Step 3: Start the Server

**Terminal 1 - Server:**
```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
source .venv/bin/activate
python3 -m app.server
```

Expected output:
```
Database initialized successfully.
Server listening on localhost:8888
```

**Important:** Use `python3` not `python` (your system doesn't have `python` command)

### Step 4: Start the Client

**Terminal 2 - Client:**
```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
source .venv/bin/activate
python3 -m app.client
```

Expected output:
```
Connected to server at localhost:8888
Server certificate validated: OK
Session key established

=== Authentication ===
Register (r) or Login (l)? 
```

### Step 5: Test the System

1. **Register a user:**
   - Type `r` and press Enter
   - Enter email: `test@example.com`
   - Enter username: `testuser`
   - Enter password: `testpass123`

2. **Login:**
   - Restart the client (Ctrl+C and run again)
   - Type `l` and press Enter
   - Enter email: `test@example.com`
   - Enter password: `testpass123`

3. **Send messages:**
   - Type messages and press Enter
   - Type `quit` to exit

## 🎯 Quick Command Summary

```bash
# 1. Set up MySQL (Docker)
docker run -d --name securechat-db -e MYSQL_ROOT_PASSWORD=rootpass -e MYSQL_DATABASE=securechat -e MYSQL_USER=scuser -e MYSQL_PASSWORD=scpass -p 3306:3306 mysql:8

# 2. Initialize database
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
source .venv/bin/activate
python3 -m app.storage.db --init

# 3. Start server (Terminal 1)
python3 -m app.server

# 4. Start client (Terminal 2)
python3 -m app.client
```

## 🔍 Troubleshooting

### Issue: "Command 'python' not found"
**Solution:** Use `python3` instead of `python`

### Issue: "ModuleNotFoundError"
**Solution:** Make sure virtual environment is activated:
```bash
source .venv/bin/activate
```

### Issue: "Database connection failed"
**Solution:** 
1. Check if MySQL is running: `docker ps` (for Docker) or `sudo systemctl status mysql` (for local)
2. Verify database exists: `docker exec -it securechat-db mysql -u scuser -pscpass -e "SHOW DATABASES;"`
3. Check .env file has correct credentials

### Issue: "Port 3306 already in use"
**Solution:**
1. Stop existing MySQL: `docker stop securechat-db` or `sudo systemctl stop mysql`
2. Or use a different port in .env file

## 📝 Notes

- Always use `python3` not `python`
- Always activate virtual environment: `source .venv/bin/activate`
- Make sure MySQL is running before starting server
- Use two separate terminals for server and client

Good luck! 🎉

