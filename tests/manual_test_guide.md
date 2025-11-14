# Manual Testing Guide

## Test Scenarios for Screenshots and Reports

### Test 1: Invalid Certificate Rejection (BAD_CERT)

#### Steps:
1. **Generate self-signed certificate**:
   ```bash
   openssl req -x509 -newkey rsa:2048 \
     -keyout certs/test_invalid_key.pem \
     -out certs/test_invalid_cert.pem \
     -days 365 -nodes \
     -subj "/CN=invalid.local"
   ```

2. **Modify client to use invalid certificate**:
   - Edit `app/client.py`
   - Change `self.client_cert_path = "certs/test_invalid_cert.pem"`
   - Change `self.client_key_path = "certs/test_invalid_key.pem"`

3. **Start server**:
   ```bash
   python3 -m app.server
   ```

4. **Start client**:
   ```bash
   python3 -m app.client
   ```

5. **Expected Result**: 
   - Server should reject connection
   - Error: `BAD_CERT: Certificate not issued by trusted CA (issuer mismatch)`

6. **Take Screenshot**: 
   - Screenshot of BAD_CERT error
   - Screenshot of server log showing rejection

#### Revert Changes:
- Change client back to use original certificates
- Restore `app/client.py` to original state

---

### Test 2: Tamper Detection (SIG_FAIL)

#### Steps:
1. **Start server**:
   ```bash
   python3 -m app.server
   ```

2. **Create modified client** (tamper with ciphertext):
   - Copy `app/client.py` to `app/client_tamper.py`
   - Modify `send_chat_message` to tamper with ciphertext:
     ```python
     # After encryption, tamper with ciphertext
     ciphertext = encrypt_aes128(plaintext_bytes, session_key)
     # Tamper: flip a bit
     tampered_ciphertext = bytearray(ciphertext)
     tampered_ciphertext[0] ^= 1  # Flip first bit
     ciphertext = bytes(tampered_ciphertext)
     ```

3. **Start modified client**:
   ```bash
   python3 -m app.client_tamper.py
   ```

4. **Login and send message**:
   - Login with credentials
   - Send a message
   - Message should be rejected

5. **Expected Result**:
   - Server should reject message
   - Error: `SIG_FAIL: Signature verification failed`

6. **Take Screenshot**:
   - Screenshot of SIG_FAIL error
   - Screenshot of server log showing rejection

---

### Test 3: Replay Protection (REPLAY)

#### Steps:
1. **Start server**:
   ```bash
   python3 -m app.server
   ```

2. **Create replay client**:
   - Copy `app/client.py` to `app/client_replay.py`
   - Modify to send same message twice with same seqno:
     ```python
     # Send message with seqno=1
     self.send_chat_message("Hello", session_key, transcript, peer_cert_fingerprint)
     # Reset seqno and send again
     self.seqno = 1
     self.send_chat_message("Hello", session_key, transcript, peer_cert_fingerprint)
     ```

3. **Start replay client**:
   ```bash
   python3 -m app.client_replay.py
   ```

4. **Login and send message**:
   - Login with credentials
   - Send a message
   - Send same message again

5. **Expected Result**:
   - First message should be accepted
   - Second message should be rejected
   - Error: `REPLAY: Expected seqno 2, got 1`

6. **Take Screenshot**:
   - Screenshot of REPLAY error
   - Screenshot of server log showing rejection

---

### Test 4: Wireshark Capture

#### Steps:
1. **Start Wireshark**:
   ```bash
   wireshark
   ```

2. **Configure Capture**:
   - Select loopback interface (lo)
   - Set display filter: `tcp.port == 8888`
   - Start capture

3. **Start server**:
   ```bash
   python3 -m app.server
   ```

4. **Start client**:
   ```bash
   python3 -m app.client
   ```

5. **Perform Actions**:
   - Register a user
   - Login
   - Send messages

6. **Stop Capture**:
   - Stop Wireshark capture
   - Save as `securechat.pcap`

7. **Analyze Capture**:
   - Verify all payloads are encrypted
   - No plaintext visible
   - Certificate exchange encrypted
   - Credential exchange encrypted
   - Chat messages encrypted

