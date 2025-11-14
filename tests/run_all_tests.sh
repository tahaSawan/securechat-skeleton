#!/bin/bash

# Run all security tests

echo "========================================="
echo "Running All Security Tests"
echo "========================================="
echo ""

cd "$(dirname "$0")/.."

# Activate virtual environment
source .venv/bin/activate

# Test 1: Invalid Certificate
echo "Test 1: Invalid Certificate Test"
echo "--------------------------------"
python3 tests/test_invalid_cert.py
echo ""

# Test 2: Tamper Detection
echo "Test 2: Tamper Detection Test"
echo "--------------------------------"
python3 tests/test_tamper.py
echo ""

# Test 3: Replay Protection
echo "Test 3: Replay Protection Test"
echo "--------------------------------"
python3 tests/test_replay.py
echo ""

# Test 4: Non-Repudiation
echo "Test 4: Non-Repudiation Test"
echo "--------------------------------"
python3 tests/test_non_repudiation.py
echo ""

# Test 5: Offline Verification
echo "Test 5: Offline Verification"
echo "--------------------------------"
if [ -n "$(ls -A transcripts/client_*.txt 2>/dev/null)" ]; then
    TRANSCRIPT=$(ls -t transcripts/client_*.txt | head -1)
    python3 tests/verify_transcript.py --transcript "$TRANSCRIPT" --cert certs/client_cert.pem --verify-messages --test-modification
else
    echo "⚠️  No transcript files found. Run the system first to generate transcripts."
fi
echo ""

echo "========================================="
echo "All Tests Completed"
echo "========================================="

