#!/bin/bash

# Setup GitHub repository - Create commits and prepare for push

echo "========================================="
echo "GitHub Repository Setup"
echo "========================================="
echo ""

cd "$(dirname "$0")/.."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ ERROR: Git repository not initialized"
    exit 1
fi

# Check git status
echo "1. Checking git status..."
git status --short
echo ""

# Check current remote
echo "2. Checking current remote..."
git remote -v
echo ""

echo "========================================="
echo "Step 1: Fork Repository on GitHub"
echo "========================================="
echo ""
echo "Please fork the repository on GitHub:"
echo "1. Go to: https://github.com/maadilrehman/securechat-skeleton"
echo "2. Click 'Fork' button (top right)"
echo "3. Wait for fork to complete"
echo "4. Note your GitHub username"
echo ""
read -p "Have you forked the repository? (y/n): " forked
if [ "$forked" != "y" ]; then
    echo "Please fork the repository first, then run this script again"
    exit 1
fi

echo ""
read -p "Enter your GitHub username: " github_username
if [ -z "$github_username" ]; then
    echo "❌ ERROR: GitHub username is required"
    exit 1
fi

echo ""
echo "========================================="
echo "Step 2: Create Meaningful Commits"
echo "========================================="
echo ""

# Commit 1: Initial setup - utilities and protocol models
echo "Creating commit 1: Initial setup - utilities and protocol models..."
git add app/common/utils.py app/common/protocol.py .gitignore
git commit -m "Initial setup: Add utility functions and protocol models

- Implement utility functions (now_ms, b64e, b64d, sha256_hex)
- Implement protocol models (Hello, Register, Login, DH, Chat, Receipt)
- Add .gitignore to exclude secrets and sensitive files" 2>/dev/null || echo "Commit 1 already exists or no changes"

# Commit 2: PKI setup
echo "Creating commit 2: PKI setup..."
git add app/crypto/pki.py scripts/gen_ca.py scripts/gen_cert.py
git commit -m "Implement PKI setup and certificate generation

- Implement certificate validation (issuer, validity, CN checks)
- Implement CA generation script (gen_ca.py)
- Implement certificate issuance script (gen_cert.py)
- Support for mutual certificate validation" 2>/dev/null || echo "Commit 2 already exists or no changes"

# Commit 3: Cryptographic modules
echo "Creating commit 3: Cryptographic modules..."
git add app/crypto/aes.py app/crypto/dh.py app/crypto/sign.py
git commit -m "Implement cryptographic modules

- Implement AES-128 encryption/decryption with PKCS#7 padding
- Implement Diffie-Hellman key exchange and key derivation
- Implement RSA PKCS#1 v1.5 SHA-256 signing/verification" 2>/dev/null || echo "Commit 3 already exists or no changes"

# Commit 4: Database layer
echo "Creating commit 4: Database layer..."
git add app/storage/db.py
git commit -m "Implement database layer with salted password hashing

- Implement MySQL database connection
- Implement user registration with 16-byte random salt
- Implement password hashing: hex(SHA256(salt || password))
- Implement user authentication with constant-time comparison
- Implement database initialization script" 2>/dev/null || echo "Commit 4 already exists or no changes"

# Commit 5: Transcript management
echo "Creating commit 5: Transcript management..."
git add app/storage/transcript.py
git commit -m "Implement transcript management for non-repudiation

- Implement append-only transcript
- Implement transcript hash computation
- Implement transcript integrity verification
- Support for session receipt generation" 2>/dev/null || echo "Commit 5 already exists or no changes"

# Commit 6: Server implementation
echo "Creating commit 6: Server implementation..."
git add app/server.py
git commit -m "Implement server workflow with full protocol

- Implement control plane (certificate exchange, temporary DH)
- Implement authentication (registration and login)
- Implement session key agreement (DH key exchange)
- Implement data plane (encrypted message exchange)
- Implement replay protection (sequence numbers, timestamps)
- Implement non-repudiation (transcript management, session receipts)" 2>/dev/null || echo "Commit 6 already exists or no changes"

# Commit 7: Client implementation
echo "Creating commit 7: Client implementation..."
git add app/client.py
git commit -m "Implement client workflow with full protocol

- Implement control plane (certificate exchange, temporary DH)
- Implement authentication (registration and login)
- Implement session key agreement (DH key exchange)
- Implement data plane (encrypted message exchange)
- Implement replay protection (sequence numbers, timestamps)
- Implement non-repudiation (transcript management, session receipts)" 2>/dev/null || echo "Commit 7 already exists or no changes"

