#!/bin/bash

# Quick Start Script for SecureChat Assignment
# This script helps you set up and test the system quickly

set -e  # Exit on error

echo "========================================="
echo "SecureChat Assignment - Quick Start"
echo "========================================="
echo ""

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
python3 --version
echo ""

# Step 2: Create virtual environment
echo "Step 2: Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
echo ""

# Step 3: Activate virtual environment
echo "Step 3: Activating virtual environment..."
source .venv/bin/activate
echo "Virtual environment activated."
echo ""

# Step 4: Install dependencies
echo "Step 4: Installing dependencies..."
pip install -r requirements.txt
echo "Dependencies installed."
echo ""

# Step 5: Create .env file if it doesn't exist
echo "Step 5: Creating .env file..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
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
    echo ".env file created."
else
    echo ".env file already exists."
fi
echo ""

# Step 6: Check MySQL
echo "Step 6: Checking MySQL..."
if command -v mysql &> /dev/null; then
    echo "MySQL is installed."
    # Try to connect to MySQL
    if mysql -u scuser -pscpass securechat -e "SELECT 1;" &> /dev/null; then
        echo "MySQL connection successful."
    else
        echo "Warning: MySQL connection failed. Please check your MySQL setup."
        echo "You may need to:"
        echo "  1. Start MySQL: sudo systemctl start mysql"
        echo "  2. Create database: mysql -u root -p -e 'CREATE DATABASE securechat; CREATE USER \"scuser\"@\"localhost\" IDENTIFIED BY \"scpass\"; GRANT ALL PRIVILEGES ON securechat.* TO \"scuser\"@\"localhost\";'"
        echo "  3. Or use Docker: docker run -d --name securechat-db -e MYSQL_ROOT_PASSWORD=rootpass -e MYSQL_DATABASE=securechat -e MYSQL_USER=scuser -e MYSQL_PASSWORD=scpass -p 3306:3306 mysql:8"
    fi
else
    echo "MySQL is not installed. Please install MySQL or use Docker."
fi
echo ""

# Step 7: Initialize database
echo "Step 7: Initializing database..."
if python -m app.storage.db --init 2>/dev/null; then
    echo "Database initialized successfully."
else
    echo "Warning: Database initialization failed. Please check your MySQL setup."
fi
echo ""

# Step 8: Generate certificates
echo "Step 8: Generating certificates..."
if [ ! -f "certs/ca_cert.pem" ]; then
    echo "Generating CA certificate..."
    python scripts/gen_ca.py --name "FAST-NU Root CA"
else
    echo "CA certificate already exists."
fi

if [ ! -f "certs/server_cert.pem" ]; then
    echo "Generating server certificate..."
    python scripts/gen_cert.py --cn server.local --out server --server
else
    echo "Server certificate already exists."
fi

if [ ! -f "certs/client_cert.pem" ]; then
    echo "Generating client certificate..."
    python scripts/gen_cert.py --cn client.local --out client
else
    echo "Client certificate already exists."
fi
echo ""

# Step 9: Verify certificates
echo "Step 9: Verifying certificates..."
if command -v openssl &> /dev/null; then
    echo "Verifying server certificate..."
    openssl verify -CAfile certs/ca_cert.pem certs/server_cert.pem || echo "Server certificate verification failed."
    echo "Verifying client certificate..."
    openssl verify -CAfile certs/ca_cert.pem certs/client_cert.pem || echo "Client certificate verification failed."
else
    echo "OpenSSL not installed. Skipping certificate verification."
fi
echo ""

echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Start the server: python -m app.server"
echo "2. Start the client (in another terminal): python -m app.client"
echo "3. Register a user and start chatting!"
echo ""
echo "For detailed instructions, see TESTING_GUIDE.md"
echo ""

