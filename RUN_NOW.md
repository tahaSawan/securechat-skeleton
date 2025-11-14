# 🚀 Run the System Now!

## ✅ Everything is Set Up:
- ✓ Virtual environment created
- ✓ Certificates generated
- ✓ MySQL database running
- ✓ Database initialized

## 🎯 Next Steps:

### Step 1: Start the Server

**Open Terminal 1 and run:**
```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
source .venv/bin/activate
python3 -m app.server
```

**Expected output:**
```
Database initialized successfully.
Server listening on localhost:8888
```

**Important:** 
- Use `python3` NOT `python`
- Make sure virtual environment is activated: `source .venv/bin/activate`

### Step 2: Start the Client

**Open Terminal 2 (new terminal) and run:**
```bash
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
source .venv/bin/activate
python3 -m app.client
```

**Expected output:**
```
Connected to server at localhost:8888
Server certificate validated: OK
Session key established

=== Authentication ===
Register (r) or Login (l)? 
```

### Step 3: Test Registration

**In Terminal 2 (client):**
1. Type `r` and press Enter
2. Enter email: `test@example.com`
3. Enter username: `testuser`
4. Enter password: `testpass123`

**Expected output:**
```
Registration successful: User registered successfully
```

### Step 4: Test Login

**In Terminal 2 (client):**
1. Restart the client (press Ctrl+C, then run again):
   ```bash
   python3 -m app.client
   ```
2. Type `l` and press Enter
3. Enter email: `test@example.com`
4. Enter password: `testpass123`

**Expected output:**
```
Login successful: Login successful
Session key established

=== Chat Session ===
Type messages to send, or 'quit' to exit.
```

### Step 5: Test Chat Messaging

**In Terminal 2 (client):**
1. Type: `Hello, this is a test message!`
2. Press Enter
3. Type: `This is message number 2`
4. Press Enter
5. Type: `quit` to exit

**Check Terminal 1 (server) - you should see:**
```
Client (testuser): Hello, this is a test message!
Client (testuser): This is message number 2
```

## 🔍 Verify Transcripts

After sending messages, check if transcripts were created:

```bash
ls -la transcripts/
```

You should see transcript files:
```
client_testuser_*.txt
server_testuser_*.txt
```

## 📋 Quick Command Reference

```bash
# Terminal 1 - Server
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
source .venv/bin/activate
python3 -m app.server

# Terminal 2 - Client
cd /home/taha/Desktop/Info-Sec-A2/securechat-skeleton
source .venv/bin/activate
python3 -m app.client
```

## ⚠️ Important Notes

1. **Always use `python3` not `python`** (your system doesn't have `python` command)
2. **Always activate virtual environment** (`source .venv/bin/activate`)
3. **Use two separate terminals** (one for server, one for client)
4. **Keep server running** (don't close Terminal 1)
5. **MySQL must be running** (check with `docker ps`)

## 🆘 Troubleshooting

### Issue: "Command 'python' not found"
**Solution:** Use `python3` instead of `python`

### Issue: "ModuleNotFoundError"
**Solution:** Make sure virtual environment is activated:
```bash
source .venv/bin/activate
```

### Issue: "Database connection failed"
**Solution:** 
1. Check MySQL is running: `docker ps | grep securechat-db`
2. If not running, start it: `docker start securechat-db`
3. Wait a few seconds for MySQL to be ready

### Issue: "Port already in use"
**Solution:** 
1. Check if server is already running: `lsof -ti:8888`
2. Kill existing process: `lsof -ti:8888 | xargs kill -9`
3. Or change port in `.env` file: `SERVER_PORT=8889`

## ✅ Success Checklist

- [ ] Server starts successfully
- [ ] Client connects successfully
- [ ] Registration works
- [ ] Login works
- [ ] Chat messages work
- [ ] Transcripts are created
- [ ] Session receipts are generated

## 🎉 You're Ready!

Just follow the steps above and you'll have the system running in no time!

Good luck! 🚀