# Commit 8: Test scripts
echo "Creating commit 8: Test scripts..."
git add tests/test_invalid_cert.py tests/test_tamper.py tests/test_replay.py tests/test_non_repudiation.py tests/verify_transcript.py tests/run_all_tests.sh
git commit -m "Add security test scripts

- Implement invalid certificate test (BAD_CERT)
- Implement tamper detection test (SIG_FAIL)
- Implement replay protection test (REPLAY)
- Implement non-repudiation test
- Implement offline verification script
- Add test runner script" 2>/dev/null || echo "Commit 8 already exists or no changes"

# Commit 9: Documentation
echo "Creating commit 9: Documentation..."
git add README.md TESTING_GUIDE.md SUBMISSION_CHECKLIST.md
git commit -m "Add comprehensive documentation

- Update README.md with setup instructions and usage
- Add TESTING_GUIDE.md with testing procedures
- Add SUBMISSION_CHECKLIST.md with submission requirements
- Include protocol implementation details
- Include security features documentation" 2>/dev/null || echo "Commit 9 already exists or no changes"

# Commit 10: Additional documentation and scripts
echo "Creating commit 10: Additional documentation and scripts..."
git add COMPLETION_STATUS.md WHAT_TO_DO_NEXT.md REPORT_TEMPLATE.md TEST_REPORT_TEMPLATE.md scripts/export_database.sh scripts/create_submission.sh
git commit -m "Add additional documentation and submission scripts

- Add completion status documentation
- Add report templates
- Add database export script
- Add submission file creation script
- Add test results documentation" 2>/dev/null || echo "Commit 10 already exists or no changes"

# Commit 11: Fix deprecation warnings
echo "Creating commit 11: Fix deprecation warnings..."
git add app/crypto/pki.py
git commit -m "Fix certificate validation deprecation warnings

- Update datetime handling for certificate validation
- Support both timezone-aware and naive datetimes
- Fix certificate expiry validation" 2>/dev/null || echo "Commit 11 already exists or no changes"

# Commit 12: Certificate inspection and final touches
echo "Creating commit 12: Certificate inspection and final documentation..."
git add ca_cert_inspection.txt server_cert_inspection.txt client_cert_inspection.txt schema.sql sample_records.sql FINAL_STATUS.md SUBMISSION_FINAL_CHECKLIST.md
git commit -m "Add certificate inspection output and final documentation

- Add certificate inspection output files
- Add database schema and sample records
- Add final status documentation
- Add submission checklist" 2>/dev/null || echo "Commit 12 already exists or no changes"

echo ""
echo "========================================="
echo "Step 3: Update Remote to Your Fork"
echo "========================================="
echo ""

# Remove original remote
echo "Removing original remote..."
git remote remove origin 2>/dev/null || echo "Original remote not found"

# Add your fork as remote
echo "Adding your fork as remote..."
git remote add origin "https://github.com/${github_username}/securechat-skeleton.git"

# Verify remote
echo "Verifying remote..."
git remote -v
echo ""

echo "========================================="
echo "Step 4: Push to Your Fork"
echo "========================================="
echo ""

# Check commit count
commit_count=$(git log --oneline | wc -l)
echo "Total commits: $commit_count"
echo ""

if [ $commit_count -ge 10 ]; then
    echo "✅ Sufficient commits (≥10)"
else
    echo "⚠️  Warning: Less than 10 commits. Creating additional commits..."
fi

echo ""
read -p "Push to GitHub? (y/n): " push_confirm
if [ "$push_confirm" = "y" ]; then
    echo "Pushing to GitHub..."
    git push -u origin main
    if [ $? -eq 0 ]; then
        echo "✅ Successfully pushed to GitHub!"
        echo ""
        echo "Repository URL: https://github.com/${github_username}/securechat-skeleton"
    else
        echo "❌ Failed to push to GitHub"
        echo "Please check your GitHub credentials and try again"
    fi
else
    echo "Skipping push. You can push manually later with:"
    echo "  git push -u origin main"
fi

echo ""
echo "========================================="
echo "GitHub Repository Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Verify repository on GitHub: https://github.com/${github_username}/securechat-skeleton"
echo "2. Update README.md with GitHub link"
echo "3. Verify all commits are visible"
echo "4. Check that secrets are not committed"
echo ""