8. **Take Screenshots**:
   - Screenshot of Wireshark showing encrypted payloads
   - Screenshot of display filter
   - Screenshot of packet analysis

---

### Test 5: Non-Repudiation Verification

#### Steps:
1. **Run system and generate transcripts**:
   - Start server and client
   - Login and send messages
   - End session
   - Transcripts should be created

2. **Verify transcript**:
   ```bash
   python3 tests/verify_transcript.py \
     --transcript transcripts/client_testuser_*.txt \
     --cert certs/client_cert.pem \
     --verify-messages \
     --test-modification
   ```

3. **Export transcript and receipt**:
   - Copy transcript file
   - Copy session receipt (from session end)
   - Verify transcript hash
   - Verify receipt signature

4. **Test modification**:
   - Modify transcript file
   - Verify hash changes
   - Verify receipt signature fails

5. **Take Screenshots**:
   - Screenshot of transcript file
   - Screenshot of session receipt
   - Screenshot of offline verification
   - Screenshot of modification test

---

### Test 6: Certificate Inspection

#### Steps:
1. **Inspect CA Certificate**:
   ```bash
   openssl x509 -in certs/ca_cert.pem -text -noout
   ```

2. **Inspect Server Certificate**:
   ```bash
   openssl x509 -in certs/server_cert.pem -text -noout
   ```

3. **Inspect Client Certificate**:
   ```bash
   openssl x509 -in certs/client_cert.pem -text -noout
   ```

4. **Verify Certificates**:
   ```bash
   openssl verify -CAfile certs/ca_cert.pem certs/server_cert.pem
   openssl verify -CAfile certs/ca_cert.pem certs/client_cert.pem
   ```

5. **Take Screenshots**:
   - Screenshot of CA certificate inspection
   - Screenshot of server certificate inspection
   - Screenshot of client certificate inspection
   - Screenshot of certificate verification

---

## Screenshots Checklist

### Required Screenshots:
- [ ] Certificate generation output
- [ ] Registration process
- [ ] Login process
- [ ] Chat messages
- [ ] Transcript files
- [ ] Session receipts
- [ ] Invalid certificate test (BAD_CERT)
- [ ] Tamper test (SIG_FAIL)
- [ ] Replay test (REPLAY)
- [ ] Wireshark capture (encrypted payloads)
- [ ] Certificate inspection output
- [ ] Offline verification
- [ ] Transcript modification test

### Screenshot Naming:
- `certificate_generation.png`
- `registration.png`
- `login.png`
- `chat_messages.png`
- `transcripts.png`
- `session_receipts.png`
- `invalid_cert_bad_cert.png`
- `tamper_test_sig_fail.png`
- `replay_test_replay.png`
- `wireshark_encrypted.png`
- `certificate_inspection.png`
- `offline_verification.png`
- `transcript_modification.png`

---

## Test Evidence Files

### Required Files:
- [ ] `securechat.pcap` - Wireshark capture
- [ ] `transcripts/` - Transcript files
- [ ] `test_results.md` - Test results
- [ ] Screenshots (all PNG files)
- [ ] Certificate inspection output (text files)

---

## Test Execution Summary

### Automated Tests: ✅ PASSED
- Invalid Certificate: ✅ PASSED
- Tamper Detection: ✅ PASSED
- Replay Protection: ✅ PASSED
- Non-Repudiation: ✅ PASSED
- Offline Verification: ✅ PASSED

### Manual Tests: ⏳ NEEDS TO BE DONE
- [ ] Invalid Certificate with Server (BAD_CERT)
- [ ] Tamper Detection with Server (SIG_FAIL)
- [ ] Replay Protection with Server (REPLAY)
- [ ] Wireshark Capture (encrypted payloads)
- [ ] Certificate Inspection
- [ ] Offline Verification
- [ ] Transcript Modification Test

---

## Notes

1. **All automated tests are passing** ✅
2. **Manual tests need to be done** ⏳
3. **Screenshots need to be taken** ⏳
4. **Wireshark capture needs to be done** ⏳
5. **Reports need to be written** ⏳

Good luck with testing! 🎉

